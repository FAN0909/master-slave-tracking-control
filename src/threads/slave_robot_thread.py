from src.ui.log_stream import Logger

from PySide6.QtCore import QObject, Signal, Slot, QTimer, Qt
from src.devices.base.base_robotArm import BaseRobotArm
from src.devices.robot_factory import create_slave_arm
from src.shared_data.robot_share_data import RobotSharedMemory,SlaveState
from src.controller.teleop_controller import MasterSlaveTeleopCalculator
class SlaveRobotThread(QObject):

        sig_connect_result = Signal(bool, str)
        sig_disconnect_result = Signal(bool, str)
        sig_enable_result = Signal(bool, str)
        sig_disable_result = Signal(bool, str)
        sig_joint_positions = Signal(list)
        sig_tcp_positions = Signal(list)
        sig_robot_type_result = Signal(bool, str, str)

        def __init__(self, arm: BaseRobotArm, shared_data: RobotSharedMemory, robot_type="NRC"):
            super().__init__()
            self.arm = arm
            self.robot_type = robot_type
            self.shared_data = shared_data
            self.if_connected = False
            self.if_power_on = False
            self.if_servoj_open = False

            # ServoJ 的目标关节位置
            self.servo_target_positions = None

            self.if_running_follow = False
            self._resume_read_timer_interval = None

            self.timer_read_pos = QTimer(self)
            self.timer_read_pos .timeout.connect(self.OnTimerTriggeredReadPos)

            # 跟随控制使用独立周期，不再绑定到从手状态刷新频率。
            self.timer_follow = QTimer(self)
            self.timer_follow.timeout.connect(self.RunFollow)

            self.teleop_controller = MasterSlaveTeleopCalculator(shared_data)

        @Slot(str)
        def ChangeRobotType(self, robot_type):
            if self.if_connected or self.if_running_follow:
                message = "请先停止跟随并断开从手，再切换型号"
                Logger.instance().error(message)
                self.sig_robot_type_result.emit(False, self.robot_type, message)
                return
            try:
                new_arm = create_slave_arm(robot_type)
            except Exception as error:
                message = str(error)
                Logger.instance().error(message)
                self.sig_robot_type_result.emit(False, self.robot_type, message)
                return

            self.StopTimer()
            self.timer_follow.stop()
            self.arm = new_arm
            self.robot_type = robot_type
            self.if_power_on = False
            self.if_servoj_open = False
            self.servo_target_positions = None
            self._resume_read_timer_interval = None
            self.teleop_controller = MasterSlaveTeleopCalculator(self.shared_data)
            self.shared_data.slave.write(SlaveState(joints=[0.0] * 7, tcp=[0.0] * 6))
            message = f"从手已切换为 {robot_type}，请重新连接"
            Logger.instance().info(message)
            self.sig_robot_type_result.emit(True, robot_type, message)


        @Slot(int)
        def StartTimer(self, interval_ms: int=20):
            if interval_ms <= 0:
                interval_ms = 20  
            self.timer_read_pos.start(interval_ms)

        @Slot()
        def StopTimer(self):
            if self.timer_read_pos.isActive():
                self.timer_read_pos.stop()

        def OnTimerTriggeredReadPos(self):
            joint_pos = self.arm.Get_joint_positions()
            tcp_pos = self.arm.Get_tcp_positions()   

            slave_state = SlaveState(joints=joint_pos, tcp=tcp_pos)
            self.shared_data.slave.write(slave_state)

            self.sig_joint_positions.emit(joint_pos)
            self.sig_tcp_positions.emit(tcp_pos)

        @Slot(str)
        def Connect(self, ip_address: str) -> bool:
            self.arm.ip_address = ip_address
            if self.arm.Connect():
                self.if_connected = True
                self.sig_connect_result.emit(True, "connected successfully")
                return True
            else:
                self.sig_connect_result.emit(False, "failed to connect")
                return False
            
        @Slot()
        def Disconnect(self) -> bool:

            self.StopFollow()
            self.StopTimer()
            if self.if_servoj_open and not self.CloseServoJ():
                self.sig_disconnect_result.emit(False, "关闭 ServoJ 失败，未断开从手")
                return False

            if self.arm.Disconnect():
                self.if_connected = False
                self.if_power_on = False
                self.if_servoj_open = False
                self.servo_target_positions = None
                self.sig_disconnect_result.emit(True, "disconnected successfully")
                return True
            else:
                self.sig_disconnect_result.emit(False, "failed to disconnect")
                return False

        @Slot()
        def Enable(self) -> bool:
            if self.arm.Enable():
                self.if_power_on = True
                self.sig_enable_result.emit(True, "enable successful")
                return True
            else:
                self.sig_enable_result.emit(False, "enable failed")
                return False

        @Slot()
        def Disable(self) -> bool:
            if self.arm.Disable():
                self.if_power_on = False
                self.sig_disable_result.emit(True, "disable successful")
                return True
            else:
                self.sig_disable_result.emit(False, "disable failed")
                return False

        @Slot()
        def OpenServoJ(self) -> bool:
            if self.arm.Open_servoJ():
                self.if_servoj_open = True
                return True
            else:
                return False

        @Slot()
        def CloseServoJ(self) -> bool:
            if self.arm.Close_servoJ():
                self.if_servoj_open = False
                return True
            else:
                return False

        @Slot()
        def MoveJ(self, target_positions: list, speed: float, acceleration: float, deceleration: float) -> bool:
            if self.arm.Move_j(target_positions, speed, acceleration, deceleration):
                return True
            else:
                return False


        def testservoj(self):
            pos = self.arm.Get_joint_positions()
            if not pos:
                return

            count = 0
            while count < 10:
                pos[0] -= 1.0
                Logger.instance().info(f"[{self.arm.name}] test servoJ angle: {pos[0]} deg")
                self.arm.Set_servoJ_pos(pos)
                count += 1


        @Slot()
        def StartFollow(self, time_interval_ms: int=20):
            """启动主从跟随，只在点击开始时调用一次reset"""
            if self.if_running_follow:
                return

            if not self.if_servoj_open:
                self.OpenServoJ()
            if not self.if_servoj_open:
                Logger.instance().error("ServoJ未打开，无法启动跟随")
                return
            # 初始化伺服目标为当前从手位置
            self.servo_target_positions = self.arm.Get_joint_positions()
            # 重置遥操作零点（内部读取当前主手作为基准）
            ok = self.teleop_controller.reset()
            if not ok:
                Logger.instance().error("遥操作重置失败，主手数据无效，无法开启跟随")
                return
            if time_interval_ms <= 0:
                time_interval_ms = 20
            self.if_running_follow = True
            self.timer_follow.start(time_interval_ms)
            Logger.instance().info("主从跟随开启")

        @Slot()
        def StopFollow(self):
            """停止跟随"""
            self.if_running_follow = False
            self.timer_follow.stop()

            Logger.instance().info("🛑 主从跟随关闭")

        @Slot()
        def RunFollow(self):
            if not self.if_running_follow:
                return

            # 调用teleop控制器，内部自动读共享内存主手，返回增量
            delta = self.teleop_controller.compute_increment()
            if self.servo_target_positions is None:
                self.servo_target_positions = self.arm.Get_joint_positions()
            # 叠加增量
            self.servo_target_positions = [
                target + d
                for target, d in zip(self.servo_target_positions, delta)
            ]
            target = list(self.servo_target_positions)
            self.arm.Set_servoJ_pos(target)
