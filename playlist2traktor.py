import os
import xml.etree.ElementTree as ET
import uuid
import random
import string

# Configuration
M3U_PLAYLIST_PATH = "example/playlist.m3u"
COLLECTION_NML_PATH = "example/collection.nml"
NEW_PLAYLIST_NAME = "#My New Playlist"

# Generate 5 random letters
random_letters = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=5))
NEW_PLAYLIST_NAME += "-" + random_letters

def convert_path_to_traktor_format(original_path):
    """
    Converts a file path to the Traktor format with forward slashes and a colon after each slash.

    :param original_path: The original file path as a string.
    :return: The converted file path as a string.
    """
    # Replace backslashes with forward slashes
    path_with_slashes = original_path.replace("\\", "/")
    # Add a colon after each slash
    traktor_path = path_with_slashes.replace("/", "/:")
    # Ensure the colon is only added after the first slash
    return traktor_path



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
        return tracks
    except Exception as e:
        print(f"Error reading .m3u playlist: {e}")
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
            print("No <SUBNODES> element found.")
            return
        
        # Create the new <NODE TYPE="PLAYLIST">
        node_element = ET.Element("NODE", {
            "TYPE": "PLAYLIST",
            "NAME": playlist_name
        })

        # Create the <PLAYLIST> child
        playlist_element = ET.SubElement(node_element, "PLAYLIST", {
            "ENTRIES": str(tracks.__len__()),
            "TYPE": "LIST",
            "UUID": str(uuid.uuid4()).replace("-", "")
        })
        
        # Add each track as an <ENTRY>
        for track_path in tracks:
            entry_element = ET.SubElement(playlist_element, "ENTRY")
            ET.SubElement(entry_element, "PRIMARYKEY", {
                "TYPE": "FILE",
                "KEY": convert_path_to_traktor_format(track_path)
            })
        
        # Append the new node to <SUBNODES>
        subnodes.append(node_element)

        # Save the modified XML back to the file
        tree.write(collection_path, encoding="utf-8", xml_declaration=True)
        print(f"Playlist '{playlist_name}' added successfully.")
    except Exception as e:
        print(f"Error modifying collection.nml: {e}")

def main():
    # Step 1: Read the .m3u playlist
    tracks = read_m3u_playlist(M3U_PLAYLIST_PATH)
    if not tracks:
        print("No tracks found in the .m3u playlist.")
        return

    # Step 2: Modify the collection.nml file
    modify_collection_nml(COLLECTION_NML_PATH, NEW_PLAYLIST_NAME, tracks)

if __name__ == "__main__":
    main()