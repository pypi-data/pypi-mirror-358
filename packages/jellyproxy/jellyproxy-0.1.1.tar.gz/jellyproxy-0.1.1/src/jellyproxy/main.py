"""
Main entry point for JellyProxy.

Handles command line argument parsing, configuration loading, and proxy startup.
"""

import argparse
import asyncio
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from .config import ProxyConfig
from .proxy import JellyProxy


async def watch_config_file(config_path: str):
    """Watch config file for changes."""
    path = Path(config_path)
    last_mtime = path.stat().st_mtime if path.exists() else 0

    while True:
        await asyncio.sleep(1)
        if path.exists():
            current_mtime = path.stat().st_mtime
            if current_mtime > last_mtime:
                return  # Config changed
            last_mtime = current_mtime


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="jellyproxy",
        description="Jellyfin MPV IPC Proxy & Filter - Intercept and filter IPC communication between jellyfin-mpv-shim and mpv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  jellyproxy                           # Run with default settings
  jellyproxy --debug                   # Run with debug logging
  jellyproxy --config proxy.json       # Run with custom config file
  jellyproxy --socket-dir /tmp/sockets # Use custom socket directory
  jellyproxy --validate               # Validate configuration and exit
  jellyproxy --generate-config > config.json # Generate example config
        """
    )

    # Configuration options
    parser.add_argument(
        "-c", "--config",
        type=str,
        help="Path to configuration file (JSON format)"
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate configuration and exit"
    )

    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Generate example configuration and exit"
    )

    # Socket configuration
    parser.add_argument(
        "--socket-dir",
        type=str,
        help="Directory for socket files (default: /tmp/mpvSockets)"
    )

    parser.add_argument(
        "--spoof-socket",
        type=str,
        help="Path to spoof socket (where JMS connects)"
    )

    parser.add_argument(
        "--real-socket",
        type=str,
        help="Path to real socket (where MPV listens)"
    )

    # Logging options
    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging"
    )

    log_group.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Disable console logging"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    parser.add_argument(
        "--log-file",
        type=str,
        help="Write logs to file"
    )

    # JMS options
    parser.add_argument(
        "--no-auto-start-jms",
        action="store_true",
        help="Don't automatically start jellyfin-mpv-shim"
    )

    parser.add_argument(
        "--jms-args",
        type=str,
        nargs="+",
        help="Custom arguments for jellyfin-mpv-shim"
    )

    # Development options
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    return parser


def load_configuration(args: argparse.Namespace) -> ProxyConfig:
    """Load and validate configuration from file and command line arguments."""
    # Load base configuration
    config = ProxyConfig(config_file=args.config)

    # Override with command line arguments
    args_dict = {
        'socket_dir': args.socket_dir,
        'spoof_socket': args.spoof_socket,
        'real_socket': args.real_socket,
        'debug': args.debug,
        'verbose': args.verbose,
        'quiet': args.quiet,
        'log_file': args.log_file,
        'no_auto_start_jms': args.no_auto_start_jms,
        'jms_args': args.jms_args,
    }

    # Filter out None values
    args_dict = {k: v for k, v in args_dict.items() if v is not None}

    config.update_from_args(args_dict)

    return config


def validate_configuration(config: ProxyConfig) -> bool:
    """Validate configuration and print any errors."""
    errors = config.validate()

    if errors:
        print("Configuration validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return False

    print("Configuration validation passed.")
    return True


def setup_signal_handlers(proxy: JellyProxy):
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(signum: int, frame):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] SHUTDOWN: Received signal {signum}")

        # Trigger graceful shutdown
        if hasattr(proxy, '_shutdown_event'):
            proxy._shutdown_event.set()
        else:
            sys.exit(0)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def run_proxy_with_config_watching(args: argparse.Namespace) -> int:
    """Run the proxy with automatic config reloading on configuration changes."""

    while True:
        # Load configuration (this respects both config file and CLI args)
        config = load_configuration(args)

        # Determine which config file to watch
        config_file = None
        if args.config:
            config_file = args.config
        else:
            # Check if default config exists
            default_config = config._get_default_config_path()
            if default_config and default_config.exists():
                config_file = str(default_config)

        # Create the proxy
        current_proxy = JellyProxy(config)

        # Set up signal handlers for this proxy instance
        setup_signal_handlers(current_proxy)

        try:
            # Start proxy in a task
            proxy_task = asyncio.create_task(current_proxy.run())

            # Watch config file if one exists
            if config_file and Path(config_file).exists():
                watcher_task = asyncio.create_task(watch_config_file(config_file))

                print(f"Watching configuration file: {config_file}")

                # Wait for either proxy to finish or config to change
                done, pending = await asyncio.wait(
                    [proxy_task, watcher_task],
                    return_when=asyncio.FIRST_COMPLETED
                )

                # Cancel any pending tasks
                for task in pending:
                    task.cancel()

                # If watcher completed first, config changed - cleanup and restart
                if watcher_task in done:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{timestamp}] CONFIG: Configuration file changed, restarting proxy...")

                    # Signal the proxy to shutdown gracefully
                    current_proxy._shutdown_event.set()

                    # Wait for the proxy task to complete its cleanup
                    try:
                        await proxy_task
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        print(f"Error during proxy shutdown: {e}", file=sys.stderr)

                    # Wait for pending watcher task to be cancelled
                    try:
                        await watcher_task
                    except asyncio.CancelledError:
                        pass

                    # Give processes time to fully terminate
                    await asyncio.sleep(2)

                    print(f"[{timestamp}] CONFIG: Proxy stopped, restarting with new configuration...")

                    # Continue to restart with new config
                    continue
                else:
                    # Proxy finished normally or with error
                    try:
                        await watcher_task
                    except asyncio.CancelledError:
                        pass

                    # Get the result from the proxy task
                    try:
                        result = await proxy_task
                        return result if result is not None else 0
                    except Exception as e:
                        print(f"Proxy error: {e}", file=sys.stderr)
                        return 1

            else:
                # No config file to watch, just run normally
                try:
                    result = await proxy_task
                    return result if result is not None else 0
                except Exception as e:
                    print(f"Proxy error: {e}", file=sys.stderr)
                    return 1

        except Exception as e:
            print(f"Error in proxy execution: {e}", file=sys.stderr)
            # Ensure cleanup happens even on error
            current_proxy._shutdown_event.set()
            current_proxy.cleanup()
            return 1

        finally:
            # Always ensure cleanup happens, but check if we need to set shutdown event
            if not current_proxy._shutdown_event.is_set():
                current_proxy._shutdown_event.set()
            # Always call cleanup - it should be idempotent
            current_proxy.cleanup()


async def run_proxy(config: ProxyConfig) -> int:
    """Run the proxy with the given configuration."""
    proxy = None
    try:
        # Create and configure proxy
        proxy = JellyProxy(config)

        # Set up signal handlers
        setup_signal_handlers(proxy)

        # Run the proxy
        await proxy.run()

        return 0

    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SHUTDOWN: Interrupted by user")
        return 0

    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1

    finally:
        if proxy:
            proxy.cleanup()


def main() -> int:
    """Main entry point for the jellyproxy command."""
    # Parse command line arguments
    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        # Handle special commands first
        if args.generate_config:
            # Generate example configuration
            config = ProxyConfig()
            example = config.generate_example_config()
            import json
            print(json.dumps(example, indent=2))
            return 0

        # Load configuration
        config = load_configuration(args)

        # Validate configuration if requested
        if args.validate:
            return 0 if validate_configuration(config) else 1

        # Validate configuration anyway
        if not validate_configuration(config):
            return 1

        # Check dependencies
        try:
            from python_mpv_jsonipc import MPV, MPVError
        except ImportError:
            print("ERROR: python_mpv_jsonipc not found. Please install it:", file=sys.stderr)
            print("pip install python-mpv-jsonipc", file=sys.stderr)
            return 1

        # Run the proxy with config watching
        return asyncio.run(run_proxy_with_config_watching(args))

    except Exception as e:
        print(f"Startup error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
