"""设备反馈与命令标签的回归测试，不访问串口、网络或 CAN。"""

import threading
import types
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QCoreApplication

from src.devices.drivers import nrc_arm
from src.devices.drivers.gello_arm import GelloArm
from src.threads.hand_thread import HandThread
from src.threads.master_robot_thread import MasterRobotThread
from src.threads.slave_robot_thread import SlaveRobotThread
from src.shared_data.capture_ring_buffer import CaptureRingBuffer
from src.shared_data.robot_share_data import RobotSharedMemory, HandState, MasterState
from vendor.gello.dynamixel import DynamixelDriver
from vendor.linkerhand_python_sdk.LinkerHand.core.can.linker_hand_o6_can import LinkerHandO6Can
from vendor.realsense import realsense_manager


class CaptureSourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def test_failed_nrc_reads_do_not_generate_zero_state(self):
        class Vector(list):
            def resize(self, n): self[:] = [0.] * n
        sdk = types.SimpleNamespace(VectorDouble=Vector, get_current_position=lambda *args: -1)
        with patch.object(nrc_arm, 'nrc_interface', sdk):
            arm = nrc_arm.NrcArm('NRC')
            arm.command_fd = 1
            state = CaptureRingBuffer(10)
            worker = SlaveRobotThread(RobotSharedMemory(), state, CaptureRingBuffer(10))
            worker.arm, worker.if_connected = arm, True
            worker.OnTimerTriggeredReadPos()
            self.assertEqual(arm.Get_joint_positions(), [])
            self.assertEqual(len(state), 0)

    def test_gello_cache_reads_preserve_bus_timestamp_and_reject_stale_feedback(self):
        backend = DynamixelDriver.__new__(DynamixelDriver)
        backend._is_fake = False
        backend._lock = threading.Lock()
        backend._joint_angles = np.array([100] * 7)
        backend._joint_timestamp_ns = 1_000_000_000
        arm = GelloArm('Gello')
        arm.dynamixel_driver = backend
        memory, buffer = RobotSharedMemory(), CaptureRingBuffer(10)
        worker = MasterRobotThread(arm, memory, buffer)
        worker.if_connected = True
        with patch('src.threads.master_robot_thread.monotonic_ns', return_value=1_050_000_000):
            worker.OnTimerTriggeredReadPos()
            worker.OnTimerTriggeredReadPos()
        self.assertEqual(len(buffer), 1)
        self.assertEqual(buffer.latest().timestamp_ns, 1_000_000_000)
        with patch('src.threads.master_robot_thread.monotonic_ns', return_value=11_000_000_000):
            worker.OnTimerTriggeredReadPos()
        self.assertEqual(memory.master.read().joints, [])
        self.assertEqual(buffer.latest().timestamp_ns, 1_000_000_000)

    def can_backend(self):
        backend = LinkerHandO6Can.__new__(LinkerHandO6Can)
        backend._state_condition = threading.Condition()
        backend._state_sequence = 0
        backend._state_timestamp_ns = None
        backend.x01 = [9] * 6
        backend.can_id = 1
        return backend

    def test_can_query_requires_a_new_feedback_packet(self):
        backend = self.can_backend()
        backend.send_frame = lambda *args, **kwargs: None
        with self.assertRaises(TimeoutError):
            backend.get_current_status_sample()
        def respond(*args, **kwargs):
            backend.process_response(types.SimpleNamespace(arbitration_id=1, data=bytes([1, 10, 20, 30, 40, 50, 60])))
        backend.send_frame = respond
        joints, timestamp = backend.get_current_status_sample()
        self.assertEqual(joints, [10, 20, 30, 40, 50, 60])
        self.assertIsInstance(timestamp, int)

    def test_test_actions_update_targets_and_are_blocked_during_recording(self):
        memory = RobotSharedMemory()
        memory.hand.write(HandState([1.] * 6, 'LinkerO6'))
        actions = CaptureRingBuffer(10)
        worker = HandThread(memory, CaptureRingBuffer(10), actions)
        calls = []
        worker.hand = types.SimpleNamespace(MAX_JOINTS=lambda: 6, Set_force=lambda v: True,
                Set_speed=lambda v: True, Set_joint_positions=lambda v: calls.append(v.copy()) or True)
        worker.if_connected = True
        self.assertTrue(worker.ExecuteTestAction('LinkerO6', 'test', [100] * 6, 255, 255))
        self.assertEqual(actions.latest().data, calls[-1])
        worker.recording_active.set()
        self.assertFalse(worker.ExecuteTestAction('LinkerO6', 'test', [200] * 6, 255, 255))
        self.assertFalse(worker.Set_joint_positions([200] * 6))
        self.assertEqual(len(calls), 1)

    def test_camera_maps_global_clock_and_labels_arrival_fallback(self):
        image = np.zeros((4, 4, 3), dtype=np.uint8)
        frame = types.SimpleNamespace(get_frame_timestamp_domain=lambda: realsense_manager.rs.timestamp_domain.global_time,
                get_timestamp=lambda: 1000., get_data=lambda: image)
        manager = realsense_manager.RealSenseManager()
        manager.pipeline = types.SimpleNamespace(poll_for_frames=lambda: types.SimpleNamespace(get_color_frame=lambda: frame))
        with patch.object(realsense_manager, 'monotonic_ns', return_value=10_000_000_000), \
                patch.object(realsense_manager, 'time_ns', return_value=2_000_000_000):
            data, timestamp, source = manager.get_color_sample()
            self.assertEqual(timestamp, 9_000_000_000)
            self.assertEqual(source, 'realsense_global_time')
            image[:] = 255
            self.assertFalse(data.any())
            frame.get_frame_timestamp_domain = lambda: realsense_manager.rs.timestamp_domain.hardware_clock
            self.assertEqual(manager.get_color_sample()[1:], (10_000_000_000, 'host_arrival'))

    def test_missing_slave_feedback_stops_follow_without_overwriting_target(self):
        memory = RobotSharedMemory()
        memory.master.write(MasterState([1.] * 7, []))
        worker = SlaveRobotThread(memory, CaptureRingBuffer(10), CaptureRingBuffer(10))
        worker.arm = types.SimpleNamespace(MAX_JOINT_COUNT=7)
        worker.if_running_follow = True
        worker.servo_target_positions = [20.] * 7
        worker.RunFollow()
        self.assertFalse(worker.if_running_follow)
        self.assertEqual(worker.servo_target_positions, [20.] * 7)


if __name__ == '__main__':
    unittest.main()
