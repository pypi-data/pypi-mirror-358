#!/usr/bin/env python
'''
the Door which communicates to tngGui via a queue
the Door is the sender using sendHshQueue()
be sure to 'senv JsonRecorder True' 
'''
import time, sys, os
import HasyUtils

try:
    import sardana.taurus.core.tango.sardana.macroserver as sms
except Exception as e:
    print( "tngGuiDoor.py: failed to import macroserver.py")
    print( "  reason: %s" % repr( e))
    print( "  exiting")
    sys.exit(255) 
import builtins

sms.registerExtensions()

#
# this global variable is supposed to store 'self' of the tngGuiDoor instance
# to be called, e.g. from SardanaMonitor to send some data
#
mainWidget = None

class tngGuiDoor( sms.BaseDoor):

    def __init__( self, name, **kw):
        global mainWidget

        mainWidget = self

        self.blocked = True

        self.queue = builtins.__dict__[ 'queue']
        
        #
        # Mind: sometimes we loose records
        #
        self.call__init__( sms.BaseDoor, name, **kw)
        
    #
    # /usr/lib/python2.7/dist-packages/sardana/taurus/core/tango/sardana/macroserver.py
    #
    def logReceived(self, log_name, output):

        if not output:
            return
        #
        # want to get rid of the 'old' door outpu
        #
        if self.blocked:
            return 

        for line in output:
            #print( "tngGuiDoor: %s" % line)

            #
            # [START] runMacro Macro 'lsenv(Scan*) -> 2811fd9e-6bb8-11eb-bd50-4c526200d21f'
            #
            #if line.find( '[START]') != -1:
            #    i = line.find( "'") + 1
            #    j = line.find( "->") - 1
            #    line = line[i:j]
            #
            # [ END ] runMacro Macro 'lsenv(Scan*) -> 2811fd9e-6bb8-11eb-bd50-4c526200d21f'
            #
            if line.find( '[ END ]') != -1:
                continue
            #
            # Job ended (stopped=False, aborted=False)
            #
            #if line.find( 'Job ended') != -1:
            #    continue
            if len( line.strip()) == 0: 
                continue
            self.sendHshQueue( { 'line': line})

        return 


    def sendHshQueue( self, hsh): 
        '''
        sends a dictionary to the tngGui via queue(): 
        handled by: 
          $HOME/gitlabDESY/tnggui/tngGui/tngGuiClass.py
            cb_refreshMain( )
        '''
        try:
            self.queue.put( hsh)
        except Exception as e:
            print( "tngGuiDoor.sendHshQueue")
            print( "hsh %s" % repr( hsh))
            print( "exception %s" % repr( e))
            raise ValueError( "tngGuiDoor.sendHshQueue: something went wrong")

        return 

# 
import taurus
factory = taurus.Factory()
factory.registerDeviceClass( 'Door',  tngGuiDoor)
#
# returns a tngGuiDoor         
#

