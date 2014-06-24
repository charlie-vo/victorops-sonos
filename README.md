victorops-sonos
===============

Send and receive VictorOps notifications to and from your Sonos Wireless HiFi

These are simple Python scripts that demonstrate two-way interaction between VictorOps
and your Sonos system.

Both applications take a configuration file as a command line argument.   A example
configuration file is provided (vo-sonos.ini.example).

# Requirements
Both applications require [SoCo](http://python-soco.com/)

Sonos Alert requires [Flask](http://flask.pocoo.org/docs/)

# Now Playing
**vo-sonos-now-playing.py**

This application polls your Sonos player on an interval and sends an informational alert into
your company's VictorOps timeline whenever a new track plays.

Alerts are sent to VictorOps using the REST API.  To enable the REST API integration, go to
your account's Integration Settings.  Enable the REST Endpoint integration.  Within the endpoint
URL shown, you will find your API key (something like 9e53cc2c-f4b3-11e3-84e6-a7d88885f031).
Copy that key into your configuration file for the Now Playing application.

[More about the VictorOps alert ingestion REST API](http://victorops.force.com/knowledgebase/articles/Integration/Alert-Ingestion-API-Documentation/)

#Sonos Alert
**vo-sonos-alerts.py**

This application runs a micro web server and accepts calls from the VictorOps outgoing notification
webhook.  Whenever a notification is sent for an incident in your VictorOps account, the webhook
will be invoked, and your Sonos system will play the alert track of your choice.

As with all VictorOps alerting policies, you have fine-grained control over which notifications are
sent to your Sonos.

To enable the VictorOps webhook notification for your account, go to your account's Integration Settings.  Click Outgoing
Notifications Webhooks and add one for the Sonos Alert application.  The URL will be whatever address will reach the alert
application when you run it.  Copy the URL and generated Auth Code into the configuration file for the Sonos Alert
application.

[More about the VictorOps notification webhook](http://victorops.force.com/knowledgebase/articles/Getting_Started/WebHooks/)

