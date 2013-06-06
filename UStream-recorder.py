#!/usr/bin/env python
# This script finds the rtmpdump command syntax for opening a UStream stream.
 
import sys
import urllib2
import re
 
 
def getVideoData(url):
    # Get the HTML contents
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    html = response.read()
 
    # Extract the channel ID from the HTML
    channelId = re.search("ustream.vars.channelId=(\d+)", html).group(1)

    # Extract the channel title from the HTML
    channelTitle = None
    m = re.search("ustream.vars.channelTitle=\"([^\"]+)\"", html)
    if (m):
      channelTitle = m.group(1)

    if (not channelTitle):
      m = re.search("property\=\"og\:url\"\s+content\=\"http\:\/\/www." +
        "ustream\.tv\/(?:channel\/)?([^\"]+)\"", html)
      if (m):
        channelTitle = m.group(1)

    amfContent = None
    if (channelId):
        amfUrl = "http://cdngw.ustream.tv/Viewer/getStream/1/%s.amf" % channelId
        print "AMF URL: %s" % amfUrl
        response = urllib2.urlopen(amfUrl)
        amfContent = response.read()
        streams = []

        try:
          rtmpUrl, streamName = re.search("\x00\x06cdnUrl\x02\x00.(rtmp:[^\x00]+)\x00\x0astreamName\x02\x00.([^\x00]+)", amfContent).groups()
        except AttributeError:
          print "Error! Can't find rtmp stream in AMF object."
          exit(1)

        streams.append({"url":rtmpUrl, "name":streamName})

        altPtn = re.compile("\x00\x0dcdnStreamName\x02\x00.([^\x00]+)\x00\x0ccdnStreamUrl\x02\x00.(rtmp:[^\x00]+)")
        for m in re.finditer(altPtn, amfContent):
          altName, altUrl = m.groups()
          if (altUrl == rtmpUrl and altName == streamName): continue
          streams.append({"url":altUrl, "name":altName})

        #f = open('tmp.txt', 'wb')
        #f.write(amfContent)

    return (channelId, channelTitle, streams)
 
 
def getRtmpCommand(rtmpUrl, streamName):
    result = "rtmpdump -v -r \"%s/%s\" -W \"http://www.ustream.tv/flash/viewer.swf\" --live" % (rtmpUrl, streamName)
    return result
 
 
def main(argv=None):
    # Process arguments
    if argv is None:
        argv = sys.argv[1:]
 
    usage = "Usage: ustreamRTMPDump.py "
    usage += "\ne.g. ustreamRTMPDump.py \"http://www.ustream.tv/ffrc\""

    if (len(argv) < 1):
        print usage
        return
 
    # Get RTMP information and print it
    url = argv[0]
    print "Opening url: %s\n" % url

    (channelId, channelTitle, streams) = getVideoData(url)
    print "Channel ID: %s" % channelId
    print "Channel Title: %s" % channelTitle
    for stream in streams:
      print "RTMP URL: %s\nRTMP Streamname: %s" % (stream["url"], stream["name"])
      print ""
      rtmpCmd = getRtmpCommand(streams[0]["url"], streams[0]["name"])
      print "RTMP Command: %s\n" % rtmpCmd

    # Example streams...
    # HQ: stream_live_1_1_6540154
    # 480p: stream_live_8_1_6540154
    # 360p: stream_live_4_1_6540154
    # 240p: stream_live_6_1_6540154
    # HQ: ustream-sj2_63@53274
    # 480p: ustream-sj2_677@19148
    # 360p: ustream-sj2_195@20448
    # 240p: ustream-sj2_44@7605

if __name__ == "__main__":
    main()
