# Traktor Playlist Manager

A set of Python scripts to interact with Native Instruments Traktor Pro's `collection.nml` file and Jellyfin server. The main functionalities include exporting Traktor playlists to `.m3u` files, importing `.m3u` playlists into Traktor, and fetching playlists from a Jellyfin server.

## Features

- Export Traktor playlists to `.m3u` files with path manipulation options
- Import `.m3u` playlists into Traktor
- Fetch favorite tracks from a Jellyfin server and create an `.m3u` playlist
- Unified command-line interface for all operations
- Configuration file support for persistent settings
- Auto-detection of Traktor's `collection.nml` file
- Configurable logging with multiple log levels

## Installation

1. Clone or download this repository
2. Ensure you have Python 3.6 or higher installed
3. Install required dependencies:
   ```bash
   pip install requests
   ```

## Configuration

Create a `config.ini` file in the project directory (you can use `config.example.ini` as a template):

```ini
[logging]
# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
level = INFO

[jellyfin]
server_url = http://your-jellyfin-server-url
api_key = your-api-key
user_id = your-user-id
remove_path_prefix = /mnt/music/
add_path_prefix = ~/Music/
playlist_name = ~/Music/playlists/Favorites.m3u

[traktor]
collection_path = /path/to/your/collection.nml
output_dir = ~/Music
```

All configuration options can be overridden with command-line arguments.

## Usage

The script is invoked through `main.py` with different subcommands for each action:

```bash
python main.py [OPTIONS] ACTION [ACTION_OPTIONS]
```

### Export Traktor Playlists

Export all playlists from Traktor's `collection.nml` to individual `.m3u` files:

```bash
# Auto-detect collection.nml and export to ~/Music
python main.py export

# Specify collection.nml path and output directory
python main.py export -c /path/to/collection.nml -o /path/to/output/dir

# Make paths relative and add a prefix
python main.py export -r "C:\\MyMusic\\" -p "..\\"

# Enable debug and statistics modes
python main.py export -d --stats

# Use a custom separator (e.g., for cross-platform compatibility)
python main.py export -s "/"

# Include folder names in exported playlist names
python main.py export --fullname
```

### Import M3U Playlist to Traktor

Import tracks from an `.m3u` playlist file into Traktor's `collection.nml`:

```bash
# Import playlist with a specific name
python main.py import -m /path/to/playlist.m3u -n "My New Playlist"

# Auto-detect collection.nml
python main.py import -m /path/to/playlist.m3u
```

### Fetch Favorites from Jellyfin

Connect to a Jellyfin server and create an `.m3u` playlist from favorite tracks:

```bash
# Use settings from config.ini
python main.py jellyfin

# Override specific settings
python main.py jellyfin --remove_path_prefix "/mnt/media/" --add_path_prefix "~/Media/"
```

## Available Options

### Global Options
- `--config`: Path to configuration file (default: config.ini)
- `-d`, `--debug`: Enable debug mode (overrides config file setting)

### Export Options
- `-c`, `--collection`: Path to `collection.nml`. If not provided, the script attempts to find it automatically.
- `-o`, `--output_dir`: Directory to write playlist files. Default is `~/Music`.
- `-r`, `--root_path`: Path to strip from each entry.
- `-p`, `--path_prefix`: Path to add at the beginning of each entry.
- `--stats`: Enable statistics mode.
- `-s`, `--separator`: Custom separator to use instead of the default OS separator.
- `--fullname`: Use full playlist name (including folder).

### Import Options
- `-m`, `--m3u_playlist`: Path to the .m3u file to import (required)
- `-c`, `--collection`: Path to `collection.nml`. If not provided, the script attempts to find it automatically.
- `-n`, `--playlist_name`: Base name for the new playlist in Traktor (default: ImportedPlaylist)

### Jellyfin Options
- `--remove_path_prefix`: Prefix to remove from Jellyfin file paths
- `--add_path_prefix`: Prefix to add to local file paths
- `--playlist_name`: Path to save the .m3u playlist file

## Logging

The application supports configurable logging with the following features:

1. **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
2. **Configuration**: Set log level in `config.ini`
3. **Override**: Use `-d` or `--debug` flag to enable debug logging regardless of config
4. **Per-Module**: Each module has its own logger with hierarchical naming

Example `config.ini` logging section:
```ini
[logging]
level = DEBUG
```

This will show detailed debug information from all modules. For production use, you might want to set the level to `INFO` or `WARNING`.