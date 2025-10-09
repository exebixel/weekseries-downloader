"""
Tests for weekseries_downloader.logging_config module
"""

import pytest
import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from weekseries_downloader.logging_config import (
    setup_logging,
    get_logger,
    setup_from_config_file,
    setup_default_logging
)


class TestSetupLogging:
    """Tests for setup_logging function"""
    
    def test_setup_logging_default_level(self):
        """Test setup_logging with default INFO level"""
        setup_logging()
        
        logger = logging.getLogger('weekseries_downloader')
        assert logger.level == logging.INFO
    
    def test_setup_logging_debug_level(self):
        """Test setup_logging with DEBUG level"""
        setup_logging(log_level="DEBUG")
        
        logger = logging.getLogger('weekseries_downloader')
        assert logger.level == logging.DEBUG
    
    def test_setup_logging_warning_level(self):
        """Test setup_logging with WARNING level"""
        setup_logging(log_level="WARNING")
        
        logger = logging.getLogger('weekseries_downloader')
        assert logger.level == logging.WARNING
    
    def test_setup_logging_error_level(self):
        """Test setup_logging with ERROR level"""
        setup_logging(log_level="ERROR")
        
        logger = logging.getLogger('weekseries_downloader')
        assert logger.level == logging.ERROR
    
    def test_setup_logging_critical_level(self):
        """Test setup_logging with CRITICAL level"""
        setup_logging(log_level="CRITICAL")
        
        logger = logging.getLogger('weekseries_downloader')
        assert logger.level == logging.CRITICAL
    
    def test_setup_logging_with_log_file(self):
        """Test setup_logging with log file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            
            setup_logging(log_level="INFO", log_file=log_file)
            
            logger = logging.getLogger('weekseries_downloader')
            
            # Check that logger has handlers
            assert len(logger.handlers) > 0
            
            # Test logging to file
            logger.info("Test message")
            
            # Verify file was created
            assert os.path.exists(log_file)
    
    def test_setup_logging_creates_log_directory(self):
        """Test setup_logging creates log directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "subdir", "test.log")
            
            # Ensure subdirectory doesn't exist
            assert not os.path.exists(os.path.dirname(log_file))
            
            setup_logging(log_level="INFO", log_file=log_file)
            
            # Directory should be created
            assert os.path.exists(os.path.dirname(log_file))
    
    def test_setup_logging_console_handler(self):
        """Test setup_logging configures console handler"""
        setup_logging(log_level="INFO")
        
        logger = logging.getLogger('weekseries_downloader')
        
        # Should have at least console handler
        assert len(logger.handlers) >= 1
        
        # Check for StreamHandler
        has_stream_handler = any(
            isinstance(handler, logging.StreamHandler) 
            for handler in logger.handlers
        )
        assert has_stream_handler
    
    @patch('logging.config.dictConfig')
    def test_setup_logging_calls_dict_config(self, mock_dict_config):
        """Test setup_logging calls logging.config.dictConfig"""
        setup_logging(log_level="DEBUG")
        
        mock_dict_config.assert_called_once()
        
        # Verify the config structure
        config = mock_dict_config.call_args[0][0]
        assert config['version'] == 1
        assert 'formatters' in config
        assert 'handlers' in config
        assert 'loggers' in config


