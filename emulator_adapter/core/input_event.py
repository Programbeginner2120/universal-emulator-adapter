from dataclasses import dataclass
from typing import Optional, Literal

@dataclass
class InputEvent:
    type: Literal["BUTTON", "STICK", "TRIGGER", "DPAD"]
    control: str                  # e.g. 'CROSS', 'LEFT_STICK', 'L2', 'DPAD_UP'
    value_x: Optional[float] = None  # For sticks or triggers
    value_y: Optional[float] = None  # For sticks only
    pressed: Optional[bool] = None   # For buttons / D-pad