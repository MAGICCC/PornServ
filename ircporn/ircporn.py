#!/usr/bin/env python3

import argparse
import itertools
import json
import pickle
import random
import uuid
import irc3
from irc3.plugins.cron import cron
import praw
import requests
import logging

browsers = []

class RedditBrowser(object):
    def __init__(self, subreddits):
        self.reddit = praw.Reddit("ircporn", check_for_async=False)
        self.dump_file = './ircporn.dump'
        self.subs = {sub_name: None for sub_name in subreddits}
        try:
            with open(self.dump_file, 'rb') as f:
                last_ids = {k: v for k, v in pickle.load(f).items()
                            if k in self.subs}
                self.subs.update(last_ids)
        except FileNotFoundError:
            pass

    def _dump_subs(self):
        with open(self.dump_file, 'wb') as f:
            pickle.dump(self.subs, f)

    def parse_subreddits(self):
        r = []
        for sub in self.subs:
            r.append(self.parse_subreddit(sub))
        self._dump_subs()
        return itertools.chain.from_iterable(r)

    def parse_subreddit(self, sub):
        s = self.reddit.subreddit(sub)
        posts = list(s.new(limit=1))
        r = []
        for post in posts:
            if post.id == self.subs[sub]:
                break
            r.append((post.title, post.url))
        self.subs[sub] = posts[0].id
        return r

    def poll(self):
        return self.parse_subreddits()

def https_if_possible(url):
    if url.startswith('https://'):
        return url
    https_url = 'https' + url[4:]
    try:
        r = requests.head(https_url, timeout=5)
        if r.status_code == 200:
            return https_url
        else:
            return url
    except:
        return url

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
for logger_name in ("praw", "prawcore"):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

@cron('0 */1 * * *')
def fetch_porn(bot):
    for browser in browsers:
        posts = list(browser.poll())
        for (title, url) in posts:
            url = https_if_possible(url)
            for channel in CHANNELS:  # Send message to each channel
                bot.privmsg(channel, f"\x0304NSFW\x0F {url}")

def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--config', required=True, help='Path to the configuration file')
    return parser.parse_args()

def load_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

def main():
    args = parse_args()
    config = load_config(args.config)

    global browsers, CHANNELS  # Use CHANNELS instead of CHANNEL
    CHANNELS = config['channels']
    subreddits = config['subreddits']
    browsers.append(RedditBrowser(subreddits))

    irc3.IrcBot.from_config({
        'host': config['server'],
        'port': config['port'],
        'ssl': config['ssl'],
        'ssl_verify': config['ssl_verify'],
        'autojoins': config['channels'],
        'nick': config['nick'],
        'username': config['username'],
        'realname': config['realname'],
        'sasl_username': config['sasl_username'],
        'sasl_password': config['sasl_password'],
        'verbose': True,
        'includes': [__name__]
    }).run()

if __name__ == '__main__':
    main()
