from abc import ABC, abstractmethod

class EmulatorAdapter(ABC):
    @abstractmethod
    def connect(self):
        """Connect to the emulator"""
        pass

    @abstractmethod
    def send_input(self, input_event, *args, **kwargs):
        """Send an input event (button/axis) to the emulator"""
        pass

    @abstractmethod
    def disconnect(self):
        """Cleanly disconnect from the emulator"""
        pass