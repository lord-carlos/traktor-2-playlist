import os
import xml.etree.ElementTree as ET
import re
import file_statistics
import argparse
import sys

DEBUG = False
STATISTIC = False

class Playlist:
    def __init__(self, name, entries, folder_name=""):
        self.name = name
        self.entries = entries


def find_latest_traktor_version():
    """
    Finds the latest version of Traktor installed on the system.

    Returns:
        str: The path to the latest version of Traktor.
            None if Traktor folder is not found.
    """
    documents_path = os.path.join(os.path.expanduser("~"), "Documents", "Native Instruments")
    traktor_versions = [folder for folder in os.listdir(documents_path) if folder.startswith("Traktor")]

    version_pattern = re.compile(r"Traktor (\d+\.\d+\.\d+)")

    valid_versions = [version_pattern.match(version).group(1) for version in traktor_versions if version_pattern.match(version)]

    if not valid_versions:
        return None

    latest_version = max(valid_versions, key=lambda v: tuple(map(int, v.split('.'))))
    return os.path.join(documents_path, f"Traktor {latest_version}")

def parse_collection_nml(file_path, args):
    """
    Parses the collection.nml file and extracts playlists and their entries.

    Args:
        file_path (str): The path to the collection.nml file.

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

            # Check if folder name starts with '$ROOT_' and skip it
            if folder_name.startswith("$ROOT"):
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
                    if args.fullname:
                        playlists.append(Playlist(full_playlist_name, entries))
                    else:
                        playlists.append(Playlist(playlist_name, entries))

    except ET.ParseError as e:
        if DEBUG:
            print(f"Error parsing XML: {e}")
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
        if STATISTIC:
            file_statistics.from_playlist([playlist])   

def main():
    """
    The main function that orchestrates the process of finding the latest Traktor version,
    parsing the collection.nml file, and writing playlist files.

    Prints the playlists with at least 1 entry and prompts the user for the output directory.

    Writes playlist files in the specified output directory.
    """

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-c', '--collection', type=str, help='Path to collection.nml If none is given we will try to find it automatically.')
    parser.add_argument('-o', '--output_dir', type=str, default=os.path.join(os.path.expanduser("~"), "Music"), help='Directory to write playlist files')
    parser.add_argument('-r', '--root_path', type=str, default='', help='Path to be stripped from each entry')
    parser.add_argument('-p', '--path_prefix', type=str, default='', help='Path added in the beginning of the path. To be used with -r')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--stats', action='store_true', help='Enable statistics mode')
    parser.add_argument('-s', '--separator', type=str, help='Custom separator to use instead of the default OS separator')
    parser.add_argument('--fullname', action='store_true', help='Use full playlist name')

    args = parser.parse_args()
  
    collection_nml_path = ''
    global DEBUG, STATISTIC
    DEBUG = args.debug
    STATISTIC = args.stats
    
    if args.collection:
        collection_nml_path = args.collection
        if not os.path.exists(collection_nml_path):
            print(f"Error: collection.nml not found at {collection_nml_path}")
            return
    else:
        traktor_path = find_latest_traktor_version()

        if traktor_path is None:
            print("Error: Traktor folder not found.")
            return

        if DEBUG:
            print(f"Using Traktor folder: {traktor_path}")
        
        collection_nml_path = os.path.join(traktor_path, "collection.nml")


    if not os.path.exists(collection_nml_path):
        print(f"Error: collection.nml not found at {collection_nml_path}")
        return
    
    output_dir = args.output_dir
    root_path = args.root_path
    path_prefix = args.path_prefix
    custom_separator = args.separator

    playlists = parse_collection_nml(collection_nml_path, args)

    if playlists:
        if DEBUG:
            print("Playlists with at least 1 entry:")
            for playlist in playlists:
                print(f"{playlist.name}: {len(playlist.entries)} entries")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        write_playlist_files(playlists, output_dir, root_path, path_prefix, custom_separator)

        # Overall statistic
        if STATISTIC:
            file_statistics.from_playlist(playlists)

if __name__ == "__main__":
    main()