"""
Basic tests for JellyProxy Phase 1

Tests the core functionality of configuration, CLI, and basic setup.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from jellyproxy.config import Config, ConfigError, ProxyConfig, MpvConfig, LoggingConfig
from jellyproxy.main import main, find_config_file, generate_example_config, create_parser


class TestConfig:
    """Test configuration management."""

    def test_default_config(self):
        """Test that default configuration is valid."""
        config = Config()
        config.validate()  # Should not raise

        # Check some defaults
        assert config.proxy.spoof_socket == Path("/tmp/mpvSockets/spoof")
        assert config.proxy.real_socket == Path("/tmp/mpvSockets/real")
        assert config.mpv.binary_path == "mpv"
        assert config.logging.level == "INFO"
        assert config.filtering.mode == "passthrough"

    def test_socket_validation(self):
        """Test socket path validation."""
        config = Config()

        # Same socket paths should fail
        config.proxy.spoof_socket = Path("/tmp/same")
        config.proxy.real_socket = Path("/tmp/same")

        with pytest.raises(ConfigError, match="cannot be the same path"):
            config.validate()

    def test_permission_validation(self):
        """Test socket permission validation."""
        config = Config()

        # Invalid permissions
        config.proxy.socket_dir_permissions = 0o999

        with pytest.raises(ConfigError, match="Invalid socket directory permissions"):
            config.validate()

    def test_logging_level_validation(self):
        """Test logging level validation."""
        config = Config()

        # Invalid logging level
        config.logging.level = "INVALID"

        with pytest.raises(ConfigError, match="Invalid logging level"):
            config.validate()

    def test_filtering_mode_validation(self):
        """Test filtering mode validation."""
        config = Config()

        # Invalid filtering mode
        config.filtering.mode = "invalid"

        with pytest.raises(ConfigError, match="Invalid filtering mode"):
            config.validate()

    def test_mpv_command_generation(self):
        """Test MPV command generation."""
        config = Config()
        cmd = config.get_mpv_command()

        assert cmd[0] == "mpv"
        assert "--keep-open=no" in cmd
        assert "--idle=yes" in cmd
        assert f"--input-ipc-server={config.proxy.real_socket}" in cmd

    def test_socket_directory_creation(self):
        """Test socket directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config()
            config.proxy.spoof_socket = Path(tmpdir) / "test" / "spoof"
            config.proxy.real_socket = Path(tmpdir) / "test" / "real"

            # Directory should not exist yet
            socket_dir = config.get_socket_directory()
            assert not socket_dir.exists()

            # Create directory
            config.ensure_socket_directory()

            # Directory should now exist with correct permissions
            assert socket_dir.exists()
            assert socket_dir.is_dir()
            assert oct(socket_dir.stat().st_mode)[-3:] == "700"


class TestCLI:
    """Test command-line interface."""

    def test_parser_creation(self):
        """Test argument parser creation."""
        parser = create_parser()

        # Test basic arguments
        args = parser.parse_args([])
        assert args.debug is False
        assert args.validate is False
        assert args.generate_config is False

        args = parser.parse_args(["--debug"])
        assert args.debug is True

        args = parser.parse_args(["--config", "/path/to/config"])
        assert args.config == Path("/path/to/config")

    def test_config_file_finding(self):
        """Test configuration file discovery."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test config file
            config_file = Path(tmpdir) / "jellyproxy.toml"
            config_file.write_text("[proxy]\n")

            # Mock Path.cwd() to return our temp directory
            with patch('pathlib.Path.cwd', return_value=Path(tmpdir)):
                found = find_config_file()
                assert found == config_file

    def test_example_config_generation(self):
        """Test example configuration generation."""
        config_text = generate_example_config()

        # Should contain key sections
        assert "[proxy]" in config_text
        assert "[mpv]" in config_text
        assert "[logging]" in config_text
        assert "[filtering]" in config_text

        # Should contain socket paths
        assert "spoof_socket" in config_text
        assert "real_socket" in config_text

    @patch('jellyproxy.main.ProxyServer')
    def test_main_basic_run(self, mock_proxy_server):
        """Test basic main function execution."""
        # Mock the proxy server
        mock_server = MagicMock()
        mock_server.run.return_value = 0
        mock_proxy_server.return_value = mock_server

        # Test with minimal arguments
        with patch('sys.argv', ['jellyproxy']):
            result = main()
            assert result == 0
            mock_proxy_server.assert_called_once()
            mock_server.run.assert_called_once()

    def test_main_generate_config(self, capsys):
        """Test config generation mode."""
        with patch('sys.argv', ['jellyproxy', '--generate-config']):
            result = main()
            assert result == 0

            captured = capsys.readouterr()
            assert "[proxy]" in captured.out

    def test_main_validate_mode(self):
        """Test validation mode."""
        with patch('sys.argv', ['jellyproxy', '--validate']):
            result = main()
            assert result == 0


class TestMpvConfig:
    """Test MPV-specific configuration."""

    def test_default_args(self):
        """Test default MPV arguments."""
        mpv_config = MpvConfig()

        expected_args = [
            "--keep-open=no",
            "--force-window=no",
            "--osc=no",
            "--idle=yes",
            "--input-terminal=no",
            "--terminal=no",
            "--script-opts=mpvSockets-enabled=no"
        ]

        for arg in expected_args:
            assert arg in mpv_config.args

    def test_restart_settings(self):
        """Test restart configuration."""
        mpv_config = MpvConfig()

        assert mpv_config.restart_on_crash is True
        assert mpv_config.max_restart_attempts == 3
        assert mpv_config.restart_delay == 2.0


class TestIntegration:
    """Integration tests for Phase 1."""

    def test_full_config_validation(self):
        """Test complete configuration validation."""
        config = Config()

        # Should validate without errors
        config.validate()

        # Verify all components are initialized
        assert isinstance(config.proxy, ProxyConfig)
        assert isinstance(config.mpv, MpvConfig)
        assert isinstance(config.logging, LoggingConfig)

    @patch('jellyproxy.proxy.MpvProcess.start')
    @patch('jellyproxy.proxy.ProxyServer._setup_signal_handlers')
    def test_proxy_server_initialization(self, mock_signals, mock_mpv_start):
        """Test proxy server initialization."""
        from jellyproxy.proxy import ProxyServer

        config = Config()
        server = ProxyServer(config)

        # Should initialize without errors
        assert server.config == config
        assert server.mpv_process is not None
        assert server.running is False


if __name__ == "__main__":
    pytest.main([__file__])
