from src.devices.drivers.nrc_arm import NrcArm
from src.devices.drivers.gello_arm import GelloArm
from src.devices.drivers.Link_hand import LinkHand


# 新增型号时，在对应字典中注册驱动类。
ROBOT_DRIVERS = {"NRC": NrcArm}
MASTER_DRIVERS = {"Gello": GelloArm}
HAND_DRIVERS = {
    "LinkHand": LinkHand,
    "LinkerO6": LinkHand,
}
CAMERA_DRIVERS = {}


def create_slave_arm(robot_type, **kwargs):
    driver = ROBOT_DRIVERS.get(robot_type)
    if driver is None:
        raise ValueError(f"{robot_type} 的从手驱动尚未实现")
    kwargs.setdefault("name", robot_type)
    return driver(**kwargs)


def create_master_arm(master_type, **kwargs):
    driver = MASTER_DRIVERS.get(master_type)
    if driver is None:
        raise ValueError(f"{master_type} 的主手驱动尚未实现")
    kwargs.setdefault("name", master_type)
    return driver(**kwargs)


def create_hand(hand_model, **kwargs):
    driver = HAND_DRIVERS.get(hand_model)
    if driver is None:
        raise ValueError(f"{hand_model} 的灵巧手驱动尚未实现")
    kwargs.setdefault("name", hand_model)
    return driver(**kwargs)


def create_camera(camera_type, **kwargs):
    driver = CAMERA_DRIVERS.get(camera_type)
    if driver is None:
        raise ValueError(f"{camera_type} 的相机驱动尚未实现")
    kwargs.setdefault("name", camera_type)
    return driver(**kwargs)
