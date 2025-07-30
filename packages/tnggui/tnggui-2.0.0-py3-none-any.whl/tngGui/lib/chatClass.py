#!/usr/bin/env python
'''
chatClass exchanges text strings between several chat partners
'''
import sys
from PySpectra.pyqtSelector import *

import zmq, json, socket, time

NEWS = "\nUse 'alias <name>' to set an alias, 'alias' to unset\n "

TIMEOUT_ZMQ = 200
#
# Master: 7800 - ... for input 
#         7850 - ... for output
# Client: 7801 + i for input 
#           7800 remains free for findClientNumber() 
#         7851 + i for output
# 
CLIENTS_MAX = 20
PORT_IN_BASE = 7800
PORT_OUT_BASE = 7850
DEBUG = False

def getTime():
    '''
    return: '10:56:57'
    '''
    return time.strftime("%H:%M:%S", time.localtime())
    
class Chat( QMainWindow):
    def __init__( self, logWidget = None, parent = None, app = None):
        super( Chat, self).__init__( parent)

        self.app = app
        self.name = "SardanaChat"
        self.setWindowTitle( "SardanaChat")
        self.prepareWidgets()
        #
        # Menu Bar
        #
        self.menuBar = QMenuBar()
        self.setMenuBar( self.menuBar)
        self.prepareMenuBar()
        #
        # Status bar
        #
        self.prepareStatusBar()
        #
        # if there is a master already running, find the clientNo.
        #
        if self.isMasterAlive():
            self.flagMaster = False
            self.clientNo = self.findClientNumber()
            self.portInClient = PORT_OUT_BASE + self.clientNo
            self.portOutClient = PORT_IN_BASE + self.clientNo
            self.openSocketsClient()
            self.timerZMQ = QtCore.QTimer( self)
            self.timerZMQ.timeout.connect( self.cb_timerZMQClient)
            self.timerZMQ.start( TIMEOUT_ZMQ)
            self.setWindowTitle( "SardanaChat, Client %d" % self.clientNo)
            self.chatWidget.append( "%s: I am client no. %d, Out %d, In %d" % 
                                    ( getTime(), self.clientNo, self.portOutClient, self.portInClient))
            self.chatWidget.append( "%s" % NEWS)
        #
        # we are the master
        #
        else: 
            self.flagMaster = True
            self.clientNo = 0
            self.nClients = 0
            self.openSocketsMaster()
            self.timerZMQ = QtCore.QTimer( self)
            self.timerZMQ.timeout.connect( self.cb_timerZMQMaster)
            self.timerZMQ.start( TIMEOUT_ZMQ)
            self.setWindowTitle( "SardanaChat, Master")
            self.chatWidget.append( "%s: I am the chat master, preparing for %d connects" % 
                                    (getTime(), CLIENTS_MAX))
            self.chatWidget.append( "%s" % NEWS)

        self.alias = None
        return 

    def isMasterAlive( self): 
        #
        # see whether the master is already running use PORT_IN_BASE
        # for a test. That is why this port is not used for other
        # purposes
        #
        hsh = { "isAlive": True} 
        node = None
        if node is None:
            node = socket.gethostbyname( socket.getfqdn())

        context = zmq.Context()
        sckt = context.socket(zmq.REQ)
        #
        # prevent context.term() from hanging, if the message
        # is not consumed by a receiver.
        #
        sckt.setsockopt(zmq.LINGER, 1)
        port = PORT_IN_BASE
        try:
            sckt.connect('tcp://%s:%s' % (node, port))
        except Exception as e:
            sckt.close()
            return False

        hshEnc = json.dumps( hsh)
        try:
            res = sckt.send( bytearray( hshEnc, encoding="utf-8"))
        except Exception as e:
            sckt.close()
            print( "isAlive: failed %s" % repr( e))
            return { 'result': "chatClass.isAlive: exception by send() %s" % repr(e)}

        #
        # wait some time for the answer
        #
        lst = zmq.select([ sckt], [], [], TIMEOUT_ZMQ*0.002)
        if sckt in lst[0]:
            hshEnc = sckt.recv() 
            res = json.loads( hshEnc)
        else: 
            res = { 'result': 'notAlive'}

        sckt.close()
        context.term()

        if res[ 'result'] == 'notAlive': 
            argout = False
        else:
            argout = True
        return argout

    def openSocketsMaster( self): 
        #
        # open some sockets to prepare for connects
        #
        node = socket.gethostbyname( socket.getfqdn())
        #
        # the ports are selected
        #
        self.context = zmq.Context()
        self.scktInMaster = []
        self.scktOutMaster = []
        self.portInMaster = []
        self.portOutMaster = []
        for i in range( CLIENTS_MAX + 1): # '+ 1' to keep 7800 free for findClientNumber() 
            scktIn = self.context.socket(zmq.REP)
            self.scktInMaster.append( scktIn) 
            #
            # don't use localhost. it is a different interface
            #
            try:
                portIn = (PORT_IN_BASE + i)
                self.portInMaster.append( portIn)
                scktIn.bind( "tcp://%s:%d" % ( node, portIn))
                if DEBUG:
                    print( "openSocketsMaster: opened %d for input" % (portIn))
            except Exception as e:
                print( "\nopenSocketsMaster-1: %s" % repr( e))
                sys.exit( 255)

            scktOut = self.context.socket(zmq.REQ)
            #
            # prevent context.term() from hanging, if the message
            # is not consumed by a receiver.
            #
            scktOut.setsockopt(zmq.LINGER, 1)
            try:
                portOut = (PORT_OUT_BASE + i)
                self.portOutMaster.append( portOut)
                scktOut.connect('tcp://%s:%d' % (node, portOut))
                if DEBUG:
                    print( "openSocketsMaster: opened %d for output" % (portOut))
                self.scktOutMaster.append( scktOut)
            except Exception as e:
                scktOut.close()
                print( "openSocketsMaster2: failed %s" % repr( e))
                return
        return 

    def openSocketsClient( self): 
        #
        # the client connects to the master
        #
        node = socket.gethostbyname( socket.getfqdn())
        self.context = zmq.Context()
        self.scktIn = self.context.socket(zmq.REP)
        #
        # don't use localhost. it is a different interface
        #
        try:
            self.scktIn.bind( "tcp://%s:%d" % ( node, self.portInClient))
            if DEBUG:
                print( "openSocketsMaster: opened %d for input" % (self.portInClient))
        except Exception as e:
                print( "\nopenSocketsClient: %s" % repr( e))
                sys.exit( 255)

        self.scktOut = self.context.socket(zmq.REQ)
        #
        # prevent context.term() from hanging, if the message
        # is not consumed by a receiver.
        #
        self.scktOut.setsockopt(zmq.LINGER, 1)
        try:
            self.scktOut.connect('tcp://%s:%d' % (node, self.portOutClient))
            if DEBUG:
                print( "openSocketsClient: opened %d for output" % (self.portOutClient))
        except Exception as e:
            self.scktOut.close()
            print( "openSocketsClient: failed %s" % repr( e))
            return
        return 

    def findClientNumber( self): 
        #
        # we know we are a client, ask the master which client number, starts with 1
        #
        if DEBUG: 
            print( "findClientNumber") 

        hsh = { "RequestClientNo": True} 
        node = None
        if node is None:
            node = socket.gethostbyname( socket.getfqdn())

        context = zmq.Context()
        sckt = context.socket(zmq.REQ)
        #
        # prevent context.term() from hanging, if the message
        # is not consumed by a receiver.
        #
        sckt.setsockopt(zmq.LINGER, 1)
        port = PORT_IN_BASE
        try:
            sckt.connect('tcp://%s:%s' % (node, port))
        except Exception as e:
            sckt.close()
            print( "findClientNumber: failed %s" % repr( e))
            return False

        hshEnc = json.dumps( hsh)
        try:
            res = sckt.send( bytearray( hshEnc, encoding="utf-8"))
        except Exception as e:
            sckt.close()
            print( "findClientNumber: failed %s" % repr( e))
            return { 'result': "chatClass.findClientNumber: exception by send() %s" % repr(e)}

        #
        # wait some time for the answer
        #
        lst = zmq.select([ sckt], [], [], TIMEOUT_ZMQ*0.002)
        if sckt in lst[0]:
            hshEnc = sckt.recv() 
            res = json.loads( hshEnc)
            if 'SendClientNo' in res: 
                if res[ 'SendClientNo'] == -1: 
                    print( "findClientNumber: too many connects, consider to re-start the Master")
                    sys.exit( 255)
                self.clientNo = res[ 'SendClientNo']
            else: 
                print( "findClientNumber: expected 'SendClientNo'") 
                sys.exit( 255)
        else: 
            print( "findClientNumber: no answer") 
            sys.exit( 255)

        sckt.close()
        context.term()

        if DEBUG: 
            print( "findClientNumber DONE %d" % self.clientNo) 

        return self.clientNo
        
    def cb_timerZMQMaster( self):
        """
        checks whether we have a request from the clients
        """
        argout = {}

        lst = zmq.select( self.scktInMaster, [], [], 0.01)
        if len( lst[0]) == 0: 
            return 
        self.timerZMQ.stop()
        try: 
            for scktIn in lst[0]:
                for iIn in range( CLIENTS_MAX):
                    if scktIn == self.scktInMaster[iIn]:
                        break
                hshEncIn = scktIn.recv()
                hshIn = json.loads( hshEncIn)
                if DEBUG: 
                    print( "cb_timerZMQMaster, received %s from %d" % (repr( hshIn), self.portInMaster[iIn]))
                argout = self.executeCommand( hshIn)
                hshEncOut = json.dumps( argout)
                if DEBUG: 
                    print( "cb_timerZMQMaster, sending response %s" % repr( argout))
                scktIn.send( bytearray( hshEncOut, encoding="utf-8"))
        except Exception as e: 
            print( "cb_timerZMQMaster: error %s" % repr( e))
        #
        # we distribute the line to all clients. this has to be done
        # after recv/send has been finished
        #
        if 'line' in hshIn: 
            if DEBUG: 
                print( "cb_timerZMQMaster: distributing %s" % repr( hshIn))
            self.writeRead( hshIn)
            
        self.timerZMQ.start( TIMEOUT_ZMQ)
        return 
        
    def cb_timerZMQClient( self):
        """
        checks whether there is a request on the ZMQ socket, 
        """
        argout = {}

        lst = zmq.select( [self.scktIn], [], [], 0.01)
        if len( lst[0]) == 0: 
            return 

        self.timerZMQ.stop()

        try: 
            if self.scktIn in lst[0]:
                msg = self.scktIn.recv()
                hsh = json.loads( msg)
                if DEBUG:
                    print( "cb_timerZMQClient, received %s" % repr( hsh))

                if 'line' not in hsh: 
                    argout = self.executeCommand( hsh)
                    msg = json.dumps( argout)
                    if DEBUG: 
                        print( "cb_timerZMQClient, sending response %s" % repr( argout))
                    self.scktIn.send( bytearray( msg, encoding="utf-8"))
                else: 
                    argout = { 'result': 'ok'}
                    msg = json.dumps( argout)
                    if DEBUG:
                        print( "cb_timerZMQClient, sending response %s" % repr( argout))
                    self.scktIn.send( bytearray( msg, encoding="utf-8"))
                    argout = self.executeCommand( hsh)

        except Exception as e: 
            print( "cb_timerZMQClient: error %s" % repr( e))

        self.timerZMQ.start( TIMEOUT_ZMQ)
        return 

    def executeCommand( self, hsh): 
        '''
        receives a command from the other side, executes it 
        and returns an answer
        '''
        if DEBUG:
            print( "executeCommand: %s" % repr( hsh))

        argout = True

        if 'isAlive' in hsh: 
            argout = { 'result': 'yes'}
            return argout

        elif 'ClientClosed' in hsh: 
            argout = { 'result': 'ok'}
            clientNo = hsh[ 'ClientClosed']
            self.chatWidget.append( "%s Client %d disconnected (%d, %d) " % (getTime(), clientNo,
                                                                     self.portInMaster[ clientNo], 
                                                                     self.portOutMaster[ clientNo]))
            self.scktOutMaster[ clientNo] = -1
            self.scktInMaster[ clientNo] = -1
            return argout

        elif 'line' in hsh: 
            if 'ClientNo' in hsh: 
                #
                # if the message comes from this process, mark it wit '>>>'
                #
                if self.clientNo == hsh[ 'ClientNo']: 
                    if self.alias is not None: 
                        self.chatWidget.append( "%s %s: %s" % ( getTime(), self.alias, hsh[ 'line']))
                    else: 
                        self.chatWidget.append( "%s <myself>: %s" % ( getTime(), hsh[ 'line']))
                else: 
                    if hsh[ 'Alias'] is not None: 
                        self.chatWidget.append( "%s %s: %s" % ( getTime(), hsh[ 'Alias'], hsh[ 'line']))
                    else: 
                        self.chatWidget.append( "%s (%d): %s" % ( getTime(), hsh[ 'ClientNo'], hsh[ 'line']))
            else: 
                self.chatWidget.append( "%s: %s" % (getTime(), hsh[ 'line']))

            argout = { 'result': 'ok'}

        elif 'RequestClientNo' in hsh:
            #
            # += 1 because the base port number has to be free for connect requests
            #
            self.nClients += 1
            if DEBUG:
                print( "executeCommand: RequestClientNo %d MAX %d " % ( self.nClients, CLIENTS_MAX))
            if self.nClients > CLIENTS_MAX: 
                self.nClients -= 1
                argout = { 'SendClientNo': -1}
                self.chatWidget.append( "%s: Too many connects, consider to re-start the master" % getTime())
            else:
                argout = { 'SendClientNo': self.nClients}
                self.chatWidget.append( "%s: Connected: %d/%d, ports %d/%d " % 
                                        (getTime(), 
                                         self.nClients, CLIENTS_MAX, self.portInMaster[ self.nClients], 
                                         self.portOutMaster[ self.nClients]))

        elif 'MasterClosed' in hsh:
            print( "chatClass.executeCommand: received MasterClosed message, exit")
            print( "chatClass.executeCommand: reason: %s" % hsh[ 'MasterClosed'])
            sys.exit( 255)

        else: 
            print( "ExecuteCommand: failed to identity %s" % repr( hsh))
            
        return argout

    def writeRead( self, hsh):
        """
        execute writeRead for all clients
        """
        if 'line' in hsh: 
            hsh[ 'line'] = "%s" % ( hsh[ 'line'])

        hshEnc = json.dumps( hsh)
        argout = { 'result': "None"}

        if self.flagMaster: 
            for i in range( 1, self.nClients + 1):
                if self.scktOutMaster[ i] == -1: 
                    if DEBUG:
                        print( "writeRead-master: NOT sending %s to %d" % (hsh, self.portOutMaster[i]))
                    continue
                if DEBUG:
                    print( "writeRead-master: sending %s to %d" % (hsh, self.portOutMaster[i]))
                try:
                    res = self.scktOutMaster[i].send( bytearray( hshEnc, encoding="utf-8"))
                except Exception as e:
                    self.scktOutMaster[i].close()
                    self.scktOutMaster[i] = -1
                    print( "writeRead-master: failed %s" % repr( e))
                    return { 'result': "writeRead-master: exception by send() %s" % repr(e)}
                #
                # don't expect any answer to the MasterClosed message
                #
                if 'MasterClosed' in hsh:
                    continue

                if 'isAlive' in hsh:
                    lst = zmq.select([ self.scktOutMaster[i]], [], [], TIMEOUT_ZMQ*0.002)
                    if self.scktOutMaster[i] in lst[0]:
                        hshEnc = self.scktOutMaster[i].recv() 
                        argout = json.loads( hshEnc)
                        if DEBUG:
                            print( "writeRead-master: response %s" % repr( argout) ) 
                    else: 
                        self.scktOutMaster[i].close()
                        self.scktOutMaster[i] = None
                        self.context.term()
                        argout = { 'result': 'notAlive'}
                        if DEBUG:
                            print( "writeRead-master: response %s" % repr( argout) ) 

                        return argout

                lst = zmq.select([ self.scktOutMaster[i]], [], [],  TIMEOUT_ZMQ*0.002)
                if self.scktOutMaster[i] in lst[0]:
                    hshRet = self.scktOutMaster[i].recv() 
                    argout = json.loads( hshRet) 
                    if DEBUG:
                        print( "writeRead-master: response from %d: %s" % ( self.portOutMaster[i], repr( argout) ) )

                else: 
                    print( "writeRead-master: the counterpart is gone, exit")
                    sys.exit( 255)
        else: 
            if DEBUG:
                print( "writeRead-client: sending %s to %d" % (hsh, self.portOutClient))
            try:
                res = self.scktOut.send( bytearray( hshEnc, encoding="utf-8"))
            except Exception as e:
                self.scktOut.close()
                self.scktOut = None
                print( "writeRead: failed %s" % repr( e))
                return { 'result': "writeRead: exception by send() %s" % repr(e)}

            if 'isAlive' in hsh:
                lst = zmq.select([ self.scktOut], [], [], TIMEOUT_ZMQ*0.002)
                if self.scktOut in lst[0]:
                    hshEnc = self.scktOut.recv() 
                    argout = json.loads( hshEnc)
                    if DEBUG:
                        print( "writeRead: response %s" % repr( argout) ) 
                else: 
                    self.scktOut.close()
                    self.scktOut = None
                    self.context.term()
                    argout = { 'result': 'notAlive'}
                    if DEBUG: 
                        print( "writeRead: response %s" % repr( argout) ) 

                    return argout

            lst = zmq.select([ self.scktOut], [], [],  TIMEOUT_ZMQ*0.002)
            if self.scktOut in lst[0]:
                hshEnc = self.scktOut.recv() 
                argout = json.loads( hshEnc) 

            else: 
                print( "writeRead: the counterpart is gone, exit")
                sys.exit( 255)

        if DEBUG:
            print( "writeRead: response %s" % ( repr( argout)))
        
        return argout
    
    
    def prepareMenuBar( self):

        self.fileMenu = self.menuBar.addMenu('&File')
        self.exitAction = QAction('E&xit', self)        
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect( self.cb_closeChat)
        self.fileMenu.addAction( self.exitAction)

        #
        # the activity menubar: help and activity
        #
        self.menuBarActivity = QMenuBar( self.menuBar)
        self.menuBar.setCornerWidget( self.menuBarActivity, QtCore.Qt.TopRightCorner)
        
        #
        # Help menu (bottom part)
        #
        self.helpMenu = self.menuBarActivity.addMenu('Help')
        self.widgetAction = self.helpMenu.addAction(self.tr("Widget"))
        self.widgetAction.triggered.connect( self.cb_helpWidget)


    def cb_helpWidget(self):
        w = HelpBox(self, self.tr("HelpWidget"), self.tr(
            "\
<p><b>Chat</b><br>\
<p>Exchange messages between several partners. The first to \
start the application is the master. \
\
<p>The master prepares %d ports for connections. A re-connecting clients eats-up an additional port.\
\
            <p>If the master terminates, the clients terminate as well. \
\
<p>Lines are preceeded by the number of the sender, 0 is the master. \
\
            <p>Use 'alias someName' to set an alias, 'alias' to unset. \
\
" % CLIENTS_MAX
                ))
        w.show()

    def prepareStatusBar( self):
        #
        # Status Bar
        #
        self.statusBar = QStatusBar()
        self.setStatusBar( self.statusBar)

        #
        # clear
        #
        self.clear = QPushButton(self.tr("&Clear")) 
        self.statusBar.addPermanentWidget( self.clear) # 'permanent' to shift it right
        self.clear.setToolTip( "Clear the log widget")
        self.clear.clicked.connect( self.cb_clear)
        self.clear.setShortcut( "Alt+c")
        #
        # exit
        #        
        self.exit = QPushButton(self.tr("E&xit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( self.cb_closeChat )
        self.exit.setShortcut( "Alt+x")

    def prepareWidgets( self):
        w = QWidget()
        self.layout_v = QVBoxLayout()
        w.setLayout( self.layout_v)
        self.setCentralWidget( w)
        self.dct = {}
        #
        # chat widget
        #
        hBox = QHBoxLayout()
        self.chatWidget = QTextEdit()
        f = QFont( 'Monospace')
        f.setPixelSize( 12)
        self.chatWidget.setFont( f)
        self.chatWidget.setMinimumWidth( 500)
        self.chatWidget.setMinimumHeight( 200)
        self.chatWidget.setReadOnly( True)
        hBox.addWidget( self.chatWidget)
        self.layout_v.addLayout( hBox)
        
        #
        # the input line
        #
        hBox = QHBoxLayout()
        self.w_line = QLineEdit()
        self.w_line.setAlignment( QtCore.Qt.AlignRight)
        self.w_line.setMinimumWidth( 300)
        hBox.addWidget( self.w_line)
        self.layout_v.addLayout( hBox)
        
        return 

    def keyPressEvent( self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            self.cb_pressedEnter()
        else:
            super( Chat, self).keyPressEvent(event)
        return 

    def cb_pressedEnter( self):

        #
        # alias <name> 
        #
        temp = str( self.w_line.text())
        if temp.find( 'alias') != -1: 
            lst = temp.split( ' ')
            if len( lst) == 2: 
                self.alias = lst[ 1]
                self.chatWidget.append( "%s: alias %s" % ( getTime(), self.alias))
                self.setWindowTitle( "SardanaChat, %s" % self.alias)
            elif len( lst) == 1:
                self.alias = None
                self.chatWidget.append( "%s: alias" % ( getTime()))
                self.setWindowTitle( "SardanaChat")
            elif len( lst) > 0:  
                self.alias = ' '.join( lst[1:])
                self.chatWidget.append( "%s: alias %s" % ( getTime(), self.alias))
                self.setWindowTitle( "SardanaChat, %s" % self.alias)
            self.w_line.clear()
            return 

        if self.flagMaster: 
            if self.alias is not None: 
                self.chatWidget.append( "%s %s: %s" % (getTime(), self.alias, temp))
            else: 
                self.chatWidget.append( "%s <myself>: %s" % (getTime(), temp))
               
        self.writeRead( { 'line': temp,
                          'ClientNo': self.clientNo,
                          'Alias': self.alias})
        self.w_line.clear()
        return 

    def cb_clear( self):
        self.chatWidget.clear()
        return

    def closeEvent( self, e):
        if not self.flagMaster: 
            self.writeRead( { 'ClientClosed': self.clientNo})
        else: 
            self.writeRead( { 'MasterClosed': 'from closeEvent'})
        self.cb_closeChat()

    def cb_closeChat( self): 
        self.close()

class HelpBox( QMainWindow):
    #
    # class to display some help text.
    # Avoid QMessageBox() because this cannot be moved
    #
    def __init__( self, parent, title = "Title", text = None):
        super( HelpBox, self).__init__( parent)
        self.setWindowTitle( title)
        w = QWidget()
        if len( text) > 1000:
            w.setMinimumWidth( 800)
            w.setMinimumHeight( 800)
        else:
            w.setMinimumWidth( 600)
            w.setMinimumHeight( 400)
        self.setCentralWidget( w)
        self.layout_v = QVBoxLayout()
        self.textBox = QTextEdit( self)
        self.textBox.insertHtml( text)
        self.textBox.setReadOnly( True)
        self.layout_v.addWidget( self.textBox)
        w.setLayout( self.layout_v)
        #
        # Status Bar
        #
        self.statusBar = QStatusBar()
        self.setStatusBar( self.statusBar)

        self.exit = QPushButton(self.tr("&Exit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( self.close)
        self.exit.setShortcut( "Alt+x")
