# Classes/view_editor_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QDialogButtonBox, QWidget, QHBoxLayout, QScrollArea

from PyQt5.QtCore import Qt
from Classes.translations import STRINGS

class ViewEditorDialog(QDialog):
    def __init__(self, parent=None, initial_states=None, class_names=None, class_visibility=None):
        super().__init__(parent)
        self.lang = self.parent().current_lang if self.parent() else "en"
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(STRINGS[self.lang].get("view_editor_title", "Edit View"))

        # Estados iniciales {'box': bool, 'line': bool, 'polyline': bool}
        self.states = initial_states or {'box': True, 'line': True, 'polyline': True}

        # Info de clases
        self.class_names = class_names or {}
        self.class_visibility = class_visibility or {
            cid: True for cid in self.class_names.keys()
        }

        layout = QVBoxLayout(self)

        # ---- Bloque: Mostrar nombres
        names_title = QLabel(STRINGS[self.lang].get("view_editor_show_names_block", "Show label names:"))
        layout.addWidget(names_title)

        # Contenedor para los checkboxes (como un bloque)
        names_container = QWidget()
        names_layout = QVBoxLayout(names_container)
        # Un poco de margen a la izquierda para que visualmente quede como un bloque
        names_layout.setContentsMargins(15, 0, 0, 0)

        # Checkbox Boxes
        self.chk_boxes = QCheckBox(STRINGS[self.lang].get("view_editor_boxes", "Boxes"))
        self.chk_boxes.setChecked(self.states.get('box', True))
        names_layout.addWidget(self.chk_boxes)

        # Checkbox Lines
        self.chk_lines = QCheckBox(STRINGS[self.lang].get("view_editor_lines", "Lines"))
        self.chk_lines.setChecked(self.states.get('line', True))
        names_layout.addWidget(self.chk_lines)

        # Checkbox Polylines
        self.chk_polys = QCheckBox(STRINGS[self.lang].get("view_editor_polylines", "Polylines"))
        self.chk_polys.setChecked(self.states.get('polyline', True))
        names_layout.addWidget(self.chk_polys)

        layout.addWidget(names_container)

        # ---- Bloque: Clases visibles
        layout.addWidget(QLabel(STRINGS[self.lang].get("view_editor_visible_classes", "Visible classes")))

        self.class_checkboxes = {}

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        vbox_classes = QVBoxLayout(container)

        # Creamos un checkbox por clase
        for class_id, class_name in sorted(self.class_names.items(), key=lambda x: int(x[0])):
            cb = QCheckBox(f"[{class_id}] {class_name}")
            cb.setChecked(self.class_visibility.get(class_id, True))
            vbox_classes.addWidget(cb)
            self.class_checkboxes[class_id] = cb

        container.setLayout(vbox_classes)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        # Botonera Save/Cancel
        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_states(self):
        return {
            'box': self.chk_boxes.isChecked(),
            'line': self.chk_lines.isChecked(),
            'polyline': self.chk_polys.isChecked()
        }
    
    def get_class_visibility(self):
        """Devuelve un dict {class_id: bool} con la visibilidad de cada clase."""
        return {
            cid: cb.isChecked()
            for cid, cb in self.class_checkboxes.items()
        }

