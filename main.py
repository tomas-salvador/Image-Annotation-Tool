import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QGraphicsScene, QFileDialog, QGraphicsPixmapItem,
    QGraphicsView, QListWidget, QListWidgetItem, QInputDialog, QGraphicsTextItem,
    QGraphicsRectItem
)
from PyQt5.QtGui import QPixmap, QPen, QColor, QFont, QBrush
from PyQt5.QtCore import Qt, QRectF, QPointF

###############################################################################
#                             Internationalization                            #
###############################################################################
STRINGS = {
    "en": {
        "window_title": "Image Annotation Tool",
        "open_images": "Open Image(s)",
        "assign_label": "Assign Label to Selected",
        "delete_annotation": "Delete Annotation",
        "rect_no_label": "No Label",
        "dialog_edit_label": "Edit Label",
        "dialog_new_label": "Enter new label:",
        "nav_title": "Image {current} of {total} - {filename}"
    },
    "es": {
        "window_title": "Herramienta de Anotación de Imágenes",
        "open_images": "Abrir imagen(es)",
        "assign_label": "Asignar etiqueta a seleccionados",
        "delete_annotation": "Eliminar anotación",
        "rect_no_label": "Sin nombre",
        "dialog_edit_label": "Editar Etiqueta",
        "dialog_new_label": "Ingrese nueva etiqueta:",
        "nav_title": "Imagen {current} de {total} - {filename}"
    },
    "de": {
        "window_title": "Bild-Anmerkungswerkzeug",
        "open_images": "Bild(er) öffnen",
        "assign_label": "Beschriftung zuweisen",
        "delete_annotation": "Anmerkung löschen",
        "rect_no_label": "Kein Label",
        "dialog_edit_label": "Label bearbeiten",
        "dialog_new_label": "Neues Label eingeben:",
        "nav_title": "Bild {current} von {total} - {filename}"
    },
    "fr": {
        "window_title": "Outil d'annotation d'images",
        "open_images": "Ouvrir Image(s)",
        "assign_label": "Attribuer une étiquette",
        "delete_annotation": "Supprimer l'annotation",
        "rect_no_label": "Pas d'étiquette",
        "dialog_edit_label": "Modifier l'étiquette",
        "dialog_new_label": "Entrez une nouvelle étiquette:",
        "nav_title": "Image {current} sur {total} - {filename}"
    },
    "pt": {
        "window_title": "Ferramenta de Anotação de Imagens",
        "open_images": "Abrir Imagem(s)",
        "assign_label": "Atribuir rótulo aos selecionados",
        "delete_annotation": "Excluir anotação",
        "rect_no_label": "Sem rótulo",
        "dialog_edit_label": "Editar Rótulo",
        "dialog_new_label": "Digite um novo rótulo:",
        "nav_title": "Imagem {current} de {total} - {filename}"
    },
    "ru": {
        "window_title": "Инструмент аннотации изображений",
        "open_images": "Открыть изображение(я)",
        "assign_label": "Назначить метку выделенным",
        "delete_annotation": "Удалить аннотацию",
        "rect_no_label": "Без метки",
        "dialog_edit_label": "Редактировать метку",
        "dialog_new_label": "Введите новую метку:",
        "nav_title": "Изображение {current} из {total} - {filename}"
    }
}

