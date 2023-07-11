# PornServ

PornServ posts porn from Reddit (and maybe other sites one day!) to IRC. No need
to explain why this is great.

## Installation

Before you can use PornServ, you must first [register](https://old.reddit.com/prefs/apps/) an application on Reddit and then you need the four pieces of information to add into your `praw.ini` file:

**client_id**: The client ID is at least a 14-character string listed just under "personal use script" for the desired [developed application](https://www.reddit.com/prefs/apps/)  
**client_secret**: The client secret is at least a 27-character string listed adjacent to
    ``secret`` for the application.  
**password**: The password for the Reddit account used to register the application.  
**username**: The username of the Reddit account used to register the application.


Then you have to edit the `config.json` file to reflect the IRC options. This is pretty self-explanatory:
```
{
  "server": "irc.example.net",
  "port": 6697,
  "ssl": "True",
  "ssl_verify": "CERT_NONE",
  "channels": ["#channel1", "#channel2", "#channel3"],
  "nick": "mybot",
  "username": "mybot",
  "realname": "my bot",
  "sasl_username": "username",
  "sasl_password": "password",
  "subreddits": ["pics", "gifs", "nsfw"]
}
```


Finally start the bot - an example `docker-compose.yml` file below:

```
version: "3"

services:
  ircporn:
    image: magic848/pornserv:latest
    volumes:
      - .:/data
    working_dir: /data
    command: python ircporn.py
     --config /data/config.json
    restart: always
```