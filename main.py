from PyQt5.QtWidgets import QApplication
import sys

from init import SetupWindow
from read_data import get_database, get_img_paths
from annotation import LabelerWindow

if __name__ == '__main__':
    # run the application
    # app = QApplication(sys.argv)
    # ex = SetupWindow()
    # ex.show()
    # sys.exit(app.exec_())

    # SHORTCUT
    app = QApplication(sys.argv)
    selected_folder = '/media/inexen/pqp_annotations/Teil2/coloscopie_2021-05-17_14-08-49_PassekRecordingPC'
    labels_to_annotate = ["polyp", "start_withdrawal", "wound", "ileum"]
    labels_to_plot = ["polyp", "snare", "grasper", "ileum", "appendix", "ileocaecalvalve"]

    df, metadata = get_database(selected_folder, labels_to_annotate)
    img_paths = get_img_paths(selected_folder, df)
    ex = LabelerWindow(df, selected_folder, labels_to_annotate, labels_to_plot, metadata, img_paths)
    ex.show()
    sys.exit(app.exec_())