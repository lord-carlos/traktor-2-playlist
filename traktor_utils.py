import os
import re
import xml.etree.ElementTree as ET
import sys
import logging
from dataclasses import dataclass
from typing import Optional

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


def find_latest_traktor_version():
    """
    Finds the latest version of Traktor installed on the system.

    Returns:
        str: The path to the latest version of Traktor.
            None if Traktor folder is not found.
    """
    documents_path = os.path.join(os.path.expanduser("~"), "Documents", "Native Instruments")
    try:
        traktor_versions = [folder for folder in os.listdir(documents_path) if folder.startswith("Traktor")]
    except FileNotFoundError:
        # Documents/Native Instruments directory not found
        logger.debug("Documents/Native Instruments directory not found")
        return None

    version_pattern = re.compile(r"Traktor (\d+\.\d+\.\d+)")

    valid_versions = [version_pattern.match(version).group(1) for version in traktor_versions if version_pattern.match(version)]

    if not valid_versions:
        logger.debug("No valid Traktor versions found")
        return None

    latest_version = max(valid_versions, key=lambda v: tuple(map(int, v.split('.'))))
    traktor_path = os.path.join(documents_path, f"Traktor {latest_version}")
    logger.debug(f"Found latest Traktor version at: {traktor_path}")
    return traktor_path


def convert_path_to_traktor_format(original_path):
    """
    Converts a file path to the Traktor format with forward slashes and a colon after each slash.

    :param original_path: The original file path as a string.
    :return: The converted file path as a string.
    """
    # Replace backslashes with forward slashes
    path_with_slashes = original_path.replace("\\\\", "/")
    # Add a colon after each slash
    traktor_path = path_with_slashes.replace("/", "/:")
    # Ensure the colon is only added after the first slash
    return traktor_path


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
    from traktor2playlist import Playlist  # Import here to avoid circular imports

    logger.info(f"Parsing collection.nml file: {file_path}")
    playlists = []

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Iterate over folder nodes first
        for folder_node in root.findall(".//NODE[@TYPE='FOLDER']"):
            folder_name = folder_node.get("NAME")

            # Check if folder name starts with '$ROOT_' and skip it
            if folder_name and folder_name.startswith("$ROOT"):
                logger.debug(f"Skipping root folder: {folder_name}")
                continue

            # Now find playlist nodes within each folder
            for node in folder_node.findall(".//NODE[@TYPE='PLAYLIST']"):
                playlist_name = node.get("NAME")
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

        logger.info(f"Successfully parsed {len(playlists)} playlists from collection.nml")
        
    except ET.ParseError as e:
        logger.error(f"Error parsing XML: {e}")
        return None
    except FileNotFoundError:
        logger.error(f"Error: collection.nml not found at {file_path}")
        return None

    return playlists