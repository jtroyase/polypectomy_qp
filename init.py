from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QDesktopWidget

from read_data import get_database, get_img_paths
from annotation import LabelerWindow
import user_widgets

import ast

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

        # Select labels checkboxes
        container = QWidget(self)
        container.setFixedSize(680, 145)
        container.move(60, 160)
        container.setStyleSheet("background-color:beige")
        grid, self.l_checkboxes = user_widgets.init_label_checkboxes(container)

        # Next Button
        self.next_button.move(330, 320)
        self.next_button.clicked.connect(self.continue_app)
        self.next_button.setObjectName("blueButton")

        # Error message
        self.error_message.setGeometry(0, 360, self.width - 20, 20)
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
        self.dialog = QFileDialog(self)
        self.dialog.setWindowModality(Qt.WindowModal)
        def_path = user_widgets.read_config('def_path').split('=')[1]
        def_path = ast.literal_eval(" ".join(def_path.split()))
        folder_path = self.dialog.getExistingDirectory(None, "Select Folder", def_path)

        self.selected_folder_label.setText(folder_path)
        self.selected_folder = folder_path

            
    def centerOnScreen(self):
        """
        Centers the window on the screen.
        """
        resolution = QDesktopWidget().screenGeometry()
        self.move(int((resolution.width() / 2) - (self.width / 2)),
                  int((resolution.height() / 2) - (self.height / 2)) - 40)


    def check_validity(self):
        """
        :return: if all the necessary information is provided for proper run of application. And error message
        """
        
        # Check if a folder has been selected
        if self.selected_folder == '':
            return False, 'Input folder has to be selected'

        # Check if at least one label has been ticked
        if all(value.isChecked()==False for value in self.l_checkboxes.values()) == True:
            return False, 'Select at least one label'

        return True, 'Form ok'

    def continue_app(self):
        """
        If the setup form is valid, retrieve the data from the database of the video to annotate
        and then start the LabelerWindow
        """
        form_is_valid, message = self.check_validity()

        if form_is_valid:
            self.hide()

            # Retrieve that the user selected to annotate
            labels_to_annotate = []
            for key, value in self.l_checkboxes.items():
                if value.isChecked() == True:
                    labels_to_annotate.append(key)

            labels_to_plot = ast.literal_eval('[' + user_widgets.read_config('labels_to_plot').split('[')[1])

            # Get the database
            df, metadata = get_database(self.selected_folder, labels_to_annotate)
            img_paths = get_img_paths(self.selected_folder, df)
            self.annotation_window = LabelerWindow(df, self.selected_folder, labels_to_annotate, labels_to_plot, metadata, img_paths)
            self.annotation_window.show()
        else:
            self.error_message.setText(message)
