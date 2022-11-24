from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer
from PyQt5.QtGui import QPixmap, QIntValidator, QKeySequence, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QCheckBox, QFileDialog, QDesktopWidget, QLineEdit, \
     QRadioButton, QShortcut, QScrollArea, QVBoxLayout, QGroupBox, QFormLayout, QSlider, QButtonGroup

from read_data import get_database
from annotation import LabelerWindow
import user_widgets

class SetupWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Window variables
        self.width = 800
        self.height = 400

        # State variables
        self.selected_folder = ''
        self.selected_labels = ''
        self.num_labels = 0
        self.label_inputs = []
        self.label_headlines = []
        self.mode = 'csv'  # default option

        # Labels
        self.headline_folder = QLabel('1. Select the video to annotate', self)
        self.headline_num_labels = QLabel('2. Specify labels to annotate', self)

        self.selected_folder_label = QLabel(self)
        self.error_message = QLabel(self)

        # Buttons
        self.browse_button = QtWidgets.QPushButton("Browse", self)
        self.next_button = QtWidgets.QPushButton("Next", self)

        # Init
        self.init_ui()

    def init_ui(self):
        # self.selectFolderDialog = QFileDialog.getExistingDirectory(self, 'Select directory')
        self.setWindowTitle('PyQt5 - Annotation tool - Parameters setup')
        self.setGeometry(0, 0, self.width, self.height)
        self.centerOnScreen()

        self.headline_folder.setGeometry(60, 30, 500, 20)
        self.headline_folder.setObjectName("headline")

        self.selected_folder_label.setGeometry(60, 60, 550, 26)
        self.selected_folder_label.setObjectName("selectedFolderLabel")

        self.browse_button.setGeometry(611, 59, 80, 28)
        self.browse_button.clicked.connect(self.pick_new)

        # Select labels headline
        self.headline_num_labels.move(60, 130)
        self.headline_num_labels.setObjectName("headline")

        # Select labels radio buttons
        self.activeRadioButtons = []
        self.l_r_button = user_widgets.init_label_rbuttons(self)
        self.l_r_button.buttonClicked.connect(self.onClicked)

        # Set cs_group to not be mutually exclusive
        self.l_r_button.setExclusive(False)

        # Next Button
        self.next_button.move(330, 320)
        self.next_button.clicked.connect(self.continue_app)
        self.next_button.setObjectName("blueButton")

        # Error message
        self.error_message.setGeometry(0, 320, self.width - 20, 20)
        self.error_message.setAlignment(Qt.AlignCenter)
        self.error_message.setStyleSheet('color: red; font-weight: bold')


        # apply custom styles
        try:
            styles_path = "./styles.qss"
            with open(styles_path, "r") as fh:
                self.setStyleSheet(fh.read())
        except:
            print("Can't load custom stylesheet.")


    def pick_new(self):
        """
        shows a dialog to choose folder with images to label
        """
        dialog = QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "Select Folder", "/media/inexen/CADe_comparison_review/PolypectomyQualityPredictor/")

        self.selected_folder_label.setText(folder_path)
        self.selected_folder = folder_path

            
    def centerOnScreen(self):
        """
        Centers the window on the screen.
        """
        resolution = QDesktopWidget().screenGeometry()
        self.move(int((resolution.width() / 2) - (self.width / 2)),
                  int((resolution.height() / 2) - (self.height / 2)) - 40)


    def onClicked(self, object):
        '''
        Controls which radio buttons for CADe systems are pressed.
        Reads csv CADe coordinates of the corresponding pressed radio buttons .
        Outputs the coordinates of each CADe system (if available).
        '''
        
        id_clicked = self.l_r_button.id(object)
        
        if id_clicked in self.activeRadioButtons:
            self.activeRadioButtons.remove(id_clicked)
        else:
            self.activeRadioButtons.append(id_clicked)

        # Read box coordinates
        # frame_number = int(os.path.split(self.img_paths[self.counter])[-1].split('.')[0])
        # coordinates = self.read_box_coordinates(frame_number, self.activeRadioButtons)
        # self.set_image(self.img_paths[self.counter], coordinates, False)


    def check_validity(self):
        """
        :return: if all the necessary information is provided for proper run of application. And error message
        """
        if self.selected_folder == '':
            return False, 'Input folder has to be selected'

        return True, 'Form ok'

    def continue_app(self):
        """
        If the setup form is valid, retrieve the data from the database of the video to annotate
        and then start the LabelerWindow
        """
        form_is_valid, message = self.check_validity()

        if form_is_valid:
            self.close()
            df = get_database(self.selected_folder)
            annotation_window = LabelerWindow(df, self.selected_folder)
            annotation_window.show()
        else:
            self.error_message.setText(message)