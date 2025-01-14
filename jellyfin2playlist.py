import requests
import os

# Configuration
JELLYFIN_SERVER_URL = "http://your-jellyfin-server-url"
API_KEY = "your-api-key"
USER_ID = "your-user-id"

# Path manipulation variables
REMOVE_PATH_PREFIX = "/mnt/music/"
ADD_PATH_PREFIX = os.path.expanduser("~/Music/")
PLAYLIST_NAME = os.path.expanduser("~/Music/playlists/Favorites.m3u")

def get_favorites():
    """
    Fetch favorite music items and create an .m3u playlist on the local disk.
    """
    # Construct the API endpoint URL
    endpoint = f"{JELLYFIN_SERVER_URL}/Users/{USER_ID}/Items"

    # Set the headers for the API request
    headers = {
        "X-Emby-Token": API_KEY
    }

    # Set query parameters to filter for favorites and include the Path field
    params = {
        "IsFavorite": "true",
        "Recursive": "true",
        "IncludeItemTypes": "Audio",
        "Fields": "Path"
    }

    try:
        # Make the GET request to the Jellyfin API
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        items = response.json().get("Items", [])

        if not items:
            print("No favorite music items found.")
            return

        # Collect paths for the playlist
        playlist_paths = []
        for item in items:
            path = item.get("Path")
            if not path:
                print(f"Skipping item without a path: {item.get('Name', 'Unknown Name')}")
                continue

            # Adjust the path
            adjusted_path = path.replace(REMOVE_PATH_PREFIX, "", 1)
            final_path = os.path.join(ADD_PATH_PREFIX, adjusted_path)

            playlist_paths.append(final_path)

        # Write the .m3u playlist
        with open(PLAYLIST_NAME, "w", encoding="utf-8") as playlist_file:
            playlist_file.write("#EXTM3U\n")  # Playlist header
            for path in playlist_paths:
                playlist_file.write(path + "\n")

        print(f"Playlist created: {PLAYLIST_NAME}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching favorite items: {e}")

# Run the function
if __name__ == "__main__":
    get_favorites()
