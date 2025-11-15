"""Logging configuration module for Python projects.

Version: 2025.10.24

This module provides a flexible logging setup for Python applications, designed for use
in a PyCharm project with a remote Python interpreter on Linux. It includes the
`LoggerConfig` class for configuring loggers with file, syslog, and console handlers,
supporting features like lazy file creation, dynamic log level changes, selectable
handlers (file, syslog, console), configuration file loading, and contextual metadata
(e.g., process ID). The `LazyRotatingFileHandler` class extends the standard
RotatingFileHandler to defer file creation until the first log message, and the
`ContextFilter` class adds process ID metadata to log records. The module is suitable
for multi-program setups, with logs accessible via PyCharm's console, remote file
access, or syslog.

Classes:
    LazyRotatingFileHandler: Custom handler for lazy log file creation with rotation.
    ContextFilter: Filter to add process ID to log records.
    LoggerConfig: Main class for configuring loggers with multiple handlers.

Example:
    >>> config = LoggerConfig(__name__, '/var/log/myapp/program.log', log_level='INFO')
    >>> logger = config.get_logger()
    >>> logger.info('Program started')
    >>> config.disable_console_logging()
"""
# Copyright 2025 <Scott m Goeken>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import logging.handlers
import os
import json
from pathlib import Path

class LazyRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """A custom RotatingFileHandler that defers log file creation until the first log message is emitted.

    Version: 2025.10.24

    This handler extends the standard RotatingFileHandler to support lazy file creation,
    ensuring the log file is only created when a log message is written, reducing unnecessary
    file creation in cases where no logging occurs.

    Args:
        filename (str): Path to the log file.
        max_bytes (int, optional): Maximum file size in bytes before rotation. Defaults to 0 (no rotation).
        backup_count (int, optional): Number of backup files to keep. Defaults to 0 (no backups).
        encoding (str, optional): File encoding. Defaults to None (system default).
        delay (bool, optional): If True, defer file creation until first log message. Defaults to True.
    """
    def __init__(self, filename, max_bytes=0, backup_count=0, encoding=None, delay=True):
        super().__init__(filename, maxBytes=max_bytes, backupCount=backup_count, encoding=encoding, delay=delay)

class ContextFilter(logging.Filter):
    """A filter to add contextual metadata, such as process ID, to log records.

    Version: 2025.10.24

    This filter adds the current process ID (pid) to each log record, enabling
    traceability in multiprocess environments.

    Methods:
        filter(record): Adds the process ID to the log record and returns True.
    """
    def filter(self, record):
        """Add the current process ID to the log record.

        Args:
            record (logging.LogRecord): The log record to be processed.

        Returns:
            bool: Always returns True to allow the log record to be processed.
        """
        record.pid = os.getpid()
        return True

