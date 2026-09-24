from src.devices.base.base_robotArm import BaseRobotArm
from vendor.nrc import nrc_interface

class NrcArm(BaseRobotArm):
    def __init__(self, name: str,ip_address: str, port: int):

        super().__init__(name, ip_address, port)

        self.ip_address = ip_address
        self.port = port
        self.socket_fd = None
        self.is_connected = False
        self.is_enabled = False

    def Connect(self) -> bool:     
        try:
            self.socket_fd = nrc_interface.connect_robot(self.ip_address, str(self.port))
            if self.socket_fd == -1:
                print(f"[{self.name}] connect failed: socket is None")
                self.is_connected = False
                return False
            else:
                print(f"[{self.name}] connected: {self.socket_fd}")
            self.is_connected = True
            return True
        except Exception as e:
            print(f"[{self.name}] connect failed: {e}")
            self.is_connected = False
            return False

    def Disconnect(self) -> bool:
        nrc_interface.disconnect_robot(self.socket_fd)
        print(f"[{self.name}] disconnected")
        self.is_connected = False
        return True

    def Enable(self) -> bool:
        nrc_interface.set_servo_state(self.socket_fd,1)
        res = nrc_interface.set_servo_poweron(self.socket_fd)
        if res == 0:
            print(f"[{self.name}] enable successful")
            self.is_enabled = True
        else:
            print(f"[{self.name}] enable failed: {res}")
            self.is_enabled = False
        return self.is_enabled


    def Disable(self) -> bool:
        res = nrc_interface.set_servo_poweroff(self.socket_fd)
        if res == 0:
            print(f"[{self.name}] disable successful")
            self.is_enabled = False
        else:
            print(f"[{self.name}] disable failed: {res}")
            self.is_enabled = True
        return not self.is_enabled

    def Get_joint_positions(self) -> list:
        # 如果还没接真机，先返回假数据测试
        out_put = nrc_interface.VectorDouble()
        res = nrc_interface.get_current_position(self.socket_fd,0, out_put)
        
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def Get_tcp_positions(self) -> list:
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def Move_j(self, joint_positions: list) -> bool:
        if not self.is_connected:
            return False
        print(f"[{self.name}] executing Move_j: {joint_positions}")
        return True

    def Move_l(self, tcp_positions: list) -> bool:
        if not self.is_connected:
            return False
        print(f"[{self.name}] executing Move_l: {tcp_positions}")
        return True