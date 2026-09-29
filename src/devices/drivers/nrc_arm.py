from src.devices.base.base_robotArm import BaseRobotArm
from vendor.nrc import nrc_interface

class NrcArm(BaseRobotArm):

    MAX_POSITION_SIZE = 7
    JOINT_COORD = 0
    TCP_COORD = 1

    # servoJ 运动约束
    SERVO_J_VMAX  = 10.0    # 速度 °/s
    SERVO_J_AVMAX = 200.0   # 加速度 °/s^2
    SERVO_J_JMAX  = 180.0   # 加加速度 °/s^3

    def __init__(self, name: str,ip_address: str, command_port: int, servo_port: int):

        super().__init__( name)

        self.ip_address = ip_address
        self.command_port = command_port
        self.servo_port = servo_port
        self.servo_fd = None
        self.command_fd = None
        self.is_connected = False
        self.is_enabled = False

    #region command 6001 port control
    def Connect(self) -> bool:     
        try:
            self.command_fd = nrc_interface.connect_robot(self.ip_address, str(self.command_port))
            self.servo_fd = nrc_interface.connect_robot(self.ip_address, str(self.servo_port))
            if self.command_fd == -1:
                print(f"[{self.name}] connect failed: command socket is None")
                self.is_connected = False
                return False
            if self.servo_fd == -1:
                print(f"[{self.name}] connect failed: servo socket is None")
                self.is_connected = False
                return False
            
            print(f"[{self.name}] connected: {self.command_fd}")
            print(f"[{self.name}] connected: {self.servo_fd}")
            self.is_connected = True
            return True
        except Exception as e:
            print(f"[{self.name}] connect failed: {e}")
            self.is_connected = False
            return False

    def Disconnect(self) -> bool:
        nrc_interface.disconnect_robot(self.command_fd)
        nrc_interface.disconnect_robot(self.servo_fd)
        print(f"[{self.name}] disconnected")
        self.is_connected = False
        return True

    def Enable(self) -> bool:
        nrc_interface.set_servo_state(self.command_fd,1)
        res = nrc_interface.set_servo_poweron(self.command_fd)
        if res == 0:
            print(f"[{self.name}] enable successful")
            self.is_enabled = True
        else:
            print(f"[{self.name}] enable failed: {res}")
            self.is_enabled = False
        return self.is_enabled


    def Disable(self) -> bool:
        res = nrc_interface.set_servo_poweroff(self.command_fd)
        if res == 0:
            print(f"[{self.name}] disable successful")
            self.is_enabled = False
        else:
            print(f"[{self.name}] disable failed: {res}")
            self.is_enabled = True
        return not self.is_enabled

    def Get_joint_positions(self) -> list:
        try:
                output = nrc_interface.VectorDouble()
                output.resize(self.MAX_POSITION_SIZE)

                result = nrc_interface.get_current_position(
                    self.command_fd,
                    self.JOINT_COORD,
                    output
                )

                if result != 0:
                    print(f"[{self.name}] get_current_position failed: {result}")
                    return [0.0] * self.MAX_POSITION_SIZE

                return [float(value) for value in output]

        except Exception as e:
                print(f"[{self.name}] get_current_position error: {e}")
                return [0.0] * self.MAX_POSITION_SIZE

    def Get_tcp_positions(self) -> list:
        try:
                output = nrc_interface.VectorDouble()
                output.resize(self.MAX_POSITION_SIZE)

                result = nrc_interface.get_current_position(
                    self.command_fd,
                    self.TCP_COORD,
                    output
                )

                if result != 0:
                    print(f"[{self.name}] get_current_position failed: {result}")
                    return [0.0] * self.MAX_POSITION_SIZE

                return [float(value) for value in output]

        except Exception as e:
                print(f"[{self.name}] get_current_position error: {e}")
                return [0.0] * self.MAX_POSITION_SIZE

    def Move_j(
        self,
        joint_positions: list,
        speed: float,
        acceleration: float,
        deceleration: float
    ) -> bool:

        # 1. 检查关节数量
        if len(joint_positions) != self.MAX_POSITION_SIZE:
            return False

        # 2. 创建 MoveJ 指令
        cmd = nrc_interface.MoveCmd()

        # 3. 设置运动参数
        cmd.acc = acceleration
        cmd.dec = deceleration
        cmd.velocity = speed
        cmd.coord = self.JOINT_COORD

        # 4. 设置目标位置
        cmd.targetPosValue.resize(self.MAX_POSITION_SIZE)

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
        cmd.targetPosValue.resize(self.MAX_POSITION_SIZE)

        for i, position in enumerate(tcp_positions):
            cmd.targetPosValue[i] = float(position)

        # 其余位置补 0
        for i in range(len(tcp_positions), self.MAX_POSITION_SIZE):
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
            print(f"[{self.name}] open_servoJ failed: invalid servo_fd")
            return False

        try:

            # servoJ 约束
            vMax  = nrc_interface.VectorDouble([self.SERVO_J_VMAX]  * self.MAX_POSITION_SIZE)
            avMax = nrc_interface.VectorDouble([self.SERVO_J_AVMAX] * self.MAX_POSITION_SIZE)
            jMax  = nrc_interface.VectorDouble([self.SERVO_J_JMAX]  * self.MAX_POSITION_SIZE)
            
            result = nrc_interface.open_servoJ(
                self.servo_fd, vMax, avMax, jMax
            )

            if result == 0:
                print(f"[{self.name}] servo J opened successfully")
                return True
            else:
                print(f"[{self.name}] failed to open servo J: {result}")
                return False

        except Exception as e:
            print(f"[{self.name}] open_servoJ error: {e}")
            return False

    def Close_servoJ(self) -> bool:
        print("111")

        if self.servo_fd is None or self.servo_fd == -1:
            print(f"[{self.name}] close_servoJ failed: invalid servo_fd")
            return False

        try:
            print("222")

            result = nrc_interface.stop_servoJ(self.servo_fd)
            if result == 0:
                print("333")

                return True
            else:
                return False
        except Exception as e:
            print(f"[{self.name}] close_servoJ error: {e}")
            return False
        
    def Set_servoJ_pos(self, target_positions: list) -> bool:
        if self.servo_fd is None or self.servo_fd == -1:
            print(f"[{self.name}] set_servoJ_pos failed: invalid servo_fd")
            return False
        
        try:
            pos = nrc_interface.VectorDouble()
            pos.resize(self.MAX_POSITION_SIZE)
            for i, v in enumerate(target_positions):
                pos[i] = float(v)

            result = nrc_interface.set_servoJ_pos(self.servo_fd, pos)
            return result == 0

        except Exception as e:
            print(f"[{self.name}] set_servoJ_pos error: {e}")
            return False        

        #endregion

    