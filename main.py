import sys
import os
import yaml
import ctypes
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QGraphicsScene, QFileDialog, QGraphicsPixmapItem,
    QListWidget, QListWidgetItem, QInputDialog, QScrollArea,
    QMessageBox, QAction, QDialog, QLabel, QLineEdit,QTextBrowser,
    QDesktopWidget, QCheckBox, QProgressDialog 
)
from PyQt5.QtGui import QPixmap, QColor, QFont, QBrush
from PyQt5.QtCore import Qt, QRectF, QLocale, QThread, pyqtSignal, QLineF, QPointF, QTimer

#Clases:
from Classes.class_editor_dialog import ClassEditorDialog
from Classes.translations import STRINGS, LANGUAGES
from Classes.graphics_items import AnnotationGraphicsItem, AnnotationView, LineAnnotationItem, PolylineAnnotationItem
from Classes.view_editor_dialog import ViewEditorDialog

# Histograma
import matplotlib.pyplot as plt

###############################################################################
#                              Stylesheets                                    #
###############################################################################
DARK_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #2b2b2b;
    color: #e0e0e0;
}
QWidget {
    background-color: #2b2b2b;
    color: #e0e0e0;
}
QMenuBar {
    background-color: #323232;
    color: #e0e0e0;
    border-bottom: 1px solid #444;
}
QMenuBar::item:selected {
    background-color: #444;
}
QMenu {
    background-color: #323232;
    color: #e0e0e0;
    border: 1px solid #444;
}
QMenu::item:selected {
    background-color: #444;
}
QPushButton {
    background-color: #404040;
    color: #e0e0e0;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #505050;
    border: 1px solid #666;
}
QPushButton:pressed {
    background-color: #303030;
}
QListWidget, QScrollArea, QTextBrowser {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border: 1px solid #444;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #3d59a1;
}
QLineEdit {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 4px;
}
QLabel {
    color: #e0e0e0;
}
QCheckBox {
    color: #e0e0e0;
}
QComboBox {
    background-color: #404040;
    color: #e0e0e0;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 4px;
}
QComboBox QAbstractItemView {
    background-color: #1e1e1e;
    color: #e0e0e0;
    selection-background-color: #3d59a1;
}
QGraphicsView {
    background-color: #1e1e1e;
}
"""

LIGHT_STYLESHEET = ""

def set_window_title_bar_theme(window, dark):
    """Aplica el modo oscuro/claro a la barra de título de Windows."""
    if sys.platform != "win32":
        return
    try:
        hwnd = int(window.winId())
        value = ctypes.c_int(1 if dark else 0)
        # Atributo 20: DWMWA_USE_IMMERSIVE_DARK_MODE (Windows 11 y Win10 20H1+)
        # Atributo 19: Versiones anteriores de Windows 10
        res = ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
        if res != 0:
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(value), ctypes.sizeof(value))
    except Exception:
        pass

###############################################################################
#                              ImageViewer Class                              #
###############################################################################
class ImageViewer(QMainWindow):
    # Main window: loads images, manages bounding boxes, and supports multilingual UI.
    def __init__(self):
        super().__init__()

        # Sistema de deshacer/rehacer
        self.undo_stack = []  # Para deshacer acciones
        self.redo_stack = []  # Para rehacer acciones
        self.max_undo_steps = 5
        
        # Tema
        self.dark_mode_enabled = False

        # Crear la barra de menú principal
        self.menuBar = self.menuBar()

        # Filtro
        self.current_class_filter = "all"  # 'all' o lista de class_ids

        # Menú File
        self.fileMenu = self.menuBar.addMenu("&File")

        # Acción: Abrir imágenes
        self.openImagesAction = QAction("&Open Images", self)
        self.openImagesAction.triggered.connect(self.openFolder)
        self.fileMenu.addAction(self.openImagesAction)

        # Acción: Abrir modelo
        self.openModelAction = QAction("&Open Model", self)
        self.openModelAction.triggered.connect(self.openModel)
        self.fileMenu.addAction(self.openModelAction)

        # Acción: Filtros (antes era un botón en el panel izquierdo)
        self.filtersAction = QAction("Filters", self)
        self.filtersAction.triggered.connect(self.open_filter_dialog)
        self.fileMenu.addAction(self.filtersAction)

        # Menú Edit
        self.editMenu = self.menuBar.addMenu("&Edit")

        # Acción Deshacer
        self.undoAction = QAction("&Undo", self)
        self.undoAction.setShortcut("Ctrl+Z")
        self.undoAction.triggered.connect(self.undo_last_action)
        self.editMenu.addAction(self.undoAction)
        
        # Acción Rehacer
        self.redoAction = QAction("&Redo", self)
        self.redoAction.setShortcut("Ctrl+Shift+Z")
        self.redoAction.triggered.connect(self.redo_last_action)
        self.editMenu.addAction(self.redoAction)

        # Acción Copiar
        self.copied_annotation = None  # Para almacenar la anotación copiada

        # Menú View
        self.viewMenu = self.menuBar.addMenu("&View")

        # Acción Edit View (placeholder)
        self.editViewAction = QAction("&Edit View", self)
        self.editViewAction.triggered.connect(self.edit_view)
        self.viewMenu.addAction(self.editViewAction)

        # Acción: Cambiar Tema
        self.toggleThemeAction = QAction("Dark Mode", self)
        self.toggleThemeAction.triggered.connect(self.toggle_theme)
        self.viewMenu.addAction(self.toggleThemeAction)

        # Visibilidad de nombres por tipo
        self.name_visibility = {'box': True, 'line': True, 'polyline': True}

        # Menú de idiomas
        self.languageMenu = self.menuBar.addMenu("Languages")

        # Crear acciones de cambio de idioma dinámicamente desde STRINGS
        self.language_actions = {}
        for lang_code in STRINGS.keys():
            language_name = LANGUAGES.get(lang_code, lang_code.upper())  # Usa LANGUAGES si lo tienes definido
            action = QAction(language_name, self)
            action.triggered.connect(lambda checked, code=lang_code: self.set_language(code))
            self.languageMenu.addAction(action)
            self.language_actions[lang_code] = action

        # Menú Help
        self.helpMenu = self.menuBar.addMenu("&Help")  # El & permite acceso rápido con Alt+H

        # Acción para el manual del usuario
        self.userManualAction = QAction("&User Manual", self)
        self.userManualAction.triggered.connect(self.show_user_manual)
        self.helpMenu.addAction(self.userManualAction)
        
        # Acción para Acerca de
        self.aboutAction = QAction("&About...", self)
        self.aboutAction.triggered.connect(self.show_about_dialog)
        self.helpMenu.addAction(self.aboutAction)
        
        # 1. Inicialización de variables
        self.image_list = []
        self.dataYamnlDirectory = ""
        self.directory = ""
        self.labels_directory = ""
        self.class_types = {}  # dict[str -> "box" | "line"]
        self.class_colors = {}
        self.class_names = {}
        self.class_visibility = {}  # dict[class_id -> bool]
        self.current_index = 0
        self.annotations = []
        self.currentTxtFile = None
        self.current_lang = "en"
        self.color_palette = [
            QColor("#e6194b"), QColor("#3cb44b"), QColor("#ffe119"),
            QColor("#0082c8"), QColor("#f58231"), QColor("#911eb4"),
            QColor("#46f0f0"), QColor("#f032e6"), QColor("#d2f53c"),
            QColor("#fabebe")
        ]
        self.color_index = 0
        self.last_label = 0
        self.image_width = 1
        self.image_height = 1
        self.detection_model = None
        
        # 2. Configuración de la ventana principal
        self.setFocusPolicy(Qt.StrongFocus)
        self.setGeometry(100, 100, 1200, 600)
        
        # 3. Configuración de la escena gráfica
        self.scene = QGraphicsScene()
        
        # 4. Creación de widgets principales
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QHBoxLayout(self.centralWidget)
        
        # --------------------------------------------------
        # 5. Panel izquierdo (Lista de clases)
        # --------------------------------------------------
        self.leftPanel = QWidget()
        self.leftPanel.setMaximumWidth(250)
        self.leftPanelLayout = QVBoxLayout(self.leftPanel)
        
        # Panel de navegación
        self.navPanel = QWidget()
        self.navLayout = QVBoxLayout(self.navPanel)
        self.navLayout.setContentsMargins(5, 5, 5, 15)  # Márgenes más ajustados

        # Control de navegación
        self.navControl = QHBoxLayout()

        self.txtImageIndex = QLineEdit()
        self.txtImageIndex.setAlignment(Qt.AlignCenter)
        self.txtImageIndex.setMaximumWidth(50)
        self.txtImageIndex.returnPressed.connect(self.goToImage)
        self.navControl.addWidget(self.txtImageIndex)

        # Etiqueta con el máximo (no editable)
        self.lblMaxImages = QLabel()
        self.lblMaxImages.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.navControl.addWidget(self.lblMaxImages)

        self.navLayout.addLayout(self.navControl)

        # Nombre del archivo (debajo del control)
        self.lblFileName = QLabel()
        self.lblFileName.setAlignment(Qt.AlignCenter)
        self.lblFileName.setStyleSheet("font-size: 11px; color: #555;")
        self.lblFileName.setWordWrap(True)
        self.navLayout.addWidget(self.lblFileName)
        self.leftPanelLayout.addWidget(self.navPanel)

        # Botón para mostrar histograma de etiquetas
        self.btnShowHistogram = QPushButton()
        self.btnShowHistogram.clicked.connect(self.show_label_histogram)
        self.leftPanelLayout.addWidget(self.btnShowHistogram)

        # Lista de clases
        self.classesListWidget = QListWidget()
        self.classesListWidget.itemClicked.connect(self.on_class_selected)
        self.leftPanelLayout.addWidget(self.classesListWidget)


        # Botón Edit
        self.btnEditClasses = QPushButton()
        self.btnEditClasses.clicked.connect(self.edit_classes)
        self.leftPanelLayout.addWidget(self.btnEditClasses)
        
        # --------------------------------------------------
        # 6. Panel central (Imagen y controles principales)
        # --------------------------------------------------
        self.centerPanel = QWidget()
        self.centerLayout = QVBoxLayout(self.centerPanel)
        
        # Crear layout horizontal para los botones
        self.topButtonsLayout = QHBoxLayout()

        # Botón para usar el modelo (oculto por defecto)
        self.btnUseModel = QPushButton()
        self.btnUseModel.clicked.connect(self.useModel)  # Método que definirás luego si quieres
        self.btnUseModel.setVisible(False)  # Oculto al inicio
        self.topButtonsLayout.addWidget(self.btnUseModel)

        # Agregar el layout de botones al panel central
        self.centerLayout.addLayout(self.topButtonsLayout)

        
        # Vista de la imagen
        self.AnnotationView = AnnotationView(self.scene, self)
        self.centerLayout.addWidget(self.AnnotationView)
        
        # --------------------------------------------------
        # 7. Panel derecho (Lista de anotaciones)
        # --------------------------------------------------
        self.rightPanel = QWidget()
        self.rightPanel.setMaximumWidth(300)
        self.rightLayout = QVBoxLayout(self.rightPanel)
        
        # Botón Eliminar Imagen
        self.btnDeleteImage = QPushButton()
        self.btnDeleteImage.clicked.connect(self.deleteCurrentImage)
        self.rightLayout.addWidget(self.btnDeleteImage)

        # Lista de anotaciones
        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QListWidget.ExtendedSelection)
        self.listWidget.itemDoubleClicked.connect(self.assignLabelToSelected)
        self.rightLayout.addWidget(self.listWidget)
        # Conectar la selección de la lista
        self.listWidget.itemClicked.connect(self.on_list_item_selected)
        
        # Botón para copiar etiquetas de la imagen anterior
        self.btnCopyPrevLabels = QPushButton()
        self.btnCopyPrevLabels.clicked.connect(self.copy_annotations_from_previous)
        self.rightLayout.addWidget(self.btnCopyPrevLabels)

        # Botones de anotaciones
        self.btnAssignLabel = QPushButton()
        self.btnAssignLabel.clicked.connect(self.assignLabelToSelected)
        self.rightLayout.addWidget(self.btnAssignLabel)
        
        self.btnDeleteAnnotation = QPushButton()
        self.btnDeleteAnnotation.clicked.connect(self.deleteAnnotation)
        self.rightLayout.addWidget(self.btnDeleteAnnotation)
        
        # --------------------------------------------------
        # 8. Ensamblaje final
        # --------------------------------------------------
        self.mainLayout.addWidget(self.leftPanel, 1)    # 20% ancho
        self.mainLayout.addWidget(self.centerPanel, 4)  # 60% ancho (imagen)
        self.mainLayout.addWidget(self.rightPanel, 1)   # 20% ancho
        
        # 9. Configuración inicial
        self.set_language("en")
        self.show()
        QTimer.singleShot(0, self.openFolder)

    def show_user_manual(self):
        """Muestra una ventana con el manual del usuario traducido."""
        from Classes.translations import STRINGS

        # Obtener tamaño de pantalla
        screen_geometry = QDesktopWidget().availableGeometry(self)
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Tamaño proporcional
        dialog_width = int(screen_width * 0.6)
        dialog_height = int(screen_height * 0.7)

        dialog = QDialog(self)
        set_window_title_bar_theme(dialog, self.dark_mode_enabled)
        dialog.setWindowTitle(STRINGS[self.current_lang].get("manual_title", "User Manual"))
        dialog.resize(dialog_width, dialog_height)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        text_browser = QTextBrowser()
        html = STRINGS[self.current_lang].get("manual_content", "No manual content available.")
        text_browser.setHtml(html)
        font = QFont("Arial", max(10, int(screen_height * 0.015)))
        text_browser.setFont(font)
        layout.addWidget(text_browser)

        close_button = QPushButton("Close")
        close_button.setFixedWidth(100)
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.exec_()


    def show_about_dialog(self):
        """Muestra el diálogo Acerca de"""
        about_text = """
        <h2>Image Annotation Tool</h2>
        <p>Version 1.0</p>
        <p>Developed by [Your Name/Company]</p>
        <p>© 2023 All rights reserved</p>
        """
        
        msg = QMessageBox()
        set_window_title_bar_theme(msg, self.dark_mode_enabled)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("About")
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def edit_view(self):
        """
        Ventana de 'Editar vista': controla la visibilidad de nombres por tipo
        y la visibilidad por clase.
        """
        dlg = ViewEditorDialog(
            self,
            initial_states=self.name_visibility,
            class_names=self.class_names,
            class_visibility=self.class_visibility,
        )
        set_window_title_bar_theme(dlg, self.dark_mode_enabled)
        if dlg.exec_() == QDialog.Accepted:
            # 1) Nombres (Boxes / Lines / Polylines)
            self.name_visibility = dlg.get_states()
            self.apply_name_visibility_to_all()

            # 2) Clases visibles
            new_visibility = dlg.get_class_visibility()
            self.class_visibility.update(new_visibility)
            self.apply_class_visibility_to_all()

            # 3) Refrescar la lista de anotaciones para respetar la visibilidad de clases
            self.update_annotation_list()


    def apply_name_visibility_to_item(self, ann):
        """Aplica la visibilidad del nombre a un ítem según su tipo (box/line/polyline)."""
        try:
            if hasattr(ann, "rect"):              # BOX
                ann.setNameVisible(self.name_visibility.get('box', True))
            elif hasattr(ann, "line"):            # LINE
                ann.setNameVisible(self.name_visibility.get('line', True))
            elif hasattr(ann, "getPoints"):       # POLYLINE
                ann.setNameVisible(self.name_visibility.get('polyline', True))
        except Exception:
            pass

    def apply_name_visibility_to_all(self):
        for ann in self.annotations:
            self.apply_name_visibility_to_item(ann)
        # Forzar repintado
        self.scene.update()
        self.AnnotationView.viewport().update()

    def apply_class_visibility_to_all(self):
        """Aplica la visibilidad por clase a todas las anotaciones actuales."""
        for ann in self.annotations:
            if ann.label in self.class_visibility:
                ann.setClassVisible(self.class_visibility[ann.label])

    def on_list_item_selected(self, item):
        """Maneja la selección desde la lista de anotaciones"""
        # Deseleccionar todas las anotaciones gráficas primero
        for annotation in self.annotations:
            annotation.setSelected(False)
        
        # Obtener la anotación asociada al ítem de lista
        selected_annotation = item.data(Qt.UserRole)
        if selected_annotation:
            # Seleccionar la anotación gráfica correspondiente
            selected_annotation.setSelected(True)
            self.AnnotationView._selected_annotation = selected_annotation
            
            # Asegurarse que es visible en la vista
            view = self.AnnotationView
            view.centerOn(selected_annotation)
            view.ensureVisible(selected_annotation)

    
    def on_class_selected(self, item):
        """Maneja la selección de una clase de la lista izquierda"""
        class_id = item.data(Qt.UserRole)
        class_name = item.text()
        self.last_label = class_id  # Usamos el ID para consistencia con el sistema de anotaciones
        print(f"Clase seleccionada: {class_name} (ID: {class_id})")
    
    def toggle_theme(self):
        """Alterna entre modo claro y oscuro."""
        self.dark_mode_enabled = not self.dark_mode_enabled
        self.apply_theme()
        
        # Actualizar texto de la acción en el menú
        theme_key = "light_mode" if self.dark_mode_enabled else "dark_mode"
        self.toggleThemeAction.setText(STRINGS[self.current_lang].get(theme_key, "Dark Mode"))
        
        # Actualizar información de imagen para el color del nombre del archivo
        self.updateImageInfo()

    def apply_theme(self):
        """Aplica el stylesheet correspondiente al tema actual."""
        if self.dark_mode_enabled:
            QApplication.instance().setStyleSheet(DARK_STYLESHEET)
        else:
            QApplication.instance().setStyleSheet(LIGHT_STYLESHEET)
        
        # Aplicar a la barra de título (Windows)
        set_window_title_bar_theme(self, self.dark_mode_enabled)

    def set_language(self, lang):
        # Sets the UI language; falls back to English if the language is not supported.
        if lang not in STRINGS:
            lang = "en"
        self.current_lang = lang
        self.setWindowTitle(STRINGS[lang]["window_title"])
        self.btnUseModel.setText(STRINGS[lang]["use_model_button"])
        self.btnEditClasses.setText(STRINGS[lang]["edit_classes"])
        self.btnAssignLabel.setText(STRINGS[lang]["assign_label"])
        self.btnDeleteAnnotation.setText(STRINGS[lang]["delete_annotation"])
        self.btnDeleteImage.setText(STRINGS[lang].get("delete_image"))
        self.btnCopyPrevLabels.setText(STRINGS[lang]["copy_prev_labels"])
        # Barra de menu
        # Menu archivo:
        self.fileMenu.setTitle(STRINGS[lang].get("menu_file", "&File"))
        self.openImagesAction.setText(STRINGS[lang]["open_images"])
        self.openModelAction.setText(STRINGS[lang]["open_model"])
        self.filtersAction.setText(STRINGS[lang].get("filter_button", "Filters"))

        self.helpMenu.setTitle(STRINGS[lang]["menu_help"])
        self.userManualAction.setText(STRINGS[lang]["menu_user_manual"])
        self.aboutAction.setText(STRINGS[lang]["menu_about"])
        self.languageMenu.setTitle(STRINGS[lang].get("menu_languages", "Languages"))
        self.editMenu.setTitle(STRINGS[lang].get("menu_edit", "&Edit"))
        self.undoAction.setText(STRINGS[lang].get("menu_undo", "&Undo"))
        self.viewMenu.setTitle(STRINGS[lang].get("menu_view", "&View"))
        self.editViewAction.setText(STRINGS[lang].get("menu_edit_view", "&Edit View"))

        # Panel de navegación
        self.btnShowHistogram.setText(STRINGS[lang].get("show_histogram", "Histograma de etiquetas"))

        # Cambiar texto del modo oscuro/claro
        theme_key = "light_mode" if self.dark_mode_enabled else "dark_mode"
        self.toggleThemeAction.setText(STRINGS[lang].get(theme_key, "Dark Mode"))

        self.updateImageInfo()  # Actualiza el texto con el nuevo idioma


    def get_class_id_by_name(self, class_name):
        for class_id, name in self.class_names.items():
            if name == class_name:
                return class_id
        return None  # o "-1" si prefieres un valor por defecto
        
    def get_next_color(self) -> QColor:
        # Returns the next color in the palette, cycling through 10 colors.
        color = self.color_palette[self.color_index]
        self.color_index = (self.color_index + 1) % len(self.color_palette)
        return color
    
    def save_class_colors(self, folder):
        yaml_file = os.path.join(folder, "class_colors.yaml")
        data = {
            'version': '1.0',
            "colors": {cid: color.name() for cid, color in self.class_colors.items()},
            "names":  self.class_names,
            "types":  self.class_types,
        }
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)
            
    def load_class_colors(self, folder):
        yaml_file = os.path.join(folder, "class_colors.yaml")
        if not os.path.exists(yaml_file):
            return False
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        # nombres
        self.class_names = {str(k): v for k, v in (data.get("names") or {}).items()}
        # colores
        self.class_colors = {str(k): QColor(v) for k, v in (data.get("colors") or {}).items()}
        # tipos (fallback a "box" si no existe en archivos viejos)
        raw_types = data.get("types") or {}
        self.class_types = {cid: (raw_types.get(cid, "box")) for cid in self.class_names.keys()}
        return True
    
    def is_color_dark(self, qcolor):
        """Devuelve True si el color es oscuro, basado en luminancia perceptual"""
        r = qcolor.red()
        g = qcolor.green()
        b = qcolor.blue()
        # Fórmula estándar de luminancia (perceptual brightness)
        brightness = 0.299 * r + 0.587 * g + 0.114 * b
        return brightness < 128


    def update_classes_list(self):
        """Actualiza la lista de clases en el panel izquierdo con colores"""
        self.class_visibility = {cid: True for cid in self.class_names.keys()}
        self.classesListWidget.clear()
        # Ordenar las clases por ID
        sorted_classes = sorted(self.class_names.items(), key=lambda x: int(x[0]))
        for class_id, class_name in sorted_classes:
            item = QListWidgetItem(f"[{class_id}] {class_name}")
            item.setData(Qt.UserRole, class_id)  # Guardamos el ID como dato adicional
            # Establecer color de fondo según la clase
            color = self.class_colors.get(class_id, QColor("#FFFFFF"))
            item.setBackground(QBrush(color))
            # Determinar si usar texto blanco o negro según el color de fondo
            if self.is_color_dark(color):
                item.setForeground(QBrush(Qt.white))
            else:
                item.setForeground(QBrush(Qt.black))
            self.classesListWidget.addItem(item)


    def edit_classes(self):
        """Abre el diálogo avanzado de edición de clases"""
        # Preparar los datos para el diálogo
        class_data = {
            class_id: (name, self.class_colors.get(class_id, QColor("#FFFFFF")), self.class_types.get(class_id, "box"))
            for class_id, name in self.class_names.items()
        }
        
        dialog = ClassEditorDialog(class_data, self)
        set_window_title_bar_theme(dialog, self.dark_mode_enabled)

        if dialog.exec_() == QDialog.Accepted:
            old_class_ids = sorted(self.class_names.keys(), key=int)
            new_class_ids = sorted(dialog.temp_data.keys(), key=int)

            deleted_ids = [cid for cid in old_class_ids if cid not in new_class_ids]
            id_mapping = {old_id: str(new_index) for new_index, old_id in enumerate(new_class_ids)}
            self.id_mapping = id_mapping  # Guardar para uso posterior

            reordering_changed = any(id_mapping.get(cid, cid) != cid for cid in old_class_ids if cid in id_mapping)
            
            if deleted_ids or reordering_changed:
                # REMAPEAR datos (clases eliminadas o IDs reorganizados)
                self.id_mapping = id_mapping  # guardar para uso posterior

                # Mostrar barra de progreso
                self.progress_dialog = QProgressDialog(
                    STRINGS[self.current_lang].get("procesing_data", "Processing data..."),
                    STRINGS[self.current_lang].get("cancel", "Cancel"),
                    0, 100, self
                )
                set_window_title_bar_theme(self.progress_dialog, self.dark_mode_enabled)
                self.progress_dialog.setWindowTitle(STRINGS[self.current_lang].get("please_wait", "Please wait..."))
                self.progress_dialog.setWindowFlags(self.progress_dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                self.progress_dialog.setWindowModality(Qt.WindowModal)
                self.progress_dialog.setMinimumWidth(300)
                self.progress_dialog.setAutoClose(True)
                self.progress_dialog.show()

                # Lanzar hilo
                self.class_remap_thread = ClassRemapWorker(
                    self.labels_directory,
                    deleted_ids,
                    id_mapping,
                    dialog.temp_data
                )
                self.class_remap_thread.progress.connect(self.progress_dialog.setValue)
                self.class_remap_thread.finished.connect(self._on_remap_complete)
                self.class_remap_thread.error.connect(lambda msg: QMessageBox.critical(self, "Error", msg))
                self.progress_dialog.canceled.connect(self.class_remap_thread.cancel)
                self.class_remap_thread.start()

            else:
                # SOLO actualizar nombres o colores
                self.class_names =  {cid: data[0] for cid, data in dialog.temp_data.items()}
                self.class_colors = {cid: data[1] for cid, data in dialog.temp_data.items()}
                self.class_types  = {cid: data[2] for cid, data in dialog.temp_data.items()}  # <--- AÑADIR

                self.update_classes_list()
                self.save_class_colors(os.path.dirname(self.dataYamnlDirectory))
                self.save_data_yaml()
                self.loadCurrentImage()
                QMessageBox.information(
                    self,
                    STRINGS[self.current_lang].get("remap_success_title", "Success"),
                    STRINGS[self.current_lang].get("remap_success_msg", "Classes were successfully saved.")
                )

    def _remap_all_annotations(self, deleted_ids, id_mapping):
        """Actualiza todos los archivos .txt eliminando clases y reordenando IDs."""
        import os

        for filename in os.listdir(self.labels_directory):
            if not filename.endswith('.txt'):
                continue

            path = os.path.join(self.labels_directory, filename)
            new_lines = []

            with open(path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if not parts or parts[0] in deleted_ids:
                        continue
                    new_id = id_mapping.get(parts[0])
                    if new_id is not None:
                        new_lines.append(' '.join([new_id] + parts[1:]))

            with open(path, 'w') as f:
                f.write('\n'.join(new_lines) + '\n')

    def _on_remap_complete(self, new_class_names):
        self.class_names = new_class_names
        self.class_colors = {
            new_id: self.class_remap_thread.temp_data[old_id][1]
            for old_id, new_id in self.id_mapping.items()
        }
        self.class_types = {                                           # <--- AÑADIR
            new_id: self.class_remap_thread.temp_data[old_id][2]
            for old_id, new_id in self.id_mapping.items()
        }
        self.update_classes_list()
        self.save_class_colors(os.path.dirname(self.dataYamnlDirectory))
        self.save_data_yaml()
        self.loadCurrentImage()
        QMessageBox.information(
            self,
            STRINGS[self.current_lang].get("remap_success_title", "Success"),
            STRINGS[self.current_lang].get("remap_success_msg", "Classes were successfully saved.")
        )


    def _invert_dict(self, d):
        return {v: k for k, v in d.items()}

    def save_data_yaml(self):

        yaml_path = os.path.join(self.dataYamnlDirectory, "data.yaml")

        if not os.path.exists(yaml_path):
            return

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Actualizar número de clases y nombres
        data["nc"] = len(self.class_names)
        data["names"] = [self.class_names[str(i)] for i in range(len(self.class_names))]

        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)

    #Panel de navegacion:
    def updateImageInfo(self):
        """Actualiza la información de la imagen en el panel izquierdo"""
        if not self.image_list:
            self.txtImageIndex.clear()
            self.lblMaxImages.clear()
            self.lblFileName.setText(STRINGS[self.current_lang].get("no_images", "No hay imágenes"))
            return
        
        # Actualizar el índice actual
        self.txtImageIndex.setText(str(self.current_index + 1))
        
        # Actualizar el máximo
        self.lblMaxImages.setText(f"/{len(self.image_list)}")
        
        # Actualizar nombre de archivo (mostrar solo el nombre base)
        filename = os.path.basename(self.image_list[self.current_index])

        # Obtener ancho actual del QLabel (en píxeles)
        label_width = self.lblFileName.width()
        if label_width == 0:
            label_width = 200  # Valor por defecto si aún no se ha renderizado

        # Estimar cuántos caracteres caben por línea (aproximadamente 7 píxeles por carácter)
        avg_char_width = 6
        max_chars = max(10, int(label_width / avg_char_width))

        # Forzar salto de línea si el nombre es muy largo
        if len(filename) > max_chars:
            wrapped = '\n'.join([filename[i:i+max_chars] for i in range(0, len(filename), max_chars)])
            self.lblFileName.setText(wrapped)
        else:
            self.lblFileName.setText(filename)
        
        # Color según el tema
        if self.dark_mode_enabled:
            self.lblFileName.setStyleSheet("font-size: 11px; color: #aaa;")
        else:
            self.lblFileName.setStyleSheet("font-size: 11px; color: #555;")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateImageInfo()

    def goToImage(self):
        """Navega a la imagen especificada en el campo de texto"""
        if not self.image_list:
            return
        
        try:
            new_index = int(self.txtImageIndex.text()) - 1
            if 0 <= new_index < len(self.image_list):
                self.current_index = new_index
                self.loadCurrentImage()
            else:
                QMessageBox.warning(
                    self,
                    STRINGS[self.current_lang].get("invalid_number_title", "Error"),
                    STRINGS[self.current_lang].get("invalid_number_msg", "Número de imagen inválido")
                )
                self.updateImageInfo()
        except ValueError:
            QMessageBox.warning(
                self,
                STRINGS[self.current_lang].get("invalid_input_title", "Error"),
                STRINGS[self.current_lang].get("invalid_input_msg", "Ingrese un número válido")
            )
            self.updateImageInfo()


    # Filtro
    def open_filter_dialog(self):
        """Abre un diálogo para seleccionar clases y filtrar imágenes con mejor UI"""
        dialog = QDialog(self)
        set_window_title_bar_theme(dialog, self.dark_mode_enabled)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setWindowTitle(STRINGS[self.current_lang]["filter_title"])
        dialog.setMinimumWidth(400)  # Más ancho

        main_layout = QVBoxLayout(dialog)

        # Checkbox "Todas"
        all_checkbox = QCheckBox(STRINGS[self.current_lang]["filter_all"])
        all_checkbox.setChecked(self.current_class_filter == "all")
        main_layout.addWidget(all_checkbox)

        # Scroll area con checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        checkbox_container = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_container)
        checkbox_layout.setContentsMargins(5, 5, 5, 5)
        checkbox_layout.setSpacing(4)

        # Checkboxes de clases
        checkboxes = {}
        for class_id, class_name in sorted(self.class_names.items(), key=lambda x: int(x[0])):
            cb = QCheckBox(f"[{class_id}] {class_name}")
            if isinstance(self.current_class_filter, list):
                cb.setChecked(class_id in self.current_class_filter)
            else:
                cb.setChecked(False)
            cb.setEnabled(not all_checkbox.isChecked())
            checkbox_layout.addWidget(cb)
            checkboxes[class_id] = cb

        scroll_area.setWidget(checkbox_container)
        main_layout.addWidget(scroll_area, stretch=1)

        # Función para desactivar/activar checkboxes
        def toggle_all(state):
            enabled = not (state == Qt.Checked)
            for cb in checkboxes.values():
                cb.setEnabled(enabled)
                if enabled:
                    cb.setChecked(False)

        all_checkbox.stateChanged.connect(toggle_all)

        # Botones Aceptar/Cancelar
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton(STRINGS[self.current_lang]["accept"])
        btn_cancel = QPushButton(STRINGS[self.current_lang]["cancel"])
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        main_layout.addLayout(btn_layout)

        btn_ok.clicked.connect(lambda: self.apply_filters(dialog, all_checkbox, checkboxes))
        btn_cancel.clicked.connect(dialog.reject)

        dialog.resize(450, 500)  # Ajuste general de tamaño
        dialog.exec_()



    def apply_filters(self, dialog, all_checkbox, checkboxes):
        """Aplica el filtro de clases seleccionadas"""
        previous_filter = self.current_class_filter
        previous_image_list = self.image_list.copy()

        self.load_image_index()  # Carga completa desde disco

        if all_checkbox.isChecked():
            if not self.image_list:
                QMessageBox.warning(self, STRINGS[self.current_lang]["filter_title"], STRINGS[self.current_lang]["filter_warning_no_images"])
                self.image_list = previous_image_list
                self.current_class_filter = previous_filter
                dialog.reject()
                return

            self.current_class_filter = "all"

        else:
            selected_classes = [cid for cid, cb in checkboxes.items() if cb.isChecked()]
            if not selected_classes:
                QMessageBox.warning(self, STRINGS[self.current_lang]["filter_title"], STRINGS[self.current_lang]["filter_warning_no_selection"])
                self.image_list = previous_image_list
                self.current_class_filter = previous_filter
                return

            # Buscar imágenes que contengan alguna de esas clases
            filtered = []
            for img_path in self.image_list:
                base = os.path.splitext(os.path.basename(img_path))[0]
                txt_path = os.path.join(self.labels_directory, f"{base}.txt")
                if not os.path.exists(txt_path):
                    continue
                with open(txt_path, "r") as f:
                    for line in f:
                        class_id = line.strip().split()[0]
                        if class_id in selected_classes:
                            filtered.append(img_path)
                            break

            if not filtered:
                QMessageBox.warning(self, STRINGS[self.current_lang]["filter_title"], STRINGS[self.current_lang]["filter_warning_no_results"])
                # Restaurar estado anterior
                self.image_list = previous_image_list
                self.current_class_filter = previous_filter
                dialog.reject()
                return

            self.image_list = filtered
            self.current_class_filter = selected_classes

        self.current_index = 0
        self.loadCurrentImage()
        dialog.accept()


    # Histograma
    def show_label_histogram(self):
        """Lanza el hilo para generar el histograma sin bloquear la interfaz."""
        if not self.labels_directory or not os.path.exists(self.labels_directory):
            QMessageBox.warning(
                self,
                STRINGS[self.current_lang].get("error", "Error"),
                STRINGS[self.current_lang].get("no_labels_dir", "No se encontró el directorio de etiquetas.")
            )
            return

        # Crear barra de progreso
        self.progress_dialog = QProgressDialog(
            STRINGS[self.current_lang].get("procesing_data", "Processing data..."),
            STRINGS[self.current_lang].get("cancel", "Cancelar"),  # Texto del botón cancelar
            0, 100, self
        )
        self.progress_dialog.setWindowTitle(STRINGS[self.current_lang].get("please_wait", "Espere..."))
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumWidth(300)
        self.progress_dialog.setWindowFlags(self.progress_dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.show()

        # Crear y lanzar el hilo
        self.histogram_thread = HistogramWorker(self.labels_directory)
        self.histogram_thread.progress.connect(self.progress_dialog.setValue)
        self.histogram_thread.finished.connect(self.plot_histogram_from_counts)

        # Conectar el botón de cancelar
        self.progress_dialog.canceled.connect(self.histogram_thread.cancel)

        self.histogram_thread.start()


    def plot_histogram_from_counts(self, counts_dict):
        if not counts_dict:
            QMessageBox.information(
                self,
                STRINGS[self.current_lang].get("histogram_title", "Histograma"),
                STRINGS[self.current_lang].get("histogram_no_data", "No se encontraron anotaciones.")
            )
            return

        # Asegurar que todas las clases estén representadas, incluso con 0 ocurrencias
        all_counts = {
            class_id: counts_dict.get(class_id, 0)
            for class_id in sorted(self.class_names.keys(), key=int)
        }

        labels = [self.class_names[cid] for cid in all_counts.keys()]
        counts = list(all_counts.values())

        plt.figure(figsize=(10, 5))
        bars = plt.bar(labels, counts, color='skyblue')
        plt.xlabel(STRINGS[self.current_lang].get("classes", "Clases"))
        plt.ylabel(STRINGS[self.current_lang].get("annotation_count", "Cantidad de etiquetas"))
        plt.title(STRINGS[self.current_lang].get("histogram_title", "Distribución de etiquetas por clase"))
        plt.xticks(rotation=45, ha='right')

        for bar, count in zip(bars, counts):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height + 1, str(count),
                    ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        plt.show()



    # Modelo:
    def openModel(self):
        """Abre un modelo YOLO (.pt) usando un diálogo de selección de archivo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select YOLO Model",
            "",
            "YOLO Model (*.pt);;All Files (*)"
        )
        
        if file_path:
            try:
                # Carga diferida para no forzar torch/ultralytics en el arranque.
                from ultralytics import YOLO
                self.detection_model = YOLO(file_path)
                QMessageBox.information(self, "Modelo cargado", f"Modelo YOLO cargado:\n{file_path}")
                self.btnUseModel.setVisible(True)  # Mostrar el botón
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cargar el modelo:\n{str(e)}")
                self.btnUseModel.setVisible(False)  # Asegurarse que no se muestre si hay error

    def useModel(self):
        """Ejecuta el modelo YOLO sobre la imagen actual y muestra los resultados"""
        if not hasattr(self, 'detection_model') or not self.detection_model:
            QMessageBox.warning(self, "Error", "No hay modelo cargado")
            return
        
        if not self.image_list or self.current_index >= len(self.image_list):
            QMessageBox.warning(self, "Error", "No hay imagen cargada")
            return
        
        try:
            # Obtener la ruta de la imagen actual
            current_image_path = self.image_list[self.current_index]
            
            # Ejecutar la detección
            results = self.detection_model(current_image_path)
            
            self.save_current_state() # Ctrl + Z
            # Limpiar anotaciones existentes
            self.annotations.clear()
            self.scene.clear()  # Cambiado de scene() a scene
            
            # Cargar la imagen de nuevo
            pixmap = QPixmap(current_image_path)
            if pixmap.isNull():
                return
            self.image_width = pixmap.width()
            self.image_height = pixmap.height()
            item = QGraphicsPixmapItem(pixmap)
            item.setZValue(0)
            self.scene.addItem(item)  # Cambiado de scene() a scene
            self.AnnotationView.image_item = item
            self.AnnotationView.fitInView(item, Qt.KeepAspectRatio)
            
            # Procesar los resultados
            for result in results:
                for box in result.boxes:
                    # Obtener coordenadas normalizadas YOLO
                    x_center, y_center, width, height = box.xywhn[0].tolist()
                    
                    # Convertir a coordenadas absolutas
                    abs_x = x_center * self.image_width
                    abs_y = y_center * self.image_height
                    abs_w = width * self.image_width
                    abs_h = height * self.image_height
                    
                    # Convertir a formato QRectF (x, y, w, h)
                    x = abs_x - abs_w / 2
                    y = abs_y - abs_h / 2
                    rect = QRectF(x, y, abs_w, abs_h)
                    
                    # Obtener clase y confianza
                    class_id = int(box.cls)
                    confidence = float(box.conf)
                    
                    # Obtener color y nombre de la clase
                    class_id_str = str(class_id)
                    color = self.class_colors.get(class_id_str, QColor("#FF0000"))
                    class_name = self.class_names.get(class_id_str, f"Class {class_id}")
                    
                    # Crear anotación
                    annotation = AnnotationGraphicsItem(
                        rect,
                        label=class_id_str,
                        color=color
                    )
                    self.apply_name_visibility_to_item(annotation)
                    self.scene.addItem(annotation)  # Cambiado de scene() a scene
                    self.annotations.append(annotation)
                    
                    # Añadir texto con confianza
                    annotation.textItem.setPlainText(f"{class_name} {confidence:.2f}")
                    annotation.updateLabelPosition()
            
            # Actualizar lista de anotaciones
            self.update_annotation_list()
            
            # Actualizar archivo de anotaciones
            self.updateAnnotationsFile()
            
            #QMessageBox.information(self, "Detección completada", f"Se encontraron {len(self.annotations)} objetos")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al ejecutar el modelo:\n{str(e)}")

    def load_image_index(self):
        """Recarga el índice de imágenes desde el disco"""
        if not self.directory:
            return
        self.image_list = [os.path.join(self.directory, img)
                        for img in sorted(os.listdir(self.directory))
                        if img.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]



    def openFolder(self):
        open_title = STRINGS[self.current_lang].get("open_folder", "Seleccionar carpeta")
        folder = QFileDialog.getExistingDirectory(self, open_title, "")
    
        if folder:
            data_file = os.path.join(folder, "data.yaml")
    
            if not os.path.exists(data_file):
                print("Error: No se encontró 'data.yaml' en la carpeta seleccionada.")
                return

            # Leer el archivo YAML
            with open(data_file, "r") as file:
                data = yaml.safe_load(file)
                print(data_file)
            self.dataYamnlDirectory = data_file
            # Verificar que 'train' está en el YAML
            if "train" in data:
                # Si la ruta en el YAML es relativa, la ajustamos correctamente
                print(folder)
                print( data["train"])
                train_folder = os.path.normpath(os.path.join(folder, data["train"].replace("../", "")))
                # Obtener la ruta de las labels (asumiendo que están en /dataset/labels)
                labels_folder = os.path.normpath(os.path.join(
                    os.path.dirname(train_folder),  # Sube un nivel desde train_folder (/dataset/images -> /dataset)
                    "labels"  # Nombre de la carpeta de labels
                ))
                if not os.path.exists(train_folder):
                    print(f"Error: La carpeta de entrenamiento {train_folder} no existe.")
                    return
                self.directory = train_folder
                # Obtener el nombre de la carpeta
                self.dataset_name = os.path.basename(folder)
                self.setWindowTitle(self.dataset_name)
                self.labels_directory = labels_folder


                
                # Cargar información de clases desde data.yaml
                self.class_info = {
                    'names': data.get('names', []),
                    'nc': data.get('nc', 0)
                }
                # Intentar cargar colores existentes
                if not self.load_class_colors(folder):
                    # Generar nuevos colores si no existen
                    self.class_colors = {}
                    self.class_names = {}
                    self.class_types = {}
                    
                    for i in range(self.class_info['nc']):
                        class_id = str(i)
                        hue = (i * 360) / max(1, self.class_info['nc'])
                        color = QColor()
                        color.setHslF(hue/360, 1.0, 0.5)
                        self.class_colors[class_id] = color
                        self.class_names[class_id] = self.class_info['names'][i] if i < len(self.class_info['names']) else f"Clase {i}"
                        self.class_types[class_id] = "box"     # <--- AÑADIR
                        print(self.class_colors)
                        print(self.class_names)
                        print(self.class_types)
                    
                    # Guardar los nuevos colores
                    self.save_class_colors(folder)

                # ACTUALIZACIÓN: Cargar las clases en la lista izquierda
                self.update_classes_list()
            
                # Obtener imágenes en la carpeta de entrenamiento
                self.load_image_index()
    
                if not self.image_list:
                    print("No se encontraron imágenes en la carpeta de entrenamiento.")
                    return
    
                self.current_index = 0
                self.loadCurrentImage()
            else:
                print("Error: No se encontró la clave 'train' en data.yaml.")

    def deleteCurrentImage(self):
        """Elimina la imagen actual y su archivo de anotaciones asociado"""
        if not self.image_list or self.current_index >= len(self.image_list):
            return

        # Preguntar confirmación
        """
        confirm = QMessageBox.question(
            self,
            STRINGS[self.current_lang]["confirm_delete_title"],
            STRINGS[self.current_lang]["confirm_delete_msg"],
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.No:
            return
        """
        try:
            # Eliminar archivo de imagen
            image_path = self.image_list[self.current_index]
            os.remove(image_path)
            
            # Eliminar archivo de anotaciones si existe
            base = os.path.splitext(os.path.basename(image_path))[0]
            txt_file = os.path.join(self.labels_directory, f"{base}.txt")
            if os.path.exists(txt_file):
                os.remove(txt_file)
            
            # Actualizar la lista de imágenes
            self.image_list.pop(self.current_index)
            
            # Ajustar el índice si es necesario
            if self.current_index >= len(self.image_list):
                self.current_index = max(0, len(self.image_list) - 1)
            
            # Cargar la nueva imagen actual
            if self.image_list:
                self.loadCurrentImage()
            else:
                # Si no hay más imágenes, limpiar la escena
                self.scene.clear()
                self.listWidget.clear()
                self.annotations = []
                self.setWindowTitle(STRINGS[self.current_lang]["window_title"])
                
            #QMessageBox.information(self, "Éxito", "Imagen eliminada correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar la imagen:\n{str(e)}") 
    
    def loadCurrentImage(self):
        # Loads the current image and its corresponding TXT annotations.
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
        self.AnnotationView.image_item = item  # Establece la referencia al ítem de imagen
        self.AnnotationView.fitInView(item, Qt.KeepAspectRatio)
        self.AnnotationView.unselectAnnotationNoAperance()
        self.AnnotationView._selected_annotation = None
        self.AnnotationView.currentRect = None
        self.AnnotationView.startPos = None
        self.AnnotationView.creating_polyline = False
        self.annotations = []
        self.listWidget.clear()
        base = os.path.splitext(os.path.basename(filename))[0]
        self.currentTxtFile = os.path.join(self.labels_directory, f"{base}.txt")
        self.loadAnnotations(self.currentTxtFile)
        self.apply_name_visibility_to_all()
        self.updateImageInfo()  # Panel de navegacion

    def keyPressEvent(self, event):
        # Handles navigation between images using arrow keys or space.
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
        # Deshacer con Ctrl+Z
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            if not event.modifiers() & Qt.ShiftModifier:
                self.undo_last_action()
                return
        
        # Rehacer con Ctrl+Shift+Z
        elif event.key() == Qt.Key_Z and event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier):
            self.redo_last_action()
            return
        
        # usar Modelo con Ctrl+M
        elif event.key() == Qt.Key_M and event.modifiers() & Qt.ControlModifier:
            self.useModel()
            return

        # Borrar con Spr
        elif event.key() == Qt.Key_Delete:  # Detecta solo la tecla Suprimir
            self.deleteAnnotation()
            return
        
        # Copiar con ctrl+C
        elif event.key() == Qt.Key_C and event.modifiers() & Qt.ControlModifier:
            # Accedemos a la anotación seleccionada a través de AnnotationView
            if hasattr(self.AnnotationView, '_selected_annotation') and self.AnnotationView._selected_annotation:
                self.copy_selected_annotation()
                event.accept()
                return
            else:
                print(STRINGS[self.current_lang].get("nothing_to_copy", "No hay anotación seleccionada para copiar"))
                return
        # Pegar con Ctrl+V
        elif event.key() == Qt.Key_V and event.modifiers() & Qt.ControlModifier:
            if hasattr(self, 'copied_annotation'):
                self.paste_annotation()
                event.accept()
                return
            else:
                print(STRINGS[self.current_lang].get("nothing_to_paste", "No hay anotación copiada para pegar"))
                return
        # Borrar imagen con Ctrl+Ç
        elif event.key() == Qt.Key_P and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
            self.deleteCurrentImage()
            return

        else:
            super().keyPressEvent(event)

    def save_current_state(self):
        """Guarda el estado actual de anotaciones"""
        print("GUARDADO ESTADO")
        # Cuando guardamos un nuevo estado, limpiamos el redo stack
        self.redo_stack = []
        
        if len(self.undo_stack) >= self.max_undo_steps:
            self.undo_stack.pop(0)
        
        # Guardamos solo la información necesaria para reconstruir
        state = {
            'image_path': self.image_list[self.current_index] if self.image_list and self.current_index < len(self.image_list) else None,
            'annotations': [],
            'current_index': self.current_index
        }
        
        for ann in self.annotations:
            if hasattr(ann, "rect"):  # BOX
                coords = [
                    ann.rect().x(),
                    ann.rect().y(),
                    ann.rect().width(),
                    ann.rect().height()
                ]
                ann_type = "box"
            elif hasattr(ann, "line"):  # LINE
                line = ann.line()
                coords = [line.x1(), line.y1(), line.x2(), line.y2()]
                ann_type = "line"
            elif hasattr(ann, "getPoints"):  # POLYLINE 
                points = ann.getPoints()
                coords = [(p.x(), p.y()) for p in points]
                ann_type = "polyline"
            else:
                continue

            state['annotations'].append({
                'type': ann_type,
                'coordinates': coords,
                'label': ann.label,
                'color': ann.color.name(),
                'text': ann.textItem.toPlainText()
            })
        self.undo_stack.append(state)


    def undo_last_action(self):
        """Reverte al estado anterior si hay acciones en el stack"""
        if not self.undo_stack or len(self.undo_stack) == 0:
            return
        print(f"undo_stack len: {len(self.undo_stack)}")
        self.AnnotationView.unselectAnnotation()
        # Guardamos el estado actual en el redo stack
        current_state = {
            'image_path': self.image_list[self.current_index] if self.image_list and self.current_index < len(self.image_list) else None,
            'annotations': [],
            'current_index': self.current_index
        }

        for ann in self.annotations:
            if hasattr(ann, "rect"):  # BOX
                coords = [
                    ann.rect().x(),
                    ann.rect().y(),
                    ann.rect().width(),
                    ann.rect().height()
                ]
                ann_type = "box"
            elif hasattr(ann, "line"):  # LINE
                line = ann.line()
                coords = [line.x1(), line.y1(), line.x2(), line.y2()]
                ann_type = "line"
            elif hasattr(ann, "getPoints"):  # POLYLINE
                coords = [(p.x(), p.y()) for p in ann.getPoints()]
                ann_type = "polyline"
            else:
                continue

            current_state['annotations'].append({
                'type': ann_type,
                'coordinates': coords,
                'label': ann.label,
                'color': ann.color.name(),
                'text': ann.textItem.toPlainText()
            })

        self.redo_stack.append(current_state)
        
        # Obtenemos el último estado guardado
        state = self.undo_stack.pop()
        
        # Verificamos si es el mismo índice de imagen
        if state['current_index'] != self.current_index:
            QMessageBox.warning(self, "Warning", "Cannot undo across different images")
            return
        
        # Limpiamos el estado actual
        self.scene.clear()
        self.listWidget.clear()
        self.annotations = []
        
        # Recargamos la imagen base
        if state['image_path']:
            pixmap = QPixmap(state['image_path'])
            if not pixmap.isNull():
                item = QGraphicsPixmapItem(pixmap)
                item.setZValue(0)
                self.scene.addItem(item)
                self.AnnotationView.image_item = item
                self.AnnotationView.fitInView(item, Qt.KeepAspectRatio)
                self.image_width = pixmap.width()
                self.image_height = pixmap.height()
        
        # Recreamos las anotaciones
        for ann_data in state['annotations']:
            if ann_data['type'] == "box":
                rect = QRectF(
                    ann_data['coordinates'][0],
                    ann_data['coordinates'][1],
                    ann_data['coordinates'][2],
                    ann_data['coordinates'][3]
                )
                annotation = AnnotationGraphicsItem(
                    rect,
                    label=ann_data['label'],
                    color=QColor(ann_data['color'])
                )
            elif ann_data['type'] == "line":
                coords = ann_data['coordinates']
                line = QLineF(QPointF(coords[0], coords[1]), QPointF(coords[2], coords[3]))
                annotation = LineAnnotationItem(
                    line,
                    label=ann_data['label'],
                    color=QColor(ann_data['color'])
                )
            elif ann_data['type'] == "polyline":
                points = [QPointF(x, y) for x, y in ann_data['coordinates']]
                annotation = PolylineAnnotationItem(
                    points,
                    label=ann_data['label'],
                    name=self.class_names.get(ann_data['label'], f"Clase {ann_data['label']}"),
                    color=QColor(ann_data['color'])
                )
            else:
                continue

            annotation.textItem.setPlainText(ann_data['text'])
            self.scene.addItem(annotation)
            self.annotations.append(annotation)

            # aplicar visibilidad persistente de la clase
            is_visible = self.class_visibility.get(annotation.label, True)
            annotation.setClassVisible(is_visible)
            self.apply_name_visibility_to_item(annotation)

            # reconstruir ítem de la lista derecha SOLO si la clase está visible
            if is_visible:
                if ann_data['type'] == "box":
                    cx = rect.x() + rect.width()/2
                    cy = rect.y() + rect.height()/2
                    label = self.class_names.get(annotation.label, STRINGS[self.current_lang]["rect_no_label"])
                    item_text = f"{label} (X: {cx:.2f}, Y: {cy:.2f}, W: {rect.width():.2f}, H: {rect.height():.2f})"
                elif ann_data['type'] == "line":
                    line = annotation.line()
                    label = self.class_names.get(annotation.label, STRINGS[self.current_lang]["rect_no_label"])
                    item_text = f"{label} ({line.x1():.2f},{line.y1():.2f}), ({line.x2():.2f},{line.y2():.2f})"
                elif ann_data['type'] == "polyline":
                    label = self.class_names.get(annotation.label, STRINGS[self.current_lang]["rect_no_label"])
                    item_text = f"{label} ({len(annotation.getPoints())} pts)"

                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, annotation)
                item.setBackground(QBrush(annotation.color))
                item.setForeground(QBrush(Qt.black))
                self.listWidget.addItem(item)
        
        # Actualizamos el archivo de anotaciones
        self.updateAnnotationsFile()

    def redo_last_action(self):
        """Rehace la última acción deshecha"""
        if not self.redo_stack:
            return
        
        self.AnnotationView.unselectAnnotation()
        # Guardamos el estado actual en el undo stack
        current_state = {
            'image_path': self.image_list[self.current_index] if self.image_list and self.current_index < len(self.image_list) else None,
            'annotations': [],
            'current_index': self.current_index
        }

        for ann in self.annotations:
            if hasattr(ann, "rect"):  # BOX
                coords = [
                    ann.rect().x(),
                    ann.rect().y(),
                    ann.rect().width(),
                    ann.rect().height()
                ]
                ann_type = "box"
            elif hasattr(ann, "line"):  # LINE
                line = ann.line()
                coords = [line.x1(), line.y1(), line.x2(), line.y2()]
                ann_type = "line"
            elif hasattr(ann, "getPoints"):  # POLYLINE
                coords = [(p.x(), p.y()) for p in ann.getPoints()]
                ann_type = "polyline"
            else:
                continue

            current_state['annotations'].append({
                'type': ann_type,
                'coordinates': coords,
                'label': ann.label,
                'color': ann.color.name(),
                'text': ann.textItem.toPlainText()
            })
        self.undo_stack.append(current_state)
        
        # Obtenemos el estado a rehacer
        state = self.redo_stack.pop()
        
        # Limpiamos el estado actual
        self.scene.clear()
        self.listWidget.clear()
        self.annotations = []
        
        # Recargamos la imagen base
        if state['image_path']:
            pixmap = QPixmap(state['image_path'])
            if not pixmap.isNull():
                item = QGraphicsPixmapItem(pixmap)
                item.setZValue(0)
                self.scene.addItem(item)
                self.AnnotationView.image_item = item
                self.image_width = pixmap.width()
                self.image_height = pixmap.height()
        
        # Recreamos las anotaciones
        for ann_data in state['annotations']:
            if ann_data['type'] == "box":
                rect = QRectF(
                    ann_data['coordinates'][0],
                    ann_data['coordinates'][1],
                    ann_data['coordinates'][2],
                    ann_data['coordinates'][3]
                )
                annotation = AnnotationGraphicsItem(
                    rect,
                    label=ann_data['label'],
                    color=QColor(ann_data['color'])
                )
            elif ann_data['type'] == "line":
                coords = ann_data['coordinates']
                line = QLineF(QPointF(coords[0], coords[1]), QPointF(coords[2], coords[3]))
                annotation = LineAnnotationItem(
                    line,
                    label=ann_data['label'],
                    color=QColor(ann_data['color'])
                )
            elif ann_data['type'] == "polyline":
                points = [QPointF(x, y) for x, y in ann_data['coordinates']]
                annotation = PolylineAnnotationItem(
                    points,
                    label=ann_data['label'],
                    name=self.class_names.get(ann_data['label'], f"Clase {ann_data['label']}"),
                    color=QColor(ann_data['color'])
                )
            else:
                continue

            annotation.textItem.setPlainText(ann_data['text'])
            self.scene.addItem(annotation)
            self.annotations.append(annotation)

            # aplicar visibilidad persistente de la clase
            is_visible = self.class_visibility.get(annotation.label, True)
            annotation.setClassVisible(is_visible)
            self.apply_name_visibility_to_item(annotation)

            # reconstruir ítem de la lista derecha SOLO si la clase está visible
            if is_visible:
                if ann_data['type'] == "box":
                    cx = rect.x() + rect.width()/2
                    cy = rect.y() + rect.height()/2
                    label = self.class_names.get(annotation.label, STRINGS[self.current_lang]["rect_no_label"])
                    item_text = f"{label} (X: {cx:.2f}, Y: {cy:.2f}, W: {rect.width():.2f}, H: {rect.height():.2f})"
                elif ann_data['type'] == "line":
                    line = annotation.line()
                    label = self.class_names.get(annotation.label, STRINGS[self.current_lang]["rect_no_label"])
                    item_text = f"{label} ({line.x1():.2f},{line.y1():.2f}), ({line.x2():.2f},{line.y2():.2f})"
                elif ann_data['type'] == "polyline":
                    label = self.class_names.get(annotation.label, STRINGS[self.current_lang]["rect_no_label"])
                    item_text = f"{label} ({len(annotation.getPoints())} pts)"

                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, annotation)
                item.setBackground(QBrush(annotation.color))
                item.setForeground(QBrush(Qt.black))
                self.listWidget.addItem(item)
        
        # Actualizamos el archivo de anotaciones
        self.updateAnnotationsFile()
        
    def addAnnotation(self, annotation):
        self.save_current_state()
        self.apply_name_visibility_to_item(annotation)

        if not annotation.label and self.last_label:
            annotation.label = self.last_label

        self.annotations.append(annotation)
        no_label_str = STRINGS[self.current_lang]["rect_no_label"]
        label = self.class_names.get(annotation.label, no_label_str)
        label_show = label if label else no_label_str

        if hasattr(annotation, "rect"):  # 📦 Caso BOX
            r = annotation.rect()
            cx = r.x() + r.width() / 2
            cy = r.y() + r.height() / 2
            text = f"{label_show} (X: {cx:.2f}, Y: {cy:.2f}, W: {r.width():.2f}, H: {r.height():.2f})"

        elif hasattr(annotation, "line"):  # 📏 Caso LINE
            line = annotation.line()
            cx = (line.x1() + line.x2()) / 2
            cy = (line.y1() + line.y2()) / 2
            text = f"{label_show} ({line.x1():.2f},{line.y1():.2f}), ({line.x2():.2f},{line.y2():.2f})"

        elif hasattr(annotation, "getPoints"):  # 🔗 Caso POLYLINE
            pts = annotation.getPoints()
            text = f"{label_show} ({len(pts)} pts)"

        else:
            text = f"{label_show} (?)"

        # Solo mostramos en la lista si la clase está visible
        if self.class_visibility.get(annotation.label, True):
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, annotation)
            item.setBackground(QBrush(annotation.color))
            item.setForeground(QBrush(Qt.black))
            self.listWidget.addItem(item)


        self.updateAnnotationsFile()

        if annotation.label:
            self.last_label = annotation.label


    def update_annotation_list(self):
        """Actualiza la lista de anotaciones respetando la visibilidad por clase"""
        self.listWidget.clear()
        for ann in self.annotations:
            # Si la clase está marcada como no visible, no la mostramos en la lista
            if not self.class_visibility.get(ann.label, True):
                continue

            no_label_str = STRINGS[self.current_lang]["rect_no_label"]
            label = self.class_names.get(ann.label, no_label_str)

            if hasattr(ann, "rect"):  # 📦 Caso BOX
                r = ann.rect()
                cx = r.x() + r.width()/2
                cy = r.y() + r.height()/2
                text = f"{label} (X: {cx:.2f}, Y: {cy:.2f}, W: {r.width():.2f}, H: {r.height():.2f})"

            elif hasattr(ann, "line"):  # 📏 Caso LINE
                line = ann.line()
                cx = (line.x1() + line.x2()) / 2
                cy = (line.y1() + line.y2()) / 2
                length = line.length()
                text = f"{label} ({line.x1():.2f},{line.y1():.2f}), ({line.x2():.2f},{line.y2():.2f})"

            elif hasattr(ann, "getPoints"):  # 🔗 Caso POLYLINE
                pts = ann.getPoints()
                text = f"{label} ({len(pts)} pts)"

            else:
                text = f"{label} (?)"

            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, ann)
            item.setBackground(QBrush(ann.color))
            item.setForeground(QBrush(Qt.black))
            self.listWidget.addItem(item)

        self.updateAnnotationsFile()

        
    def updateAnnotationsFile(self):
        # Writes all annotations to a TXT file using normalized coordinates.
        if self.currentTxtFile:
            with open(self.currentTxtFile, "w") as f:
                for ann in self.annotations:
                    class_id = ann.label if ann.label else "0"

                    if hasattr(ann, "rect"):  # 📦 Caso BOX
                        r = ann.rect()
                        # Convertir a YOLO format (x_center, y_center, w, h)
                        x_center = (r.x() + r.width() / 2) / self.image_width
                        y_center = (r.y() + r.height() / 2) / self.image_height
                        w = r.width() / self.image_width
                        h = r.height() / self.image_height
                        line = f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n"

                    elif hasattr(ann, "line"):  # 📏 Caso LINE
                        line_obj = ann.line()
                        # Coordenadas normalizadas
                        x1 = line_obj.x1() / self.image_width
                        y1 = line_obj.y1() / self.image_height
                        x2 = line_obj.x2() / self.image_width
                        y2 = line_obj.y2() / self.image_height
                        line = f"{class_id} ({x1:.6f},{y1:.6f}, ({x2:.6f},{y2:.6f})\n"

                    elif hasattr(ann, "getPoints"):  # 📐 Caso POLYLINE
                        pts = ann.getPoints()
                        coords = " ".join(f"{p.x()/self.image_width:.6f} {p.y()/self.image_height:.6f}" for p in pts)
                        line = f"{class_id} {coords}\n"

                    else:
                        continue  # ignorar si no tiene ni rect ni line

                    f.write(line)


    def loadAnnotations(self, txt_file):
        """Carga las anotaciones desde un archivo TXT (box o line)."""
        if not os.path.exists(txt_file):
            return

        with open(txt_file, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 5:
                    continue  # línea malformada

                class_id = parts[0]
                color = self.class_colors.get(class_id, QColor("#FF0000"))
                class_type = self.class_types.get(class_id, "box")

                if class_type == "box":
                    # Espera: id, x_center, y_center, w, h
                    if len(parts) != 5:
                        continue
                    x_center = float(parts[1]) * self.image_width
                    y_center = float(parts[2]) * self.image_height
                    w = float(parts[3]) * self.image_width
                    h = float(parts[4]) * self.image_height

                    x = x_center - w / 2
                    y = y_center - h / 2
                    rect = QRectF(x, y, w, h)

                    ann = AnnotationGraphicsItem(
                        rect,
                        label=class_id,
                        name=self.class_names.get(class_id, f"Class {class_id}"),
                        color=color
                    )
                    self.apply_name_visibility_to_item(ann)

                elif class_type == "line":
                    # Espera: id, x1, y1, x2, y2
                    if len(parts) != 5:
                        continue
                    x1 = float(parts[1]) * self.image_width
                    y1 = float(parts[2]) * self.image_height
                    x2 = float(parts[3]) * self.image_width
                    y2 = float(parts[4]) * self.image_height

                    qline = QLineF(QPointF(x1, y1), QPointF(x2, y2))

                    ann = LineAnnotationItem(
                        qline,
                        label=class_id,
                        name=self.class_names.get(class_id, f"Class {class_id}"),
                        color=color
                    )
                    self.apply_name_visibility_to_item(ann)

                elif class_type == "polyline":
                    coords = list(map(float, parts[1:]))
                    if len(coords) % 2 != 0:
                        continue
                    points = [QPointF(coords[i]*self.image_width, coords[i+1]*self.image_height) for i in range(0, len(coords), 2)]
                    ann = PolylineAnnotationItem(
                        points,
                        label=class_id,
                        name=self.class_names.get(class_id, f"Class {class_id}"),
                        color=color
                    )
                    self.apply_name_visibility_to_item(ann)
                    
                else:
                    continue  # clase desconocida

                self.scene.addItem(ann)
                self.annotations.append(ann)

                # 🔽 AQUI aplicar visibilidad persistente
                if hasattr(self, "class_visibility"):  # asegúrate de que exista
                    if ann.label in self.class_visibility:
                        ann.setClassVisible(self.class_visibility[ann.label])
                        
                # Añadir a la lista derecha
                if self.class_visibility.get(class_id, True):
                    if class_type == "box":
                        cx = rect.x() + rect.width() / 2
                        cy = rect.y() + rect.height() / 2
                        item_text = f"{self.class_names.get(class_id, 'NoLabel')} (X: {cx:.2f}, Y: {cy:.2f}, W: {rect.width():.2f}, H: {rect.height():.2f})"

                    elif class_type == "line":
                        item_text = f"{self.class_names.get(class_id, 'NoLabel')} ({x1:.2f},{y1:.2f}), ({x2:.2f},{y2:.2f})"

                    elif class_type == "polyline":
                        item_text = f"{self.class_names.get(class_id, 'NoLabel')} ({len(points)} pts)"
                    
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, ann)
                    item.setBackground(QBrush(color))
                    item.setForeground(QBrush(Qt.black))
                    self.listWidget.addItem(item)

    def copy_annotations_from_previous(self):
        """Reemplaza todas las anotaciones de la imagen actual con las de la imagen anterior."""
        import os

        # Validaciones
        if not self.image_list or self.current_index is None or self.current_index <= 0:
            return  # No hay imagen anterior

        # Rutas de prev y actual
        prev_img_path = self.image_list[self.current_index - 1]
        prev_base = os.path.splitext(os.path.basename(prev_img_path))[0]
        prev_txt = os.path.join(self.labels_directory, f"{prev_base}.txt")

        # currentTxtFile ya se fija en loadCurrentImage, si no lo calculamos
        if self.currentTxtFile:
            curr_txt = self.currentTxtFile
        else:
            curr_img_path = self.image_list[self.current_index]
            curr_base = os.path.splitext(os.path.basename(curr_img_path))[0]
            curr_txt = os.path.join(self.labels_directory, f"{curr_base}.txt")
            self.currentTxtFile = curr_txt

        # Si no existe archivo previo, no hay nada que copiar
        if not os.path.exists(prev_txt):
            return

        # Leer todas las anotaciones de la imagen anterior
        with open(prev_txt, "r", encoding="utf-8") as f:
            prev_lines = [ln.strip() for ln in f if ln.strip()]

        if not prev_lines:
            return  # Imagen anterior no tenía etiquetas

        # Guardar estado para undo
        self.save_current_state()

        # Sobrescribir el archivo actual con las etiquetas del anterior
        with open(curr_txt, "w", encoding="utf-8") as f:
            for ln in prev_lines:
                f.write(ln + "\n")

        # Recargar la vista para reflejar los cambios
        self.loadCurrentImage()



    def assignLabelToSelected(self):
        self.save_current_state()
        # Assigns a new label to all selected annotations.
        selected_items = self.listWidget.selectedItems()
        if not selected_items:
            return
        new_label, ok = QInputDialog.getText(
            self,
            STRINGS[self.current_lang]["dialog_edit_label"],
            STRINGS[self.current_lang]["dialog_new_label"]
        )
        if ok:
            for item in selected_items:
                annotation = item.data(Qt.UserRole)
                annotation.label = new_label
                annotation.textItem.setPlainText(new_label)
                annotation.updateLabelPosition()
            self.updateAnnotationsFile()
            self.loadCurrentImage()

    def deleteAnnotation(self):
        self.save_current_state()
        # Deletes selected annotations from the scene and list.
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
        self.AnnotationView.unselectAnnotation()

    # Copiar y pegar:
    def copy_selected_annotation(self):
        """Copia la anotación seleccionada al portapapeles interno"""
        ann = getattr(self.AnnotationView, '_selected_annotation', None)
        if not ann:
            print(STRINGS[self.current_lang].get("nothing_to_copy", "No hay anotación seleccionada para copiar"))
            return

        # Copiar según tipo
        if hasattr(ann, "rect"):  # 📦 BOX
            data = {
                'type': 'box',
                'rect': ann.rect(),
                'label': ann.label,
                'color': ann.color,
                'name': ann.name
            }

        elif hasattr(ann, "line"):  # 📏 LINE
            data = {
                'type': 'line',
                'line': ann.line(),
                'label': ann.label,
                'color': ann.color,
                'name': ann.name
            }

        elif hasattr(ann, "getPoints"):  # 🔗 POLYLINE
            data = {
                'type': 'polyline',
                'points': ann.getPoints().copy(),
                'label': ann.label,
                'color': ann.color,
                'name': ann.name
            }

        else:
            print("Tipo de anotación desconocido, no se puede copiar.")
            return

        self.copied_annotation = data
        print(STRINGS[self.current_lang].get("copy_success", "Anotación copiada"))


    def paste_annotation(self):
        """Pega una anotación copiada previamente"""
        if not getattr(self, 'copied_annotation', None):
            print(STRINGS[self.current_lang].get("nothing_to_paste", "No hay anotación copiada para pegar"))
            return

        self.save_current_state()

        data = self.copied_annotation
        new_annotation = None
        offset = 0  # pequeño desplazamiento

        if data['type'] == 'box':
            r = data['rect']
            new_rect = QRectF(r.x() + offset, r.y() + offset, r.width(), r.height())
            new_annotation = AnnotationGraphicsItem(
                new_rect,
                label=data['label'],
                name=data['name'],
                color=data['color']
            )

        elif data['type'] == 'line':
            l = data['line']
            new_line = QLineF(
                QPointF(l.x1() + offset, l.y1() + offset),
                QPointF(l.x2() + offset, l.y2() + offset)
            )
            new_annotation = LineAnnotationItem(
                new_line,
                label=data['label'],
                name=data['name'],
                color=data['color']
            )

        elif data['type'] == 'polyline':
            pts = [QPointF(p.x() + offset, p.y() + offset) for p in data['points']]
            new_annotation = PolylineAnnotationItem(
                pts,
                label=data['label'],
                name=data['name'],
                color=data['color']
            )

        if not new_annotation:
            print("Error: tipo de anotación no soportado para pegar.")
            return

        self.apply_name_visibility_to_item(new_annotation)
        self.scene.addItem(new_annotation)
        self.annotations.append(new_annotation)
        self.update_annotation_list()
        self.updateAnnotationsFile()

        # Seleccionar la nueva anotación
        self.AnnotationView._selected_annotation = new_annotation
        new_annotation.setSelected(True)

        # Buscar y seleccionar en la lista
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if item.data(Qt.UserRole) == new_annotation:
                self.listWidget.setCurrentItem(item)
                break

        print(STRINGS[self.current_lang].get("paste_success", "Anotación pegada"))