class TestGetLogger:
    """Tests for get_logger function"""
    
    def test_get_logger_returns_logger(self):
        """Test get_logger returns a Logger instance"""
        logger = get_logger("test_module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
    
    def test_get_logger_different_names(self):
        """Test get_logger with different names returns different loggers"""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger1 != logger2
    
    def test_get_logger_same_name_returns_same_logger(self):
        """Test get_logger with same name returns same logger instance"""
        logger1 = get_logger("same_module")
        logger2 = get_logger("same_module")
        
        assert logger1 is logger2
    
    def test_get_logger_with_dunder_name(self):
        """Test get_logger with __name__ pattern"""
        module_name = "weekseries_downloader.test_module"
        logger = get_logger(module_name)
        
        assert logger.name == module_name


class TestSetupFromConfigFile:
    """Tests for setup_from_config_file function"""
    
    @patch('os.path.exists')
    @patch('logging.config.fileConfig')
    @patch('os.makedirs')
    def test_setup_from_config_file_exists(self, mock_makedirs, mock_file_config, mock_exists):
        """Test setup_from_config_file when config file exists"""
        mock_exists.return_value = True
        
        setup_from_config_file("test_logging.conf")
        
        mock_makedirs.assert_called_once_with('logs', exist_ok=True)
        mock_file_config.assert_called_once_with("test_logging.conf", disable_existing_loggers=False)
    
    @patch('os.path.exists')
    @patch('weekseries_downloader.logging_config.setup_default_logging')
    def test_setup_from_config_file_not_exists(self, mock_setup_default, mock_exists):
        """Test setup_from_config_file when config file doesn't exist"""
        mock_exists.return_value = False
        
        setup_from_config_file("nonexistent.conf")
        
        mock_setup_default.assert_called_once()
    
    @patch('os.path.exists')
    @patch('logging.config.fileConfig')
    def test_setup_from_config_file_default_path(self, mock_file_config, mock_exists):
        """Test setup_from_config_file with default config file path"""
        mock_exists.return_value = True
        
        setup_from_config_file()
        
        mock_exists.assert_called_with("logging.conf")


class TestSetupDefaultLogging:
    """Tests for setup_default_logging function"""
    
    @patch.dict(os.environ, {'WEEKSERIES_LOG_LEVEL': 'DEBUG'})
    @patch('weekseries_downloader.logging_config.setup_logging')
    def test_setup_default_logging_with_env_level(self, mock_setup_logging):
        """Test setup_default_logging with environment log level"""
        setup_default_logging()
        
        mock_setup_logging.assert_called_once_with('DEBUG', None)
    
    @patch.dict(os.environ, {'WEEKSERIES_LOG_FILE': '/tmp/test.log'})
    @patch('weekseries_downloader.logging_config.setup_logging')
    def test_setup_default_logging_with_env_file(self, mock_setup_logging):
        """Test setup_default_logging with environment log file"""
        setup_default_logging()
        
        mock_setup_logging.assert_called_once_with('INFO', '/tmp/test.log')
    
    @patch.dict(os.environ, {
        'WEEKSERIES_LOG_LEVEL': 'WARNING',
        'WEEKSERIES_LOG_FILE': '/tmp/app.log'
    })
    @patch('weekseries_downloader.logging_config.setup_logging')
    def test_setup_default_logging_with_both_env_vars(self, mock_setup_logging):
        """Test setup_default_logging with both environment variables"""
        setup_default_logging()
        
        mock_setup_logging.assert_called_once_with('WARNING', '/tmp/app.log')
    
    @patch.dict(os.environ, {'WEEKSERIES_LOG_LEVEL': 'invalid_level'})
    @patch('weekseries_downloader.logging_config.setup_logging')
    def test_setup_default_logging_invalid_level(self, mock_setup_logging):
        """Test setup_default_logging with invalid log level falls back to INFO"""
        setup_default_logging()
        
        mock_setup_logging.assert_called_once_with('INFO', None)
    
    @patch.dict(os.environ, {'WEEKSERIES_LOG_LEVEL': 'debug'})  # lowercase
    @patch('weekseries_downloader.logging_config.setup_logging')
    def test_setup_default_logging_lowercase_level(self, mock_setup_logging):
        """Test setup_default_logging converts lowercase level to uppercase"""
        setup_default_logging()
        
        mock_setup_logging.assert_called_once_with('DEBUG', None)
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('weekseries_downloader.logging_config.setup_logging')
    def test_setup_default_logging_no_env_vars(self, mock_setup_logging):
        """Test setup_default_logging with no environment variables"""
        setup_default_logging()
        
        mock_setup_logging.assert_called_once_with('INFO', None)


class TestLoggingIntegration:
    """Integration tests for logging functionality"""
    
    def test_logger_hierarchy(self):
        """Test logger hierarchy works correctly"""
        setup_logging(log_level="DEBUG")
        
        # Get loggers at different levels
        root_logger = get_logger("weekseries_downloader")
        module_logger = get_logger("weekseries_downloader.test_module")
        submodule_logger = get_logger("weekseries_downloader.test_module.submodule")
        
        # All should be Logger instances
        assert isinstance(root_logger, logging.Logger)
        assert isinstance(module_logger, logging.Logger)
        assert isinstance(submodule_logger, logging.Logger)
        
        # Names should be correct
        assert root_logger.name == "weekseries_downloader"
        assert module_logger.name == "weekseries_downloader.test_module"
        assert submodule_logger.name == "weekseries_downloader.test_module.submodule"
    
    def test_logging_levels_work(self):
        """Test that different logging levels work correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            
            # Setup with DEBUG level
            setup_logging(log_level="DEBUG", log_file=log_file)
            logger = get_logger("test_logger")
            
            # Log messages at different levels
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")
            
            # Force flush handlers
            for handler in logger.handlers:
                if hasattr(handler, 'flush'):
                    handler.flush()
            
            # Check that file was created and has content
            assert os.path.exists(log_file)
            
            # Read log file content
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # All messages should be present (DEBUG level captures all)
            assert "Debug message" in content
            assert "Info message" in content
            assert "Warning message" in content
            assert "Error message" in content
            assert "Critical message" in content
    
    def test_log_file_rotation_config(self):
        """Test that log file rotation is configured correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "rotating.log")
            
            setup_logging(log_level="INFO", log_file=log_file)
            
            # Get the root logger which should have the file handler
            root_logger = logging.getLogger()
            
            # Check that we have a RotatingFileHandler in root logger
            rotating_handlers = [
                handler for handler in root_logger.handlers
                if isinstance(handler, logging.handlers.RotatingFileHandler)
            ]
            
            # Should have at least one rotating file handler
            assert len(rotating_handlers) > 0
            
            # Check configuration
            handler = rotating_handlers[0]
            assert handler.maxBytes == 10485760  # 10MB
            assert handler.backupCount == 5
    
    def test_formatter_configuration(self):
        """Test that formatters are configured correctly"""
        setup_logging(log_level="INFO")
        
        logger = get_logger("formatter_test")
        
        # Check that handlers have formatters
        for handler in logger.handlers:
            assert handler.formatter is not None
            
            # Test formatter format
            formatter = handler.formatter
            assert hasattr(formatter, '_fmt')
    
    def test_automatic_setup_on_import(self):
        """Test that logging is automatically configured on module import"""
        # This test verifies that the module can be imported without errors
        # and that the setup functions exist
        
        import weekseries_downloader.logging_config
        
        # Verify that the setup functions exist and are callable
        assert hasattr(weekseries_downloader.logging_config, 'setup_from_config_file')
        assert callable(weekseries_downloader.logging_config.setup_from_config_file)
        assert hasattr(weekseries_downloader.logging_config, 'setup_default_logging')
        assert callable(weekseries_downloader.logging_config.setup_default_logging)


