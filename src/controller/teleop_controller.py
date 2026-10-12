from PySide6.QtCore import QObject, Signal, Slot
import math

class TeleopController(QObject):

    # 发送从手目标关节增量（每次相对于上一次主手位置的增量）
    sig_set_slave_target = Signal(list)

    # 遥操作状态变化
    sig_teleop_state_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        # 是否开启跟随
        self.is_running = False

        # 保存最新一次读取到的主手关节位置
        self.master_joint_positions = None

        # 保存上一次用于计算增量的主手关节位置
        self.master_last_positions = None

        # ==================== 滤波参数（可在此处修改） ====================
        # 1) 死区阈值：每个关节增量绝对值小于该值时不发送，先累积；
        #    当累积绝对值 >= 阈值时，一次性发送累计增量。
        #    单位与主手关节角度一致（通常为 度）。
        #    设为 None 或 <= 0 表示关闭死区滤波。
        self.joint_increment_threshold = 1.0

        # 2) 单帧限幅：单帧原始增量的绝对值上限，防止异常跳变。
        #    设为 None 表示不限制。
        self.joint_increment_max = 10.0
        # =================================================================

        # 每个关节累积的未发送增量（长度与主手关节数一致）
        self._pending_increment = None


    @Slot(list)
    def UpdateMasterJointPositions(self, joint_positions: list):
        """接收主手关节数据"""

        self.master_joint_positions = list(joint_positions)

        # 未开启跟随时，只保存数据
        if not self.is_running:
            return

        # 计算相对于上一次位置的增量
        joint_increment = self.CalculateJointIncrement(joint_positions)

        # 更新上一次位置，供下一帧计算增量
        self.master_last_positions = list(joint_positions)

        #print(f"TeleopController master joint positions: {joint_positions}")
        print(f"Joint increments: {joint_increment}")

        self.sig_set_slave_target.emit(joint_increment)

    @Slot()
    def StartTeleop(self):
        """开始跟随"""

        if self.is_running:
            return

        # 没有获取到主手数据时，不允许开始跟随
        if self.master_joint_positions is None:
            print("无法开始跟随：尚未获取主手关节数据")
            return

        # 记录开始跟随时的主手位置，作为第一次增量计算基准
        self.master_last_positions = list(self.master_joint_positions)

        self.is_running = True
        self.sig_teleop_state_changed.emit(True)

    @Slot()
    def StopTeleop(self):
        """停止跟随"""

        if not self.is_running:
            return

        self.is_running = False
        self.master_last_positions = None
        self.sig_teleop_state_changed.emit(False)

    # def CalculateJointIncrement(self, master_positions: list) -> list:
    #     """计算主手当前位置相对于上一次位置的关节增量"""

    #     if self.master_last_positions is None:
    #         return []

    #     if len(master_positions) != len(self.master_last_positions):
    #         raise ValueError("主手当前关节数量与上一次关节数量不一致")

    #     joint_increment = [
    #         current - last
    #         for current, last in zip(master_positions, self.master_last_positions)
    #     ]

    #     return joint_increment
    def CalculateJointIncrement(self, master_positions: list) -> list:
        """计算主手当前位置相对于上一次位置的关节增量，带死区滤波和限幅"""

        if self.master_last_positions is None:
            return []

        if len(master_positions) != len(self.master_last_positions):
            raise ValueError("主手当前关节数量与上一次关节数量不一致")

        n = len(master_positions)

        # 初始化/对齐累积数组
        if self._pending_increment is None or len(self._pending_increment) != n:
            self._pending_increment = [0.0] * n

        threshold = self.joint_increment_threshold
        max_step = self.joint_increment_max

        joint_increment = []

        for i in range(n):
            # 本帧原始增量
            raw = master_positions[i] - self.master_last_positions[i]

            # --- 1) 单帧限幅 ---
            if max_step is not None:
                if raw > max_step:
                    raw = max_step
                elif raw < -max_step:
                    raw = -max_step

            # --- 2) 累积 ---
            self._pending_increment[i] += raw

            # --- 3) 死区滤波 ---
            if threshold is not None and threshold > 0:
                if abs(self._pending_increment[i]) < threshold:
                    # 未超过阈值：发送 0，增量继续累积
                    joint_increment.append(0.0)
                else:
                    # 超过阈值：发送累计增量，并清零累积
                    joint_increment.append(self._pending_increment[i])
                    self._pending_increment[i] = 0.0
            else:
                # 关闭滤波：直接发送本帧累积（等同于本帧原始增量）
                joint_increment.append(self._pending_increment[i])
                self._pending_increment[i] = 0.0

        return joint_increment