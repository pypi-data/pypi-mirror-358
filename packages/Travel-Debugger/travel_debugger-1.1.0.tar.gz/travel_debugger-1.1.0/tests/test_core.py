"""
Tests for TimeTravelDebugger core functionality
"""
import unittest
import time
import json
from pathlib import Path
import tempfile

from time_travel_debugger.core import TimeTravelDebugger, ExecutionState, DebugSession


class TestExecutionState(unittest.TestCase):
    
    def test_execution_state_creation(self):
        """Test ExecutionState creation and serialization"""
        frame_info = {
            'filename': 'test.py',
            'function_name': 'test_func',
            'line_number': 10,
            'event': 'call'
        }
        
        state = ExecutionState(frame_info, 1.5)
        
        self.assertIsInstance(state.id, str)
        self.assertEqual(state.timestamp, 1.5)
        self.assertEqual(state.frame_info, frame_info)
        self.assertEqual(state.locals, {})
        self.assertEqual(state.globals, {})
    
    def test_execution_state_serialization(self):
        """Test ExecutionState to_dict and from_dict"""
        frame_info = {'filename': 'test.py', 'function_name': 'test', 'line_number': 1, 'event': 'call'}
        state = ExecutionState(frame_info, 2.0)
        state.locals = {'x': 42, 'y': 'hello'}
        state.globals = {'PI': 3.14}
        
        # Test serialization
        state_dict = state.to_dict()
        self.assertIn('id', state_dict)
        self.assertEqual(state_dict['timestamp'], 2.0)
        self.assertEqual(state_dict['locals'], {'x': 42, 'y': 'hello'})
        
        # Test deserialization
        restored_state = ExecutionState.from_dict(state_dict)
        self.assertEqual(restored_state.id, state.id)
        self.assertEqual(restored_state.timestamp, state.timestamp)
        self.assertEqual(restored_state.locals, state.locals)


