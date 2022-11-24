import os
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
    def __init__(self, df, input_folder):
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
        self.counter = 0
        self.input_folder = input_folder
        self.video_name = os.path.split(input_folder)[1] + '.mkv'
        self.img_paths = read_data.get_img_paths(input_folder, self.df)
        self.img_root = os.path.split(self.img_paths[0])[0]
        self.num_images = len(self.img_paths)
        self.frame_to_jump = int(os.path.split(self.img_paths[0])[-1][:-4])
        self.assigned_labels = {}
        self.label_inputs = []
        self.label_headlines = []
        self.btn_overview = []
        self.start = False

        # Get path of the master csv
        self.df_path = os.path.join(input_folder, self.video_name[:-4] + '.csv')

        # initialize list to save all label buttons
        self.label_buttons = []

        # Initialize Labels
        self.img_name_label = QLabel(self)
        self.progress_bar = QLabel(self)
        self.curr_image_headline = QLabel('Current image', self)
        self.csv_generated_message = QLabel(self)
        self.jumpto = QLabel('Jump to frame: ', self)
        self.error_message = QLabel(self)
        self.speed = QLabel('Choose speed (in ms): ', self)
        self.showSpeed = QLabel(self)

        # Jump to QLineEdit
        self.jumpto_user = QLineEdit(self)

        #layouts
        self.formLayout =QFormLayout()

        #GroupBoxs
        self.groupBox = QGroupBox()

        #Scrolls for overview annotation
        self.scroll = QScrollArea(self)
        
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

        # progress bar (how many images have I labeled so far)
        self.progress_bar.setGeometry(20, 995, self.img_panel_width, 20)

        # jump to label
        self.jumpto.setGeometry(700, 940, self.img_panel_width, 20)
        self.jumpto.setObjectName('headline')

        # jump to editline user
        self.jumpto_user.setGeometry(700, 970, 105, 25)

        # Error message jump
        self.error_message.setGeometry(700, 1000, 500, 25)
        self.error_message.setStyleSheet('color: red; font-weight: bold')

        # Speed label
        self.speed.setGeometry(980, 940, 180, 20)
        self.speed.setObjectName('headline')

        # Show speed label
        self.showSpeed.setGeometry(980, 995, 200, 25)
        self.showSpeed.setText('Current spped: 500')

        # message that csv was generated
        self.csv_generated_message.setGeometry(self.img_panel_width + -800, 1000, 1200, 20)
        self.csv_generated_message.setStyleSheet('color: #43A047')

        # Set the first image and draw the coordinates if there are
        coordinates = self.read_box_coordinates(int(os.path.split(self.img_paths[0])[-1][:-4]), [])
        self.set_image(self.img_paths[0], coordinates, False)

        #initiate the ScrollArea
        self.scroll.setGeometry(1653, 310, 197, 618)
        
        # image name
        self.img_name_label.setText(self.img_paths[self.counter])

        # progress bar
        self.progress_bar.setText(f'image 1 of {self.num_images}')

        # draw line to for better UX
        ui_line = QLabel(self)
        ui_line.setGeometry(20, 930, 1012, 1)
        ui_line.setStyleSheet('background-color: black')

        #coordinates Box
        self.box_coordinates = []

        # Initiate pending annotations
        self.pending_annotations = {}
        for index, row in self.df.iterrows():          
            if type(row['Goldstandard coord']) == float:
                self.pending_annotations[row['frame']] = None

        # create buttons
        self.init_buttons()

        # Create the radio buttons
        self.init_radioButtons()

        # create a timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.show_next_image(self.start, False))
        self.timer.start(500)

        # Create a slider for the timer
        self.slider = QSlider(self)
        self.slider.setGeometry(980, 970, 240, 20)
        self.slider.setMinimum(100)
        self.slider.setMaximum(1000)
        self.slider.setTickInterval(100)
        self.slider.setFocusPolicy(Qt.StrongFocus)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.valueChanged.connect(self.changeSpeed)
        self.slider.setValue(500)

        # apply custom styles
        try:
            styles_path = "./styles.qss"
            with open(styles_path, "r") as fh:
                self.setStyleSheet(fh.read())
        except:
            print("Can't load custom stylesheet.")

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

        # Add "Where is the polyp?" button
        where_polyp = QtWidgets.QPushButton("Where is the polyp?", self)
        where_polyp.move(self.img_panel_width + 85, 60)
        where_polyp.clicked.connect(self.polyp_not_found)

        # Add "Start" button to start showing images
        start_btn = QtWidgets.QPushButton("Start", self)
        start_btn.move(self.img_panel_width - 325, 965)
        start_btn.clicked.connect(lambda: self.iterate_images(False))
        
        # Add "Stop" button to pause showing images
        stop_btn = QtWidgets.QPushButton("Stop", self)
        stop_btn.move(self.img_panel_width - 240, 965)
        stop_btn.clicked.connect(lambda: self.iterate_images(True))

        # Add "Open" button to load a new file
        open_file = QtWidgets.QPushButton("Open", self)
        open_file.move(self.img_panel_width + 100, 980)
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

        # Add "Start/Stop" shortcut
        start_kbs = QShortcut(QKeySequence(" "), self)
        start_kbs.activated.connect(lambda : self.iterate_images(self.start))

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

        # Add scroll tab
        self.annotation_overview(None, True)

    def init_radioButtons(self):

        self.activeRadioButtons = []


        self.radioButton1 = QRadioButton("GIGv1 (green)", self)
        self.radioButton1.move(self.img_panel_width + 60, 110)
        self.radioButton1.status = "GIGv1"
        
        self.radioButton2 = QRadioButton("GIGv3 (dark green)", self)
        self.radioButton2.move(self.img_panel_width + 60, 150)
        self.radioButton2.status = "GIGv3"
        
        self.radioButton3 = QRadioButton("EndoAID-A (blue)", self)
        self.radioButton3.move(self.img_panel_width + 60, 190)
        self.radioButton3.status = "EndoAID-A"
       
        
        self.radioButton4 = QRadioButton("EndoAID-B (dark blue)", self)
        self.radioButton4.move(self.img_panel_width + 60, 230)
        self.radioButton4.status = "EndoAID-B"
        
        self.radioButton5 = QRadioButton("EndoMind (magenta)", self)
        self.radioButton5.move(self.img_panel_width + 60, 270)
        self.radioButton5.status = "EndoMind"
        
        
        #Create a key group and add keys
        self.cs_group = QButtonGroup(self)
        self.cs_group.addButton(self.radioButton1, 1)
        self.cs_group.addButton(self.radioButton2, 2)
        self.cs_group.addButton(self.radioButton3, 3)
        self.cs_group.addButton(self.radioButton4, 4)
        self.cs_group.addButton(self.radioButton5, 5)

        # Connects the onclicked function and print the received paramenters
        self.cs_group.buttonClicked.connect(self.onClicked)

        # Set cs_group to not be mutually exclusive
        self.cs_group.setExclusive(False)



    def changeSpeed(self, value):
        self.showSpeed.setText('Current speed: {}'.format(value))
        self.timer.start(value)

    def onClicked(self, object):
        '''
        Controls which radio buttons for CADe systems are pressed.
        Reads csv CADe coordinates of the corresponding pressed radio buttons .
        Outputs the coordinates of each CADe system (if available).
        '''
        
        id_clicked = self.cs_group.id(object)
        
        if id_clicked in self.activeRadioButtons:
            self.activeRadioButtons.remove(id_clicked)
        else:
            self.activeRadioButtons.append(id_clicked)

        # Read box coordinates
        frame_number = int(os.path.split(self.img_paths[self.counter])[-1].split('.')[0])
        coordinates = self.read_box_coordinates(frame_number, self.activeRadioButtons)
        self.set_image(self.img_paths[self.counter], coordinates, False)
 
        
    def iterate_images(self, start):

        if start == True:
            self.start = False
        if start == False:
            self.start = True

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
                self.progress_bar.setText(f'image {self.counter + 1} of {self.num_images}')
                self.img_name_label.setText(path)
                
                message = 'Jump to {}'.format(frame_number)
                self.error_message.setText(message)
            else:
                message = 'Frame number {} does not exist'.format(frame_number)
                self.error_message.setText(message)
            
        except ValueError:
            message = 'Frame number must be an integer. Ex: 27134'
            self.error_message.setText(message)
    

    def show_next_image(self, with_box, from_button):
        """
        calls method to store coordinates drawn in pandas dataframe
        calls method to update the annotations overview (pending)
        loads and shows next image in dataset
        :param with_box: load next image with previous box coordinates
        """
        
        # only if it is start mode or comes from button
        if (self.start == True) or (from_button == True):
            # Frame number of the image to store
            frame_number = int(os.path.split(self.img_paths[self.counter])[-1].split('.')[0])
            
            if len(self.box_coordinates) != 0:
                self.df = self.store_coordinates(self.box_coordinates, frame_number)
                if frame_number in self.pending_annotations:
                    self.annotation_overview(frame_number, False)
                    

            # Load new image
            if self.counter < self.num_images - 1:
                self.counter += 1

                path = self.img_paths[self.counter]
                filename = os.path.split(path)[-1]
                frame_number = int(filename.split('.')[0])

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
                self.progress_bar.setText(f'image {self.counter + 1} of {self.num_images}')
                
    

    def show_prev_image(self):
        """
        calls method to store coordinates drawn
        loads and shows previous image in dataset
        """

        # Frame number of the image to store
        frame_number = int(os.path.split(self.img_paths[self.counter])[-1].split('.')[0])

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
                frame_number = int(filename.split('.')[0])              
                
                # Read if there are previous annotations in the new frame number
                coordinates = self.read_box_coordinates(frame_number, self.activeRadioButtons)
                self.set_image(path, coordinates, False)
                self.img_name_label.setText(path)
                self.progress_bar.setText(f'image {self.counter + 1} of {self.num_images}')

                self.csv_generated_message.setText('')

                # Update the coordinates
                self.box_coordinates = coordinates['Goldstandard coord']
                

    def store_coordinates(self, coordinates, image):
        '''
        :param coordinates: box coordinates drawn in the image
        :param image: frame number of the image where coordinates where drawn
        '''

        try:
            index = self.df.loc[self.df['frame'] == image].index[0]
            
            if coordinates == 'Polyp not identified':
                self.df.at[index, 'Goldstandard coord'] = 'Polyp not identified'
            else:
                # Rescale the coordinates from 1650,928 to 1920,1080     
                rescaled_coordinates = []
                factor = 1.1636
                
                for coordinate in coordinates:
                    x = int(round(coordinate[0]*factor))
                    y = int(round(coordinate[1]*factor))
                    width = int(round(coordinate[2]*factor))
                    height = int(round(coordinate[3]*factor))

                    rescaled_coordinates.append((x,y,width, height))

                self.df.at[index, 'Goldstandard coord'] = str(rescaled_coordinates)
            
        except:
            raise ValueError('Coordinates could not be saved on dataframe')

        return self.df


    def read_box_coordinates(self, image, systems):
        '''
        :param image: image frame number
        :param systems: list of systems to which we want to obtain the coordinates
            if 1 in systems --> obtains coordinates of GIGv1
            if 2 in systems --> obtains coordinates of GIGv3
            if 3 in systems --> obtains coordinates of Oly A
            if 4 in systems --> obtains coordinates of Oly B
            if 5 in systems --> obtains coordinates of EM
            in all the cases, obtain always the coordinates of Goldstandard coordinates
        returns previous annotated coordinates, if available, RESCALING THEM!!!
        '''

        coordinates_systems = {}

        correlation = {1:'GIG coord',
                       2:'GIGv3 coord',
                       3:'Oly_A coord',
                       4:'Oly_B coord',
                       5:'EM coord'
                       }

        # Show always Goldstandard coordinates 
        coordinates_goldstandard = self.df.loc[self.df['frame'] == image]['Goldstandard coord'].values[0]
        # print('Beginning read_box_coordinates', coordinates_goldstandard, type(coordinates_goldstandard))
        # For already saved annotations, we need to convert str to list
        if type(coordinates_goldstandard) == str:
            if coordinates_goldstandard == "Polyp not identified": # In case user did not identify a polyp
                coordinates_goldstandard = "Polyp not identified"
            else:
                coordinates_goldstandard = ast.literal_eval(coordinates_goldstandard)

                # Rescale the coordinates from 1920,1080 to 1650,928
                rescaled_coordinates = []
                factor = 1.1636
                for coordinate in coordinates_goldstandard:
                    x = int(round(coordinate[0]/factor))
                    y = int(round(coordinate[1]/factor))
                    width = int(round(coordinate[2]/factor))
                    height = int(round(coordinate[3]/factor))

                    rescaled_coordinates.append((x,y,width, height))
                
                coordinates_goldstandard=rescaled_coordinates
            
        # If there are no previous annotations, return an empty list.
        try:
            if math.isnan(coordinates_goldstandard):
                coordinates_goldstandard = []
        except TypeError:
            coordinates_goldstandard = coordinates_goldstandard

        coordinates_systems['Goldstandard coord'] = coordinates_goldstandard

        # Show coordinates of the other systems if user has checked the boxes
        if len(systems) != 0:
            for system in systems: 
                coordinates = self.df.loc[self.df['frame'] == image][correlation[system]].values[0]
                
                # If there are annotations, then they are strings, if there are no annotations, then they are float
                if type(coordinates) == str:
                    coordinates = ast.literal_eval(coordinates)

                    rescaled_coordinates = []
                    factor = 1.1636

                    # Rescale the coordinates from 1920,1080 to 1650,928
                    for coordinate in coordinates:
                        x = int(round(coordinate[0]/factor))
                        y = int(round(coordinate[1]/factor))
                        width = int(round(coordinate[2]/factor))
                        height = int(round(coordinate[3]/factor))

                        rescaled_coordinates.append((x,y,width, height))

                    coordinates=rescaled_coordinates
                    
                # If there are no previous annotations, return an empty list.
                try:
                    if math.isnan(coordinates):
                        coordinates = []
                except TypeError:
                    coordinates = coordinates

                coordinates_systems[system] = coordinates

        # print('Final coordinates:\n{}'.format(coordinates_systems))
        
        return coordinates_systems

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


    def set_image(self, path, coordinates, from_scroll):
        """
        displays the image in GUI
        :param path: path to the image that should be show
        :param coordinates: contains the coordinates of the different boxes that need to be drawn.
        :param from_scrool: True if the image has been set by clicking the annotations_pending scroll tab
        """
      
        self.pixmap = QPixmap(path)
        img_width = self.pixmap.width()
        img_height = self.pixmap.height()
        self.pixmap = self.pixmap.scaledToWidth(1650)
        self.box_coordinates = []

        # In case the method is called from annotation_overview(), we need to update the other fields
        # and read from the dataframe if we have to draw coordinates
        if from_scroll:

            # If coordinates drawn we have to store them because the method next_image or previous_image is not called:
            if len(self.box_coordinates) != 0:
                # Frame number of the image to store before updating self.counter
                frame_number = int(os.path.split(self.img_paths[self.counter])[-1].split('.')[0])
                self.df = self.store_coordinates(self.box_coordinates, frame_number)

                # Update annotations_pending
                if frame_number in self.pending_annotations:
                    self.annotation_overview(frame_number, False)


        # Draw the coordinates of all the systems that want to be drawn
        colors_systems = {'Goldstandard coord':Qt.red, 1:Qt.green, 2:Qt.darkGreen, 3:Qt.blue, 4:Qt.darkBlue, 5:Qt.magenta}
        # create painter instance with pixmap
        painterInstance = QPainter(self.pixmap)
        
        for system in coordinates:

            # Draw red frame rectangle if polyp not identified
            if coordinates[system] == 'Polyp not identified':
                # set rectangle color and thickness
                penRectangle = QPen(Qt.red, 10, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

                # draw rectangle on painter
                painterInstance.setPen(penRectangle)

                rect = QRect(QPoint(5, 5), QPoint(1645, 922))
                painterInstance.drawRect(rect.normalized())
                
            else:
                # set rectangle color and thickness
                penRectangle = QPen(colors_systems[system], 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

                # draw rectangle on painter
                painterInstance.setPen(penRectangle)
                
                
                for box in coordinates[system]:
                    # print('Painting {} for {}'.format(box, system))
                    rect = QRect(box[0], box[1], box[2], box[3])
                    painterInstance.drawRect(rect) # The coordinates are already normalized


        self.img_name_label.setText(path)
        # we need to find the value of self.counter for the image
        self.counter = self.img_paths.index(path)
        self.progress_bar.setText(f'image {self.counter + 1} of {self.num_images}')
        self.update()



    def annotation_overview(self, frame_number_to_remove, init):
        '''
        Creates a scroll tab overview with pending annotations
        :param frame_number_to_remove: self explanatory
        :param init: the first time needs to be different
        '''

        if init == True:
            self.groupBox.setTitle('Annotations pending:')
            self.groupBox.setStyleSheet('font-weight: bold')

            # display input fields
            for value in self.pending_annotations:
                # append widgets to lists
                self.btn = QtWidgets.QPushButton('Frame {}'.format(value), self)
                self.pending_annotations[value] = self.btn
                self.btn.clicked.connect(lambda state, im_path=os.path.join(self.img_root, str(value)) + '.jpg', coord = []: self.set_image(im_path, coord, True))
                self.formLayout.addRow(self.btn)

            self.groupBox.setLayout(self.formLayout)
            self.scroll.setWidget(self.groupBox)
            self.scroll.setWidgetResizable(True)
            
        else:
            self.formLayout.removeWidget(self.pending_annotations[frame_number_to_remove])
            self.pending_annotations[frame_number_to_remove].deleteLater()
            self.pending_annotations[frame_number_to_remove] = None
           
            if frame_number_to_remove is not None:
                del self.pending_annotations[frame_number_to_remove]


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
        frame_number = int(os.path.split(current_image_path)[-1].split('.')[0])
        
        try:
            index = self.df.loc[self.df['frame'] == frame_number].index[0]
            self.df.at[index, 'Goldstandard coord'] = float("nan")
        except:
            raise ValueError('Coordinates could not be eliminated on dataframe')

        # We need to add the frame to the pending annotation
        if frame_number not in self.pending_annotations: #Then it means we have to create the button again
            self.btn = QtWidgets.QPushButton('Frame {}'.format(frame_number), self)
            self.pending_annotations[frame_number] = self.btn
            self.btn.clicked.connect(lambda state, im_path=os.path.join(self.img_root, str(frame_number)) + '.jpg', coord = {'Goldstandard coord':[]}: self.set_image(im_path, coord, False))
            self.formLayout.addRow(self.btn)

         

    def polyp_not_found(self):
        '''
        Modify the database
        '''

        current_image_path = self.img_paths[self.counter]

        # remove the coordinates from database
        frame_number = int(os.path.split(current_image_path)[-1].split('.')[0])
        
        try:
            index = self.df.loc[self.df['frame'] == frame_number].index[0]
            self.df.at[index, 'Goldstandard coord'] = "Polyp not identified"
        except:
            raise ValueError('Dataframe could not be updated')

        # Set the image with a red square
        self.set_image(current_image_path, {"Goldstandard coord":"Polyp not identified"}, False)

        # Update the scroll tab with images pending of annotation
        self.annotation_overview(frame_number, False)
         


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