from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsPixmapItem, 
    QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsItem, QGraphicsEllipseItem
)
from PyQt5.QtGui import QColor, QPen, QFont, QPainter, QBrush
from PyQt5.QtCore import Qt, QRectF, QPointF

class AnnotationGraphicsItem(QGraphicsPixmapItem):
    HANDLE_SIZE = 8  # Tamaño de los puntos de control
    
    def __init__(self, rect: QRectF, label="", color=QColor(255, 0, 0), parent=None):
        super().__init__(parent)
        self.rect_item = QGraphicsRectItem(rect, parent=self)
        self.label = label
        self.color = color
        self.textItem = QGraphicsTextItem(self.label, parent=self)
        self.is_selected = False
        self.isAnnotationItem = True
        self.handles = []  # Para almacenar los puntos de control
        
        self._setup_appearance()
        
    def _setup_appearance(self):
        """Configura los aspectos visuales incluyendo los puntos de control"""
        self.textItem.setDefaultTextColor(Qt.white)
        font = QFont()
        font.setPointSize(8)
        self.textItem.setFont(font)
        
        pen = QPen(self.color, 3 if self.is_selected else 2)
        pen.setStyle(Qt.DashLine if self.is_selected else Qt.SolidLine)
        self.rect_item.setPen(pen)
        
        self.updateLabelPosition()
        self.updateHandles()  # Actualizar puntos de control
        
    def setSelected(self, selected):
        self.is_selected = selected
        self._setup_appearance()
        
    def setRect(self, new_rect: QRectF):
        self.rect_item.setRect(new_rect)
        self.updateLabelPosition()
        self.updateHandles()
        
    def rect(self) -> QRectF:
        return self.rect_item.rect()
        
    def updateLabelPosition(self):
        margin = 2
        r = self.rect()
        textRect = self.textItem.boundingRect()
        x = r.left()
        y = r.top() - textRect.height() - margin
        self.textItem.setPos(x, y)
        
    def updateHandles(self):
        """Actualiza las posiciones de los puntos de control"""
        # Limpiar handles anteriores
        for handle in self.handles:
            try:
                # Verificar si el handle existe y está en la escena
                if handle and handle.scene():
                    scene = handle.scene()
                    if scene:
                        scene.removeItem(handle)
            except RuntimeError:
                # El objeto C++ ya fue eliminado, continuamos
                continue
        self.handles = []
        
        if not self.is_selected:
            return
            
        r = self.rect()
        corners = [
            r.topLeft(), r.topRight(), 
            r.bottomLeft(), r.bottomRight()
        ]
        
        for corner in corners:
            handle = QGraphicsEllipseItem(
                -self.HANDLE_SIZE/2, -self.HANDLE_SIZE/2,
                self.HANDLE_SIZE, self.HANDLE_SIZE,
                parent=self
            )
            handle.setPos(corner)
            handle.setBrush(QBrush(self.color))
            handle.setPen(QPen(Qt.black, 1))
            self.handles.append(handle)

# ---------------------------------------------------------------------------------
#                           AnnotationView View
# ---------------------------------------------------------------------------------
        # self.setMouseTracking(True)
        
