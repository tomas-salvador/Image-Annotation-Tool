from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsPixmapItem, QGraphicsLineItem,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem,
    QGraphicsPathItem
)
from PyQt5.QtGui import QColor, QPen, QFont, QPainter, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF

class PolylineAnnotationItem(QGraphicsPixmapItem):
    HANDLE_SIZE = 6

    def __init__(self, points=None, label="", name="", color=QColor(0,255,0), parent=None):
        super().__init__(parent)
        self.points = points if points else []
        self.path_item = QGraphicsPathItem(parent=self)
        self.label = label
        self.name = name
        self.color = color
        self.textItem = QGraphicsTextItem(self.name, parent=self)
        self.is_selected = False
        self.isAnnotationItem = True
        self.handles = []
        self._preview_point = None
        self.is_class_visible = True
        
        self._setup_appearance()

    def setClassVisible(self, visible: bool):
        self.is_class_visible = visible
        self.setVisible(visible)
        if hasattr(self, "rect_item"):
            self.rect_item.setVisible(visible)
        if hasattr(self, "line_item"):
            self.line_item.setVisible(visible)
        if hasattr(self, "path_item"):
            self.path_item.setVisible(visible)
        #if hasattr(self, "textItem"):
        #    self.textItem.setVisible(visible)
        for h in getattr(self, "handles", []):
            if h:
                h.setVisible(visible)
        
    def normalizeOrder(self):
        """Si el último punto está más abajo (o igual y más a la izquierda) que el primero,
        se invierte la lista completa de puntos. Si no, se deja como está."""
        if len(self.points) < 2:
            return

        first = self.points[0]
        last = self.points[-1]

        # ¿Está el último "más abajo"? (mayor y, o mismo y y menor x)
        if (last.y() > first.y()) or (last.y() == first.y() and last.x() < first.x()):
            self.points.reverse()

        self.setPoints(self.points)
        
    def _setup_appearance(self):
        self.updatePath()
        self.textItem.setDefaultTextColor(Qt.white)
        font = QFont()
        font.setPointSize(4)
        self.textItem.setFont(font)
        self.updateLabelPosition()
        self.updateHandles()
    
    def setNameVisible(self, visible: bool):
        if hasattr(self, "textItem"):
            self.textItem.setVisible(visible)


    def updatePath(self):
        """Construye el path con los puntos reales y, opcionalmente, con un punto de preview."""
        path = QPainterPath()
        if self.points:
            path.moveTo(self.points[0])
            for p in self.points[1:]:
                path.lineTo(p)

        # Si existe un punto de preview, lo añadimos solo al trazado visual (no a self.points)
        if getattr(self, "_preview_point", None) is not None:
            path.lineTo(self._preview_point)

        pen = QPen(self.color, 2 if not self.is_selected else 3)
        pen.setStyle(Qt.DashLine if self.is_selected else Qt.SolidLine)
        self.path_item.setPen(pen)
        self.path_item.setPath(path)
    def setPreviewPoint(self, point: QPointF):
        """Establece un punto temporal que se dibuja en el path sin modificar self.points."""
        self._preview_point = point
        self.updatePath()

    def clearPreview(self):
        """Elimina el punto de preview y actualiza el path."""
        self._preview_point = None
        self.updatePath()


    def setSelected(self, selected):
        self.is_selected = selected
        self._setup_appearance()

    def setSelectedNoAperance(self, selected):
        self.is_selected = selected

    def updateLabelPosition(self):
        if not self.points:
            return
        # colocar etiqueta en el punto medio de la polilínea
        xs = [p.x() for p in self.points]
        ys = [p.y() for p in self.points]
        midpoint = QPointF(sum(xs)/len(xs), sum(ys)/len(ys))
        self.textItem.setPos(midpoint)

    def updateHandles(self):
        for h in self.handles:
            try:
                if h and h.scene():
                    h.scene().removeItem(h)
            except RuntimeError:
                continue
        self.handles = []
        if not self.is_selected:
            return
        for p in self.points:
            handle = QGraphicsEllipseItem(
                -self.HANDLE_SIZE/2, -self.HANDLE_SIZE/2,
                self.HANDLE_SIZE, self.HANDLE_SIZE,
                parent=self
            )
            handle.setPos(p)
            handle.setBrush(QBrush(self.color))
            handle.setPen(QPen(Qt.black, 1))
            self.handles.append(handle)

    def setPoints(self, points):
        self.points = points
        self.updatePath()
        self.updateLabelPosition()
        self.updateHandles()

    def getPoints(self):
        return self.points
    
