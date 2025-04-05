from PySide6.QtCore import (
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    Signal,
)
from PySide6.QtGui import QImage, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QListView,
    QStyledItemDelegate,
    QStyleOptionViewItem,
)

from settings.settings import Settings  # type: ignore


class StyledItemDelegate(QStyledItemDelegate):
    def initStyleOption(
        self, option: QStyleOptionViewItem, index: QPersistentModelIndex | QModelIndex
    ) -> None:
        super(StyledItemDelegate, self).initStyleOption(option, index)
        option.decorationPosition = QStyleOptionViewItem.Position.Top  # type: ignore
        option.displayAlignment = (  # type: ignore
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
        )


class ItemImage(QStandardItem):
    def __init__(self, image_path: str, page_data: dict, thumbnail_size: int) -> None:
        super().__init__()

        # TODO: Use larger thumbnail, scale down in view

        self.setEditable(False)
        thumbnail = QImage(image_path).scaled(
            thumbnail_size,
            thumbnail_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setData(thumbnail, Qt.ItemDataRole.DecorationRole)
        self.setText(str(page_data.get("number", "")))
        self.setData(page_data, Qt.ItemDataRole.UserRole)


class PagesListStore(QStandardItemModel):
    def __init__(self, thumbnail_size: int, parent) -> None:
        super().__init__(parent)

        self.thumbnail_size = thumbnail_size

    def add_page(self, image_path: str, page_data: dict) -> None:
        item = ItemImage(image_path, page_data, self.thumbnail_size)
        self.appendRow(item)

    def flags(self, index) -> Qt.ItemFlag:
        default_flags = super().flags(index)

        if index.isValid():
            return (
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsDragEnabled
            )

        return default_flags


class PagesIconView(QListView):
    current_page_changed = Signal(int, int)
    selection_changed = Signal(list)

    def __init__(self, settings: Settings, parent) -> None:
        super().__init__(parent)

        self.settings = settings

        model = PagesListStore(
            self.settings.get(
                "thumbnail_size", self.settings.get("thumbnail_size", 150)
            ),
            self,
        )
        self.setModel(model)
        # self.setViewMode(QListView.ViewMode.IconMode)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.setWordWrap(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.project = None

        delegate = StyledItemDelegate(self)
        self.setItemDelegate(delegate)

        self.selectionModel().currentChanged.connect(self.emit_page_changed)
        self.selectionModel().selectionChanged.connect(self.emit_selection_changed)

    #     self.installEventFilter(self)

    # def eventFilter(self, obj: QObject, event: QEvent) -> bool:
    #     if event.type() == QEvent.Type.KeyPress:
    #             qDebug("KeyPress")
    #     return super().eventFilter(obj, event)

    def clear(self) -> None:
        model = self.model()

        if isinstance(model, PagesListStore):
            model.clear()

    def emit_page_changed(self) -> None:
        index = self.currentIndex().data(Qt.ItemDataRole.UserRole)
        if index:
            self.current_page_changed.emit(
                index.get("number") - 1, self.model().rowCount()
            )

    def emit_selection_changed(self) -> None:
        selected_pages = [
            index.data(Qt.ItemDataRole.UserRole).get("number") - 1
            for index in self.selectedIndexes()
        ]
        self.selection_changed.emit(selected_pages)

    def remove_selected_pages(self) -> None:
        model = self.model()

        if isinstance(model, PagesListStore):
            for index in self.selectedIndexes():
                model.removeRow(index.row())

    def add_page(self, image_path: str, page_data: dict) -> None:
        model = self.model()
        if isinstance(model, PagesListStore):
            model.add_page(image_path, page_data)

    def clean_pages(self) -> None:
        model = self.model()

        if isinstance(model, PagesListStore):
            model.clear()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            # Delete the currently selected item
            self.remove_selected_pages()
        elif event.key() == Qt.Key.Key_Up:
            index = self.currentIndex()
            if index.row() > 0:
                self.setCurrentIndex(
                    self.model().index(index.row() - 1, index.column())
                )
        elif event.key() == Qt.Key.Key_Down:
            index = self.currentIndex()
            if index.row() < self.model().rowCount() - 1:
                self.setCurrentIndex(
                    self.model().index(index.row() + 1, index.column())
                )
        elif event.key() == Qt.Key.Key_PageUp:
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - self.viewport().height()
            )
        elif event.key() == Qt.Key.Key_PageDown:
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + self.viewport().height()
            )
        else:
            # Pass the event on to the default handler
            super().keyPressEvent(event)

    def page_selected(self, index: QModelIndex):
        page = index.data(Qt.ItemDataRole.UserRole)

        # if page:
        #     if self.box_editor.current_page == page:
        #         return

        #     self.box_editor.load_page(page)
        #     self.project.current_page_idx = self.page_icon_view.currentIndex().row()
        #     self.box_editor.scene().update()
        #     # self.box_editor.setFocus()
        # else:
        #     self.box_editor.clear()

    def open_page(self, page_index: int):
        self.setCurrentIndex(self.model().index(page_index, 0))

    def get_current_page_index(self) -> int:
        return self.currentIndex().row()

    def focusNextChild(self) -> bool:
        return False
