"""
Tests for TimeTravelDebugger decorators and context managers
"""
import unittest
import tempfile
from pathlib import Path

from time_travel_debugger.decorators import (
    time_travel_debug,
    TimeTravelContext,
    start_global_debugging,
    stop_global_debugging,
    get_global_timeline,
    debug_function,
    quick_debug
)


class TestTimeravelDebugDecorator(unittest.TestCase):
    
    def test_basic_decorator_usage(self):
        """Test basic @time_travel_debug usage"""
        
        @time_travel_debug
        def test_function(n):
            result = 0
            for i in range(n):
                result += i
            return result
        
        # Call the decorated function
        result = test_function(5)
        self.assertEqual(result, 10)  # 0+1+2+3+4 = 10
        
        # Check that debugging session was recorded
        self.assertTrue(hasattr(test_function, '_debugger_sessions'))
        sessions = test_function._debugger_sessions
        self.assertGreater(len(sessions), 0)
        
        # Get the last session
        debugger = sessions[-1]
        timeline = debugger.get_timeline()
        self.assertGreater(len(timeline), 0)
    
    def test_decorator_with_parameters(self):
        """Test @time_travel_debug with parameters"""
        
        def my_filter(frame):
            return 'test_function' in frame.f_code.co_name
        
        @time_travel_debug(filter_func=my_filter)
        def test_function():
            x = 42
            return x * 2
        
        result = test_function()
        self.assertEqual(result, 84)
        
        # Verify debugging was applied
        debugger = test_function.get_last_session()
        self.assertIsNotNone(debugger)
    
    def test_decorator_convenience_methods(self):
        """Test convenience methods added to decorated functions"""
        
        @time_travel_debug
        def test_function():
            return 42
        
        test_function()
        
        # Test get_last_session
        last_session = test_function.get_last_session()
        self.assertIsNotNone(last_session)
        
        # Test get_all_sessions
        all_sessions = test_function.get_all_sessions()
        self.assertGreater(len(all_sessions), 0)
        
        # Test that the convenience methods work
        # (We can't easily test print methods without capturing output)
        self.assertTrue(hasattr(test_function, 'print_timeline'))
        self.assertTrue(hasattr(test_function, 'print_variables_at'))
    
    def test_multiple_calls_session_limit(self):
        """Test that session history is limited"""
        
        @time_travel_debug
        def test_function(x):
            return x * 2
        
        # Call multiple times (more than the limit of 10)
        for i in range(15):
            test_function(i)
        
        sessions = test_function.get_all_sessions()
        # Should be limited to 10 sessions
        self.assertLessEqual(len(sessions), 10)


class TestTimeTravelContext(unittest.TestCase):
    
    def test_basic_context_manager(self):
        """Test basic TimeTravelContext usage"""
        
        with TimeTravelContext() as debugger:
            x = 10
            y = 20
            result = x + y
        
        # Check that debugging was recorded
        timeline = debugger.get_timeline()
        self.assertGreater(len(timeline), 0)
        
        # Verify we can access the results
        variables = debugger.get_variables_at_time(timeline[0].timestamp)
        self.assertIn('locals', variables)
        self.assertIn('globals', variables)
    
    def test_context_manager_with_function_calls(self):
        """Test TimeTravelContext with function calls"""
        
        def helper_function(n):
            return n * 2
        
        with TimeTravelContext() as debugger:
            result = helper_function(21)
            self.assertEqual(result, 42)
        
        timeline = debugger.get_timeline()
        self.assertGreater(len(timeline), 0)
        
        # Check for function calls
        call_states = debugger.get_states_by_event('call')
        self.assertGreater(len(call_states), 0)
    
    def test_context_manager_with_save_session(self):
        """Test TimeTravelContext with session saving"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            session_file = Path(temp_dir) / "test_session.json"
            
            with TimeTravelContext(save_session=True, session_name=str(session_file)):
                x = 42
                y = x * 2
            
            # Verify session file was created
            self.assertTrue(session_file.exists())


class TestGlobalDebugging(unittest.TestCase):
    
    def setUp(self):
        """Ensure global debugging is stopped before each test"""
        try:
            stop_global_debugging()
        except:
            pass
    
    def tearDown(self):
        """Clean up global debugging after each test"""
        try:
            stop_global_debugging()
        except:
            pass
    
    def test_global_debugging_lifecycle(self):
        """Test global debugging start/stop"""
        
        # Start global debugging
        start_global_debugging()
        
        # Execute some code
        x = 10
        y = 20
        result = x + y
        
        # Stop global debugging
        stop_global_debugging()
        
        # Get timeline
        timeline = get_global_timeline()
        self.assertGreater(len(timeline), 0)
    
    def test_global_debugging_with_functions(self):
        """Test global debugging with function calls"""
        
        def test_function(n):
            return n * 3
        
        start_global_debugging()
        
        result = test_function(14)
        self.assertEqual(result, 42)
        
        stop_global_debugging()
        
        timeline = get_global_timeline()
        self.assertGreater(len(timeline), 0)
        
        # Check for function calls
        call_events = [s for s in timeline if s.frame_info.get('event') == 'call']
        self.assertGreater(len(call_events), 0)


class TestUtilityFunctions(unittest.TestCase):
    
    def test_debug_function(self):
        """Test debug_function utility"""
        
        def test_func(a, b):
            return a + b
        
        result, debugger = debug_function(test_func, 10, 20)
        
        self.assertEqual(result, 30)
        self.assertIsNotNone(debugger)
        
        timeline = debugger.get_timeline()
        self.assertGreater(len(timeline), 0)
    
    def test_debug_function_with_kwargs(self):
        """Test debug_function with keyword arguments"""
        
        def test_func(a, b, multiplier=1):
            return (a + b) * multiplier
        
        result, debugger = debug_function(test_func, 5, 10, multiplier=2)
        
        self.assertEqual(result, 30)  # (5 + 10) * 2 = 30
        
        timeline = debugger.get_timeline()
        self.assertGreater(len(timeline), 0)
    
    def test_quick_debug(self):
        """Test quick_debug utility"""
        
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
"""
        
        debugger = quick_debug(code)
        
        timeline = debugger.get_timeline()
        self.assertGreater(len(timeline), 0)
        
        # Should have captured recursive calls
        call_events = debugger.get_states_by_event('call')
        # factorial(5) calls factorial(4), factorial(3), etc.
        # So we should have multiple calls
        factorial_calls = [s for s in call_events if 'factorial' in s.frame_info.get('function_name', '')]
        self.assertGreater(len(factorial_calls), 1)
    
    def test_quick_debug_with_globals(self):
        """Test quick_debug with custom globals"""
        
        custom_globals = {
            'PI': 3.14159,
            'custom_var': 'hello world'
        }
        
        code = """
radius = 5
area = PI * radius * radius
message = f"{custom_var}: area = {area}"
"""
        
        debugger = quick_debug(code, custom_globals)
        
        timeline = debugger.get_timeline()
        self.assertGreater(len(timeline), 0)
        
        # Check that custom globals were available
        # We can verify this by checking if the code executed without error
        # and produced a timeline
        self.assertTrue(True)  # If we got here, the code executed successfully


if __name__ == '__main__':
    unittest.main()