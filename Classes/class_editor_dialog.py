from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QScrollArea, QWidget, 
    QHBoxLayout, QPushButton, QComboBox, QLineEdit,
    QDialogButtonBox, QColorDialog, QMessageBox
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from functools import partial

from Classes.translations import STRINGS

class ClassEditorDialog(QDialog):
    def __init__(self, class_data, parent=None):
        super().__init__(parent)
        
        self.lang = self.parent().current_lang if self.parent() else "en" # IDIOMA
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(STRINGS[self.lang].get("class_editor_title", "Class Editor"))
        self.original_data = class_data
        self.temp_data = class_data.copy()
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Scroll area para las clases
        self.scroll_area = QScrollArea()
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        
        # Crear widgets para cada clase
        self.class_widgets = []
        for class_id, (class_name, class_color, class_type) in self.temp_data.items():
            self._add_class_widget(class_id, class_name, class_color, class_type)
        
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)
        
        # Botón para añadir nueva clase
        self.btn_add = QPushButton(STRINGS[self.lang].get("new_class", "New Class"))
        self.btn_add.clicked.connect(self.add_new_class)
        self.layout.addWidget(self.btn_add)
        
        # Botones de guardar/cancelar
        self.btn_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)
        self.layout.addWidget(self.btn_box)
        
    def accept(self):
        # Detectar cambios
        changes = []

        old_ids = sorted(self.original_data.keys(), key=int)
        new_ids = sorted(self.temp_data.keys(), key=int)

        # Clases eliminadas
        deleted = [cid for cid in old_ids if cid not in self.temp_data]
        for cid in deleted:
            name = self.original_data[cid][0]
            changes.append(
                STRINGS[self.lang].get("change_deleted", "Deleted class") + f": [{cid}] {name}"
            )

        # Clases reordenadas
        for new_index, old_id in enumerate(new_ids):
            if str(new_index) != old_id:
                name = self.temp_data[old_id][0]
                changes.append(
                    STRINGS[self.lang].get("change_reordered", "Reordered class") + f": [{old_id}] → [{new_index}] ({name})"
                )

        # Cambios de nombre o color
        for cid in self.temp_data:
            if cid in self.original_data:
                old_name, old_color, _ = self.original_data[cid]
                new_name, new_color, _ = self.temp_data[cid]

                if old_name != new_name:
                    changes.append(
                        STRINGS[self.lang].get("change_name", "Renamed class") + f": [{cid}] '{old_name}' → '{new_name}'"
                    )
                if old_color.name() != new_color.name():
                    changes.append(
                        STRINGS[self.lang].get("change_color", "Color changed") + f": [{cid}] {old_color.name()} → {new_color.name()}"
                    )

        if not changes:
            super().accept()
            return

        # Crear mensaje de confirmación
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle(STRINGS[self.lang].get("confirm_changes_title", "Confirm changes"))
        msg.setText(STRINGS[self.lang].get("confirm_changes_text", "Are you sure you want to apply the following changes?"))
        msg.setWindowTitle("Confirmar cambios")
        msg.setText("¿Seguro que desea aplicar los siguientes cambios?")
        msg.setDetailedText("\n".join(changes))
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        if msg.exec_() == QMessageBox.Ok:
            super().accept()

    def _add_class_widget(self, class_id, class_name, class_color, class_type):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Botón para borrar clase
        btn_delete = QPushButton("X")
        btn_delete.setFixedWidth(30)
        btn_delete.clicked.connect(partial(self.delete_class, class_id))
        layout.addWidget(btn_delete)
        
        # Botón para cambiar color
        btn_color = QPushButton()
        btn_color.setFixedWidth(30)
        btn_color.setStyleSheet(f"background-color: {class_color.name()}")
        btn_color.clicked.connect(lambda: self.change_color(class_id))
        layout.addWidget(btn_color)
        
        # Selector de tipo
        type_combo = QComboBox()
        type_combo.addItems(["box", "line", "polyline"])
        type_combo.setCurrentText(class_type)
        type_combo.currentTextChanged.connect(
            lambda t: self.update_class_type(class_id, t)
        )
        layout.addWidget(type_combo)
        
        # Editor de nombre
        name_edit = QLineEdit(class_name)
        name_edit.textChanged.connect(
            lambda t: self.update_class_name(class_id, t)
        )
        layout.addWidget(name_edit)
        
        self.scroll_layout.addWidget(widget)
        self.class_widgets.append(widget)
    
    def add_new_class(self):
        # Encontrar el próximo ID disponible
        new_id = str(max(int(k) for k in self.temp_data.keys()) + 1) if self.temp_data else "0"
        self.temp_data[new_id] = (
            STRINGS[self.lang].get("default_class_name", "New Class"),
            QColor("#FFFFFF"),
            "box"
        )
        self._add_class_widget(new_id, *self.temp_data[new_id])
    
    def delete_class(self, class_id):
        if class_id in self.temp_data:
            del self.temp_data[class_id]
            # Actualizar la vista
            self._refresh_view()
    
    def change_color(self, class_id):
        color = QColorDialog.getColor(self.temp_data[class_id][1], self)
        if color.isValid():
            self.temp_data[class_id] = (
                self.temp_data[class_id][0], 
                color, 
                self.temp_data[class_id][2]
            )
            self._refresh_view()
    
    def update_class_name(self, class_id, new_name):
        if class_id in self.temp_data:
            self.temp_data[class_id] = (
                new_name, 
                self.temp_data[class_id][1], 
                self.temp_data[class_id][2]
            )
    
    def update_class_type(self, class_id, new_type):
        if class_id in self.temp_data:
            self.temp_data[class_id] = (
                self.temp_data[class_id][0], 
                self.temp_data[class_id][1], 
                new_type
            )
    
    def _refresh_view(self):
        # Limpiar y reconstruir la vista
        for widget in self.class_widgets:
            self.scroll_layout.removeWidget(widget)
            widget.deleteLater()
        self.class_widgets = []
        
        for class_id, (class_name, class_color, class_type) in self.temp_data.items():
            self._add_class_widget(class_id, class_name, class_color, class_type)