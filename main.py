from PyQt5.QtWidgets import QApplication
import sys

from init import SetupWindow


if __name__ == '__main__':
    #run the application
    app = QApplication(sys.argv)
    ex = SetupWindow()
    ex.show()
    sys.exit(app.exec_())

    #SHORTCUT
    # app = QApplication(sys.argv)
    # selected_folder = '/media/inexen/CADe_comparison_review/Polypectomy-Data/coloscopie_2018-12-20_12-16-02_BoeckRetro'
    # labels_to_annotate = ['polyp', 'needle', 'grasper', 'snare', 'clip', 'wound', 'ileum']
    # df, metadata = get_database(selected_folder, labels_to_annotate)
    # img_paths = get_img_paths(selected_folder, df)
    # ex = LabelerWindow(df, selected_folder, labels_to_annotate, metadata, img_paths)
    # ex.show()
    # sys.exit(app.exec_())