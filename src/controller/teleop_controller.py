from PySide6.QtCore import QObject, Signal, Slot


class TeleopController(QObject):
    """Map master joint motion to slave joint increments."""

    """把主手关节运动映射为从手关节增量。

    核心思路：
        维护一个"账本" _sent_offset，记录已经累计发给从手的偏移量。
        每帧拿"主手相对起点的总偏移"减去"账本"，得到"还欠多少"，
        经死区过滤后发给从手，并更新账本。
        这样死区过滤掉的量不会丢失，下一帧会补上。
    """


    # The slave worker keeps its own target position and adds this increment.
    sig_set_slave_target = Signal(list)
    sig_teleop_state_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.is_running = False
        self.master_joint_positions = None
        self.master_start_positions = None

        # Offset already sent to the slave since this follow session began.
        self._sent_offset = None

        # Joint mapping. Adjust signs for joints whose master/slave directions
        # are opposite, and adjust scales when their joint ranges differ.
        self.joint_sign = [
            1.0,  # joint0：同方向
            1.0,  # joint1：同方向
            -1.0,  # joint2：反方向
            1.0,  # joint3：同方向
            1.0,  # joint4：同方向
            1.0,  # joint5：同方向
            1.0,  # joint6：同方向
        ]
        self.joint_scale = [1.0] * 7

        # All joint values are degrees. Set to 0.0 to send every small change.
        self.position_deadband_deg = 0.1

    @Slot(list)
    def UpdateMasterJointPositions(self, joint_positions: list):
        """Convert the newest master pose into a slave increment."""
        self.master_joint_positions = list(joint_positions)

        if not self.is_running:
            return

        desired_offset = self._calculate_desired_offset(joint_positions)
        if desired_offset is None:
            return

        increment = self._calculate_increment(desired_offset)
        if not any(increment):
            return

        self.sig_set_slave_target.emit(increment)

    @Slot()
    def StartTeleop(self):
        """Record the master reference pose and reset session state."""
        if self.is_running:
            return

        if self.master_joint_positions is None:
            print("Unable to start teleoperation: master joint data is unavailable")
            return

        joint_count = len(self.master_joint_positions)
        if joint_count != len(self.joint_sign) or joint_count != len(self.joint_scale):
            print("Unable to start teleoperation: master joint count must be 7")
            return

        self.master_start_positions = list(self.master_joint_positions)
        self._sent_offset = [0.0] * joint_count
        self.is_running = True
        self.sig_teleop_state_changed.emit(True)

    @Slot()
    def StopTeleop(self):
        """Clear all follow-session state to prevent a restart jump."""
        if not self.is_running:
            return

        self.is_running = False
        self.master_start_positions = None
        self._sent_offset = None
        self.sig_teleop_state_changed.emit(False)

    def _calculate_desired_offset(self, master_positions: list):
        if self.master_start_positions is None:
            return None
        if len(master_positions) != len(self.master_start_positions):
            print("Master joint count changed during teleoperation")
            self.StopTeleop()
            return None

        return [
            sign * scale * (current - start)
            for current, start, sign, scale in zip(
                master_positions,
                self.master_start_positions,
                self.joint_sign,
                self.joint_scale,
            )
        ]

    def _calculate_increment(self, desired_offset: list):
        if self._sent_offset is None:
            return None

        increment = []
        for desired, sent in zip(desired_offset, self._sent_offset):
            delta = desired - sent
            if abs(delta) < self.position_deadband_deg:
                delta = 0.0
            increment.append(delta)

        self._sent_offset = [
            sent + delta
            for sent, delta in zip(self._sent_offset, increment)
        ]
        return increment
