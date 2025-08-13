# Traktor Playlist Manager

This project provides a set of Python scripts to interact with Native Instruments Traktor Pro's `collection.nml` file and Jellyfin servers. The main functionalities include exporting Traktor playlists to `.m3u` files, importing `.m3u` playlists into Traktor, and fetching playlists from a Jellyfin server.

## Project Structure

- `main.py`: The main script that provides a unified command-line interface for all functionalities.
- `traktor2playlist.py`: Module for exporting Traktor playlists to `.m3u` files.
- `playlist2traktor.py`: Module for importing `.m3u` playlists into Traktor's `collection.nml`.
- `jellyfin2playlist.py`: Module for fetching favorite tracks from a Jellyfin server and creating an `.m3u` playlist.
- `traktor_utils.py`: Shared utility functions for Traktor operations.
- `logger_utils.py`: Utility functions for logging configuration.
- `file_statistics.py`: A helper module for generating statistics about file types in playlists.
- `example/`: Contains example files for `collection.nml` and `playlist.m3u`.
- `config.example.ini`: An example configuration file.

## Scripts

### main.py

The main entry point for all operations. It provides subcommands for export, import, and jellyfin operations.

**Usage:**
```bash
# Export Traktor playlists
python main.py export [OPTIONS]

# Import M3U playlist to Traktor
python main.py import [OPTIONS]

# Fetch favorites from Jellyfin
python main.py jellyfin [OPTIONS]
```

### traktor2playlist.py

Exports playlists from Traktor's `collection.nml` XML file to individual `.m3u` playlist files.

**Features:**
- Automatically detects the latest Traktor installation and its `collection.nml` file.
- Exports all user-defined playlists (skipping special playlists like `_LOOPS` and `_RECORDINGS`).
- Supports making file paths relative for portability.
- Supports custom path prefixes.
- Option to include folder names in exported playlist names.
- Debug mode for troubleshooting.
- Statistics mode to see file type distribution.

**Usage (via main.py):**
```bash
# Basic usage, finds collection.nml automatically and exports to ~/Music
python main.py export

# Specify collection.nml path and output directory
python main.py export -c /path/to/collection.nml -o /path/to/output/dir

# Make paths relative and add a prefix
python main.py export -r "C:\\MyMusic\\" -p "..\\"

# Enable debug and statistics modes
python main.py export -d --stats

# Use a custom separator (e.g., for cross-platform compatibility)
python main.py export -s "/"

# Include folder names in playlist names
python main.py export --fullname
```

**Arguments:**
- `-c`, `--collection`: Path to `collection.nml`. If not provided, the script attempts to find it automatically.
- `-o`, `--output_dir`: Directory to write playlist files. Default is `~/Music`.
- `-r`, `--root_path`: Path to strip from each entry.
- `-p`, `--path_prefix`: Path to add at the beginning of each entry.
- `-d`, `--debug`: Enable debug mode.
- `--stats`: Enable statistics mode.
- `-s`, `--separator`: Custom separator to use instead of the default OS separator.
- `--fullname`: Use full playlist name (including folder).

### playlist2traktor.py

Imports tracks from an `.m3u` playlist file into Traktor's `collection.nml`, creating a new playlist.

**Features:**
- Reads an `.m3u` file.
- Adds the tracks to a specified `collection.nml` file as a new playlist.
- Automatically generates a unique playlist name.

**Usage (via main.py):**
```bash
# Import playlist with a specific name
python main.py import -m /path/to/playlist.m3u -n "My New Playlist"

# Auto-detect collection.nml
python main.py import -m /path/to/playlist.m3u
```

**Arguments:**
- `-m`, `--m3u_playlist`: Path to the .m3u file to import (required)
- `-c`, `--collection`: Path to `collection.nml`. If not provided, the script attempts to find it automatically.
- `-n`, `--playlist_name`: Base name for the new playlist in Traktor (default: ImportedPlaylist)

### jellyfin2playlist.py

Fetches favorite tracks from a Jellyfin server and creates an `.m3u` playlist file.

**Features:**
- Connects to a Jellyfin server using an API key.
- Retrieves a list of favorite audio items.
- Adjusts file paths to match the local file system.
- Creates an `.m3u` playlist file with the favorite tracks.

**Usage (via main.py):**
```bash
# Use settings from config.ini
python main.py jellyfin

# Override specific settings
python main.py jellyfin --remove_path_prefix "/mnt/media/" --add_path_prefix "~/Media/"
```

**Arguments:**
- `--remove_path_prefix`: Prefix to remove from Jellyfin file paths
- `--add_path_prefix`: Prefix to add to local file paths
- `--playlist_name`: Path to save the .m3u playlist file

## Configuration

A `config.ini` file can be used to store persistent settings for all operations:

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

## Logging

The application uses Python's built-in logging module with per-module loggers. Each module has its own logger with hierarchical naming (e.g., `traktor2playlist`, `playlist2traktor`, `jellyfin2playlist`).

### Log Levels

The application supports the following log levels:
- **DEBUG**: Detailed information, typically of interest only when diagnosing problems
- **INFO**: Confirmation that things are working as expected
- **WARNING**: An indication that something unexpected happened
- **ERROR**: Due to a more serious problem, the software has not been able to perform some function
- **CRITICAL**: A serious error, indicating that the program itself may be unable to continue running

### Configuration

Logging can be configured in two ways:
1. **Config file**: Set the default log level in `config.ini`
2. **Command line**: Use the `-d` or `--debug` flag to enable debug logging regardless of config file settings

### Examples

For detailed debugging information:
```bash
python main.py export -d
```

For normal operation with only important messages:
```bash
python main.py export
```

To set the log level in `config.ini`:
```ini
[logging]
level = DEBUG
```

## File Statistics

The `file_statistics.py` module is used by `traktor2playlist.py` when the `--stats` flag is enabled. It analyzes the file extensions of tracks in the exported playlists and prints a simple bar chart showing the distribution of file types.

## Example Files

The `example/` directory contains sample files:
- `collection.nml`: A minimal example of a Traktor collection file with playlists.
- `playlist.m3u`: A sample `.m3u` playlist file for use with `playlist2traktor.py`.