# JellyProxy

A proxy that sits between jellyfin-mpv-shim and mpv to filter and control IPC commands.

## What it does

Jellyfin-mpv-shim sometimes overrides your carefully configured mpv settings. JellyProxy prevents this by intercepting commands between JMS and mpv, letting you block unwanted changes while keeping the features you want.

## Installation

```bash
pip install jellyproxy-py
```

## Quick Start

1. **Generate a config file:**
   ```bash
   jellyproxy --generate-config > ~/.config/jellyproxy/conf.json
   ```

2. **Edit the config** to block commands you don't want. The example config blocks `set_property` commands that override your settings.

3. **Update your JMS config** to point to the proxy socket:
   ```json
   {
     "mpv_ext": true,
     "mpv_ext_ipc": "/tmp/mpvSockets/spoof",
     "mpv_ext_start": false,
     "mpv_ext_path": null,
   }
   ```
   
   **Note**, `mpv_ext_ipc` should match your `spoof_socket`
   path in `~/.config/jellyproxy/conf.json`, if you've
   changed it.

4. **Run it:**
   ```bash
   jellyproxy
   ```

That's it. JellyProxy will start mpv and JMS automatically, and your mpv settings won't get clobbered anymore.

## Configuration

The config file uses JSON with two main filtering lists:

- **`blacklist`** - Commands to block
- **`whitelist`** - Commands to explicitly allow (overrides blacklist)

Each rule matches commands using regex patterns:

```json
{
  "blacklist": [
    {
      "#": "Block JMS from changing OSC setting",
      "command": ["set_property", "osc", ".*"]
    }
  ],
  "whitelist": [
    {
      "#": "But allow subtitle color changes",
      "command": ["set_property", "sub-color", ".*"]
    }
  ]
}
```

### Command Line Options

```bash
jellyproxy --help                    # Show all options
jellyproxy --config myconfig.json    # Use custom config
jellyproxy --debug                   # Enable debug logging
jellyproxy --validate               # Check config for errors
```

## Config Reloading

JellyProxy watches your config file and restarts automatically when you make changes. No need to manually restart.

## Logging

All IPC traffic gets logged so you can see what commands JMS is sending. Use `--debug` for extra detail, or edit the logging section in your config.

## Socket Paths

By default:
- JMS connects to `/tmp/mpvSockets/spoof` (the proxy)
- Proxy connects to `/tmp/mpvSockets/real` (actual mpv)

Change these in the config if needed.

## Troubleshooting

**JMS can't connect:** Check that the socket paths match between your JMS config and JellyProxy config.

**Commands not being filtered:** Run with `--debug` to see the exact commands being sent and whether they match your rules.

**Config errors:** Use `jellyproxy --validate` to check for problems.

**Multiple JMS instances:** The old config reloading had a bug that left processes running. This is fixed now.

## Requirements

- Python 3.8+
- `python-mpv-jsonipc` (pip install python-mpv-jsonipc)
- A working jellyfin-mpv-shim setup

## License

GPL-3.0
