# Universal Emulator Adapter

A Python library that provides a universal interface for sending input to various game emulators through virtual controller emulation. This adapter abstracts the complexity of different emulator input systems, allowing you to control games with a simple, unified API.

## Features

- 🎮 **Universal Input Interface** - Consistent API across different emulators
- 🔌 **Virtual Controller Support** - Uses virtual gamepad technology for reliable input
- 🐬 **Dolphin Emulator Support** - Full DS4 (PlayStation 4) controller emulation
- 🏗️ **Extensible Architecture** - Easy to add support for additional emulators
- 📦 **Simple Integration** - Install via pip and start controlling games immediately

## Supported Emulators

| Emulator | Status | Controller Type |
|----------|--------|-----------------|
| Dolphin  | ✅ Supported | DS4 (PlayStation 4) |

## Installation

### From GitHub (Recommended)

```bash
pip install git+https://github.com/Programbeginner2120/universal-emulator-adapter.git
```

### From Local Source (Development)

```bash
git clone https://github.com/Programbeginner2120/universal-emulator-adapter.git
cd universal-emulator-adapter
pip install -e .
```

## Requirements

- Python 3.7+
- Windows OS (required for `vgamepad` virtual controller support)
- Administrator privileges (for virtual controller driver installation)

## Quick Start

```python
from emulator_adapter.adapters.dolphin_adapter import DolphinAdapter
from emulator_adapter.core.input_event import InputEvent

# Create and connect adapter
adapter = DolphinAdapter()
adapter.connect()

# Press a button
button_press = InputEvent(type="BUTTON", control="CROSS", pressed=True)
adapter.send_input(button_press)

# Release the button
button_release = InputEvent(type="BUTTON", control="CROSS", pressed=False)
adapter.send_input(button_release)

# Disconnect when done
adapter.disconnect()
```

## Usage Examples

### Button Input

```python
from emulator_adapter.adapters.dolphin_adapter import DolphinAdapter
from emulator_adapter.core.input_event import InputEvent

adapter = DolphinAdapter()
adapter.connect()

# Press X button (Cross)
adapter.send_input(InputEvent(type="BUTTON", control="CROSS", pressed=True))

# Press Triangle button
adapter.send_input(InputEvent(type="BUTTON", control="TRIANGLE", pressed=True))

# Release Triangle button
adapter.send_input(InputEvent(type="BUTTON", control="TRIANGLE", pressed=False))

adapter.disconnect()
```

### Analog Stick Input

```python
# Move left stick (values range from 0.0 to 1.0)
# Center position is (0.5, 0.5)
adapter.send_input(InputEvent(
    type="STICK",
    control="LEFT_STICK",
    value_x=0.0,  # Full left
    value_y=0.5   # Centered vertically
))

# Move right stick to upper-right
adapter.send_input(InputEvent(
    type="STICK",
    control="RIGHT_STICK",
    value_x=1.0,  # Full right
    value_y=0.0   # Full up
))

# Reset to center
adapter.send_input(InputEvent(
    type="STICK",
    control="LEFT_STICK",
    value_x=0.5,
    value_y=0.5
))
```

### Trigger Input

```python
# Press L2 trigger (values range from 0.0 to 1.0)
adapter.send_input(InputEvent(
    type="TRIGGER",
    control="L2",
    value_x=1.0  # Full press
))

# Half press R2 trigger
adapter.send_input(InputEvent(
    type="TRIGGER",
    control="R2",
    value_x=0.5
))

# Release triggers
adapter.send_input(InputEvent(type="TRIGGER", control="L2", value_x=0.0))
adapter.send_input(InputEvent(type="TRIGGER", control="R2", value_x=0.0))
```

### D-Pad Input

```python
# Press D-pad up
adapter.send_input(InputEvent(type="DPAD", control="DPAD_UP", pressed=True))

# Release D-pad up
adapter.send_input(InputEvent(type="DPAD", control="DPAD_UP", pressed=False))

# Press D-pad right
adapter.send_input(InputEvent(type="DPAD", control="DPAD_RIGHT", pressed=True))
```

## API Reference

### InputEvent

The `InputEvent` dataclass represents a single input action.

