import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QGraphicsScene, QFileDialog, QGraphicsPixmapItem,
    QGraphicsView, QListWidget, QListWidgetItem, QInputDialog, QGraphicsTextItem
)
from PyQt5.QtGui import QPixmap, QPen, QColor, QFont, QBrush
from PyQt5.QtCore import Qt, QRectF, QPointF

###############################################################################
#                         ResizableAnnotationRect                             #
###############################################################################

class ResizableAnnotationRect(QGraphicsPixmapItem):
    """
    Rectángulo de anotación que permite redimensionar arrastrando los bordes,
    utiliza un color fijo y muestra la etiqueta por fuera (arriba-izquierda).
    """
    HANDLE_SIZE = 8  # Tamaño en píxeles para detectar los "handles" de redimensionado

    def __init__(self, rect: QRectF, label: str = "", color: QColor = QColor(255, 0, 0)):
        super().__init__()
        self.rect_item = QGraphicsRectItem(rect, parent=self)
        self.label = label
        self.color = color

        # Flags para redimensionar
        self._resizing = False
        self._resizeDir = None
        self._startPos = None
        self._origRect = None

        # QGraphicsTextItem para la etiqueta
        self.textItem = QGraphicsTextItem(self.label, parent=self)
        self.textItem.setDefaultTextColor(Qt.white)
        font = QFont()
        font.setPointSize(8)
        self.textItem.setFont(font)
        self.textItem.setZValue(2)

        # Ajustes iniciales
        self.updateLabelPosition()
        pen = QPen(self.color, 2)
        self.rect_item.setPen(pen)
        self.rect_item.setZValue(1)

    def boundingRect(self):
        return self.rect_item.rect()

    def setRect(self, new_rect: QRectF):
        self.rect_item.setRect(new_rect)
        self.updateLabelPosition()

    def rect(self) -> QRectF:
        return self.rect_item.rect()

    def updateLabelPosition(self):
        """
        Etiqueta por fuera (arriba-izquierda) del rectángulo.
        """
        rect = self.rect()
        textRect = self.textItem.boundingRect()
        margin = 2
        x = rect.left()
        y = rect.top() - textRect.height() - margin
        self.textItem.setPos(x, y)

    def paint(self, painter, option, widget=None):
        # No dibujamos pixmap ni nada; la parte visual la hace rect_item + textItem
        pass

    def mousePressEvent(self, event):
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
        if self._resizing:
            self._resizing = False
            self._resizeDir = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def getResizeHandle(self, pos: QPointF):
        r = self.rect()
        margin = self.HANDLE_SIZE
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
#                           ImageView                                        #
###############################################################################

from PyQt5.QtWidgets import QGraphicsRectItem

class ImageView(QGraphicsView):
    """
    Vista para mostrar la imagen, crear anotaciones y hacer zoom
    alrededor del ratón.
    """
    def __init__(self, scene, main_window, parent=None):
        super().__init__(scene, parent)
        self.main_window = main_window
        self.image_file = None
        self.startPos = None
        self.currentRect = None

        # Zoom alrededor del ratón
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setFocusPolicy(Qt.NoFocus)

    def mousePressEvent(self, event):
        clicked_item = self.itemAt(event.pos())
        if clicked_item is not None and isinstance(clicked_item, ResizableAnnotationRect):
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
        if self.currentRect is not None and self.startPos is not None:
            currentPos = self.mapToScene(event.pos())
            rect = QRectF(self.startPos, currentPos).normalized()
            self.currentRect.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.currentRect is not None:
            rect = self.currentRect.rect()
            if rect.width() < 5 or rect.height() < 5:
                self.scene().removeItem(self.currentRect)
            else:
                # Si tenemos una etiqueta global, se asigna (pero no la sobreescribimos)
                if self.main_window.last_label:
                    self.currentRect.label = self.main_window.last_label
                    self.currentRect.textItem.setPlainText(self.main_window.last_label)
                    self.currentRect.updateLabelPosition()

            self.main_window.addAnnotation(self.currentRect)
            self.currentRect = None
            self.startPos = None
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        modifiers = event.modifiers()
        if modifiers & Qt.ControlModifier or modifiers & Qt.ShiftModifier:
            angle = event.angleDelta().y()
            factor = 1.15 if angle > 0 else 0.85
            self.scale(factor, factor)
            event.accept()
        else:
            super().wheelEvent(event)

###############################################################################
#                           ImageViewer (Ventana Principal)                   #
###############################################################################