class TestDebugSession(unittest.TestCase):
    
    def test_debug_session_creation(self):
        """Test DebugSession creation"""
        session = DebugSession()
        
        self.assertIsInstance(session.id, str)
        self.assertIsNotNone(session.created_at)
        self.assertEqual(session.timeline, [])
        self.assertEqual(session.metadata, {})
    
    def test_debug_session_serialization(self):
        """Test DebugSession export/import"""
        session = DebugSession()
        
        # Add some test data
        frame_info = {'filename': 'test.py', 'function_name': 'test', 'line_number': 1, 'event': 'call'}
        state = ExecutionState(frame_info, 1.0)
        session.timeline.append(state)
        session.metadata = {'test': 'data'}
        
        # Test serialization
        session_dict = session.to_dict()
        self.assertEqual(len(session_dict['timeline']), 1)
        self.assertEqual(session_dict['metadata'], {'test': 'data'})
        
        # Test deserialization
        restored_session = DebugSession.from_dict(session_dict)
        self.assertEqual(restored_session.id, session.id)
        self.assertEqual(len(restored_session.timeline), 1)
        self.assertEqual(restored_session.metadata, {'test': 'data'})
    
    def test_debug_session_file_operations(self):
        """Test DebugSession file export/import"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_session.json"
            
            # Create and export session
            session = DebugSession()
            session.metadata = {'test': 'file_operations'}
            session.export_to_file(file_path)
            
            # Verify file exists
            self.assertTrue(file_path.exists())
            
            # Import session
            imported_session = DebugSession.import_from_file(file_path)
            self.assertEqual(imported_session.id, session.id)
            self.assertEqual(imported_session.metadata, {'test': 'file_operations'})


class TestTimeTravelDebugger(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.debugger = TimeTravelDebugger()
    
    def test_debugger_initialization(self):
        """Test TimeTravelDebugger initialization"""
        self.assertIsNotNone(self.debugger.db)
        self.assertIsNotNone(self.debugger.session)
        self.assertFalse(self.debugger.is_tracing)
        self.assertEqual(self.debugger.call_stack, [])
    
    def test_safe_copy_vars(self):
        """Test safe variable copying"""
        # Test serializable variables
        vars_dict = {
            'int_var': 42,
            'str_var': 'hello',
            'list_var': [1, 2, 3],
            'dict_var': {'key': 'value'}
        }
        
        safe_vars = self.debugger._safe_copy_vars(vars_dict)
        self.assertEqual(safe_vars['int_var'], 42)
        self.assertEqual(safe_vars['str_var'], 'hello')
        self.assertEqual(safe_vars['list_var'], [1, 2, 3])
        self.assertEqual(safe_vars['dict_var'], {'key': 'value'})
    
    def test_safe_copy_vars_non_serializable(self):
        """Test safe copying of non-serializable variables"""
        # Create a non-serializable object
        class NonSerializable:
            def __init__(self):
                self.circular_ref = self
        
        vars_dict = {
            'normal_var': 42,
            'non_serializable': NonSerializable()
        }
        
        safe_vars = self.debugger._safe_copy_vars(vars_dict)
        self.assertEqual(safe_vars['normal_var'], 42)
        self.assertIn('non_serializable', safe_vars)
        # Non-serializable should be converted to a description dict
        self.assertIsInstance(safe_vars['non_serializable'], dict)
    
    def test_tracing_lifecycle(self):
        """Test tracing start/stop lifecycle"""
        self.assertFalse(self.debugger.is_tracing)
        
        # Start tracing
        self.debugger.start_tracing()
        self.assertTrue(self.debugger.is_tracing)
        self.assertIsNotNone(self.debugger.session.start_time)
        
        # Stop tracing
        self.debugger.stop_tracing()
        self.assertFalse(self.debugger.is_tracing)
        self.assertIsNotNone(self.debugger.session.end_time)
    
    def test_simple_function_tracing(self):
        """Test tracing a simple function"""
        def test_function():
            x = 10
            y = 20
            return x + y
        
        # Trace the function
        self.debugger.start_tracing()
        result = test_function()
        self.debugger.stop_tracing()
        
        # Verify result
        self.assertEqual(result, 30)
        
        # Check timeline
        timeline = self.debugger.get_timeline()
        self.assertGreater(len(timeline), 0)
        
        # Check that we captured some states
        call_states = [s for s in timeline if s.frame_info.get('event') == 'call']
        self.assertGreater(len(call_states), 0)
    
    def test_get_state_at_time(self):
        """Test getting state at specific timestamp"""
        def test_function():
            x = 1
            y = 2
            return x + y
        
        self.debugger.start_tracing()
        test_function()
        self.debugger.stop_tracing()
        
        timeline = self.debugger.get_timeline()
        if timeline:
            # Get state at middle timestamp
            mid_time = timeline[len(timeline) // 2].timestamp
            state = self.debugger.get_state_at_time(mid_time)
            self.assertIsNotNone(state)
            self.assertIsInstance(state, ExecutionState)
    
    def test_get_variables_at_time(self):
        """Test getting variables at specific timestamp"""
        def test_function():
            x = 42
            y = "test"
            return f"{x}: {y}"
        
        self.debugger.start_tracing()
        test_function()
        self.debugger.stop_tracing()
        
        timeline = self.debugger.get_timeline()
        if timeline:
            # Get variables at a timestamp
            timestamp = timeline[-1].timestamp
            variables = self.debugger.get_variables_at_time(timestamp)
            
            self.assertIn('locals', variables)
            self.assertIn('globals', variables)
            self.assertIn('timestamp', variables)
    
    def test_search_variables(self):
        """Test variable search functionality"""
        def test_function():
            special_var = 999
            other_var = "hello"
            return special_var
        
        self.debugger.start_tracing()
        test_function()
        self.debugger.stop_tracing()
        
        # Search for specific variable
        states = self.debugger.search_variables('special_var')
        # We might find states with this variable
        self.assertIsInstance(states, list)
        
        # Search for specific variable with value
        states_with_value = self.debugger.search_variables('special_var', value=999)
        self.assertIsInstance(states_with_value, list)
    
    def test_get_states_by_event(self):
        """Test filtering states by event type"""
        def test_function():
            return 42
        
        self.debugger.start_tracing()
        test_function()
        self.debugger.stop_tracing()
        
        # Get call events
        call_states = self.debugger.get_states_by_event('call')
        self.assertIsInstance(call_states, list)
        
        # Get line events
        line_states = self.debugger.get_states_by_event('line')
        self.assertIsInstance(line_states, list)
    
    def test_session_summary(self):
        """Test session summary generation"""
        def test_function():
            return 42
        
        self.debugger.start_tracing()
        test_function()
        self.debugger.stop_tracing()
        
        summary = self.debugger.get_session_summary()
        
        self.assertIn('session_id', summary)
        self.assertIn('total_states', summary)
        self.assertIn('duration', summary)
        self.assertIn('functions_called', summary)
        self.assertIn('exceptions', summary)
        
        self.assertIsInstance(summary['total_states'], int)
        self.assertIsInstance(summary['functions_called'], list)
        self.assertIsInstance(summary['exceptions'], list)


if __name__ == '__main__':
    unittest.main()