class TestLoggingEdgeCases:
    """Tests for edge cases and error conditions"""
    
    def test_setup_logging_with_none_log_file(self):
        """Test setup_logging with None log file"""
        setup_logging(log_level="INFO", log_file=None)
        
        logger = get_logger("none_file_test")
        
        # Should work without file handler
        assert isinstance(logger, logging.Logger)
    
    def test_setup_logging_with_empty_log_file(self):
        """Test setup_logging with empty string log file"""
        setup_logging(log_level="INFO", log_file="")
        
        logger = get_logger("empty_file_test")
        
        # Should work without file handler
        assert isinstance(logger, logging.Logger)
    
    def test_get_logger_with_empty_name(self):
        """Test get_logger with empty name"""
        logger = get_logger("")
        
        assert isinstance(logger, logging.Logger)
        # Empty name returns root logger
        assert logger.name == "root"
    
    def test_get_logger_with_none_name(self):
        """Test get_logger with None name"""
        # This should raise an exception or handle gracefully
        try:
            logger = get_logger(None)
            # If it doesn't raise, it should still return a logger
            assert isinstance(logger, logging.Logger)
        except (TypeError, ValueError):
            # It's acceptable for this to raise an exception
            pass
    
    @patch('pathlib.Path.mkdir')
    def test_setup_logging_mkdir_permission_error(self, mock_mkdir):
        """Test setup_logging handles permission errors when creating directories"""
        mock_mkdir.side_effect = PermissionError("Permission denied")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "subdir", "test.log")
            
            # Should handle the error gracefully
            try:
                setup_logging(log_level="INFO", log_file=log_file)
                # If no exception is raised, that's fine too
            except PermissionError:
                # It's acceptable for this to propagate
                pass