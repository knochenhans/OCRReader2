import sys
from PySide6.QtWidgets import (
    QApplication,
)

from src.model_trainer.model_trainer_dialog import ModelTrainerDialog  # type: ignore

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModelTrainerDialog("deu", "/tmp/tesstraintest", "/usr/share/tessdata")
    window.show()
    sys.exit(app.exec())
