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
import sys
from soco import SoCo

if len(sys.argv) < 2:
    print """
    USAGE: %s <player ip address>"
    """ % sys.argv[0]
else:
    sonos = SoCo(sys.argv[1])
    print 'Player info:'
    print sonos.get_speaker_info()
    print 'Favorite radio:'
    print sonos.get_favorite_radio_stations()
    print 'Queue (%d):' % len(sonos.get_queue())
    print sonos.get_queue()
    print 'Transport info:'
    print sonos.get_current_transport_info()
    print 'Track info:'
    print sonos.get_current_track_info()
