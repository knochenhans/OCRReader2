from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QContextMenuEvent
from PySide6.QtWidgets import QMenu, QTextEdit


class ClickableTextEdit(QTextEdit):
    linkRightClicked = Signal(str)
    ctrlEnterPressed = Signal()

    def mousePressEvent(self, e):
        self.anchor = self.anchorAt(e.pos())
        super().mousePressEvent(e)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        anchor = self.anchorAt(event.pos())
        if anchor:
            menu = QMenu(self)
            action = menu.addAction("Switch Hyphenation")
            action.triggered.connect(lambda: self.linkRightClicked.emit(anchor))
            menu.exec(event.globalPos())
        else:
            super().contextMenuEvent(event)

    def keyPressEvent(self, event):
        if (
            event.key() == Qt.Key.Key_Return
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self.ctrlEnterPressed.emit()
        else:
            super().keyPressEvent(event)