###############################################################################
#                         ResizableAnnotationRect Class                       #
###############################################################################
class ResizableAnnotationRect(QGraphicsPixmapItem):
    """
    Represents a bounding box with a text label drawn above-left.
    Supports resizing by dragging edges or corners.
    """
    HANDLE_SIZE = 8

    def __init__(self, rect: QRectF, label="", color=QColor(255, 0, 0)):
        super().__init__()
        self.rect_item = QGraphicsRectItem(rect, parent=self)
        self.label = label
        self.color = color
        self.textItem = QGraphicsTextItem(self.label, parent=self)
        self.textItem.setDefaultTextColor(Qt.white)
        font = QFont()
        font.setPointSize(8)
        self.textItem.setFont(font)
        self.textItem.setZValue(2)
        self._resizing = False
        self._resizeDir = None
        self._startPos = None
        self._origRect = None
        self.updateLabelPosition()
        pen = QPen(self.color, 2)
        self.rect_item.setPen(pen)
        self.rect_item.setZValue(1)

    def boundingRect(self):
        return self.rect_item.rect()

    def setRect(self, new_rect: QRectF):
        """
        Updates the rectangle and repositions the label.
        """
        self.rect_item.setRect(new_rect)
        self.updateLabelPosition()

    def rect(self) -> QRectF:
        """
        Returns the current rectangle of this annotation.
        """
        return self.rect_item.rect()

    def updateLabelPosition(self):
        """
        Places the label above and to the left of the bounding box.
        """
        margin = 2
        r = self.rect()
        textRect = self.textItem.boundingRect()
        x = r.left()
        y = r.top() - textRect.height() - margin
        self.textItem.setPos(x, y)

    def paint(self, painter, option, widget=None):
        """
        Overridden to prevent default pixmap drawing,
        since we use QGraphicsRectItem and QGraphicsTextItem.
        """
        pass

    def mousePressEvent(self, event):
        """
        Handles mouse press to detect if the user wants to resize the box.
        """
        pos = event.pos()
        handle = self.getResizeHandle(pos)
        if handle:
            self._resizing = True
            self._resizeDir = handle
            self._startPos = event.scenePos()
            self._origRect = QRectF(self.rect())
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Resizes the box while dragging if a handle is active.
        """
        if self._resizing:
            delta = event.scenePos() - self._startPos
            newRect = QRectF(self._origRect)
            if "left" in self._resizeDir:
                newRect.setLeft(newRect.left() + delta.x())
            if "right" in self._resizeDir:
                newRect.setRight(newRect.right() + delta.x())
            if "top" in self._resizeDir:
                newRect.setTop(newRect.top() + delta.y())
            if "bottom" in self._resizeDir:
                newRect.setBottom(newRect.bottom() + delta.y())
            if newRect.width() < 5:
                newRect.setWidth(5)
            if newRect.height() < 5:
                newRect.setHeight(5)
            self.setRect(newRect)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Ends resizing on mouse release.
        """
        if self._resizing:
            self._resizing = False
            self._resizeDir = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def getResizeHandle(self, pos: QPointF):
        """
        Determines if 'pos' is near any edge or corner, returning a direction string.
        """
        margin = self.HANDLE_SIZE
        r = self.rect()
        left, right, top, bottom = r.left(), r.right(), r.top(), r.bottom()
        if abs(pos.x() - left) <= margin and abs(pos.y() - top) <= margin:
            return "top-left"
        if abs(pos.x() - right) <= margin and abs(pos.y() - top) <= margin:
            return "top-right"
        if abs(pos.x() - left) <= margin and abs(pos.y() - bottom) <= margin:
            return "bottom-left"
        if abs(pos.x() - right) <= margin and abs(pos.y() - bottom) <= margin:
            return "bottom-right"
        if abs(pos.x() - left) <= margin and top < pos.y() < bottom:
            return "left"
        if abs(pos.x() - right) <= margin and top < pos.y() < bottom:
            return "right"
        if abs(pos.y() - top) <= margin and left < pos.x() < right:
            return "top"
        if abs(pos.y() - bottom) <= margin and left < pos.x() < right:
            return "bottom"
        return None

