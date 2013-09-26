#!/usr/bin/env python
#
#  COMP206 Chatting client.
#
# For COMP 206 be very very sure to read through all of this code!
#
# To complete (and pass) the assignment you need to modify this code
# file as well as the file called chatter.py
#

# test destination for messages
WHOTO="yucong880@gmail.com" # Jerry Wei's jabber.org account to talk to

myroster = {}  # my Buddy list
id2name = {}   # real names for buddies (if available)

# COMP 206: the chatter.py file is where most of your code should go
import chatter

import sys
import logging
import getpass
from optparse import OptionParser
import sleekxmpp
import ssl
from sleekxmpp.xmlstream import cert


# This is overkill for COMP 206, but
# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# we will set the default encoding to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input


class Talkbot206(sleekxmpp.ClientXMPP):
    
    """
        This is the chatting client for the COMP 206 assignment.
        It supports connecting to an XMPP server and interacting with it.
        """
    
    global get_buddies
    get_buddies = 0
    
    def __init__(self, jid, password, autoreply=0, buddies=0):
        # send automatic replies?
        self.autoreply=autoreply
        get_buddies = buddies
        
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        
        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)
        
        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("message", self.message)
        self.add_event_handler("changed_status", self.changed_status)
        
        # Using a Google Apps custom domain, the certificate
        # does not contain the custom domain, just the GTalk
        # server name. So we will need to process invalid
        # certifcates ourselves and check that it really
        # is from Google.
        self.add_event_handler("ssl_invalid_cert", self.invalid_cert)
    
    #self.add_event_handler("session_start", self.start, threaded=True)
    #self.add_event_handler("roster_update", self.show_roster)
    
    def show_roster(self, event):
        for jid in event:
            print "show_roster: %s(%s)" % (event[jid]['name'], jid)
    
    def changed_status(self,event):
        """ This method gets called when the status of one of our buddies changes (i.e. somebody
            goes offline or online, etc.
            We record their status in a global list called myroster.  It would be cleaner to
            use a class variable and a method for accessing it, but I thought a global would
            serve as a useful illustration.
            """
        global myroster
        # Report status changes for buddies
        # print "-   Status change from",event['from']
        # print "    type:", "status="+str(event['type']), event['status']
        
        # remember the status of each buddy
        myroster[event['from']] = str(event['type'])
        
        # add the full name, if we know it, to the status field.
        try: myroster[event['from']] = myroster[event['from']] + " " + str(id2name[event['from'].bare])
        except: pass
    # print event['name']
    
    def invalid_cert(self, pem_cert):
        """ PEM certification is used to verify the identity of a web site to avoid certain kinds of
            network hacking attacks.  This kind of network security is not required for the COMP 206 assignment, but we
            support it just in case you want to use this code in the future.  For this to work
            you may need to install extra non-standard Python modules.
            """
        print "Got invalid certificate error"
        der_cert = ssl.PEM_cert_to_DER_cert(pem_cert)
        try:
            print "Try using talk.google.com certificate"
            cert.verify('talk.google.com', der_cert)
            logging.debug("CERT: Found GTalk certificate")
        except cert.CertificateError as err:
            log.error(err.message)
            self.disconnect(send_close=False)

    def start(self, event):
        """
            Process the session_start event.
            Typical actions for the session_start event are
            requesting the roster and broadcasting an initial
            presence stanza.
            
            Re. presence, see: http://xmpp.org/rfcs/rfc3921.html#presence
            """
        global WHOTO
        
        # Announce our availability and status
        # status: away, dnd, xa, chat or available
        # Keep priority low to avoid over-riding real logins
        self.send_presence(pstatus="206bot", pshow='available', ppriority=12)
        
        # Who else can we talk to?
        # This recovers our buddy list.
        if get_buddies:
            self.get_roster()
            print "ROSTER:"
            for user in self.roster.keys():
                print "    ","Roster for",user
                print "    Keys:",self.roster[user].keys()
                print "    roster:",self.roster[user]
                global myroster
                for j in self.roster[user].keys():
                    myroster[j] = self.roster[user][j]['name']
                    id2name[j]=str(self.roster[user][j]['name'])
    #for j in self.roster[user].keys():
    #    print "    ",j,self.roster[user][j]
    #print "Sending."
    #print "Send result:",self.send_message(mto=WHOTO, mbody="I came from myself")
    
    
    def cleanmessage(self, text):
        text = text.strip()
        return text

    def message(self, msg):
        """
            Process incoming messages.
            SInce there are various kinds of "system related" messages, like errors, it is
            a good idea to check the messages's type before processing
            or sending replies.
            
            Note that message is not a string, but a dictionary-like collection.
            """
        global replied, last
        # COMP206 PEOPLE please explain with a comment here what this block
        # of code (the if statement) does, and why it might be here.
        """This if statement is to make sure that we don't spam messages unnecessarily"""
        if (not globals().has_key("replied")):
            replied=0
            last=""
        

        
        # If this is a normal message, we might want to reply
        if msg['type'] in ('chat', 'normal'):
            print "Got %s message: "%msg['type'],msg['body']
            # are we doing automated replies?
            if self.autoreply:
                if replied<30:  # only reply a few times just in case of ugly bugs
                    # count how many replies we send
                    replied=replied+1
                    # clean up the text string
                    text = self.cleanmessage( msg['body'] )
                    # prepare a reply
                    response = chatter.respond( text, sender=msg['from'] )  # too bad we don't use this response text (hint, hint [COMP206] )
                    # stock response: pretty boring, isn't it?
                    replytext = "Thanks for sending: %s... [reply #%d]" % (text[0:10],replied)
                    print "Sending reply",replytext
                    # send the reply
                    msg.reply( response ).send()
        # Error messages need to be displayed in their raw form
        elif msg['type'] in ('error'):
            print "ERROR:",msg
        else: print "UNKNOWN:",msg

