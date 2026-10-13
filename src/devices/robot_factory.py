from src.devices.drivers.nrc_arm import NrcArm


# 新增从手型号时，在这里注册对应的驱动类。
ROBOT_DRIVERS = {"NRC": NrcArm}


def create_slave_arm(robot_type):
    driver = ROBOT_DRIVERS.get(robot_type)
    if driver is None:
        raise ValueError(f"{robot_type} 的从手驱动尚未实现")
    return driver(name=robot_type)
