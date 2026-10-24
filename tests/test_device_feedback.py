"""反馈校验与 SDK 封装的回归测试，不连接机器人、相机或 CAN。"""

import math
from threading import Lock
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import can
import numpy as np
from PySide6.QtCore import QCoreApplication

from src.devices.drivers.gello_arm import GelloArm
from src.devices.drivers.Link_hand import LinkHand
from src.devices.drivers.nrc_arm import NrcArm
from src.devices.sdk_feedback_adapters import DynamixelFeedbackAdapter
from src.shared_data.capture_ring_buffer import CaptureRingBuffer
from src.shared_data.device_feedback import (
    DEFAULT_MAX_AGE_NS, DeviceReadError, FeedbackStatus, FeedbackTracker,
    PositionFeedback, validate_positions,
)
from src.shared_data.robot_share_data import MasterState, RobotSharedMemory, SlaveState
from src.threads.camera_thread import CameraThread
from src.threads.hand_thread import HandThread
from src.threads.master_robot_thread import MasterRobotThread
from src.threads.slave_robot_thread import SlaveRobotThread
from vendor.linkerhand_python_sdk.LinkerHand.core.can.linker_hand_o6_can import LinkerHandO6Can


class Vector(list):
    def resize(self, count):
        self[:] = [0.0] * count


class DeviceFeedbackTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self):
        self.shared = RobotSharedMemory()

    def make_slave(self):
        worker = SlaveRobotThread(self.shared, CaptureRingBuffer(10), CaptureRingBuffer(10))
        worker.arm = Mock(name="arm", MAX_JOINT_COUNT=7, TCP_DIM=6)
        worker.arm.name = "NRC"
        worker.if_connected = True
        return worker

    def make_hand(self, modbus="None"):
        backend = LinkerHandO6Can.__new__(LinkerHandO6Can)
        backend.can_id = 0x28
        backend.x01 = [0] * 6
        backend.bus = Mock()
        api = SimpleNamespace(
            hand=backend, get_state=backend.get_current_status,
            finger_move=backend.set_joint_positions, set_speed=backend.set_speed,
            set_torque=backend.set_torque,
        )
        hand = LinkHand("LinkerO6", modbus=modbus)
        with patch("src.devices.drivers.Link_hand.LinkerHandApi", return_value=api):
            self.assertTrue(hand.Connect())
        return hand, backend

    @staticmethod
    def receive(backend, values):
        backend.process_response(SimpleNamespace(
            arbitration_id=backend.can_id, data=bytes([0x01, *values]),
        ))

    def test_valid_zero_and_numpy_positions_are_preserved(self):
        self.assertEqual(validate_positions(np.zeros(7), 7), (0.0,) * 7)

    def test_invalid_dimensions_and_values_are_rejected(self):
        for values in (None, [], [0] * 6, [0] * 8, [math.nan] * 7,
                       [math.inf] * 7, ["0"] * 7, [True] * 7, np.zeros((7, 1))):
            with self.subTest(values=values), self.assertRaises(DeviceReadError):
                validate_positions(values, 7)
        with self.assertRaises(DeviceReadError):
            validate_positions([256] * 6, 6, 0, 255)

    def test_tracker_keeps_original_time_and_sequence_until_new_feedback(self):
        tracker = FeedbackTracker(6)
        with self.assertRaises(DeviceReadError):
            tracker.read()
        with patch("src.shared_data.device_feedback.monotonic_ns", return_value=100):
            sample = tracker.publish([0] * 6)
            self.assertIs(tracker.read(), sample)
            self.assertIs(tracker.read(), sample)
            # 数值相同的真实新包仍是新反馈。
            self.assertEqual(tracker.publish([0] * 6).sequence, 2)
        with patch("src.shared_data.device_feedback.monotonic_ns", return_value=DEFAULT_MAX_AGE_NS + 101):
            with self.assertRaisesRegex(DeviceReadError, "超时"):
                tracker.read()
        tracker.invalidate("通信失败")
        with self.assertRaisesRegex(DeviceReadError, "通信失败"):
            tracker.read()
        self.assertEqual(tracker.publish([1] * 6).sequence, 3)

    def test_nrc_failure_does_not_fabricate_zero_samples_and_can_recover(self):
        arm = NrcArm("NRC")
        arm.is_connected = True
        arm.command_fd = 1
        sdk = SimpleNamespace(VectorDouble=Vector, get_current_position=Mock(return_value=-1))
        with patch("src.devices.drivers.nrc_arm.nrc_interface", sdk):
            self.assertEqual(arm.Get_joint_positions(), [])
            self.assertEqual(arm.Get_tcp_positions(), [])
            sdk.get_current_position.return_value = 0
            sample = arm.Read_joint_positions()
            self.assertEqual(sample.values, (0.0,) * 7)
            self.assertEqual(sample.sequence, 1)
            self.assertEqual(len(arm.Read_tcp_positions().values), 6)

    def test_nrc_rejects_malformed_success_responses(self):
        arm = NrcArm("NRC")
        arm.is_connected = True
        sdk = SimpleNamespace(VectorDouble=Vector)
        for values in ([1] * 6, [1] * 8, [math.nan] * 7):
            def read(fd, coord, output):
                output[:] = values
                return 0
            sdk.get_current_position = read
            with self.subTest(values=values), patch("src.devices.drivers.nrc_arm.nrc_interface", sdk):
                self.assertEqual(arm.Get_joint_positions(), [])

    def test_nrc_rejects_invalid_servo_targets_before_sending(self):
        arm = NrcArm("NRC")
        arm.is_connected = True
        arm.servo_fd = 2
        sdk = SimpleNamespace(VectorDouble=Vector, set_servoJ_pos=Mock(return_value=0))
        with patch("src.devices.drivers.nrc_arm.nrc_interface", sdk):
            for values in ([0] * 6, [math.nan] * 7, [math.inf] * 7):
                self.assertFalse(arm.Set_servoJ_pos(values))
            sdk.set_servoJ_pos.assert_not_called()
            self.assertTrue(arm.Set_servoJ_pos([0] * 7))
            self.assertEqual(list(sdk.set_servoJ_pos.call_args.args[1]), [0.0] * 7)

    def test_dynamixel_observer_rejects_old_cache_and_tracks_transactions(self):
        group = Mock()
        transaction = Mock(return_value=0)
        group.txRxPacket = transaction
        group.isAvailable.return_value = True
        group.getData.side_effect = lambda joint_id, address, size: 0xFFFFFFFF if joint_id == 1 else 0
        driver = SimpleNamespace(_lock=Lock(), _groupSyncRead=group)
        adapter = DynamixelFeedbackAdapter(driver, [1, 2, 3, 4, 5, 6, 7])
        arm = GelloArm("Gello")
        arm.is_connected = True
        arm._feedback_adapter = adapter
        self.assertEqual(arm.Get_joint_positions(), [])
        group.txRxPacket()
        sample = arm.Read_joint_positions()
        self.assertAlmostEqual(sample.values[0], -math.pi / 2048)
        self.assertIs(arm.Read_joint_positions(), sample)
        transaction.return_value = -1
        # 失败不会抛到厂商循环外，SDK 仍可继续重试。
        self.assertEqual(group.txRxPacket(), -1)
        self.assertEqual(arm.Get_joint_positions(), [])
        transaction.return_value = 0
        group.txRxPacket()
        self.assertEqual(arm.Read_joint_positions().sequence, 2)

    def test_dynamixel_partial_packet_does_not_produce_feedback(self):
        group = Mock()
        group.txRxPacket.return_value = 0
        group.isAvailable.side_effect = lambda joint_id, address, size: joint_id != 7
        group.getData.return_value = 0
        adapter = DynamixelFeedbackAdapter(SimpleNamespace(_lock=Lock(), _groupSyncRead=group), list(range(1, 8)))
        with self.assertRaises(DeviceReadError):
            group.txRxPacket()
        with self.assertRaises(DeviceReadError):
            adapter.tracker.read()

    def test_can_requires_a_real_response_and_repeated_reads_keep_timestamp(self):
        hand, backend = self.make_hand()
        self.assertEqual(hand.Get_joint_positions(), [])
        self.receive(backend, [0] * 6)
        first = hand.Read_joint_positions()
        self.assertEqual(first.values, (0.0,) * 6)
        self.assertIs(hand.Read_joint_positions(), first)
        self.receive(backend, [0] * 6)
        self.assertEqual(hand.Read_joint_positions().sequence, first.sequence + 1)
        with patch("src.shared_data.device_feedback.monotonic_ns", return_value=first.timestamp_ns + 2 * DEFAULT_MAX_AGE_NS):
            self.assertEqual(hand.Get_joint_positions(), [])

    def test_malformed_can_packet_invalidates_feedback_until_recovery(self):
        hand, backend = self.make_hand()
        self.receive(backend, [10] * 6)
        self.receive(backend, [10] * 5)
        self.assertEqual(hand.Get_joint_positions(), [])
        self.receive(backend, [20] * 6)
        self.assertEqual(hand.Get_joint_positions(), [20.0] * 6)

    def test_sdk_cannot_hide_can_send_failure(self):
        hand, backend = self.make_hand()
        self.receive(backend, [10] * 6)
        backend.bus._bus.send.side_effect = can.CanError("CAN unavailable")
        self.assertFalse(hand.Set_joint_positions([10] * 6))
        self.assertFalse(hand.Set_speed([100] * 6))
        self.assertFalse(hand.Set_force([100] * 6))
        self.assertEqual(hand.Get_joint_positions(), [])

    def test_hand_rejects_arguments_sdk_would_ignore_or_truncate(self):
        hand, backend = self.make_hand()
        for positions in ([1.5] * 6, [-1] * 6, [256] * 6, [0] * 5):
            self.assertFalse(hand.Set_joint_positions(positions))
        self.assertFalse(hand.Set_speed([-1] * 6))
        backend.bus._bus.send.assert_not_called()

    def test_modbus_feedback_is_validated_and_timestamped_after_response(self):
        hand, _ = self.make_hand(modbus="/dev/fake")
        hand.hand_api.get_state = Mock(return_value=[20] * 6)
        sample = hand.Read_joint_positions()
        self.assertEqual(sample.values, (20.0,) * 6)
        hand.hand_api.get_state.return_value = [math.nan] * 6
        self.assertEqual(hand.Get_joint_positions(), [])
        hand.hand_api.get_state.side_effect = RuntimeError("Modbus timeout")
        self.assertEqual(hand.Get_joint_positions(), [])

    def test_master_thread_deduplicates_feedback_and_marks_failure(self):
        tracker = FeedbackTracker(7)
        sample = tracker.publish([0] * 7)
        arm = Mock(MAX_JOINT_COUNT=7, TCP_DIM=6)
        arm.name = "Gello"
        arm.Read_joint_positions.return_value = sample
        worker = MasterRobotThread(arm, self.shared, CaptureRingBuffer(10))
        worker.if_connected = True
        worker.OnTimerTriggeredReadPos()
        worker.OnTimerTriggeredReadPos()
        self.assertEqual(len(worker.capture_buffer), 1)
        self.assertEqual(worker.capture_buffer.latest().timestamp_ns, sample.timestamp_ns)
        self.assertEqual(self.shared.master.read().tcp, [])
        arm.Read_joint_positions.side_effect = DeviceReadError("timeout")
        worker.OnTimerTriggeredReadPos()
        state = self.shared.master.read()
        self.assertFalse(state.feedback.valid)
        self.assertEqual(state.joints, [])
        self.assertEqual(state.feedback.timestamp_ns, sample.timestamp_ns)
        self.assertEqual(len(worker.capture_buffer), 1)

    def test_slave_requires_successful_joint_and_tcp_reads(self):
        worker = self.make_slave()
        joints = FeedbackTracker(7).publish([0] * 7)
        tcp = FeedbackTracker(6).publish([0] * 6)
        worker.arm.Read_joint_positions.return_value = joints
        worker.arm.Read_tcp_positions.side_effect = DeviceReadError("TCP failed")
        worker.OnTimerTriggeredReadPos()
        self.assertEqual(len(worker.capture_buffer), 0)
        self.assertFalse(self.shared.slave.read().feedback.valid)
        worker.arm.Read_tcp_positions.side_effect = None
        worker.arm.Read_tcp_positions.return_value = tcp
        worker.OnTimerTriggeredReadPos()
        state = self.shared.slave.read()
        self.assertTrue(state.feedback.is_fresh())
        self.assertEqual(state.tcp_timestamp_ns, tcp.timestamp_ns)

    def test_hand_thread_does_not_turn_cached_feedback_into_new_samples(self):
        hand, backend = self.make_hand()
        self.receive(backend, [10] * 6)
        worker = HandThread(self.shared, CaptureRingBuffer(10), CaptureRingBuffer(10))
        worker.hand = hand
        worker.if_connected = True
        worker.OnTimerTriggeredReadPos()
        timestamp = worker.capture_buffer.latest().timestamp_ns
        worker.OnTimerTriggeredReadPos()
        self.assertEqual(len(worker.capture_buffer), 1)
        with patch("src.shared_data.device_feedback.monotonic_ns", return_value=timestamp + DEFAULT_MAX_AGE_NS + 1):
            worker.OnTimerTriggeredReadPos()
        self.assertFalse(self.shared.hand.read().feedback.valid)
        self.assertEqual(self.shared.hand.read().joints, [])

    def test_failed_hand_action_clears_previous_action_label(self):
        hand, backend = self.make_hand()
        worker = HandThread(self.shared, CaptureRingBuffer(10), CaptureRingBuffer(10))
        worker.hand = hand
        worker.if_connected = True
        self.shared.hand.update_partial(name="LinkerO6")
        worker.action_buffer.append([0] * 6)
        backend.bus._bus.send.side_effect = can.CanError("send failed")
        self.assertFalse(worker.ExecuteFollowState(True))
        self.assertEqual(len(worker.action_buffer), 0)

    def test_successful_hand_action_records_the_sent_target(self):
        hand, backend = self.make_hand()
        worker = HandThread(self.shared, CaptureRingBuffer(10), CaptureRingBuffer(10))
        worker.hand = hand
        worker.if_connected = True
        self.shared.hand.update_partial(name="LinkerO6")
        self.assertTrue(worker.ExecuteFollowState(True))
        target = worker.action_buffer.latest().data
        # 最后一次 CAN 发送的 0x01 包必须与记录的目标一致。
        sent_frame = backend.bus._bus.send.call_args.args[0]
        self.assertEqual(list(sent_frame.data), [0x01, *target])

    def test_modbus_action_read_failure_invalidates_feedback_and_action(self):
        hand, _ = self.make_hand(modbus="/dev/fake")
        hand.hand_api.get_state = Mock(side_effect=(
            [10.] * 6, [10.] * 6, RuntimeError("Modbus timeout"),
        ))
        worker = HandThread(self.shared, CaptureRingBuffer(10), CaptureRingBuffer(10))
        worker.hand, worker.if_connected = hand, True
        self.shared.hand.update_partial(name="LinkerO6")
        worker.action_buffer.append([0] * 6)
        self.assertFalse(worker.ExecuteFollowState(True))
        self.assertFalse(self.shared.hand.read().feedback.valid)
        self.assertIn("Modbus timeout", self.shared.hand.read().feedback.error)
        self.assertEqual(len(worker.action_buffer), 0)
        self.assertIsNone(worker._configured_speed)
        self.assertIsNone(worker._configured_force)

    def test_manual_speed_and_disconnect_invalidate_cached_action_parameters(self):
        hand, _ = self.make_hand()
        hand.hand_api.set_speed = Mock(wraps=hand.hand_api.set_speed)
        hand.hand_api.set_torque = Mock(wraps=hand.hand_api.set_torque)
        worker = HandThread(self.shared, CaptureRingBuffer(10), CaptureRingBuffer(10))
        worker.hand, worker.if_connected = hand, True
        self.shared.hand.update_partial(name="LinkerO6")
        bounds = {"min": 0, "max": 255}
        worker._execute_action("LinkerO6", "close", [100] * 6, 255, 255, bounds)
        self.assertTrue(worker.Set_speed([40] * 6))
        worker._execute_action("LinkerO6", "open", [200] * 6, 255, 255, bounds)
        self.assertEqual(hand.hand_api.set_speed.call_count, 3)
        self.assertEqual(hand.hand_api.set_speed.call_args.args[0], [255] * 6)
        self.assertEqual(hand.hand_api.set_torque.call_count, 1)
        hand.Disconnect = Mock(return_value=True)
        self.assertTrue(worker.Disconnect())
        self.assertIsNone(worker._configured_speed)
        self.assertIsNone(worker._configured_force)

    def test_follow_rejects_missing_initial_feedback(self):
        worker = self.make_slave()
        worker.if_power_on = True
        worker.StartFollow()
        self.assertFalse(worker.if_running_follow)
        worker.arm.Open_servoJ.assert_not_called()

    def test_follow_stops_on_stale_feedback_without_sending_a_target(self):
        worker = self.make_slave()
        worker.if_running_follow = True
        worker.action_buffer.append([0] * 7)
        worker.RunFollow()
        worker.arm.Set_servoJ_pos.assert_not_called()
        self.assertFalse(worker.if_running_follow)
        self.assertEqual(len(worker.action_buffer), 0)

    def test_follow_send_failure_stops_and_does_not_commit_target(self):
        worker = self.make_slave()
        status = FeedbackStatus.success(FeedbackTracker(7).publish([0] * 7))
        self.shared.master.write(MasterState([0] * 7, [], feedback=status))
        self.shared.slave.write(SlaveState([0] * 7, [0] * 6, feedback=status))
        worker.if_running_follow = True
        worker.servo_target_positions = [0] * 7
        worker.teleop_controller.compute_increment = Mock(return_value=[1] * 7)
        worker.arm.Set_servoJ_pos.return_value = False
        worker.RunFollow()
        self.assertFalse(worker.if_running_follow)
        self.assertEqual(worker.servo_target_positions, [0] * 7)
        self.assertEqual(len(worker.action_buffer), 0)

    def test_follow_starts_with_fresh_feedback_and_records_successful_targets(self):
        worker = self.make_slave()
        worker.if_power_on = True
        sample = FeedbackTracker(7).publish([0] * 7)
        status = FeedbackStatus.success(sample)
        self.shared.master.write(MasterState([0] * 7, [], feedback=status))
        self.shared.slave.write(SlaveState([0] * 7, [0] * 6, feedback=status))
        worker.arm.Read_joint_positions.return_value = sample
        worker.arm.Open_servoJ.return_value = True
        worker.arm.Set_servoJ_pos.return_value = True
        worker.StartFollow()
        try:
            self.assertTrue(worker.if_running_follow)
            self.shared.master.update_partial(joints=[1] * 7)
            worker.RunFollow()
            expected = [1, 1, -1, 1, 1, 1, 0]
            worker.arm.Set_servoJ_pos.assert_called_once_with(expected)
            self.assertEqual(worker.action_buffer.latest().data, expected)
        finally:
            worker.StopFollow()

    def test_camera_rejects_malformed_frames_and_owns_valid_frame_memory(self):
        worker = CameraThread(CaptureRingBuffer(5))
        worker.camera = Mock()
        worker.if_connected = True
        for frame in (np.zeros((2, 2), np.uint8), np.zeros((2, 2, 3)),
                      np.zeros((0, 2, 3), np.uint8)):
            worker.camera.Get_color_frame.return_value = frame
            worker.OnTimerTriggeredReadFrame()
            self.assertEqual(len(worker.capture_buffer), 0)
            self.assertFalse(worker.feedback_status.valid)
        frame = np.zeros((2, 2, 3), np.uint8)
        worker.camera.Get_color_frame.return_value = frame
        worker.OnTimerTriggeredReadFrame()
        self.assertTrue(worker.feedback_status.valid)
        frame[:] = 255
        self.assertTrue(np.all(worker.capture_buffer.latest().data == 0))
        worker.camera.Get_color_frame.return_value = None
        worker.OnTimerTriggeredReadFrame()
        self.assertTrue(worker.feedback_status.valid)
        with patch("src.shared_data.device_feedback.monotonic_ns", return_value=worker.feedback_status.timestamp_ns + DEFAULT_MAX_AGE_NS + 1):
            worker.OnTimerTriggeredReadFrame()
        self.assertFalse(worker.feedback_status.valid)
        self.assertEqual(len(worker.capture_buffer), 0)


if __name__ == "__main__":
    unittest.main()
