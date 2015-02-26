#!/usr/bin/env python2

##############################################################################
### NZBGET QUEUE/POST-PROCESSING SCRIPT                                    ###

# Windows Phone 8 and Windows 8 Toast Notifier
#
# NOTE: This script requires Python 2.x.

##############################################################################
### OPTIONS                                                                ###

# Notify on Success (yes, no).
#
#Success=yes

# Notify on Failure and Warnings (yes, no).
#
#Failure=yes

# Notify on Add (yes, no).
#
#NewAdd=yes

# PushAlot API Token
#
# Your PushAlot API Token from https://pushalot.com/manager/authorizations
#AuthToken=

# Silent Delivery (yes, no).
#
# If enabled, will only update badge count and won't send Toast notification
#Silent=no

# Purge new alert
#
# Time to purge new download notification. (Default 5 minutes)
#NewPurge = 5

# Expires
#
# Number of minutes before message automatically purged. (Set to 0 to disable)
#Expires=0

# Include URL (yes, no).
#
# Include a URL to open NZBGet in the push?
#ShowURL=no

# NZBGet URL
#
# URL to your NZBGet host
#url=http://

# URL Title
#
# Title to display (If you need to localize)
#title=Open NZBGet

### NZBGET QUEUE/POST-PROCESSING SCRIPT                                    ###
##############################################################################

import os
import sys
import urllib
import httplib2
import simplejson as json

# Statuses
nzb_status = os.environ.get('NZBPP_TOTALSTATUS')
nzb_event = os.environ.get('NZBNA_EVENT')
on_success = os.environ.get('NZBOP_PUSHALOT2_PY_SUCCESS')
on_fail = os.environ.get('NZBOP_PUSHALOT2_PY_FAILURE')
on_add = os.environ.get('NZBOP_PUSHALOT2_PY_NEWADD')

# Read Settings
token = os.environ.get('NZBOP_PUSHALOT2_PY_AUTHTOKEN')
silent = os.environ.get('NZBOP_PUSHALOT2_PY_SILENT')
purge_ttl = os.environ.get('NZBOP_PUSHALOT2_PY_NEWPURGE')
ttl = os.environ.get('NZBOP_PUSHALOT2_PY_EXPIRES')
show_url = os.environ.get('NZBOP_PUSHALOT2_PY_SHOWURL')
display_url = os.environ.get('NZBOP_PUSHALOT2_PY_URL')
display_title = os.environ.get('NZBOP_PUSHALOT2_PY_TITLE')

# Exit codes
PP_SUCCESS = 93
PP_ERROR = 94


def sendPush(title, message, ttl):
    http = httplib2.Http()
    url = 'https://pushalot.com/api/sendmessage'
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    image = 'https://raw.githubusercontent.com/exiva/nzbget-pushalot/master/nzbget.png'
    body = {
        'AuthorizationToken': token,
        'Title': title,
        'Body': message,
        'Image': image,
    }
    if ttl != "0":
        body.update({'TimeTolive': ttl})

    if silent == 'yes':
        body.update({'IsSilent': 'True'})

    if show_url == 'yes':
        body.update({
            'Link': display_url,
            'LinkTitle': display_title
            })

    try:
        resp, cont = http.request(url, 'POST', headers=headers,
                                  body=urllib.urlencode(body))
    except Exception as e:
        print "[ERROR] Couldn't send pushalot. {}".format(e)
        sys.exit(PP_ERROR)
    else:
        if int(resp['status']) != 200:
            try:
                error_json = json.loads(cont)
            except json.JSONDecodeError:
                print "[ERROR] pushalot: json malformed"
                sys.exit(PP_ERROR)
            else:
                desc = error_json['Description']
                print "[ERROR] pushalot: There was an error. {} {}".format(
                    resp['status'], desc)
                sys.exit(PP_ERROR)
        else:
            sys.exit(PP_SUCCESS)

# Check status of download.
# SUCCESS, WARNING, FAILURE, NZB_ADDED
if nzb_status == "SUCCESS" and on_success == "yes":
    sendPush("Download Complete", os.environ.get('NZBPP_NZBNAME'), ttl)

if nzb_status == "WARNING" and on_fail == "yes":
    sendPush("Download Incomplete", os.environ.get('NZBPP_NZBNAME'), ttl)

if nzb_status == "FAILURE" and on_fail == "yes":
    sendPush("Download Failed", os.environ.get('NZBPP_NZBNAME'), ttl)

if nzb_event == "NZB_ADDED" and on_add == "yes":
    sendPush("Added To Queue", os.environ.get('NZBNA_NZBNAME'), purge_ttl)
