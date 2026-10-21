from src.ui.log_stream import Logger
class MasterSlaveTeleopCalculator:
    """
    保留共享内存引用，内部自己读取master快照，
    不需要外部传入主手关节坐标；算法完全沿用你原来TeleopController逻辑
    """
    def __init__(self, shared_data):
        self.shared_data = shared_data

        # 关节方向与缩放
        self.joint_sign = []
        self.joint_scale = []
        self.position_deadband_deg = 0.1

        # 会话状态
        self.master_start_positions = None
        self._sent_offset = None

    def reset(self):
        master_state = self.shared_data.master.read()
        master_joints = master_state.joints
        joint_count = len(self.shared_data.slave.read().joints)
        if not master_joints or len(master_joints) != joint_count:
            Logger.instance().error("[Teleop] master joint data invalid, reset failed")
            self.master_start_positions = None
            self._sent_offset = None
            return False
        self.master_start_positions = list(master_joints)
        # 主手第七轴用于 hand 扳机，不再驱动从手第七轴。
        self.joint_sign = [0.0 if index == 6 else -1.0 if index == 2 else 1.0
                           for index in range(joint_count)]
        self.joint_scale = [1.0] * joint_count
        self._sent_offset = [0.0] * joint_count
        return True


    def compute_increment(self, master_joints=None) -> list:
        """
        每帧调用，返回本帧增量；可传入主手快照供其他控制逻辑复用。
        return: 与当前从手关节数一致的增量
        """
        joint_count = len(self.shared_data.slave.read().joints)
        if self.master_start_positions is None or self._sent_offset is None:
            return [0.0] * joint_count

        if master_joints is None:
            master_joints = self.shared_data.master.read().joints
        if (not master_joints or len(master_joints) != joint_count
                or len(self.master_start_positions) != joint_count):
            return [0.0] * joint_count

        # 期望总偏移
        desired_offset = [
            sign * scale * (curr - start)
            for curr, start, sign, scale in zip(
                master_joints,
                self.master_start_positions,
                self.joint_sign,
                self.joint_scale
            )
        ]

        increment = []
        for desired, sent in zip(desired_offset, self._sent_offset):
            delta = desired - sent
            if abs(delta) < self.position_deadband_deg:
                delta = 0.0
            increment.append(delta)

        # 更新账本
        self._sent_offset = [sent + delta for sent, delta in zip(self._sent_offset, increment)]
        return increment
