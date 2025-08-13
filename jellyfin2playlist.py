import requests
import os
import logging

# Get logger for this module
logger = logging.getLogger(__name__)


def get_favorites(jellyfin_server_url, api_key, user_id, remove_path_prefix, add_path_prefix, playlist_name):
    """
    Fetch favorite music items and create an .m3u playlist on the local disk.
    
    Args:
        jellyfin_server_url (str): The URL of the Jellyfin server.
        api_key (str): The API key for the Jellyfin server.
        user_id (str): The user ID for the Jellyfin server.
        remove_path_prefix (str): Prefix to remove from the Jellyfin file paths.
        add_path_prefix (str): Prefix to add to the local file paths.
        playlist_name (str): Path to save the .m3u playlist file.
    """
    logger.info("Fetching favorites from Jellyfin server")
    logger.debug(f"Server URL: {jellyfin_server_url}")
    logger.debug(f"User ID: {user_id}")
    
    # Construct the API endpoint URL
    endpoint = f"{jellyfin_server_url}/Users/{user_id}/Items"

    # Set the headers for the API request
    headers = {
        "X-Emby-Token": api_key
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
            logger.warning("No favorite music items found.")
            return

        logger.info(f"Found {len(items)} favorite items")
        
        # Collect paths for the playlist
        playlist_paths = []
        skipped_items = 0
        for item in items:
            path = item.get("Path")
            if not path:
                logger.debug(f"Skipping item without a path: {item.get('Name', 'Unknown Name')}")
                skipped_items += 1
                continue

            # Adjust the path
            adjusted_path = path.replace(remove_path_prefix, "", 1)
            final_path = os.path.join(add_path_prefix, adjusted_path)
            logger.debug(f"Processed path: {path} -> {final_path}")

            playlist_paths.append(final_path)

        if skipped_items > 0:
            logger.warning(f"Skipped {skipped_items} items due to missing paths")
            
        # Ensure the directory for the playlist exists
        playlist_dir = os.path.dirname(playlist_name)
        if playlist_dir and not os.path.exists(playlist_dir):
            os.makedirs(playlist_dir)
            logger.debug(f"Created directory for playlist: {playlist_dir}")

        # Write the .m3u playlist
        with open(playlist_name, "w", encoding="utf-8") as playlist_file:
            playlist_file.write("#EXTM3U\n")  # Playlist header
            for path in playlist_paths:
                playlist_file.write(path + "\n")

        logger.info(f"Playlist created: {playlist_name} with {len(playlist_paths)} tracks")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching favorite items: {e}")


def fetch_jellyfin_favorites(jellyfin_server_url, api_key, user_id, remove_path_prefix, add_path_prefix, playlist_name):
    """
    Main function to fetch favorites from Jellyfin and create a playlist.
    
    Args:
        jellyfin_server_url (str): The URL of the Jellyfin server.
        api_key (str): The API key for the Jellyfin server.
        user_id (str): The user ID for the Jellyfin server.
        remove_path_prefix (str): Prefix to remove from the Jellyfin file paths.
        add_path_prefix (str): Prefix to add to the local file paths.
        playlist_name (str): Path to save the .m3u playlist file.
    """
    logger.info("Starting Jellyfin favorites fetch")
    logger.debug(f"Remove path prefix: {remove_path_prefix}")
    logger.debug(f"Add path prefix: {add_path_prefix}")
    logger.debug(f"Playlist name: {playlist_name}")
    
    get_favorites(jellyfin_server_url, api_key, user_id, remove_path_prefix, add_path_prefix, playlist_name)
    
    logger.info("Jellyfin favorites fetch completed")