class ImageViewer(QMainWindow):
    """
    Ventana principal con:
    - Navegación entre imágenes.
    - Paleta de 10 colores para rectángulos.
    - Etiqueta por fuera (arriba izq).
    - Zoom en posición del ratón.
    - La última etiqueta introducida por el usuario se conserva entre imágenes,
      sin sobreescribirse por lo que exista en un TXT.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visor de Imágenes: Etiquetas persistentes, Zoom y colores")
        self.setGeometry(100, 100, 1000, 600)

        self.image_list = []
        self.current_index = 0
        self.annotations = []
        self.currentTxtFile = None

        # Paleta de 10 colores, se repite
        self.color_palette = [
            QColor("#e6194b"),  # rojo
            QColor("#3cb44b"),  # verde
            QColor("#ffe119"),  # amarillo
            QColor("#0082c8"),  # azul
            QColor("#f58231"),  # naranja
            QColor("#911eb4"),  # púrpura
            QColor("#46f0f0"),  # cian
            QColor("#f032e6"),  # magenta
            QColor("#d2f53c"),  # lima
            QColor("#fabebe"),  # rosa claro
        ]
        self.color_index = 0

        # Esta variable se mantiene aunque cambies de imagen
        # y no se sobreescribe al cargar un TXT.
        self.last_label = ""

        # Dimensiones de la imagen actual
        self.image_width = 1
        self.image_height = 1

        self.setFocusPolicy(Qt.StrongFocus)

        # Layout principal
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QHBoxLayout(self.centralWidget)

        # Panel izquierdo
        self.leftLayout = QVBoxLayout()
        self.btnOpenImage = QPushButton("Abrir imagen(es)")
        self.btnOpenImage.clicked.connect(self.openImages)
        self.leftLayout.addWidget(self.btnOpenImage)

        self.scene = QGraphicsScene()
        self.imageView = ImageView(self.scene, self)
        self.leftLayout.addWidget(self.imageView)
        self.mainLayout.addLayout(self.leftLayout, 3)

        # Panel derecho
        self.rightLayout = QVBoxLayout()
        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QListWidget.ExtendedSelection)
        self.listWidget.itemDoubleClicked.connect(self.editAnnotationLabel)
        self.rightLayout.addWidget(self.listWidget)

        self.btnAssignLabel = QPushButton("Asignar etiqueta a seleccionados")
        self.btnAssignLabel.clicked.connect(self.assignLabelToSelected)
        self.rightLayout.addWidget(self.btnAssignLabel)

        self.btnDeleteAnnotation = QPushButton("Eliminar anotación")
        self.btnDeleteAnnotation.clicked.connect(self.deleteAnnotation)
        self.rightLayout.addWidget(self.btnDeleteAnnotation)

        self.mainLayout.addLayout(self.rightLayout, 1)

    def get_next_color(self) -> QColor:
        """
        Devuelve el siguiente color de la paleta y avanza el índice cíclicamente.
        """
        color = self.color_palette[self.color_index]
        self.color_index = (self.color_index + 1) % len(self.color_palette)
        return color

    def openImages(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Abrir imagen(es)", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        if files:
            self.image_list = files
            self.current_index = 0
            self.loadCurrentImage()

    def loadCurrentImage(self):
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

        self.setWindowTitle(
            f"Imagen {self.current_index + 1} de {len(self.image_list)} - {os.path.basename(filename)}"
        )

    def keyPressEvent(self, event):
        # Navegación entre imágenes
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

    def addAnnotation(self, annotation: ResizableAnnotationRect):
        """
        Se llama al terminar de crear un rectángulo.
        Lo añadimos a la lista interna y lo reflejamos en la listWidget.
        """
        if annotation not in self.annotations:
            self.annotations.append(annotation)

        r = annotation.rect()
        center_x = r.x() + r.width() / 2
        center_y = r.y() + r.height() / 2
        text = (f"Rect: (Centro: {center_x:.3f}, {center_y:.3f}, "
                f"Ancho: {r.width():.3f}, Alto: {r.height():.3f}) - "
                f"Etiqueta: {annotation.label if annotation.label else 'Sin nombre'}")

        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, annotation)
        # Mismo color de fondo en la lista
        item.setBackground(QBrush(annotation.color))
        item.setForeground(QBrush(Qt.black))

        self.listWidget.addItem(item)
        self.updateAnnotationsFile()

        # OJO: No modificamos self.last_label aquí si el rect no tiene label
        # para no romper la persistencia de la última etiqueta que el usuario introdujo.

        if annotation.label:
            # Si el rectángulo sí tiene label, esa es la nueva last_label
            self.last_label = annotation.label

    def updateAnnotationsFile(self):
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
        Carga anotaciones del TXT, crea los rects con su color, 
        pero NO sobreescribe self.last_label con la del archivo.
        """
        if os.path.exists(txt_file):
            with open(txt_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            label = parts[0]
                            norm_center_x = float(parts[1])
                            norm_center_y = float(parts[2])
                            norm_width = float(parts[3])
                            norm_height = float(parts[4])

                            center_x = norm_center_x * self.image_width
                            center_y = norm_center_y * self.image_height
                            width = norm_width * self.image_width
                            height = norm_height * self.image_height

                            x = center_x - width / 2
                            y = center_y - height / 2
                            rect = QRectF(x, y, width, height)

                            color_for_rect = self.get_next_color()
                            annotation = ResizableAnnotationRect(
                                rect, label=label, color=color_for_rect
                            )
                            self.scene.addItem(annotation)
                            self.annotations.append(annotation)

                            annotation.textItem.setPlainText(label)
                            annotation.updateLabelPosition()

                            text = (f"Rect: (Centro: {center_x:.3f}, {center_y:.3f}, "
                                    f"Ancho: {width:.3f}, Alto: {height:.3f}) - "
                                    f"Etiqueta: {label if label else 'Sin nombre'}")

                            item = QListWidgetItem(text)
                            item.setData(Qt.UserRole, annotation)
                            item.setBackground(QBrush(annotation.color))
                            item.setForeground(QBrush(Qt.black))

                            self.listWidget.addItem(item)
                            # No hacemos: if label: self.last_label = label
                            # para NO sobreescribir la última etiqueta global.
                        except Exception as e:
                            print("Error al parsear la anotación:", e)
        else:
            with open(txt_file, "w") as f:
                pass

    def editAnnotationLabel(self, item: QListWidgetItem):
        """
        Edita la etiqueta de un rect existing, con un diálogo.
        """
        annotation = item.data(Qt.UserRole)
        current_label = annotation.label
        new_label, ok = QInputDialog.getText(self, "Editar Etiqueta", "Ingrese nuevo nombre:", text=current_label)
        if ok:
            annotation.label = new_label
            annotation.textItem.setPlainText(new_label)
            annotation.updateLabelPosition()

            r = annotation.rect()
            center_x = r.x() + r.width() / 2
            center_y = r.y() + r.height() / 2
            text = (f"Rect: (Centro: {center_x:.3f}, {center_y:.3f}, "
                    f"Ancho: {r.width():.3f}, Alto: {r.height():.3f}) - "
                    f"Etiqueta: {new_label if new_label else 'Sin nombre'}")
            item.setText(text)

            self.updateAnnotationsFile()
            # Actualizamos last_label a la que acaba de poner el usuario.
            if new_label:
                self.last_label = new_label

    def assignLabelToSelected(self):
        """
        Asigna una etiqueta a todos los ítems seleccionados en la lista,
        y actualiza last_label para las próximas anotaciones.
        """
        selected_items = self.listWidget.selectedItems()
        if not selected_items:
            return
        new_label, ok = QInputDialog.getText(self, "Asignar Etiqueta", "Ingrese la etiqueta para los seleccionados:")
        if ok:
            for item in selected_items:
                annotation = item.data(Qt.UserRole)
                annotation.label = new_label
                annotation.textItem.setPlainText(new_label)
                annotation.updateLabelPosition()

                r = annotation.rect()
                center_x = r.x() + r.width()/2
                center_y = r.y() + r.height()/2
                text = (f"Rect: (Centro: {center_x:.3f}, {center_y:.3f}, "
                        f"Ancho: {r.width():.3f}, Alto: {r.height():.3f}) - "
                        f"Etiqueta: {new_label if new_label else 'Sin nombre'}")
                item.setText(text)
            self.updateAnnotationsFile()
            self.last_label = new_label  # persistimos la nueva etiqueta

    def deleteAnnotation(self):
        selected_items = self.listWidget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            annotation = item.data(Qt.UserRole)
            self.scene.removeItem(annotation)
            if annotation in self.annotations:
                self.annotations.remove(annotation)
            self.listWidget.takeItem(self.listWidget.row(item))
        self.updateAnnotationsFile()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())

