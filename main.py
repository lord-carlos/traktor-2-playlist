import argparse
import configparser
import os
import sys
import logging
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from traktor2playlist import export_playlists, ExportConfig
from playlist2traktor import import_playlist
from jellyfin2playlist import fetch_jellyfin_favorites
from traktor_utils import find_latest_traktor_version
from logger_utils import setup_logging_from_config


def load_config(config_file_path="config.ini"):
    """Load configuration from config.ini."""
    config = configparser.ConfigParser()
    if os.path.exists(config_file_path):
        config.read(config_file_path)
    return config


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Traktor Playlist Manager: Export, import, and manage playlists.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s export -c /path/to/collection.nml -o /path/to/output
  %(prog)s import -m /path/to/playlist.m3u -n "My New Playlist"
  %(prog)s jellyfin --config /path/to/config.ini
        """
    )
    
    # Global options
    parser.add_argument(
        "--config",
        default="config.ini",
        help="Path to configuration file (default: config.ini)"
    )
    
    # Subparsers for different actions
    subparsers = parser.add_subparsers(dest='action', help='Action to perform')
    
    # Export subcommand
    export_parser = subparsers.add_parser('export', help='Export Traktor playlists to M3U files')
    export_parser.add_argument(
        '-c', '--collection',
        help='Path to collection.nml. If not provided, will try to find it automatically.'
    )
    export_parser.add_argument(
        '-o', '--output_dir',
        default=os.path.join(os.path.expanduser("~"), "Music"),
        help='Directory to write playlist files (default: ~/Music)'
    )
    export_parser.add_argument(
        '-r', '--root_path',
        default='',
        help='Path to strip from each entry'
    )
    export_parser.add_argument(
        '-p', '--path_prefix',
        default='',
        help='Path to add at the beginning of each entry'
    )
    export_parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable debug mode (overrides config file setting)'
    )
    export_parser.add_argument(
        '--stats',
        action='store_true',
        help='Enable statistics mode'
    )
    export_parser.add_argument(
        '-s', '--separator',
        help='Custom separator to use instead of the default OS separator'
    )
    export_parser.add_argument(
        '--fullname',
        action='store_true',
        help='Use full playlist name (including folder)'
    )
    
    # Import subcommand
    import_parser = subparsers.add_parser('import', help='Import M3U playlist into Traktor')
    import_parser.add_argument(
        '-m', '--m3u_playlist',
        required=True,
        help='Path to the .m3u file to import'
    )
    import_parser.add_argument(
        '-c', '--collection',
        help='Path to collection.nml. If not provided, will try to find it automatically.'
    )
    import_parser.add_argument(
        '-n', '--playlist_name',
        default="ImportedPlaylist",
        help='Base name for the new playlist in Traktor (default: ImportedPlaylist)'
    )
    import_parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable debug mode (overrides config file setting)'
    )
    
    # Jellyfin subcommand
    jellyfin_parser = subparsers.add_parser('jellyfin', help='Fetch favorites from Jellyfin server')
    jellyfin_parser.add_argument(
        '--jellyfin_server_url',
        help='Jellyfin server URL'
    )
    jellyfin_parser.add_argument(
        '--api_key',
        help='Jellyfin API key'
    )
    jellyfin_parser.add_argument(
        '--user_id',
        help='Jellyfin user ID'
    )
    jellyfin_parser.add_argument(
        '--remove_path_prefix',
        help='Prefix to remove from Jellyfin file paths'
    )
    jellyfin_parser.add_argument(
        '--add_path_prefix',
        help='Prefix to add to local file paths'
    )
    jellyfin_parser.add_argument(
        '--playlist_name',
        help='Path to save the .m3u playlist file'
    )
    jellyfin_parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable debug mode (overrides config file setting)'
    )
    
    return parser


def main():
    """Main function to parse arguments and execute the appropriate action."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        return
    
    # Load configuration
    config = load_config(args.config)
    
    # Set up logging
    # If --debug flag is used, override config file setting
    if hasattr(args, 'debug') and args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    else:
        setup_logging_from_config(args.config)
    
    # Get logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Starting Traktor Playlist Manager")
    
    # Handle actions
    if args.action == 'export':
        # Merge config with args for export
        if config.has_section('traktor'):
            if not args.collection and config.has_option('traktor', 'collection_path'):
                args.collection = config.get('traktor', 'collection_path')
            if not args.output_dir and config.has_option('traktor', 'output_dir'):
                args.output_dir = config.get('traktor', 'output_dir')
                
        # Auto-detect collection.nml if not provided
        if not args.collection:
            traktor_path = find_latest_traktor_version()
            if traktor_path:
                args.collection = os.path.join(traktor_path, "collection.nml")
                logger.info(f"Using auto-detected collection.nml: {args.collection}")
            else:
                logger.error("Could not auto-detect collection.nml and no path provided.")
                return
                
        # Create ExportConfig from args
        export_config = ExportConfig(
            collection_path=args.collection,
            output_dir=args.output_dir,
            root_path=args.root_path,
            path_prefix=args.path_prefix,
            debug=getattr(args, 'debug', False),
            stats=args.stats,
            separator=args.separator,
            fullname=args.fullname
        )
        
        export_playlists(export_config)
        
    elif args.action == 'import':
        # Merge config with args for import
        if config.has_section('traktor'):
            if not args.collection and config.has_option('traktor', 'collection_path'):
                args.collection = config.get('traktor', 'collection_path')
                
        # Auto-detect collection.nml if not provided
        if not args.collection:
            traktor_path = find_latest_traktor_version()
            if traktor_path:
                args.collection = os.path.join(traktor_path, "collection.nml")
                logger.info(f"Using auto-detected collection.nml: {args.collection}")
            else:
                logger.error("Could not auto-detect collection.nml and no path provided.")
                return
                
        import_playlist(args.m3u_playlist, args.collection, args.playlist_name)
        
    elif args.action == 'jellyfin':
        # Check if required Jellyfin config options are available
        # Get required parameters from config or command line
        jellyfin_server_url = args.jellyfin_server_url or (config.get('jellyfin', 'server_url') if config.has_section('jellyfin') and config.has_option('jellyfin', 'server_url') else None)
        api_key = args.api_key or (config.get('jellyfin', 'api_key') if config.has_section('jellyfin') and config.has_option('jellyfin', 'api_key') else None)
        user_id = args.user_id or (config.get('jellyfin', 'user_id') if config.has_section('jellyfin') and config.has_option('jellyfin', 'user_id') else None)
        
        # These can be in config or passed via command line
        remove_path_prefix = args.remove_path_prefix or (config.get('jellyfin', 'remove_path_prefix') if config.has_section('jellyfin') and config.has_option('jellyfin', 'remove_path_prefix') else "/mnt/music/")
        add_path_prefix = args.add_path_prefix or (config.get('jellyfin', 'add_path_prefix') if config.has_section('jellyfin') and config.has_option('jellyfin', 'add_path_prefix') else os.path.expanduser("~/Music/"))
        playlist_name = args.playlist_name or (config.get('jellyfin', 'playlist_name') if config.has_section('jellyfin') and config.has_option('jellyfin', 'playlist_name') else os.path.expanduser("~/Music/playlists/Favorites.m3u"))
        
        # Validate required parameters
        if not all([jellyfin_server_url, api_key, user_id]):
            logger.error("Missing required Jellyfin configuration (server_url, api_key, user_id).")
            logger.error("Please provide these in config.ini or as command-line arguments.")
            return
            
        fetch_jellyfin_favorites(
            jellyfin_server_url,
            api_key,
            user_id,
            remove_path_prefix,
            add_path_prefix,
            playlist_name
        )


if __name__ == "__main__":
    main()