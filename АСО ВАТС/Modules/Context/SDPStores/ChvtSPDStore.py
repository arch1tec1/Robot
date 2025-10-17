from dataclasses import dataclass, field

from Core import BaseSPD, BaseSPDSet


@dataclass
class ControlSPD(BaseSPD):
    color: int = 0
    glitch: bool = False


@dataclass
class CleaningSPD(BaseSPD):
    color: int = 0
    glitch: bool = False


@dataclass
class PipeSPD(BaseSPD):
    color: list[int] = field(default_factory=lambda: [0 for _ in range(4)])
    twin_color: list[int] = field(default_factory=lambda: [0 for _ in range(4)])
    pipes_glitch: list[int] = field(default_factory=lambda: [0 for _ in range(4)])
    barrel_glitch: bool = False


@dataclass
class RemoteSPD(BaseSPD):
    color: list[int] = field(default_factory=lambda: [0 for _ in range(20)])


class ChvtSPDSet(BaseSPDSet):
    def __init__(self, context):
        super().__init__(context)

        self.controls = [
            ControlSPD(
                d_id=0,
                address="127.0.0.1" if self.context.args.get_arg("twin") else "192.168.60.133",
                port="5031" if self.context.args.get_arg("twin") else "4031",
            ),
            ControlSPD(
                d_id=1,
                address="127.0.0.1" if self.context.args.get_arg("twin") else "192.168.60.132",
                port="5032" if self.context.args.get_arg("twin") else "4031",
            ),
            ControlSPD(
                d_id=2,
                address="127.0.0.1" if self.context.args.get_arg("twin") else "192.168.60.131",
                port="5033" if self.context.args.get_arg("twin") else "4031",
            ),
        ]

        self.cleaning = CleaningSPD(
            d_id=3,
            address="127.0.0.1" if self.context.args.get_arg("twin") else "192.168.60.141",
            port="5041" if self.context.args.get_arg("twin") else "4041",
        )

        self.pipes = PipeSPD(
            d_id=4,
            address="127.0.0.1" if self.context.args.get_arg("twin") else "192.168.60.151",
            port="5051" if self.context.args.get_arg("twin") else "4051",
        )

        self.remote = RemoteSPD(
            d_id=5,
            address="127.0.0.1" if self.context.args.get_arg("twin") else "192.168.60.161",
            port="5061" if self.context.args.get_arg("twin") else "4061",
        )
