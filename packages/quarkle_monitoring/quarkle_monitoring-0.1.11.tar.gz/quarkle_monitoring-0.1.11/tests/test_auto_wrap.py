"""Tests for auto_wrap module."""

import pytest
import sys
from unittest.mock import Mock, patch
from types import ModuleType

from quarkle_monitoring.auto_wrap import auto_wrap_modules


class TestAutoWrapModules:
    """Test auto_wrap_modules function."""

    def _create_test_function(self, name, module_name, body=None):
        """Helper to create a test function with correct __module__ attribute."""
        if body is None:
            body = lambda: f"result from {name}"

        func = body
        func.__name__ = name
        func.__module__ = module_name
        return func

    def test_basic_module_wrapping(self):
        """Test basic module function wrapping."""
        # Create a test module
        test_module = ModuleType("test_module")

        test_function = self._create_test_function(
            "test_function", "test_module", lambda: "success"
        )
        another_function = self._create_test_function(
            "another_function",
            "test_module",
            lambda: exec('raise Exception("Test error")'),
        )

        test_module.test_function = test_function
        test_module.another_function = another_function

        # Add to sys.modules
        sys.modules["test_module"] = test_module

        try:
            # Mock error tracker
            error_tracker = Mock()

            # Wrap the module
            wrapped_count = auto_wrap_modules(
                module_names=["test_module"], error_tracker_func=error_tracker
            )

            assert wrapped_count == 2

            # Test successful function still works
            result = test_module.test_function()
            assert result == "success"
            error_tracker.assert_not_called()

            # Test error function triggers tracking
            with pytest.raises(Exception, match="Test error"):
                test_module.another_function()

            error_tracker.assert_called_once()
            call_args = error_tracker.call_args[1]
            assert call_args["error_code"] == 500
            assert call_args["endpoint"] == "another_function"
            assert call_args["error_message"] == "Test error"
            assert call_args["extra"]["function"] == "another_function"
            assert call_args["extra"]["exception_type"] == "Exception"

        finally:
            # Clean up
            if "test_module" in sys.modules:
                del sys.modules["test_module"]

    def test_skip_private_functions(self):
        """Test that private functions are skipped by default."""
        test_module = ModuleType("test_private")

        public_function = self._create_test_function(
            "public_function", "test_private", lambda: "public"
        )
        private_function = self._create_test_function(
            "_private_function", "test_private", lambda: "private"
        )

        test_module.public_function = public_function
        test_module._private_function = private_function

        sys.modules["test_private"] = test_module

        try:
            error_tracker = Mock()

            wrapped_count = auto_wrap_modules(
                module_names=["test_private"],
                error_tracker_func=error_tracker,
                skip_private=True,
            )

            # Only public function should be wrapped
            assert wrapped_count == 1

        finally:
            if "test_private" in sys.modules:
                del sys.modules["test_private"]

    def test_include_private_functions(self):
        """Test that private functions can be included."""
        test_module = ModuleType("test_include_private")

        public_function = self._create_test_function(
            "public_function", "test_include_private", lambda: "public"
        )
        private_function = self._create_test_function(
            "_private_function", "test_include_private", lambda: "private"
        )

        test_module.public_function = public_function
        test_module._private_function = private_function

        sys.modules["test_include_private"] = test_module

        try:
            error_tracker = Mock()

            wrapped_count = auto_wrap_modules(
                module_names=["test_include_private"],
                error_tracker_func=error_tracker,
                skip_private=False,
            )

            # Both functions should be wrapped
            assert wrapped_count == 2

        finally:
            if "test_include_private" in sys.modules:
                del sys.modules["test_include_private"]

    def test_skip_patterns(self):
        """Test skipping functions based on patterns."""
        test_module = ModuleType("test_patterns")

        user_function = self._create_test_function(
            "user_function", "test_patterns", lambda: "user"
        )
        test_helper = self._create_test_function(
            "test_helper", "test_patterns", lambda: "test"
        )
        setup_function = self._create_test_function(
            "setup_function", "test_patterns", lambda: "setup"
        )

        test_module.user_function = user_function
        test_module.test_helper = test_helper
        test_module.setup_function = setup_function

        sys.modules["test_patterns"] = test_module

        try:
            error_tracker = Mock()

            wrapped_count = auto_wrap_modules(
                module_names=["test_patterns"],
                error_tracker_func=error_tracker,
                skip_patterns=["test", "setup"],
            )

            # Only user_function should be wrapped (others contain skip patterns)
            assert wrapped_count == 1

        finally:
            if "test_patterns" in sys.modules:
                del sys.modules["test_patterns"]

    def test_context_getter(self):
        """Test context getter functionality."""
        test_module = ModuleType("test_context")

        def failing_func():
            raise Exception("Context test")

        failing_function = self._create_test_function(
            "failing_function", "test_context", failing_func
        )
        test_module.failing_function = failing_function

        sys.modules["test_context"] = test_module

        try:
            error_tracker = Mock()

            def mock_context_getter():
                return {"user_id": "user123", "session_id": "sess456"}

            wrapped_count = auto_wrap_modules(
                module_names=["test_context"],
                error_tracker_func=error_tracker,
                context_getter=mock_context_getter,
            )

            assert wrapped_count == 1

            # Trigger error to test context
            with pytest.raises(Exception):
                test_module.failing_function()

            call_args = error_tracker.call_args[1]
            assert call_args["extra"]["user_id"] == "user123"
            assert call_args["extra"]["session_id"] == "sess456"

        finally:
            if "test_context" in sys.modules:
                del sys.modules["test_context"]

    def test_context_getter_exception(self):
        """Test handling of context getter exceptions."""
        test_module = ModuleType("test_context_error")

        def failing_func():
            raise Exception("Test error")

        failing_function = self._create_test_function(
            "failing_function", "test_context_error", failing_func
        )
        test_module.failing_function = failing_function

        sys.modules["test_context_error"] = test_module

        try:
            error_tracker = Mock()

            def failing_context_getter():
                raise Exception("Context error")

            wrapped_count = auto_wrap_modules(
                module_names=["test_context_error"],
                error_tracker_func=error_tracker,
                context_getter=failing_context_getter,
            )

            assert wrapped_count == 1

            # Should still work even if context getter fails
            with pytest.raises(Exception, match="Test error"):
                test_module.failing_function()

            error_tracker.assert_called_once()

        finally:
            if "test_context_error" in sys.modules:
                del sys.modules["test_context_error"]

    def test_multiple_module_names(self):
        """Test wrapping functions from multiple modules."""
        # Create two test modules
        module1 = ModuleType("multi_test1")
        module2 = ModuleType("multi_test2")

        func1 = self._create_test_function("func1", "multi_test1", lambda: "func1")
        func2 = self._create_test_function("func2", "multi_test2", lambda: "func2")

        module1.func1 = func1
        module2.func2 = func2

        sys.modules["multi_test1"] = module1
        sys.modules["multi_test2"] = module2

        try:
            error_tracker = Mock()

            wrapped_count = auto_wrap_modules(
                module_names=["multi_test1", "multi_test2"],
                error_tracker_func=error_tracker,
            )

            assert wrapped_count == 2

        finally:
            for name in ["multi_test1", "multi_test2"]:
                if name in sys.modules:
                    del sys.modules[name]

    def test_module_name_variations(self):
        """Test that module name variations are tried."""
        # Create module with app. prefix
        app_module = ModuleType("app.test_variations")

        test_func = self._create_test_function(
            "test_func", "app.test_variations", lambda: "test"
        )
        app_module.test_func = test_func

        sys.modules["app.test_variations"] = app_module

        try:
            error_tracker = Mock()

            # Try to wrap using base name
            wrapped_count = auto_wrap_modules(
                module_names=["test_variations"], error_tracker_func=error_tracker
            )

            assert wrapped_count == 1

        finally:
            if "app.test_variations" in sys.modules:
                del sys.modules["app.test_variations"]

    def test_nonexistent_module(self):
        """Test handling of nonexistent modules."""
        error_tracker = Mock()

        wrapped_count = auto_wrap_modules(
            module_names=["nonexistent_module"], error_tracker_func=error_tracker
        )

        assert wrapped_count == 0

    def test_non_callable_attributes_ignored(self):
        """Test that non-callable attributes are ignored."""
        test_module = ModuleType("test_non_callable")

        callable_func = self._create_test_function(
            "callable_func", "test_non_callable", lambda: "callable"
        )

        test_module.callable_func = callable_func
        test_module.string_attr = "not callable"
        test_module.number_attr = 42
        test_module.list_attr = [1, 2, 3]

        sys.modules["test_non_callable"] = test_module

        try:
            error_tracker = Mock()

            wrapped_count = auto_wrap_modules(
                module_names=["test_non_callable"], error_tracker_func=error_tracker
            )

            # Only the callable function should be wrapped
            assert wrapped_count == 1

        finally:
            if "test_non_callable" in sys.modules:
                del sys.modules["test_non_callable"]

    def test_exception_with_status_code(self):
        """Test error tracking with exception that has status_code."""
        test_module = ModuleType("test_status_code")

        def failing_func():
            error = Exception("Custom error")
            error.status_code = 422
            raise error

        failing_function = self._create_test_function(
            "failing_function", "test_status_code", failing_func
        )
        test_module.failing_function = failing_function

        sys.modules["test_status_code"] = test_module

        try:
            error_tracker = Mock()

            wrapped_count = auto_wrap_modules(
                module_names=["test_status_code"], error_tracker_func=error_tracker
            )

            assert wrapped_count == 1

            with pytest.raises(Exception):
                test_module.failing_function()

            call_args = error_tracker.call_args[1]
            assert call_args["error_code"] == 422

        finally:
            if "test_status_code" in sys.modules:
                del sys.modules["test_status_code"]

    def test_functions_without_module_attribute_ignored(self):
        """Test that functions without __module__ attribute are ignored."""
        test_module = ModuleType("test_no_module_attr")

        # Create function without __module__ attribute
        def func_without_module():
            return "test"

        # Remove __module__ attribute
        delattr(func_without_module, "__module__")

        # Create function with correct __module__
        good_func = self._create_test_function(
            "good_func", "test_no_module_attr", lambda: "good"
        )

        test_module.func_without_module = func_without_module
        test_module.good_func = good_func

        sys.modules["test_no_module_attr"] = test_module

        try:
            error_tracker = Mock()

            wrapped_count = auto_wrap_modules(
                module_names=["test_no_module_attr"], error_tracker_func=error_tracker
            )

            # Only the function with correct __module__ should be wrapped
            assert wrapped_count == 1

        finally:
            if "test_no_module_attr" in sys.modules:
                del sys.modules["test_no_module_attr"]
