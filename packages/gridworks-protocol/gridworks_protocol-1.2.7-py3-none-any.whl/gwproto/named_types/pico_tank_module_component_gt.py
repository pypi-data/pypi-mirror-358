"""Type pico.tank.reader.component.gt, version 010"""

from typing import Literal, Optional

from pydantic import ConfigDict, model_validator
from typing_extensions import Self

from gwproto.enums import TempCalcMethod
from gwproto.named_types.component_gt import ComponentGt


class PicoTankModuleComponentGt(ComponentGt):
    Enabled: bool
    PicoHwUid: Optional[str] = None
    PicoAHwUid: Optional[str] = None
    PicoBHwUid: Optional[str] = None
    TempCalcMethod: TempCalcMethod
    ThermistorBeta: int
    SendMicroVolts: bool
    Samples: int
    NumSampleAverages: int
    PicoKOhms: Optional[int] = None
    SerialNumber: str = "NA"
    AsyncCaptureDeltaMicroVolts: int
    TypeName: Literal["pico.tank.module.component.gt"] = "pico.tank.module.component.gt"
    Version: Literal["010"] = "010"

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom 1: Exactly one of PicoHwUid, PicoAwUid, PicoBHwUid exists.
        """
        id_fields = [self.PicoHwUid, self.PicoAHwUid, self.PicoBHwUid]
        num_provided = sum(1 for v in id_fields if v is not None)

        if num_provided != 1:
            raise ValueError(
                "Exactly one of PicoHwUid, PicoAHwUid, PicoBHwUid must be provided"
            )

        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> Self:
        """
        Axiom 2: PicoKOhms exists iff TempCalcMethod is TempCalcMethod.SimpleBetaForPico
        # note this is a known incorrect method, but there are a few in the field
        # that do this.
        """
        is_simple_beta = self.TempCalcMethod == TempCalcMethod.SimpleBetaForPico
        has_kohms = self.PicoKOhms is not None

        if is_simple_beta != has_kohms:
            raise ValueError(
                "PicoKOhms must be provided if and only if TempCalcMethod is SimpleBetaForPico"
            )

        return self