###############################################################################
#                                 Workers                                     #
###############################################################################
class HistogramWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)

    def __init__(self, labels_dir):
        super().__init__()
        self.labels_dir = labels_dir
        self._should_cancel = False  # Nueva bandera

    def run(self):
        from collections import Counter
        import os

        label_counts = Counter()
        txt_files = [f for f in os.listdir(self.labels_dir) if f.endswith('.txt')]
        total_files = len(txt_files)

        for i, filename in enumerate(txt_files):
            if self._should_cancel:
                return  # Terminamos el hilo silenciosamente si se cancela

            path = os.path.join(self.labels_dir, filename)
            with open(path, 'r') as f:
                for line in f:
                    if line.strip():
                        class_id = line.strip().split()[0]
                        label_counts[class_id] += 1

            self.progress.emit(int((i + 1) / total_files * 100))

        self.finished.emit(dict(label_counts))

    def cancel(self):
        self._should_cancel = True

class ClassRemapWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)  # new_class_names
    error = pyqtSignal(str)

    def __init__(self, labels_dir, deleted_ids, id_mapping, temp_data):
        super().__init__()
        self.labels_dir = labels_dir
        self.deleted_ids = deleted_ids
        self.id_mapping = id_mapping
        self.temp_data = temp_data
        self._cancel = False

    def run(self):
        try:
            txt_files = [f for f in os.listdir(self.labels_dir) if f.endswith('.txt')]
            total = len(txt_files)

            for i, filename in enumerate(txt_files):
                if self._cancel:
                    return

                path = os.path.join(self.labels_dir, filename)
                new_lines = []

                with open(path, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if not parts or parts[0] in self.deleted_ids:
                            continue
                        new_id = self.id_mapping.get(parts[0])
                        if new_id is not None:
                            new_lines.append(' '.join([new_id] + parts[1:]))

                with open(path, 'w') as f:
                    f.write('\n'.join(new_lines) + '\n')

                self.progress.emit(int((i + 1) / total * 100))

            # Reconstruir class_names con nuevos IDs
            new_class_names = {
                str(new_index): self.temp_data[old_id][0]
                for old_id, new_index in self.id_mapping.items()
            }
            self.finished.emit(new_class_names)

        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self._cancel = True

###############################################################################
#                                   Main                                      #
###############################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    # Auto-detect system language using QLocale
    sys_lang = QLocale.system().name().split('_')[0]
    if sys_lang not in STRINGS:
        sys_lang = "en"
    viewer.set_language(sys_lang)
    viewer.show()
    sys.exit(app.exec_())
