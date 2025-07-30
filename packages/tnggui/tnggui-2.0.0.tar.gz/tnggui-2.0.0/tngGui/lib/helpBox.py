#!/usr/bin/env python

import sys
from PySpectra.pyqtSelector import *
#
# the line below insert QMainWindow into PyQt5.QtGui
# normally this would be in QtWidgets
#
import PySpectra

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
        #self.textBox = QTextBrowser( self)
        #self.textBox.setOpenExternalLinks(True)
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

class HelpBoxPlain( QMainWindow):
    #
    # class to display some help text.
    # Avoid QMessageBox() because this cannot be moved
    #
    def __init__( self, parent, title = "Title", text = None):
        super( HelpBoxPlain, self).__init__( parent)
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
        #self.textBox = QTextBrowser( self)
        #self.textBox.setOpenExternalLinks(True)
        self.textBox.setPlainText( text)
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
