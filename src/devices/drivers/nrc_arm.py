import json
import math
from pathlib import Path

from src.ui.log_stream import Logger
from src.devices.base.base_robotArm import BaseRobotArm
from vendor.nrc import nrc_interface

class NrcArm(BaseRobotArm):

    CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "slave_arm.json"

    def __init__(
        self,
        name: str,
        ip_address: str = "192.168.2.14",
        command_port: int = 6001,
        servo_port: int = 7000,
        config_path=None,
    ):

        super().__init__(name)
        self.config_path = Path(config_path) if config_path is not None else self.CONFIG_PATH
        self._load_config(self.config_path)

        self.ip_address = ip_address
        self.command_port = command_port
        self.servo_port = servo_port
        self.servo_fd = None
        self.command_fd = None
        self.is_connected = False
        self.is_enabled = False

    def _load_config(self, path):
        """创建驱动和连接前读取配置，跟随循环不访问磁盘。"""
        try:
            with path.open(encoding="utf-8") as file:
                config = json.load(file)["NRC"]
            for key in ("MAX_JOINT_COUNT", "TCP_DIM"):
                value = config[key]
                if type(value) is not int or value <= 0:
                    raise ValueError(f"{key} 必须是正整数")
                setattr(self, key, value)
            for key in ("JOINT_COORD", "TCP_COORD"):
                setattr(self, key, config[key])
            # 单位分别为 °/s、°/s²、°/s³。
            for key in ("SERVO_J_VMAX", "SERVO_J_AVMAX", "SERVO_J_JMAX"):
                value = config[key]
                if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                    raise ValueError(f"{key} 必须是有限的正数")
                setattr(self, key, float(value))
        except (OSError, ValueError, KeyError, TypeError) as error:
            message = f"NRC 配置读取失败 ({path}): {error}"
            Logger.instance().error(message)
            raise ValueError(message) from error

    #region command 6001 port control
    def Connect(self) -> bool:
        try:
            self._load_config(self.config_path)
            Logger.instance().info(f"[{self.name}] connecting to {self.ip_address}:{self.command_port} and {self.servo_port}...")
            self.command_fd = nrc_interface.connect_robot(self.ip_address, str(self.command_port))
            self.servo_fd = nrc_interface.connect_robot(self.ip_address, str(self.servo_port))
            if self.command_fd == -1:
                Logger.instance().error(f"[{self.name}] connect failed: command socket is None")
                self.is_connected = False
                return False
            if self.servo_fd == -1:
                Logger.instance().error(f"[{self.name}] connect failed: servo socket is None")
                self.is_connected = False
                return False

            Logger.instance().info(f"[{self.name}] connected: {self.command_fd}")
            Logger.instance().info(f"[{self.name}] connected: {self.servo_fd}")
            self.is_connected = True
            return True
        except Exception as e:
            Logger.instance().error(f"[{self.name}] connect failed: {e}")
            self.is_connected = False
            return False

    def Disconnect(self) -> bool:
        nrc_interface.disconnect_robot(self.command_fd)
        nrc_interface.disconnect_robot(self.servo_fd)
        Logger.instance().info(f"[{self.name}] disconnected")
        self.is_connected = False
        return True

    def Enable(self) -> bool:
        nrc_interface.set_servo_state(self.command_fd,1)
        res = nrc_interface.set_servo_poweron(self.command_fd)
        if res == 0:
            Logger.instance().info(f"[{self.name}] enable successful")
            self.is_enabled = True
        else:
            Logger.instance().error(f"[{self.name}] enable failed: {res}")
            self.is_enabled = False
        return self.is_enabled


    def Disable(self) -> bool:
        res = nrc_interface.set_servo_poweroff(self.command_fd)
        if res == 0:
            Logger.instance().info(f"[{self.name}] disable successful")
            self.is_enabled = False
        else:
            Logger.instance().error(f"[{self.name}] disable failed: {res}")
            self.is_enabled = True
        return not self.is_enabled

    def Get_joint_positions(self) -> list:
        try:
                output = nrc_interface.VectorDouble()
                output.resize(self.MAX_JOINT_COUNT)

                result = nrc_interface.get_current_position(
                    self.command_fd,
                    self.JOINT_COORD,
                    output
                )

                if result != 0:
                    Logger.instance().error(f"[{self.name}] get_current_position failed: {result}")
                    return [0.0] * self.MAX_JOINT_COUNT

                return [float(value) for value in output]

        except Exception as e:
                Logger.instance().error(f"[{self.name}] get_current_position error: {e}")
                return [0.0] * self.MAX_JOINT_COUNT

    def Get_tcp_positions(self) -> list:
        try:
                output = nrc_interface.VectorDouble()
                output.resize(self.MAX_JOINT_COUNT)

                result = nrc_interface.get_current_position(
                    self.command_fd,
                    self.TCP_COORD,
                    output
                )

                if result != 0:
                    Logger.instance().error(f"[{self.name}] get_current_position failed: {result}")
                    return [0.0] * self.TCP_DIM

                return [float(value) for value in output][:self.TCP_DIM]

        except Exception as e:
                Logger.instance().error(f"[{self.name}] get_current_position error: {e}")
                return [0.0] * self.TCP_DIM

    def Move_j(
        self,
        joint_positions: list,
        speed: float,
        acceleration: float,
        deceleration: float
    ) -> bool:

        # 1. 检查关节数量
        if len(joint_positions) != self.MAX_JOINT_COUNT:
            return False

        # 2. 创建 MoveJ 指令
        cmd = nrc_interface.MoveCmd()

        # 3. 设置运动参数
        cmd.acc = acceleration
        cmd.dec = deceleration
        cmd.velocity = speed
        cmd.coord = self.JOINT_COORD

        # 4. 设置目标位置
        cmd.targetPosValue.resize(self.MAX_JOINT_COUNT)

        for i, position in enumerate(joint_positions):
            cmd.targetPosValue[i] = position

        # 5. 发送指令
        result = nrc_interface.robot_movej(
            self.command_fd,
            cmd
        )

        # 6. 返回执行结果
        return result == 0

    def Move_l(
        self,
        tcp_positions: list,
        speed: float,
        acceleration: float,
        deceleration: float
    ) -> bool:

        if not self.is_connected:
            return False

        # TCP 点位应该包含 6 个值：
        # X, Y, Z, Rx, Ry, Rz
        if len(tcp_positions) != 6:
            return False

        cmd = nrc_interface.MoveCmd()

        # 设置运动参数
        cmd.velocity = float(speed)
        cmd.acc = float(acceleration)
        cmd.dec = float(deceleration)

        # 设置坐标系
        cmd.coord = self.TCP_COORD

        # 设置目标位置
        cmd.targetPosValue.resize(self.MAX_JOINT_COUNT)

        for i, position in enumerate(tcp_positions):
            cmd.targetPosValue[i] = float(position)

        # 其余位置补 0
        for i in range(len(tcp_positions), self.MAX_JOINT_COUNT):
            cmd.targetPosValue[i] = 0.0

        # 调用 SDK
        result = nrc_interface.robot_movel(
            self.command_fd,
            self.robot_num,
            cmd
        )

        return result == 0

        #endregion

    #servo control 7000 port
    def Open_servoJ(self) -> bool:

        if self.servo_fd is None or self.servo_fd == -1:
            Logger.instance().error(f"[{self.name}] open_servoJ failed: invalid servo_fd")
            return False

        try:

            # servoJ 约束
            vMax  = nrc_interface.VectorDouble([self.SERVO_J_VMAX]  * self.MAX_JOINT_COUNT)
            avMax = nrc_interface.VectorDouble([self.SERVO_J_AVMAX] * self.MAX_JOINT_COUNT)
            jMax  = nrc_interface.VectorDouble([self.SERVO_J_JMAX]  * self.MAX_JOINT_COUNT)

            result = nrc_interface.open_servoJ(
                self.servo_fd, vMax, avMax, jMax
            )

            if result == 0:
                Logger.instance().info(f"[{self.name}] servo J opened successfully")
                return True
            else:
                Logger.instance().error(f"[{self.name}] failed to open servo J: {result}")
                return False

        except Exception as e:
            Logger.instance().error(f"[{self.name}] open_servoJ error: {e}")
            return False

    def Close_servoJ(self) -> bool:

        if self.servo_fd is None or self.servo_fd == -1:
            Logger.instance().error(f"[{self.name}] close_servoJ failed: invalid servo_fd")
            return False

        try:

            result = nrc_interface.stop_servoJ(self.servo_fd)
            if result == 0:

                return True
            else:
                return False
        except Exception as e:
            Logger.instance().error(f"[{self.name}] close_servoJ error: {e}")
            return False

    def Set_servoJ_pos(self, target_positions: list) -> bool:
        if self.servo_fd is None or self.servo_fd == -1:
            Logger.instance().error(f"[{self.name}] set_servoJ_pos failed: invalid servo_fd")
            return False

        try:
            pos = nrc_interface.VectorDouble()
            pos.resize(self.MAX_JOINT_COUNT)
            for i, v in enumerate(target_positions):
                pos[i] = float(v)

            result = nrc_interface.set_servoJ_pos(self.servo_fd, pos)
            return result == 0

        except Exception as e:
            Logger.instance().error(f"[{self.name}] set_servoJ_pos error: {e}")
            return False

        #endregion


