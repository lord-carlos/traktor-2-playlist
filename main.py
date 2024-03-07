import os
import xml.etree.ElementTree as ET
import re
import file_statistics

DEBUG = True
STATISTIC = True

class Playlist:
    def __init__(self, name, entries):
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

def parse_collection_nml(file_path):
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

        for node in root.findall(".//NODE[@TYPE='PLAYLIST']"):
            playlist_name = node.get("NAME")
            entries = []

            for entry_node in node.findall(".//ENTRY/PRIMARYKEY"):
                track_key = entry_node.get("KEY")
                entries.append(track_key)

            if entries:
                playlists.append(Playlist(playlist_name, entries))

    except ET.ParseError as e:
        if DEBUG:
            print(f"Error parsing XML: {e}")
        return None

    return playlists

def write_playlist_files(playlists, output_dir, root_path):
    for playlist in playlists:
        if playlist.entries:
            playlist_file_path = os.path.join(output_dir, f"{playlist.name}.m3u")
            with open(playlist_file_path, "w") as playlist_file:
                    # Write playlist entries to the M3U file
                playlist_file.write("#EXTM3U\n")

                    # Replace ':' with '\\' in the file paths for Windows compatibility
                entries = [entry.replace('/:', '\\') for entry in playlist.entries]
                    # Remove the root path of every entry if root_path is provided
                if root_path:
                    entries = [entry.replace(root_path, '') for entry in entries]

                playlist_file.write("\n".join(entries))

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

    playlists = parse_collection_nml(collection_nml_path)

    if playlists:
        if DEBUG:
            print("Playlists with at least 1 entry:")
            for playlist in playlists:
                print(f"{playlist.name}: {len(playlist.entries)} entries")

        output_dir_default = os.path.join(os.path.expanduser("~"), "Music")
        output_dir = input("Enter the directory to write playlist files (press Enter for {}): ".format(output_dir_default))
        if not output_dir:
            output_dir = output_dir_default

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(f"Please provide a root path for relative paths.")
        root_path = input("(Optional) path to be stripped from each entry: ")

        write_playlist_files(playlists, output_dir, root_path)

        # Overall statistic
        if STATISTIC:
            file_statistics.from_playlist(playlists)

if __name__ == "__main__":
    main()
