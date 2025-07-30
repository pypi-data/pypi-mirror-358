# Aria2TUI

Aria2TUI is a TUI frontend for the Aria2 download utility.


https://github.com/user-attachments/assets/07ab1f63-3a5e-42dd-bddb-56c948ecd620

## Quickstart

Aria2TUI fetches the download data from the aria2c daemon over RPC and displays it using list_picker. As both Aria2TUI and list_picker are in active development you will need to clone both repositories.

```
git clone https://github.com/grimandgreedy/Aria2TUI

cd Aria2TUI && python -m pip install -r requirements

cd ..

git clone https://github.com/grimandgreedy/list_picker

cd list_picker && python -m pip install -r requirements
```

Edit the config.toml in the aria2tui repo and make sure your url, port, and secret token are correct.

 - Note that starting/restarting the aria2 daemon is done using systemd by default. There is a sample service file that you can put in ~/.config/systemd/user/. You can also change the cmds that are run in the config.

Navigate to the aria2tui repo and run aria2tui.py

```
python aria2tui.py
```

or if you have multiple daemons you can specify another config file:

```
ARIA2TUI_CONFIG_PATH=/path/to/config/aria2c_torrents.toml python aria2tui.py

ARIA2TUI_CONFIG_PATH=/path/to/config/aria_on_home_server_config.toml python aria2tui.py
```

If you wish to use it regularly, then for the moment the best way to make it accessible to your PATH is to simply add aliases to your ~/.bashrc.
```
alias a2="python /path/to/Aria2TUI/aria2tui.py"

alias a2t="ARIA2TUI_CONFIG_PATH=/path/to/config/aria2c_torrents.toml python /path/to/Aria2TUI/aria2tui.py"

alias a2n="ARIA2TUI_CONFIG_PATH=/path/to/config/aria_on_home_server_config.toml python /path/to/Aria2TUI/aria2tui.py"
```

in addition to those requirements the application uses:
 - `yazi` for opening download locations
 - `nvim` for viewing/editing download options as well as adding URIs, magnet links and torrent files
 - `xdg-open` and `gio` for opening files.

## Tips

 - Press '?' to see the help page which will list the available keys.

## Features

 - Dynamic display of downloads
     - View active, queue, errored, stopped
 - Sort/filter/search using regular expressions
 - Add downloads with options
   - Simply dump a list of links;
     - or specify options:
       - proxy
       - User agent
       - ... Many more!
          - See [this section of the aria2c manual](https://aria2.github.io/manual/en/html/aria2c.html#input-file) for all available options all of which are supported
 - Add magnet links and torrent files
 - Operations on downloads:
   - Pause/unpause
   - Remove
   - Change position in queue
   - Open downloaded files
   - Open download location (with yazi)
   - Change download options by value of keys in nvim

     - Select download(s) you wish to change the value
     - Change save directory
     - Specify proxy, proxy user, and proxy password
     - Specify user-agent
     - Specify download piece length
     - ... Many more!
         - See [this section of the aria2c manual](https://aria2.github.io/manual/en/html/aria2c.html#input-file) for all available options all of which are supported.

<div align="center"> <img src="assets/change_options.gif" alt="change_options" width="70%"> </div>

   - View current options of download
   - Retry download
 - Interact with aria2 daemon
   - Edit config
   - Pause all
   - Restart aria
 - Global and particular download transfer speed *graphs*.

  <div align="center"> <img src="assets/transfer_speed_graph.png" alt="speed_graph" width="70%"> </div>

 - Visual options
   - Modify theme
     - '~' to view settings and then select theme

<div align="center"> <img src="assets/themes.png" alt="themes" width="70%"> </div>

   - Show/hide columns
     - Press Shift+Column_number to toggle or press '~' to view settings and find the column you wish to toggle.
   - Quick-toggle footer: press '_'


## Important

While I use Aria2TUI every day, it is still in development and there are many things that still need to be cleaned up.

Some things that should be mentioned:

 - Realistically Aria2TUI will only work in a UNIX (linux, macos) environment. If you register your interest I might be able to look into what I would need to change.
 - If you are performing bulk operations and the downloads are changing state rapidly--e.g., hundreds of images are changing from active/waiting to completed--it is recommended to stop the auto-refresh and operate on a static list.
    - This can be done by either:
      - exiting to the main menu ('q') and going to "View Downloads"; or
      - Pressing ~ and toggling the auto-refresh in the default "Watch Downloads" viewer.
    - You know that auto-refresh is active because there is a refresh symbol in the top right.
 - Note: This was created for personal use and so some of the code is quite ugly and/or buggy and simply needs to be re-written.

## Similar Projects

- [Ariang](https://github.com/mayswind/AriaNg) A web client for aria2c.

## Support and Feedback

Feel free to request features. Please report any errors you encounter with appropriate context.
