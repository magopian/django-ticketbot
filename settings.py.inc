#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Settings file used by the ticket bot"""

TICKET_URL = "https://path/to/ticket/%s"
CHANGESET_URL = "https://path/to/changeset/%s"
NICKNAME = "ticketbot"
PASSWORD = "" # nickserv pass, optional
CHANNELS = "#django-dev,#other-channel" # comma separated list of channels
HELP = """Hi, I'm a ticketbot. I know how to linkify tickets like \"#12345\", and changesets like \"r12345\" or \"[12345]\"."""
