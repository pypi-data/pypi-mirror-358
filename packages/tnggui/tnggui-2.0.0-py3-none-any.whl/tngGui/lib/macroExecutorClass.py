#!/usr/bin/env python

from PySpectra.pyqtSelector import *
import PyTango
import HasyUtils
import tngGui.lib.utils as utils
import tngGui.lib.definitions as definitions
import tngGui.lib.helpBox as helpBox
import tngGui.lib.macroServerIfc as macroServerIfc
# gives an import conflict
#import tngGui.lib.mcaWidget as mcaWidget
import queue, os
import builtins
import zmq, json, socket
# needed, because of
#   door = taurus.Device( HasyUtils.getLocalDoorNames()[0])
# otherwise no data records are received
#
import taurus

HISTORY_MAX = 50
TIMEOUT_ZMQ = 500

class MacroExecutor( QMainWindow):
    def __init__( self, logWidget = None, parent = None, app = None):
        super( MacroExecutor, self).__init__( parent)
        self.parent = parent
        #
        # typically w 1920, h 1200 
        # laptop    w 1184 h 528
        #
        screen_resolution = app.desktop().screenGeometry()
        self.width, self.height = screen_resolution.width(), screen_resolution.height()
        #
        # a queue to receive messages from the door
        # 
        self.queue = queue.Queue()
        builtins.__dict__[ 'queue'] = self.queue
        #
        # create the door
        #
        import tngGui.tngGuiDoor
        #
        # need to create the taurus door. otherwise the
        # door-magic is not working
        #
        try:
            door = taurus.Device( HasyUtils.getLocalDoorNames()[0])
        except Exception as e:
            print( "tngGui.main: trouble Connecting to door %s" % repr( HasyUtils.getLocalDoorNames()[0]))
            print( repr( e))
            sys.exit(255)
        #
        # bad hack to avoid that the old door-output is 
        # received. 
        #
        tngGui.tngGuiDoor.mainWidget.blocked = False

        try: 
            self.doorProxy = PyTango.DeviceProxy( HasyUtils.getLocalDoorNames()[0])
        except Exception as e: 
            raise ValueError( "TngGuiClass.__init__: failed to create door proxy, %s" % repr( e))

        self.app = app
        self.name = "MacroExecutor"
        self.tkFlag = False
        self.setWindowTitle( "Macro Executor")
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

        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.timeout.connect( self.cb_refreshMacroExecutor)
        self.updateTimer.start( definitions.TIMEOUT_REFRESH)

        self.commandComboBox.setFocus()

        self.setupZMQ()

        return 


    def setupZMQ( self): 
        #
        self.context = zmq.Context()
        self.sckt = self.context.socket(zmq.REP)
        #
        # don't use localhost. it is a different interface
        #
        try:
            # port 7790 is mentioned also in $HOME/gitlabDESY/hasyutils/HasyUtils/TgUtils.py toMacroExecutor()
            self.sckt.bind( "tcp://%s:7790" % socket.gethostbyname( socket.getfqdn()))
            self.timerZMQ = QtCore.QTimer( self)
            self.timerZMQ.timeout.connect( self.cb_timerZMQ)
            self.timerZMQ.start( TIMEOUT_ZMQ)
        except Exception as e:
            #
            # we fall into this exception, if there is already another 
            # running. Where should the toPyspMonitor() send the data? For the
            # time being the first pyspMonitor will deal with this
            #
            print( "\nmacroExecutorClass.setupZMQ(): %s" % repr( e))
            print( "  assuming that another macroExecutor process is already")
            print( "  listening to the ZMQ socket taking care of the input")
            print( "  from TgUtils.toMacroExector()\n")

        return 

    def cb_timerZMQ( self):
        """
        checks whether there is a request on the ZMQ socket
        """
        lst = zmq.select([self.sckt], [], [], 0.01)
        if len( lst[0]) == 0: 
            return 
        self.timerZMQ.stop()
        argout = {}
        #
        # if we received some input, we do another select to see, if 
        # more input is arriving. this way the MacroExecutor appears  
        # to be very responsive
        #
        while self.sckt in lst[0]:
            msg = self.sckt.recv()
            hsh = json.loads( msg)
            argout = self.executeZmqCommand( hsh)
            msg = json.dumps( argout)
            self.sckt.send( bytearray( msg, encoding="utf-8"))
            lst = zmq.select([self.sckt], [], [], 0.1)
        #
        # mandelbrot 20x20: if we change 10 to 1, time from 15s to 10s
        #
        self.timerZMQ.start( TIMEOUT_ZMQ)
        return 

    def prepareMenuBar( self):

        self.fileMenu = self.menuBar.addMenu('&File')
        self.exitAction = QAction('E&xit', self)        
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect( self.cb_closeMacroExecutor)
        self.fileMenu.addAction( self.exitAction)

        #
        # Tools menu
        #
        self.toolsMenu = self.menuBar.addMenu('&Tools')

        #self.nxselectorAction = QAction('Nxselector', self)        
        #self.nxselectorAction.triggered.connect( self.cb_launchNxselector)
        #self.toolsMenu.addAction( self.nxselectorAction)

        #
        # sardanaMonitor
        #
        self.sardanaMonitorAction = QAction('SardanaMonitor', self)        
        self.sardanaMonitorAction.triggered.connect( self.cb_launchSardanaMonitor)
        self.sardanaMonitorAction.setStatusTip('Monitor 0D and 1D data, consider to use pyspMonitor')
        self.toolsMenu.addAction( self.sardanaMonitorAction)
        #
        # lavue
        #
        self.lavueAction = QAction('lavue', self)        
        self.lavueAction.triggered.connect( self.cb_launchLavue)
        self.toolsMenu.addAction( self.lavueAction)
        #
        # chat
        #
        self.chatAction = QAction('SardanaChat', self)        
        self.chatAction.triggered.connect( self.cb_launchChat)
        self.chatAction.setStatusTip('Start a chat. All partners have to be on the same host')
        self.toolsMenu.addAction( self.chatAction)
        #
        # pymca
        #
        self.pymcaAction = QAction('pymca', self)        
        self.pymcaAction.triggered.connect( self.cb_launchPymca)
        self.pymcaAction.setStatusTip('PyMca, the ESRF X-ray Fluorescence Toolkit')
        self.toolsMenu.addAction( self.pymcaAction)
        #
        # pyspMonitor
        #
        self.pyspMonitorAction = QAction('pyspMonitor', self)        
        self.pyspMonitorAction.triggered.connect( self.cb_launchPyspMonitor)
        self.pyspMonitorAction.setStatusTip('Monitor 0D and 1D data.')
        self.toolsMenu.addAction( self.pyspMonitorAction)
        #
        # motor monitor
        #
        self.motorMonitorAction = QAction('SardanaMotorMonitor', self)        
        self.motorMonitorAction.triggered.connect( self.cb_launchMotorMonitor)
        self.toolsMenu.addAction( self.motorMonitorAction)
        #
        # MacroServer, selected features
        #
        self.macroServerAction = QAction('MacroServer (Selected Features)', self)        
        self.macroServerAction.setStatusTip('Selected MacroServer features')
        self.macroServerAction.triggered.connect( self.cb_msIfc)
        self.toolsMenu.addAction( self.macroServerAction)
        #
        # edit run_seq
        #
        temp = HasyUtils.getEnv( "SequencyPath")
        if temp is None: 
            home = os.getenv( "HOME")
            HasyUtils.setEnv( "SequencyPath", temp)

        self.editRunSeqAction = QAction('Edit %s/run_seq.lis' % temp, self)        
        self.editRunSeqAction.setStatusTip( "Edit %s/run_seq.lis'" % temp)
        self.editRunSeqAction.triggered.connect( self.cb_editRunSeq)
        self.toolsMenu.addAction( self.editRunSeqAction)
        #
        # gives an import conflict
        #self.mcaAction = QAction('MCA', self)        
        #self.mcaAction.triggered.connect( self.cb_launchMCA)
        #self.toolsMenu.addAction( self.mcaAction)

        #
        # Misc
        #
        self.miscMenu = self.menuBar.addMenu('Misc')
        #
        # restart timer
        #
        self.restartTimerAction = QAction('Restart refresh timer', self)        
        self.restartTimerAction.setStatusTip('Restart the timer that refreshes this widget')
        self.restartTimerAction.triggered.connect( self.cb_restartTimer)
        self.miscMenu.addAction( self.restartTimerAction)

        #
        # stop timer
        #
        self.stopTimerAction = QAction('Stop refresh timer', self)        
        self.stopTimerAction.setStatusTip('Stop the timer that refreshes this widget')
        self.stopTimerAction.triggered.connect( self.cb_stopTimer)
        self.miscMenu.addAction( self.stopTimerAction)

        #
        # write log widget to file and edit it
        #
        self.logToTempFileAction = QAction('Write log widget to file and edit it.', self)
        self.logToTempFileAction.triggered.connect( self.cb_logToTempFile)
        self.miscMenu.addAction( self.logToTempFileAction)

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

        self.comAction = self.helpMenu.addAction(self.tr("Commands"))
        self.comAction.triggered.connect( self.cb_helpCom)

        self.toolsAction = self.helpMenu.addAction(self.tr("Tools"))
        self.toolsAction.triggered.connect( self.cb_helpTools)

        self.tkAction = QAction('TK', self, checkable = True)        
        self.tkAction.setStatusTip('If TK, emacs is the editor)')
        self.tkAction.triggered.connect( self.cb_tk)
        self.helpMenu.addAction( self.tkAction)
        
        self.activityIndex = 0
        self.activity = self.menuBarActivity.addMenu( "_")

    def cb_helpWidget(self):
        w = helpBox.HelpBox(self, self.tr("HelpWidget"), self.tr(
            "\
<p><b>ActiveMntGrp</b><br>\
Stores the devices used for scans.\
\
<p><b>ScanDir</b><br>\
Where the files are stored.\
\
<p><b>ScanFile</b><br>\
Use [\"tst.fio\"] to create .fio files or [\"tst.fio\", \"tst.spe\"] \
to to create .fio and spec files.<br>\
<br>\
LIkewise you can supply the following string to 'Command:' <br>\
senv ScanFile \"['tst.fio', 'tst.spe']\" \
\
<p><b>Commands</b><br>\
Commands are executed by Alt-e or by pressing ENTER (if the focus is on the command widget).<br>\
The command history is stored in the MacroServer environment variable MacroExecutorHistory. \
\
<p><b>Command</b><br>\
A ComboBox containing the recently executed Macros. The entries can \
be edited and executed by ENTER, if the focus in on the \
comboBox or by hitting Exec or Ctrl-e.\
\
<p><b>Abort Macro</b><br>\
Sends an AbortMacro command to the active Door.\
\
<p><b>Stop Macro</b><br>\
Sends a StopMacro command to the active Door.\
\
<p><b>Apply</b><br>\
Fetches the input for ScanDir, ScanFile\
and executes it.\
\
<p><b>pyspMonitor</b><br>\
pyspMonitor.py view 0D and 1D data during scans.\
\
"
                ))
        w.show()

    def cb_helpCom(self):
        w = helpBox.HelpBox(self, self.tr("HelpCommands"), self.tr(
            "\
<p><b>Frequently used commands</b>\
<ul> \
<li> ct <br> \
     a single measurement of the detectors, no motor movements. \
<li> ascan? <br> \
     help for ascan \
<li> ascan exp_dmy01 0 10 10 0.1 <br> \
     execute a scan using absolute positions \
<li> a2scan exp_dmy01 0 10 exp_dmy02 5 7 10 0.1 <br>\
     ... with 2 motors \
<li> dscan exp_dmy01 -1 1 10 0.1 <br>\
     a scan centered around the current position \
<li> lsmeas <br>\
     list the measurement groups. The ActiveMntGrp is marked with a *. \
<li> lsenv <br>\
     list all environment variables \
<li> lsenv Scan*<br>\
     list environment variables beginning with 'Scan'\
<li> lsmac<br>\
     list all macros\
<li> wa <br>\
     show all motors \
<li> wm eh_mot01 <br>\
     show the position and limits of eh_mot01 \
<li> mv eh_mot01 1 <br>\
     move eh_mot01 to 1 \
</ul> \
\
"
                ))
        w.show()

    def cb_helpTools(self):
        w = helpBox.HelpBox(self, self.tr("HelpTools"), self.tr(
            "\
<p><b>Tools</b>\
<ul> \
<li> edit SequencyPath/run_seq.lis <br> \
     SequencyPath, a Macroserver environment variable. <br>\
     run_seq.lis contains spock commands. <br>\
     Execute the file with 'run_seq run_seq.lis' \
</ul> \
\
"
                ))
        w.show()

    def cb_tk( self): 
        if self.tkAction.isChecked():
            self.tkFlag = True
        else:
            self.tkFlag = False
        return 
        
    def prepareStatusBar( self):
        #
        # Status Bar
        #
        self.statusBar = QStatusBar()
        self.setStatusBar( self.statusBar)
        #
        # abortMacro() is not working under python3
        #
        if sys.version_info.major == 2: 
            self.abortMacro = QPushButton(self.tr("Abort Macro")) 
            self.abortMacro.setToolTip( "Sends AbortMacro to Door")
            self.statusBar.addWidget( self.abortMacro) 
            self.abortMacro.clicked.connect( self.cb_abortMacro)

        self.stopMacro = QPushButton(self.tr("Stop Macro")) 
        self.stopMacro.setToolTip( "Sends StopMacro to door; no action, if door.state == ON; stops all moves; dscan: motors return to start position")
        self.statusBar.addWidget( self.stopMacro) 
        self.stopMacro.clicked.connect( self.cb_stopMacro)
        #
        # Door
        #
        door = QLabel( "Door")
        self.statusBar.addPermanentWidget( door)
        self.stateLabel = QLabel()
        self.stateLabel.setAlignment( QtCore.Qt.AlignCenter)
        self.stateLabel.setMinimumWidth( 80)
        self.statusBar.addPermanentWidget( self.stateLabel) # 'permanent' to shift it right
        #
        # pyspMonitor
        #
        self.pyspMonitor = QPushButton(self.tr("&pyspMonitor")) 
        self.pyspMonitor.setToolTip( "Launch PyspMonitor to display 0D and 1D data during scans.")
        self.statusBar.addPermanentWidget( self.pyspMonitor) # 'permanent' to shift it right
        self.pyspMonitor.clicked.connect( self.cb_launchPyspMonitor)
        self.pyspMonitor.setShortcut( "Alt+p")
        #
        # apply
        #
        self.apply = QPushButton(self.tr("&Apply")) 
        self.apply.setToolTip( "Apply ScanDir, ScanFile, etc.")
        self.statusBar.addPermanentWidget( self.apply) # 'permanent' to shift it right
        self.apply.clicked.connect( self.cb_applyMacroExecutor)
        self.apply.setShortcut( "Alt+a")
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
        self.exit.clicked.connect( self.cb_closeMacroExecutor )
        self.exit.setShortcut( "Alt+x")

    def fillMgComboBox( self):
        """
        called initially but also after new MGs have been created
        """
        activeMntGrp = HasyUtils.getEnv( "ActiveMntGrp")
        count = 0
        self.activeMntGrpComboBox.clear()
        for mg in HasyUtils.getMgAliases():
            self.activeMntGrpComboBox.addItem( mg)
            #
            # initialize the comboBox to the current ActiveMntGrp
            #
            if activeMntGrp == mg:
                self.activeMntGrpComboBox.setCurrentIndex( count)
            count += 1
        return 
        
    def prepareWidgets( self):
        w = QWidget()
        self.layout_v = QVBoxLayout()
        w.setLayout( self.layout_v)
        self.setCentralWidget( w)
        self.dct = {}
        #
        # the ActiveMntGrp
        #
        if HasyUtils.getMgAliases() is not None:
            hBox = QHBoxLayout()
            w = QLabel( "ActiveMntGrp")
            w.setToolTip( "The ActiveMntGrp contains the devices used for measurements.")
            w.setMinimumWidth( 120)
            hBox.addWidget( w)
            self.activeMntGrpComboBox = QComboBox()
            self.activeMntGrpComboBox.setToolTip( "The ActiveMntGrp contains the devices used for measurements.")
            self.activeMntGrpComboBox.setMinimumWidth( 300)
            self.fillMgComboBox()
            
            #
            # connect the callback AFTER the combox is filled. Otherwise there
            # will be some useless changes
            #
            self.activeMntGrpComboBox.currentIndexChanged.connect( self.cb_activeMntGrpChanged)
            hBox.addWidget( self.activeMntGrpComboBox)
            hBox.addStretch()            

            #
            # launch nxselector
            #
            self.nxselector = QPushButton(self.tr("&nxselector")) 
            self.nxselector.setMinimumWidth( 300)
            self.nxselector.setToolTip( "launch nxselector, e.g. to change or add a measurement group")
            self.nxselector.clicked.connect( self.cb_nxselector)
            self.nxselector.setShortcut( "Alt+n")
            hBox.addWidget( self.nxselector)
            hBox.addStretch()            

            self.layout_v.addLayout( hBox)
            
        #
        # horizontal line
        #
        hBox = QHBoxLayout()
        w = QFrame()
        w.setFrameShape( QFrame.HLine)
        w.setFrameShadow(QFrame.Sunken)
        hBox.addWidget( w)
        self.layout_v.addLayout( hBox)
        #
        # some Env variables
        #
        self.varsEnv = [ "ScanDir", "ScanFile"]
        for var in self.varsEnv:
            hBox = QHBoxLayout()
            w = QLabel( "%s:" % var)
            w.setMinimumWidth( 120)
            hBox.addWidget( w)
            hsh = {}
            w_value = QLabel()
            w_value.setMinimumWidth( 300)
            w_value.setFrameStyle( QFrame.Panel | QFrame.Sunken)
            hBox.addWidget( w_value)
            w_line = QLineEdit()
            w_line.setAlignment( QtCore.Qt.AlignRight)
            w_line.setMinimumWidth( 300)
            hBox.addWidget( w_line)
            self.dct[ var] = { "w_value": w_value, "w_line": w_line}
            self.layout_v.addLayout( hBox)
            if var == "ScanFile": 
                TEXT = \
