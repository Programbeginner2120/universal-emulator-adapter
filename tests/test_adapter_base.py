import unittest
from unittest.mock import MagicMock, patch, call
from abc import ABC

from emulator_adapter.core.adapter_base import EmulatorAdapter
from emulator_adapter.core.input_event import InputEvent


class TestEmulatorAdapterInterface(unittest.TestCase):
    """Test the EmulatorAdapter abstract base class"""
    
    def test_cannot_instantiate_abstract_class(self):
        """Verify that EmulatorAdapter cannot be instantiated directly"""
        with self.assertRaises(TypeError) as context:
            EmulatorAdapter()
        
        self.assertIn("abstract", str(context.exception).lower())
    
    def test_abstract_methods_exist(self):
        """Verify all required abstract methods are defined"""
        abstract_methods = EmulatorAdapter.__abstractmethods__
        
        expected_methods = {'connect', 'send_input', 'disconnect'}
        self.assertEqual(abstract_methods, expected_methods)
    
    def test_subclass_must_implement_all_methods(self):
        """Verify that incomplete subclass cannot be instantiated"""
        
        # Incomplete implementation (missing send_input)
        class IncompleteAdapter(EmulatorAdapter):
            def connect(self):
                pass
            
            def disconnect(self):
                pass
        
        with self.assertRaises(TypeError):
            IncompleteAdapter()
    
    def test_complete_subclass_can_be_instantiated(self):
        """Verify that complete subclass implementation works"""
        
        class CompleteAdapter(EmulatorAdapter):
            def connect(self):
                pass
            
            def send_input(self, input_event):
                pass
            
            def disconnect(self):
                pass
        
        # Should not raise an error
        adapter = CompleteAdapter()
        self.assertIsInstance(adapter, EmulatorAdapter)


class TestConcreteAdapterWithMocks(unittest.TestCase):
    """Test a concrete adapter implementation using mocks"""
    
    def setUp(self):
        """Create a testable concrete adapter for each test"""
        
        class MockableAdapter(EmulatorAdapter):
            def __init__(self):
                self.connected = False
                self.emulator_connection = None
            
            def connect(self):
                # Simulate connecting to an emulator
                self.emulator_connection = MagicMock()
                self.connected = True
                return True
            
            def send_input(self, input_event):
                if not self.connected:
                    raise RuntimeError("Not connected")
                self.emulator_connection.send(input_event)
            
            def disconnect(self):
                if self.connected:
                    self.emulator_connection = None
                    self.connected = False
        
        self.adapter = MockableAdapter()
    
    def test_connect_establishes_connection(self):
        """Test that connect() properly establishes a connection"""
        result = self.adapter.connect()
        
        self.assertTrue(result)
        self.assertTrue(self.adapter.connected)
        self.assertIsNotNone(self.adapter.emulator_connection)
    
    def test_send_input_requires_connection(self):
        """Test that send_input raises error when not connected"""
        test_input = InputEvent(button="CROSS", action="press")
        
        with self.assertRaises(RuntimeError) as context:
            self.adapter.send_input(test_input)
        
        self.assertIn("Not connected", str(context.exception))
    
    def test_send_input_when_connected(self):
        """Test that send_input works when connected"""
        self.adapter.connect()
        test_input = InputEvent(button="CROSS", action="press")
        
        # Should not raise an error
        self.adapter.send_input(test_input)
        
        # Verify the mock was called with the input event
        self.adapter.emulator_connection.send.assert_called_once_with(test_input)
    
    def test_disconnect_cleans_up_connection(self):
        """Test that disconnect properly cleans up"""
        self.adapter.connect()
        self.assertTrue(self.adapter.connected)
        
        self.adapter.disconnect()
        
        self.assertFalse(self.adapter.connected)
        self.assertIsNone(self.adapter.emulator_connection)
    
    def test_disconnect_when_not_connected(self):
        """Test that disconnect is safe when not connected"""
        # Should not raise an error
        self.adapter.disconnect()
        self.assertFalse(self.adapter.connected)


if __name__ == '__main__':
    unittest.main()

