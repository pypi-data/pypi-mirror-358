import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton # Removed QColorDialog
from PyQt5.QtGui import QColor # QColor is still useful for color manipulation if needed, or default init
from PyQt5.QtCore import Qt
import pyqtgraph as pg # Import pyqtgraph
import time # For time.sleep for I2C delays

from kuttyPy import *

AVR_SLAVE_ADDRESS = 0x20 # I2C address of your AVR slave

if AVR_SLAVE_ADDRESS not in I2CScan():
	print('client device not found')
	sys.exit(1)

class App(QWidget):
    def __init__(self):
    
        super().__init__(); self.l=QVBoxLayout(self) # Init app window & layout
        self.led_colors = [[0,0,0], [0,0,0]] # Local state for R,G,B of LED1 & LED2
        for i in range(2): # Create two ColorButton widgets for LEDs
            # 'color='k'' sets default to black. 'sigColorChanging' emits QColor.
            b=pg.ColorButton(color='b')
            b.setMinimumHeight(100)
            b.setText(f"Set LED {i+1}")
            b.sigColorChanging.connect(lambda c,n=i+1: self.sc(c,n))
            self.l.addWidget(b)
        b=QPushButton("Fade LEDs (5x)"); b.clicked.connect(self.fl); self.l.addWidget(b) # Fade button

        b=QPushButton("FWD"); b.clicked.connect(self.fwd); self.l.addWidget(b) # FORWARD
        self.f=QHBoxLayout();self.l.addLayout(self.f)
        b=QPushButton("<  "); b.clicked.connect(self.left); self.f.addWidget(b) # left
        b=QPushButton("   >"); b.clicked.connect(self.right); self.f.addWidget(b) # right

        b=QPushButton("BACK"); b.clicked.connect(self.back); self.l.addWidget(b) # back
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.fwd()
            event.accept()  # Crucial: tell PyQt we handled this event
        elif event.key() == Qt.Key_Down:
            self.back()
            event.accept()  # Crucial: tell PyQt we handled this event
        elif event.key() == Qt.Key_Left:
            self.left()
            event.accept()  # Crucial: tell PyQt we handled this event
        elif event.key() == Qt.Key_Right:
            self.right()
            event.accept()  # Crucial: tell PyQt we handled this event
        else:
            # For other keys, let the default behavior happen
            super().keyPressEvent(event)

    def sc(self, btn, n): # Method to set color via I2C (connected to ColorButton's signal)
        color = btn.color()
        #print(color,n)
        r,g,b=color.red(),color.green(),color.blue() # Extract R,G,B from QColor
        self.led_colors[n-1]=[r,g,b] # Update local state for the modified LED
        # Send combined 0x30 command with colors for *both* LEDs simultaneously
        I2CWriteBulk(AVR_SLAVE_ADDRESS,[0x30,self.led_colors[0][0],self.led_colors[0][1],self.led_colors[0][2],self.led_colors[1][0],self.led_colors[1][1],self.led_colors[1][2]])

    def fl(self): # Method to send fade command
        I2CWriteBulk(AVR_SLAVE_ADDRESS,[0x20,5])

    def fwd(self): #move
        I2CWriteBulk(AVR_SLAVE_ADDRESS,[0x40,1, 2,2]) #move, once, fwd, fwd
    def back(self): #move
        I2CWriteBulk(AVR_SLAVE_ADDRESS,[0x40,1, 0,0]) #move, once, bk, bk
    def left(self): #move
        I2CWriteBulk(AVR_SLAVE_ADDRESS,[0x40,1, 0,2]) #move, once, bk, fwd
    def right(self): #move
        I2CWriteBulk(AVR_SLAVE_ADDRESS,[0x40,1, 2,0]) #move, once, fwd, bk

if __name__=="__main__": # Standard Python application entry point
    app=QApplication(sys.argv); w=App(); w.show(); sys.exit(app.exec_()) # Create, show, and run the app
