import threading
from dataclasses import dataclass, replace
from typing import List

# ===================== 状态结构体 =====================
@dataclass
class MasterState:
    """主手整套状态：由同一个线程更新"""
    joints: List[float]
    tcp: List[float]
    name: str = ""  # 当前主手设备名称
    # 后续扩展在这里追加字段，如：
    # force: List[float]
    # timestamp: float
    # error_code: int = 0

    def snapshot(self):
        """手动拷贝，生成独立快照"""
        return MasterState(
            joints=self.joints.copy(),
            tcp=self.tcp.copy(),
            name=self.name,
        )


@dataclass
class SlaveState:
    """从手整套状态：由另一个独立线程更新"""
    joints: List[float]
    tcp: List[float]
    name: str = ""  # 当前从手设备名称
    # 后续扩展：force、status、imu等

    def snapshot(self):
        """手动拷贝，生成独立快照"""
        return SlaveState(
            joints=self.joints.copy(),
            tcp=self.tcp.copy(),
            name=self.name,
        )


@dataclass
class SlaveIncrementState:
    """遥控制器计算得到的从手关节增量（角度）"""
    delta_joints: List[float]

    def snapshot(self):
        """手动拷贝，生成独立快照"""
        return SlaveIncrementState(
            delta_joints=self.delta_joints.copy()
        )


# ===================== 通用快照容器 =====================
class SharedStateContainer:
    def __init__(self, init_data):
        self._data = init_data
        self._write_lock = threading.Lock()

    def read(self):
        """无锁读取，返回独立快照，外部修改不会污染原始数据"""
        return self._data.snapshot()

    def write(self, new_state):
        #锁外先完成数据拷贝 避免锁内耗时过长，降低性能
        snap = new_state.snapshot()
        with self._write_lock:
            # 锁内只做简单引用赋值
            self._data = snap


    def update_partial(self, **kwargs):
        """备用：锁内局部更新，安全。例如只更新tcp"""
        with self._write_lock:
            raw_new = replace(self._data, **kwargs)
            self._data = raw_new.snapshot()


# ===================== 顶层共享内存 =====================
class RobotSharedMemory:
    def __init__(self):
        # 主手初始状态
        init_master = MasterState(
            joints=[],
            tcp=[]
        )
        self.master = SharedStateContainer(init_master)

        # 从手初始状态
        init_slave = SlaveState(
            joints=[],
            tcp=[]
        )
        self.slave = SharedStateContainer(init_slave)

        # 从手遥控关节增量
        init_slave_inc = SlaveIncrementState(
            delta_joints=[]
        )
        self.slave_increment = SharedStateContainer(init_slave_inc)
