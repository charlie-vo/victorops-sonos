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
# Runs a micro web server to listen for VictorOps webhook alerts.
# Causes a Sonos player on the local network to play an alert sound
# when an incident is created in your VictorOps account.
#
# Enable the notification webhook on your VictorOps settings pages.  The webhook
# URL should be that of the server where this application is running.  For
# example, http://alerts.mycompany.com/alert
#
# Learn more about outgoing notifications on the VictorOps knowledge base:
#     http://victorops.force.com/knowledgebase/articles/Getting_Started/WebHooks/
#
# Requires:
#     SoCo     https://github.com/SoCo/SoCo
#     Flask    https://github.com/mitsuhiko/flask
#
# You may also find helpful:
#     ngrok    https://ngrok.com/
#
# ------------------------------------------------------------------------------

import sys
import soco
import time
import hmac
import hashlib
import base64
import ConfigParser
from soco import SoCo
from flask import Flask
from flask import request

if len(sys.argv) < 2:
    print """
    USAGE: %s <config file>"
    """ % sys.argv[0]
else:
    # Calculate the expected signature of the notification received
    # from VictorOps.
    def calcSig( parameters ):
        # Concatenate this webhook URL and the notification arguments
        buf = alertWebhookURL
        for key in sorted(parameters):
            buf += "%s%s" % (key, parameters[key])

        # Hash the alert details; base64 encode it
        hsh = hmac.new(alertWebhookAuthKey, buf, hashlib.sha1).digest()
        b64 = base64.b64encode(hsh)
        return b64

    # 0:03:18 -> 198
    def timeToInt( timeStr ):
        accum = 0
        mult = 1
        for p in reversed(timeStr.split(':')):
            accum += (int(p)*mult)
            mult *= 60
        return accum

    # Read the config file
    config = ConfigParser.ConfigParser()
    config.read(sys.argv[1])
    sonosPlayer = config.get('vo-sonos-alerts', 'sonosPlayer')
    alertSoundURL = config.get('vo-sonos-alerts', 'alertSoundURL')
    alertWebhookURL = config.get('vo-sonos-alerts', 'alertWebhookURLRoot')
    alertWebhookAuthKey = config.get('vo-sonos-alerts', 'alertWebhookAuthKey')
    listenPort = int(config.get('vo-sonos-alerts','listenPort'))

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
    # VictorOps will POST notification information to this path
    app = Flask(__name__)
    @app.route('/', methods=['POST'])
    def alert():

        # Verify that the alert actually comes from VictorOps by getting
        # the signature header, calculating a signature locally and compare.
        if 'X-VictorOps-Signature' not in request.headers:
            print 'No X-VictorOps-Signature header'
            return "Nope"

        voSignature = request.headers['X-VictorOps-Signature']
        sig = calcSig(request.form)
        if sig != voSignature:
            print "Signatures don't match"
            return 'Nope'

        # Get our player resume position so we can resume after playing
        # the alert sound.
        track = sonos.get_current_track_info()
        playlistPos = int(track['playlist_position'])-1
        trackPos = track['position']
        trackURI = track['uri']

        # This information allows us to resume services like Pandora
        mediaInfo = sonos.avTransport.GetMediaInfo([('InstanceID', 0)])
        mediaURI = mediaInfo['CurrentURI']
        mediaMeta = mediaInfo['CurrentURIMetaData']

        # Play the alert sound, and sleep to allow it to play through
        print 'Playing alert %s' % alertSoundURL
        sonos.play_uri(alertSoundURL)
        alertDuration = sonos.get_current_track_info()['duration']
        sleepTime = timeToInt(alertDuration) + 2
        time.sleep(sleepTime)

        # TODO: Fix resuming Pandora (and other services?) playback
        if len(sonos.get_queue()) > 0 and playlistPos > 0:
            print 'Resume queue from %d: %s - %s' % (playlistPos, track['artist'], track['title'])
            sonos.play_from_queue(playlistPos)
            sonos.seek(trackPos)
        else:
            print 'Resuming %s' % mediaURI
            sonos.play_uri(mediaURI, mediaMeta)

        return "OK"

    if __name__ == "__main__":
        app.run(host='0.0.0.0', port=listenPort, debug=True)
