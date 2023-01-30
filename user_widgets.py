from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QPen, QFont, QBrush
from PyQt5.QtWidgets import QLabel, QCheckBox, QShortcut, QGridLayout, QPushButton

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

import ast
import numpy as np

def init_label_checkboxes(window):
     '''
     Reads the labels to annotate written in the config file and
     creates the label radio buttons that appear in the init GUI.
     :param window: The PyQt5 window object
     '''

     # Open the config file
     labels_to_annotate = []
     extra_labels = []

     labels_to_annotate = ast.literal_eval('[' + read_config('labels_to_annotate').split('[')[1])
     extra_labels = ast.literal_eval('[' + read_config('extra_labels').split('[')[1])
     
     grid = QGridLayout(window)

     positions = []
     row = 0
     for _ , label in enumerate(labels_to_annotate + extra_labels):
          remainder = _%5
          if remainder == 4:
               positions.append((row, remainder))
               row+=1 
          else:
               positions.append((row, remainder))

     checkboxes = {}
     for position, label in zip(positions,labels_to_annotate + extra_labels):
          checkbox = QCheckBox(label, window)
          if label in labels_to_annotate:
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

     if colors[label] == 'green':
          pyqt_color = Qt.green
     elif colors[label] == 'red':
          pyqt_color = Qt.red
     elif colors[label] == 'blue':
          pyqt_color = Qt.blue
     elif colors[label] == 'magenta':
          pyqt_color = Qt.magenta
     elif colors[label] == 'cyan':
          pyqt_color = Qt.cyan
     elif colors[label] == 'yellow':
          pyqt_color = Qt.yellow
     elif colors[label] == 'gray':
          pyqt_color = Qt.gray
     elif colors[label] == 'black':
          pyqt_color = Qt.black
     else:
          raise ValueError('This color is not possible')

     return colors[label], pyqt_color


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


def init_buttons(window, panel_width, df_path, labels, spacing):
     '''
     This function creates all the buttons in the annotation screen.
     '''

     # Add "Paint polyp" button
     paint_polyp_btn = QPushButton("Paint polyp", window)
     paint_polyp_btn.move(panel_width +  spacing + 75, 590)
     paint_polyp_btn.clicked.connect(window.draw_polyp)

     # Add "Reset boxes" button
     reset_btn = QPushButton("Reset boxes", window)
     reset_btn.move(panel_width +  spacing + 72, 620)
     reset_btn.clicked.connect(window.reset_box)   

     # Add "Prev Image" and "Next Image" buttons    
     prev_im_btn = QPushButton("Prev", window)
     prev_im_btn.move(panel_width +  spacing + 20, 675)
     prev_im_btn.clicked.connect(window.show_prev_image)

     next_im_btn = QPushButton("Next", window)
     next_im_btn.move(panel_width +  spacing + 120, 675)
     next_im_btn.clicked.connect(window.show_next_image)

     # Add "Prev Image" and "Next Image" keyboard shortcuts
     prev_im_kbs = QShortcut(QKeySequence("b"), window)
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
     next_im_btn = QPushButton("Generate csv", window)
     next_im_btn.move(panel_width +  spacing + 5, 1005)
     next_im_btn.clicked.connect(lambda state, filename=df_path: window.generate_csv(filename))
     next_im_btn.setObjectName("blueButton")

     # Add "Open" button to load a new file
     open_file = QPushButton("Open", window)
     open_file.move(panel_width +  spacing + 120, 1005)
     open_file.clicked.connect(window.openFile)
     open_file.setObjectName("blueButton")

     # Create button for each instrument to include in "Resection" scroll bar
     instruments = ast.literal_eval('[' + read_config('instruments').split('[')[1])
     
     instrument_buttons = []
     for i, instrument in enumerate(instruments):
          instrument_buttons.append(QPushButton(instrument, window))
          inst = instrument_buttons[i]
          inst.clicked.connect(lambda state, x=instrument, y=inst: window.set_label(x, y))
          window.formLayout_resection.addRow(inst)


     # create button for each label except for polyp because is annotated differently
     if 'polyp' in labels:
          labels_without_polyp = []
          for l in labels:
               if l != 'polyp':
                    labels_without_polyp.append(l)
     else:
          labels_without_polyp = labels

     label_buttons = []
     for i, label in enumerate(labels_without_polyp):
          label_buttons.append(QPushButton(label, window))
          button = label_buttons[i]
          button.clicked.connect(lambda state, x=label, y=button: window.set_label(x, button))
          window.formLayout_labels.addRow(button)

     return instrument_buttons, label_buttons


