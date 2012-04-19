#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Very heavily inspired by Idan Gazit's ticket bot

Original ticket bot can be found here:
https://github.com/idangazit/django-ticketbot

Use together with a settings.py file containing:

TICKET_URL = "https://path/to/ticket/%s"
CHANGESET_URL = "https://path/to/changeset/%s"
NICKNAME = "ticketbot"
PASSWORD = "some_secret_pass"
CHANNELS = "#django-dev,#other-channel"
HELP = "Hello, I'm a robot"

A template file (settings.py.inc) is provided for convenience

"""

import sys
import re
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
from settings import (TICKET_URL, CHANGESET_URL, NICKNAME, PASSWORD, CHANNELS,
                      HELP, IGNORE_NICKS_FILE, IGNORE_MSGS_FILE)


TICKET_RE = re.compile(r'#(\d+)')
CHANGESET_RE = re.compile(r'(?:^|\s)\[(\w+)\]')


def load_ignores(filename):
    with open(filename, 'r') as f:
        return [re.compile(l.strip()) for l in f.readlines()
                                      if l.strip() and not l.startswith('#')]


IGNORE_NICKS = load_ignores(IGNORE_NICKS_FILE)
IGNORE_MSGS = load_ignores(IGNORE_MSGS_FILE)


class TicketBot(irc.IRCClient):
    """A bot for URLifying tickets."""

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.setNick(NICKNAME)
        if PASSWORD:
            self.msg('NickServ', 'identify %s' % (PASSWORD))
        for channel in CHANNELS.split(','):
            self.join(channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        tickets = TICKET_RE.findall(msg)
        changesets = CHANGESET_RE.findall(msg)

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            target = user
        else:
            target = channel

        if any([nick_ignore.search(user) for nick_ignore in IGNORE_NICKS]):
            return

        if any([msg_ignore.search(msg) for msg_ignore in IGNORE_MSGS]):
            return

        if msg.startswith(self.nickname) and not tickets and not changesets:
            self.msg(user, HELP)
            return

        for ticket in set(tickets):
            self.msg(target, TICKET_URL % ticket)
        for changeset in set(changesets):
            self.msg(target, CHANGESET_URL % changeset)
        return


class TicketBotFactory(protocol.ClientFactory):
    """A factory for TicketBots.

    A new protocol instance will be created each time we connect to the server.
    """

    # the class of the protocol to build when new connection is made
    protocol = TicketBot

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)

    # create factory protocol and application
    f = TicketBotFactory()

    # connect factory to this host and port
    reactor.connectTCP("chat.freenode.net", 6667, f)

    # run bot
    reactor.run()
