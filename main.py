import os
import xml.etree.ElementTree as ET
import re

DEBUG = True

class Playlist:
    def __init__(self, name, entries):
        self.name = name
        self.entries = entries

def find_latest_traktor_version():
    documents_path = os.path.join(os.path.expanduser("~"), "Documents", "Native Instruments")
    traktor_versions = [folder for folder in os.listdir(documents_path) if folder.startswith("Traktor")]

    version_pattern = re.compile(r"Traktor (\d+\.\d+\.\d+)")

    valid_versions = [version_pattern.match(version).group(1) for version in traktor_versions if version_pattern.match(version)]

    if not valid_versions:
        return None

    latest_version = max(valid_versions, key=lambda v: tuple(map(int, v.split('.'))))
    return os.path.join(documents_path, f"Traktor {latest_version}")

def parse_collection_nml(file_path):
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

def main():
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
        print("Playlists with at least 1 entry:")
        for playlist in playlists:
            print(f"{playlist.name}: {len(playlist.entries)} entries")

        output_dir = input("Enter the directory to write playlist files (press Enter for default): ")
        if not output_dir:
            output_dir = os.path.join(os.path.expanduser("~"), "Music")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for playlist in playlists:
            if playlist.entries:
                playlist_file_path = os.path.join(output_dir, f"{playlist.name}.m3u")
                with open(playlist_file_path, "w") as playlist_file:
                    # Write playlist entries to the M3U file
                    playlist_file.write("#EXTM3U\n")
                    # Replace ':' with '\\' in the file paths for Windows compatibility
                    entries = [entry.replace('/:', '\\') for entry in playlist.entries]
                    playlist_file.write("\n".join(entries))

                print(f"Playlist file '{playlist.name}.m3u' written to {output_dir}")

if __name__ == "__main__":
    main()
