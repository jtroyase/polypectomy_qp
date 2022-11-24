import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer
from PyQt5.QtGui import QPixmap, QIntValidator, QKeySequence, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QCheckBox, QFileDialog, QDesktopWidget, QLineEdit, \
     QRadioButton, QShortcut, QScrollArea, QVBoxLayout, QGroupBox, QFormLayout, QSlider, QButtonGroup


def init_label_rbuttons(window):
    '''
    Creates the label radio buttons that appear in the init GUI.
    '''
    radioButton1 = QRadioButton("Appendix", window)
    radioButton1.move(60, 170)
    radioButton1.status = "appendix"
    
    radioButton2 = QRadioButton("Blood", window)
    radioButton2.move(210, 170)
    radioButton2.status = "blood"
    
    radioButton3 = QRadioButton("Clip", window)
    radioButton3.move(360, 170)
    radioButton3.status = "clip"
    
    radioButton4 = QRadioButton("Diverticule", window)
    radioButton4.move(510, 170)
    radioButton4.status = "diverticule"
    
    radioButton5 = QRadioButton("Grasper", window)
    radioButton5.move(660, 170)
    radioButton5.status = "grasper"

    radioButton6 = QRadioButton("Ileocaecalvalve", window)
    radioButton6.move(60, 220)
    radioButton6.status = "ileocaecalvalve"
    
    radioButton7 = QRadioButton("Ileum", window)
    radioButton7.move(210, 220)
    radioButton7.status = "ileum"
    
    radioButton8 = QRadioButton("Low quality", window)
    radioButton8.move(360, 220)
    radioButton8.status = "low_quality"
    
    radioButton9 = QRadioButton("NBI", window)
    radioButton9.move(510, 220)
    radioButton9.status = "nbi"
    
    radioButton10 = QRadioButton("Needle", window)
    radioButton10.move(660, 220)
    radioButton10.status = "needle"

    radioButton11 = QRadioButton("Outside", window)
    radioButton11.move(60, 270)
    radioButton11.status = "outside"

    radioButton12 = QRadioButton("Polyp", window)
    radioButton12.move(210, 270)
    radioButton12.status = "polyp"
    
    radioButton13 = QRadioButton("Snare", window)
    radioButton13.move(360, 270)
    radioButton13.status = "snare"
    
    radioButton14 = QRadioButton("Waterjet", window)
    radioButton14.move(510, 270)
    radioButton14.status = "water_jet"

    radioButton15 = QRadioButton("Wound", window)
    radioButton15.move(660, 270)
    radioButton15.status = "wound"
    
    
    #Create a key group and add keys
    cs_group = QButtonGroup(window)
    cs_group.addButton(radioButton1, 1)
    cs_group.addButton(radioButton2, 2)
    cs_group.addButton(radioButton3, 3)
    cs_group.addButton(radioButton4, 4)
    cs_group.addButton(radioButton5, 5)
    cs_group.addButton(radioButton6, 6)
    cs_group.addButton(radioButton7, 7)
    cs_group.addButton(radioButton8, 8)
    cs_group.addButton(radioButton9, 9)
    cs_group.addButton(radioButton10, 10)
    cs_group.addButton(radioButton11, 11)
    cs_group.addButton(radioButton12, 12)
    cs_group.addButton(radioButton13, 13)
    cs_group.addButton(radioButton14, 14)
    cs_group.addButton(radioButton15, 15)

    return cs_group



    # radioButton1 = QRadioButton("Appendix")
    # radioButton1.move(60, 140)
    # radioButton1.status = "appendix"
    
    # radioButton2 = QRadioButton("Blood")
    # radioButton2.move(90, 140)
    # radioButton2.status = "blood"
    
    # radioButton3 = QRadioButton("Clip")
    # radioButton3.move(120, 140)
    # radioButton3.status = "clip"
    
    # radioButton4 = QRadioButton("Diverticule")
    # radioButton4.move(150, 140)
    # radioButton4.status = "diverticule"
    
    # radioButton5 = QRadioButton("Grasper")
    # radioButton5.move(180, 140)
    # radioButton5.status = "grasper"

    # radioButton6 = QRadioButton("Ileocaecalvalve")
    # radioButton6.move(60, 170)
    # radioButton6.status = "ileocaecalvalve"
    
    # radioButton7 = QRadioButton("Ileum")
    # radioButton7.move(90, 170)
    # radioButton7.status = "ileum"
    
    # radioButton8 = QRadioButton("Low quality")
    # radioButton8.move(120, 170)
    # radioButton8.status = "low_quality"
    
    # radioButton9 = QRadioButton("NBI")
    # radioButton9.move(150, 170)
    # radioButton9.status = "nbi"
    
    # radioButton10 = QRadioButton("Needle")
    # radioButton10.move(180, 170)
    # radioButton10.status = "needle"

    # radioButton11 = QRadioButton("Outside")
    # radioButton11.move(60, 220)
    # radioButton11.status = "outside"

    # radioButton12 = QRadioButton("Polyp")
    # radioButton12.move(90, 220)
    # radioButton12.status = "polyp"
    
    # radioButton13 = QRadioButton("Snare")
    # radioButton13.move(120, 220)
    # radioButton13.status = "snare"
    
    # radioButton14 = QRadioButton("Waterjet")
    # radioButton14.move(150, 220)
    # radioButton14.status = "water_jet"

    # radioButton14 = QRadioButton("Wound")
    # radioButton14.move(180, 220)
    # radioButton14.status = "wound"
    
    
    # #Create a key group and add keys
    # cs_group = QButtonGroup(self)
    # cs_group.addButton(radioButton1, 1)
    # cs_group.addButton(radioButton2, 2)
    # cs_group.addButton(radioButton3, 3)
    # cs_group.addButton(radioButton4, 4)
    # cs_group.addButton(radioButton5, 5)
    # cs_group.addButton(radioButton6, 6)
    # cs_group.addButton(radioButton7, 7)
    # cs_group.addButton(radioButton8, 8)
    # cs_group.addButton(radioButton9, 9)
    # cs_group.addButton(radioButton10, 10)
    # cs_group.addButton(radioButton11, 11)
    # cs_group.addButton(radioButton12, 12)
    # cs_group.addButton(radioButton13, 13)
    # cs_group.addButton(radioButton14, 14)
    # cs_group.addButton(radioButton15, 15)

    # # Connects the onclicked function and print the received paramenters
    # cs_group.buttonClicked.connect(onClicked)

    # # Set cs_group to not be mutually exclusive
    # cs_group.setExclusive(False)
