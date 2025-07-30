#!/usr/bin/env python
#
import math, time, os, signal, sys
import HasyUtils
from PySpectra.pyqtSelector import *
import socket
import numpy as np
 
import tngGui.lib.helpBox as helpBox
import tngGui.lib.defineSignal as defineSignal 
import tngGui.lib.moveMotor as moveMotor
import tngGui.lib.tngAPI as tngAPI
import tngGui.lib.macroServerIfc as macroServerIfc
import tngGui.lib.macroExecutorClass as macroExecutorClass
import tngGui.lib.mcaWidget as mcaWidget
import tngGui.lib.utils as utils
import tngGui.lib.definitions as definitions
import tngGui.lib.devices as devices
import PySpectra.pySpectraGuiClass
import PyTango

def launchMoveMotor( dev, devices, app, logWidget = None, parent = None, tabletMode = False): 
    '''
    called from 
      - TngGui.main() 
      - pyspMonitorClass
    '''
    print( "tngGuiClass, launchMoveMotor, flag %s " % repr( tabletMode))
    w = moveMotor.moveMotor( dev, devices, logWidget, app, parent, tabletMode)
    return w

class mainMenu( QMainWindow):
    '''
    the main class of the TngTool application
    '''
    def __init__( self, args = None, app = None, devs = None, parent = None, tabletMode = False):
        super( mainMenu, self).__init__( parent)

        self.name = "tngGuiClass.mainMenu"
        # select emacs
        self.tkFlag = False

        self.tabletMode = tabletMode

        self.hostName = socket.gethostname()                      # haso107tk
        self.setWindowTitle( "TngGui@%s" % self.hostName)

        if PySpectra.InfoBlock.monitorGui is None:
            PySpectra.InfoBlock.setMonitorGui( self)

        self.args = args        
        if devs is None: 
            self.devices = devices.Devices( args = args, xmlFile = None, parent = self)
        else: 
            self.devices = devs

        if self.args.tags and len( self.args.namePattern) > 0:
            print( "TngGui: specify tags or names")
            sys.exit( 255)

        self.app = app
        #
        # 28.07.2021: do we really need self.doorProxy
        # 16.02.2022: yes, to execute a stopMacro()
        doors = HasyUtils.getLocalDoorNames()
        self.doorProxies = []
        if len( doors) > 0: 
            try: 
                for d in doors: 
                    self.doorProxies.append( PyTango.DeviceProxy( d))
            except Exception as e: 
                raise ValueError( "TngGuiClass.__init__: failed to create door proxy, %s" % repr( e))
        else: 
            self.doorProxies = None

        self.w_attr = None
        self.w_commands = None
        self.w_encAttr = None
        self.w_moveMotor = None
        self.w_prop = None
        self.w_timer = None
        #self.pyspGui = None
        self.move( 700, 20)

        if not os.access( "/etc/tangorc", os.R_OK): 
            QMessageBox.critical(self, 'Error', 
                                       "/etc/tangorc does not exist", QMessageBox.Ok)
            raise ValueError( "tngGuiClass no /etc/tangorc")

        prc = os.popen( "grep TANGO_USER /etc/tangorc")
        ret = prc.read()
        prc.close()
        ret = ret.strip()
        self.tangoUser = ret.split( '=')[1]
        

        self.prepareWidgets()

        self.prepareMenuBar()

        self.prepareStatusBar()

        self.updateCount = 0

        self.refreshFunc = self.refreshMotors

        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.timeout.connect( self.cb_refreshMain)
        self.updateTimer.start( definitions.TIMEOUT_REFRESH)



    #
    # the central part
    #
    def prepareWidgets( self):
        self.centralWidget = QWidget()
        self.setCentralWidget( self.centralWidget)
        self.layout_v = QVBoxLayout()
        self.centralWidget.setLayout( self.layout_v)

        #
        # log widget, used by fillMotorList()
        #
        self.logWidget = QTextEdit()
        self.logWidget.setMinimumHeight( 200)
        self.logWidget.setReadOnly( 1)

        self.scrollArea = QScrollArea()
        self.scrollArea.setMinimumWidth( 800)
        if len( self.devices.allMotors) < 5:
            self.scrollArea.setMinimumHeight( 200)
        elif len( self.devices.allMotors) < 9:
            self.scrollArea.setMinimumHeight( 400)
        else:
            self.scrollArea.setMinimumHeight( 600)

        self.base = None
        #
        # fill-in the motors
        #
        self.fillMotorList()

        self.layout_v.addWidget( self.scrollArea)
        self.layout_v.addWidget( self.logWidget)
    #
    # the menubar
    #
    def prepareMenuBar( self):
        #
        # Menu Bar
        #
        self.menuBar = QMenuBar()
        self.setMenuBar( self.menuBar)

        #
        # File menu
        #
        self.fileMenu = self.menuBar.addMenu('&File')

        self.exitAction = QAction('E&xit', self)        
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect( QApplication.quit)
        self.fileMenu.addAction( self.exitAction)

        #
        # Tools menu
        #
        self.toolsMenu = self.menuBar.addMenu('&Tools')

        self.nxselectorAction = QAction('Nxselector', self)        
        self.nxselectorAction.triggered.connect( self.cb_launchNxselector)
        self.toolsMenu.addAction( self.nxselectorAction)


        self.pyspMonitorAction = QAction('pyspMonitor', self)        
        self.pyspMonitorAction.triggered.connect( self.cb_launchPyspMonitor)
        self.toolsMenu.addAction( self.pyspMonitorAction)

        #
        # SardanaMacroExecutor
        #
        self.macroExecutorAction = QAction('SardanaMacroExecutor', self)        
        self.macroExecutorAction.triggered.connect( self.cb_macroExecutor)
        self.toolsMenu.addAction( self.macroExecutorAction)

        self.jiveAction = QAction('jive', self)        
        self.jiveAction.triggered.connect( self.cb_launchJive)
        self.toolsMenu.addAction( self.jiveAction)

        self.astorAction = QAction('astor', self)        
        self.astorAction.triggered.connect( self.cb_launchAstor)
        self.toolsMenu.addAction( self.astorAction)

        self.mcaAction = QAction('MCA', self)        
        self.mcaAction.triggered.connect( self.cb_launchMCA)
        self.toolsMenu.addAction( self.mcaAction)
        #
        # PyMCA
        #
        self.pymcaAction = QAction('PyMCA', self)        
        self.pymcaAction.triggered.connect( self.cb_launchPyMCA)
        self.toolsMenu.addAction( self.pymcaAction)

        #
        self.motorMonitorAction = QAction('SardanaMotorMonitor', self)        
        self.motorMonitorAction.triggered.connect( self.cb_launchMotorMonitor)
        self.toolsMenu.addAction( self.motorMonitorAction)

        #self.toolsMenu.addAction( self.spectraAction)

        #
        # Files
        #
        self.filesMenu = self.menuBar.addMenu('Files')
        self.editOnlineXmlAction = QAction('online.xml', self)        
        self.editOnlineXmlAction.setStatusTip('Edit /online_dir/online.xml')
        self.editOnlineXmlAction.triggered.connect( self.cb_editOnlineXml)
        self.filesMenu.addAction( self.editOnlineXmlAction)

        self.editTangoDumpLisAction = QAction('TangoDump.lis', self)        
        self.editTangoDumpLisAction.setStatusTip('Edit /online_dir/TangoDump.lis')
        self.editTangoDumpLisAction.triggered.connect( self.cb_editTangoDumpLis)
        self.filesMenu.addAction( self.editTangoDumpLisAction)


        self.editGenFeaturesAction = QAction('general_features.py', self)  
        self.editGenFeaturesAction.setStatusTip('Edit ~/sardanaMacros/general_features.py (Hooks)')
        self.editGenFeaturesAction.triggered.connect( self.cb_editGenFeatures)
        self.filesMenu.addAction( self.editGenFeaturesAction)

        self.editMotorLogLisAction = QAction('motorLog.lis', self)        
        self.editMotorLogLisAction.setStatusTip('Edit /online_dir/MotorLogs/motorLog.lis')
        self.editMotorLogLisAction.triggered.connect( self.cb_editMotorLogLis)
        self.filesMenu.addAction( self.editMotorLogLisAction)

        self.editSardanaConfigAction = self.filesMenu.addAction(self.tr("SardanaConfig.py"))   
        self.editSardanaConfigAction.setStatusTip('Edit /online_dir/SardanaConfig.py (executed at the end of SardanaAIO.py)')
        self.editSardanaConfigAction.triggered.connect( self.cb_editSardanaConfig)

        self.editMacroServerRestartPostScriptAction = self.filesMenu.addAction(self.tr("MacroServerRestartPostScript"))   
        self.editMacroServerRestartPostScriptAction.setStatusTip('Edit file selected by MacroServerRestartPostScritp (MS-Env)')
        self.editMacroServerRestartPostScriptAction.triggered.connect( self.cb_editMacroServerRestartPostScript)

        self.edit00StartAction = QAction('00-start.py', self)  
        self.edit00StartAction.setStatusTip('Edit the Spock startup file')
        self.edit00StartAction.triggered.connect( self.cb_edit00Start)
        self.filesMenu.addAction( self.edit00StartAction)

        self.convertMacroServerPropertiesAction = QAction('MacroServer-Properties', self)  
        self.convertMacroServerPropertiesAction.setStatusTip('Convert /online_dir/MacroServer/macroserver.properties to a new version of /online_dir/MacroServer/msProperties.lis and launch an editor')
        self.convertMacroServerPropertiesAction.triggered.connect( self.cb_convertMacroServerProperties)
        self.filesMenu.addAction( self.convertMacroServerPropertiesAction)

        self.editMacroServerEnvironmentAction = QAction('MacroServer Environment', self)  
        self.editMacroServerEnvironmentAction.setStatusTip('Stores the current MacroServer environment in a temporary file and launches an editor')
        self.editMacroServerEnvironmentAction.triggered.connect( self.cb_editMacroServerEnvironment)
        self.filesMenu.addAction( self.editMacroServerEnvironmentAction)

        self.editIpythonLogAction = QAction('/online_dir/ipython_log.py', self)        
        self.editIpythonLogAction.triggered.connect( self.cb_editIpythonLog)
        self.filesMenu.addAction( self.editIpythonLogAction)

        self.editNexusSavesAction = QAction('/online_dir/nexusSaves/dir_current', self)        
        self.editNexusSavesAction.triggered.connect( self.cb_editNexusSaves)
        self.filesMenu.addAction( self.editNexusSavesAction)

        #
        # LogFiles
        #
        self.logFilesMenu = self.menuBar.addMenu('&LogFiles')
        self.fillLogFilesMenu()
        #
        # Misc
        #
        self.miscMenu = self.menuBar.addMenu('Misc')

        self.restartTimerAction = QAction('Restart refresh timer', self)        
        self.restartTimerAction.setStatusTip('Restart the timer that refreshes this widget')
        self.restartTimerAction.triggered.connect( self.cb_restartTimer)
        self.miscMenu.addAction( self.restartTimerAction)

        self.stopTimerAction = QAction('Stop refresh timer', self)        
        self.stopTimerAction.setStatusTip('Stop the timer that refreshes this widget')
        self.stopTimerAction.triggered.connect( self.cb_stopTimer)
        self.miscMenu.addAction( self.stopTimerAction)

        self.logToTempFileAction = QAction('Write log widget to file and edit it.', self)
        self.logToTempFileAction.triggered.connect( self.cb_logToTempFile)
        self.miscMenu.addAction( self.logToTempFileAction)

        #
        # selected MacroServer variables
        #
        self.macroServerAction = QAction('MacroServer (Selected Features)', self)        
        self.macroServerAction.setStatusTip('Selected MacroServer features')
        self.macroServerAction.triggered.connect( self.cb_msIfc)
        self.miscMenu.addAction( self.macroServerAction)
        #
        # print macro stats
        #
        self.printMacroStatsAction = QAction('Print macro stats', self)        
        self.printMacroStatsAction.setStatusTip('Print macro stats, according to directories')
        self.printMacroStatsAction.triggered.connect( self.cb_printMacroStats)
        self.miscMenu.addAction( self.printMacroStatsAction)
        #
        # show all devices
        #
        self.showAllDevicesAction = QAction('Show all devices', self)        
        self.showAllDevicesAction.setStatusTip('Show all devices, create file and edit')
        self.showAllDevicesAction.triggered.connect( self.cb_showAllDevices)
        self.miscMenu.addAction( self.showAllDevicesAction)
        #
        # checkECStatus
        #
        #self.checkECStatusAction = QAction('Check EC Status', self)        
        #self.checkECStatusAction.setStatusTip('Check Pool, Macroserver, Door, ActiveMntGrp')
        #self.checkECStatusAction.triggered.connect( self.cb_checkECStatus)
        #self.miscMenu.addAction( self.checkECStatusAction)
        #
        # Table
        #
        self.tableMenu = self.menuBar.addMenu('Table')

        self.motorTableAction = QAction('Motors', self)        
        self.motorTableAction.triggered.connect( self.cb_motorTable)
        self.tableMenu.addAction( self.motorTableAction)

        if len( self.devices.allAdcs) > 0 or len( self.devices.allDacs) > 0:
            self.adcDacTableAction = QAction('ADC/DACs', self)        
            self.adcDacTableAction.triggered.connect( self.cb_adcDacTable)
            self.tableMenu.addAction( self.adcDacTableAction)

        if len( self.devices.allCameras) > 0:
            self.cameraTableAction = QAction('Cameras', self)        
            self.cameraTableAction.triggered.connect( self.cb_cameraTable)
            self.tableMenu.addAction( self.cameraTableAction)

        if len( self.devices.allCounters) or \
           len( self.devices.allTangoAttrCtrls) > 0 or \
           len( self.devices.allTangoCounters) > 0:
            self.counterTableAction = QAction('Counters', self)        
            self.counterTableAction.triggered.connect( self.cb_counterTable)
            self.tableMenu.addAction( self.counterTableAction)

        if len( self.devices.allIRegs) > 0 or len(self.devices.allORegs) > 0:
            self.ioregTableAction = QAction('IORegs', self)        
            self.ioregTableAction.triggered.connect( self.cb_ioregTable)
            self.tableMenu.addAction( self.ioregTableAction)

        if len( self.devices.allMCAs) > 0:
            self.mcaTableAction = QAction('MCAs', self)        
            self.mcaTableAction.triggered.connect( self.cb_mcaTable)
            self.tableMenu.addAction( self.mcaTableAction)

        if len( self.devices.allTDCs) > 0:
            self.tdcTableAction = QAction('TDCs', self)        
            self.tdcTableAction.triggered.connect( self.cb_tdcTable)
            self.tableMenu.addAction( self.tdcTableAction)

        if len( self.devices.allModuleTangos) > 0:
            self.moduleTangoTableAction = QAction('ModuleTango', self)        
            self.moduleTangoTableAction.triggered.connect( self.cb_moduleTangoTable)
            self.tableMenu.addAction( self.moduleTangoTableAction)

        if len( self.devices.allPiLCModules) > 0:
            self.PiLCModulesTableAction = QAction('PiLCModules', self)        
            self.PiLCModulesTableAction.triggered.connect( self.cb_PiLCModulesTable)
            self.tableMenu.addAction( self.PiLCModulesTableAction)

        if len( self.devices.allTimers) > 0:
            self.timerTableAction = QAction('Timers', self)        
            self.timerTableAction.triggered.connect( self.cb_timerTable)
            self.tableMenu.addAction( self.timerTableAction)

            self.timerExtraTableAction = QAction('Timers (extra widget)', self)        
            self.timerExtraTableAction.triggered.connect( self.cb_launchTimerExtra)
            self.tableMenu.addAction( self.timerExtraTableAction)

        if len( self.devices.allVfcAdcs) > 0:
            self.vfcadcTableAction = QAction('VFCADCs', self)        
            self.vfcadcTableAction.triggered.connect( self.cb_vfcadcTable)
            self.tableMenu.addAction( self.vfcadcTableAction)

        if len( self.devices.allMGs) > 0:
            self.mgTableAction = QAction('MGs', self)        
            self.mgTableAction.triggered.connect( self.cb_mgTable)
            self.tableMenu.addAction( self.mgTableAction)

        if len( self.devices.allDoors) > 0:
            self.doorTableAction = QAction('Doors', self)        
            self.doorTableAction.triggered.connect( self.cb_doorTable)
            self.tableMenu.addAction( self.doorTableAction)

        if len( self.devices.allMSs) > 0:
            self.msTableAction = QAction('Macroserver', self)        
            self.msTableAction.triggered.connect( self.cb_msTable)
            self.tableMenu.addAction( self.msTableAction)

        if len( self.devices.allPools) > 0:
            self.poolTableAction = QAction('Pools', self)        
            self.poolTableAction.triggered.connect( self.cb_poolTable)
            self.tableMenu.addAction( self.poolTableAction)

        self.macrosTableAction = QAction('Macros', self)        
        self.macrosTableAction.triggered.connect( self.cb_macrosTable)
        self.tableMenu.addAction( self.macrosTableAction)

        if len( self.devices.allNXSConfigServer) > 0:
            self.nxsConfigServerTableAction = QAction('NXSConfigServer', self)        
            self.nxsConfigServerTableAction.triggered.connect( self.cb_nxsConfigServerTable)
            self.tableMenu.addAction( self.nxsConfigServerTableAction)
            
        #
        # the activity menubar: help and activity
        #
        self.menuBarActivity = QMenuBar( self.menuBar)
        self.menuBar.setCornerWidget( self.menuBarActivity, QtCore.Qt.TopRightCorner)

        #
        # Help menu 
        #
        self.helpMenu = self.menuBarActivity.addMenu('Help')
        self.historyAction = self.helpMenu.addAction(self.tr("History"))
        self.historyAction.triggered.connect( self.cb_history)
        self.versionsAction = self.helpMenu.addAction(self.tr("Versions"))
        self.versionsAction.triggered.connect( self.cb_versions)
        self.fileNameAction = self.helpMenu.addAction(self.tr("__file__"))
        self.fileNameAction.triggered.connect( self.cb_fileName)
        self.colorCodeAction = self.helpMenu.addAction(self.tr("Color code"))
        self.colorCodeAction.triggered.connect( self.cb_colorCode)


        self.tkAction = QAction('TK', self, checkable = True)        
        self.tkAction.setStatusTip('If TK, emacs is the editor)')
        self.tkAction.triggered.connect( self.cb_tk)
        self.helpMenu.addAction( self.tkAction)

        self.activityIndex = 0
        self.activity = self.menuBarActivity.addMenu( "_")

    def cb_tk( self): 
        if self.tkAction.isChecked():
            self.tkFlag = True
        else:
            self.tkFlag = False
        return 

    def fillLogFilesMenu( self): 
        import glob
        #
        # MacroServer log files
        #
        logFiles = glob.glob( "/var/tmp/ds.log/MacroServer*.log")        
        logFiles.extend( glob.glob( "/tmp/tango-%s/MacroServer/%s/log.txt*" %  ( self.tangoUser, self.hostName)))
        logFiles.sort()

        for fl in logFiles:
            logFileAction = QAction( fl, self)  
            logFileAction.triggered.connect( self.make_logFileCb( fl))
            self.logFilesMenu.addAction( logFileAction)

        self.logFilesMenu.addSeparator()
        #
        # Pool log files
        #
        logFiles = glob.glob( "/var/tmp/ds.log/Pool*.log")        
        logFiles.extend( glob.glob( "/tmp/tango-%s/Pool/%s/log.txt*" %  ( self.tangoUser, self.hostName)))
        logFiles.sort()

        for fl in logFiles:
            logFileAction = QAction( fl, self)  
            logFileAction.triggered.connect( self.make_logFileCb( fl))
            self.logFilesMenu.addAction( logFileAction)

        self.logFilesMenu.addSeparator()

        #
        # all server logs
        #
        logFiles = glob.glob( "/var/tmp/ds.log/*.log")
        
        logFiles.sort()

        for fl in logFiles:
            if fl.find( '[') > 0 and fl.find( ']') > 0: 
                continue
            if fl.find( 'MacroServer') != -1: 
                continue
            if fl.find( 'Pool') != -1: 
                continue
            logFileAction = QAction( fl, self)  
            logFileAction.triggered.connect( self.make_logFileCb( fl))
            self.logFilesMenu.addAction( logFileAction)

    def findEditor( self):
        if self.tkFlag:
            argout = "emacs"
        else: 
            argout = HasyUtils.findEditor()                    
        return argout
    def make_logFileCb( self, fileName): 
        def cb():
            os.system( "%s %s&" % ( self.findEditor(), fileName))
            return 
        return cb

    def make_macroCb( self, macro): 
        def cb():
            import tempfile
            new_file, filename = tempfile.mkstemp( suffix='.py')
            file_path = HasyUtils.getMacroInfo( macro)[ 'file_path']
            inp = open( file_path, 'r')
            os.write(new_file, bytearray( "#\n", encoding='utf-8'))
            os.write(new_file, bytearray( "# below you find a copy of \n", encoding='utf-8'))
            os.write(new_file, bytearray( "#   %s\n" % file_path, encoding='utf-8'))
            os.write(new_file, bytearray( "#\n", encoding='utf-8'))
            for line in inp.readlines():
                os.write(new_file, bytearray( line, encoding='utf-8'))
            os.close(new_file)
            inp.close()
            os.system( "%s %s&" % ( self.findEditor(), filename))
            return 
        return cb
            
    def cb_launchTimerExtra( self): 
        self.w_timerExtra = tngAPI.timerWidget( self.logWidget, self.devices.allTimers, self)
        self.w_timerExtra.show()
        return self.w_timerExtra

    def cb_motorTable( self):
        self.fillMotorList()
        
    def cb_ioregTable( self):
        self.fillIORegs()
        
    def cb_adcDacTable( self):
        self.fillAdcDacs()
        
    def cb_cameraTable( self):
        self.fillCameras()
        
    def cb_PiLCModulesTable( self):
        self.fillPiLCModules()
        
    def cb_moduleTangoTable( self):
        self.fillModuleTangos()
        
    def cb_mcaTable( self):
        self.fillMCAs()
        
    def cb_tdcTable( self):
        self.fillTDCs()
        
    def cb_timerTable( self):
        self.fillTimers()
        
    def cb_counterTable( self):
        self.fillCounters()
        
    def cb_vfcadcTable( self):
        self.fillVfcAdcs()
        
    def cb_mgTable( self):
        self.fillMGs()
        
    def cb_doorTable( self):
        self.fillDoors()
        
    def cb_msTable( self):
        self.fillMSs()
        
    def cb_poolTable( self):
        self.fillPools()
                
    def cb_macrosTable( self):
        self.fillMacros()
        
    def cb_nxsConfigServerTable( self):
        self.fillNXSConfigServer()
        
    def cb_showAllDevices( self):
        self.devices.showAllDevices()
        return 
        
    def cb_checkECStatus( self):
        HasyUtils.checkECStatus( widget = self)
        return 

    def cb_tk( self): 
        if self.tkAction.isChecked():
            self.tkFlag = True
        else:
            self.tkFlag = False
        return 

    def cb_printMacroStats( self): 
        """
        Generate a statistic of Macros w.r.t to the directories mentioned in the MacroPath:
          /usr/lib/python3/dist-packages/sardana/sardana-macros/DESY_general
          /home/<user>/sardanaMacros
          /gpfs/local/sardanaMacros
          /bl_documents/sardanaMacros
          /usr/lib/python3/dist-packages/sardana/macroserver/macros
        """
        macros = HasyUtils.getMacroList()
        if macros is None: 
            self.logWidget.append( "no macros")
            return 

        macroDirs = HasyUtils.getDeviceProperty( HasyUtils.getMacroServerNames()[0], 'MacroPath')
        macroDirs.append( "/usr/lib/python3/dist-packages/sardana/macroserver/macros")
        dirHsh = {}
        for macroDir in macroDirs: 
            dirHsh[ macroDir] = 0
        
        self.logWidget.append( "Running through all macros. This may take some seconds.")
        self.app.processEvents()
        i = 0
        j = 0
        for macro in macros: 
            i += 1
            file_path = HasyUtils.getMacroInfo( macro)[ 'file_path']
            found = False
            for macroDir in macroDirs: 
                if file_path.find( macroDir) == 0:
                    dirHsh[ macroDir] += 1
                    found = True
                    break
            if not found:
                if j < 20: 
                    self.logWidget.append( "failed to identify %s" % file_path)
                    j += 1

            if i % 50 == 0: 
                self.logWidget.append( "at %d of %d" % ( i, len( macros)))
                self.app.processEvents()

        for k in list( dirHsh.keys()): 
            self.logWidget.append( "%s: %d" % ( k, dirHsh[k]))
        self.logWidget.append( "Total no. of macros %d " % ( len( macros)))
            
        return


    #
    # the closeEvent is called when the window is closed by 
    # clicking the X at the right-upper corner of the frame
    #
    def closeEvent( self, e):
        self.cb_closeMainMenu()
        #e.ignore()
    
    def cb_closeMainMenu( self):

        self.cb_stopMove()

        if self.app is not None: 
            for window in self.app.topLevelWidgets():
                window.close()

        PySpectra.close()
            
        if self.w_attr is not None:
            self.w_attr.close()
            self.w_attr = None

        if self.w_commands is not None: 
            self.w_commands.close()
            self.w_commands = None

        if self.w_encAttr is not None: 
            self.w_encAttr.close()
            self.w_encAttr = None

        if self.w_moveMotor is not None: 
            self.w_moveMotor.close()
            self.w_moveMotor = None

        if self.w_prop is not None: 
            self.w_prop.close()
            self.w_prop = None

        if self.w_timer is not None:
            self.w_timer.close()
            self.w_timer = None

        #if self.pyspGui: 
        #    self.pyspGui.close()
        #    self.pyspGui = None
        #
        # eventually 
        #
        #PySpectra.close()

        return 

    def cb_editOnlineXml( self):
        if not os.access( "/online_dir/online.xml", os.R_OK):
            QMessageBox.critical(self, 'Error', 
                                       "/online_dir/online.xml does not exist",
                                       QMessageBox.Ok)
            return
        os.system( "test -e /usr/local/bin/vrsn && /usr/local/bin/vrsn -s /online_dir/online.xml")
        os.system( "%s /online_dir/online.xml&" % self.findEditor())

    def cb_editTangoDumpLis( self):
        if not os.access( "/online_dir/TangoDump.lis", os.R_OK):
            QMessageBox.critical(self, 'Error', 
                                       "/online_dir/TangoDump.lis does not exist",
                                       QMessageBox.Ok)
            return
        
        os.system( "%s /online_dir/TangoDump.lis&" % self.findEditor())

    def cb_editMotorLogLis( self):
        if not os.access( "/online_dir/MotorLogs/motorLog.lis", os.R_OK):
            QMessageBox.critical(self, 'Error', 
                                       "/online_dir/MotorLogs/motorLog.lis does not exist",
                                       QMessageBox.Ok)
            return

        os.system( "%s /online_dir/MotorLogs/motorLog.lis&" % self.findEditor())

    def cb_editIpythonLog( self):
        if not os.access( "/online_dir/ipython_log.py", os.R_OK):
            QMessageBox.critical(self, 'Error', 
                                       "/online_dir/ipython_log.py does not exist",
                                       QMessageBox.Ok)
            return
        os.system( "%s /online_dir/ipython_log.py&" % self.findEditor())


    def cb_editNexusSaves( self):
        import glob
        logFiles = glob.glob( "/online_dir/nexusSaves/dir_current/*.lis")        
        for fName in logFiles: 
            if not os.access( fName, os.R_OK):
                QMessageBox.critical(self, 'Error', 
                                     "%s does not exist" % fName,
                                     QMessageBox.Ok)
                return
            self.logWidget.append( "Open %s" % fName)
            os.system( "%s %s&" % (self.findEditor(), fName))
        return 

    def cb_editSardanaConfig( self):
        if not os.access( "/online_dir/SardanaConfig.py", os.R_OK):
            QMessageBox.critical(self, 'Error', 
                                       "/online_dir/SardanaConfig.py does not exist",
                                       QMessageBox.Ok)
            return
        os.system( "%s /online_dir/SardanaConfig.py&" % self.findEditor())

    def cb_editMacroServerRestartPostScript( self):
        fName = HasyUtils.getEnv( "MacroServerRestartPostScript") 
        if fName is None: 
            QMessageBox.critical(self, 'Error', 
                                       "MacroServerRestartPostScript (MS-Env) does not exist",
                                       QMessageBox.Ok)
            return 
            
        if not os.access( fName, os.R_OK):
            QMessageBox.critical(self, 'Error', 
                                       "%s does not exist" % fName,
                                       QMessageBox.Ok)
            return
        os.system( "%s %s&" % (self.findEditor(), fName))

    def cb_editGenFeatures( self):
        home = os.getenv( "HOME")
        fName = "%s/sardanaMacros/general_features.py" % home
        if not os.access( fName, os.R_OK):
            QMessageBox.critical(self, 'Error', 
                                       "%s does not exist" % fName,
                                       QMessageBox.Ok)
            return
        os.system( "%s %s&" % ( self.findEditor(), fName))

    def cb_edit00Start( self):
        home = os.getenv( "HOME")
        fName = "%s/.ipython/profile_spockdoor/startup/00-start.py" % home
        if not os.access( fName, os.R_OK):
            QMessageBox.critical(self, 'Error', 
                                       "%s does not exist" % fName,
                                       QMessageBox.Ok)
            return
        os.system( "%s %s&" % ( self.findEditor(), fName))

    def cb_editMacroServerLogTxt( self):
            
        fName =  "/tmp/tango-%s/MacroServer/%s/log.txt" %  ( self.tangoUser, self.hostName)
        if not os.access( fName, os.R_OK):
            QMessageBox.critical(self, 'Error', 
                                       "%s does not exist" % fName,
                                       QMessageBox.Ok)
            return
        os.system( "%s %s&" % ( self.findEditor(), fName))

    def cb_editMacroServerLogLog( self):
            
        fName =  "/var/tmp/ds.log/MacroServer_%s.log" %  ( self.hostName)
        if not os.access( fName, os.R_OK):
            QMessageBox.critical(self, 'Error', 
                                       "%s does not exist" % fName,
                                       QMessageBox.Ok)
            return
        os.system( "%s %s&" % ( self.findEditor(), fName))

    def cb_editPoolLogTxt( self):

        fName =  "/tmp/tango-%s/Pool/%s/log.txt" %  ( self.tangoUser, self.hostName)
        if not os.access( fName, os.R_OK):
            QMessageBox.critical(self, 'Error', 
                                       "%s does not exist" % fName,
                                       QMessageBox.Ok)
            return
        os.system( "%s %s&" % ( self.findEditor(), fName))

    def cb_editPoolLogLog( self):

        fName =  "/var/tmp/ds.log/Pool_%s.log" %  ( self.hostName)
        if not os.access( fName, os.R_OK):
            QMessageBox.critical(self, 'Error', 
                                       "%s does not exist" % fName,
                                       QMessageBox.Ok)
            return
        os.system( "%s %s&" % ( self.findEditor(), fName))

    def convertMacroServerPropertiesNoEdit( self):
        '''
        creates a new version of the human readable file /online_dir/Macroserver/msProperties.lis
        this functionality has been put into a separate file to allow for a command line call.
        '''
        import tempfile
        import shelve

        print( "tngGuiClass: save old version of /online_dir/MacroServer/msProperties.lis") 
        os.system( "test -e /usr/local/bin/vrsn && /usr/local/bin/vrsn -s /online_dir/MacroServer/msProperties.lis")

        hsh = shelve.open('/online_dir/MacroServer/macroserver.properties')
        if sys.version.split( '.')[0] != '2': 
            hsh = dict( hsh)

        ret = HasyUtils.dct_print2str( hsh)

        new_file, filename = tempfile.mkstemp()
        if sys.version_info.major == 2:
            os.write(new_file, "#\n%s" % ret)
        else: 
            os.write(new_file, bytes( "#\n%s" % ret, 'utf-8'))
        os.close(new_file)

        print( "tngGuiClass: create new version of /online_dir/MacroServer/msProperties.lis") 
        os.system( "mv %s /online_dir/MacroServer/msProperties.lis" % ( filename))
        return True

    def cb_convertMacroServerProperties( self):
        '''
        creates a new version of the human readable file /online_dir/Macroserver/msProperties.lis
        and calls an EDITOR to open it
        '''
        if not self.convertMacroServerPropertiesNoEdit(): 
            return 
        os.system( "%s /online_dir/MacroServer/msProperties.lis&" % ( self.findEditor()))
        return 

    def cb_editMacroServerEnvironment( self):
        '''
        creates a temporary file containing the active MacroSerqver environment
        calls an EDITOR to open it
        
        '''
        import tempfile

        d = HasyUtils.getEnvDct()
        ret = HasyUtils.dct_print2str( d)

        new_file, filename = tempfile.mkstemp()
        
        if sys.version.split( '.')[0] == '2': 
            os.write(new_file, "#\nimport HasyUtils\nHasyUtils.setEnvDct(\n")
            os.write(new_file, "%s\n)" % ret)
        else: 
            os.write(new_file, bytes( "#\nimport HasyUtils\nHasyUtils.setEnvDct(\n", 'utf-8'))
            os.write(new_file, bytes( "%s\n)" % ret, 'utf-8'))
        os.close(new_file)

        os.system( "%s %s&" % ( self.findEditor(), filename))
        return 
        
    def cb_restartTimer( self):
        self.updateTimer.stop()
        self.updateTimer.start( definitions.TIMEOUT_REFRESH)
        
    def cb_stopTimer( self):
        self.updateTimer.stop()

    def cb_logToTempFile( self):
        fName = HasyUtils.createScanName( "smm") + ".lis"
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

    #
    # the status bar
    #
    def prepareStatusBar( self):
        #
        # Status Bar
        #
        self.statusBar = QStatusBar()
        self.setStatusBar( self.statusBar)

        self.stopMove = QPushButton(self.tr("&Stop Moves")) 
        self.stopMove.setToolTip( "Stop moving motors")
        self.statusBar.addWidget( self.stopMove) 
        self.stopMove.clicked.connect( self.cb_stopMove)
        self.stopMove.setShortcut( "Alt+s")

        self.stopMacro = QPushButton(self.tr("Stop Macro")) 
        self.stopMacro.setToolTip( "Execute StopMacro on all Doors")
        self.statusBar.addWidget( self.stopMacro) 
        self.stopMacro.clicked.connect( self.cb_stopMacro)

        self.restartMS = QPushButton(self.tr("Restart MacroServer")) 
        self.restartMS.setToolTip( "Restart the MacroServer")
        self.statusBar.addWidget( self.restartMS) 
        self.restartMS.clicked.connect( self.cb_restartMS)

        self.restartBoth = QPushButton(self.tr("Restart Both"))
        self.restartBoth.setToolTip( "Restart the MacroServer and Pool")
        self.statusBar.addWidget( self.restartBoth) 
        self.restartBoth.clicked.connect( self.cb_restartBoth)

        self.checkECStatus = QPushButton(self.tr("CheckEC"))
        self.checkECStatus.setToolTip('Check Pool, Macroserver, Door, ActiveMntGrp')
        self.statusBar.addWidget( self.checkECStatus) 
        self.checkECStatus.clicked.connect( self.cb_checkECStatus)
        #
        # Door
        #
        if self.doorProxies and len( self.doorProxies) > 0: 
            self.statusBar.addWidget( QLabel( "Door"))
            self.doorStateLabel = QLabel()
            self.doorStateLabel.setAlignment( QtCore.Qt.AlignCenter)
            self.doorStateLabel.setMinimumWidth( 60)
            self.statusBar.addWidget( self.doorStateLabel) # 'permanent' to shift it right
        #
        # MacroServer Ifc
        #
        #self.msIfc = QPushButton(self.tr("MacroServer")) 
        #self.msIfc.setToolTip( "Selected MacroServer variables")
        #self.statusBar.addPermanentWidget( self.msIfc) # 'permanent' to shift it right
        #self.msIfc.clicked.connect( self.cb_msIfc)

        #self.clear.setShortcut( "Alt+c")
        #
        # clear log widget
        #
        self.clear = QPushButton(self.tr("Clear")) 
        self.statusBar.addPermanentWidget( self.clear) # 'permanent' to shift it right
        self.clear.clicked.connect( self.cb_clear)
        #
        # exit
        #
        self.exit = QPushButton(self.tr("E&xit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( self.close)
        self.exit.setShortcut( "Alt+x")

    def cb_stopMove( self):
        for dev in self.devices.allMotors:
            if dev[ 'proxy'].state() == PyTango.DevState.MOVING:
                utils.execStopMove( dev)

    def cb_stopMacro( self):
        for p in self.doorProxies: 
            if p.state() != PyTango.DevState.ON:
                self.logWidget.append( "execute stopMacro on %s, state %s" % (p.name(), p.state()))
                p.StopMacro()
                startTime = time.time()
                self.logWidget.append( "stopMacro executed, waiting for Door to become ON")
                while p.State() != PyTango.DevState.ON: 
                    self.app.processEvents()
                    time.sleep( 0.1) 
                self.logWidget.append( "stopMacro executed, Door is ON, AFTER %gs" % (time.time() - startTime))
            else: 
                self.logWidget.append( "state of %s is already ON" % p.name())

        return 

    def cb_restartMS( self):
        self.logWidget.append( "restarting the MacroServer will take a few seconds")
        self.logWidget.append( "  wait for the Door state to become ON again")
        os.system( "/usr/bin/SardanaRestartMacroServer.py -x &")

        return 

    def cb_restartBoth( self):
        self.logWidget.append( "restarting the MacroServer and Pool will take a few seconds")
        self.logWidget.append( "  wait for the Door state to become ON again")
        os.system( "/usr/bin/SardanaRestartBoth.py -x &")

        return 

    def cb_msIfc( self):
        self.ms = macroServerIfc.MacroServerIfc( self.logWidget, self)
        self.ms.show()

    def cb_launchNxselector( self):
        os.system( "/usr/bin/nxselector &")

    def cb_launchMotorMonitor( self):
        os.system( "/usr/bin/SardanaMotorMonitor.py &")

    def cb_launchPyMCA( self):
        os.system( "pymca")

    def cb_macroExecutor( self):
        self.macroExecutor = macroExecutorClass.MacroExecutor( self.logWidget, self, self.app)
        self.macroExecutor.show()

    #
    #def cb_launchSardanaMonitor( self):
    #    os.system( "/usr/bin/SardanaMonitor.py &")

    def cb_launchSpock( self):
        display = os.getenv( "DISPLAY")
        if display == ':0':
            sts = os.system( "gnome-terminal -e /usr/bin/spock -t spock &")
        else:
            if os.path.exists( "/usr/bin/terminator"):
                sts = os.system( "terminator -e /usr/bin/spock &")
            else: 
                sts = os.system( "xterm -bg white -fg black -e /usr/bin/spock &")
        return 

    #def cb_launchPyspGui( self):
    #    #
    #    # one pyspViewer GUI is enough
    #    #
    #    if self.pyspGui is None: 
    #        self.pyspGui = PySpectra.pySpectraGuiClass.pySpectraGui()
    #        self.pyspGui.show()
    #    else: 
    #        self.pyspGui.raise_()
    #        self.pyspGui.activateWindow()
    #    return 

    def cb_launchMCA( self): 
        self.mcaWidget = mcaWidget.mcaWidget( devices = self.devices, 
                                              logWidget = self.logWidget, 
                                              app = None, parent = self)
        self.mcaWidget.show()
        
    def cb_launchPyspMonitor( self):
        os.system( "/usr/bin/pyspMonitor.py &")
        
    def cb_launchJive( self):
        os.system( "/usr/bin/jive &")

    def cb_launchAstor( self):
        os.system( "/usr/bin/astor &")

    def __del__( self):
        pass

    def cb_clear( self):
        self.logWidget.clear()

    def cb_history(self):
        w = helpBox.HelpBox(self, self.tr("HelpWidget"), self.tr(
            "<h3> Version history</h3>"
            "<ul>"
            "<li> 01.10.2024: Addes saved Nexus files to Files menu</li>"
            "<li> 12.01.2023: Added tablet mode, TngGui.py --tablet</li>"
            "<li> 20.12.2021: Created a table for Macros</li>"
            "<li> 25.11.2021: Added limaccd as camera</li>"
            "<li> 12.11.2021: Files menu, added ~/sardanaMacro/general_features.py </li>"
            "<li> 23.07.2021: Command line option: --mp creates creates a new version of /online_dir/MacroServer/msProperties.lis </li>"
            "<li> 22.07.2021: Files - MacroServer-Properties creates a new version of /online_dir/MacroServer/msProperties.lis </li>"
            "<li> 13.06.2019: Attributes and properties available for various devices </li>"
            "<li> 06.06.2019: Color orange for status == DISABLE (e.g. undulator) </li>"
            "<li> 11.06.2018: Pool motors not appearing in online.xml are included (e.g.: exp_dmy01, e6cctrl_h) </li>"
            "<li> 11.06.2018: Signal can be without timer </li>"
            "<li> 11.06.2018: tangoattributectctrl can be used as signal </li>"
            "<li> 11.04.2018: EDITOR online.xml </li>"
            "<li> 10.04.2018: Selected MacroServer Variables </li>"
            "<li> 23.03.2018: vfcadcs and vcexecutors can be signal counters </li>"
            "</ul>"
                ))
        w.show()

    def cb_versions(self):
        QMessageBox.about(self, self.tr("Help Versions"), self.tr(
                "<h3> Versions</h3>"
                "<br> TngGui: %s"
                "<br> QtGui: %s" % ( HasyUtils.getPackageVersion( "python3-tnggui"), str( QtGui.__name__))))

    def cb_fileName(self):
        self.logWidget.append( "File name: %s" % __file__)

    def cb_colorCode( self):
        w = helpBox.HelpBox( self, title = self.tr("Help Update Rate"), text = self.tr(
            "<h3>Color Code</h3>"
            "<ul>"
            "<li> blue    MOVING"
            "<li> green   OK"
            "<li> magenta DISABLE (position) "
            "<li> red     ALARM or Upper/lower limit"
            "</ul>"
                ))
        w.show()

    def fillMotorList( self):

        if self.base is not None:
            self.base.destroy( True, True)
        self.base = QWidget()
        layout_grid = QGridLayout()
        
        layout_grid.addWidget( QLabel( "Alias"), 0, 0)
        layout_grid.addWidget( QLabel( "Position"), 0, 1)
        layout_grid.addWidget( QLabel( "Min"), 0, 2)
        layout_grid.addWidget( QLabel( "Max"), 0, 3)
        layout_grid.addWidget( QLabel( "Module"), 0, 4)
        layout_grid.addWidget( QLabel( "DeviceName"), 0, 5)

        count = 1
        hndlr = signal.getsignal( signal.SIGALRM)
        signal.signal( signal.SIGALRM, self.handlerALRM)
        for dev in self.devices.allMotors:
            #print( "connecting to %s" % dev[ 'name'])
            signal.alarm( 2)
            try:
                b = utils.QPushButtonTK(self.tr("%s" % dev[ 'name'])) 
                b.setToolTip( "MB-1: move menu\nMB-2: attributes (oms58, dac, motor_tango)\nMB-3: encAttributes (if FlagEncoder)")
                
                b.mb1.connect( self.make_cb_move( dev, self.logWidget))
                b.mb2.connect( self.make_cb_attributes( dev, self.logWidget))
                b.mb3.connect( self.make_cb_mb3( dev, self.logWidget))
                layout_grid.addWidget( b, count, 0)
                #
                # position
                #
                # Note: we have to store the widget in dev, not in self because
                #       we have many of them
                #
                dev[ 'w_pos'] = QLabel( "0.0")
                dev[ 'w_pos'].setObjectName( dev['name'])
                dev[ 'w_pos'].setFixedWidth( definitions.POSITION_WIDTH)
                dev[ 'w_pos'].setFrameStyle( QFrame.Panel | QFrame.Sunken)
                layout_grid.addWidget( dev[ 'w_pos'], count, 1 )
                #
                # unitlimitmin, ~max
                #
                dev[ 'w_unitlimitmin'] = QLabel( "0.0")
                dev[ 'w_unitlimitmin'].setFixedWidth( definitions.POSITION_WIDTH)
                dev[ 'w_unitlimitmin'].setFrameStyle( QFrame.Panel | QFrame.Sunken)
                dev[ 'w_unitlimitmax'] = QLabel( "0.0")
                dev[ 'w_unitlimitmax'].setFixedWidth( definitions.POSITION_WIDTH)
                dev[ 'w_unitlimitmax'].setFrameStyle( QFrame.Panel | QFrame.Sunken)
                layout_grid.addWidget( dev[ 'w_unitlimitmin'], count, 2 )
                layout_grid.addWidget( dev[ 'w_unitlimitmax'], count, 3 )
                #
                # module
                #
                moduleName = QLabel()
                moduleName.setText( "%s" % (dev['module']))
                moduleName.setAlignment( QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)
                layout_grid.addWidget( moduleName, count, 4 )
                #
                # device name
                #
                devName = QLabel()
                devName.setText( "%s/%s" % (dev['hostname'], dev['device']))
                devName.setAlignment( QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)
                layout_grid.addWidget( devName, count, 5 )

                count += 1
                    
            except utils.TMO as e:
                print( "fillMotorList: failed to connect to %s" % dev[ 'name'])
                del dev
            signal.alarm(0)
        signal.signal( signal.SIGALRM, hndlr)
        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshMotors

    def fillIORegs( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        layout_grid.addWidget( QLabel( "Alias"), 0, 0)
        layout_grid.addWidget( QLabel( "Value"), 0, 1)
        layout_grid.addWidget( QLabel( "Module"), 0, 2)
        layout_grid.addWidget( QLabel( "DeviceName"), 0, 3)

        #
        # <device>
        # <name>d1_ireg01</name>
        # <type>input_register</type>
        # <module>sis3610</module>
        # <device>p09/register/d1.in01</device>
        # <control>tango</control>
        # <hostname>haso107d1:10000</hostname>
        # <channel>1</channel>
        # </device>
        #
        count = 1
        for dev in self.devices.allIRegs:
            aliasName = utils.QPushButtonTK( dev['name'])
            aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
            aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
            layout_grid.addWidget( aliasName, count, 0)

            dev[ 'w_value'] = QLabel( "0")
            dev[ 'w_value'].setFixedWidth( 50)
            dev[ 'w_value'].setFrameStyle( QFrame.Panel | QFrame.Sunken)
            layout_grid.addWidget( dev[ 'w_value'], count, 1)

            moduleName = QLabel()
            moduleName.setText( "%s" % (dev['module']))
            moduleName.setAlignment( QtCore.Qt.AlignLeft)
            moduleName.setFixedWidth( definitions.POSITION_WIDTH)
            layout_grid.addWidget( moduleName, count, 2 )
            #
            # device name
            #
            devName = QLabel()
            devName.setText( "%s/%s" % (dev['hostname'], dev['device']))
            devName.setAlignment( QtCore.Qt.AlignLeft)
            layout_grid.addWidget( devName, count, 3 )
            
            count += 1

        for dev in self.devices.allORegs:
            aliasName = utils.QPushButtonTK(self.tr("%s" % dev[ 'name'])) 
            aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
            aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
            layout_grid.addWidget( aliasName, count, 0)

            dev[ 'w_value'] = utils.QPushButtonTK( dev['name'])
            dev[ 'w_value'].setToolTip( "MB-1: toggle ouput state")
            dev[ 'w_value'].mb1.connect( self.make_cb_oreg( dev, self.logWidget))
            dev[ 'w_value'].setFixedWidth( 50)
            layout_grid.addWidget( dev[ 'w_value'], count, 1)

            moduleName = QLabel()
            moduleName.setText( "%s" % (dev['module']))
            moduleName.setAlignment( QtCore.Qt.AlignLeft)
            moduleName.setFixedWidth( definitions.POSITION_WIDTH)
            layout_grid.addWidget( moduleName, count, 2 )
            #
            # device name
            #
            devName = QLabel()
            devName.setText( "%s/%s" % (dev['hostname'], dev['device']))
            devName.setAlignment( QtCore.Qt.AlignLeft)
            layout_grid.addWidget( devName, count, 3 )
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshIORegs

    def fillAdcDacs( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        layout_grid.addWidget( QLabel( "Alias"), 0, 0)
        layout_grid.addWidget( QLabel( "Value"), 0, 1)
        layout_grid.addWidget( QLabel( "Module"), 0, 2)
        layout_grid.addWidget( QLabel( "DeviceName"), 0, 3)

        #
        # <device>
        # <name>d1_ireg01</name>
        # <type>input_register</type>
        # <module>sis3610</module>
        # <device>p09/register/d1.in01</device>
        # <control>tango</control>
        # <hostname>haso107d1:10000</hostname>
        # <channel>1</channel>
        # </device>
        #
        count = 1
        for dev in self.devices.allAdcs:
            aliasName = utils.QPushButtonTK( dev['name'])
            aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
            aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
            layout_grid.addWidget( aliasName, count, 0)

            dev[ 'w_value'] = QLabel( "0")
            dev[ 'w_value'].setFixedWidth( definitions.POSITION_WIDTH)
            dev[ 'w_value'].setFrameStyle( QFrame.Panel | QFrame.Sunken)
            layout_grid.addWidget( dev[ 'w_value'], count, 1)

            moduleName = QLabel()
            moduleName.setText( "%s" % (dev['module']))
            moduleName.setAlignment( QtCore.Qt.AlignLeft)
            moduleName.setFixedWidth( definitions.POSITION_WIDTH)
            layout_grid.addWidget( moduleName, count, 2 )
            #
            # device name
            #
            devName = QLabel()
            devName.setText( "%s/%s" % (dev['hostname'], dev['device']))
            devName.setAlignment( QtCore.Qt.AlignLeft)
            layout_grid.addWidget( devName, count, 3 )
            
            count += 1

        for dev in self.devices.allDacs:
            aliasName = utils.QPushButtonTK( dev['name'])
            aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
            aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
            layout_grid.addWidget( aliasName, count, 0)

            dev[ 'w_value'] = utils.QPushButtonTK( dev['name'])
            dev[ 'w_value'].setToolTip( "MB-2: change voltage")
            dev[ 'w_value'].mb1.connect( self.make_cb_dac( dev, self.logWidget))
            layout_grid.addWidget( dev[ 'w_value'], count, 1)

            moduleName = QLabel()
            moduleName.setText( "%s" % (dev['module']))
            moduleName.setAlignment( QtCore.Qt.AlignLeft)
            moduleName.setFixedWidth( definitions.POSITION_WIDTH)
            layout_grid.addWidget( moduleName, count, 2 )
            #
            # device name
            #
            devName = QLabel()
            devName.setText( "%s/%s" % (dev['hostname'], dev['device']))
            devName.setAlignment( QtCore.Qt.AlignLeft)
            layout_grid.addWidget( devName, count, 3 )
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshAdcDacs

    def fillCameras( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        layout_grid.addWidget( QLabel( "Alias"), 0, 0)
        layout_grid.addWidget( QLabel( "Value"), 0, 1)
        layout_grid.addWidget( QLabel( "Module"), 0, 2)
        layout_grid.addWidget( QLabel( "DeviceName"), 0, 3)
        #
        # <device>
        # <name>lmbd</name>
        # <sardananame>lmbd</sardananame>
        # <type>DETECTOR</type>
        # <module>lambda</module>
        # <device>p23/lambda/01</device>
        # <control>tango</control>
        # <hostname>hasep23oh:10000</hostname>
        # </device>
        #
        count = 1
        for dev in self.devices.allCameras:
            aliasName = utils.QPushButtonTK( dev['name'])
            aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
            aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
            layout_grid.addWidget( aliasName, count, 0)

            moduleName = QLabel()
            moduleName.setText( "%s" % (dev['module']))
            moduleName.setAlignment( QtCore.Qt.AlignLeft)
            moduleName.setFixedWidth( definitions.POSITION_WIDTH)
            layout_grid.addWidget( moduleName, count, 1 )
            #
            # device name
            #
            devName = QLabel()
            devName.setText( "%s/%s" % (dev['hostname'], dev['device']))
            devName.setAlignment( QtCore.Qt.AlignLeft)
            layout_grid.addWidget( devName, count, 2 )
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshCameras

    def fillPiLCModules( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        layout_grid.addWidget( QLabel( "Alias"), 0, 0)
        layout_grid.addWidget( QLabel( "Value"), 0, 1)
        layout_grid.addWidget( QLabel( "Module"), 0, 2)
        layout_grid.addWidget( QLabel( "DeviceName"), 0, 3)
        #
        # <device>
        # <name>lmbd</name>
        # <sardananame>lmbd</sardananame>
        # <type>DETECTOR</type>
        # <module>lambda</module>
        # <device>p23/lambda/01</device>
        # <control>tango</control>
        # <hostname>hasep23oh:10000</hostname>
        # </device>
        #
        count = 1
        for dev in self.devices.allPiLCModules:
            aliasName = utils.QPushButtonTK( dev['name'])
            aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
            aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
            layout_grid.addWidget( aliasName, count, 0)

            moduleName = QLabel()
            moduleName.setText( "%s" % (dev['module']))
            moduleName.setAlignment( QtCore.Qt.AlignLeft)
            moduleName.setFixedWidth( definitions.POSITION_WIDTH)
            layout_grid.addWidget( moduleName, count, 1 )
            #
            # device name
            #
            devName = QLabel()
            devName.setText( "%s/%s" % (dev['hostname'], dev['device']))
            devName.setAlignment( QtCore.Qt.AlignLeft)
            layout_grid.addWidget( devName, count, 2 )
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshPiLCModules

    def fillModuleTangos( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        layout_grid.addWidget( QLabel( "Alias"), 0, 0)
        layout_grid.addWidget( QLabel( "Value"), 0, 1)
        layout_grid.addWidget( QLabel( "Module"), 0, 2)
        layout_grid.addWidget( QLabel( "DeviceName"), 0, 3)
        count = 1
        for dev in self.devices.allModuleTangos:
            aliasName = utils.QPushButtonTK( dev['name'])
            aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
            aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
            layout_grid.addWidget( aliasName, count, 0)

            moduleName = QLabel()
            moduleName.setText( "%s" % (dev['module']))
            moduleName.setAlignment( QtCore.Qt.AlignLeft)
            moduleName.setFixedWidth( definitions.POSITION_WIDTH)
            layout_grid.addWidget( moduleName, count, 1 )
            #
            # device name
            #
            devName = QLabel()
            devName.setText( "%s/%s" % (dev['hostname'], dev['device']))
            devName.setAlignment( QtCore.Qt.AlignLeft)
            layout_grid.addWidget( devName, count, 2 )
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshModuleTangos

    def fillTimers( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        layout_grid.addWidget( QLabel( "Alias"), 0, 0)
        layout_grid.addWidget( QLabel( "Value"), 0, 1)
        layout_grid.addWidget( QLabel( "Module"), 0, 2)
        layout_grid.addWidget( QLabel( "DeviceName"), 0, 3)
        count = 1
        for dev in self.devices.allTimers:
            aliasName = utils.QPushButtonTK( dev['name'])
            aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
            aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
            layout_grid.addWidget( aliasName, count, 0)

            moduleName = QLabel()
            moduleName.setText( "%s" % (dev['module']))
            moduleName.setAlignment( QtCore.Qt.AlignLeft)
            moduleName.setFixedWidth( definitions.POSITION_WIDTH)
            layout_grid.addWidget( moduleName, count, 1 )
            #
            # device name
            #
            devName = QLabel()
            devName.setText( "%s/%s" % (dev['hostname'], dev['device']))
            devName.setAlignment( QtCore.Qt.AlignLeft)
            layout_grid.addWidget( devName, count, 2 )
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshTimers

    def fillMCAs( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        layout_grid.addWidget( QLabel( "Alias"), 0, 0)
        layout_grid.addWidget( QLabel( "Module"), 0, 1)
        layout_grid.addWidget( QLabel( "DeviceName"), 0, 2)

        #
        # <device>
        # <name>d1_mca01</name>
        # <type>mca</type>
        # <module>mca_8701</module>
        # <device>p09/mca/d1.01</device>
        # <control>tango</control>
        # <hostname>haso107d1:10000</hostname>
        # <channel>1</channel>
        # </device>
        #
        count = 1
        for dev in self.devices.allMCAs:
            if dev[ 'module'].lower() == 'mca_8701':
                aliasName = utils.QPushButtonTK( dev['name'])
                aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
                aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
                aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
                aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
                layout_grid.addWidget( aliasName, count, 0)
            elif dev[ 'module'].lower() == 'sis3302':
                aliasName = utils.QPushButtonTK( dev['name'])
                aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
                aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
                aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
                aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
                layout_grid.addWidget( aliasName, count, 0)

            moduleName = QLabel()
            moduleName.setText( "%s" % (dev['module']))
            moduleName.setAlignment( QtCore.Qt.AlignLeft)
            moduleName.setFixedWidth( definitions.POSITION_WIDTH)
            layout_grid.addWidget( moduleName, count, 1 )
            #
            # device name
            #
            devName = QLabel()
            devName.setText( "%s/%s" % (dev['hostname'], dev['device']))
            devName.setAlignment( QtCore.Qt.AlignLeft)
            layout_grid.addWidget( devName, count, 2 )
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshMCAs

    def fillTDCs( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        layout_grid.addWidget( QLabel( "Alias"), 0, 0)
        layout_grid.addWidget( QLabel( "Module"), 0, 1)
        layout_grid.addWidget( QLabel( "DeviceName"), 0, 2)

        # <device>
        # <name>tdc_01</name>
        # <type>tdc</type>
        # <module>hydraharp400</module>
        # <device>slm/hydraharp400/lab.01</device>
        # <control>tango</control>
        # <hostname>hasx013slmlxctrl:10000</hostname>
        # </device>
        #
        count = 1
        for dev in self.devices.allTDCs:
            if dev[ 'module'].lower() == 'hydraharp400':
                aliasName = utils.QPushButtonTK( dev['name'])
                aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
                aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
                aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
                aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
                layout_grid.addWidget( aliasName, count, 0)

            moduleName = QLabel()
            moduleName.setText( "%s" % (dev['module']))
            moduleName.setAlignment( QtCore.Qt.AlignLeft)
            moduleName.setFixedWidth( definitions.POSITION_WIDTH)
            layout_grid.addWidget( moduleName, count, 1 )
            #
            # device name
            #
            devName = QLabel()
            devName.setText( "%s/%s" % (dev['hostname'], dev['device']))
            devName.setAlignment( QtCore.Qt.AlignLeft)
            layout_grid.addWidget( devName, count, 2 )
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshTDCs

    def fillVfcAdcs( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        count = 0
        layout_grid.addWidget( QLabel( "Alias"), count, 0)
        layout_grid.addWidget( QLabel( "Counts"), count, 1)
        layout_grid.addWidget( QLabel( "Reset"), count, 2)
        layout_grid.addWidget( QLabel( "Module"), count, 4)
        layout_grid.addWidget( QLabel( "DeviceName"), count, 5)
        count += 1

        for dev in self.devices.allVfcAdcs:
            dev[ 'w_aliasName'] = utils.QPushButtonTK( dev['name'])
            dev[ 'w_aliasName'].setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            dev[ 'w_aliasName'].mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            dev[ 'w_aliasName'].mb2.connect( self.make_cb_commands( dev, self.logWidget))
            dev[ 'w_aliasName'].mb3.connect( self.make_cb_properties( dev, self.logWidget))
            
            layout_grid.addWidget( dev[ 'w_aliasName'], count, 0)

            dev[ 'w_counts'] = QLabel()
            dev[ 'w_counts'].setFixedWidth( definitions.POSITION_WIDTH)
            layout_grid.addWidget( dev[ 'w_counts'], count, 1)

            dev[ 'w_reset'] = utils.QPushButtonTK( 'Reset')
            dev[ 'w_reset'].setToolTip( "MB-1: reset counter")
            dev[ 'w_reset'].mb1.connect( self.make_cb_resetCounter( dev, self.logWidget))
            layout_grid.addWidget( dev[ 'w_reset'], count, 2)

            moduleName = QLabel()
            moduleName.setText( "%s" % (dev['module']))
            moduleName.setAlignment( QtCore.Qt.AlignLeft)
            moduleName.setFixedWidth( definitions.POSITION_WIDTH)
            layout_grid.addWidget( moduleName, count, 4 )
            #
            # device name
            #
            devName = QLabel()
            devName.setText( "%s/%s" % (dev['hostname'], dev['device']))
            devName.setAlignment( QtCore.Qt.AlignLeft)
            layout_grid.addWidget( devName, count, 5 )
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshVfcAdcs

    def fillCounters( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        count = 0
        layout_grid.addWidget( QLabel( "Alias"), count, 0)
        layout_grid.addWidget( QLabel( "Counts"), count, 1)
        layout_grid.addWidget( QLabel( "Reset"), count, 2)
        layout_grid.addWidget( QLabel( "Module"), count, 4)
        layout_grid.addWidget( QLabel( "DeviceName"), count, 5)
        count += 1

        for dev in self.devices.allCounters + \
            self.devices.allTangoAttrCtrls + \
            self.devices.allTangoCounters:

            aliasName = utils.QPushButtonTK( dev['name'])
            aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
            aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
            layout_grid.addWidget( aliasName, count, 0)
            #
            #dev[ 'w_aliasName'] = QLabel( dev['name'])
            #layout_grid.addWidget( dev[ 'w_aliasName'], count, 0)

            dev[ 'w_counts'] = QLabel()
            dev[ 'w_counts'].setFixedWidth( definitions.POSITION_WIDTH)
            layout_grid.addWidget( dev[ 'w_counts'], count, 1)

            dev[ 'w_reset'] = utils.QPushButtonTK( 'Reset')
            dev[ 'w_reset'].setToolTip( "MB-1: reset counter")
            dev[ 'w_reset'].mb1.connect( self.make_cb_resetCounter( dev, self.logWidget))
            layout_grid.addWidget( dev[ 'w_reset'], count, 2)

            moduleName = QLabel()
            moduleName.setText( "%s" % (dev['module']))
            moduleName.setAlignment( QtCore.Qt.AlignLeft)
            moduleName.setFixedWidth( definitions.POSITION_WIDTH)
            layout_grid.addWidget( moduleName, count, 4 )
            #
            # device name
            #
            devName = QLabel()
            devName.setText( "%s/%s" % (dev['hostname'], dev['device']))
            devName.setAlignment( QtCore.Qt.AlignLeft)
            layout_grid.addWidget( devName, count, 5 )
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshCounters

    def fillMGs( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        layout_grid.addWidget( QLabel( "Alias"), 0, 0)

        activeMntGrp = HasyUtils.getEnv( 'ActiveMntGrp')
        self.mgAliases = HasyUtils.getMgAliases()
        count = 1
        self.MgEntries = []
        for dev in self.devices.allMGs:
            aliasName = utils.QPushButtonTK( dev['name'])
            if dev[ 'name'] == activeMntGrp: 
                aliasName.setStyleSheet( "color: blue")
            self.MgEntries.append( aliasName)
            aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
            aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
            layout_grid.addWidget( aliasName, count, 0)
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshMGs
        return 

    def fillDoors( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        layout_grid.addWidget( QLabel( "Name"), 0, 0)
        count = 1
        for dev in self.devices.allDoors:
            aliasName = utils.QPushButtonTK( dev['name'])
            aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
            aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
            layout_grid.addWidget( aliasName, count, 0)
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshDoors

    def fillMSs( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        layout_grid.addWidget( QLabel( "Name"), 0, 0)
        count = 1
        for dev in self.devices.allMSs:
            aliasName = utils.QPushButtonTK( dev['name'])
            aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
            aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
            layout_grid.addWidget( aliasName, count, 0)
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshMSs

    def fillPools( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        layout_grid.addWidget( QLabel( "Name"), 0, 0)
        count = 1
        for dev in self.devices.allPools:
            aliasName = utils.QPushButtonTK( dev['name'])
            aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
            aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
            layout_grid.addWidget( aliasName, count, 0)
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshPools

    def fillMacros( self):
        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        macros = HasyUtils.getMacroList()
        if macros is None: 
            return 
        macros.sort()

        NoOfCols = 4
        while len( macros) % NoOfCols != 0: 
            macros.append( "dummy")
        
        layout_grid.addWidget( QLabel( "Macros"), 0, 0)
        count = 1
        tableSize = int( len( macros) / NoOfCols)
        for i in range( tableSize): 
            for j in range( NoOfCols): 
                if macros[i+j*tableSize] != "dummy": 
                    macroName = utils.QPushButtonTK( macros[i+j*tableSize])
                    macroName.setToolTip( "MB-1: edit a copy of the macro")
                    macroName.mb1.connect( self.make_macroCb( macros[i+j*tableSize]))
                    layout_grid.addWidget( macroName, count, j + 0)
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshMacros

    def fillNXSConfigServer( self):

        if self.base is not None:
            self.base.destroy( True, True)

        self.base = QWidget()
        layout_grid = QGridLayout()

        layout_grid.addWidget( QLabel( "Name"), 0, 0)
        count = 1
        for dev in self.devices.allNXSConfigServer:
            aliasName = utils.QPushButtonTK( dev['name'])
            aliasName.setToolTip( "MB-1: Attributes\nMB-2: Commands\nMB-3: Properties")
            aliasName.mb1.connect( self.make_cb_attributes( dev, self.logWidget))
            aliasName.mb2.connect( self.make_cb_commands( dev, self.logWidget))
            aliasName.mb3.connect( self.make_cb_properties( dev, self.logWidget)) 
            layout_grid.addWidget( aliasName, count, 0)
            
            count += 1

        self.base.setLayout( layout_grid)
        self.scrollArea.setWidget( self.base)
        self.refreshFunc = self.refreshNXSConfigServer
        

    def cb_refreshMain( self):

        if self.isMinimized(): 
            return
        
        self.activityIndex += 1
        if self.activityIndex > (len( definitions.ACTIVITY_SYMBOLS) - 1):
            self.activityIndex = 0
        self.activity.setTitle( definitions.ACTIVITY_SYMBOLS[ self.activityIndex])
        self.updateTimer.stop()

        self.refreshFunc()


        if self.doorProxies and len( self.doorProxies) > 0: 
            try: 
                state = self.doorProxies[0].state()
                if state == PyTango.DevState.MOVING:
                    self.doorStateLabel.setText( "MOVING")
                    self.doorStateLabel.setStyleSheet( "background-color:%s;" % definitions.BLUE_MOVING)
                elif state == PyTango.DevState.RUNNING:
                    self.doorStateLabel.setText( "RUNNING")
                    self.doorStateLabel.setStyleSheet( "background-color:%s;" % definitions.BLUE_MOVING)
                elif state == PyTango.DevState.ON:
                    self.doorStateLabel.setText( "ON")
                    self.doorStateLabel.setStyleSheet( "background-color:%s;" % definitions.GREEN_OK)
                elif state == PyTango.DevState.DISABLE:
                    self.doorStateLabel.setText( "DISABLE")
                    self.doorStateLabel.setStyleSheet( "background-color:%s;" % definitions.MAGENTA_DISABLE)
                elif state == PyTango.DevState.ALARM:
                    self.doorStateLabel.setText( "ALARM")
                    self.doorStateLabel.setStyleSheet( "background-color:%s;" % definitions.MAGENTA_DISABLE)
                else:
                    self.doorStateLabel.setText( repr( state))
                    self.doorStateLabel.setStyleSheet( "background-color:%s;" % definitions.RED_ALARM)
            except: 
                    self.doorStateLabel.setText( "Offline")
                    self.doorStateLabel.setStyleSheet( "background-color:%s;" % definitions.RED_ALARM)


        self.updateTimer.start( definitions.TIMEOUT_REFRESH)

        return 

    def refreshMotors( self):
        hndlr = signal.getsignal( signal.SIGALRM)
        signal.signal( signal.SIGALRM, self.handlerALRM)
        #
        # for the old OmsVme58 cards, 1s is not enough
        #
        signal.alarm( 2)
        self.updateCount += 1
        try:
            for dev in self.devices.allMotors:
                if dev[ 'flagOffline']:
                    continue
                if dev[ 'w_pos'].visibleRegion().isEmpty():
                    continue
                #
                # see, if state() responds. If not ignore the motor
                #
                try:
                    sts = dev[ 'proxy'].state()
                except Exception as e:
                    dev[ 'w_pos'].setText( "None")
                    dev[ 'w_unitlimitmin'].setText( "None")
                    dev[ 'w_unitlimitmax'].setText( "None")
                    continue
                #
                # handle the position
                #
                dev[ 'w_pos'].setText( utils.getPositionString( dev))
                if dev[ 'proxy'].state() == PyTango.DevState.MOVING:
                    dev[ 'w_pos'].setStyleSheet( "background-color:%s;" % definitions.BLUE_MOVING)
                elif dev[ 'proxy'].state() == PyTango.DevState.RUNNING:
                    dev[ 'w_pos'].setStyleSheet( "background-color:%s;" % definitions.BLUE_RUNNING)
                elif dev[ 'proxy'].state() == PyTango.DevState.ON:
                    dev[ 'w_pos'].setStyleSheet( "background-color:%s;" % definitions.GREY_NORMAL)
                elif dev[ 'proxy'].state() == PyTango.DevState.DISABLE:
                    dev[ 'w_pos'].setStyleSheet( "background-color:%s;" % definitions.MAGENTA_DISABLE)
                else:
                    dev[ 'w_pos'].setStyleSheet( "background-color:%s;" % definitions.RED_ALARM)

                if (self.updateCount % 10) != 0:
                    continue
                #
                # and the limit widgets
                #
                dev[ 'w_unitlimitmin'].setText( utils.getUnitLimitMinString( dev, self.logWidget))
                if utils.getLowerLimit( dev, self):
                    dev[ 'w_unitlimitmin'].setStyleSheet( "background-color:%s;" % definitions.RED_ALARM)
                else:
                    dev[ 'w_unitlimitmin'].setStyleSheet( "background-color:%s;" % definitions.GREY_NORMAL)
                dev[ 'w_unitlimitmax'].setText( utils.getUnitLimitMaxString( dev, self.logWidget))
                if utils.getUpperLimit( dev, self):
                    dev[ 'w_unitlimitmax'].setStyleSheet( "background-color:%s;" % definitions.RED_ALARM)
                else:
                    dev[ 'w_unitlimitmax'].setStyleSheet( "background-color:%s;" % definitions.GREY_NORMAL)
        except utils.TMO as e:
            self.logWidget.append( "main.cb_refresh: expired, dev %s, ignoring" % dev[ 'name'])
            dev[ 'flagOffline'] = True
            self.updateTimer.start( definitions.TIMEOUT_REFRESH)
            return

        signal.alarm(0)
        signal.signal( signal.SIGALRM, hndlr)

    def refreshIORegs( self):
        hndlr = signal.getsignal( signal.SIGALRM)
        signal.signal( signal.SIGALRM, self.handlerALRM)
        signal.alarm( 1)
        startTime = time.time()
        self.updateCount += 1
        try:
            for dev in self.devices.allIRegs + self.devices.allORegs:
                if dev[ 'flagOffline']:
                    continue
                if dev[ 'w_value'].visibleRegion().isEmpty():
                    continue
                #
                # see, if state() responds. If not ignore the motor
                #
                try:
                    sts = dev[ 'proxy'].state()
                except Exception as e:
                    dev[ 'w_value'].setText( "None")
                    continue
                
                # handle the position
                #
                dev[ 'w_value'].setText( "%d" % dev ['proxy'].Value)

        except utils.TMO as e:
            self.logWidget.append( "main.cb_refresh: expired, dev %s, ignoring" % dev[ 'name'])
            dev[ 'flagOffline'] = True
            self.updateTimer.start( definitions.TIMEOUT_REFRESH)
            return
        # 
        #self.logWidget.append( "time-diff %g" % ( time.time() - startTime))
        signal.alarm(0)
        signal.signal( signal.SIGALRM, hndlr)

    def refreshVfcAdcs( self):

        hndlr = signal.getsignal( signal.SIGALRM)
        signal.signal( signal.SIGALRM, self.handlerALRM)
        signal.alarm( 1)
        startTime = time.time()
        self.updateCount += 1
        try:
            for dev in self.devices.allVfcAdcs:
                if dev[ 'flagOffline']:
                    continue
                if dev[ 'w_counts'].visibleRegion().isEmpty():
                    continue
                #
                # see, if state() responds. If not ignore the motor
                #
                try:
                    sts = dev[ 'proxy'].state()
                except Exception as e:
                    dev[ 'w_counts'].setText( "None")
                    continue
                try:
                    dev[ 'w_counts'].setText( utils.getCounterValueStr( dev))
                except Exception as e:
                    dev[ 'w_counts'].setText( "None")
                    print( "refreshTimerCounters: trouble reading Value of %s" % dev[ 'name'])
                    

        except utils.TMO as e:
            self.logWidget.append( "main.cb_refresh: expired, dev %s, ignoring" % dev[ 'name'])
            dev[ 'flagOffline'] = True
            self.updateTimer.start( definitions.TIMEOUT_REFRESH)
            return
        # 
        #self.logWidget.append( "time-diff %g" % ( time.time() - startTime))
        signal.alarm(0)
        signal.signal( signal.SIGALRM, hndlr)

    def refreshCounters( self):

        hndlr = signal.getsignal( signal.SIGALRM)
        signal.signal( signal.SIGALRM, self.handlerALRM)
        signal.alarm( 1)
        startTime = time.time()
        self.updateCount += 1
        try:
            for dev in self.devices.allCounters + \
                self.devices.allTangoAttrCtrls + \
                self.devices.allTangoCounters:
                if dev[ 'flagOffline']:
                    continue
                if dev[ 'w_counts'].visibleRegion().isEmpty():
                    continue
                #
                # see, if state() responds. If not ignore the motor
                #
                try:
                    sts = dev[ 'proxy'].state()
                except Exception as e:
                    dev[ 'w_counts'].setText( "None")
                    continue
                try:
                    dev[ 'w_counts'].setText( utils.getCounterValueStr( dev))
                except Exception as e:
                    dev[ 'w_counts'].setText( "None")
                    print( "refreshTimerCounters: trouble reading Value of %s" % dev[ 'name'])
                    

        except utils.TMO as e:
            self.logWidget.append( "main.cb_refresh: expired, dev %s, ignoring" % dev[ 'name'])
            dev[ 'flagOffline'] = True
            self.updateTimer.start( definitions.TIMEOUT_REFRESH)
            return
        # 
        #self.logWidget.append( "time-diff %g" % ( time.time() - startTime))
        signal.alarm(0)
        signal.signal( signal.SIGALRM, hndlr)

    def refreshAdcDacs( self):
        hndlr = signal.getsignal( signal.SIGALRM)
        signal.signal( signal.SIGALRM, self.handlerALRM)
        signal.alarm( 1)
        startTime = time.time()
        self.updateCount += 1
        try:
            for dev in self.devices.allAdcs + self.devices.allDacs:
                if dev[ 'flagOffline']:
                    continue
                if dev[ 'w_value'].visibleRegion().isEmpty():
                    continue
                #
                # see, if state() responds. If not ignore the motor
                #
                try:
                    sts = dev[ 'proxy'].state()
                except Exception as e:
                    dev[ 'w_value'].setText( "None")
                    continue
                #
                # handle the value
                #
                dev[ 'w_value'].setText( "%g" % utils.getDacValue( dev))

        except utils.TMO as e:
            self.logWidget.append( "main.cb_refresh: expired, dev %s, ignoring" % dev[ 'name'])
            dev[ 'flagOffline'] = True
            self.updateTimer.start( definitions.TIMEOUT_REFRESH)
            return
        # 
        #self.logWidget.append( "time-diff %g" % ( time.time() - startTime))
        signal.alarm(0)
        signal.signal( signal.SIGALRM, hndlr)

    def refreshCameras( self):
        pass

    def refreshPiLCModules( self):
        pass

    def refreshModuleTangos( self):
        pass

    def refreshTimers( self):
        pass

    def refreshMCAs( self):
        pass

    def refreshTDCs( self):
        pass

    def updateMGs( self): 
        '''
        an MG has been deleted or appended
        '''

        mgAliases = HasyUtils.getMgAliases()
        if mgAliases is None: 
            return 
        #
        # first check whether devices.allMGs has to be extended
        #
        for mg in mgAliases:
            flag = False
            #
            # see which group we already have
            #
            for dev in self.devices.allMGs:
                if mg.lower() == dev[ 'name']:
                    flag = True
                    break
            if flag: 
                continue
            dev = {}
            dev[ 'name'] = mg.lower()
            dev[ 'device'] = 'None'
            dev[ 'module'] = 'None'
            dev[ 'type'] = 'measurement_group'
            dev[ 'hostname'] = "%s" % os.getenv( "TANGO_HOST")
            dev[ 'proxy'] = devices.createProxy( dev)
            if dev[ 'proxy'] is None:
                print( "tngGuiClass.updateMGs: No proxy to %s, ignoring this device" % dev[ 'name'])
                continue
            self.devices.allMGs.append( dev)
        #
        # then we check whether MGs have to be deleted 
        #
        for dev in self.devices.allMGs:
            if dev[ 'name'] not in mgAliases:
                del dev

        self.devices.allMGs = sorted( self.devices.allMGs, key=lambda k: k['name'])
        return 

    def refreshMGs( self):
        
        mgAliases = HasyUtils.getMgAliases()
        if len( mgAliases) != len( self.mgAliases): 
            self.logWidget.append( "refreshMGs: MGs changed, length")
            self.updateMGs()
            self.fillMGs()
            return 
            
        for mg in mgAliases: 
            if mg not in self.mgAliases: 
                self.logWidget.append( "refreshMGs: MGs changed, members")
                self.updateMGs()
                self.fillMGs()
                return 

        activeMntGrp = HasyUtils.getEnv( 'ActiveMntGrp')
        for btn in self.MgEntries:
            if btn.text() == activeMntGrp:
                btn.setStyleSheet( "color: blue")
            else: 
                btn.setStyleSheet( "color: black")
        return 

    def refreshDoors( self):
        pass

    def refreshMSs( self):
        pass

    def refreshPools( self):
        pass

    def refreshMacros( self):
        pass

    def refreshNXSConfigServer( self):
        pass

    def handlerALRM( self, signum, frame):
        print( "\n<<<handlerALRM>>>: called with signal %d" % signum)
        raise utils.TMO( "tmo-excepttion")

    def make_cb_resetCounter( self, dev, logWidget):
        def cb():
            try:
                sts = dev[ 'proxy'].state()
            except Exception as e:
                utils.ExceptionToLog( e, self.logWidget)
                QMessageBox.critical(self, 'Error', 
                                           "make_cb_oreg: %s, device is offline" % dev[ 'name'], 
                                           QMessageBox.Ok)
                return

            try:
                dev[ 'proxy'].reset()
                self.logWidget.append( "tngGuiClass.cb_resetCounter: reset %s" % dev[ 'name'])
            except Exception as e:
                print( "Trouble to reset %s" % dev[ 'name'])
                print( repr( e))

        return cb

    def make_cb_setSampleTime( self, dev, logWidget):
        def cb():
            try:
                sts = dev[ 'proxy'].state()
            except Exception as e:
                utils.ExceptionToLog( e, self.logWidget)
                QMessageBox.critical(self, 'Error', 
                                           "make_cb_oreg: %s, device is offline" % dev[ 'name'], 
                                           QMessageBox.Ok)
                return

            oldValue = dev[ 'proxy'].sampleTime
            value, ok = QInputDialog.getText(self, "Enter a value", "New value for %s:" % dev[ 'name'],
                                                   QLineEdit.Normal, "%g" % oldValue)
            if ok:
                dev[ 'proxy'].sampleTime = float(value)

        return cb

    def make_cb_startStopTimer( self, dev, logWidget):
        def cb():
            try:
                sts = dev[ 'proxy'].state()
            except Exception as e:
                utils.ExceptionToLog( e, self.logWidget)
                QMessageBox.critical(self, 'Error', 
                                           "make_cb_oreg: %s, device is offline" % dev[ 'name'], 
                                           QMessageBox.Ok)
                return

            if sts == PyTango.DevState.MOVING:
                dev[ 'proxy'].stop()
            else:
                dev[ 'proxy'].start()
        
        return cb

    def make_cb_oreg( self, dev, logWidget):
        def cb():
            try:
                sts = dev[ 'proxy'].state()
            except Exception as e:
                utils.ExceptionToLog( e, self.logWidget)
                QMessageBox.critical(self, 'Error', 
                                           "make_cb_oreg: %s, device is offline" % dev[ 'name'], 
                                           QMessageBox.Ok)
                return

            value = dev[ 'proxy'].Value
            if value == 0:
                dev[ 'proxy'].Value = 1
            else:
                dev[ 'proxy'].Value = 0
        return cb

    def make_cb_dac( self, dev, logWidget):
        def cb():
            try:
                sts = dev[ 'proxy'].state()
            except Exception as e:
                utils.ExceptionToLog( e, self.logWidget)
                QMessageBox.critical(self, 'Error', 
                                           "make_cb_oreg: %s, device is offline" % dev[ 'name'], 
                                           QMessageBox.Ok)
                return

            oldValue = utils.getDacValue( dev)
            value, ok = QInputDialog.getText(self, "Enter a value", "New value for %s:" % dev[ 'name'],
                                                   QLineEdit.Normal, "%g" % oldValue)
            if ok:
                utils.setDacValue( dev, float(value))

        return cb

    def make_cb_move( self, dev, logWidget):
        def cb():

            if dev[ 'name'].upper() in [ 'EXP_DMY01', 'EXP_DMY02', 'EXP_DMY03']: 
                if logWidget is not None: 
                    logWidget.append( "tngGuiClass: MoveMotor not for dummy motors")
                else:
                    raise ValueError( "tngGuiClass: MoveMotor not for dummy motors")

            if self.w_moveMotor is not None:
                self.w_moveMotor.close()
                del self.w_moveMotor
                
            try:
                sts = dev[ 'proxy'].state()
            except Exception as e:
                utils.ExceptionToLog( e, self.logWidget)
                QMessageBox.critical(self, 'Error', 
                                           "cb_move: %s, device is offline" % dev[ 'name'], 
                                           QMessageBox.Ok)
                return

            self.w_moveMotor = moveMotor.moveMotor( dev, self.devices, logWidget, self.app, self, self.tabletMode)
            self.w_moveMotor.show()
            return self.w_moveMotor
        return cb

    def make_cb_attributes( self, dev, logWidget):
        def cb():
            import tngGui.lib.deviceAttributes as deviceAttributes
            try:
                sts = dev[ 'proxy'].state()
            except Exception as e:
                utils.ExceptionToLog( e, self.logWidget)
                QMessageBox.critical(self, 'Error', 
                                           "cb_attributes: %s, device is offline" % dev[ 'name'], 
                                           QMessageBox.Ok)
                return 
                
            # 
            # remove 'self.' to allow for one widget only
            # 
            self.w_attr = deviceAttributes.deviceAttributes( dev, logWidget, self)
            self.w_attr.show()
            return self.w_attr
        return cb

    def make_cb_commands( self, dev, logWidget):
        def cb():
            import tngGui.lib.deviceCommands as deviceCommands
            try:
                sts = dev[ 'proxy'].state()
            except Exception as e:
                utils.ExceptionToLog( e, self.logWidget)
                QMessageBox.critical(self, 'Error', 
                                           "cb_commands: %s, device is offline" % dev[ 'name'], 
                                           QMessageBox.Ok)
                return 
                
            # 
            # remove 'self.' to allow for one widget only
            # 
            self.w_commands = deviceCommands.deviceCommands( dev, logWidget, self)
            self.w_commands.show()
            return self.w_commands
        return cb

    def make_cb_properties( self, dev, logWidget):
        def cb():
            import tngGui.lib.deviceProperties as deviceProperties
            #
            # replace self.w_prop with w_prop to allow for one 
            # properties widget only
            #
            self.w_prop = deviceProperties.deviceProperties( dev, self.logWidget, self)
            self.w_prop.show()
            return self.w_prop

        return cb

    def make_cb_mb3( self, dev, logWidget):
        def cb():
            import tngGui.lib.deviceAttributes as deviceAttributes
            lst = HasyUtils.getDeviceProperty( dev['device'], "FlagEncoder", dev[ 'hostname'])
            if len(lst) == 0 or lst[0] != "1":
                QMessageBox.critical(self, 'Error', 
                                           "EncoderAttribute widget not available for %s, FlagEncoder != 1" % dev[ 'name'], 
                                           QMessageBox.Ok)
                return

            try:
                sts = dev[ 'proxy'].state()
            except Exception as e:
                QMessageBox.critical(self, 'Error', 
                                           "cb_mb3: %s, device is offline" % dev[ 'name'], 
                                           QMessageBox.Ok)
                return 
                
            self.w_encAttr = deviceAttributes.motorEncAttributes( dev, logWidget, self)
            self.w_encAttr.show()
            return self.w_encAttr
        return cb

    def make_cb_readMCA( self, dev, logWidget):
        def cb():
            proxy = dev[ 'proxy']
            try:
                sts = proxy.state()
            except Exception as e:
                utils.ExceptionToLog( e, self.logWidget)
                QMessageBox.critical(self, 'Error', 
                                     "cb_readMCA: %s, device is offline" % dev[ 'name'], 
                                     QMessageBox.Ok)
                return 
            PySpectra.cls()
            PySpectra.delete()
            try: 
                proxy.read()
            except Exception as e: 
                self.logWidget.append( "cb_readMCA: read() threw an exception")
                utils.ExceptionToLog( e, self.logWidget)
                for arg in e.args: 
                    if arg.desc.find( 'busy') != -1:
                        self.logWidget.append( "consider to execute stop() on the MCA first")
                        break
                return 
            PySpectra.Scan( name =  dev[ 'name'], 
                            y = proxy.data)
            PySpectra.display()
            self.cb_launchPyspGui()
            return 
        return cb