class LoggerConfig:
    """A class to configure a logger with file, syslog, and console handlers for a Python project.

    Version: 2025.10.24.2

    This class provides a flexible logging setup with support for lazy file creation,
    dynamic log level changes, selectable handlers (file, syslog, console), configuration
    file loading, and contextual metadata (process ID). It is designed for use in a
    PyCharm project with a remote Python interpreter on Linux, supporting multiple
    programs. Console logging can be dynamically enabled or disabled.

    Attributes:
        name (str): Logger name, typically the module name (__name__).
        log_file (str): Path to the local log file.
        syslog_facility (str): Syslog facility (e.g., 'user', 'local0').
        use_file_logging (bool): Whether file logging is enabled.
        use_syslog_logging (bool): Whether syslog logging is enabled.
        use_console_logging (bool): Whether console logging is enabled.
        log_level (int): Logging level for the logger (e.g., logging.DEBUG).
        file_log_level (int): Logging level for the file handler.
        syslog_log_level (int): Logging level for the syslog handler.
        console_log_level (int): Logging level for the console handler.
        file_handler (LazyRotatingFileHandler, optional): File handler instance.
        syslog_handler (logging.handlers.SysLogHandler, optional): Syslog handler instance.
        console_handler (logging.StreamHandler, optional): Console handler instance.
        logger (logging.Logger): Configured logger instance.

    Args:
        name (str): Logger name, typically __name__.
        log_file (str): Path to the local log file (e.g., '/var/log/myapp/program.log').
        log_level (str, optional): Default logging level (e.g., 'DEBUG', 'INFO'). Defaults to 'DEBUG'.
        file_log_level (str, optional): Specific log level for file handler. Defaults to log_level.
        syslog_log_level (str, optional): Specific log level for syslog handler. Defaults to max(log_level, INFO).
        console_log_level (str, optional): Specific log level for console handler. Defaults to log_level.
        syslog_facility (str, optional): Syslog facility (e.g., 'user', 'local0'). Defaults to 'user'.
        use_file_logging (bool, optional): Enable file logging initially. Defaults to True.
        use_syslog_logging (bool, optional): Enable syslog logging initially. Defaults to True.
        use_console_logging (bool, optional): Enable console logging initially. Defaults to True.
        config_file (str, optional): Path to a JSON configuration file. Defaults to None.

    Example:
        >>> config = LoggerConfig(__name__, '/var/log/myapp/program.log', log_level='INFO')
        >>> logger = config.get_logger()
        >>> logger.info('Program started')
        >>> config.disable_console_logging()
        >>> config.enable_console_logging()
    """
    def __init__(self, name, log_file, log_level='DEBUG', file_log_level=None, syslog_log_level=None,
                 console_log_level=None, syslog_facility='user', use_file_logging=True, use_syslog_logging=True,
                 use_console_logging=True, config_file=None):
        self.name = name
        self.log_file = log_file
        self.syslog_facility = syslog_facility
        self.use_file_logging = use_file_logging
        self.use_syslog_logging = use_syslog_logging
        self.use_console_logging = use_console_logging
        self.log_level = getattr(logging, log_level.upper(), logging.DEBUG)
        self.file_log_level = getattr(logging, file_log_level.upper(), self.log_level) if file_log_level else self.log_level
        self.syslog_log_level = getattr(logging, syslog_log_level.upper(), max(self.log_level, logging.INFO)) if syslog_log_level else max(self.log_level, logging.INFO)
        self.console_log_level = getattr(logging, console_log_level.upper(), self.log_level) if console_log_level else self.log_level
        self.file_handler = None
        self.syslog_handler = None
        self.console_handler = None
        self.logger = None

        # Load settings from config file if provided
        if config_file:
            self._load_config(config_file)

        self._setup_logger()

    def _load_config(self, config_file):
        """Load logging settings from a JSON configuration file.

        Version: 2025.10.24.2

        Updates instance attributes based on the provided JSON file. If the file cannot
        be loaded or contains invalid settings, a warning is printed, and defaults are used.

        Args:
            config_file (str): Path to the JSON configuration file.

        Raises:
            Exception: If the file cannot be read or parsed, a warning is printed.
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            self.log_file = config.get('log_file', self.log_file)
            self.log_level = getattr(logging, config.get('log_level', 'DEBUG').upper(), logging.DEBUG)
            self.file_log_level = getattr(logging, config.get('file_log_level', 'DEBUG').upper(), self.log_level)
            self.syslog_log_level = getattr(logging, config.get('syslog_log_level', 'INFO').upper(), max(self.log_level, logging.INFO))
            self.console_log_level = getattr(logging, config.get('console_log_level', 'DEBUG').upper(), self.log_level)
            self.syslog_facility = config.get('syslog_facility', self.syslog_facility)
            self.use_file_logging = config.get('use_file_logging', self.use_file_logging)
            self.use_syslog_logging = config.get('use_syslog_logging', self.use_syslog_logging)
            self.use_console_logging = config.get('use_console_logging', self.use_console_logging)
        except Exception as e:
            # Log to console if logger isn't set up yet
            print(f"Failed to load config file {config_file}: {e}")

    def _setup_logger(self):
        """Configure the logger with file, syslog, and console handlers based on settings.

        Version: 2025.10.24.2

        Sets up the logger with the specified name, adds a context filter for process ID,
        and configures handlers (file, syslog, console) based on initialization settings.
        Ensures no duplicate handlers are added if the logger is reused.

        Raises:
            Exception: If syslog handler configuration fails, a warning is logged.
        """
        # Create a logger with the specified name
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)  # Set initial logger level
        self.logger.addFilter(ContextFilter())  # Add context filter for PID

        # Avoid duplicate handlers if logger is reused
        if not self.logger.handlers:
            # Formatter with PID for consistent log format
            log_format = logging.Formatter(
                '%(asctime)s [%(levelname)s] pid=%(pid)d %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # File handler with lazy creation and rotation
            if self.use_file_logging:
                log_dir = Path(self.log_file).parent
                log_dir.mkdir(parents=True, exist_ok=True)
                self.file_handler = LazyRotatingFileHandler(
                    self.log_file,
                    max_bytes=5 * 1024 * 1024,
                    backup_count=5,
                    delay=True
                )
                self.file_handler.setLevel(self.file_log_level)
                self.file_handler.setFormatter(log_format)
                self.logger.addHandler(self.file_handler)

            # Syslog handler (Linux-specific)
            if self.use_syslog_logging:
                try:
                    self.syslog_handler = logging.handlers.SysLogHandler(
                        address='/dev/log',
                        facility=self.syslog_facility
                    )
                    self.syslog_handler.setLevel(self.syslog_log_level)
                    self.syslog_handler.setFormatter(log_format)
                    self.logger.addHandler(self.syslog_handler)
                except Exception as e:
                    self.logger.warning(f"Failed to configure syslog handler: {e}")

            # Console handler for local debugging in PyCharm
            if self.use_console_logging:
                self.console_handler = logging.StreamHandler()
                self.console_handler.setLevel(self.console_log_level)
                self.console_handler.setFormatter(log_format)
                self.logger.addHandler(self.console_handler)

    def set_log_level(self, log_level):
        """Change the logging level for the logger and all handlers.

        Version: 2025.10.24

        Updates the logger's log level and propagates the change to all active handlers.
        The syslog handler maintains a minimum level of INFO to reduce noise.

        Args:
            log_level (str): New logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').

        Example:
            >>> config = LoggerConfig(__name__, '/var/log/myapp/program.log', log_level='INFO')
            >>> config.set_log_level('INFO')
        """
        new_level = getattr(logging, log_level.upper(), logging.DEBUG)
        self.log_level = new_level
        self.logger.setLevel(new_level)
        if self.file_handler:
            self.file_log_level = new_level
            self.file_handler.setLevel(new_level)
        if self.syslog_handler:
            self.syslog_log_level = max(new_level, logging.INFO)
            self.syslog_handler.setLevel(self.syslog_log_level)
        if self.console_handler:
            self.console_log_level = new_level
            self.console_handler.setLevel(new_level)
        self.logger.info(f"Log level changed to {log_level.upper()} for logger and all handlers")

    def set_file_log_level(self, log_level):
        """Change the logging level for the file handler.

        Version: 2025.10.24

        Updates the log level for the file handler if it is enabled. If the handler is not
        enabled, a warning is logged.

        Args:
            log_level (str): New logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').

        Example:
            >>> config = LoggerConfig(__name__, '/var/log/myapp/program.log', log_level='INFO')
            >>> config.set_file_log_level('DEBUG')
        """
        if not self.use_file_logging or not self.file_handler:
            self.logger.warning("File handler is not enabled; cannot change log level")
            return
        new_level = getattr(logging, log_level.upper(), logging.DEBUG)
        self.file_log_level = new_level
        self.file_handler.setLevel(new_level)
        self.logger.info(f"File handler log level changed to {log_level.upper()}")

    def set_syslog_log_level(self, log_level):
        """Change the logging level for the syslog handler.

        Version: 2025.10.24

        Updates the log level for the syslog handler if it is enabled, ensuring it remains
        at INFO or above to reduce noise. If the handler is not enabled, a warning is logged.

        Args:
            log_level (str): New logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').

        Example:
            >>> config = LoggerConfig(__name__, '/var/log/myapp/program.log', log_level='INFO')
            >>> config.set_syslog_log_level('WARNING')
        """
        if not self.use_syslog_logging or not self.syslog_handler:
            self.logger.warning("Syslog handler is not enabled; cannot change log level")
            return
        new_level = getattr(logging, log_level.upper(), logging.DEBUG)
        self.syslog_log_level = max(new_level, logging.INFO)
        self.syslog_handler.setLevel(self.syslog_log_level)
        self.logger.info(f"Syslog handler log level changed to {log_level.upper()}")

    def set_console_log_level(self, log_level):
        """Change the logging level for the console handler.

        Version: 2025.10.24

        Updates the log level for the console handler if it is enabled. If the handler is not
        enabled, a warning is logged.

        Args:
            log_level (str): New logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').

        Example:
            >>> config = LoggerConfig(__name__, '/var/log/myapp/program.log', log_level='INFO')
            >>> config.set_console_log_level('ERROR')
        """
        if not self.use_console_logging or not self.console_handler:
            self.logger.warning("Console handler is not enabled; cannot change log level")
            return
        new_level = getattr(logging, log_level.upper(), logging.DEBUG)
        self.console_log_level = new_level
        self.console_handler.setLevel(new_level)
        self.logger.info(f"Console handler log level changed to {log_level.upper()}")

    def enable_file_logging(self):
        """Enable file logging if not already enabled.

        Version: 2025.10.24

        Creates and adds a LazyRotatingFileHandler with the configured log file path
        and settings. Logs a message to confirm activation.

        Example:
            >>> config = LoggerConfig(__name__, '/var/log/myapp/program.log', log_level='INFO')
            >>> config.enable_file_logging()
        """
        if not self.use_file_logging:
            log_dir = Path(self.log_file).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            self.file_handler = LazyRotatingFileHandler(
                self.log_file,
                max_bytes=5 * 1024 * 1024,
                backup_count=5,
                delay=True
            )
            log_format = logging.Formatter(
                '%(asctime)s [%(levelname)s] pid=%(pid)d %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            self.file_handler.setLevel(self.file_log_level)
            self.file_handler.setFormatter(log_format)
            self.logger.addHandler(self.file_handler)
            self.use_file_logging = True
            self.logger.info("File logging enabled")

    def disable_file_logging(self):
        """Disable file logging if enabled.

        Version: 2025.10.24

        Removes and closes the file handler if active, freeing resources. Logs a message
        to confirm deactivation.

        Example:
            >>> config = LoggerConfig(__name__, '/var/log/myapp/program.log', log_level='INFO')
            >>> config.disable_file_logging()
        """
        if self.use_file_logging and self.file_handler:
            self.logger.removeHandler(self.file_handler)
            self.file_handler.close()
            self.file_handler = None
            self.use_file_logging = False
            self.logger.info("File logging disabled")

    def enable_syslog_logging(self):
        """Enable syslog logging if not already enabled.

        Version: 2025.10.24

        Creates and adds a SysLogHandler with the configured facility and settings.
        Logs a message to confirm activation or a warning if configuration fails.

        Raises:
            Exception: If syslog handler configuration fails, a warning is logged.

        Example:
            >>> config = LoggerConfig(__name__, '/var/log/myapp/program.log', log_level='INFO')
            >>> config.enable_syslog_logging()
        """
        if not self.use_syslog_logging:
            try:
                self.syslog_handler = logging.handlers.SysLogHandler(
                    address='/dev/log',
                    facility=self.syslog_facility
                )
                log_format = logging.Formatter(
                    '%(asctime)s [%(levelname)s] pid=%(pid)d %(name)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                self.syslog_handler.setLevel(self.syslog_log_level)
                self.syslog_handler.setFormatter(log_format)
                self.logger.addHandler(self.syslog_handler)
                self.use_syslog_logging = True
                self.logger.info("Syslog logging enabled")
            except Exception as e:
                self.logger.warning(f"Failed to enable syslog handler: {e}")

    def disable_syslog_logging(self):
        """Disable syslog logging if enabled.

        Version: 2025.10.24

        Removes and closes the syslog handler if active, freeing resources. Logs a message
        to confirm deactivation.

        Example:
            >>> config = LoggerConfig(__name__, '/var/log/myapp/program.log', log_level='INFO')
            >>> config.disable_syslog_logging()
        """
        if self.use_syslog_logging and self.syslog_handler:
            self.logger.removeHandler(self.syslog_handler)
            self.syslog_handler.close()
            self.syslog_handler = None
            self.use_syslog_logging = False
            self.logger.info("Syslog logging disabled")

    def enable_console_logging(self):
        """Enable console logging if not already enabled.

        Version: 2025.10.24

        Creates and adds a StreamHandler for console output with the configured settings.
        Logs a message to confirm activation.

        Example:
            >>> config = LoggerConfig(__name__, '/var/log/myapp/program.log', log_level='INFO')
            >>> config.enable_console_logging()
        """
        if not self.use_console_logging:
            log_format = logging.Formatter(
                '%(asctime)s [%(levelname)s] pid=%(pid)d %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            self.console_handler = logging.StreamHandler()
            self.console_handler.setLevel(self.console_log_level)
            self.console_handler.setFormatter(log_format)
            self.logger.addHandler(self.console_handler)
            self.use_console_logging = True
            self.logger.info("Console logging enabled")

    def disable_console_logging(self):
        """Disable console logging if enabled.

        Version: 2025.10.24

        Removes and closes the console handler if active, freeing resources. Logs a message
        to confirm deactivation.

        Example:
            >>> config = LoggerConfig(__name__, '/var/log/myapp/program.log', log_level='INFO')
            >>> config.disable_console_logging()
        """
        if self.use_console_logging and self.console_handler:
            self.logger.removeHandler(self.console_handler)
            self.console_handler.close()
            self.console_handler = None
            self.use_console_logging = False
            self.logger.info("Console logging disabled")

    def get_logger(self):
        """Return the configured logger instance.

        Version: 2025.10.24

        Returns:
            logging.Logger: The configured logger instance with all handlers and settings applied.

        Example:
            >>> config = LoggerConfig(__name__, '/var/log/myapp/program.log', log_level='INFO')
            >>> logger = config.get_logger()
            >>> logger.debug('Debug message')
        """
        return self.logger

    def get_handler_status(self):
        """Return the status of the logger's handlers.

        Version: 2025.10.24

        Provides a dictionary with the enabled status and log level for each handler
        (file, syslog, console) and the logger's overall log level.

        Returns:
            dict: Status of handlers and logger, with keys 'file', 'syslog', 'console', and 'logger_level'.
                  Each handler entry includes 'enabled' (bool) and 'level' (str or 'N/A').

        Example:
            >>> config = LoggerConfig(__name__, '/var/log/myapp/program.log', log_level='INFO')
            >>> my_status = config.get_handler_status()
            >>> print(my_status)
            {'file': {'enabled': True, 'level': 'DEBUG'}, 'syslog': {'enabled': True, 'level': 'INFO'},
             'console': {'enabled': True, 'level': 'DEBUG'}, 'logger_level': 'INFO'}
        """
        status = {
            'file': {
                'enabled': self.use_file_logging,
                'level': logging.getLevelName(self.file_log_level) if self.file_handler else 'N/A'
            },
            'syslog': {
                'enabled': self.use_syslog_logging,
                'level': logging.getLevelName(self.syslog_log_level) if self.syslog_handler else 'N/A'
            },
            'console': {
                'enabled': self.use_console_logging,
                'level': logging.getLevelName(self.console_log_level) if self.console_handler else 'N/A'
            },
            'logger_level': logging.getLevelName(self.log_level)
        }
        return status
