#!/usr/bin/python
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2014 VictorOps, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ------------------------------------------------------------------------------
#
# Sends INFO level alerts to your VictorOps timeline with the artist and track
# name playing on your Sonos player.
#
# Enable the REST API integration on your VictorOps settings pages, and use
# the API key for this program.
#
# Requires:
#     SoCo     https://github.com/SoCo/SoCo
#
# ------------------------------------------------------------------------------

import sys
import soco
import json
import time
import ConfigParser
from httplib2 import Http
from urllib import urlencode
from soco import SoCo

if len(sys.argv) < 2:
    print """
    USAGE: %s <config file>"
    """ % sys.argv[0]
else:
    # Read the config file
    config = ConfigParser.ConfigParser()
    config.read(sys.argv[1])
    sonosPlayer = config.get('vo-sonos-now-playing', 'sonosPlayer')
    pollInterval = int(config.get('vo-sonos-now-playing', 'pollInterval'))
    apiKey = config.get('vo-sonos-now-playing', 'apiKey')
    routingKey = config.get('vo-sonos-now-playing', 'routingKey')

    # Connect to the player
    sonos = None
    for zone in soco.discover():
        if zone.player_name == sonosPlayer:
            sonos = SoCo(zone.ip_address)
            break
    if sonos == None:
        print 'Player %s not found' % sonosPlayer
        sys.exit(1)

    print 'Connected to Sonos %s' % sonosPlayer
    entity = '%s Sonos' % sonos.player_name
    vourl = 'https://alert.victorops.com/integrations/generic/20131114/alert/%s/%s' % (apiKey, routingKey)
    oldmsg = ''

    # Just run forever, polling the player for the current track
    while True:
        track = sonos.get_current_track_info()
        msg = '%s - %s' % ( track['artist'], track['title'] )
        msg = msg.encode('utf-8')
        if oldmsg != msg:
            print time.strftime("%H:%M:%S")
            print msg
            data = {'message_type': 'INFO', 'state_message': msg, 'entity_id': entity}
            headers = {'Content-type': 'application/json'}
            resp, content = Http().request(vourl, "POST", json.dumps(data), headers=headers)
            print resp
            print content
        oldmsg = msg
        time.sleep(pollInterval)
