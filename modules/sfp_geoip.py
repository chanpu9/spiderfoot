#-------------------------------------------------------------------------------
# Name:         sfp_geoip
# Purpose:      SpiderFoot plug-in to identify the Geo-location of IP addresses
#               identified by other modules.
#
# Author:      Steve Micallef <steve@binarypool.com>
#
# Created:     18/02/2013
# Copyright:   (c) Steve Micallef 2013
# Licence:     GPL
#-------------------------------------------------------------------------------

import sys
import re
import json
import socket
from sflib import SpiderFoot, SpiderFootPlugin

# SpiderFoot standard lib (must be initialized in setup)
sf = None

class sfp_geoip(SpiderFootPlugin):
    """Identifies the physical location of IP addresses identified."""

    # Default options
    opts = { }

    # URL this instance is working on
    seedUrl = None
    baseDomain = None # calculated from the URL in setup
    results = dict()

    def setup(self, sfc, url, userOpts=dict()):
        global sf

        sf = sfc
        self.seedUrl = url
        self.results = dict()

        for opt in userOpts.keys():
            self.opts[opt] = userOpts[opt]

        # Extract the 'meaningful' part of the FQDN from the URL
        self.baseDomain = sf.urlBaseDom(self.seedUrl)

    # What events is this module interested in for input
    def watchedEvents(self):
        return ['IP_ADDRESS']

    # Handle events sent to this module
    def handleEvent(self, srcModuleName, eventName, eventSource, eventData):
        sf.debug("Received event, " + eventName + ", from " + srcModuleName)

        # Don't look up stuff twice
        if self.results.has_key(eventData):
            sf.debug("Skipping " + eventData + " as already mapped.")
            return None
        else:
            self.results[eventData] = True

        res = sf.fetchUrl("http://api.hostip.info/get_json.php?ip=" + eventData)
        if res['content'] == None:
            sf.debug("No GeoIP info found for " + eventData)
        hostip = json.loads(res['content'])
        countrycity = hostip['country_name'] + " (" + hostip['city'] + ")"

        self.notifyListeners("GEOINFO", eventData, countrycity)

        return None

# End of sfp_geoip class

if __name__ == '__main__':
    print "This module cannot be run stand-alone."
    exit(-1)
