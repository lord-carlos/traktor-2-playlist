# Traktor 2 Playlist

This project provides a set of Python scripts to interact with Native Instruments Traktor Pro's `collection.nml` file. The main functionalities include exporting Traktor playlists to `.m3u` files, importing `.m3u` playlists into Traktor, and fetching playlists from a Jellyfin server.

## Project Structure

- `traktor2playlist.py`: The main script to export playlists from Traktor's `collection.nml` to `.m3u` files.
- `playlist2traktor.py`: A script to import `.m3u` playlists into Traktor's `collection.nml`.
- `jellyfin2playlist.py`: A script to fetch favorite tracks from a Jellyfin server and create an `.m3u` playlist.
- `file_statistics.py`: A helper module for `traktor2playlist.py` to generate statistics about the file types in the playlists.
- `example/`: Contains example files for `collection.nml` and `playlist.m3u`.
- `config.example.ini`: An example configuration file for `jellyfin2playlist.py`.

## Scripts

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

**Usage:**
```bash
# Basic usage, finds collection.nml automatically and exports to ~/Music
python traktor2playlist.py

# Specify collection.nml path and output directory
python traktor2playlist.py -c /path/to/collection.nml -o /path/to/output/dir

# Make paths relative and add a prefix
python traktor2playlist.py -r "C:\\MyMusic\\" -p "..\\"

# Enable debug and statistics modes
python traktor2playlist.py -d --stats

# Use a custom separator (e.g., for cross-platform compatibility)
python traktor2playlist.py -s "/"

# Include folder names in playlist names
python traktor2playlist.py --fullname
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

**Usage:**
Modify the configuration variables at the top of the script:
- `M3U_PLAYLIST_PATH`: Path to the `.m3u` file to import.
- `COLLECTION_NML_PATH`: Path to the `collection.nml` file to modify.
- `NEW_PLAYLIST_NAME`: Base name for the new playlist (a random suffix will be added).

Then run:
```bash
python playlist2traktor.py
```

### jellyfin2playlist.py

Fetches favorite tracks from a Jellyfin server and creates an `.m3u` playlist file.

**Features:**
- Connects to a Jellyfin server using an API key.
- Retrieves a list of favorite audio items.
- Adjusts file paths to match the local file system.
- Creates an `.m3u` playlist file with the favorite tracks.

**Usage:**
1. Copy `config.example.ini` to `config.ini`.
2. Edit `config.ini` to include your Jellyfin server URL, API key, and user ID.
3. Adjust the path manipulation variables `REMOVE_PATH_PREFIX` and `ADD_PATH_PREFIX` in the script if needed.
4. Run the script:
```bash
python jellyfin2playlist.py
```

## File Statistics

The `file_statistics.py` module is used by `traktor2playlist.py` when the `--stats` flag is enabled. It analyzes the file extensions of tracks in the exported playlists and prints a simple bar chart showing the distribution of file types.

## Example Files

The `example/` directory contains sample files:
- `collection.nml`: A minimal example of a Traktor collection file with playlists.
- `playlist.m3u`: A sample `.m3u` playlist file for use with `playlist2traktor.py`.