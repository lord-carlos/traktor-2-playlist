import os
import xml.etree.ElementTree as ET
import file_statistics
import sys
import logging
from dataclasses import dataclass
from typing import Optional
from traktor_utils import parse_collection_nml, find_latest_traktor_version

# Get logger for this module
logger = logging.getLogger(__name__)

@dataclass
class ExportConfig:
    collection_path: str
    output_dir: str
    root_path: str = ""
    path_prefix: str = ""
    debug: bool = False
    stats: bool = False
    separator: Optional[str] = None
    fullname: bool = False


class Playlist:
    def __init__(self, name, entries, folder_name=""):
        self.name = name
        self.entries = entries


def parse_collection_nml(file_path, config: ExportConfig):
    """
    Parses the collection.nml file and extracts playlists and their entries.

    Args:
        file_path (str): The path to the collection.nml file.
        config (ExportConfig): Configuration parameters.

    Returns:
        list: A list of Playlist objects, each containing the name and entries of a playlist.
            None if there was an error parsing the XML.
    """
    playlists = []

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Iterate over folder nodes first
        for folder_node in root.findall(".//NODE[@TYPE='FOLDER']"):
            folder_name = folder_node.get("NAME")

            logger.debug(f"Processing folder: {folder_name}")

            # Check if folder name starts with '$ROOT_' and skip it
            # if folder_name.startswith("$ROOT"):
            #     continue

            # Now find playlist nodes within each folder
            for node in folder_node.findall(".//NODE[@TYPE='PLAYLIST']"):
                playlist_name = node.get("NAME")
                logger.debug(f"Found playlist: {playlist_name} in folder: {folder_name}")
                full_playlist_name = f"{folder_name} {playlist_name}"  # Prepend folder name
                entries = []

                for entry_node in node.findall(".//ENTRY/PRIMARYKEY"):
                    track_key = entry_node.get("KEY")
                    entries.append(track_key)

                if entries:
                    if config.fullname:
                        playlists.append(Playlist(full_playlist_name, entries))
                    else:
                        playlists.append(Playlist(playlist_name, entries))

    except ET.ParseError as e:
        logger.error(f"Error parsing XML: {e}")
        return None

    return playlists


def write_playlist_files(playlists, output_dir, root_path, path_prefix, custom_separator=None):
    for playlist in playlists:
        if playlist.entries:
            # if playlist.name is '_LOOPS' or '_RECORDINGS' skip it
            if playlist.name == '_LOOPS' or playlist.name == '_RECORDINGS':
                continue

            playlist_file_path = os.path.join(output_dir, f"{playlist.name}.m3u")
            with open(playlist_file_path, "w", encoding='utf-8') as playlist_file:
                # Write playlist entries to the M3U file
                playlist_file.write("#EXTM3U\n")

                # Replace ':' with the custom separator or default OS separator
                separator = custom_separator if custom_separator is not None else os.sep
                entries = [entry.replace('/:', separator) for entry in playlist.entries]
                
                # Modify the entries to start with '/Users/' and not 'DiskName' under MacOS
                if sys.platform == "darwin":
                    entries = [f'/Users/{entry.split("/Users/", 1)[-1]}' if '/Users/' in entry else entry for entry in entries]

                # Remove the root path of every entry if root_path is provided
                if root_path:
                    entries = [entry.replace(root_path, '') for entry in entries]

                playlist_file.write("\n".join([f"{path_prefix}{entry}" for entry in entries]))

            print(f"Playlist file '{playlist.name}.m3u' written to {output_dir}")
        # Note: file_statistics.from_playlist will handle its own logging if needed


def export_playlists(config: ExportConfig):
    """
    Orchestrates the process of parsing the collection.nml file and writing playlist files.

    Args:
        config (ExportConfig): Configuration parameters.
    """
    # Configure logging based on debug flag
    if config.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
    
    # Validate collection.nml path
    if not config.collection_path:
        logger.error("No collection.nml path provided.")
        return
        
    if not os.path.exists(config.collection_path):
        logger.error(f"collection.nml not found at {config.collection_path}")
        return
    
    playlists = parse_collection_nml(config.collection_path, config)

    if playlists:
        logger.debug("Playlists with at least 1 entry:")
        for playlist in playlists:
            logger.debug(f"{playlist.name}: {len(playlist.entries)} entries")

        if not os.path.exists(config.output_dir):
            os.makedirs(config.output_dir)

        write_playlist_files(playlists, config.output_dir, config.root_path, config.path_prefix, config.separator)

        # Overall statistic
        if config.stats:
            file_statistics.from_playlist(playlists)