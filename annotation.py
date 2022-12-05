import os
import pandas as pd

import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer
from PyQt5.QtGui import QPixmap, QIntValidator, QKeySequence, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QCheckBox, QFileDialog, QDesktopWidget, QLineEdit, \
     QRadioButton, QShortcut, QScrollArea, QVBoxLayout, QGroupBox, QFormLayout, QSlider, QButtonGroup

import read_data


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
        self.start = False

        # initialize list to save all label buttons
        self.label_buttons = []

        # Get path of the master csv
        self.df_path = os.path.join(input_folder, self.video_name[:-4] + '.csv')

        # Initialize Labels
        self.img_name_label = QLabel(self)
        self.curr_image_headline = QLabel('Current image', self)
        self.csv_generated_message = QLabel(self)
        self.jumpto = QLabel('Jump to frame: ', self)
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

        # image headline
        self.curr_image_headline.setGeometry(20, 940, 300, 20)
        self.curr_image_headline.setObjectName('headline')

        # image name label
        self.img_name_label.setGeometry(20, 970, self.img_panel_width, 20)

        # jump to label
        self.jumpto.setGeometry(700, 940, self.img_panel_width, 20)
        self.jumpto.setObjectName('headline')

        # jump to editline user
        self.jumpto_user.setGeometry(700, 970, 105, 25)

        # Error message jump
        self.error_message.setGeometry(700, 1000, 500, 25)
        self.error_message.setStyleSheet('color: red; font-weight: bold')

        # message that csv was generated
        self.csv_generated_message.setGeometry(self.img_panel_width + -800, 1000, 1200, 20)
        self.csv_generated_message.setStyleSheet('color: #43A047')

        # Initiate the ScrollAreas AI and position them
        self.scroll_gs.setGeometry(1653, 280, 197, 380)
        self.scroll_ai.setGeometry(1653, 670, 197, 260)

        # image name
        self.img_name_label.setText(os.path.split(self.img_paths[self.counter])[1])

        # draw line to for better UX
        ui_line = QLabel(self)
        ui_line.setGeometry(20, 930, 1012, 1)
        ui_line.setStyleSheet('background-color: black')

        #coordinates Box
        self.box_coordinates = []

        # create buttons
        self.init_buttons()

        # apply custom styles
        try:
            styles_path = "./styles.qss"
            with open(styles_path, "r") as fh:
                self.setStyleSheet(fh.read())
        except:
            print("Can't load custom stylesheet.")

        # Set the first image with GS and AI annotations if there are:
        self.annotations = read_data.read_annotations(int(os.path.split(self.img_paths[0])[-1][:-4]), self.labels, self.df)
        self.set_image(self.img_paths[0], self.annotations, False)



    def init_buttons(self):

        # Add "Prev Image" and "Next Image" buttons    
        prev_im_btn = QtWidgets.QPushButton("Prev", self)
        prev_im_btn.move(self.img_panel_width - 115, 965)
        prev_im_btn.clicked.connect(self.show_prev_image)

        next_im_btn = QtWidgets.QPushButton("Next", self)
        next_im_btn.move(self.img_panel_width-30, 965)
        next_im_btn.clicked.connect(lambda: self.show_next_image(False, True))

        # Add "Reset boxes" button
        reset_btn = QtWidgets.QPushButton("Reset boxes", self)
        reset_btn.move(self.img_panel_width + 110, 20)
        reset_btn.clicked.connect(self.reset_box)

        # Add "Open" button to load a new file
        open_file = QtWidgets.QPushButton("Open", self)
        open_file.move(self.img_panel_width + 95, 980)
        open_file.clicked.connect(self.openFile)
        open_file.setObjectName("blueButton")

        # Add "Prev Image" and "Next Image" keyboard shortcuts
        prev_im_kbs = QShortcut(QKeySequence("p"), self)
        prev_im_kbs.activated.connect(self.show_prev_image)

        next_im_kbs = QShortcut(QKeySequence("n"), self)
        next_im_kbs.activated.connect(lambda : self.show_next_image(False, True))

        # Add "Next Image" with same box keyboard shortcut
        next_im_box_kbs = QShortcut(QKeySequence("m"), self)
        next_im_box_kbs.activated.connect(lambda : self.show_next_image(True, True))

        # Add "Reset box" shortcut
        reset_kbs = QShortcut(QKeySequence("r"), self)
        reset_kbs.activated.connect(self.reset_box)

        # Add "generate csv file" button
        next_im_btn = QtWidgets.QPushButton("Generate csv", self)
        next_im_btn.move(self.img_panel_width + 95, 940)
        next_im_btn.clicked.connect(lambda state, filename=self.df_path: self.generate_csv(filename))
        next_im_btn.setObjectName("blueButton")

        # Add "Jump" button
        jump_btn = QtWidgets.QPushButton("Jump", self)
        jump_btn.move(self.img_panel_width - 780, 970)
        jump_btn.clicked.connect(self.toJump)

        # create button for each label
        for i, label in enumerate(self.labels):
            self.label_buttons.append(QtWidgets.QPushButton(label, self))
            button = self.label_buttons[i]
            button.clicked.connect(lambda state, x=label: self.set_label(x))
            self.formLayout_gs.addRow(button)


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
                self.img_name_label.setText(path)
                
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
        
        # store the annotations on the image
        

        # load the new image with the previous annotations
            # Frame number of the image to store
            frame_number = int(os.path.split(self.img_paths[self.counter])[-1].split('.'))
            
            if len(self.box_coordinates) != 0:
                self.df = self.store_coordinates(self.box_coordinates, frame_number)
                if frame_number in self.pending_annotations:
                    self.annotation_overview(frame_number, False)
                    

            # Load new image
            if self.counter < self.num_images - 1:
                self.counter += 1

                path = self.img_paths[self.counter]
                filename = os.path.split(path)[-1]
                frame_number = int(filename.split('.'))

                # Read if there are previous annotations
                coordinates = self.read_box_coordinates(frame_number, self.activeRadioButtons)
                         
                if with_box == True:
                    if len(coordinates) == 0: # If there are no previous boxes in dataframe, load the image with the previous coordinates
                        self.set_image(path, self.box_coordinates, False) 
                    else:
                        self.set_image(path, coordinates, False) # Then load the image with the boxes stored in the dataframe
                        self.box_coordinates = coordinates['Goldstandard coord']
                else:
                    self.set_image(path, coordinates, False) # Load the images with the boxes stored in the dataframe if any
                    self.box_coordinates = coordinates['Goldstandard coord']

                self.img_name_label.setText(path)
                
    

    def show_prev_image(self):
        """
        calls method to store coordinates drawn
        loads and shows previous image in dataset
        """

        # Frame number of the image to store
        frame_number = int(os.path.split(self.img_paths[self.counter])[-1].split('.'))

        if len(self.box_coordinates) != 0:
            self.df = self.store_coordinates(self.box_coordinates, frame_number)
            if frame_number in self.pending_annotations:
                self.annotation_overview(frame_number, False)

        # Load new image
        if self.counter > 0:
            self.counter -= 1

            if self.counter < self.num_images:
                path = self.img_paths[self.counter]
                filename = os.path.split(path)[-1]
                frame_number = int(filename.split('.'))              
                
                # Read if there are previous annotations in the new frame number
                coordinates = self.read_box_coordinates(frame_number, self.activeRadioButtons)
                self.set_image(path, coordinates, False)
                self.img_name_label.setText(path)

                self.csv_generated_message.setText('')

                # Update the coordinates
                self.box_coordinates = coordinates['Goldstandard coord']
                

    def store_coordinates(self, coordinates, image):
        '''
        :param coordinates: box coordinates drawn in the image
        :param image: frame number of the image where coordinates where drawn
        '''

        try:
            index = self.df.loc[self.df['frame'] == image].index
            
            if coordinates == 'Polyp not identified':
                self.df.at[index, 'Goldstandard coord'] = 'Polyp not identified'
            else:
                # Rescale the coordinates from 1650,928 to 1920,1080     
                rescaled_coordinates = []
                factor = 1.1636
                
                for coordinate in coordinates:
                    x = int(round(coordinate*factor))
                    y = int(round(coordinate[1]*factor))
                    width = int(round(coordinate[2]*factor))
                    height = int(round(coordinate[3]*factor))

                    rescaled_coordinates.append((x,y,width, height))

                self.df.at[index, 'Goldstandard coord'] = str(rescaled_coordinates)
            
        except:
            raise ValueError('Coordinates could not be saved on dataframe')

        return self.df


    def set_image(self, path, annotations, from_scroll):
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

        ##### UPDATE ANNOTATIONS
        # Coordinates need to be drawn in case of polyp annotations
        # The bounding boxes will be drawn with different pen colors depending on the id of the polyp
        colors_polyp = {1:Qt.red, 2:Qt.green, 3:Qt.blue, 4:Qt.yellow, 5:Qt.cyan, 6:Qt.magenta, 7:Qt.gray, 8:Qt.black}
        painterInstance = QPainter(self.pixmap)

        if 'polyp' in annotations['gs_annotations']:
            '[(1, (x,y,width,height)), (2, (x,y,width,height))]'
            for polyp in annotations['gs_annotations']['polyp']:

                penRectangle = QPen(colors_polyp[polyp], 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painterInstance.setPen(penRectangle)

                # The coordinates need to be normalized from 1920x1080 to 1650
                for box in polyp[1]:
                    x = box*0.8594
                    y = box[1]*0.8594
                    width = box[2]*0.8594
                    height = box[3]*0.8594
                    
                    rect = QRect(x, y, width, height)
                    painterInstance.drawRect(rect)

        ##### CALL FOR UPDATE PREDICTIONS
        self.predictions_overview(self.annotations)

        ##### OTHER INFO
        # Set the name of the image displayed
        self.img_name_label.setText(path)
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

        #if not self.begin.isNull() and not self.destination.isNull():
        if ((abs(self.begin.x() - self.destination.x()) > 10) and (abs(self.begin.x() - self.destination.x()) > 10)):
            pen = QPen(Qt.green, 3, Qt.DashDotLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            rect = QRect(self.begin, self.destination)
            painter.drawRect(rect.normalized())


    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.begin = event.pos()
            self.destination = self.begin
            self.update()
        
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.destination = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() & Qt.LeftButton:
            # Print the rectangle only in case is bigger than a threshold:
            if ((abs(self.begin.x() - self.destination.x()) > 10) and (abs(self.begin.x() - self.destination.x()) > 10)):
                rect = QRect(self.begin, self.destination)
                painter = QPainter(self.pixmap)
                pen = QPen(Qt.green, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(pen)
                painter.drawRect(rect.normalized())
                self.box_coordinates.append([rect.normalized().x(), rect.normalized().y(), rect.normalized().width(), rect.normalized().height()])
                self.begin, self.destination = QPoint(), QPoint()
                self.update()

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