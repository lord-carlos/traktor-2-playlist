# traktor-2-playlist
Exports playlist from traktor collection.nml to .m3u playlist files.
It can make the path to relative.

Currently windows only. (Might actually work on mac, please test)

Work in progress

![shitty logo](image.png)

## How to use

If you use it without any arguments, it will try to find the latest `collection.nml` and dump every playlist into `~/Music`

You can use it in a way to make the path relative. For example if all you files are in `C:\Users\hans\Music` but you want to share the music folder on another device. You can use the `--root_path` option to remove the `C:\Users...` part. If you at the same time save the playlists to the music folder they should still work.

But what if you want all the playlist into a `Playlists` folder in the music folder? Then you need to add the prefix `..\` with `-p` parameter.

All of that could look something like this:

```bash
python ./traktor2playlist -o "C:\MyMusic\MyPlaylists" -r "C:\MyMusic\" -p "..\"
```

That will write all the playlist into the `MyPlaylits` folder and each line starts with `..\` without the `C:\..`

## Available Options

- `-c` or `--collection`: Specifies the path to the `collection.nml` file. If none is given, the script will try to find it automatically.

- `-o` or `--output_dir`: Specifies the directory where the playlist files will be written. By default, this is the "Music" folder in the user's home directory.

- `-r` or `--root_path`: Specifies the path to be stripped from each entry in the playlist files. (Optional)

- `-p` or `--path_prefix`: Specifies the path to be added at the beginning of each entry in the playlist files. This is to be used with `-r`. For example `-r "..\"`

- `-d` or `--debug`: Enables debug mode.

- `--stats`: Enables statistics mode.

- `-s` or `--seprator`: instead of OS separator it will use one of your choice