class LineAnnotationItem(QGraphicsPixmapItem):
    HANDLE_SIZE = 8

    def __init__(self, line, label="", name="", color=QColor(255,0,0), parent=None):
        super().__init__(parent)
        self.line_item = QGraphicsLineItem(line, parent=self)
        self.label = label
        self.name = name
        self.color = color
        self.textItem = QGraphicsTextItem(self.name, parent=self)
        self.is_selected = False
        self.isAnnotationItem = True
        self.handles = []
        self.is_class_visible = True

        self._setup_appearance()

    def setClassVisible(self, visible: bool):
        self.is_class_visible = visible
        self.setVisible(visible)
        if hasattr(self, "rect_item"):
            self.rect_item.setVisible(visible)
        if hasattr(self, "line_item"):
            self.line_item.setVisible(visible)
        if hasattr(self, "path_item"):
            self.path_item.setVisible(visible)
        #if hasattr(self, "textItem"):
        #    self.textItem.setVisible(visible)
        for h in getattr(self, "handles", []):
            if h:
                h.setVisible(visible)
        
    def _setup_appearance(self):
        self.textItem.setDefaultTextColor(Qt.white)
        font = QFont()
        font.setPointSize(4)
        self.textItem.setFont(font)

        pen = QPen(self.color, 2 if not self.is_selected else 3)
        pen.setStyle(Qt.DashLine if self.is_selected else Qt.SolidLine)
        self.line_item.setPen(pen)

        self.updateLabelPosition()
        self.updateHandles()

    def setNameVisible(self, visible: bool):
        if hasattr(self, "textItem"):
            self.textItem.setVisible(visible)


    def setSelected(self, selected):
        self.is_selected = selected
        self._setup_appearance()

    def setSelectedNoAperance(self, selected):
        self.is_selected = selected
        #self._setup_appearance()

    def line(self):
        return self.line_item.line()

    def setLine(self, line):
        self.line_item.setLine(line)
        self.updateLabelPosition()
        self.updateHandles()

    def updateLabelPosition(self):
        line = self.line_item.line()
        midpoint = (line.p1() + line.p2()) / 2
        self.textItem.setPos(midpoint)

    def updateHandles(self):
        """Actualiza los puntos de control en los extremos de la línea"""
        # Eliminar handles anteriores
        for handle in self.handles:
            try:
                if handle and handle.scene():
                    scene = handle.scene()
                    if scene:
                        scene.removeItem(handle)
            except RuntimeError:
                continue
        self.handles = []

        if not self.is_selected:
            return

        line = self.line_item.line()
        endpoints = [line.p1(), line.p2()]

        for point in endpoints:
            handle = QGraphicsEllipseItem(
                -self.HANDLE_SIZE/2, -self.HANDLE_SIZE/2,
                self.HANDLE_SIZE, self.HANDLE_SIZE,
                parent=self
            )
            handle.setPos(point)
            handle.setBrush(QBrush(self.color))
            handle.setPen(QPen(Qt.black, 1))
            self.handles.append(handle)

