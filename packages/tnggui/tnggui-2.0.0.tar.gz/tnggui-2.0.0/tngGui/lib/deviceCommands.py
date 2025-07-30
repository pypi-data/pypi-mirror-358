#!/usr/bin/env python

import sys
from PySpectra.pyqtSelector import *

import PyTango
import math, os
import HasyUtils
import tngGui.lib.utils as utils
import tngGui.lib.definitions as definitions
import json
import tngGui.lib.helpBox as helpBox
import pprint
pp = pprint.PrettyPrinter( indent=4)
            
class deviceCommands( QMainWindow):
    def __init__( self, dev, logWidget, parent = None):
        super( deviceCommands, self).__init__( parent)
        self.parent = parent
        self.tkFlag = self.parent.tkFlag
        self.dev = dev
        self.setWindowTitle( "Commands of %s" % self.dev[ 'name'])
        self.logWidget = logWidget
        w = QWidget()
        self.layout_v = QVBoxLayout()
        w.setLayout( self.layout_v)
        self.setCentralWidget( w)
        alias_l = QLabel( self.dev[ 'name'])
        name_l = QLabel( "%s/%s" % (self.dev[ 'hostname'], self.dev[ 'device']))
        layout_h = QHBoxLayout()
        layout_h.addWidget( alias_l)
        layout_h.addWidget( name_l)
        self.layout_v.addLayout( layout_h)
        self.layout_grid = QGridLayout()
        self.layout_v.addLayout( self.layout_grid)

        self.fillCommands()
            
        #
        # Menu Bar
        #
        self.menuBar = QMenuBar()
        self.setMenuBar( self.menuBar)
        self.fileMenu = self.menuBar.addMenu('&File')
        self.exitAction = QAction('E&xit', self)        
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect( self.cb_closeMotorAttr)
        self.fileMenu.addAction( self.exitAction)


        if self.dev[ 'module'].lower() == "oms58":
            self.miscMenu = self.menuBar.addMenu('&Misc')
            self.blackBoxAction = QAction( 'BlackBox', self)        
            self.blackBoxAction.triggered.connect( self.cb_blackBox)
            self.miscMenu.addAction( self.blackBoxAction)

        #
        # the activity menubar: help and activity
        #
        self.menuBarActivity = QMenuBar( self.menuBar)
        self.menuBar.setCornerWidget( self.menuBarActivity, QtCore.Qt.TopRightCorner)

        self.helpMenu = self.menuBarActivity.addMenu('Help')
        self.helpCommand = self.helpMenu.addAction(self.tr("Widget"))
        self.helpCommand.triggered.connect( self.cb_helpCommand)
        if self.dev[ 'module'] == 'nxsconfigserver': 
            self.helpNXSConfigServer = self.helpMenu.addAction(self.tr("NXSConfigServer"))
            self.helpNXSConfigServer.triggered.connect( self.cb_helpNXSConfigServer)

        self.activityIndex = 0
        self.activity = self.menuBarActivity.addMenu( "_")

        #
        # Status Bar
        #
        self.statusBar = QStatusBar()
        self.setStatusBar( self.statusBar)


        self.attributes = QPushButton(self.tr("Attributes")) 
        self.statusBar.addWidget( self.attributes)
        self.attributes.clicked.connect( self.cb_launchAttributes)

        self.properties = QPushButton(self.tr("Properties")) 
        self.statusBar.addWidget( self.properties)
        self.properties.clicked.connect( self.cb_launchProperties)

        
        self.exit = QPushButton(self.tr("E&xit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( self.cb_closeMotorAttr)
        self.exit.setShortcut( "Alt+x")

        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.timeout.connect( self.cb_refreshCommands)
        self.updateTimer.start( definitions.TIMEOUT_REFRESH)

    def cb_helpCommand( self):
        w = helpBox.HelpBox( self, self.tr("Help Commands"), self.tr(
            "<h3>Commands</h3>"
            "<ul>"
            "<li> Array elements are separated by commas"
            "</ul>"
                ))
        w.show()

    def cb_helpNXSConfigServer( self):
        w = helpBox.HelpBox( self, self.tr("Help NXSConfigServer"), self.tr(
            "<h3>Debugging</h3>"
            "<ul>"
            "<li> nxselector displays invalid component and data source"
            "<li> insert the data source in DataSources and click button"
            "<li> the logWidget displays the details"
            "</ul>"
                ))
        w.show()

    def cb_refreshCommands( self):
        pass

    def cb_launchAttributes( self): 

        import tngGui.lib.deviceAttributes as deviceAttributes
        self.w_attributes = deviceAttributes.deviceAttributes( self.dev, self.logWidget, self)
        self.w_attributes.show()
        return self.w_attributes

    def cb_launchProperties( self): 
        import tngGui.lib.deviceProperties as deviceProperties
        self.w_prop = deviceProperties.deviceProperties( self.dev, self.logWidget, self)
        self.w_prop.show()
        return self.w_prop

    def getCommandInfoList( self): 
        '''
        return the list of commands info blocks
        '''
        commandInfoList = self.dev[ 'proxy'].command_list_query()
        return commandInfoList

    def fillCommands( self): 
        count = 0
        self.commandInfoList = self.getCommandInfoList()

        self.commandDct = {}
        #
        # if we have many attributes, we have to create 2 'columns'
        #
        columnOffset = 0
        splitNo = len( self.commandInfoList)
        if len( self.commandInfoList) > 10:
            splitNo = math.ceil( len( self.commandInfoList)/2.)

        #
        # countMax keeps track of the line numbers, even if we have
        # several columns. Solves this problem: if the right column
        # ends earlier than the first column, the reply label still
        # has to be in the right line
        #
        countMax = 0
        for commandInfo in self.commandInfoList:
            nameBtn = utils.QPushButtonTK( commandInfo.cmd_name)
            nameBtn.setToolTip( "In: %s\nOut:%s" % (commandInfo.in_type_desc, commandInfo.out_type_desc))
            self.layout_grid.addWidget( nameBtn, count, 0 + columnOffset)
            
            line = None
            if commandInfo.in_type != PyTango.CmdArgType.DevVoid:
                line = QLineEdit()
                line.setAlignment( QtCore.Qt.AlignRight)
                self.layout_grid.addWidget( line, count, 1 + columnOffset)

            nameBtn.mb1.connect( self.make_cb_command( commandInfo, line))

            count += 1
            if count > countMax:
                countMax = count
            #
            # we don't want to reset the count, if there is only one 
            # command column. Otherwise the 'Reply' will be
            # put with count == 0
            #
            if splitNo != len( self.commandInfoList) and \
               count >= splitNo and columnOffset == 0: 
                columnOffset += 4
                count = 0

        self.replyLabel = QLabel( "Reply:")
        self.layout_grid.addWidget( self.replyLabel, countMax, 0, 1, 2)


        return 

    def make_cb_command( self, commandInfo, line):
        def cb():
            try:
                if commandInfo.in_type == PyTango.CmdArgType.DevVoid:
                    reply = self.dev[ 'proxy'].command_inout( commandInfo.cmd_name)
                elif commandInfo.in_type == PyTango.CmdArgType.DevBoolean:
                    if line.text().lower() == "false": 
                        t = False
                    elif line.text().lower() == "true": 
                        t = True
                    reply = self.dev[ 'proxy'].command_inout( commandInfo.cmd_name, t)
                elif commandInfo.in_type == PyTango.CmdArgType.DevDouble or \
                     commandInfo.in_type == PyTango.CmdArgType.DevFloat:
                    reply = self.dev[ 'proxy'].command_inout( commandInfo.cmd_name, float( line.text()))
                elif commandInfo.in_type == PyTango.CmdArgType.DevLong or \
                     commandInfo.in_type == PyTango.CmdArgType.DevULong or \
                     commandInfo.in_type == PyTango.CmdArgType.DevLong64 or \
                     commandInfo.in_type == PyTango.CmdArgType.DevULong64 or \
                     commandInfo.in_type == PyTango.CmdArgType.DevShort or \
                     commandInfo.in_type == PyTango.CmdArgType.DevUShort:
                    reply = self.dev[ 'proxy'].command_inout( commandInfo.cmd_name, int( line.text()))
                elif commandInfo.in_type == PyTango.CmdArgType.DevVarDoubleArray or \
                     commandInfo.in_type == PyTango.CmdArgType.DevVarFloatArray:
                    lst = [ float( n) for n in line.text().split( ',')]
                    reply = self.dev[ 'proxy'].command_inout( commandInfo.cmd_name, lst)
                elif commandInfo.in_type == PyTango.CmdArgType.DevString:
                    reply = self.dev[ 'proxy'].command_inout( commandInfo.cmd_name, str( line.text()))
                elif commandInfo.in_type == PyTango.CmdArgType.DevVarStringArray:
                    lst = [ str(elm) for elm in line.text().split( ',')]                    
                    reply = self.dev[ 'proxy'].command_inout( commandInfo.cmd_name, lst)
                elif commandInfo.in_type == PyTango.CmdArgType.DevVarLongArray or \
                     commandInfo.in_type == PyTango.CmdArgType.DevVarLong64Array or \
                     commandInfo.in_type == PyTango.CmdArgType.DevVarShortArray or \
                     commandInfo.in_type == PyTango.CmdArgType.DevVarUShortArray or \
                     commandInfo.in_type == PyTango.CmdArgType.DevVarULongArray or \
                     commandInfo.in_type == PyTango.CmdArgType.DevVarULong64Array or \
                     commandInfo.in_type == PyTango.CmdArgType.DevVarCharArray:
                    lst = [int( n) for n in line.text().split( ',')]
                    reply = self.dev[ 'proxy'].command_inout( commandInfo.cmd_name, lst)
                else:
                    print( "make_cb_command: need to implement %s" % repr( commandInfo.in_type))
                    return
            except Exception as e:
                self.logWidget.append( "exception executing %s() on %s" % (commandInfo.cmd_name, self.dev[ 'name']))
                utils.ExceptionToLog( e, self.logWidget)
                QMessageBox.critical(self, 'Error', 
                                           "make_cb_command: %s, %s" % (self.dev[ 'name'], repr(e)), 
                                           QMessageBox.Ok)
                return

            if line is not None:
                line.clear()

            self.logWidget.append( "%s: %s(), reply %s" % (self.dev[ 'name'], commandInfo.cmd_name, pp.pformat( reply)))
            if len(repr( reply)) > 20:
                self.replyLabel.setText( "Reply: see logWidget")
            else: 
                self.replyLabel.setText( "Reply: %s" % repr( reply))
            return 

        return cb

    def getAttrInfoList( self): 
        '''
        return the list of attribute info blocks
        '''
        attrOms = [ 'State', 'Status', 'Position', 'UnitLimitMin', 'UnitLimitMax', 'UnitBacklash', 'UnitCalibration',
                    'StepPositionController', 'StepPositionInternal',
                    'SlewRate', 'SlewRateMin', 'SlewRateMax', 'BaseRate',
                    'Conversion', 'Acceleration', 
                    #'StepBacklash', 'StepLimitMin', 'StepLimitMax', 
                    'SettleTime',
                    'CwLimit', 'CcwLimit', 'FlagProtected', 'FlagCheckZMXActivated', 'WriteRead']
        attrTip551 = [ 'State', 'Status', 'Voltage', 'VoltageMax', 'VoltageMin']
        attrVfcAdc = [ 'State', 'Status', 'Counts', 'Value', 'Gain', 'Offset', 'Polarity']
        attrPilcVfcAdc = [ 'State', 'Status', 'Counts', 'Value', 'Polarity']
        attrMCA_8701 = [ 'State', 'Status', 'DataLength', 'NbRois', 
                         'Counts1', 'Counts1Diff', 'ROI1',
                         'Counts2', 'Counts2Diff', 'ROI2',
                         'Counts3', 'Counts3Diff', 'ROI3',
                         'Counts4', 'Counts4Diff', 'ROI4']
        #attrMotorTango = [ 'State', 'Position', 'UnitLimitMin', 'UnitLimitMax']
        attrSpk =  [ 'State', 'Status', 'Position', 'CcwLimit', 'CwLimit', 'ConversionFactor', 'ErrorCode', 
                     'Position', 'SlewRate', 'UnitBackLash', 'UnitLimitMin', 'UnitLimitMax']
        attrMotorPool = [ 'State', 'Status', 'Position', 'Backlash', 'Acceleration', 'Velocity', 'Step_per_unit']

        attrExtra = ['BraggAngle', 'BraggOffset', 'BraggOffset0', 'BraggOffset1', 'BraggOffset3', 
                     'Crystal', 'ExitOffset', 'ExitOffsetC0', 'ExitOffsetC1', 'UpdateStatusRate', 'PositionSim']

        attrSelected = None

        if self.dev[ 'module'].lower() == 'oms58':
            attrSelected = attrOms
        elif self.dev[ 'module'].lower() == 'tip551':
            attrSelected = attrTip551
        elif self.dev[ 'module'].lower() == 'motor_pool':
            attrSelected = attrMotorPool
        elif self.dev[ 'module'].lower() == 'spk':
            attrSelected = attrSpk
        elif self.dev[ 'module'].lower() == 'vfcadc':
            if HasyUtils.proxyHasAttribute( self.dev[ 'proxy'], 'Gain'):
                attrSelected = attrVfcAdc
            else:
                attrSelected = attrPilcVfcAdc
        elif self.dev[ 'module'].lower() == 'mca_8701':
            attrSelected = attrMCA_8701
        #elif self.dev[ 'module'].lower() == 'motor_tango':
        #    attrSelected = attrMotorTango
        #    for a in attrExtra:
        #        if hasattr( self.motor, a):
        #            attrSelected.append( a)

        attrInfoListAll = self.dev[ 'proxy'].attribute_list_query()
        attrInfoList = []
        for attrInfo in attrInfoListAll: 
            if attrInfo.name == 'State': 
                ste = attrInfo
                continue
            if attrInfo.name == 'Status': 
                sts = attrInfo
                continue
            if attrSelected is not None: 
                if attrInfo.name not in attrSelected: 
                    continue
            attrInfoList.append( attrInfo)

        def cmpr( x): 
            return x.name
        attrInfoList.sort( key = cmpr)
        attrInfoList.append( ste)
        attrInfoList.append( sts)
        return attrInfoList
        
    def cb_clearError( self):
        '''
        Spk
        '''
        self.dev[ 'proxy'].ClearError()

    def cb_resetVfcAdc( self):
        self.dev[ 'proxy'].reset()

    def cb_resetAllVfcAdc( self):
        '''
        after a reset of a single channel, all readings are 0, but
        the next gate period shows that not all are really reset
        '''
        for dev in allVfcAdcs:
            dev[ 'proxy'].reset()

    def cb_initVFCADC( self):
        self.dev[ 'proxy'].InitVFCADC()

    #
    # the closeEvent is called when the window is closed by 
    # clicking the X at the right-upper corner of the frame
    #
    def closeEvent( self, e):
        self.cb_closeMotorAttr()
        #e.ignore()

    def cb_closeMotorAttr( self):
        self.updateTimer.stop()
        self.close()

    def cb_helpAttrOms58( self):
        w = helpBox.HelpBox( self, self.tr("Help Attributes"), self.tr(
            "<h3>Attributes</h3>"
            "<ul>"
            "<li> Position (cal.): Calibrates the motor, the motor position is calibrated to the "
            "user supplied value. The user is prompted for confirmation."
            "<li> StepPositionController/Internal: the command setStepRegister is used to set " 
            "the internal and controller register. The position does not change."
            "</ul>"
                ))
        w.show()

    def cb_helpAttrSpk( self):
        w = helpBox.HelpBox( self, self.tr("Help widget"), self.tr(
            "<ul>"
            "<li> use 'online -tki' for more details"
            "<li> Error code"
            "<ul>"
            "<li> 0 no error"
            "<li> 1 emergency off"
            "<li> 2 unexpected limit switch (wrong direction)"
            "<li> 3 at limit when switched on"
            "<li> 4 both limit switches fired"
            "<li> 5 reference move stopped by limit switch"
            "<li> 6 reference move: wrong limit"
            "<li> 7 backlash greater than 1"
            "<li> 8 inconsistent limits"
            "<li> 9 hardware error( Schrittmotorklemme)"
            "<li> 10 encoder error (misaligned?)"
            "<li> 11 error during init"
            "</ul>"
            "</ul>"
                ))
        w.show()
    def cb_helpAttrVfcAdc( self):
        w = helpBox.HelpBox( self, self.tr("Help widget"), self.tr(
            "<ul>"
            "<li> Polarity: 1 or 0"
            "<li> ResetAll: after a reset of a single channel, all readings are 0, but"
            "the next gate period shows that not all are really reset"
            "</ul>"
                ))
        w.show()

    def cb_helpBlackBox( self):
        w = helpBox.HelpBox( self, self.tr("Help BlackBox"), self.tr(
            "<h3>BlackBox</h3>"
            "The Black Box contents is written to the log widget. "
            "This features finds connected clients."
                ))
        w.show()
    def cb_helpWriteRead( self):
        w = helpBox.HelpBox( self, self.tr("Help WriteRead"), self.tr(
            "<h3>WriteRead</h3>"
            "The input string is sent to the motor and the result "
            "is printed in the log widget. The server inserts an axis specification "
            "at the beginning of the string."
            "<hr>"
            "<br>"
            "<b>RP</b> Request position"
            "<br>"
            "<b>RE</b> Request encoder"
            "<br>"
            "<b>LO12345</b> Load motor position"
            "<br>"
            "<b>LP12345</b> Load motor and encoder position"
            "<br>"
            "<b>LPE12345</b> Load encoder position, independent of motor position"
            "<br>"
            "<b>CL?</b> Query closed loop state"
            "<br>"
            "<b>SI</b> Stop"
            "<br>"
            "<b>MA12345;GO;SI</b> Move absolute, set DONE when finished"
            "<br>"
            "<b>VL4321</b> Set slew rate"
            "<br>"
            "<b>VL?</b> Query slew rate"
                ))
        w.show()
        
    def cb_blackBox( self):
        lst = self.dev[ 'proxy'].black_box( 100)
        self.logWidget.append('---')
        self.logWidget.append( "%s" % self.dev[ 'name'])
        for line in lst:
            if line.find('Empty') == -1:
                self.logWidget.append( line)


            
