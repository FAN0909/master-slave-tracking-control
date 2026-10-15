from src.ui.log_stream import Logger
class MasterSlaveTeleopCalculator:
    """
    保留共享内存引用，内部自己读取master快照，
    不需要外部传入主手关节坐标；算法完全沿用你原来TeleopController逻辑
    """
    def __init__(self, shared_data):
        self.shared_data = shared_data

        # 关节方向与缩放
        self.joint_sign = [
            1.0,   # joint0
            1.0,   # joint1
            -1.0,  # joint2 反向
            1.0,   # joint3
            1.0,   # joint4
            1.0,   # joint5
            1.0    # joint6
        ]
        self.joint_scale = [1.0] * 7
        self.position_deadband_deg = 0.1

        # 会话状态
        self.master_start_positions = None
        self._sent_offset = None

    def reset(self):
        master_state = self.shared_data.master.read()
        master_joints = master_state.joints
        if master_joints is None or len(master_joints) != 7:
            Logger.instance().error("[Teleop] master joint data invalid, reset failed")
            self.master_start_positions = None
            self._sent_offset = None
            return False
        self.master_start_positions = list(master_joints)
        self._sent_offset = [0.0] * 7
        return True


    def compute_increment(self) -> list:
        """
        每帧调用，内部自动读共享内存主手，返回本帧增量delta列表
        return: 7个关节增量
        """
        if self.master_start_positions is None or self._sent_offset is None:
            return [0.0] * 7

        master_state = self.shared_data.master.read()
        master_joints = master_state.joints
        if master_joints is None or len(master_joints) != 7:
            return [0.0] * 7

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
