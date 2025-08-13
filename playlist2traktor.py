import os
import xml.etree.ElementTree as ET
import uuid
import random
import string
import logging
from traktor_utils import convert_path_to_traktor_format

# Get logger for this module
logger = logging.getLogger(__name__)


def read_m3u_playlist(file_path):
    """
    Reads an .m3u playlist file and returns a list of track paths.
    """
    tracks = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Ignore comments and empty lines
                    tracks.append(line)
        logger.info(f"Successfully read {len(tracks)} tracks from {file_path}")
        return tracks
    except Exception as e:
        logger.error(f"Error reading .m3u playlist: {e}")
        return []


def modify_collection_nml(collection_path, playlist_name, tracks):
    """
    Modifies the Traktor Pro collection.nml file to add a new playlist.
    """
    try:
        # Parse the collection.nml XML
        tree = ET.parse(collection_path)
        root = tree.getroot()

        # Locate the <SUBNODES> element
        subnodes = root.find(".//SUBNODES")
        if subnodes is None:
            logger.error("No <SUBNODES> element found.")
            return
        
        # Create the new <NODE TYPE="PLAYLIST">
        node_element = ET.Element("NODE", {
            "TYPE": "PLAYLIST",
            "NAME": playlist_name
        })

        # Create the <PLAYLIST> child
        playlist_element = ET.SubElement(node_element, "PLAYLIST", {
            "ENTRIES": str(len(tracks)),
            "TYPE": "LIST",
            "UUID": str(uuid.uuid4()).replace("-", "")
        })
        
        # Add each track as an <ENTRY>
        for track_path in tracks:
            entry_element = ET.SubElement(playlist_element, "ENTRY")
            ET.SubElement(entry_element, "PRIMARYKEY", {
                "TYPE": "TRACK",
                "KEY": convert_path_to_traktor_format(track_path)
            })
        
        # Append the new node to <SUBNODES>
        subnodes.append(node_element)

        # Save the modified XML back to the file
        tree.write(collection_path, encoding="utf-8", xml_declaration=True)
        logger.info(f"Playlist '{playlist_name}' added successfully with {len(tracks)} tracks.")
    except Exception as e:
        logger.error(f"Error modifying collection.nml: {e}")


def import_playlist(m3u_playlist_path, collection_nml_path, new_playlist_name_base):
    """
    Main function to import an .m3u playlist into Traktor's collection.nml.
    
    Args:
        m3u_playlist_path (str): Path to the .m3u file to import.
        collection_nml_path (str): Path to the collection.nml file to modify.
        new_playlist_name_base (str): Base name for the new playlist.
    """
    logger.info(f"Starting import of playlist from {m3u_playlist_path}")
    
    # Generate 5 random letters for a unique playlist name
    random_letters = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=5))
    new_playlist_name = f"{new_playlist_name_base}-{random_letters}"
    logger.debug(f"Generated playlist name: {new_playlist_name}")

    # Step 1: Read the .m3u playlist
    tracks = read_m3u_playlist(m3u_playlist_path)
    if not tracks:
        logger.warning("No tracks found in the .m3u playlist.")
        return

    # Step 2: Modify the collection.nml file
    logger.info(f"Adding {len(tracks)} tracks to playlist '{new_playlist_name}' in {collection_nml_path}")
    modify_collection_nml(collection_nml_path, new_playlist_name, tracks)
    
    logger.info("Playlist import completed successfully.")