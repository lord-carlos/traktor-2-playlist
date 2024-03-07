import os

def from_playlist(playlists):
    """
    Collects statistics from a list of playlists.

    Args:
        playlists (list): A list of playlists.

    Returns:
        None
    """
    file_types = {}
    total_files = 0
    for playlist in playlists:
        for entry in playlist.entries:
            _, ext = os.path.splitext(entry)
            file_types[ext] = file_types.get(ext, 0) + 1
            total_files += 1

    scale_factor = 50  # Adjust this to change the scale of the graph
    for file_type, count in file_types.items():
        proportion = count / total_files
        graph_length = int(proportion * scale_factor)
        print(f"{file_type}: {'#' * graph_length} ({count})")