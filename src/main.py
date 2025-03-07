import sys

from PySide6 import QtCore

from main_window.main_window import MainWindow  # type: ignore
from ocrreader2 import ocrreader2  # type: ignore

if __name__ == "__main__":
    app = ocrreader2(sys.argv)

    translator = QtCore.QTranslator()

    if translator.load(QtCore.QLocale().system(), "ocrreader", "_", "."):
        QtCore.QCoreApplication.installTranslator(translator)

    window = MainWindow()

    window.show()
    app.exec()
