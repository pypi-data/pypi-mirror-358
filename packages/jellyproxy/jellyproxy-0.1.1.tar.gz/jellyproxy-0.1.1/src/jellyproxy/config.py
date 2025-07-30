"""
Configuration management for JellyProxy using JSON.

Handles loading, validation, and management of proxy configuration settings
with a pattern-based filtering system.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class FilterRule:
    """Represents a single filtering rule with regex pattern matching."""

    def __init__(self, rule_data: Dict[str, Any]):
        """Initialize a filter rule from JSON data."""
        self.command_pattern = rule_data.get("command", [])
        self.comment = rule_data.get("#", "")

        # Compile regex patterns for efficiency
        self._compiled_patterns = []
        for pattern in self.command_pattern:
            if isinstance(pattern, str):
                try:
                    self._compiled_patterns.append(re.compile(pattern))
                except re.error:
                    # Invalid regex, treat as literal string by escaping it
                    self._compiled_patterns.append(re.compile(re.escape(pattern)))
            else:
                # Non-string patterns, convert to string and escape
                self._compiled_patterns.append(re.compile(re.escape(str(pattern))))

    def matches(self, command: List[Any]) -> bool:
        """Check if this rule matches the given command."""
        if len(self._compiled_patterns) != len(command):
            return False

        for i, compiled_pattern in enumerate(self._compiled_patterns):
            command_part = str(command[i])
            if not compiled_pattern.match(command_part):
                return False

        return True

    def update_from_args(self, args: Dict[str, Any]):
        """Update configuration from command line arguments."""
        # Socket configuration
        if args.get('socket_dir'):
            self.socket_dir = Path(args['socket_dir'])
            self.spoof_socket_path = self.socket_dir / "spoof"
            self.real_socket_path = self.socket_dir / "real"

        if args.get('spoof_socket'):
            self.spoof_socket_path = Path(args['spoof_socket'])

        if args.get('real_socket'):
            self.real_socket_path = Path(args['real_socket'])

        # Logging configuration
        if args.get('debug'):
            self.log_level = "DEBUG"

        if args.get('verbose'):
            self.log_level = "DEBUG"

        if args.get('quiet'):
            self.log_to_console = False

        if args.get('log_file'):
            self.log_to_file = True
            self.log_file_path = args['log_file']

        # JMS configuration
        if args.get('no_auto_start_jms'):
            self.auto_start_jms = False

        if args.get('jms_args'):
            self.jms_args = args['jms_args']

    def __repr__(self) -> str:
        return f"FilterRule({self.command_pattern})"


class ProxyConfig:
    """Configuration manager for JellyProxy using JSON."""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration with default values."""
        self.config_file = config_file

        # Default configuration values
        self._load_defaults()

        # Load default configuration if it exists
        default_config = self._get_default_config_path()
        if default_config and default_config.exists():
            try:
                self.load_config(str(default_config))
            except Exception as e:
                # Don't fail on default config errors, just use defaults
                pass

        # Load user-specified configuration file if provided (overrides default)
        if config_file:
            self.load_config(config_file)

    def _get_default_config_path(self) -> Optional[Path]:
        """Get the default configuration file path using XDG_CONFIG_DIR."""
        import os

        # Get XDG_CONFIG_HOME or fall back to ~/.config
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config_home:
            config_dir = Path(xdg_config_home)
        else:
            config_dir = Path.home() / '.config'

        return config_dir / 'jellyproxy' / 'conf.json'

    def _load_defaults(self):
        """Load default configuration values."""
        # Socket configuration
        self.socket_dir = Path("/tmp/mpvSockets")
        self.spoof_socket_path = self.socket_dir / "spoof"
        self.real_socket_path = self.socket_dir / "real"
        self.socket_dir_permissions = 0o700
        self.socket_permissions = 0o600

        # MPV configuration
        self.mpv_binary = "mpv"
        self.mpv_config = {
            "keep_open": False,
            "force_window": False,
            "osc": False,
            "idle": True,
            "input_terminal": False,
            "terminal": False,
            "script_opts": "mpvSockets-enabled=no"
        }

        # JMS configuration
        self.jms_binary = "jellyfin-mpv-shim"
        self.jms_args = []  # No default arguments
        self.auto_start_jms = True

        # Filtering configuration
        self.blacklist_rules: List[FilterRule] = []
        self.whitelist_rules: List[FilterRule] = []

        # Logging configuration
        self.log_level = "INFO"
        self.log_to_console = True
        self.log_to_file = False
        self.log_file_path = None
        self.log_ipc_messages = True
        self.log_filtered_commands = True

        # Process management
        self.mpv_restart_on_crash = True
        self.mpv_max_restart_attempts = 3
        self.process_monitor_interval = 1.0

        # Advanced features
        self.enable_health_checks = False
        self.health_check_interval = 30.0

    def load_config(self, config_file: str):
        """Load configuration from JSON file."""
        config_path = Path(config_file)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")

        self.config_file = config_file
        self._apply_config_data(config_data)

    def _apply_config_data(self, config_data: Dict[str, Any]):
        """Apply configuration data from loaded JSON."""
        # Socket configuration
        if "sockets" in config_data:
            sockets = config_data["sockets"]
            if "directory" in sockets:
                self.socket_dir = Path(sockets["directory"])
                self.spoof_socket_path = self.socket_dir / "spoof"
                self.real_socket_path = self.socket_dir / "real"
            if "spoof_socket" in sockets:
                self.spoof_socket_path = Path(sockets["spoof_socket"])
            if "real_socket" in sockets:
                self.real_socket_path = Path(sockets["real_socket"])
            if "directory_permissions" in sockets:
                self.socket_dir_permissions = int(sockets["directory_permissions"], 8)
            if "socket_permissions" in sockets:
                self.socket_permissions = int(sockets["socket_permissions"], 8)

        # MPV configuration
        if "mpv" in config_data:
            mpv_config = config_data["mpv"]
            if "binary" in mpv_config:
                self.mpv_binary = mpv_config["binary"]
            if "config" in mpv_config:
                self.mpv_config.update(mpv_config["config"])

        # JMS configuration
        if "jms" in config_data:
            jms_config = config_data["jms"]
            if "binary" in jms_config:
                self.jms_binary = jms_config["binary"]
            if "args" in jms_config:
                self.jms_args = jms_config["args"]
            if "auto_start" in jms_config:
                self.auto_start_jms = jms_config["auto_start"]

        # Filtering configuration - load blacklist and whitelist directly
        if "blacklist" in config_data:
            self.blacklist_rules = [FilterRule(rule) for rule in config_data["blacklist"]]

        if "whitelist" in config_data:
            self.whitelist_rules = [FilterRule(rule) for rule in config_data["whitelist"]]

        # Legacy configuration (kept for backwards compatibility in transition)
        if "filtering" in config_data:
            filtering = config_data["filtering"]

            # Load blacklist rules from nested structure
            if "blacklist" in filtering:
                self.blacklist_rules.extend([FilterRule(rule) for rule in filtering["blacklist"]])

            # Load whitelist rules from nested structure
            if "whitelist" in filtering:
                self.whitelist_rules.extend([FilterRule(rule) for rule in filtering["whitelist"]])

            # Legacy property-based filtering
            if "blocked_properties" in filtering:
                self.blocked_properties = set(filtering["blocked_properties"])
            if "blocked_commands" in filtering:
                self.blocked_commands = set(filtering["blocked_commands"])
            if "property_overrides" in filtering:
                self.property_overrides = filtering["property_overrides"]

        # Logging configuration
        if "logging" in config_data:
            logging_config = config_data["logging"]
            if "level" in logging_config:
                self.log_level = logging_config["level"].upper()
            if "console" in logging_config:
                self.log_to_console = logging_config["console"]
            if "file" in logging_config:
                if isinstance(logging_config["file"], str):
                    self.log_to_file = True
                    self.log_file_path = logging_config["file"]
                elif isinstance(logging_config["file"], bool):
                    self.log_to_file = logging_config["file"]
            if "ipc_messages" in logging_config:
                self.log_ipc_messages = logging_config["ipc_messages"]
            if "filtered_commands" in logging_config:
                self.log_filtered_commands = logging_config["filtered_commands"]

        # Process management
        if "processes" in config_data:
            processes = config_data["processes"]
            if "mpv_restart_on_crash" in processes:
                self.mpv_restart_on_crash = processes["mpv_restart_on_crash"]
            if "mpv_max_restart_attempts" in processes:
                self.mpv_max_restart_attempts = processes["mpv_max_restart_attempts"]
            if "monitor_interval" in processes:
                self.process_monitor_interval = processes["monitor_interval"]

    def check_command_filter(self, command_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Check if a command should be filtered and return the reason.

        Logic:
        - If command matches whitelist: allow (return False, reason)
        - Elif command matches blacklist: deny (return True, reason)
        - Else: allow (return False, None)

        Returns:
            Tuple[bool, Optional[str]]: (should_filter, reason)
            - should_filter: True if the command should be blocked/filtered
            - reason: String description of why it was filtered (or None if not filtered)
        """
        if "command" not in command_data:
            return False, None

        command = command_data["command"]

        # Check whitelist first - if it matches, always allow
        for rule in self.whitelist_rules:
            if rule.matches(command):
                reason = f"Whitelisted: {rule.comment or str(rule.command_pattern)}"
                return False, reason  # Explicitly allowed

        # Check blacklist - if it matches, deny
        for rule in self.blacklist_rules:
            if rule.matches(command):
                reason = f"Blacklisted: {rule.comment or str(rule.command_pattern)}"
                return True, reason  # Explicitly blocked

        # Default: allow
        return False, None

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []

        # Validate paths
        if not self.socket_dir.parent.exists():
            errors.append(f"Socket directory parent does not exist: {self.socket_dir.parent}")

        # Validate permissions
        if not (0o000 <= self.socket_dir_permissions <= 0o777):
            errors.append(f"Invalid socket directory permissions: {oct(self.socket_dir_permissions)}")

        if not (0o000 <= self.socket_permissions <= 0o777):
            errors.append(f"Invalid socket permissions: {oct(self.socket_permissions)}")

        # Validate log level
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"Invalid log level: {self.log_level}")

        # Validate intervals
        if self.process_monitor_interval <= 0:
            errors.append("Process monitor interval must be positive")

        if self.health_check_interval <= 0:
            errors.append("Health check interval must be positive")

        # Validate filter rules
        for i, rule in enumerate(self.blacklist_rules):
            if not rule.command_pattern:
                errors.append(f"Blacklist rule {i} has empty command pattern")

        for i, rule in enumerate(self.whitelist_rules):
            if not rule.command_pattern:
                errors.append(f"Whitelist rule {i} has empty command pattern")

        return errors

    def get_mpv_args(self) -> List[str]:
        """Generate MPV command line arguments from configuration."""
        args = [self.mpv_binary]

        # Add IPC socket
        args.append(f"--input-ipc-server={self.real_socket_path}")

        # Add configuration options
        for key, value in self.mpv_config.items():
            arg_name = key.replace("_", "-")
            if isinstance(value, bool):
                args.append(f"--{arg_name}={'yes' if value else 'no'}")
            else:
                args.append(f"--{arg_name}={value}")

        return args

    def update_from_args(self, args: Dict[str, Any]):
        """Update configuration from command line arguments."""
        # Socket configuration
        if args.get('socket_dir'):
            self.socket_dir = Path(args['socket_dir'])
            self.spoof_socket_path = self.socket_dir / "spoof"
            self.real_socket_path = self.socket_dir / "real"

        if args.get('spoof_socket'):
            self.spoof_socket_path = Path(args['spoof_socket'])

        if args.get('real_socket'):
            self.real_socket_path = Path(args['real_socket'])

        # Logging configuration
        if args.get('debug'):
            self.log_level = "DEBUG"

        if args.get('verbose'):
            self.log_level = "DEBUG"

        if args.get('quiet'):
            self.log_to_console = False

        if args.get('log_file'):
            self.log_to_file = True
            self.log_file_path = args['log_file']

        # JMS configuration
        if args.get('no_auto_start_jms'):
            self.auto_start_jms = False

        if args.get('jms_args'):
            self.jms_args = args['jms_args']

    def generate_example_config(self) -> Dict[str, Any]:
        """Generate an example configuration with documentation."""
        return {
            "#": "JellyProxy Configuration File",
            "sockets": {
                "#": "Socket configuration for IPC communication",
                "directory": "/tmp/mpvSockets",
                "spoof_socket": "/tmp/mpvSockets/spoof",
                "real_socket": "/tmp/mpvSockets/real",
                "directory_permissions": "0o700",
                "socket_permissions": "0o600"
            },
            "mpv": {
                "#": "MPV player configuration",
                "binary": "mpv",
                "config": {
                    "keep_open": False,
                    "force_window": False,
                    "osc": False,
                    "idle": True,
                    "input_terminal": False,
                    "terminal": False,
                    "script_opts": "mpvSockets-enabled=no"
                }
            },
            "jms": {
                "#": "Jellyfin MPV Shim configuration",
                "binary": "jellyfin-mpv-shim",
                "args": [],
                "auto_start": True
            },
            "blacklist": [
                {
                    "#": "Block all set_property commands to prevent JMS from overriding settings",
                    "command": ["set_property", ".*", ".*"]
                },
                {
                    "#": "Block key binding commands for specific keys",
                    "command": ["keybind", "(q|esc|enter)", ".*"]
                }
            ],
            "whitelist": [
                {
                    "#": "Allow JMS to set subtitle color",
                    "command": ["set_property", "sub-color", ".*"]
                },
                {
                    "#": "Allow JMS to control playback",
                    "command": ["(pause|play|stop|seek)", ".*"]
                }
            ],
            "logging": {
                "#": "Logging configuration",
                "level": "INFO",
                "console": True,
                "file": "/var/log/jellyproxy.log",
                "ipc_messages": True,
                "filtered_commands": True
            },
            "processes": {
                "#": "Process management configuration",
                "mpv_restart_on_crash": True,
                "mpv_max_restart_attempts": 3,
                "monitor_interval": 1.0
            }
        }

    def save_example_config(self, file_path: str):
        """Save an example configuration file."""
        example = self.generate_example_config()
        with open(file_path, 'w') as f:
            json.dump(example, f, indent=2)

    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"ProxyConfig("
            f"socket_dir={self.socket_dir}, "
            f"blacklist_rules={len(self.blacklist_rules)}, "
            f"whitelist_rules={len(self.whitelist_rules)}, "
            f"log_level={self.log_level})"
        )
