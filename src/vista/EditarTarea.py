import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit, QComboBox, QVBoxLayout,
    QPushButton, QTextEdit, QHBoxLayout, QDateEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from src.logica.Tareas import TareaRepository
from src.Conexion.BaseDatos import get_db
from src.logica.Categorias import CategoriaRepository

class EditarTarea(QMainWindow):
    tarea_guardada = pyqtSignal(dict)

    def __init__(self, tarea_data):
        super().__init__()
        self.tarea_data = tarea_data
        self.db = next(get_db())
        self.tarea_repository = TareaRepository(self.db)
        self.setWindowTitle("Editar Tarea")
        self.setFixedWidth(330)
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        self.titulo_input = self.create_form_field("NOMBRE:", "✏️", main_layout)
        self.titulo_input.setText(self.tarea_data["titulo"])

        desc_label = QLabel("DESCRIPCIÓN:")
        main_layout.addWidget(desc_label)
        self.description = QTextEdit()
        self.description.setPlaceholderText("📝 Escribir aquí...")
        self.description.setText(self.tarea_data["descripcion"])
        self.description.setFixedHeight(80)
        main_layout.addWidget(self.description)
        self.categoria_combo = QComboBox()
        main_layout.addWidget(QLabel("CATEGORÍA:"))
        main_layout.addWidget(self.categoria_combo)
        self.populate_categoria_combo()
        index = self.categoria_combo.findText(self.tarea_data["categoria"], Qt.MatchFlag.MatchFixedString)
        if index >= 0:
            self.categoria_combo.setCurrentIndex(index)
        self.prioridad_combo = self.create_combo_field("PRIORIDAD:", ["Alta", "Media", "Baja"], main_layout)
        self.prioridad_combo.setCurrentText(self.tarea_data["prioridad"])
        self.estado_combo = self.create_combo_field("ESTADO:", ["Pendiente", "En Proceso", "Completada"], main_layout)
        self.estado_combo.setCurrentText(self.tarea_data["estado"])
        date_label = QLabel("FECHA:")
        main_layout.addWidget(date_label)
        self.date_edit = QDateEdit(calendarPopup=True)
        fecha_str = self.tarea_data["fecha"]
        if isinstance(fecha_str, str):
            fecha_qdate = QDate.fromString(fecha_str, "yyyy-MM-dd")
            if fecha_qdate.isValid():
                self.date_edit.setDate(fecha_qdate)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        main_layout.addWidget(self.date_edit)
        button_layout = QHBoxLayout()
        save_btn = QPushButton("GUARDAR")
        save_btn.clicked.connect(self.guardar_cambios)
        button_layout.addWidget(save_btn)

        back_btn = QPushButton("VOLVER")
        back_btn.clicked.connect(self.close)
        button_layout.addWidget(back_btn)
        main_layout.addLayout(button_layout)

    def create_form_field(self, label_text, emoji, layout):
        layout.addWidget(QLabel(label_text))
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(f"{emoji} Escribir aquí...")
        layout.addWidget(line_edit)
        return line_edit

    def create_combo_field(self, label_text, items, layout):
        layout.addWidget(QLabel(label_text))
        combo = QComboBox()
        combo.addItems(items)
        layout.addWidget(combo)
        return combo

    def populate_categoria_combo(self):
        self.categoria_combo.clear()
        with next(get_db()) as session:
            repo = CategoriaRepository(session)
            categorias = repo.listar_categorias()
            # Add each category name to the combobox
            for cat in categorias:
                self.categoria_combo.addItem(cat.nombre)

    def guardar_cambios(self):
        try:
            tarea_actualizada = {
                "idTarea": self.tarea_data["idTarea"],  # Preserve the original ID
                "titulo": self.titulo_input.text().strip(),
                "descripcion": self.description.toPlainText().strip(),
                "categoria": self.categoria_combo.currentText(),
                "prioridad": self.prioridad_combo.currentText(),
                "estado": self.estado_combo.currentText(),
                "fecha": self.date_edit.date().toString("yyyy-MM-dd")
            }

            if not tarea_actualizada['titulo'] or not tarea_actualizada['descripcion']:
                QMessageBox.warning(self, "Campos vacíos", "Los campos no pueden estar vacíos.")
                return
            actualizado = self.tarea_repository.actualizar_tarea(
                tarea_id=tarea_actualizada["idTarea"],
                titulo=tarea_actualizada["titulo"],
                descripcion=tarea_actualizada["descripcion"],
                categoria=tarea_actualizada["categoria"],
                prioridad=tarea_actualizada["prioridad"],
                estado=tarea_actualizada["estado"],
                fecha=tarea_actualizada["fecha"]
            )

            if not actualizado:
                QMessageBox.critical(self, "Error", "No se pudo actualizar la tarea en la base de datos.")
                return
            self.tarea_guardada.emit(tarea_actualizada)
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar los cambios: {e}")

    def closeEvent(self, event):
        # Close the database session if it is open
        if hasattr(self, 'db') and self.db:
            self.db.close()
        event.accept()