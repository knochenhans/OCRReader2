import sys

from PySide6 import QtCore

from OCRReader2.main_window.main_window import MainWindow
from OCRReader2.OCRReader2 import OCRReader2

if __name__ == "__main__":
    app = OCRReader2(sys.argv)

    translator = QtCore.QTranslator()

    if translator.load(QtCore.QLocale().system(), "ocrreader", "_", "."):
        QtCore.QCoreApplication.installTranslator(translator)

    window = MainWindow()

    window.show()
    app.exec()
