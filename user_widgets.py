import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer
from PyQt5.QtGui import QPixmap, QIntValidator, QKeySequence, QPainter, QPen, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QCheckBox, QFileDialog, QDesktopWidget, QLineEdit, \
     QRadioButton, QShortcut, QScrollArea, QVBoxLayout, QGroupBox, QFormLayout, QSlider, QButtonGroup, QGridLayout, \
     QHBoxLayout

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

import ast
import annotation

class LegendItem(QtWidgets.QWidget):
    def __init__(self, text, color, parent=None):
        super().__init__(parent)
        self.text = text
        self.color = color

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        rect = event.rect()
        rect.setWidth(20)  # width of the color square
        painter.fillRect(rect, self.color)  # paint the color square

        font = painter.font()
        font.setBold(True)
        painter.setPen(QColor("red"))
        painter.setFont(QFont("Arial", 16))
        rect = QtCore.QRect(10, 10, 90, 25)
        painter.drawText(rect, QtCore.Qt.AlignCenter, self.text)

class Legend(QtWidgets.QWidget):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(5,5,5,5)
        self._layout.setSpacing(5)
        self.create_items()

    def create_items(self):
        for item in self.items:
            self._layout.addWidget(item)

def init_label_checkboxes(window):
     '''
     Reads the labels to annotate written in the config file and
     creates the label radio buttons that appear in the init GUI.
     :param window: The PyQt5 window object
     '''

     # Open the config file
     labels = []
     extra_labels = []

     labels = ast.literal_eval('[' + read_config('labels').split('[')[1])
     extra_labels = ast.literal_eval('[' + read_config('extra_labels').split('[')[1])
     
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


def colors_polyp(id):
     '''
     Returns the color to use of the polyp depending
     on the id assigned to that polyp. The different
     colors for each polyp can be configured on the
     config file.
     '''
     colors_id = '{' + read_config('colors_id').split('{')[1]
     colors = ast.literal_eval(colors_id)
     
     if colors[id] == 'green':
          color = Qt.green
     elif colors[id] == 'red':
          color = Qt.red
     elif colors[id] == 'blue':
          color = Qt.blue
     elif colors[id] == 'magenta':
          color = Qt.magenta
     elif colors[id] == 'cyan':
          color = Qt.cyan
     elif colors[id] == 'yellow':
          color = Qt.yellow
     elif colors[id] == 'gray':
          color = Qt.gray
     elif colors[id] == 'black':
          color = Qt.black
     else:
          raise ValueError('This color is not possible')

     return color


def label_color(label):
     '''
     Returns the color assigned in the config file for
     that particular label
     '''
     colors_id = '{' + read_config('label_colors').split('{')[1]
     colors = ast.literal_eval(colors_id)

     return colors[label]


def read_config(label):
     '''
     Reads the line of the config file that starts
     with the parameter label.
     :return line: line of the config file
     '''
     
     found_line = None
     with open('config.txt', 'r') as f:
          for line in f.readlines():
               if line.startswith(label):
                    found_line = line

     if found_line == None:
          raise ValueError('Label {} not found in the config file'.format(label))

     return found_line


def init_buttons(window, panel_width, df_path, labels):
     '''
     This function creates all the buttons in the annotation screen.
     '''

     # Add "Prev Image" and "Next Image" buttons    
     prev_im_btn = QtWidgets.QPushButton("Prev", window)
     prev_im_btn.move(panel_width + 20, 780)
     prev_im_btn.clicked.connect(window.show_prev_image)

     next_im_btn = QtWidgets.QPushButton("Next", window)
     next_im_btn.move(panel_width+120, 780)
     next_im_btn.clicked.connect(window.show_next_image)

     # Add "Paint polyp" button
     paint_polyp_btn = QtWidgets.QPushButton("Paint polyp", window)
     paint_polyp_btn.move(panel_width + 75, 650)
     paint_polyp_btn.clicked.connect(window.draw_polyp)

     # Add "Reset boxes" button
     reset_btn = QtWidgets.QPushButton("Reset boxes", window)
     reset_btn.move(panel_width + 75, 710)
     reset_btn.clicked.connect(window.reset_box)

     # Add "Open" button to load a new file
     open_file = QtWidgets.QPushButton("Open", window)
     open_file.move(panel_width + 60, 980)
     open_file.clicked.connect(window.openFile)
     open_file.setObjectName("blueButton")

     # Add "Prev Image" and "Next Image" keyboard shortcuts
     prev_im_kbs = QShortcut(QKeySequence("p"), window)
     prev_im_kbs.activated.connect(window.show_prev_image)

     next_im_kbs = QShortcut(QKeySequence("n"), window)
     next_im_kbs.activated.connect(window.show_next_image)

     # Add "Paint polyp" shortcut
     paint_polyp_kbs = QShortcut(QKeySequence("d"), window)
     paint_polyp_kbs.activated.connect(window.draw_polyp)

     # Add "Reset box" shortcut
     reset_kbs = QShortcut(QKeySequence("r"), window)
     reset_kbs.activated.connect(window.reset_box)

     # Add "generate csv file" button
     next_im_btn = QtWidgets.QPushButton("Generate csv", window)
     next_im_btn.move(panel_width + 60, 940)
     next_im_btn.clicked.connect(lambda state, filename=df_path: window.generate_csv(filename))
     next_im_btn.setObjectName("blueButton")

     # Add "Jump" button
     jump_btn = QtWidgets.QPushButton("Jump", window)
     jump_btn.move(panel_width + 75, 110)
     jump_btn.clicked.connect(window.toJump)

     # create button for each label except for polyp
     if 'polyp' in labels:
          labels_without_polyp = []
          for l in labels:
               if l != 'polyp':
                    labels_without_polyp.append(l)
     else:
          labels_without_polyp = labels

     label_buttons = []
     for i, label in enumerate(labels_without_polyp):
          label_buttons.append(QtWidgets.QPushButton(label, window))
          button = label_buttons[i]
          button.clicked.connect(lambda state, x=label: window.set_label(x))
          window.formLayout_gs.addRow(button)

     return label_buttons