def position_widgets(window, img_panel_width, img_panel_height, spacing):

     # video name headline
     window.video_name_headline.setGeometry(img_panel_width + spacing + 5, 5, 45 + spacing, 20)
     window.video_name_headline.setObjectName('headline')

     # video name label
     window.video_name_label.setGeometry(img_panel_width + spacing + 5, 23, 220 + spacing, 20)

     # frame number headline
     window.frame_number_headline.setGeometry(img_panel_width + spacing + 5, 50, 50 + spacing, 20)
     window.frame_number_headline.setObjectName('headline')

     # frame number label
     window.frame_number_label.setGeometry(img_panel_width + spacing + 70, 50, 45 + spacing, 20)

     # jump to label
     window.jumpto.setGeometry(img_panel_width + spacing + 5, 75, 62, 20)
     window.jumpto.setObjectName('headline')

     # jump to editline user
     window.jumpto_user.setGeometry(img_panel_width + spacing + 71, 75, 150 + spacing, 25)

     # Error message jump
     window.error_message.setGeometry(img_panel_width + spacing + 23, 100, 191 + spacing, 25)
     window.error_message.setStyleSheet('color: red; font-weight: bold; size')

     # Label "Your Annotations"
     window.your_annotations.setGeometry(img_panel_width + 2*spacing + 50, 225, 150, 15)
     window.your_annotations.setObjectName('headline')

     # Draw polyp message "Press button to draw polyp"
     window.draw_polyp_message.setGeometry(img_panel_width + spacing + 5, 565, 200 + spacing, 15)
     window.draw_polyp_message.setObjectName('headline')

     # Label of "Change image"
     window.change_image.setGeometry(img_panel_width + spacing + 5, 650, 220 + spacing, 20)
     window.change_image.setObjectName('headline')

     # Label "Comments:":
     window.comment_label.setGeometry(img_panel_width +  spacing + 5, 710, 150 + spacing, 15)
     window.comment_label.setObjectName('headline')

     # Editline "insert_comment":
     window.insert_comment.setGeometry(img_panel_width +  spacing + 5, 730, 220 + spacing, 25)

     # message that csv was generated
     window.csv_generated_message.setGeometry(img_panel_width +  spacing + 5, 1032, 1200 + spacing, 20)
     window.csv_generated_message.setStyleSheet('color: #43A047')

     # Initiate the ScrollAreas AI and position them
     window.scroll_ai.setGeometry(img_panel_width +  spacing + 5, 125, 220 + spacing, 95)
     window.scroll_resection.setGeometry(img_panel_width +  spacing + 5 , 245, 220 + spacing, 165)
     window.scroll_labels.setGeometry(img_panel_width +  spacing + 5, 415, 220 + spacing, 135)

     # draw line for better UX
     ui_line = QLabel(window)
     ui_line.setGeometry(img_panel_width +  3*spacing + 230, 0, 1, img_panel_height)
     ui_line.setStyleSheet('background-color: black')

def draw_legend(painter, img_panel_width, instruments, labels_to_annotate, labels_to_plot, spacing):
     
     # Titles:
     painter.setFont(QFont("SansSerif", 10, QFont.Bold))
     painter.drawText(img_panel_width +  spacing + 58, 785, 'PLOT LEGEND')
     
     painter.setFont(QFont("SansSerif", 10))
     painter.drawText(img_panel_width +  spacing + 5, 805, 'AI:')
     painter.drawText(img_panel_width +  spacing + 115, 805, 'Resection:')
     painter.drawText(img_panel_width +  spacing + 77, 920, 'Labels')
     #painter.setBrush(QBrush(Qt.black, 5, Qt.SolidPattern))
     
     # For AI
     resection = ["snare", "grasper", "polyp"]

     for i, label in enumerate(labels_to_plot):
          # Do not show more than 7 labels
          if i==7:
               break
          
          # Show only resection labels
          if label in resection:
               # Text
               painter.drawText(img_panel_width +  spacing + 20, 825 + (i*20), label)
               # Box
               painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
               painter.setBrush(QBrush(label_color(label)[1]))
               painter.drawRect(img_panel_width +  spacing + 5, 815 + (i*20), 10, 10)
     

     # Show only coecum for localisation labels one time
     # Text
     painter.drawText(img_panel_width +  spacing + 20, 825 + (len(resection) *20), 'coecum')
     # Box
     painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
     painter.setBrush(QBrush(Qt.black))
     painter.drawRect(img_panel_width +  spacing + 5, 815 + (len(resection)*20), 10, 10)

     # For resection labels
     for i, instrument in enumerate(instruments):
          # Text
          painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))
          painter.drawText(img_panel_width +  2*spacing + 130, 825 + (i*20), instrument)

          # Box
          painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
          painter.setBrush((label_color(instrument)[1]))
          painter.drawRect(img_panel_width +  2*spacing + 115, 815 + (i*20), 10, 10)

     #For labels to annotate
     for i, label in enumerate(labels_to_annotate):
          label_name = label if label != 'start_withdrawal' else 'withdrawal'
          
          if i < 2:
               # Text
               painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))
               painter.drawText(img_panel_width +  spacing + 20, 945 + (i*20), label_name)

               # Box
               painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
               painter.setBrush((label_color(label)[1]))
               painter.drawRect(img_panel_width +  spacing + 5, 935 + (i*20), 10, 10)
          else:
               # Text
               painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))
               painter.drawText(img_panel_width +  2*spacing + 130, 945 + ((i-2)*20), label_name)

               # Box
               painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
               painter.setBrush((label_color(label)[1]))
               painter.drawRect(img_panel_width +  2*spacing + 115, 935 + ((i-2)*20), 10, 10)