# self.disconnect(wait=True)

def show_buddylist(includeUnavailable=0):
    """ Run over our copy of the roster and print the
        availability of each contect.
        """
    print "Contacts:"
    for n in range(len(myroster.keys())):
        # print each contact, possibly skipping those not available
        if includeUnavailable:
            print "%4d"%n,"%50s:   "%myroster.keys()[n], myroster[myroster.keys()[n]]
        else:
            if "available" in myroster[myroster.keys()[n]]:
                print "%4d"%n,"%50s:   "%myroster.keys()[n], myroster[myroster.keys()[n]]


if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()
    
    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)
    
    # JID and other options.
    optp.add_option("-t", "--to", dest="WHOTO",
                    help="default user to send to")
    optp.add_option("-u", "--uid", dest="jid",
                    help="JID to use (same as -j)")
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    
    opts, args = optp.parse_args()
    
    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')
    
    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")
    if opts.WHOTO is not None:
        WHOTO = opts.WHOTO

    # Setup the Talkbot206 and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = Talkbot206(opts.jid, opts.password, 1)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # If you are working with an OpenFire server, you may need
    # to adjust the SSL version used:
    # xmpp.ssl_version = ssl.PROTOCOL_SSLv3

    # If you want to verify the SSL certificates offered by a server:
    # xmpp.ca_certs = "path/to/ca/cert"

    # Connect to the XMPP server and start processing XMPP stanzas.
    if "gmail" in opts.jid.lower():
        # google addresses go to talk.google, even when that is not in the jid
        status = xmpp.connect(('talk.google.com', 5222))
    else:
        # should be possible by extracting address from JID automatically
        status = xmpp.connect()
        if not status:
            # just in case, try this...
            status = xmpp.connect(('jabber.org', 5222))
    if status:
        xmpp.process(threaded=True) # block=True)
        #xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")


import threading
import time
time.sleep(5)

print "-"*60
print " - This is the COMP206 talk206 chat client (part of Talk2013)."
print " - The flags '-j' and '-p' can be used to provide the ID and password to avoid retyping them."
print " - The flag '-q' can suppress the annoying INFO and diagnostic messages."
print " - Use the '-h' for tips on startup arguments."
print " - This program is for Assignment 5 and was submitted by YOURNAME YOURSTUDENTID."
print "-"*60


show_buddylist()
print

while 1:
    sys.stdout.write("TO %s> "%WHOTO)
    try:
        s = sys.stdin.readline().strip()
    except KeyboardInterrupt:
        print "\nControl-C: exit.\n"
        xmpp.disconnect(wait=True)
        break

    justanumber=0
    # A string composed only of a number is considered to be the ID of a new person
    # to chat with
    if len(s.split())==1:
        try:
            # get the number
            v = int(s)
            justanumber=1
        except: justanumber=0
        if justanumber:
            WHOTO = myroster.keys()[v]
            continue
    # an empty string means print the numbered buddy list
    if len(s)<1:
        show_buddylist()
        print
    else:
        xmpp.send_message(mto=WHOTO, mbody=s)
    time.sleep(1)
