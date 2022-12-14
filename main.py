from PyQt5.QtWidgets import QApplication
import sys

from init import SetupWindow
from annotation import LabelerWindow
#import annotation
from read_data import get_database

if __name__ == '__main__':
    # run the application
    # app = QApplication(sys.argv)
    # ex = SetupWindow()
    # ex.show()
    # sys.exit(app.exec_())

    # SHOOOORTCUT
    app = QApplication(sys.argv)
    selected_folder = '/media/inexen/CADe_comparison_review/PolypectomyQualityPredictor/coloscopie_2021-03-23_15-00-16_Ludwig_crop'
    labels_to_annotate = ['polyp', 'needle', 'grasper', 'snare', 'clip']
    df, metadata = get_database(selected_folder, labels_to_annotate)
    ex = LabelerWindow(df, selected_folder, labels_to_annotate, metadata)
    ex.show()
    sys.exit(app.exec_())