# Deweybot
Discord bot using discord.py for the [okayxairen](https://www.youtube.com/@okayxairen2) (and maybe other) discord server

## Running
Copy `examples/dewey.yaml.example` to the same directory as StartBot.py and fill it out

Run `./StartBot.py` directly or with `python3` or `py`


### Systemd service
To use the systemd service, fill in `ExecStart` (with the path to StartBot.py), `WorkingDirectory` (with the path containing StartBot.py), and `User` (with your user/the account you want the bot to run as), then copy it to `/etc/systemd/system/deweybot.service`

Run:
```
sudo systemctl daemon-reload
sudo systemctl enable deweybot
sudo systemctl start deweybot
```

To view logs, run `sudo journalctl -eu deweybot.service`