def your_annotations_plot(window, instruments, labels_to_annotate, labels_to_plot, img_panel_width, spacing):
     plot = pg.PlotWidget(window)
     plot.setTitle("Your annotations", color="black", size="15pt", position='bottom')
     plot.setGeometry(img_panel_width + 3*spacing + 235, 10, 265, 1040)
     plot.setBackground((240,240,240,255)) # Set color to same background
     #self.plot.hideAxis('bottom')
     #self.plot.hideAxis('left')
     # We set the name of the x_ticks in x axis
     x_ticks = [[(0, 'AI resection'), (1, 'AI location'), (2, 'Resection'), (3, 'Labels')]]
     plot.setXRange(0, len(x_ticks[0])-1)
     
     # Reverse y axis
     plot.getPlotItem().invertY(True)
     
     x_axis = plot.getAxis('bottom')
     # x_axis.setLabel('Labels')
     font = QFont()
     font.setPointSize(8)
     x_axis.setStyle(tickFont=font)

     y_axis = plot.getAxis('left')
     font = QFont()
     font.setPointSize(8)
     y_axis.setStyle(tickFont=font)

     # Create a ScatterPlotItem for AI resection, AI location, Resection and Labels
     plot_items = {'AI':{},
                   'resection':{},
                   'label':{}
                   }
     
     # For AI resection and AI location
     for label in labels_to_plot:
          plot_items['AI'][label] = {'scatter':pg.ScatterPlotItem(), 'color': label_color(label)[0]}
          plot.addItem(plot_items['AI'][label]['scatter'])
     
     # For resection/instrument annotation
     for instrument in instruments:
          plot_items['resection'][instrument] = {'scatter':pg.ScatterPlotItem(), 'color': label_color(instrument)[0]}
          plot.addItem(plot_items['resection'][instrument]['scatter'])

     # For label annotations
     for label in labels_to_annotate:
          plot_items['label'][label] = {'scatter':pg.ScatterPlotItem(), 'color': label_color(label)[0]}
          plot.addItem(plot_items['label'][label]['scatter'])

     x_axis.setTicks(x_ticks)

     return plot, plot_items


def ai_plot(df, plot_items):
     '''
     This creates the AI plot in the initialization
     It is distributed in two:
          - AI resection: snare, grasper, polyp
          - AI localisation: ileum, appendix, ileocaecalvalve
     '''

     resection = ["snare", "grasper", "polyp"]
     localisation = ["ileum", "appendix", "ileocaecalvalve"]

     for label in plot_items['AI']:
          if label in resection:
               positive = df.query(f'{label} == 1')['frame_integers'].values
               if len(positive)>0:
                    x_array = np.repeat(0, len(positive))
                    y_array = np.array(positive, dtype=int)
                    pen=pg.mkPen(color=plot_items['AI'][label]['color'], width=0.5)
                    brush=pg.mkBrush(plot_items['AI'][label]['color'])
                    plot_items['AI'][label]['scatter'].setData(x=x_array, y=y_array, size=5, brush=brush, pen=pen)
                    plot_items['AI'][label]['scatter'].update()

          if label in localisation:
               positive = df.query(f'{label} == 1')['frame_integers'].values
               if len(positive)>0:
                    x_array = np.repeat(1, len(positive))
                    y_array = np.array(positive, dtype=int)
                    pen=pg.mkPen(color=plot_items['AI'][label]['color'], width=0.5)
                    brush=pg.mkBrush(plot_items['AI'][label]['color'])
                    plot_items['AI'][label]['scatter'].setData(x=x_array, y=y_array, size=5, brush=brush, pen=pen)
                    plot_items['AI'][label]['scatter'].update()