class AnnotationView(QGraphicsView):
    """Vista especializada para manejar anotaciones sobre imágenes"""
    def __init__(self, scene, main_window, parent=None):
        super().__init__(scene, parent)
        self.main_window = main_window
        self.startPos = None
        self.currentRect = None
        self.image_item = None
        self._selected_annotation = None
        self._dragging = False
        self._resizing = False
        
        # Configuración básica de la vista
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setFocusPolicy(Qt.NoFocus)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setMouseTracking(True)

    def unselectAnnotation(self):
        if self._selected_annotation:
            self._selected_annotation.setSelected(False)
        self._selected_annotation = None
    
    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
    
        # Click derecho para seleccionar
        if event.button() == Qt.RightButton:
            # Limpiar selección en la lista
            self.main_window.listWidget.clearSelection()
            
            # Deseleccionar todas primero
            for ann in self.scene().items():
                if isinstance(ann, AnnotationGraphicsItem):
                    ann.setSelected(False)
            # Buscar y deseleccionar el ítem correspondiente en la lista
            for i in range(self.main_window.listWidget.count()):
                list_item = self.main_window.listWidget.item(i)
                list_item.setSelected(False)
                            
            # Resto de la lógica de selección gráfica...
            for item in self.scene().items():
                if isinstance(item, AnnotationGraphicsItem):
                    if item.rect().contains(scene_pos):
                        # Seleccionar esta
                        item.setSelected(True)
                        self._selected_annotation = item
                        
                        # Buscar y seleccionar en la lista
                        for i in range(self.main_window.listWidget.count()):
                            list_item = self.main_window.listWidget.item(i)
                            if list_item.data(Qt.UserRole) == item:
                                self.main_window.listWidget.setCurrentItem(list_item)
                                break
                        
                        break
            event.accept()
            return
        
        # Click izquierdo para mover, redimensionar o crear
        if event.button() == Qt.LeftButton:
            if self._selected_annotation:
                # Verificar si se hizo click en un handle
                for handle in self._selected_annotation.handles:
                    try:
                        if handle and handle.scene() and handle.contains(handle.mapFromScene(scene_pos)):
                            self.main_window.save_current_state()
                            self._resizing = True
                            self._resize_handle = handle
                            self._original_rect = self._selected_annotation.rect()
                            self._resize_start_pos = scene_pos
                            break
                    except RuntimeError:
                        # Si el handle fue eliminado, lo quitamos de la lista
                        self._selected_annotation.handles.remove(handle)
                        continue
                if not self._resizing:
                    # Comenzar arrastre
                    self.main_window.save_current_state()
                    self._dragging = True
                    self._drag_start_pos = scene_pos
                    self._original_rect = self._selected_annotation.rect()
            else:
                # Crear nueva anotación
                self.startPos = scene_pos
                color = self.main_window.get_next_color()
                self.currentRect = AnnotationGraphicsItem(
                    QRectF(scene_pos, scene_pos), 
                    label="", 
                    color=color
                )
                self.scene().addItem(self.currentRect)
            event.accept()
            return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        
        # Redimensionar anotación seleccionada
        if hasattr(self, '_resizing') and self._resizing and self._selected_annotation and self.image_item:
            image_rect = self.image_item.sceneBoundingRect()
            delta = scene_pos - self._resize_start_pos
            new_rect = QRectF(self._original_rect)
            
            # Determinar qué esquina estamos moviendo
            handle_pos = self._resize_handle.pos()
            if handle_pos == self._original_rect.topLeft():
                new_rect.setTopLeft(image_rect.intersected(
                    QRectF(new_rect.topLeft() + delta, new_rect.bottomRight())
                ).topLeft())
            elif handle_pos == self._original_rect.topRight():
                new_rect.setTopRight(image_rect.intersected(
                    QRectF(new_rect.topRight() + delta, new_rect.bottomLeft())
                ).topRight())
            elif handle_pos == self._original_rect.bottomLeft():
                new_rect.setBottomLeft(image_rect.intersected(
                    QRectF(new_rect.bottomLeft() + delta, new_rect.topRight())
                ).bottomLeft())
            elif handle_pos == self._original_rect.bottomRight():
                new_rect.setBottomRight(image_rect.intersected(
                    QRectF(new_rect.bottomRight() + delta, new_rect.topLeft())
                ).bottomRight())
                
            # Asegurar tamaño mínimo
            if new_rect.width() < 5:
                if handle_pos.x() == self._original_rect.left():
                    new_rect.setLeft(new_rect.right() - 5)
                else:
                    new_rect.setRight(new_rect.left() + 5)
            if new_rect.height() < 5:
                if handle_pos.y() == self._original_rect.top():
                    new_rect.setTop(new_rect.bottom() - 5)
                else:
                    new_rect.setBottom(new_rect.top() + 5)
            
            self._selected_annotation.setRect(new_rect)
            event.accept()
            return
        
        # Mover anotación seleccionada
        if self._dragging and self._selected_annotation:
            delta = scene_pos - self._drag_start_pos
            new_rect = self._original_rect.translated(delta.x(), delta.y())
            self._selected_annotation.setRect(new_rect)
            event.accept()
            return
        
        # Crear nueva anotación
        if self.currentRect and self.startPos:
            self.currentRect.setRect(QRectF(self.startPos, scene_pos).normalized())
            event.accept()
            return
            
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if hasattr(self, '_resizing') and self._resizing:
                # Finalizar redimensionamiento
                self._resizing = False
                if hasattr(self, 'main_window'):
                    self.main_window.update_annotation_list()
                event.accept()
                return
            elif self._dragging:
                # Finalizar arrastre
                self._dragging = False
                if hasattr(self, 'main_window'):
                    self.main_window.update_annotation_list()
                event.accept()
                return
                
            if self.currentRect:
                # Finalizar creación de nueva anotación
                if self.image_item:
                    image_rect = self.image_item.sceneBoundingRect()
                    final_rect = self.currentRect.rect().intersected(image_rect)
                    
                    if final_rect.width() >= 5 and final_rect.height() >= 5:
                        self.currentRect.setRect(final_rect)
                        if self.main_window.last_label:
                            self.currentRect.label = self.main_window.last_label
                            self.currentRect.textItem.setPlainText(self.main_window.last_label)
                            self.currentRect.updateLabelPosition()
                        self.main_window.addAnnotation(self.currentRect)
                    else:
                        self.scene().removeItem(self.currentRect)
                
                self.currentRect = None
                self.startPos = None
                event.accept()
                return
        
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