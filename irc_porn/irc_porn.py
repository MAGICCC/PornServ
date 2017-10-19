#!/usr/bin/env python3
# Copyright (c) 2016, Cyril Roelandt
# Reupload by Peter Stanke (MAGIC), https://git.kthx.at/MAGIC/PornServ
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import itertools
import pickle
import random
import uuid

import irc3
from irc3.plugins.cron import cron
import praw
import requests


CHANNEL = None
NICK = None
browsers = []


class RedditBrowser(object):
    def __init__(self, subreddits):
        self.reddit = praw.Reddit(user_agent='irc-porn')
        self.dump_file = '/tmp/irc-porn-reddit.dump'
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
        s = self.reddit.get_subreddit(sub)
        posts = list(s.get_new(limit=5))
        r = []
        for post in posts:
            if post.id == self.subs[sub]:
                break
            r.append((post.title, post.url))
        self.subs[sub] = posts[0].id
        return r

    def poll(self):
        return self.parse_subreddits()


def random_nick(bot):
    nicks = list(bot.channels[CHANNEL])
    try:
        nicks.remove(NICK)
    except ValueError:
        pass  # Weird, but eh.
    try:
        return random.choice(nicks)
    except IndexError:
        return NICK  # The bot is alone :(


def random_message(bot):
    version = random.randint(0, 2)
    if version == 0:
        return '%s, %s, %s' % (
            random.choice([
                'Bon', 'Alors', 'Putain'
            ]),
            random.choice([
                'bande de connards',
                'les glandus',
                'tas de cons'
            ]),
            random.choice([
                'je vous offre un peu de bon porn',
                'du porn tout frais, pas comme les chattes de vos mères',
                'vous allez bien vous vider les couilles'
            ])
        )
    elif version == 1:
        return random.choice([
            'Bon, lâchez tout et attrapez vos queues.',
            'Allez hop, c\'est l\'heure de se branler !'
        ])
    elif version == 2:
        return '%s: %s' % (
            random_nick(bot),
            random.choice([
                "t'as une petite bite mais tu peux participer quand même",
                "des idées de trucs à faire avec ta copine",
                "mate-moi ça mon cochon, tu vas aimer"
            ]),
        )


def random_message_failure(bot):
    return random.choice([
        "Merde, j'ai pas trouvé de bon pr0n :(",
        "Putain, les Internets sont à sec, "
        "on dirait les burnes de %s." % random_nick(bot)
    ])


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


@cron('0 10,11,12,13,14,15,16,17,18 * * 1-5')
def fetch_porn(bot):
    for browser in browsers:
        posts = list(browser.poll())
        if posts:
            bot.privmsg(CHANNEL, random_message(bot))
        else:
            bot.privmsg(CHANNEL, random_message_failure(bot))
        for (title, url) in posts:
            url = https_if_possible(url)
            url_uid = str(uuid.uuid4())[:6]
            bot.privmsg(CHANNEL, "%s: %s (%s)" % (url_uid, title, url))


def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--server', required=True,
                        help='IRC server to connect to')
    parser.add_argument('--port', required=True, type=int,
                        help='Port to use to connect to IRC')
    parser.add_argument('--channel', required=True,
                        help='Channel to join')
    parser.add_argument('--nick', required=True,
                        help='Nick used by the IRC bot')
    parser.add_argument('--reddit', required=True,
                        help='Comma-separated list of subreddits to parse')
    return parser.parse_args()


def main():
    args = parse_args()
    global browsers, CHANNEL, NICK
    CHANNEL = args.channel
    NICK = args.nick
    subreddits = args.reddit.split(',')
    browsers.append(RedditBrowser(subreddits))

    irc3.IrcBot(
        nick=NICK,
        autojoins=[CHANNEL],
        host=args.server,
        port=args.port,
        ssl=True,
        ssl_verify='CERT_NONE',
        verbose=True,
        includes=[
            'irc3.plugins.userlist',
            __name__,
        ]).run()


if __name__ == '__main__':
    main()
