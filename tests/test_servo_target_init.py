import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.threads.slave_robot_thread import SlaveRobotThread
from src.devices.base.base_robotArm import BaseRobotArm


class FakeArm(BaseRobotArm):
    MAX_POSITION_SIZE = 7

    def __init__(self):
        super().__init__("FakeArm")
        self._positions = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]

    def Connect(self):
        return True

    def Disconnect(self):
        return True

    def Enable(self):
        return True

    def Disable(self):
        return True

    def Get_joint_positions(self):
        return list(self._positions)

    def Get_tcp_positions(self):
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def Move_j(self, target_positions, speed, acceleration, deceleration):
        return True

    def Move_l(self, target_positions, speed, acceleration, deceleration):
        return True

    def Open_servoJ(self):
        return True

    def Close_servoJ(self):
        return True

    def Set_servoJ_pos(self, target_positions):
        return True


def test_add_servoj_delta_initializes_target_from_current_positions():
    worker = SlaveRobotThread(FakeArm())

    worker.AddServoJDelta([0.5] * 7)

    assert worker.servo_target_positions == [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]