"\
Use [\"tst.fio\"] to create .fio files,\n\
[\"tst.spe\"] to create spec files\n\
or [\"tst.fio\", \"tst.nxs\"] to create .fio and HDF files."
                w.setToolTip( TEXT)
                w_value.setToolTip( TEXT)
                w_line.setToolTip( TEXT)

        #
        # horizontal line
        #
        hBox = QHBoxLayout()
        w = QFrame()
        w.setFrameShape( QFrame.HLine)
        w.setFrameShadow(QFrame.Sunken)
        hBox.addWidget( w)
        self.layout_v.addLayout( hBox)

        #
        # log widget
        #
        hBox = QHBoxLayout()
        self.logWidget = QTextEdit()
        f = QFont( 'Monospace')
        f.setPixelSize( 12)
        self.logWidget.setFont( f)
        #
        # take care of the laptops
        #
        if self.height > 1000: 
            self.logWidget.setMinimumWidth( 800)
            self.logWidget.setMinimumHeight( 400)
        else: 
            self.logWidget.setMaximumWidth( 800)
            self.logWidget.setMinimumHeight( self.height - 300)
            self.logWidget.setMaximumHeight( self.height - 280)
        self.logWidget.setReadOnly( 1)
        hBox.addWidget( self.logWidget)
        self.layout_v.addLayout( hBox)

        #
        # horizontal line
        #
        hBox = QHBoxLayout()
        w = QFrame()
        w.setFrameShape( QFrame.HLine)
        w.setFrameShadow(QFrame.Sunken)
        hBox.addWidget( w)
        self.layout_v.addLayout( hBox)
        #
        # macro line
        #
        hBox = QHBoxLayout()
        w = QLabel( "Command: ")
        w.setMinimumWidth( 80)
        hBox.addWidget( w)
        
        self.commandComboBox = QComboBox()
        self.commandComboBox.setToolTip( "Enter a command. Execute with Ctrl-e or ENTER")
        self.commandComboBox.setEditable(True)
        self.commandComboBox.setMinimumWidth( 450)
        lst = HasyUtils.getEnv( "MacroExecutorHistory")

        if lst is None:
            lst = []
            for i in range( HISTORY_MAX):
                lst.append( "")
        else:
            for line in lst:
                if len( line.strip()) > 0: 
                    self.commandComboBox.addItem( line)
                else: 
                    self.commandComboBox.addItem( " ")
                    
        self.commandComboBox.activated.connect( self.cb_combo)
        
        hBox.addWidget( self.commandComboBox)
        hBox.addStretch()            

        #
        # Exec
        #
        self.execCmd = QPushButton(self.tr("&Exec")) 
        self.execCmd.setToolTip( "Execute the 'Command'")
        self.execCmd.clicked.connect( self.cb_execCmd)
        self.execCmd.setShortcut( "Alt+e")
        hBox.addWidget( self.execCmd)

        self.layout_v.addLayout( hBox)
        #
        # write the elements of the activeMntGrp to the log widget
        #
        try: 
            elements = HasyUtils.getMgElements( HasyUtils.getEnv( "ActiveMntGrp"))
            self.logWidget.append( "")
            self.logWidget.append( "ActiveMntGrp: %s" % temp)
            self.logWidget.append( "%s" % repr( elements))
        except: 
            pass
        return 

    def keyPressEvent( self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            self.cb_execCmd()
        else:
            super( MacroExecutor, self).keyPressEvent(event)
        return 

        
    def cb_restartTimer( self):
        self.updateTimer.stop()
        self.updateTimer.start( definitions.TIMEOUT_REFRESH)
        
    def cb_stopTimer( self):
        self.updateTimer.stop()

    def findEditor( self):
        if self.tkFlag:
            argout = "emacs"
        else: 
            argout = HasyUtils.findEditor()                    
        return argout


    def cb_logToTempFile( self):
        fName = HasyUtils.createScanName( "macroExecutor") + ".lis"
        try:
            out = open( fName, "w")
        except Exception as e:
            self.logWidget( "Failed to open %s" % fName)
            self.logWidget( repr( e))
            return
        lst = self.logWidget.toPlainText()
        out.writelines(lst)
        out.close()
        self.logWidget.append( "Save log widget contents to %s" % fName)
        os.system( "%s %s&" % ( self.findEditor(), fName))
        

    def cb_msIfc( self):
        self.ms = macroServerIfc.MacroServerIfc( self.logWidget, self)
        self.ms.show()

    def cb_editRunSeq( self): 
        temp = HasyUtils.getEnv( "SequencyPath")
        if temp is None: 
            self.logWidget( "editRunSeq: SequencyPath does not exist")
        os.system( "%s %s/run_seq.lis&" % ( self.findEditor(), temp))
        return

    def cb_nxselector( self): 
        os.system( "/usr/bin/nxselector &")
        return 

    def cb_clear( self):
        self.logWidget.clear()
        return

    def cb_launchMCA( self): 
        self.mcaWidget = mcaWidget.mcaWidget( devices = self.devices, 
                                              logWidget = self.logWidget, 
                                              app = None, parent = self)
        self.mcaWidget.show()
        
    def cb_launchPyspMonitor( self):
        os.system( "/usr/bin/pyspMonitor.py &")
        
    def cb_launchSardanaMonitor( self):
        os.system( "/usr/bin/SardanaMonitor.py &")
        
    def cb_launchLavue( self):
        if sys.version_info.major == 2: 
            os.system( "/usr/bin/lavue &")
        else: 
            os.system( "/usr/bin/lavue3 &")
        
    def cb_launchPymca( self):
        os.system( "/usr/bin/pymca &")
        
    def cb_launchChat( self):
        os.system( "/usr/bin/SardanaChat.py &")
        
    def cb_launchMotorMonitor( self):
        os.system( "/usr/bin/SardanaMotorMonitor.py &")
    
    #
    # cb_combo() is not used because we cannot connect
    # it to a useful signal, like ENTER. The activated
    # signal is useless because this is also thrown when
    # we are togglich through the combo box.
    #
    def cb_combo( self, index):
        temp = str( self.commandComboBox.currentText())
        return 

        
    def cb_applyMacroExecutor( self):
        '''
        apply ScanDir, ScanFile, etc.
        '''
        for var in self.varsEnv:
            hsh = self.dct[ var]
            inp = str(hsh[ "w_line"].text())
            if len( inp) > 0:
                hsh[ "w_line"].clear()
                self.logWidget.append( "setting %s to %s " % (var, repr(inp)))
                try: 
                    HasyUtils.setEnv( var, inp)
                except Exception as e: 
                    self.logWidget.append( "error %s" % repr( e))
                hsh[ 'w_value'].setText( repr( HasyUtils.getEnv( var)))
        return 
        
    def cb_execCmd( self):
        '''
        execute 'Command'
        '''
        temp = str( self.commandComboBox.currentText()).strip()
        if len( temp) == 0: 
            return 

        #
        # prepare history
        #
        tmp = str( self.commandComboBox.itemText( 0))
        if tmp != temp: 
            self.commandComboBox.insertItem( 0, temp)
            self.commandComboBox.setCurrentIndex( 0)
        #
        # retrieve macro doc
        #
        if temp[-1] == '?': 
            self.logWidget.append( "")
            self.logWidget.append( "--- Help for %s" % temp[:-1])
            self.printMacroInfo( temp[:-1])
            self.app.processEvents()
            return

        #
        # execute command
        #
        lst = str( temp).split( " ")
        try: 
            self.logWidget.append( "")
            self.logWidget.append( "--- Executing %s (temp)" % temp)
            #
            # special treatment for 'senv ScanFile ...'
            #
            # input:    senv ScanFile "['tst.fio', 'tst.spe']"
            # extract: "['tst.fio', 'tst.spe']"
            # convert to the list: ['tst.fio', 'tst.spe']
            # set ScanFile to the list
            #
            if lst[0] == 'senv' and lst[1] == 'ScanFile':
                self.logWidget.append( "--- Executing %s" % str(lst))
                temp1 = ''.join(lst[2:])
                if temp1[0] == '"' and temp1[-1] == '"':
                    temp1 = temp1[1:-1]
                    a = eval( temp1)
                    HasyUtils.setEnv( 'ScanFile', a)
                self.logWidget.append( "--- Setting ScanFile to %s" % str(a))
            else: 
                self.doorProxy.runMacro( lst)
                
        except Exception as e: 
            self.logWidget.append( "Error executing %s" % str( temp))
            self.logWidget.append( "%s" % str( e))
        return 

    def printMacroInfo( self, mName): 
        hsh = HasyUtils.getMacroInfo( mName)
        if hsh is None: 
            self.logWidget.append( "macro %s unknown" % temp[:-1])
            return 

        self.logWidget.append( "")
        self.logWidget.append( "Syntax:")

        line = "  %s " % hsh[ 'name']
        for dct in hsh[ 'parameters']: 
            line += "%s " % dct[ 'name']
        self.logWidget.append( "%s" % (line))

        self.logWidget.append( "")

        self.logWidget.append( "Description:")
        self.logWidget.append( "%s" % ( hsh[ 'description']))

        self.logWidget.append( "")

        self.logWidget.append( "Parameters")
        for dct in hsh[ 'parameters']: 
            self.logWidget.append( "  %s: %s, def. %s, %s " % ( dct[ 'name'], dct[ 'description'], dct[ 'default_value'], dct[ 'type']))

        self.logWidget.append( "")
        for key in [ 'file_path', 'hints']: 
            if hsh[ key] is None or hsh[ key] == {}: 
                continue
            self.logWidget.append( "%s: %s" % ( key, hsh[ key]))

        return 

    def cb_refreshMacroExecutor( self):

        if self.isMinimized(): 
            return

        self.activityIndex += 1
        if self.activityIndex > (len( definitions.ACTIVITY_SYMBOLS) - 1):
            self.activityIndex = 0
        self.activity.setTitle( definitions.ACTIVITY_SYMBOLS[ self.activityIndex])
        #
        # has the ActiveMntGrp been changed from outside?
        #
        if HasyUtils.getMgAliases() is not None:
            activeMntGrp = HasyUtils.getEnv( "ActiveMntGrp")
            temp = str(self.activeMntGrpComboBox.currentText())
            if temp != activeMntGrp:
                max = self.activeMntGrpComboBox.count()
                for count in range( 0, max):
                    temp1 = str( self.activeMntGrpComboBox.itemText( count))
                    if temp1 == activeMntGrp:
                        self.activeMntGrpComboBox.setCurrentIndex( count)
                    break
                else:
                    self.logWidget.append( "New ActiveMntGrp not on the list, restart widget")

        envDct = HasyUtils.getEnvDct()
                    
        for var in self.varsEnv:
            try: 
                res = envDct[ var]
                if type( res) is list:
                    res = repr( res)
                if res is None:
                    self.dct[ var][ "w_value"].setText( "None")
                else:
                    self.dct[ var][ "w_value"].setText( str(res))
            except: 
                self.dct[ var][ "w_value"].setText( "None")

        #
        # the queue() is filled from sendHshQueue() in
        #  $HOME/gitlabDESY/tnggui/tngGui/tngGuiDoor.py
        #
        try:
            cnt = 0
            while True:
                hsh = self.queue.get_nowait()
                self.logWidget.append( hsh[ 'line'])
                self.app.processEvents() 
                #print( "%s" % hsh[ 'line'])
                self.queue.task_done()
                cnt += 1
        except queue.Empty as e:
            pass

        try: 
            state = self.doorProxy.state()
        except Exception as e: 
            print( "macroExecutorClass.cb_refreshMacroExecutor: %s" % repr( e))
            self.stateLabel.setText( "Offline")
            self.stateLabel.setStyleSheet( "background-color:%s;" % definitions.RED_ALARM)
            return 

        if state == PyTango.DevState.MOVING:
            self.stateLabel.setText( "MOVING")
            self.stateLabel.setStyleSheet( "background-color:%s;" % definitions.BLUE_MOVING)
        elif state == PyTango.DevState.RUNNING:
            self.stateLabel.setText( "RUNNING")
            self.stateLabel.setStyleSheet( "background-color:%s;" % definitions.BLUE_MOVING)
        elif state == PyTango.DevState.ON:
            self.stateLabel.setText( "ON")
            self.stateLabel.setStyleSheet( "background-color:%s;" % definitions.GREEN_OK)
        elif state == PyTango.DevState.DISABLE:
            self.stateLabel.setText( "DISABLE")
            self.stateLabel.setStyleSheet( "background-color:%s;" % definitions.MAGENTA_DISABLE)
        else:
            self.stateLabel.setText( repr( state))
            self.stateLabel.setStyleSheet( "background-color:%s;" % definitions.RED_ALARM)
        
        return
        
    def closeEvent( self, e):
        lst = []
        for i in range( self.commandComboBox.count()):
            line = str( self.commandComboBox.itemText( i)).strip()
            if len( line) > 0:
                #
                # we don't want commands to appear twice
                #
                if line not in lst: 
                    lst.append( line) 
        try: 
            HasyUtils.setEnv( "MacroExecutorHistory", lst)
        except: 
            pass
        self.cb_closeMacroExecutor()

    def cb_closeMacroExecutor( self): 
        self.updateTimer.stop()
        self.close()

    def cb_abortMacro( self): 
        try:
            door = PyTango.DeviceProxy( HasyUtils.getLocalDoorNames()[0])
        except Exception as e:
            self.logWidget.append( "cb_abortMacro: Failed to create proxy to Door" )
            self.logWidget.append( repr( e))
            return 

        door.abortmacro()
        self.logWidget.append( "Sent abortmacro() to door")
        return 

    def cb_stopMacro( self): 
        try:
            door = PyTango.DeviceProxy( HasyUtils.getLocalDoorNames()[0])
        except Exception as e:
            self.logWidget.append( "cb_stopacro: Failed to create proxy to Door" )
            self.logWidget.append( repr( e))
            return 
        
        if door.State() != PyTango.DevState.ON:        
            door.StopMacro()
            self.logWidget.append( "Sent StopMacro() to %s" % door.name())
        else:
            self.logWidget.append( "%s is already in ON state, no action" % door.name())
        return 

    def cb_activeMntGrpChanged( self):
        temp = str(self.activeMntGrpComboBox.currentText())
        if len( temp.strip()) == 0:
            return 
        HasyUtils.setEnv( "ActiveMntGrp", temp)
        elements = HasyUtils.getMgElements( temp)

        self.logWidget.append( "")
        self.logWidget.append( "ActiveMntGrp: %s" % temp)
        self.logWidget.append( "%s" % repr( elements))
        return 

    def executeZmqCommand( self, hsh): 
        '''
        receives a dictionary sent by an interactive macro

        yesno: 
          hsh = { 'yesno': 'do you really want if'}
          argout = { 'result': 'yes'}
                   { 'result': 'no'}
        getstring: 
          hsh = { 'getstring': "Enter 'hallo'"} 
          argout = { 'result': 'hallo')
        '''

        if 'isAlive' in hsh: 
            argout = { 'result': 'yes'}
            return argout
        
        #
        # YesNo
        #
        if 'yesno' in hsh: 
            temp = hsh[ 'yesno']

            # Create the dialog without running it yet
            msgBox = QMessageBox()

            # Set the various texts
            msgBox.setWindowTitle("YesNo")
            msgBox.setText( "%s" % (hsh[ 'yesno']))

            # Add buttons and set default
            msgBox.setStandardButtons( QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton( QMessageBox.No)     

            msgBox.show()
            msgBox.setFocus()
            # Run the dialog, and check results   
            bttn = msgBox.exec_()
            if bttn == QMessageBox.Yes:
                argout = { 'result': 'yes'}
            else: 
                argout = { 'result': 'no'}
        #
        # getsting
        #
        elif 'getstring' in hsh: 

            d = QDialog()
            d.setWindowTitle("Enter a String")

            layout_v = QVBoxLayout()
            d.setLayout( layout_v)

            hBox = QHBoxLayout()
            label = QLabel( hsh[ 'getstring'])
            hBox.addWidget( label)
            getStringLine = QLineEdit()
            getStringLine.setAlignment( QtCore.Qt.AlignRight)
            getStringLine.setMinimumWidth( 150)

            hBox.addWidget( getStringLine)
            layout_v.addLayout( hBox)

            hBox = QHBoxLayout()

            doneBtn = QPushButton( "&Done", d)
            doneBtn.clicked.connect( d.close)
            hBox.addStretch()            
            hBox.addWidget( doneBtn)
            layout_v.addLayout( hBox)

            d.show()
            d.setFocus()
            d.exec_()

            argout = { 'result': '%s' % getStringLine.text()} 
        else: 
            argout = { 'result': 'macroExecutor: failed to identify %s' % repr( hsh)}

        return argout


