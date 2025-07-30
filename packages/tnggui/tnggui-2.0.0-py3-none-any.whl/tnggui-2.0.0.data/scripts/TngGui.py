#!python
##
#
# here we check whether the correct version is launched, Python2 vs Python3
#
import sys, os

from PySpectra.pyqtSelector import *
from tngGui.lib.tngGuiClass import mainMenu
from tngGui.lib.tngGuiClass import launchMoveMotor
import tngGui.lib.devices as devices
import tngGui.lib.mcaWidget as mcaWidget

import argparse, os, time
import HasyUtils 

def parseCLI():
    parser = argparse.ArgumentParser( 
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description="TngGui", 
        epilog='''\
Examples:
  TngGui.py 
    select all devices from online.xml
  TngGui.py exp_mot01 exp_mot02
    select only two motors and all other devices
  TngGui.py exp_mot0 
    select 9 motors (exp_mot01 - 09) and all other devices
  TngGui.py exp_mot01
    open move widget for one motor

  The Python regular expression rules apply.

  TngGui.py -t expert
    select all devices tagged with expert (and all those 
    pool devices that have no counterpart in online.xml).
    Tags have to match exactly

  TngGui.py -t expert,user
    select all devices tagged with expert or user (and all 
    those pool devices that have no counterpart in online.xml).
    Tags have to match exactly

    ''')
    #
    # notice that 'pattern' is a positional argument
    #
    parser.add_argument( 'namePattern', nargs='*', help='pattern to match the motor names, not applied to other devices')
    parser.add_argument( '--xml', dest='xmlFile', default=None, help='a file to be be read instead of /online_dir/online.xml')
    parser.add_argument( '--mca', dest='mca', action="store_true", help='start the MCA widget')
    parser.add_argument( '-t', dest='tags', nargs='+', help='tags matching online.xml tags')
    parser.add_argument( '--fs', dest="fontSize", action="store", default=None, help='font size, def. 14')
    parser.add_argument( '--tablet', dest="tablet", action="store_true", default=False, help='change style for tablet usage')
    parser.add_argument( '--mp', dest="msProperties", action="store_true", default=False, help='Convert macroserver.properties to msProperties.lis')
    args = parser.parse_args()

    # 

    return args

stylesheet = """
QScrollBar::handle:pressed
{
    background: pink;
    min-height : 50;
}
QScrollBar:horizontal:handle
{
    min-width : 50; 
    min-height : 50;
}
QPushButton#moveexit
{
  min-width : 50;
  min-height : 60;

}
QPushButton#moveselectmotor
{
  min-width : 80;
  min-height : 50;

}
QPushButton#movebutton
{
  min-width : 80;
  min-height : 80;

}
QPushButton#movebutton2
{
  min-width : 60;
  min-height : 60;

}
QLineEdit#moveedit
{
  min-height : 60;
}
QPushButton#movetomax
{
  min-width : 50;
  min-height : 60;
}
QCheckBox::indicator
{
  width : 50px;
  height : 50px;
}
QComboBox#movecb
{
  width : 80px;
  height : 80px;
}
"""
def main():

    args = parseCLI()
    # 
    args.counterName = None
    args.timerName = None

    #
    # before you uncomment the following line check
    #   - whether you can create a pdf file via pysp
    #     this was the error message: 
    #       File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1819, in __init__
    #         baseName = os.path.basename(sys.argv[0])
    #sys.argv = []
    
    #app = TaurusApplication( sys.argv)

    app = QApplication(sys.argv)

    #
    # if .setStyle() is not called, if TngGui is running
    # locally (not via ssh), the function app.style().metaObject().className()
    # returns QGtkStyle. If this string is supplied to .setStyle()
    # a segmentation fault is generated, locally and remotely.
    # so for remote running we use 'Ceanlooks' which is quite OK.
    #
    app.setStyle( 'Cleanlooks')

    font = QFont( 'Sans Serif')
    if args.fontSize is not None:
        font.setPixelSize( int( args.fontSize))
    else: 
        if args.tablet: 
            font.setPixelSize( 20)
        else: 
            font.setPixelSize( 14)
    app.setFont( font)

    if args.tablet: 
        app.setStyleSheet( stylesheet)

    devs = devices.Devices( args, xmlFile = args.xmlFile)
    
    if args.mca:
        w = mcaWidget.mcaWidget( devices = devs, app = app)
        w.show()
    else:
        if len( devs.allMotors) == 1 or args.tablet:
            w = launchMoveMotor( devs.allMotors[0], devs, app, logWidget = None, parent = None, tabletMode = args.tablet)
            w.show()
        else: 
            mainW = mainMenu(args, app, devs, parent = None, tabletMode = args.tablet)
            if args.msProperties: 
                mainW.convertMacroServerPropertiesNoEdit()
                return 
            else: 
                mainW.show()

    try:
        sys.exit( app.exec_())
    except Exception as e:
        print( repr( e))

if __name__ == "__main__":
    main()
    
