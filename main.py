from PyQt5.QtWidgets import QApplication
import sys

from init import SetupWindow
#import annotation

if __name__ == '__main__':
    # run the application
    app = QApplication(sys.argv)
    ex = SetupWindow()
    ex.show()
    sys.exit(app.exec_())