def position_widgets(window, img_panel_width, img_panel_height):

     # video name headline
     window.video_name_headline.setGeometry(img_panel_width + 5, 5, 45, 20)
     window.video_name_headline.setObjectName('headline')

     # video name label
     window.video_name_label.setGeometry(img_panel_width + 5, 23, 220, 20)

     # frame number headline
     window.frame_number_headline.setGeometry(img_panel_width + 5, 50, 50, 20)
     window.frame_number_headline.setObjectName('headline')

     # frame number label
     window.frame_number_label.setGeometry(img_panel_width + 70, 50, 45, 20)

     # Draw polyp message
     window.draw_polyp_message.setGeometry(img_panel_width + 5, 680, 150, 20)
     window.draw_polyp_message.setObjectName('headline')

     # jump to label
     window.jumpto.setGeometry(img_panel_width + 5, 75, 60, 20)
     window.jumpto.setObjectName('headline')

     # jump to editline user
     window.jumpto_user.setGeometry(img_panel_width + 70, 75, 150, 25)

     # Error message jump
     window.error_message.setGeometry(img_panel_width + 27, 140, 500, 25)
     window.error_message.setStyleSheet('color: red; font-weight: bold; size')

     # Label of "Change image"
     window.change_image.setGeometry(img_panel_width + 5, 750, 220, 20)
     window.change_image.setObjectName('headline')

     # message that csv was generated
     window.csv_generated_message.setGeometry(img_panel_width + 30, 1000, 1200, 20)
     window.csv_generated_message.setStyleSheet('color: #43A047')

     # Initiate the ScrollAreas AI and position them
     window.scroll_gs.setGeometry(img_panel_width + 5 , 330, 220, 300)
     window.scroll_ai.setGeometry(img_panel_width + 5, 175, 220, 150)

     # draw line for better UX
     ui_line = QLabel(window)
     ui_line.setGeometry(img_panel_width + 230, 0, 1, img_panel_height)
     ui_line.setStyleSheet('background-color: black')


def your_annotations_plot(window, labels, img_panel_width):

     plot = pg.PlotWidget(window)
     plot.setTitle("Your annotations", color="black", size="15pt")
     plot.setGeometry(img_panel_width + 227, 5, 265, 1015)
     plot.setBackground((240,240,240,255)) # Set color to same background
     #self.plot.hideAxis('bottom')
     #self.plot.hideAxis('left')
     plot.setXRange(0, len(labels))
     
     x_axis = plot.getAxis('bottom')
     x_axis.setLabel('Labels')
     font = QFont()
     font.setPointSize(7)
     x_axis.setStyle(tickFont=font)

     y_axis = plot.getAxis('left')
     font = QFont()
     font.setPointSize(6)
     y_axis.setStyle(tickFont=font)
     #y_axis.tickTextOffset = 0

     # Create a ScatterPlotItem for each label except polyp
     plot_items = {}

     x_ticks = [[(0, 'AI')]]
     for i, label in enumerate(labels):
          x_ticks[0].append((i+1, label))
          if label != 'polyp':
               # Create ScatterPlotItem for goldstandard annotation
               plot_items[label + '_start'] = pg.ScatterPlotItem()
               plot.addItem(plot_items[label + '_start'])

               plot_items[label + '_stop'] = pg.ScatterPlotItem()
               plot.addItem(plot_items[label + '_stop'])

               # Create ScatterPlotItem for AI
               plot_items[label] = {'scatter':pg.ScatterPlotItem(), 'color': label_color(label)}
               plot.addItem(plot_items[label]['scatter'])

          else:
               # Create ScatterPlotItem for polyp for goldstandard annotation
               plot_items[label + '_gs'] = pg.ScatterPlotItem()
               plot.addItem(plot_items[label + '_gs'])

               # Create ScatterPlotItem for polyp AI
               plot_items[label] = {'scatter':pg.ScatterPlotItem(), 'color': label_color(label)}
               plot.addItem(plot_items[label]['scatter'])

     x_axis.setTicks(x_ticks)

     return plot, plot_items