###############################################################################
#                                  ImageView                                  #
###############################################################################
class ImageView(QGraphicsView):
    """
    Manages zoom anchored under the mouse and creates bounding boxes on mouse drag.
    """
    def __init__(self, scene, main_window, parent=None):
        super().__init__(scene, parent)
        self.main_window = main_window
        self.startPos = None
        self.currentRect = None
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setFocusPolicy(Qt.NoFocus)

    def mousePressEvent(self, event):
        """
        On left click, starts drawing a new annotation rectangle.
        """
        clicked_item = self.itemAt(event.pos())
        if clicked_item and isinstance(clicked_item, ResizableAnnotationRect):
            super().mousePressEvent(event)
            return
        if event.button() == Qt.LeftButton:
            self.startPos = self.mapToScene(event.pos())
            rect = QRectF(self.startPos, self.startPos)
            color_for_rect = self.main_window.get_next_color()
            self.currentRect = ResizableAnnotationRect(rect, label="", color=color_for_rect)
            self.scene().addItem(self.currentRect)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Updates the annotation rectangle as the user drags the mouse.
        """
        if self.currentRect and self.startPos:
            currentPos = self.mapToScene(event.pos())
            rect = QRectF(self.startPos, currentPos).normalized()
            self.currentRect.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Finalizes the annotation upon mouse release.
        """
        if event.button() == Qt.LeftButton and self.currentRect:
            r = self.currentRect.rect()
            if r.width() < 5 or r.height() < 5:
                self.scene().removeItem(self.currentRect)
            else:
                if self.main_window.last_label:
                    self.currentRect.label = self.main_window.last_label
                    self.currentRect.textItem.setPlainText(self.main_window.last_label)
                    self.currentRect.updateLabelPosition()
            self.main_window.addAnnotation(self.currentRect)
            self.currentRect = None
            self.startPos = None
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        """
        Applies zoom if Ctrl or Shift is held, otherwise pass to default behavior.
        """
        modifiers = event.modifiers()
        if modifiers & Qt.ControlModifier or modifiers & Qt.ShiftModifier:
            angle = event.angleDelta().y()
            factor = 1.15 if angle > 0 else 0.85
            self.scale(factor, factor)
            event.accept()
        else:
            super().wheelEvent(event)