class AnnotationGraphicsItem(QGraphicsPixmapItem):
    HANDLE_SIZE = 8  # Tamaño de los puntos de control
                
    def __init__(self, rect: QRectF, label="", name="", color=QColor(255, 0, 0), parent=None):
        super().__init__(parent)
        self.rect_item = QGraphicsRectItem(rect, parent=self)
        self.label = label
        self.name = name
        self.color = color
        self.textItem = QGraphicsTextItem(self.name, parent=self)
        self.is_selected = False
        self.isAnnotationItem = True
        self.handles = []  # Para almacenar los puntos de control
        self.is_class_visible = True

        self._setup_appearance()

    def setClassVisible(self, visible: bool):
        self.is_class_visible = visible
        self.setVisible(visible)
        if hasattr(self, "rect_item"):
            self.rect_item.setVisible(visible)
        if hasattr(self, "line_item"):
            self.line_item.setVisible(visible)
        if hasattr(self, "path_item"):
            self.path_item.setVisible(visible)
        #if hasattr(self, "textItem"):
        #    self.textItem.setVisible(visible)
        for h in getattr(self, "handles", []):
            if h:
                h.setVisible(visible)
        
    def _setup_appearance(self):
        """Configura los aspectos visuales incluyendo los puntos de control"""
        self.textItem.setDefaultTextColor(Qt.white)
        font = QFont()
        font.setPointSize(4)
        self.textItem.setFont(font)
        
        pen = QPen(self.color, 3 if self.is_selected else 2)
        pen.setStyle(Qt.DashLine if self.is_selected else Qt.SolidLine)
        self.rect_item.setPen(pen)
        
        self.updateLabelPosition()
        self.updateHandles()  # Actualizar puntos de control
        
    def setNameVisible(self, visible: bool):
        if hasattr(self, "textItem"):
            self.textItem.setVisible(visible)

    def setSelected(self, selected):
        self.is_selected = selected
        self._setup_appearance()

    def setSelectedNoAperance(self, selected):
        self.is_selected = selected
        #self._setup_appearance()
        
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
        self._panning = False  # Para controlar el desplazamiento de la imagen con el raton
        self._pan_start_pos = QPointF()  # Posición inicial del pan
        self.setCursor(Qt.ArrowCursor) # Para el moviento de la imagen con el raton
        self.main_window = main_window
        self.startPos = None
        self.currentRect = None
        self.image_item = None
        self._selected_annotation = None
        self._dragging = False
        self._resizing = False
        self.creating_polyline = False
        
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

    def unselectAnnotationNoAperance(self):
        if self._selected_annotation:
            self._selected_annotation.setSelectedNoAperance(False)
        self._selected_annotation = None
    
    def point_line_distance(self, p, a, b):
        """Devuelve la distancia del punto p al segmento AB"""
        line = QLineF(a, b)
        if line.length() == 0:
            return (p - a).manhattanLength()
        t = max(0, min(1, ((p.x()-a.x())*(b.x()-a.x()) + (p.y()-a.y())*(b.y()-a.y())) / line.length()**2))
        proj = QPointF(a.x() + t*(b.x()-a.x()), a.y() + t*(b.y()-a.y()))
        return (p - proj).manhattanLength()


    def mousePressEvent(self, event):
        if self._selected_annotation and self._selected_annotation.scene() is None:
            self._selected_annotation = None
        scene_pos = self.mapToScene(event.pos())

        # ------------------------------
        # CLICK DERECHO → Selección
        # ------------------------------
        if event.button() == Qt.RightButton:
            # --- Caso especial: cerrar polilínea en creación ---
            if self.creating_polyline and isinstance(self.currentRect, PolylineAnnotationItem):
                points = self.currentRect.getPoints()
                if len(points) >= 2:
                    if self.main_window.last_label:
                        self.currentRect.label = self.main_window.last_label
                        self.currentRect.name = self.main_window.class_names.get(
                            self.main_window.last_label, f"Clase {self.main_window.last_label}"
                        )
                        self.currentRect.textItem.setPlainText(self.currentRect.name)
                        self.currentRect.updateLabelPosition()
                    # antes de añadir, quitar cualquier preview
                    self.currentRect.clearPreview()
                    self.currentRect.normalizeOrder()
                    self.main_window.addAnnotation(self.currentRect)
                else:
                    # no hay suficientes puntos → eliminar item
                    self.currentRect.clearPreview()
                    self.scene().removeItem(self.currentRect)

                self.currentRect = None
                self.startPos = None
                self.creating_polyline = False
                event.accept()
                return

            # --- Caso especial: borrar vértice en polyline seleccionada ---
            if (
                (event.modifiers() & Qt.ControlModifier)
                and isinstance(self._selected_annotation, PolylineAnnotationItem)
                and self._selected_annotation.scene() is not None
            ):
                points = self._selected_annotation.getPoints()
                clicked_idx = None
                tolerance = max(6, PolylineAnnotationItem.HANDLE_SIZE)

                for i, p in enumerate(points):
                    if QLineF(scene_pos, p).length() <= tolerance:
                        clicked_idx = i
                        break

                if clicked_idx is not None:
                    self.main_window.save_current_state()

                    if len(points) <= 2:
                        if self._selected_annotation in self.main_window.annotations:
                            self.main_window.annotations.remove(self._selected_annotation)
                        self.scene().removeItem(self._selected_annotation)
                        self._selected_annotation = None
                        self.main_window.update_annotation_list()
                    else:
                        new_points = points[:clicked_idx] + points[clicked_idx+1:]
                        self._selected_annotation.setPoints(new_points)
                        self._selected_annotation.normalizeOrder()
                        self.main_window.update_annotation_list()

                        # mantener sincronizada la selección en la lista
                        for i in range(self.main_window.listWidget.count()):
                            list_item = self.main_window.listWidget.item(i)
                            if list_item.data(Qt.UserRole) == self._selected_annotation:
                                self.main_window.listWidget.setCurrentItem(list_item)
                                break

                    event.accept()
                    return


            # --- Selección normal (como ya lo tenías) ---
            self.main_window.listWidget.clearSelection()
            for ann in self.scene().items():
                if hasattr(ann, "isAnnotationItem"):
                    ann.setSelected(False)
            for i in range(self.main_window.listWidget.count()):
                self.main_window.listWidget.item(i).setSelected(False)
            self._selected_annotation = None

            # Ctrl + click derecho → cambiar etiqueta (solo BOX por ahora)
            if event.modifiers() & Qt.ControlModifier:
                for item in self.scene().items():
                    hit = False
                    # 📦 BOX
                    if isinstance(item, AnnotationGraphicsItem) and item.rect().contains(scene_pos):
                        hit = True
                    # 📏 LINE
                    elif isinstance(item, LineAnnotationItem):
                        p1, p2 = item.line().p1(), item.line().p2()
                        if self.point_line_distance(scene_pos, p1, p2) < 5:
                            hit = True
                    # 🔗 POLYLINE
                    elif isinstance(item, PolylineAnnotationItem):
                        points = item.getPoints()
                        for i in range(len(points) - 1):
                            if self.point_line_distance(scene_pos, points[i], points[i+1]) < 5:
                                hit = True
                                break
                    if hit:
                        self.main_window.save_current_state()
                        new_label = str(self.main_window.last_label)
                        if self._relabel_item(item, new_label):
                            self.main_window.updateAnnotationsFile()
                            self.main_window.loadCurrentImage()
                        event.accept()
                        return

            # Selección normal
            for item in self.scene().items():
                if not getattr(item, "isAnnotationItem", False):
                    continue
                if not getattr(item, "is_class_visible", True):
                    continue  # 🔹 saltar objetos de clases invisibles
                if isinstance(item, AnnotationGraphicsItem) and item.rect().contains(scene_pos):
                    item.setSelected(True)
                    self._selected_annotation = item
                elif isinstance(item, LineAnnotationItem):
                    p1, p2 = item.line().p1(), item.line().p2()
                    dist = self.point_line_distance(scene_pos, p1, p2)
                    if dist < 5:  # tolerancia
                        item.setSelected(True)
                        self._selected_annotation = item
                elif isinstance(item, PolylineAnnotationItem):
                    # comprobar distancia al segmento más cercano
                    points = item.getPoints()
                    for i in range(len(points) - 1):
                        dist = self.point_line_distance(scene_pos, points[i], points[i+1])
                        if dist < 5:  # tolerancia
                            item.setSelected(True)
                            self._selected_annotation = item
                            break

                if self._selected_annotation:
                    # Sincronizar con la lista
                    for i in range(self.main_window.listWidget.count()):
                        list_item = self.main_window.listWidget.item(i)
                        if list_item.data(Qt.UserRole) == self._selected_annotation:
                            self.main_window.listWidget.setCurrentItem(list_item)
                            break
                    break
            event.accept()
            return

        # ------------------------------
        # CLICK IZQUIERDO → mover/redimensionar/crear
        # ------------------------------
        if event.button() == Qt.LeftButton:
            if event.modifiers() & Qt.ControlModifier:
                # Si hacemos Ctrl + Click izquierdo sobre un vértice de la polilínea seleccionada, lo borramos
                if (
                    isinstance(self._selected_annotation, PolylineAnnotationItem)
                    and self._selected_annotation.scene() is not None
                ):
                    points = self._selected_annotation.getPoints()
                    clicked_idx = None
                    tolerance = max(6, PolylineAnnotationItem.HANDLE_SIZE)

                    for i, p in enumerate(points):
                        if QLineF(scene_pos, p).length() <= tolerance:
                            clicked_idx = i
                            break

                    if clicked_idx is not None:
                        self.main_window.save_current_state()

                        if len(points) <= 2:
                            if self._selected_annotation in self.main_window.annotations:
                                self.main_window.annotations.remove(self._selected_annotation)
                            self.scene().removeItem(self._selected_annotation)
                            self._selected_annotation = None
                            self.main_window.update_annotation_list()
                        else:
                            new_points = points[:clicked_idx] + points[clicked_idx+1:]
                            self._selected_annotation.setPoints(new_points)
                            self._selected_annotation.normalizeOrder()
                            self.main_window.update_annotation_list()

                            # mantener sincronizada la selección en la lista
                            for i in range(self.main_window.listWidget.count()):
                                list_item = self.main_window.listWidget.item(i)
                                if list_item.data(Qt.UserRole) == self._selected_annotation:
                                    self.main_window.listWidget.setCurrentItem(list_item)
                                    break

                        event.accept()
                        return

                self._panning = True
                self._pan_start_pos = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
                event.accept()
                return

            elif self._selected_annotation:
                # Detectar si clic en un handle (box o line)
                for handle in self._selected_annotation.handles:
                    if handle and handle.scene() and handle.contains(handle.mapFromScene(scene_pos)):
                        self.main_window.save_current_state()
                        self._resizing = True
                        self._resize_handle_index = self._selected_annotation.handles.index(handle)
                        self._resize_handle = handle
                        if isinstance(self._selected_annotation, AnnotationGraphicsItem):
                            self._original_rect = self._selected_annotation.rect()
                        elif isinstance(self._selected_annotation, LineAnnotationItem):
                            self._original_line = self._selected_annotation.line()
                        elif isinstance(self._selected_annotation, PolylineAnnotationItem):
                            self._original_points = self._selected_annotation.getPoints().copy()
                        self._resize_start_pos = scene_pos
                        break
                if not self._resizing:
                    # Comenzar arrastre
                    self.main_window.save_current_state()
                    self._dragging = True
                    self._drag_start_pos = scene_pos
                    if isinstance(self._selected_annotation, AnnotationGraphicsItem):
                        self._original_rect = self._selected_annotation.rect()
                    elif isinstance(self._selected_annotation, LineAnnotationItem):
                        self._original_line = self._selected_annotation.line()
                    elif isinstance(self._selected_annotation, PolylineAnnotationItem):
                        self._original_points = self._selected_annotation.getPoints().copy()

            else:
                # Crear nueva anotación
                self.startPos = scene_pos
                color = self.main_window.class_colors.get(self.main_window.last_label, QColor("#FFFFFF"))
                ctype = self.main_window.class_types.get(self.main_window.last_label, "box")
                if ctype == "line":
                    self.currentRect = LineAnnotationItem(
                        QLineF(scene_pos, scene_pos),
                        label=self.main_window.last_label,
                        name=self.main_window.class_names.get(self.main_window.last_label, f"Clase {self.main_window.last_label}"),
                        color=color
                    )
                elif ctype == "polyline":
                    # Usamos scene_pos pero lo limitamos a la imagen si existe
                    def clamp_to_image(pt):
                        if self.image_item:
                            ir = self.image_item.sceneBoundingRect()
                            x = min(max(pt.x(), ir.left()), ir.right())
                            y = min(max(pt.y(), ir.top()), ir.bottom())
                            return QPointF(x, y)
                        return pt

                    if not self.creating_polyline:
                        start_point = clamp_to_image(scene_pos)
                        self.currentRect = PolylineAnnotationItem(
                            [start_point],
                            label=self.main_window.last_label,
                            name=self.main_window.class_names.get(
                                self.main_window.last_label,
                                f"Clase {self.main_window.last_label}"
                            ),
                            color=color
                        )
                        self.creating_polyline = True
                        self.scene().addItem(self.currentRect)
                    else:
                        # Añadir un nuevo punto fijo con clic izquierdo (clampeado)
                        if self.currentRect:
                            new_point = clamp_to_image(scene_pos)
                            pts = self.currentRect.getPoints()
                            # evitar añadir el mismo punto repetido
                            if not pts or pts[-1] != new_point:
                                self.currentRect.setPoints(pts + [new_point])
                            self.currentRect.clearPreview()

                else:
                    self.currentRect = AnnotationGraphicsItem(
                        QRectF(scene_pos, scene_pos),
                        label=self.main_window.last_label,
                        name=self.main_window.class_names.get(self.main_window.last_label, f"Clase {self.main_window.last_label}"),
                        color=color
                    )

                if ctype != "polyline":
                    self.scene().addItem(self.currentRect)
            event.accept()
            return

        super().mousePressEvent(event)

    def _relabel_item(self, item, new_label):
        """Asigna una nueva etiqueta a un item, si es compatible en tipo."""
        # Verificar compatibilidad de tipos
        new_type = self.main_window.class_types.get(new_label, "box")
        if isinstance(item, AnnotationGraphicsItem) and new_type != "box":
            return False
        if isinstance(item, LineAnnotationItem) and new_type != "line":
            return False
        if isinstance(item, PolylineAnnotationItem) and new_type != "polyline":
            return False

        # Aplicar cambios
        item.label = new_label
        item.name = self.main_window.class_names.get(new_label, f"Clase {new_label}")
        item.textItem.setPlainText(item.name)
        item.updateLabelPosition()
        return True

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.RightButton:
            scene_pos = self.mapToScene(event.pos())
            for item in self.scene().items():
                if (
                    isinstance(item, AnnotationGraphicsItem)
                    and getattr(item, "is_class_visible", True)  # 🔹 Solo si la clase está visible
                    and item.rect().contains(scene_pos)
                    and item.is_selected  # ✅ Solo si ya está seleccionada
                ):
                    # Llamar a la función de asignar etiqueta
                    self.main_window.assignLabelToSelected()
                    event.accept()
                    return
        super().mouseDoubleClickEvent(event)


    def mouseMoveEvent(self, event):
        if self._selected_annotation and self._selected_annotation.scene() is None:
            self._selected_annotation = None
        scene_pos = self.mapToScene(event.pos())

        # ------------------------------
        # PAN con Ctrl + arrastre
        # ------------------------------
        if self._panning:
            delta = (self.mapToScene(event.pos()) - self.mapToScene(self._pan_start_pos)) * 0.0002
            self._pan_start_pos = event.pos()
            self.translate(delta.x(), delta.y())
            event.accept()
            return

        # ------------------------------
        # REDIMENSIONAR anotación
        # ------------------------------
        if self._resizing and self._selected_annotation and self.image_item:
            if isinstance(self._selected_annotation, AnnotationGraphicsItem):
                image_rect = self.image_item.sceneBoundingRect()
                delta = scene_pos - self._resize_start_pos
                new_rect = QRectF(self._original_rect)

                handle_pos = self._resize_handle.pos()
                if handle_pos == self._original_rect.topLeft():
                    new_rect.setTopLeft((new_rect.topLeft() + delta))
                elif handle_pos == self._original_rect.topRight():
                    new_rect.setTopRight((new_rect.topRight() + delta))
                elif handle_pos == self._original_rect.bottomLeft():
                    new_rect.setBottomLeft((new_rect.bottomLeft() + delta))
                elif handle_pos == self._original_rect.bottomRight():
                    new_rect.setBottomRight((new_rect.bottomRight() + delta))

                # Asegurar tamaño mínimo
                min_size = 3
                if new_rect.width() < min_size:
                    if handle_pos.x() == self._original_rect.left():
                        new_rect.setLeft(new_rect.right() - min_size)
                    else:
                        new_rect.setRight(new_rect.left() + min_size)
                if new_rect.height() < min_size:
                    if handle_pos.y() == self._original_rect.top():
                        new_rect.setTop(new_rect.bottom() - min_size)
                    else:
                        new_rect.setBottom(new_rect.top() + min_size)

                # Aplicar
                new_rect = new_rect.intersected(image_rect)
                self._selected_annotation.setRect(new_rect)

            elif isinstance(self._selected_annotation, LineAnnotationItem):
                line = QLineF(self._original_line)
                delta = scene_pos - self._resize_start_pos
                if self._resize_handle_index == 0:
                    line.setP1(line.p1() + delta)
                elif self._resize_handle_index == 1:
                    line.setP2(line.p2() + delta)
                self._selected_annotation.setLine(line)
            
            elif isinstance(self._selected_annotation, PolylineAnnotationItem):
                points = self._original_points.copy()
                if 0 <= self._resize_handle_index < len(points):
                    p = scene_pos
                    image_rect = self.image_item.sceneBoundingRect()
                    x = min(max(p.x(), image_rect.left()), image_rect.right())
                    y = min(max(p.y(), image_rect.top()), image_rect.bottom())
                    points[self._resize_handle_index] = QPointF(x, y)
                    self._selected_annotation.setPoints(points)

            event.accept()
            return

        # ------------------------------
        # MOVER anotación seleccionada
        # ------------------------------
        if self._dragging and self._selected_annotation and self.image_item:
            image_rect = self.image_item.sceneBoundingRect()
            delta = scene_pos - self._drag_start_pos

            if isinstance(self._selected_annotation, AnnotationGraphicsItem):
                new_rect = self._original_rect.translated(delta.x(), delta.y())
                # Restringir dentro de la imagen
                if not image_rect.contains(new_rect):
                    if new_rect.left() < image_rect.left():
                        delta.setX(image_rect.left() - self._original_rect.left())
                    elif new_rect.right() > image_rect.right():
                        delta.setX(image_rect.right() - self._original_rect.right())
                    if new_rect.top() < image_rect.top():
                        delta.setY(image_rect.top() - self._original_rect.top())
                    elif new_rect.bottom() > image_rect.bottom():
                        delta.setY(image_rect.bottom() - self._original_rect.bottom())
                    new_rect = self._original_rect.translated(delta.x(), delta.y())
                self._selected_annotation.setRect(new_rect)

            elif isinstance(self._selected_annotation, LineAnnotationItem):
                new_line = QLineF(
                    self._original_line.p1() + delta,
                    self._original_line.p2() + delta
                )
                # Restringir dentro de la imagen
                if image_rect.contains(new_line.p1()) and image_rect.contains(new_line.p2()):
                    self._selected_annotation.setLine(new_line)
            elif isinstance(self._selected_annotation, PolylineAnnotationItem):
                # Delta propuesto por el ratón
                dx, dy = delta.x(), delta.y()

                # BBox actual de la polyline (con puntos originales al inicio del drag)
                min_x = min(p.x() for p in self._original_points)
                max_x = max(p.x() for p in self._original_points)
                min_y = min(p.y() for p in self._original_points)
                max_y = max(p.y() for p in self._original_points)

                # Rango de movimiento permitido por eje para no salirse
                dx_min = image_rect.left()  - min_x
                dx_max = image_rect.right() - max_x
                dy_min = image_rect.top()   - min_y
                dy_max = image_rect.bottom()- max_y

                # Clampear cada componente del delta al rango permitido
                dx = max(min(dx, dx_max), dx_min)
                dy = max(min(dy, dy_max), dy_min)

                # Aplicar el delta corregido (se “pega” al borde si choca en ese eje)
                new_points = [QPointF(p.x() + dx, p.y() + dy) for p in self._original_points]
                self._selected_annotation.setPoints(new_points)



            event.accept()
            return

        # ------------------------------
        # CREAR nueva anotación
        # ------------------------------
        if self.currentRect and self.startPos:
            if isinstance(self.currentRect, LineAnnotationItem):
                self.currentRect.setLine(QLineF(self.startPos, scene_pos))
            elif isinstance(self.currentRect, PolylineAnnotationItem):
                points = self.currentRect.getPoints()
                if len(points) >= 1:
                    # Mostrar un punto temporal durante el movimiento del ratón, clampeado
                    if self.image_item:
                        ir = self.image_item.sceneBoundingRect()
                        x = min(max(scene_pos.x(), ir.left()), ir.right())
                        y = min(max(scene_pos.y(), ir.top()), ir.bottom())
                        preview_point = QPointF(x, y)
                    else:
                        preview_point = scene_pos
                    self.currentRect.setPreviewPoint(preview_point)

            else:
                self.currentRect.setRect(QRectF(self.startPos, scene_pos).normalized())
            event.accept()
            return

        super().mouseMoveEvent(event)

    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # ------------------------------
            # Control de errores
            # ------------------------------
            if event.button() == Qt.LeftButton:
                # Si la imagen cambió, currentRect puede haber sido borrado
                if self.currentRect and self.currentRect.scene() is None:
                    self.currentRect = None
                    self.startPos = None
                    self.creating_polyline = False
                    return
            # ------------------------------
            # Finalizar PAN
            # ------------------------------
            if self._panning:
                self._panning = False
                self.setCursor(Qt.ArrowCursor)
                event.accept()
                return

            # ------------------------------
            # Finalizar REDIMENSIONAMIENTO
            # ------------------------------
            elif self._resizing:
                self._resizing = False
                if isinstance(self._selected_annotation, PolylineAnnotationItem):
                    self._selected_annotation.normalizeOrder()
                if hasattr(self, 'main_window'):
                    self.main_window.update_annotation_list()
                event.accept()
                return

            # ------------------------------
            # Finalizar ARRASTRE
            # ------------------------------
            elif self._dragging:
                self._dragging = False
                if hasattr(self, 'main_window'):
                    self.main_window.update_annotation_list()
                event.accept()
                return

            # ------------------------------
            # Finalizar CREACIÓN de nueva anotación
            # ------------------------------
            if self.currentRect and self.image_item and not isinstance(self.currentRect, PolylineAnnotationItem):
                image_rect = self.image_item.sceneBoundingRect()

                if isinstance(self.currentRect, LineAnnotationItem):
                    # Caso LINE
                    line = self.currentRect.line()
                    p1, p2 = line.p1(), line.p2()

                    # Recortar a los límites de la imagen
                    p1.setX(min(max(p1.x(), image_rect.left()), image_rect.right()))
                    p1.setY(min(max(p1.y(), image_rect.top()), image_rect.bottom()))
                    p2.setX(min(max(p2.x(), image_rect.left()), image_rect.right()))
                    p2.setY(min(max(p2.y(), image_rect.top()), image_rect.bottom()))

                    new_line = QLineF(p1, p2)
                    self.currentRect.setLine(new_line)

                    # Validar que la línea no sea demasiado corta
                    if new_line.length() >= 3:
                        if self.main_window.last_label:
                            self.currentRect.label = self.main_window.last_label
                            self.currentRect.updateLabelPosition()
                        self.main_window.addAnnotation(self.currentRect)
                    else:
                        self.scene().removeItem(self.currentRect)
                elif isinstance(self.currentRect, AnnotationGraphicsItem):
                    # Caso BOX
                    final_rect = self.currentRect.rect().intersected(image_rect)
                    if final_rect.width() >= 3 and final_rect.height() >= 3:
                        self.currentRect.setRect(final_rect)
                        if self.main_window.last_label:
                            self.currentRect.label = self.main_window.last_label
                            self.currentRect.updateLabelPosition()
                        self.main_window.addAnnotation(self.currentRect)
                    else:
                        self.scene().removeItem(self.currentRect)

                self.currentRect = None
                self.startPos = None
                event.accept()
                return


    def wheelEvent(self, event):
        modifiers = event.modifiers()
        if modifiers & Qt.ControlModifier or modifiers & Qt.ShiftModifier:
            angle = event.angleDelta().y()
            factor = 1.15 if angle > 0 else 0.85
            self.scale(factor, factor)
            event.accept()
        else:
            super().wheelEvent(event)

class ClassificationAnnotationItem(QGraphicsTextItem):
    def __init__(self, label="", name="", color=QColor(255, 0, 0), parent=None):
        super().__init__(name, parent)
        self.label = label
        self.name = name
        self.color = color
        self.is_selected = False
        self.isAnnotationItem = True
        self.handles = []
        self.is_class_visible = True
        self.textItem = self  # Para compatibilidad con otras funciones

        self._setup_appearance()

    def setClassVisible(self, visible: bool):
        self.is_class_visible = visible
        self.setVisible(visible)

    def _setup_appearance(self):
        self.setDefaultTextColor(self.color)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.setFont(font)

    def setNameVisible(self, visible: bool):
        pass

    def setSelected(self, selected):
        self.is_selected = selected
        
    def setSelectedNoAperance(self, selected):
        self.is_selected = selected

    def updateLabelPosition(self):
        pass

