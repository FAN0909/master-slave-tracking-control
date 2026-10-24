"""在项目层观察 SDK 实例的收发结果，不修改 vendor 文件或全局 SDK 类。"""

import math
from time import monotonic_ns

from src.shared_data.device_feedback import DeviceReadError, FeedbackTracker


class DynamixelFeedbackAdapter:
    """观察完整的 GroupSyncRead；避免把 SDK 的旧缓存重新标记成新读数。"""

    def __init__(self, driver, joint_ids):
        from vendor.gello.dynamixel.driver import (
            ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION, COMM_SUCCESS,
        )

        self.tracker = FeedbackTracker(len(joint_ids))
        group = driver._groupSyncRead
        # SDK 用同一个锁保护轮询，安装观察器时不会切入半次读取。
        with driver._lock:
            original = group.txRxPacket

            def read_packet():
                try:
                    result = original()
                    if result != COMM_SUCCESS:
                        self.tracker.invalidate(f"Dynamixel 读取失败：{result}")
                        return result
                    values = []
                    for joint_id in joint_ids:
                        if not group.isAvailable(joint_id, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION):
                            raise DeviceReadError(f"Dynamixel {joint_id} 缺少位置反馈")
                        value = group.getData(joint_id, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
                        if value > 0x7FFFFFFF:
                            value -= 0x100000000
                        # 与厂商 get_joints() 的编码器单位转换一致。
                        values.append(value / 2048.0 * math.pi)
                    self.tracker.publish(values)
                    return result
                except Exception as error:
                    self.tracker.invalidate(error)
                    raise

            group.txRxPacket = read_packet


class _CheckedCanBus:
    """将发送失败转成 RuntimeError，避免 SDK 吞掉 CanError 后报告成功。"""

    def __init__(self, bus):
        self._bus = bus

    def send(self, *args, **kwargs):
        try:
            result = self._bus.send(*args, **kwargs)
            if result is False:
                raise RuntimeError("CAN 总线拒绝发送")
            return result
        except Exception as error:
            raise RuntimeError(f"CAN 发送失败：{error}") from error

    def __getattr__(self, name):
        return getattr(self._bus, name)


class LinkerO6CanFeedbackAdapter:
    """从 SDK 原有接收线程观察 O6 位置包，不额外创建 CAN 接收者。"""

    def __init__(self, backend):
        self.tracker = FeedbackTracker(6, 0, 255)
        original = backend.process_response

        def process_response(message):
            is_position = (message.arbitration_id == backend.can_id
                           and len(message.data) > 0 and message.data[0] == 0x01)
            received_ns = monotonic_ns()
            try:
                original(message)
                if is_position:
                    self.tracker.publish(message.data[1:], received_ns)
            except Exception as error:
                # 不让畸形反馈结束厂商的接收线程。
                self.tracker.invalidate(error)

        backend.process_response = process_response
        backend.bus = _CheckedCanBus(backend.bus)
