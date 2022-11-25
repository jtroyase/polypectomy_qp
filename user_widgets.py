import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer
from PyQt5.QtGui import QPixmap, QIntValidator, QKeySequence, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QCheckBox, QFileDialog, QDesktopWidget, QLineEdit, \
     QRadioButton, QShortcut, QScrollArea, QVBoxLayout, QGroupBox, QFormLayout, QSlider, QButtonGroup, QGridLayout, \
     QHBoxLayout

import ast


def init_label_checkboxes(window):
     '''
     Reads the labels to annotate written in the config file and
     creates the label radio buttons that appear in the init GUI.
     :param window: The PyQt5 window object
     '''

     # Open the config file
     labels = []
     extra_labels = []

     with open('config.txt', 'r') as f:
          for line in f.readlines():
               if line.startswith('labels'):
                    labels = ast.literal_eval('[' + line.split('[')[1])
               if line.startswith('extra_labels'):
                    extra_labels = ast.literal_eval('[' + line.split('[')[1])
     
     grid = QGridLayout(window)

     positions = []
     row = 0
     for _ , label in enumerate(labels+extra_labels):
          remainder = _%5
          if remainder == 4:
               positions.append((row, remainder))
               row+=1 
          else:
               positions.append((row, remainder))

     checkboxes = {}
     for position, label in zip(positions,labels + extra_labels):
          checkbox = QCheckBox(label, window)
          if label in labels:
               checkbox.setChecked(True)
          checkboxes[label]=checkbox
          grid.addWidget(checkbox, *position)
          
     
     return grid, checkboxes