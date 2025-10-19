from dataclasses import dataclass, field

from Core import BaseSPD, BaseSPDSet


@dataclass
class PedestrianSPD(BaseSPD):
    state: int = 0


@dataclass
class BarrierSPD(BaseSPD):
    state: int = 0
    color: int = 0


@dataclass
class TLightSPD(BaseSPD):
    color: int = 1
    last_update_time: int = 0


@dataclass
class FieldCellSPD(BaseSPD):
    state: int = 0


@dataclass
class RemoteSPD(BaseSPD):
    color: list[int] = field(default_factory=lambda: [0 for _ in range(20)])


@dataclass
class BrushSPD(BaseSPD):
    state: int = 0


@dataclass
class MtsSPD(BaseSPD):
    state: int = 0


class LctSPDSet(BaseSPDSet):
    def __init__(self, context):
        super().__init__(context)

        self.pedestrians = [
            PedestrianSPD(
                d_id=0,
                address="127.0.0.1" if self.context.args.get_arg("twin") else "192.168.60.121",
                port="5021" if self.context.args.get_arg("twin") else "4000",
            ),
            PedestrianSPD(
                d_id=1,
                address="127.0.0.1" if self.context.args.get_arg("twin") else "192.168.60.122",
                port="5022" if self.context.args.get_arg("twin") else "4000",
            ),
        ]

        self.barrier = BarrierSPD(
            d_id=2,
            address="127.0.0.1" if self.context.args.get_arg("twin") else "192.168.60.131",
            port="5031" if self.context.args.get_arg("twin") else "4000",
        )

        self.t_lights = [
            TLightSPD(
                d_id=3,
                address="127.0.0.1" if self.context.args.get_arg("twin") else "192.168.60.181",
                port="5041" if self.context.args.get_arg("twin") else "4000",
            ),
            TLightSPD(
                d_id=4,
                address="127.0.0.1" if self.context.args.get_arg("twin") else "192.168.60.182",
                port="5042" if self.context.args.get_arg("twin") else "4000",
            ),
            TLightSPD(
                d_id=5,
                address="127.0.0.1" if self.context.args.get_arg("twin") else "192.168.60.183",
                port="5043" if self.context.args.get_arg("twin") else "4000",
            ),
        ]

        self.brush = BrushSPD(d_id=6, address="127.0.0.1", port="11500")

        self.mts = MtsSPD(
            d_id=7,
            address="127.0.0.1" if self.context.args.get_arg("twin") else "192.168.60.145",
            port="5071" if self.context.args.get_arg("twin") else "4000",
        )

        self.remote = RemoteSPD(
            d_id=8,
            address="127.0.0.1" if self.context.args.get_arg("twin") else "192.168.60.161",
            port="5061" if self.context.args.get_arg("twin") else "4000",
        )

        self.field_cells = [
            FieldCellSPD(
                d_id=10 + _,
                address=f"192.168.60.{71 + _}",
                port="4000",
            )
            for _ in range(40)
        ]
