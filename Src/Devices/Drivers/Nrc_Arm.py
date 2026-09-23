from Src.Devices.Base.Base_RobotArm import BaseRobotArm
from vendor.nrc import nrc_interface

class NrcArm(BaseRobotArm):
    def __init__(self, name: str,ip_address: str, port: int):
        # 3. 必须调用父类的初始化，把 name 传进去
        super().__init__(name)
        # 这里可以初始化你 vendor SDK 的变量
        self.ip_address = ip_address
        self.port = port
        self.socket_fd = None

        self.nrc_api = None
        self.is_connected = False
        self.is_enabled = False

    # 4. 挨个实现所有带有 @abstractmethod 的方法
    def Connect(self) -> bool:     
        try:
            # 你的 vendor SDK 调用代码，比如：
            if self.nrc_api is None:
                self.nrc_api = nrc_interface()
            
            self.socket_fd = self.nrc_api.connect_robot(self.ip_address, self.port)
            if self.socket_fd == -1:
                print(f"[{self.name}] 连接失败: 返回的 socket 为 None")
                self.is_connected = False
                return False
            else:
                print(f"[{self.name}] 已连接: {self.socket_fd}")
            self.is_connected = True
            return True
        except Exception as e:
            print(f"[{self.name}] 连接失败: {e}")
            self.is_connected = False
            return False

    def Disconnect(self) -> bool:
        self.nrc_api.disconnect_robot(self.socket_fd)
        print(f"[{self.name}] 断开连接")
        self.is_connected = False
        return True

    def Enable(self) -> bool:
        self.nrc_api.set_servo_state(1)
        res = self.nrc_api.set_servo_poweron(self.socket_fd)
        if res == 0:
            print(f"[{self.name}] 上使能成功")
            self.is_enabled = True
        else:
            print(f"[{self.name}] 上使能失败: {res}")
            self.is_enabled = False
        return self.is_enabled


    def Disable(self) -> bool:
        res = self.nrc_api.set_servo_poweroff(self.socket_fd)
        if res == 0:
            print(f"[{self.name}] 下使能成功")
            self.is_enabled = False
        else:
            print(f"[{self.name}] 下使能失败: {res}")
            self.is_enabled = True
        return not self.is_enabled

    def Get_joint_positions(self) -> list:
        # 如果还没接真机，先返回假数据测试
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def Get_tcp_positions(self) -> list:
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def Move_j(self, joint_positions: list) -> bool:
        if not self.is_connected:
            return False
        print(f"[{self.name}] 执行 Move_j: {joint_positions}")
        return True

    def Move_l(self, tcp_positions: list) -> bool:
        if not self.is_connected:
            return False
        print(f"[{self.name}] 执行 Move_l: {tcp_positions}")
        return True