import os
import pandas as pd
import numpy as np
import ast
import time

from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPixmap, QPainter, QPen, QFont, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QScrollArea, \
     QGroupBox, QFormLayout, QTableWidget, QStyle, QStyleOptionTitleBar

import pyqtgraph as pg

import read_data
import user_widgets
import transform_coord
import init


def make_folder(directory):
    """
    :param directory: The folder destination path
    :return: 
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


class LabelerWindow(QWidget):
    def __init__(self, df, input_folder, labels, metadata, img_paths):
        super().__init__()

        # init UI state
        self.title = 'PyQt5 - Box annotation tool'
        self.original_resolution = metadata['original_resolution']
        self.cropping_coordinates = metadata['cropping_coordinates']
        self.width_without_scale = self.cropping_coordinates[3] - self.cropping_coordinates[2]
        self.height_without_scale = self.cropping_coordinates[1] - self.cropping_coordinates[0]
        

        # state variables
        self.df = df
        self.labels = labels
        self.instruments = ast.literal_eval('[' + user_widgets.read_config('instruments').split('[')[1])
        self.counter = 0
        self.input_folder = input_folder
        self.video_name = os.path.split(input_folder)[1] + '.mkv'
        self.img_paths = img_paths
        self.img_root = os.path.split(self.img_paths[0])[0]
        self.num_images = len(self.img_paths)
        self.update_annotations = 1 # When there is a new annotation is set to 1. Otherwise 0. Used to accelerate the program.

        # labels to identify different polyps
        self.paint_activation = 0
        self.polyp_id = 0
        
        # initialize list to save all label buttons
        self.label_buttons = []

        # Get path of the master csv
        self.df_path = os.path.join(input_folder, self.video_name[:-4] + '.csv')

        # Get scale factor and position of the image
        image_attributes = read_data.image_attributes((self.width_without_scale, self.height_without_scale))
        self.width = image_attributes['width_scaled']
        self.height = image_attributes['height_scaled']
        self.factor = image_attributes['reduction_factor']
        self.position_image_x = image_attributes['position_x']
        self.position_image_y = image_attributes['position_y']
        
        self.img_panel_width = self.width + self.position_image_x
        self.img_panel_height = self.height + self.position_image_y

        # Initialize Labels
        self.video_name_headline = QLabel('Video: ', self)
        self.video_name_label = QLabel(self.video_name.split('coloscopie_')[-1], self)
        self.video_name_label.setFont(QFont('Arial', 9))
        self.frame_number_headline = QLabel('Frame: ', self)
        self.frame_number_label = QLabel(self)
        self.csv_generated_message = QLabel(self)
        self.draw_polyp_message = QLabel('Press button to draw polyp:', self)
        self.jumpto = QLabel('Jump to: ', self)
        self.your_annotations = QLabel('Your Annotations', self)
        self.comment_label = QLabel('Comments: ', self)
        self.error_message = QLabel(self)
        self.error_message.setFont(QFont('Arial', 9))
        self.change_image = QLabel('Change image: ', self)

        # Jump to QLineEdit
        self.jumpto_user = QLineEdit(self)
        self.jumpto_user.setFocusPolicy(Qt.ClickFocus)
        self.jumpto_user.returnPressed.connect(self.toJump)

        # Insert comment QLinEdit
        self.insert_comment = QLineEdit(self)
        self.insert_comment.setFocusPolicy(Qt.ClickFocus)
        self.insert_comment.returnPressed.connect(self.on_return_pressed)

        ##### SCROLL TO VISUALIZE ANNOTATIONS/PREDICTIONS
        # layouts
        self.formLayout_ai = QFormLayout()
        self.formLayout_resection = QFormLayout()
        self.formLayout_labels = QFormLayout()

        # scroll areas
        self.scroll_ai = QScrollArea(self)
        self.scroll_resection = QScrollArea(self)
        self.scroll_labels = QScrollArea(self)
        
        # GroupBoxs
        self.groupBox_ai = QGroupBox()
        self.groupBox_resection = QGroupBox()
        self.groupBox_labels = QGroupBox()
        self.groupBox_ai.setTitle('AI predictions:')
        self.groupBox_ai.setStyleSheet('font-weight: bold')
        self.groupBox_resection.setTitle('Resection:')
        self.groupBox_resection.setStyleSheet('font-weight: bold')
        self.groupBox_labels.setTitle('Labels:')
        self.groupBox_labels.setStyleSheet('font-weight: bold')
        
        self.groupBox_ai.setLayout(self.formLayout_ai)
        self.scroll_ai.setWidget(self.groupBox_ai)
        self.scroll_ai.setWidgetResizable(True)
 
        self.groupBox_resection.setLayout(self.formLayout_resection)
        self.scroll_resection.setWidget(self.groupBox_resection)
        self.scroll_resection.setWidgetResizable(True)

        self.groupBox_labels.setLayout(self.formLayout_labels)
        self.scroll_labels.setWidget(self.groupBox_labels)
        self.scroll_labels.setWidgetResizable(True)
        
        self.groupBox_ai.setStyleSheet('background: palette(window)')
        self.groupBox_resection.setStyleSheet('background: palette(window)')
        self.groupBox_labels.setStyleSheet('background: palette(window)')

        # Create two point instances
        self.begin, self.destination = QPoint(), QPoint()

        # init UI
        self.init_ui()
        

    def init_ui(self):

        self.titleBarHeight = self.style().pixelMetric(
            QStyle.PM_TitleBarHeight,
            QStyleOptionTitleBar(),
            self
        )
        
        self.setWindowTitle(self.title)
        self.geometry = QApplication.desktop().availableGeometry()
        self.geometry_width = self.geometry.width()
        self.geometry.setHeight(self.geometry.height() - (self.titleBarHeight*2))
        self.setGeometry(self.geometry)
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Read spacing between the objects on the x axis
        self.spacing = int(user_widgets.read_config('spacing').split('=')[1])

        # Position all the widgets in the screen
        user_widgets.position_widgets(self, self.img_panel_width, self.img_panel_height, self.spacing)

        # Getting the frame number
        frame_number_jpg = os.path.split(self.img_paths[self.counter])[-1]
        frame_number = self.df.loc[self.df['frame'] == frame_number_jpg]['frame_integers'].values

        if len(frame_number) > 1:
            raise ValueError('Multiple frames with same frame number?')
        else:
            frame_number = frame_number[0]

        # create buttons
        self.instrument_buttons, self.label_buttons = user_widgets.init_buttons(self, self.img_panel_width, self.df_path, self.labels, self.spacing)

        # apply custom styles
        try:
            styles_path = "./styles.qss"
            with open(styles_path, "r") as fh:
                self.setStyleSheet(fh.read())
        except:
            print("Can't load custom stylesheet.")

        # Set the first image with GS and AI annotations if there are:
        self.annotations = read_data.read_annotations(frame_number, self.labels, self.df,
                                                      self.cropping_coordinates, self.factor, (self.position_image_x, self.position_image_y)
                                                      )

        # Create YOUR ANNOTATIONS plot
        self.plot, self.plot_items = user_widgets.your_annotations_plot(self, self.instruments, self.labels, self.img_panel_width, self.spacing)

        # set a plot and the data for the AI
        user_widgets.ai_plot(self.labels, self.df, self.plot_items)
        self.set_image(self.img_paths[0], self.annotations)

    
    def update_plot(self):
        '''
        This function updates the "Your annotations" plot
        '''
        
        # The x position for plotting data of resection is 1
        for instrument in self.instruments:
            frame_label = self.df.query('resections == @instrument')['frame_integers'].values
            
            if len(frame_label)>0: # If there are points
                x_array = np.repeat(1, len(frame_label))
                y_array = np.array(frame_label, dtype=int)
                pen=pg.mkPen(self.plot_items[instrument]['color'], width=1)
                brush = pg.mkBrush(self.plot_items[instrument]['color'])
                self.plot_items[instrument]['scatter'].setData(x=x_array, y=y_array, size=7, brush=brush, pen=pen)
            else: # If there are no points
                self.plot_items[instrument]['scatter'].setData([])

        
        # The x position for plotting data of AI prediction is 2
        for label in self.labels:
            if label != 'polyp':
                if label + '_gs' in self.df.columns:  
                    # Find if there are "1" which equals to start
                    starts = self.df.query(f"{label+'_gs'}==1")['frame_integers'].values

                    # Find if there are "2" which equals to stop
                    stops = self.df.query(f"{label+'_gs'}==2")['frame_integers'].values

                    # We plot the starts
                    if len(starts)>0:
                        x_array = np.repeat(2, len(starts))
                        y_array = np.array(starts, dtype=int)
                        pen=pg.mkPen(color=(0,200,0), width=3)
                        brush = pg.mkBrush(self.plot_items[label]['color'])
                        self.plot_items[label + '_start'].setData(x=x_array, y=y_array, size=7, brush=brush, pen=pen)
                    else:
                        self.plot_items[label + '_start'].setData([])
      
                    # We plot the ends
                    if len(stops)>0:
                        x_array = np.repeat(2, len(stops))
                        y_array = np.array(stops, dtype=int)
                        pen=pg.mkPen(color='r', width=3)
                        brush = pg.mkBrush(self.plot_items[label]['color'])
                        self.plot_items[label + '_stop'].setData(x=x_array, y=y_array, size=7, brush=brush, pen=pen)
                    else:
                        self.plot_items[label + '_stop'].setData([])

            else:
                if 'polyp_gs' in self.df.columns:
                    mask = pd.notnull(self.df['polyp_gs'])
                    frames_without_none = self.df[mask]['frame_integers'].values
                         
                    if len(frames_without_none)>0:
                        x_array = np.repeat(2, len(frames_without_none))
                        y_array = np.array(frames_without_none, dtype=int)
                        pen=pg.mkPen((0,255,0), width=3)
                        brush = pg.mkBrush((0,255,0))
                        self.plot_items['polyp_gs'].setData(x=x_array, size=7, y=y_array, brush=brush, pen=pen)
                    else:
                        self.plot_items['polyp_gs'].setData([])

        self.plot_items[instrument]['scatter'].update()     


    def draw_polyp(self):
        '''
        When a kbs is pressed, allows the user to draw the polyp
        '''
        # Activate the event function to draw
        self.paint_activation = 1

        # Show a label
        self.draw_polyp_message.setText('Select polyp ID')

        # Annotations will need to be updated
        self.update_annotations = 1


    def toJump(self):

        # Retrieve value from QLineEdit
        frame_number = self.jumpto_user.text()
        
        try:
            # Check it is a number
            frame_number_int = int(frame_number)
            
            # Because we have not all the frames numbers, we need to
            # find the closest one
            closest_index = (self.df['frame_integers'] - frame_number_int).abs().idxmin()
            path = os.path.join(self.img_root, self.df.at[closest_index, 'frame'])
            frame_number_int = self.df.at[closest_index, 'frame_integers']

            # Check if the path exists:
            if path in self.img_paths:
                
                # Reinitialize texts and variables of draw polyp
                self.draw_polyp_message.setText('')
                self.paint_activation = 0

                # Store the current coordinates if there has been any update
                if self.update_annotations == 1:
                    self.store_annotations()

                # Read the AI predictions and if there are previous annotated GS labels
                self.annotations = read_data.read_annotations(frame_number_int, self.labels, self.df,
                                                      self.cropping_coordinates, self.factor, (self.position_image_x, self.position_image_y)
                                                      )
                
                # Update the self.counter
                self.counter = self.img_paths.index(path)

                # Set the image
                self.set_image(path, self.annotations) 
                
                message = 'Jump to closest image {}'.format(str(frame_number_int) + '.jpg')
                self.error_message.setText(message)
                self.draw_polyp_message.setText('Press button to draw polyp:')

                self.jumpto_user.clearFocus()
            else:
                message = 'Frame number {} does not exist'.format(frame_number)
                self.error_message.setText(message)
            
        except ValueError:
            message = 'Must be an integer. Ex: 27134'
            self.error_message.setText(message)

    def on_return_pressed(self):
        '''
        This function is called when the Return button
        in the user comment section is pressed.
        We need to store the data that the user inputs.
        '''
        
        # Obtain the index of dataframe
        frame_number_string = os.path.split(self.img_paths[self.counter])[-1]
        
        # index of the frame number of the database
        df_index = self.df[self.df['frame'] == frame_number_string].index[0]
        
        # Store data
        user_comment_data = self.insert_comment.text()
        self.df.at[df_index, 'comment'] = user_comment_data
        
        # Clear the QLineEdit entry line
        self.insert_comment.clear()
        self.insert_comment.clearFocus()
    

    def show_next_image(self):
        """
        calls method to store coordinates drawn in pandas dataframe
        calls method to update the annotations overview (pending)
        loads and shows next image in dataset
        """
        
        ##### Reinitialize texts and variables of draw polyp
        self.draw_polyp_message.setText('Press button to draw polyp:')
        self.paint_activation = 0

        # and toJump function
        self.error_message.setText('')
        
        ##### Store the annotations / coordinates on the image (not the next image) if there has been an update
        if self.update_annotations == 1:
            self.store_annotations()

        ##### LOAD THE NEW IMAGE WITH THE PREVIOUS ANNOTATIONS
        if self.counter < self.num_images -1:
            self.counter += 1
            
            path = self.img_paths[self.counter]
            filename = os.path.split(path)[-1]
            frame_number = int(filename.split('.')[0])
            
            # Read the AI predictions and if there are previous annotated GS labels
            self.annotations = read_data.read_annotations(frame_number, self.labels, self.df,
                                                      self.cropping_coordinates, self.factor, (self.position_image_x, self.position_image_y)
                                                      )

            # Set the image
            self.set_image(path, self.annotations) 
    

    def show_prev_image(self):
        """
        calls method to store coordinates drawn
        loads and shows previous image in dataset
        """

        # Reinitialize texts and variables of draw polyp
        self.draw_polyp_message.setText('Press button to draw polyp:')
        self.paint_activation = 0

        # and toJump function
        self.error_message.setText('')
        
        # Store the annotations / coordinates on the image (of the actual image) if there has been an update
        if self.update_annotations == 1:
            self.store_annotations()
        
        # Check if it is the first image
        if self.counter > 0:
            self.counter -= 1

            if self.counter < self.num_images:
                
                # Load the new image with the previous annotations
                path = self.img_paths[self.counter]
                filename = os.path.split(path)[-1]
                frame_number = int(filename.split('.')[0])
                
                # Read the AI predictions and if there are previous annotated GS labels
                self.annotations = read_data.read_annotations(frame_number, self.labels, self.df,
                                                      self.cropping_coordinates, self.factor, (self.position_image_x, self.position_image_y)
                                                      )
                # Set the image
                self.set_image(path, self.annotations)                 

    def store_annotations(self):
        '''
        stores the current annotations to the database
        stores the current coordinates of each polyp
        '''
        
    
        ##### ANNOTATIONS
        # We obtain the frame number as a string because dtype in df of "frame" is object
        frame_number = os.path.split(self.img_paths[self.counter])[-1]
        
        # index of the frame number of the database
        #df_index = self.df[self.df['frame'] == frame_number].index[0]
        df_index = self.df.query("frame == '{}'".format(frame_number)).index[0]

        for key, value in self.annotations['gs_annotations'].items():
            if key != 'polyp':
                if value:
                    self.df.at[df_index, '{}_gs'.format(key)] = int(value)
                else:
                    self.df.at[df_index, '{}_gs'.format(key)] = None

        ##### COORDINATES (bounding boxes)
        # If there is any annotation
        if 'polyp' in self.annotations['gs_annotations']:      
            coordinates = self.annotations['gs_annotations']['polyp']

            # rescale and reorient the coordinates from p2p to original coordinates
            rescaled_coordinates = transform_coord.pqp2original(coordinates, self.cropping_coordinates,
                                                                self.factor, (self.position_image_x, self.position_image_y)
            )
            self.df.at[df_index, 'polyp_gs'] = rescaled_coordinates
        else:
            self.df.at[df_index, 'polyp_gs'] = None

        #### STORE RESECTION DATA
        self.df.at[df_index, 'resections'] = self.annotations['resections']


    def set_image(self, path, annotations):
        """
        displays the image in GUI
        :param path: path to the image that should be show
        :param annotations: contains the annotations and predictions that need to be drawn or shown.
        :param from_scroll: True if the image has been set by clicking the annotations_pending scroll tab
        """
      
        ##### UPDATE IMAGE      
        # Image scaled in height to make sure is entirely displayed laptops.
        self.pix = QPixmap(path)
        self.pix = self.pix.scaledToHeight(self.height)

        #### UPDATE COORDINATE ANNOTATIONS
        # Coordinates need to be drawn in case of polyp annotations
        # The bounding boxes will be drawn with different pen colors depending on the id of the polyp
        if 'polyp' in annotations['gs_annotations']:
            painterInstance = QPainter(self.pix)
            # '[(1, (x,y,width,height)), (2, (x,y,width,height))]'
            for polyp in annotations['gs_annotations']['polyp']:
                polyp_id = polyp[0]
                coordinates = polyp[1]
                penRectangle = QPen(user_widgets.colors_polyp(polyp[0]), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painterInstance.setPen(penRectangle)
                rect = QRect(coordinates[0], coordinates[1], coordinates[2], coordinates[3])
                painterInstance.drawRect(rect)
            

        ##### CALL FOR UPDATE PREDICTIONS SCROLL BAR
        self.predictions_overview(self.annotations)

        ##### OTHER INFO
        # Set the frame number of the image displayed
        frame_number = os.path.split(self.img_paths[self.counter])[-1][:-4]
        if frame_number=='0000000':
            frame_number = '0'
        else:
            frame_number = frame_number.lstrip('0')

        self.frame_number_label.setText(frame_number)
        # we need to find the value of self.counter for the image
        self.counter = self.img_paths.index(path)
        # Mark in green the buttons
        self.set_button_color()

        # Update annotation plot only if there have been annotations
        if self.update_annotations == 1:
            self.update_plot()

        self.update_annotations = 0
        
        self.update()
    
    
    def predictions_overview(self, annotations):
        '''
        Creates a scroll tab overview of the AI predictions
        :param annotations: self explanatory
        '''
        
        # First delete the previous labels on the layout
        for i in reversed(range(self.formLayout_ai.count())): 
            self.formLayout_ai.itemAt(i).widget().setParent(None)
        
        # Add new labels on the layout
        for label in annotations['ai_predictions']:
            # append widgets to lists
            label = QLabel(label, self)
            self.formLayout_ai.addRow(label)

            
    def set_label(self, label, button_object):
        """
        When button of the labels (Resection and Labels) are pressed,
        it stores the value in self.annotations in the following way:
        - Resection: string of the button.text
        - Labels:
            > 0: Means that there is no annotation of the label
            > 1: Start of the label (first appearance of the label)
            > 2: End of the label (last appearance of the label)
            The function iterates according to the previous. From 0 to 1 to 2.
        
        :param label: selected label
        """
        
        # Has the user pressed any button of the resection?
        if button_object in self.instrument_buttons:
            if label == self.annotations['resections']:
                # Then it means that the user wants to unselect it
                self.annotations['resections'] = None
            else:
                self.annotations['resections'] = label

        # Has the user pressed any button of the labels?
        if button_object in self.label_buttons:
            if label in self.annotations['gs_annotations'].keys():
                # Then it can be two things, green to red or red to none
                if self.annotations['gs_annotations'][label] == 1:
                    self.annotations['gs_annotations'][label] = 2
                elif self.annotations['gs_annotations'][label] == 2:
                    self.annotations['gs_annotations'][label] = None
                else:
                    self.annotations['gs_annotations'][label] = 1
            else:
                self.annotations['gs_annotations'][label] = 1
  
        
        self.set_button_color()
        self.update_annotations = 1


    def set_button_color(self):
        """
        Changes the color of the button which corresponds to selected label
        """
        
        for button in self.label_buttons:
            if button.text() in self.annotations['gs_annotations'].keys():
                if self.annotations['gs_annotations'][button.text()] == 1:
                    button.setStyleSheet('border: 3px solid #43A047; background-color: #4CAF50; color: white')
                elif self.annotations['gs_annotations'][button.text()] == 2:
                    button.setStyleSheet('border: 3px solid #FF0000; background-color: #FF0000; color: white')
                else:
                    button.setStyleSheet('background-color: None')
            else:
                button.setStyleSheet('background-color: None')

        # Now for the resections part
        for button in self.instrument_buttons:
            if self.annotations['resections'] == button.text():
                button.setStyleSheet('border: 3px solid #43A047; background-color: #4CAF50; color: white')
            else:
                button.setStyleSheet('background-color: None')


    def reset_box(self):
        '''
        Present the current image without boxes
        Remove the coordinate boxes from the master database
        '''

        # Load the new image with the previous annotations
        path = self.img_paths[self.counter]
        filename = os.path.split(path)[-1]

        # Reset the boxes
        if 'polyp' in self.annotations['gs_annotations']:
            del self.annotations['gs_annotations']['polyp']

        # Store the annotations
        self.store_annotations()

        # Set the image
        self.set_image(path, self.annotations) 


    def paintEvent(self, event):
        
        # Draw a black rectangle for the background
        painter = QPainter(self)
        #painter.begin(self)
        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))
        painter.drawRect(0, 0, self.img_panel_width, self.img_panel_height)
        
        # Draw the image
        painter.drawPixmap(QPoint(self.position_image_x, self.position_image_y), self.pix)

        # DRAW THE LEGEND
        user_widgets.draw_legend(painter, self.img_panel_width, self.instruments, self.labels, self.spacing)

        # To draw the coordinates of mouse events
        if self.paint_activation == 1 and self.polyp_id != 0:
            #if not self.begin.isNull() and not self.destination.isNull():
            if ((abs(self.begin.x() - self.destination.x()) > 10) and (abs(self.begin.x() - self.destination.x()) > 10)):
                try:
                    pen = QPen(user_widgets.colors_polyp(self.polyp_id), 3, Qt.DashDotLine, Qt.RoundCap, Qt.RoundJoin)
                except KeyError:
                    pen = QPen(Qt.green, 3, Qt.DashDotLine, Qt.RoundCap, Qt.RoundJoin)
                
                painter.setPen(pen)
                rect = QRect(self.begin, self.destination)
                painter.drawRect(rect.normalized())

        painter.end()


    def mousePressEvent(self, event):
        if self.paint_activation == 1 and self.polyp_id != 0:
            if event.buttons() & Qt.LeftButton:
                self.begin = event.pos()
                self.destination = self.begin
                self.update()
        
    def mouseMoveEvent(self, event):     
        if self.paint_activation == 1 and self.polyp_id != 0:
            if event.buttons() & Qt.LeftButton:
                self.destination = event.pos()
                self.update()

    def mouseReleaseEvent(self, event):  
        if self.paint_activation == 1 and self.polyp_id != 0:
            if event.button() & Qt.LeftButton:
                # Print the rectangle only in case is bigger than a threshold:
                if ((abs(self.begin.x() - self.destination.x()) > 10) and (abs(self.begin.x() - self.destination.x()) > 10)):
                    # Update begin and destination because of the movement of centering the screen
                    self.begin += QPoint(-self.position_image_x, -self.position_image_y)
                    self.destination += QPoint(-self.position_image_x, -self.position_image_y)
                    
                    rect = QRect(self.begin, self.destination)
                    painter = QPainter(self.pix)
                    try:
                        pen = QPen(user_widgets.colors_polyp(self.polyp_id), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                    except KeyError:
                        pen = QPen(Qt.green, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                    
                    painter.setPen(pen)
                    painter.drawRect(rect.normalized())
                    # Coordinates need to be stored as [(1, (x,y,width,height)), (2, (x,y,width,height))]
                    # Check if exists in annotations
                    if 'polyp' in self.annotations['gs_annotations']:
                        self.annotations['gs_annotations']['polyp'].append((self.polyp_id,
                                            (rect.normalized().x(), rect.normalized().y(),
                                            rect.normalized().width(), rect.normalized().height()
                                            )
                                            )
                        )
                    else:
                        self.annotations['gs_annotations']['polyp'] = [(self.polyp_id,
                                            (rect.normalized().x(), rect.normalized().y(),
                                            rect.normalized().width(), rect.normalized().height()
                                            )
                        )]

                    self.polyp_id = 0 # Make the user select again a polyp id
                    self.draw_polyp_message.setText('Select polyp ID') # and inform him/her
                    self.begin, self.destination = QPoint(), QPoint()
                    self.update()

    def keyPressEvent(self, e):
        # If the user has pressed "paint polyp"
        if self.paint_activation == 1:
            if e.key()  == Qt.Key_1:
                self.polyp_id = 1
                self.draw_polyp_message.setText('Polyp 1 selected')
            elif e.key() == Qt.Key_2:   
                self.polyp_id = 2
                self.draw_polyp_message.setText('Polyp 2 selected')
            elif e.key() == Qt.Key_3:   
                self.polyp_id = 3
                self.draw_polyp_message.setText('Polyp 3 selected')
            elif e.key() == Qt.Key_4:   
                self.polyp_id = 4
                self.draw_polyp_message.setText('Polyp 4 selected')
            elif e.key() == Qt.Key_5:   
                self.polyp_id = 5
                self.draw_polyp_message.setText('Polyp 5 selected')
            elif e.key() == Qt.Key_6:   
                self.polyp_id = 6
                self.draw_polyp_message.setText('Polyp 6 selected')
            elif e.key() == Qt.Key_7:   
                self.polyp_id = 7
                self.draw_polyp_message.setText('Polyp 7 selected')
            elif e.key() == Qt.Key_8:   
                self.polyp_id = 8
                self.draw_polyp_message.setText('Polyp 8 selected')
            elif e.key() == Qt.Key_9:   
                self.polyp_id = 9
                self.draw_polyp_message.setText('Polyp 9 selected')
            else:
                print('Please, press a digit (1-9)')
                self.polyp_id = 0


    def openFile(self):
        """
        This function opens a new file.
        """
        self.close()
        self.m = init.SetupWindow()
        self.m.show()
        
        
    def closeEvent(self, event):
        """
        This function is executed when the app is closed.
        It automatically generates csv file in case the user forgot to do that
        """
        print("closing the App..")
        self.generate_csv(self.df_path)

    
    def generate_csv(self, out_filename):
        """
        Reads from the subset polyp dataframe all the annotations that have been done
        and stores them in the master dataframe
        :param out_filename: name of csv file to be generated
        """

        # Save different versions
        path_to_save = os.path.join(self.input_folder, 'output')
        make_folder(path_to_save)

        timestr = time.strftime("%Y-%m-%d_%H-%M-%S_")
        csv_file_path = path_to_save + '/' + timestr + os.path.split(out_filename)[-1]

        self.df.to_csv(csv_file_path)

        # Drop column frame_integers because no longer needed
        self.df.drop('frame_integers', axis=1, inplace=True)
        self.df.to_csv(self.df_path)

        message = 'csv saved'
        self.csv_generated_message.setText(message)
        print(message)