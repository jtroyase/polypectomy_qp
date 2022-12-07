import os
import pandas as pd

import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer
from PyQt5.QtGui import QPixmap, QIntValidator, QKeySequence, QPainter, QPen, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QCheckBox, QFileDialog, QDesktopWidget, QLineEdit, \
     QRadioButton, QShortcut, QScrollArea, QVBoxLayout, QGroupBox, QFormLayout, QSlider, QButtonGroup, QTableWidget, QTableWidgetItem

import read_data
import user_widgets


def make_folder(directory):
    """
    :param directory: The folder destination path
    :return: 
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


class LabelerWindow(QWidget):
    def __init__(self, df, input_folder, labels):
        super().__init__()

        # init UI state
        self.title = 'PyQt5 - Box annotation tool'
        self.left = 200
        self.top = 100
        self.width = 1100
        self.height = 770
        # img panel size should be square-like to prevent some problems with different aspect ratios
        self.img_panel_width = 1600
        self.img_panel_height = 900

        # state variables
        self.df = df
        self.labels = labels
        self.counter = 0
        self.input_folder = input_folder
        self.video_name = os.path.split(input_folder)[1] + '.mkv'
        self.img_paths = read_data.get_img_paths(input_folder, self.df)
        self.img_root = os.path.split(self.img_paths[0])[0]
        self.num_images = len(self.img_paths)
        self.frame_to_jump = int(os.path.split(self.img_paths[0])[-1][:-4])

        # labels to identify different polyps
        self.paint_activation = 0
        self.polyp_id = 0
        
        # initialize list to save all label buttons
        self.label_buttons = []

        # Get path of the master csv
        self.df_path = os.path.join(input_folder, self.video_name[:-4] + '.csv')

        # Initialize Labels
        self.video_name_headline = QLabel('Video: ', self)
        self.video_name_label = QLabel(self.video_name.split('coloscopie_')[-1], self)
        self.video_name_label.setFont(QFont('Arial', 9))
        self.frame_number_headline = QLabel('Frame: ', self)
        self.frame_number_label = QLabel(self)
        self.csv_generated_message = QLabel(self)
        self.draw_polyp_message = QLabel(self)
        self.jumpto = QLabel('Jump to: ', self)
        self.error_message = QLabel(self)

        # Jump to QLineEdit
        self.jumpto_user = QLineEdit(self)

        ##### SCROLL TO VISUALIZE ANNOTATIONS/PREDICTIONS
        # layouts
        self.formLayout_gs =QFormLayout()
        self.formLayout_ai =QFormLayout()

        # scroll areas
        self.scroll_gs = QScrollArea(self)
        self.scroll_ai = QScrollArea(self)
        
        # GroupBoxs
        self.groupBox_gs = QGroupBox()
        self.groupBox_ai = QGroupBox()
        self.groupBox_gs.setTitle('Annotations:')
        self.groupBox_gs.setStyleSheet('font-weight: bold')
        self.groupBox_ai.setTitle('AI predictions:')
        self.groupBox_ai.setStyleSheet('font-weight: bold')

        self.groupBox_gs.setLayout(self.formLayout_gs)
        self.scroll_gs.setWidget(self.groupBox_gs)
        self.scroll_gs.setWidgetResizable(True)

        self.groupBox_ai.setLayout(self.formLayout_ai)
        self.scroll_ai.setWidget(self.groupBox_ai)
        self.scroll_ai.setWidgetResizable(True)

        # Create two point instances
        self.begin, self.destination = QPoint(), QPoint()

        # init UI
        self.init_ui()


    def init_ui(self):

        self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top, self.width, self.height) # initial dimension of the window
        self.setMinimumSize(self.width, self.height)  # minimum size of the window

        # video name headline
        self.video_name_headline.setGeometry(1655, 5, 45, 20)
        self.video_name_headline.setObjectName('headline')

        # video name label
        self.video_name_label.setGeometry(1655, 23, 220, 20)

        # frame number headline
        self.frame_number_headline.setGeometry(1655, 50, 50, 20)
        self.frame_number_headline.setObjectName('headline')

        # frame number label
        self.frame_number_label.setGeometry(1705, 50, 45, 20)
        
        # Draw polyp message
        self.draw_polyp_message.setGeometry(1700, 130, 150, 20)
        self.draw_polyp_message.setObjectName('headline')

        # jump to label
        self.jumpto.setGeometry(1, 80, 60, 20)
        self.jumpto.setObjectName('headline')

        # jump to editline user
        self.jumpto_user.setGeometry(1720, 80, 120, 25)

        # Error message jump
        self.error_message.setGeometry(700, 1000, 500, 25)
        self.error_message.setStyleSheet('color: red; font-weight: bold')

        # message that csv was generated
        self.csv_generated_message.setGeometry(self.img_panel_width + -800, 1000, 1200, 20)
        self.csv_generated_message.setStyleSheet('color: #43A047')

        # Initiate the ScrollAreas AI and position them
        self.scroll_gs.setGeometry(1653, 280, 197, 380)
        self.scroll_ai.setGeometry(1653, 670, 197, 260)

        # frame_number set text
        frame_number = os.path.split(self.img_paths[self.counter])[-1][:-4]
        if frame_number=='0000000':
            frame_number = '0'
        else:
            frame_number = frame_number.lstrip('0')
        self.frame_number_label.setText(frame_number)

        # draw line to for better UX
        ui_line = QLabel(self)
        ui_line.setGeometry(20, 930, 1012, 1)
        ui_line.setStyleSheet('background-color: black')

        #coordinates Box
        self.box_coordinates = []

        # create buttons
        self.label_buttons = user_widgets.init_buttons(self, self.img_panel_width, self.df_path, self.labels)

        # apply custom styles
        try:
            styles_path = "./styles.qss"
            with open(styles_path, "r") as fh:
                self.setStyleSheet(fh.read())
        except:
            print("Can't load custom stylesheet.")

        # Set the first image with GS and AI annotations if there are:
        self.annotations = read_data.read_annotations(int(os.path.split(self.img_paths[0])[-1][:-4]), self.labels, self.df)
        self.set_image(self.img_paths[0], self.annotations)


    def draw_polyp(self):
        '''
        When a kbs is pressed, allows the user to draw the polyp
        '''
        # Activate the event function to draw
        self.paint_activation = 1

        # Show a label
        self.draw_polyp_message.setText('Select polyp ID')


    def toJump(self):

        # Retrieve value from QLineEdit
        frame_number = self.jumpto_user.text()
        try:
            frame_number = int(frame_number)
            path = os.path.join(self.img_root, str(frame_number) + '.jpg')

            # Check if the path exists:
            if path in self.img_paths:
                
                # Obtain the coordinates drawn in that image
                coordinates = self.read_box_coordinates(frame_number, self.activeRadioButtons)
                self.set_image(path, coordinates, True) # True es perque guardi les coordenades anteriors
                self.counter = self.img_paths.index(path)
                self.frame_number_label.setText(str(frame_number))
                
                message = 'Jump to {}'.format(frame_number)
                self.error_message.setText(message)
            else:
                message = 'Frame number {} does not exist'.format(frame_number)
                self.error_message.setText(message)
            
        except ValueError:
            message = 'Frame number must be an integer. Ex: 27134'
            self.error_message.setText(message)
    

    def show_next_image(self):
        """
        calls method to store coordinates drawn in pandas dataframe
        calls method to update the annotations overview (pending)
        loads and shows next image in dataset
        """
        
        ##### REINITIALIZE TEXTS AND VARIABLES
        self.draw_polyp_message.setText('')
        self.paint_activation = 1
        
        ##### STORE THE ANNOTATIONS / COORDINATES ON THE IMAGE
        print(self.annotations)
        self.store_annotations()

        ##### LOAD THE NEW IMAGE WITH THE PREVIOUS ANNOTATIONS
        if self.counter < self.num_images -1:
            self.counter += 1

            path = self.img_paths[self.counter]
            filename = os.path.split(path)[-1]
            frame_number = filename.split('.')[0].lstrip('0')

            # Read the AI predictions and if there are previous annotated GS labels
            self.annotations = read_data.read_annotations(frame_number, self.labels, self.df)
            # Set the image
            self.set_image(path, self.annotations) 
    

    def show_prev_image(self):
        """
        calls method to store coordinates drawn
        loads and shows previous image in dataset
        """

        ##### REINITIALIZE TEXTS AND VARIABLES
        self.draw_polyp_message.setText('')
        self.paint_activation = 1
        
        ##### STORE THE ANNOTATIONS / COORDINATES ON THE IMAGE
        print(self.annotations)
        self.store_annotations()

        ##### LOAD THE NEW IMAGE WITH THE PREVIOUS ANNOTATIONS
        if self.counter > 0:
            self.counter -= 1

            if self.counter < self.num_images:
                path = self.img_paths[self.counter]
                filename = os.path.split(path)[-1]
                frame_number = filename.split('.')[0].lstrip('0')

                # Read the AI predictions and if there are previous annotated GS labels
                self.annotations = read_data.read_annotations(frame_number, self.labels, self.df)
                # Set the image
                self.set_image(path, self.annotations)                 

    def store_annotations(self):
        '''
        stores the current annotations to the database
        stores the current coordinates of each polyp
        '''
        ##### ANNOTATIONS
        # We obtain the frame number as a string because dtype in df of "frame" is object
        frame_number_base7 = os.path.split(self.img_paths[self.counter])[-1].split('.')[0]
        if frame_number_base7=='0000000':
            frame_number = '0'
        else:
            frame_number = frame_number_base7.lstrip('0')
        
        # index of the frame number of the database
        df_index = self.df[self.df['frame'] == frame_number].index[0]
        
        for key, value in self.annotations['gs_annotations'].items():
            #print('Written {} in {}_gs'.format(int(value), key))
            if key != 'polyp':
                self.df.at[df_index, '{}_gs'.format(key)] = int(value)

        ##### COORDINATES
        # If there is any annotation
        if 'polyp' in self.annotations['gs_annotations']:
            # rescale the coordinates from 1650,928 to 1920,1080
            rescaled_coordinates = []
            factor = 1.16363
            
            for polyp_id, coordinate in self.annotations['gs_annotations']['polyp']:
                x = int(round(coordinate[0]*factor))
                y = int(round(coordinate[1]*factor))
                width = int(round(coordinate[2]*factor))
                height = int(round(coordinate[3]*factor))

                rescaled_coordinates.append((polyp_id, (x,y,width, height)))

            self.df.at[df_index, 'polyp_gs'] = rescaled_coordinates


    def set_image(self, path, annotations):
        """
        displays the image in GUI
        :param path: path to the image that should be show
        :param annotations: contains the annotations and predictions that need to be drawn or shown.
        :param from_scroll: True if the image has been set by clicking the annotations_pending scroll tab
        """
      
        ##### UPDATE IMAGE      
        self.pixmap = QPixmap(path)
        img_width = self.pixmap.width()
        img_height = self.pixmap.height()
        self.pixmap = self.pixmap.scaledToWidth(1650)

        ##### UPDATE COORDINATE ANNOTATIONS
        # Coordinates need to be drawn in case of polyp annotations
        # The bounding boxes will be drawn with different pen colors depending on the id of the polyp
        if 'polyp' in annotations['gs_annotations']:
            painterInstance = QPainter(self.pixmap)
            # '[(1, (x,y,width,height)), (2, (x,y,width,height))]'
            for polyp in annotations['gs_annotations']['polyp']:
                polyp_id = polyp[0]
                coordinates = polyp[1]
                penRectangle = QPen(user_widgets.colors_polyp(polyp[0]), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painterInstance.setPen(penRectangle)
                print('Painting coordinates: {}'.format(coordinates))
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

            
    def set_label(self, label):
        """
        Sets the label for just loaded image
        :param label: selected label
        """

        # Has the image the label?
        if label in self.annotations['gs_annotations'].keys():
            # Then it can be two things, green to red or red to none
            if self.annotations['gs_annotations'][label] == 1:
                self.annotations['gs_annotations'][label] = 2
            else:
                del self.annotations['gs_annotations'][label]
        else:
            # Add the label
            self.annotations['gs_annotations'][label] = 1
        
        self.set_button_color()



    def set_button_color(self):
        """
        Changes the color of the button which corresponds to selected label
        """

        for button in self.label_buttons:
            if button.text() in self.annotations['gs_annotations'].keys():
                if self.annotations['gs_annotations'][button.text()] == 1:
                    button.setStyleSheet('border: 3px solid #43A047; background-color: #4CAF50; color: white')
                else:
                    button.setStyleSheet('border: 3px solid #FF0000; background-color: #FF0000; color: white')
            else:
                button.setStyleSheet('background-color: None')


    def reset_box(self):
        '''
        Present the current image without boxes
        Remove the coordinate boxes from the master database
        '''

        current_image_path = self.img_paths[self.counter]
        self.box_coordinates = []        
        
        # set the image without boxes
        self.set_image(current_image_path, {'Goldstandard coord':[]}, False)

        # remove the coordinaates from database
        frame_number = int(os.path.split(current_image_path)[-1].split('.'))
        
        try:
            index = self.df.loc[self.df['frame'] == frame_number].index
            self.df.at[index, 'Goldstandard coord'] = float("nan")
        except:
            raise ValueError('Coordinates could not be eliminated on dataframe')

        # We need to add the frame to the pending annotation
        if frame_number not in self.pending_annotations: #Then it means we have to create the button again
            self.btn = QtWidgets.QPushButton('Frame {}'.format(frame_number), self)
            self.pending_annotations[frame_number] = self.btn
            self.btn.clicked.connect(lambda state, im_path=os.path.join(self.img_root, str(frame_number)) + '.jpg', coord = {'Goldstandard coord':[]}: self.set_image(im_path, coord, False))
            self.formLayout.addRow(self.btn)


    def paintEvent(self, event):
        painter = QPainter(self)       
        painter.drawPixmap(QPoint(), self.pixmap)

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
                    rect = QRect(self.begin, self.destination)
                    painter = QPainter(self.pixmap)
                    
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
        self.m = SetupWindow()
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

        # Transfer the annotated data to the master dataframe
        for index, row in self.df.iterrows():
            self.df_MASTER.at[index, 'Goldstandard coord'] = row['Goldstandard coord']

        self.df_MASTER.to_csv(csv_file_path)

        # Rewrite the master csv
        self.df_MASTER.to_csv(self.df_path)

        message = f'csv saved to: {csv_file_path}'
        self.csv_generated_message.setText(message)
        print(message)