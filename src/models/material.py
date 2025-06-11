from pydantic import BaseModel, Field
from typing import List


class MaterialAbsorptionResult(BaseModel):
    name: str = Field(
        ..., title="Material name", description="Name or description of the material"
    )
    coeffs: List[float] = Field(
        ...,
        title="Absorption coefficients",
        description="Absorption coefficients for octave bands",
    )
    center_freqs: List[int] = Field(
        ...,
        title="Center frequencies",
        description="Center frequencies of the absorption coefficients",
    )
