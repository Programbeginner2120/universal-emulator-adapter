from dataclasses import dataclass

@dataclass
class InputEvent:
    button: str
    action: str # "press", "release", "axis"
    value: float = 0.0 # optional for analog sticks