**Parameters:**
- `type` (str): Type of input - `"BUTTON"`, `"STICK"`, `"TRIGGER"`, or `"DPAD"`
- `control` (str): The specific control being used
- `value_x` (float, optional): X-axis value for sticks (0.0-1.0) or trigger pressure (0.0-1.0)
- `value_y` (float, optional): Y-axis value for sticks (0.0-1.0)
- `pressed` (bool, optional): Button/D-pad press state (True/False)

### DolphinAdapter

Adapter for Dolphin emulator using DS4 virtual controller.

#### Supported Controls

**Buttons:**
- `CROSS` (X button)
- `CIRCLE` (O button)
- `SQUARE` (□ button)
- `TRIANGLE` (△ button)
- `L1`, `R1` (shoulder buttons)
- `L3`, `R3` (stick buttons)
- `OPTIONS`, `SHARE`

**Analog Sticks:**
- `LEFT_STICK`
- `RIGHT_STICK`

**Triggers:**
- `L2` (left trigger)
- `R2` (right trigger)

**D-Pad:**
- `DPAD_UP`
- `DPAD_DOWN`
- `DPAD_LEFT`
- `DPAD_RIGHT`

#### Methods

##### `connect()`
Initializes the virtual DS4 controller. Must be called before sending input.

```python
adapter.connect()
```

##### `send_input(event: InputEvent)`
Sends an input event to the emulator.

```python
adapter.send_input(InputEvent(type="BUTTON", control="CROSS", pressed=True))
```

##### `disconnect()`
Releases the virtual controller and cleans up resources.

```python
adapter.disconnect()
```

## Creating Custom Adapters

To add support for a new emulator, extend the `EmulatorAdapter` base class:

```python
from emulator_adapter.core.adapter_base import EmulatorAdapter
from emulator_adapter.core.input_event import InputEvent

class MyEmulatorAdapter(EmulatorAdapter):
    def connect(self):
        # Initialize connection to your emulator
        pass
    
    def send_input(self, event: InputEvent):
        # Handle input event and send to emulator
        if event.type == "BUTTON":
            # Handle button input
            pass
        elif event.type == "STICK":
            # Handle stick input
            pass
        # ... etc
    
    def disconnect(self):
        # Clean up resources
        pass
```

## Project Structure

```
universal-emulator-adapter/
├── emulator_adapter/
│   ├── __init__.py
│   ├── adapters/
│   │   └── dolphin_adapter.py    # Dolphin emulator adapter
│   ├── core/
│   │   ├── adapter_base.py       # Base adapter interface
│   │   └── input_event.py        # Input event data structure
│   └── utils/
│       └── logger.py             # Logging utilities
├── tests/
│   ├── dolphin/
│   │   ├── test_connect_dolphin.py
│   │   └── test_dolphin_adapter.py
│   └── test_adapter_base.py
├── setup.py
├── .gitignore
└── README.md
```

## Testing

Run the included tests to verify functionality:

```bash
# Test Dolphin adapter connection
python tests/dolphin/test_connect_dolphin.py

# Run all tests with pytest
pytest tests/
```

## Troubleshooting

### Virtual Controller Not Detected

If the emulator doesn't detect the virtual controller:
1. Ensure you're running Python with administrator privileges
2. Install the ViGEm bus driver (automatically installed with `vgamepad`)
3. Restart your emulator after connecting the adapter

### Input Not Working

- Verify the emulator is configured to accept DS4/PlayStation 4 controllers
- Check that the controller is detected in the emulator's controller settings
- Ensure `connect()` was called before sending input

## Dependencies

- [vgamepad](https://github.com/yannbouteiller/vgamepad) - Virtual gamepad emulation library

## Contributing

Contributions are welcome! To add support for additional emulators:

1. Fork the repository
2. Create a new adapter in `emulator_adapter/adapters/`
3. Extend the `EmulatorAdapter` base class
4. Add tests for your adapter
5. Submit a pull request

## License

MIT License

## Roadmap

- [ ] Add support for RetroArch
- [ ] Add support for PCSX2
- [ ] Add support for RPCS3
- [ ] Add Xbox controller emulation option
- [ ] Add Linux/macOS support (if possible)
- [ ] Add recording and playback functionality

## Acknowledgments

- Built with [vgamepad](https://github.com/yannbouteiller/vgamepad) for virtual controller support
- Inspired by the need for unified emulator control interfaces

---

**Note:** This library requires Windows and administrator privileges for virtual controller functionality. Make sure your emulator is configured to accept controller input before use.

