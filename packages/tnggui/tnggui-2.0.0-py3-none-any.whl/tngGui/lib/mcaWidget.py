#!/usr/bin/env python

from PySpectra.pyqtSelector import *

import PyTango
import numpy
import math, time, sys, os
import HasyUtils
import tngGui.lib.utils as utils
import tngGui.lib.definitions as definitions
import tngGui.lib.devices as devices
import tngGui.lib.selectMcaAndTimer as selectMcaAndTimer
import PySpectra

TIMEOUT_MCA_BUSY = 100

class mcaWidget( QMainWindow):
    def __init__( self, dev = None, devices = None, logWidget = None, app = None, parent = None):
        super( mcaWidget, self).__init__( parent)

        if PySpectra.InfoBlock.monitorGui is None:
            PySpectra.InfoBlock.setMonitorGui( self)
        self.dev = dev
        self.devices = devices
        if self.devices == None: 
            self.devices = devices.Devices()
        self.logWidget = logWidget
        self.app = app
        self.parent = parent
        if self.parent is not None: 
            self.tkFlag = self.parent.tkFlag
        #
        # search the selected device by a function because 
        # devices may change during the live time of thei widget
        self.findSelectedDevices()
        self.mcaOntop = self.selectedMCAs[0]
        #
        # set the window title
        #
        if self.dev is not None: 
            self.setWindowTitle( "MCA %s" % self.dev[ 'name'])
        else: 
            self.setWindowTitle( "MCA")
        self.move( 10, 750)

        #
        # prepare widgets
        #
        self.prepareWidgets()

        self.flagClosed = False
        self.pyspGui = None
        self.statusMCA = "Idle"
        self.flagTimerWasBusy = False
        #
        # updateTimeMCA: the interval between MCA readings
        #
        self.updateTimeMCA = 1.
        self.timeDead = 0.
        self.timeTotal = 0
        # 
        #
        self.refreshTimer = QtCore.QTimer(self)
        self.refreshTimer.start( definitions.TIMEOUT_REFRESH_MOTOR) 
        self.refreshTimer.timeout.connect( self.cb_refreshMCAWidget)
        #
        # the timer which is busy while the MCAs are active
        #
        self.mcaTimer = QtCore.QTimer( self)
        self.mcaTimer.timeout.connect( self.updateMeasurement)

        for dev in self.selectedMCAs: 
            dev[ 'proxy'].stop()
        self.clearMCAs()

        return 

    def findSelectedDevices( self): 
        
        res = HasyUtils.setEnv( "ActiveMntGrp", "mg_tnggui") 
        res = HasyUtils.getEnv( "ActiveMntGrp") 
        lst = HasyUtils.getMgElements( res)
        if lst is None or len( lst) == 0: 
            self.selectedTimers = self.devices.allTimers[:]
            self.selectedMCAs = self.devices.allMCAs[:]
        else: 
            #
            # ['eh_t01', 'eh_c01', 'eh_mca01']
            #
            self.selectedTimers = []
            for elm in lst: 
                if elm.find( '_t0') != -1: 
                    self.selectedTimers.append( self.getDev( elm))
            self.selectedMCAs = []
            for elm in lst: 
                if elm.find( '_mca') != -1 and elm.find( "roi") == -1: 
                    temp = self.getDev( elm)
                    self.selectedMCAs.append( temp)

        if len( self.selectedMCAs) == 0: 
            if self.logWidget:
                self.logWidget.append( "mcaWidget: the MCA does not contains MCAs")
            raise ValueError( "mcaWidget: the MG does not contain MCAs")
        return 

    def getDev( self, name): 
        """
        return the dictionary belonging to name
        """
        for dev in self.devices.allDevices: 
            if name == dev[ 'name']:
                return dev
        return None

    def cb_refreshMCAWidget( self): 
        #
        # update the widgets
        #

        self.activityIndex += 1
        if self.activityIndex > (len( definitions.ACTIVITY_SYMBOLS) - 1):
            self.activityIndex = 0
        self.activity.setTitle( definitions.ACTIVITY_SYMBOLS[ self.activityIndex])

        if 'scanGQE' in self.mcaOntop: 
            self.totalCountsLabel.setText( "%g" % self.mcaOntop[ 'scanGQE'].getTotalCounts())

        #print( "refreshMCAWidget %s" % self.statusMCA)
        return 

    def prepareWidgets( self):
        w = QWidget()
        self.layout_v = QVBoxLayout()
        w.setLayout( self.layout_v)
        self.setCentralWidget( w)
        #
        # sample time, total time, remaining
        #
        hBox = QHBoxLayout()
        hBox.addWidget( QLabel( "Sample time"))
        self.sampleTimeLine = QLineEdit()
        self.sampleTimeLine.setFixedWidth( 50)
        self.sampleTimeLine.setAlignment( QtCore.Qt.AlignRight)
        self.sampleTimeLine.setText( "-1")
        hBox.addWidget( self.sampleTimeLine)
        #
        # total time
        #
        hBox.addWidget( QLabel( "Total time"))
        self.totalTimeLabel = QLabel( "")
        self.totalTimeLabel.setFixedWidth( 50)
        hBox.addWidget( self.totalTimeLabel)
        #
        # remaining time
        #
        hBox.addWidget( QLabel( "Remaining"))
        self.remainingTimeLabel = QLabel()
        self.remainingTimeLabel.setFixedWidth( 50)
        hBox.addWidget( self.remainingTimeLabel)
        #
        # dead time
        #
        hBox.addWidget( QLabel( "Dead time[%]"))
        self.deadTimeLabel = QLabel()
        self.deadTimeLabel.setFixedWidth( 50)
        hBox.addWidget( self.deadTimeLabel)
        #
        # status
        #
        self.statusLabel = QLabel( "Idle")
        self.statusLabel.setFixedWidth( 50)
        self.statusLabel.setAlignment( QtCore.Qt.AlignCenter)
        self.statusLabel.setStyleSheet( "background-color:%s;" % definitions.GREEN_OK)
        hBox.addWidget( self.statusLabel)
        self.layout_v.addLayout( hBox)

        #
        # the devices frame
        #
        frame = QFrame()
        frame.setFrameShape( QFrame.Box)
        self.layout_v.addWidget( frame)
        self.layout_frame_v = QVBoxLayout()
        frame.setLayout( self.layout_frame_v)

        hBox = QHBoxLayout()
        #
        # MCA 
        #
        self.mcaComboBox = QComboBox()
        for dev in self.selectedMCAs: 
            self.mcaComboBox.addItem( dev[ 'name'])
        hBox.addWidget( self.mcaComboBox)
        #
        # channels
        #
        hBox.addWidget( QLabel( 'Channels:'))
        self.channelsComboBox = QComboBox()
        for chan in definitions.channelsArr:
            self.channelsComboBox.addItem( chan)
        self.channelsComboBox.setCurrentIndex( definitions.channelsDct[ '%d' % self.mcaOntop[ 'proxy'].DataLength])
        
        hBox.addWidget( self.channelsComboBox)
        #
        # total counts
        #
        hBox.addWidget( QLabel( 'Total:'))
        self.totalCountsLabel = QLabel( "")

        hBox.addWidget( self.totalCountsLabel)
        self.layout_frame_v.addLayout( hBox)

        #
        # Menu Bar
        #
        self.menuBar = QMenuBar()
        self.setMenuBar( self.menuBar)
        self.prepareMenuBar()

        #
        # Status Bar
        #
        self.statusBar = QStatusBar()
        self.setStatusBar( self.statusBar)
        self.prepareStatusBar()

        #
        # create the log widget, if necessary
        #
        if self.logWidget is None:
             self.logWidget = QTextEdit()
             self.logWidget.setMaximumHeight( 150)
             self.logWidget.setReadOnly( 1)
             self.layout_v.addWidget( self.logWidget)
             self.w_clearLog = QPushButton(self.tr("ClearLog")) 
             self.w_clearLog.setToolTip( "Clear log widget")
             self.statusBar.addPermanentWidget( self.w_clearLog) # 'permanent' to shift it right
             self.w_clearLog.clicked.connect( self.logWidget.clear)

        self.exit = QPushButton(self.tr("&Exit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( self.cb_closeMCAWidget)
        self.exit.setShortcut( "Alt+x")
        #
        # connect the callback functions at the end because the depend on each other
        #
        self.channelsComboBox.currentIndexChanged.connect( self.cb_channelsChanged)
        self.mcaComboBox.currentIndexChanged.connect( self.cb_mcaChanged)
        return 

    def prepareMenuBar( self):

        self.fileMenu = self.menuBar.addMenu('&File')

        self.writeFileAction = QAction('Write .fio file', self)        
        self.writeFileAction.triggered.connect( self.cb_writeFile)
        self.fileMenu.addAction( self.writeFileAction)

        self.hardcopyAction = QAction('Hardcopy', self)        
        self.hardcopyAction.setStatusTip('Create pdf output')
        self.hardcopyAction.triggered.connect( self.cb_hardcopy)
        self.fileMenu.addAction( self.hardcopyAction)

        self.hardcopyActionA6 = QAction('Hardcopy A6', self)        
        self.hardcopyActionA6.setStatusTip('Create pdf output, A6')
        self.hardcopyActionA6.triggered.connect( self.cb_hardcopyA6)
        self.fileMenu.addAction( self.hardcopyActionA6)
        
        self.exitAction = QAction('E&xit', self)        
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect( self.cb_closeMCAWidget)
        self.fileMenu.addAction( self.exitAction)

        self.optionsMenu = self.menuBar.addMenu('Options')

        self.selectDevicesAction = QAction('Select devices', self)       
        self.selectDevicesAction.triggered.connect( self.cb_selectDevices)
        self.optionsMenu.addAction( self.selectDevicesAction)
        #
        # the activity menubar: help and activity
        #
        self.menuBarActivity = QMenuBar( self.menuBar)
        self.menuBar.setCornerWidget( self.menuBarActivity, QtCore.Qt.TopRightCorner)

        self.helpMenu = self.menuBarActivity.addMenu('Help')
        self.helpMCA = self.helpMenu.addAction(self.tr("MCA"))
        self.helpMCA.triggered.connect( self.cb_helpMCA)

        self.activityIndex = 0
        self.activity = self.menuBarActivity.addMenu( "_")

        return 

    def prepareStatusBar( self): 
        self.w_startButton = QPushButton(self.tr("&Start")) 
        self.w_startButton.setToolTip( "Start the MCAs")
        self.statusBar.addPermanentWidget( self.w_startButton) # 'permanent' to shift it right
        self.w_startButton.clicked.connect( self.cb_startMeasurement)
        self.w_startButton.setShortcut( "Alt+s")

        self.w_clearButton = QPushButton(self.tr("&Clear")) 
        self.w_clearButton.setToolTip( "Stop timers, stop MCAs, clea MCAs, delete data, reset dead-time and total-time")
        self.statusBar.addPermanentWidget( self.w_clearButton) # 'permanent' to shift it right
        self.w_clearButton.clicked.connect( self.cb_clearMeasurement)
        self.w_clearButton.setShortcut( "Alt+c")

        return 

    def reconfigureWidget( self): 
        """
        called from selectTimerAndMCAs
        """
        lst = HasyUtils.getMgElements( "mg_tnggui")
        if len( lst) == 0:
            self.logWidget.append( "reconfigureWidget: mg_tnggui is empty")
            return 
        #
        # ['eh_t01', 'eh_c01', 'eh_mca01']
        #
        self.selectedTimers = []
        for elm in lst: 
            if elm.find( '_t0') != -1: 
                self.selectedTimers.append( self.getDev( elm))
        self.selectedMCAs = []
        for elm in lst: 
            if elm.find( '_mca') != -1: 
                self.selectedMCAs.append( self.getDev( elm))

        #self.selectedTimers.sort()
        #self.selectedMCAs.sort()
        self.mcaComboBox.clear()
        for dev in self.selectedMCAs: 
            self.mcaComboBox.addItem( dev[ 'name'])
        self.mcaOntop = self.selectedMCAs[0]
        return 

    def checkTimers( self): 
        """
        return True, if one of the selectedTimers is busy
        """
        for tm in self.selectedTimers: 
            if tm[ 'proxy'].state() == PyTango.DevState.MOVING:
                return True
        return False
            
    def resetCounters( self): 
        return 
    def readCounters( self): 
        return 
    def preparePetraCurrent( self): 
        return 

    def calcROIs( self): 
        
        return 

    def updateMeasurement( self): 
        """
        """
        if self.checkTimers(): 
            return 

        if self.flagTimerWasBusy: 
            self.stopMCAs()
            self.readMCAs()
            self.calcROIs()
            self.readCounters()
            self.preparePetraCurrent()
            self.flagTimerWasBusy = False
            self.statusMCA = "Idle"

            if self.timeTotal > 0:
                now = time.time()
                timeDeadTemp = 100.*( now - self.timeStartElapsed - self.timeTotal)/(now - self.timeStartElapsed)
                if timeDeadTemp > 0.:
                    self.timeDead = timeDeadTemp
                    self.deadTimeLabel.setText( "%g" % self.timeDead)

        timeGate = 0
        #
        # '-1' -> forever
        #
        if self.timeRemaining != 0: 
            if self.updateTimeMCA < self.timeRemaining or self.timeRemaining == -1.:
                timeGate = self.updateTimeMCA
            else:
                timeGate = self.timeRemaining

            #self.clearMCAs()
            self.startMCAs()

            self.resetCounters()
            
            self.startTimers( timeGate)
            self.flagTimerWasBusy = True
            if self.timeRemaining != -1.:
                self.timeRemaining -= timeGate
            self.remainingTimeLabel.setText( "%g" % self.timeRemaining)

            self.timeTotal += timeGate
            self.totalTimeLabel.setText( "%g" % self.timeTotal)
            self.statusMCA = "Busy"

        else: 
            self.statusMCA = "Idle"
            self.statusLabel.setText( self.statusMCA)
            self.statusLabel.setStyleSheet( "background-color:%s;" % definitions.GREEN_OK)

            self.configureWidgetsBusy( False)

        # update the menu and re-call this function
        #self.cb_refreshMCAWidget()

        if timeGate: 
            self.mcaTimer.start( TIMEOUT_MCA_BUSY)
            self.w_startButton.setText( "Stop")
        else: 
            self.mcaTimer.stop()
            self.w_startButton.setText( "Start")

        return 
        
    def cb_clearMeasurement( self):
        """
        """
        self.logWidget.append( "cb_clearMeasurement")

        self.stopTimers()
        self.stopMCAs()
        self.clearMCAs()

        for mca in self.selectedMCAs:
            if 'scanGQE' in mca: 
                PySpectra.delete( mca[ 'scanGQE'].name)
                del mca[ 'scanGQE']

        PySpectra.cls()

        self.timeDead = 0
        self.deadTimeLabel.setText( "%g" % self.timeDead)
        self.timeTotal = 0
        self.totalTimeLabel.setText( "%g" % self.timeTotal)
        self.totalCountsLabel.setText( "0")

        return 

    def cb_startMeasurement( self):
        """
        start MCAs and timers
        """

        if self.statusMCA.upper() == "BUSY":
            self.logWidget.append( "cb_stopMeasurement")
            self.stopTimers()
            self.stopMCAs()
            self.timeRemaining = 0
            self.updateMeasurement()
            self.w_startButton.setText( self.tr("&Start")) 
            return

        self.logWidget.append( "cb_startMeasurement")
        #
        # may have changed in between
        #
        self.findSelectedDevices()
        #
        # get the sample time from the QlineEdit
        #
        temp = self.sampleTimeLine.text()
        if len( temp) == 0:
            self.logWidget.append( "startMeasurement: specify sample time")
            return
        try: 
            self.sampleTime = float( temp)
        except Exception as e: 
            self.logWidget.append( "cb_startMeasurement: error from float( sampleTIme)")
            self.logWidget.append( repr( e))
            return 

        self.timeRemaining = self.sampleTime
        self.timeStartElapsed = time.time()

        self.configureWidgetsBusy( True)
        self.statusMCA = "Busy"
        self.statusLabel.setText( self.statusMCA)
        self.statusLabel.setStyleSheet( "background-color:%s;" % definitions.BLUE_MOVING)
        
        self.statusLabel.setText( self.statusMCA)
        self.w_startButton.setText( self.tr("&Stop")) 

        PySpectra.setTitle( "Started %s" % time.strftime("%d %b %Y %H:%M:%S", time.localtime()))
        self.updateMeasurement()
        
        return

    def stopTimers( self):
        for timer in self.selectedTimers:
            timer[ 'proxy'].stop()
        return
            
    def startTimers( self, gateTime):
        for timer in self.selectedTimers:
            timer[ 'proxy'].sampleTime = gateTime
            timer[ 'proxy'].start()

    def startMCAs( self):
        for mca in self.selectedMCAs:
            mca[ 'proxy'].start()

    def clearMCAs( self):
        for mca in self.selectedMCAs:
            mca[ 'proxy'].clear()

    def stopMCAs( self):
        for mca in self.selectedMCAs:
            mca[ 'proxy'].stop()
        
    def readMCAs( self): 
        for mca in self.selectedMCAs:
            mca[ 'proxy'].read()
            if 'scanGQE' in mca: 
                if len( mca[ 'scanGQE'].x) != mca[ 'proxy'].DataLength:
                    PySpectra.delete( mca[ 'scanGQE'].name)
                    mca[ 'scanGQE'] = PySpectra.Scan( name = mca[ 'name'], 
                                                      y = mca[ 'proxy'].data)
                    PySpectra.display()
                else:  
                    mca[ 'scanGQE'].smartUpdateDataAndDisplay( y = numpy.copy( mca[ 'proxy'].data))
            else: 
                mca[ 'scanGQE'] = PySpectra.Scan( name = mca[ 'name'], 
                                                   y = mca[ 'proxy'].data)
                PySpectra.display()

        return 

    def cb_channelsChanged( self):
        """
        change the channel number of the current MCA
        """
        print( "channelsChanged %s  to %s " % (self.mcaOntop[ 'name'], self.channelsComboBox.currentText()))
        self.mcaOntop[ 'proxy'].DataLength = int( self.channelsComboBox.currentText())
        return 

    def cb_mcaChanged( self):
        """
        called when the current MCA is changed
        """
        self.mcaOntop = self.getDev( self.mcaComboBox.currentText())
        print( "mcaChanged to %s" % self.mcaOntop[ 'name'])
        print( "mcaChanged channel from HW %d, index %d" % 
               (self.mcaOntop[ 'proxy'].DataLength, definitions.channelsDct[ '%d' % self.mcaOntop[ 'proxy'].DataLength]))
        self.channelsComboBox.setCurrentIndex( definitions.channelsDct[ '%d' % self.mcaOntop[ 'proxy'].DataLength])
        return 
            
    def cb_selectDevices( self): 
        w = selectMcaAndTimer.SelectMcaAndTimer( devices = self.devices, parent = self)
        w.show()
        return w

    def cb_helpMCA(self):
        QMessageBox.about(self, self.tr("Help MCA"), self.tr(
                "<h3> Operation </h3>"
                "<ul>"
                "<li> Options-SelectDevices to select the timer and the MCA</li>"
                "<li> Set sample time, '-1' encodes eternity</li>"
                "<li> Press 'Start'</li>"
                "</ul>"
                ))

    def cb_writeFile( self):
        res = PySpectra.write()
        self.logWidget.append( "Created %s" % res)

    def _printHelper( self, frmt): 
        '''
        do the visible plot only
        '''
        prnt = os.getenv( "PRINTER")
        if prnt is None: 
            QMessageBox.about(self, 'Info Box', "No shell environment variable PRINTER.") 
            return

        fName = PySpectra.createPDF( flagPrint = False, format = frmt)
        #
        # necessary to bring pqt and mpl again in-sync, mind lastIndex
        #
        PySpectra.cls()
        PySpectra.display()

        self.logWidget.append( HasyUtils.getDateTime())
        self.logWidget.append("Created %s (%s)" % (fName, frmt))

        msg = "Send %s to %s" % ( fName, prnt)
        reply = QMessageBox.question(self, 'YesNo', msg, 
                                           QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if os.system( "/usr/bin/lpr -P %s %s" % (prnt, fName)):
                self.logWidget.append( "failed to print %s on %s" % (fName, prnt))
            self.logWidget.append(" printed on %s" % (prnt))
        
    def cb_hardcopy(self):
        self._printHelper( "DINA4")
        
    def cb_hardcopyA6(self):
        self._printHelper( "DINA6")

    #
    # the closeEvent is called when the window is closed by 
    # clicking the X at the right-upper corner of the frame
    #
    def closeEvent( self, e):
        self.cb_closeMCAWidget()
        #e.ignore()

    def cb_closeMCAWidget( self):
        import PySpectra.pyspMonitorClass

        if self.flagClosed:
            return
                    
        self.refreshTimer.stop()

        if self.pyspGui is not None:
            self.pyspGui.close()
        
        self.flagClosed = True
        self.close()

        #
        # do not close the application, if we have been called from pyspMonitor
        #
        if type( self.parent) is PySpectra.pyspMonitorClass.pyspMonitor: 
            return 
        #
        #  
        #
        PySpectra.close()
        #
        # we have to close the application, if we arrive here from 
        # TngGui.main() -> TngGuiClass.launchMoveMotor() -> moveMotor()
        #
        if self.app is not None: 
            self.app.quit()
        return

    def configureWidgetsBusy( self, flag):
        #self.w_slider.setEnabled( flag)
        return
    
    def cb_launchPyspGui( self): 
        '''
        launches the pyspGui to allow for actions like the Cursor widget
        '''
        import PySpectra.pySpectraGuiClass
        self.pyspGui = PySpectra.pySpectraGuiClass.pySpectraGui()
        self.pyspGui.show()