###############################################################################
#                                ImageViewer                                  #
###############################################################################
class ImageViewer(QMainWindow):
    """
    Loads images, manages bounding boxes, and provides multilingual UI.
    """
    def __init__(self):
        super().__init__()
        self.image_list = []
        self.current_index = 0
        self.annotations = []
        self.currentTxtFile = None
        self.languages = ["en", "es", "de", "fr", "pt", "ru"]
        self.current_lang = "en"
        self.color_palette = [
            QColor("#e6194b"), QColor("#3cb44b"), QColor("#ffe119"),
            QColor("#0082c8"), QColor("#f58231"), QColor("#911eb4"),
            QColor("#46f0f0"), QColor("#f032e6"), QColor("#d2f53c"),
            QColor("#fabebe")
        ]
        self.color_index = 0
        self.last_label = ""
        self.image_width = 1
        self.image_height = 1
        self.scene = QGraphicsScene()
        self.setFocusPolicy(Qt.StrongFocus)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QHBoxLayout(self.centralWidget)
        self.leftLayout = QVBoxLayout()
        self.btnOpenImage = QPushButton()
        self.btnOpenImage.clicked.connect(self.openImages)
        self.leftLayout.addWidget(self.btnOpenImage)
        self.imageView = ImageView(self.scene, self)
        self.leftLayout.addWidget(self.imageView)
        self.mainLayout.addLayout(self.leftLayout, 3)
        self.rightLayout = QVBoxLayout()
        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QListWidget.ExtendedSelection)
        self.listWidget.itemDoubleClicked.connect(self.editAnnotationLabel)
        self.rightLayout.addWidget(self.listWidget)
        self.btnAssignLabel = QPushButton()
        self.btnAssignLabel.clicked.connect(self.assignLabelToSelected)
        self.rightLayout.addWidget(self.btnAssignLabel)
        self.btnDeleteAnnotation = QPushButton()
        self.btnDeleteAnnotation.clicked.connect(self.deleteAnnotation)
        self.rightLayout.addWidget(self.btnDeleteAnnotation)
        self.mainLayout.addLayout(self.rightLayout, 1)
        self.set_language("en")
        self.setGeometry(100, 100, 1200, 600)
        self.show()

    def set_language(self, lang):
        """
        Applies a given language from STRINGS if it exists; otherwise defaults to English.
        """
        if lang not in STRINGS:
            lang = "en"
        self.current_lang = lang
        self.setWindowTitle(STRINGS[lang]["window_title"])
        self.btnOpenImage.setText(STRINGS[lang]["open_images"])
        self.btnAssignLabel.setText(STRINGS[lang]["assign_label"])
        self.btnDeleteAnnotation.setText(STRINGS[lang]["delete_annotation"])

    def get_next_color(self) -> QColor:
        """
        Returns the next color in the palette, cycling through 10 colors.
        """
        color = self.color_palette[self.color_index]
        self.color_index = (self.color_index + 1) % len(self.color_palette)
        return color

    def openImages(self):
        """
        Opens a file dialog for selecting one or more images.
        """
        open_title = STRINGS[self.current_lang]["open_images"]
        files, _ = QFileDialog.getOpenFileNames(self, open_title, "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if files:
            self.image_list = files
            self.current_index = 0
            self.loadCurrentImage()

    def loadCurrentImage(self):
        """
        Loads the current image, clears previous annotations, and parses the corresponding TXT file.
        """
        if not self.image_list or self.current_index >= len(self.image_list):
            return
        filename = self.image_list[self.current_index]
        pixmap = QPixmap(filename)
        if pixmap.isNull():
            return
        self.image_width = pixmap.width()
        self.image_height = pixmap.height()
        self.scene.clear()
        item = QGraphicsPixmapItem(pixmap)
        item.setZValue(0)
        self.scene.addItem(item)
        self.imageView.fitInView(item, Qt.KeepAspectRatio)
        self.annotations = []
        self.listWidget.clear()
        base, _ = os.path.splitext(filename)
        self.currentTxtFile = base + ".txt"
        self.loadAnnotations(self.currentTxtFile)
        new_title = STRINGS[self.current_lang]["nav_title"].format(
            current=self.current_index + 1,
            total=len(self.image_list),
            filename=os.path.basename(filename)
        )
        self.setWindowTitle(new_title)

    def keyPressEvent(self, event):
        """
        Handles arrow keys or spacebar to navigate through images.
        """
        if event.key() in (Qt.Key_Right, Qt.Key_Space):
            if self.current_index < len(self.image_list) - 1:
                self.current_index += 1
                self.loadCurrentImage()
            event.accept()
        elif event.key() == Qt.Key_Left:
            if self.current_index > 0:
                self.current_index -= 1
                self.loadCurrentImage()
            event.accept()
        else:
            super().keyPressEvent(event)

    def addAnnotation(self, annotation):
        """
        Appends a newly created bounding box to the list and updates the TXT file.
        """
        if annotation not in self.annotations:
            self.annotations.append(annotation)
        r = annotation.rect()
        cx = r.x() + r.width()/2
        cy = r.y() + r.height()/2
        no_label_str = STRINGS[self.current_lang]["rect_no_label"]
        show_label = annotation.label if annotation.label else no_label_str
        text = (
            f"Label: {show_label}  "
            f"(Center: {cx:.2f}, {cy:.2f}, "
            f"W: {r.width():.2f}, H: {r.height():.2f})"
        )
        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, annotation)
        item.setBackground(QBrush(annotation.color))
        item.setForeground(QBrush(Qt.black))
        self.listWidget.addItem(item)
        self.updateAnnotationsFile()

    def updateAnnotationsFile(self):
        """
        Writes all annotation data to the current TXT file with normalized coordinates.
        """
        if not self.currentTxtFile:
            return
        with open(self.currentTxtFile, "w") as f:
            for ann in self.annotations:
                r = ann.rect()
                center_x = (r.x() + r.width()/2) / self.image_width
                center_y = (r.y() + r.height()/2) / self.image_height
                norm_width = r.width() / self.image_width
                norm_height = r.height() / self.image_height
                line = f"{ann.label} {center_x} {center_y} {norm_width} {norm_height}\n"
                f.write(line)

    def loadAnnotations(self, txt_file):
        """
        Reads the TXT file for the current image, reconstructs bounding boxes, and shows them in the list.
        """
        if os.path.exists(txt_file):
            with open(txt_file, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        label = parts[0]
                        x_c = float(parts[1])
                        y_c = float(parts[2])
                        w_n = float(parts[3])
                        h_n = float(parts[4])
                        cx = x_c * self.image_width
                        cy = y_c * self.image_height
                        w = w_n * self.image_width
                        h = h_n * self.image_height
                        x = cx - w/2
                        y = cy - h/2
                        c = self.get_next_color()
                        ann = ResizableAnnotationRect(QRectF(x, y, w, h), label=label, color=c)
                        self.scene.addItem(ann)
                        self.annotations.append(ann)
                        no_label_str = STRINGS[self.current_lang]["rect_no_label"]
                        label_show = label if label else no_label_str
                        item_txt = (
                            f"Label: {label_show}  "
                            f"(Center: {cx:.2f}, {cy:.2f}, W: {w:.2f}, H: {h:.2f})"
                        )
                        item = QListWidgetItem(item_txt)
                        item.setData(Qt.UserRole, ann)
                        item.setBackground(QBrush(c))
                        item.setForeground(QBrush(Qt.black))
                        self.listWidget.addItem(item)

    def editAnnotationLabel(self, item):
        """
        Lets the user edit a single bounding box label via a dialog.
        """
        annotation = item.data(Qt.UserRole)
        current_label = annotation.label
        new_label, ok = QInputDialog.getText(
            self,
            STRINGS[self.current_lang]["dialog_edit_label"],
            STRINGS[self.current_lang]["dialog_new_label"],
            text=current_label
        )
        if ok:
            annotation.label = new_label
            annotation.textItem.setPlainText(new_label)
            annotation.updateLabelPosition()
            r = annotation.rect()
            no_label_str = STRINGS[self.current_lang]["rect_no_label"]
            show_label = new_label if new_label else no_label_str
            item_txt = (
                f"Label: {show_label}  "
                f"(Center: {r.x() + r.width()/2:.2f}, {r.y() + r.height()/2:.2f}, "
                f"W: {r.width():.2f}, H: {r.height():.2f})"
            )
            item.setText(item_txt)
            self.updateAnnotationsFile()
            if new_label:
                self.last_label = new_label

    def assignLabelToSelected(self):
        """
        Assigns a new label to all selected items in the list.
        """
        selected_items = self.listWidget.selectedItems()
        if not selected_items:
            return
        new_label, ok = QInputDialog.getText(
            self,
            STRINGS[self.current_lang]["dialog_edit_label"],
            STRINGS[self.current_lang]["dialog_new_label"]
        )
        if ok:
            for it in selected_items:
                ann = it.data(Qt.UserRole)
                ann.label = new_label
                ann.textItem.setPlainText(new_label)
                ann.updateLabelPosition()
                r = ann.rect()
                no_label_str = STRINGS[self.current_lang]["rect_no_label"]
                show_label = new_label if new_label else no_label_str
                item_txt = (
                    f"Label: {show_label}  "
                    f"(Center: {r.x() + r.width()/2:.2f}, {r.y() + r.height()/2:.2f}, "
                    f"W: {r.width():.2f}, H: {r.height():.2f})"
                )
                it.setText(item_txt)
            self.updateAnnotationsFile()
            self.last_label = new_label

    def deleteAnnotation(self):
        """
        Deletes the selected annotations from the scene and the list.
        """
        selected_items = self.listWidget.selectedItems()
        if not selected_items:
            return
        for it in selected_items:
            ann = it.data(Qt.UserRole)
            self.scene.removeItem(ann)
            if ann in self.annotations:
                self.annotations.remove(ann)
            self.listWidget.takeItem(self.listWidget.row(it))
        self.updateAnnotationsFile()

###############################################################################
#                                     Main                                    #
###############################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    # viewer.set_language("es") # or de, fr, pt, ru as examples
    viewer.show()
    sys.exit(app.exec_())
