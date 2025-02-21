import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QLineEdit, QComboBox, QVBoxLayout, QPushButton,
    QTextEdit, QHBoxLayout, QDateEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal


from src.logica.Tareas import TareaRepository
from src.logica.Categorias import CategoriaRepository
from src.Conexion.BaseDatos import get_db


class CategoryForm(QMainWindow):
    tarea_guardada = pyqtSignal(dict)

    def __init__(self, user_id: str):  
        super().__init__()
        self.user_id = user_id  
        self.setFixedWidth(330)
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        self.titulo_input = self.create_form_field("NOMBRE:", "✏️", main_layout)

        desc_label = QLabel("DESCRIPCIÓN:")
        main_layout.addWidget(desc_label)

        self.description = QTextEdit()
        self.description.setPlaceholderText("📝 Escribir aquí...")
        self.description.setFixedHeight(80)
        main_layout.addWidget(self.description)

        self.categoria_combo = self.create_combo_field("CATEGORÍA:", [], main_layout)  
        self.cargar_categorias()
        self.prioridad_combo = self.create_combo_field("PRIORIDAD:", ["Alta", "Media", "Baja"], main_layout)
        self.estado_combo = self.create_combo_field("ESTADO:", ["Pendiente", "En Proceso", "Completada"], main_layout)

        date_label = QLabel("FECHA:")
        main_layout.addWidget(date_label)

        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        main_layout.addWidget(self.date_edit)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("GUARDAR")
        save_btn.clicked.connect(self.guardar_tarea)
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

    def cargar_categorias(self):
        """Carga las categorías desde la base de datos."""
        try:
            
            with next(get_db()) as db:
                categoria_repository = CategoriaRepository(db)
                categorias = categoria_repository.listar_categorias()
                nombres_categorias = [cat.nombre for cat in categorias]
                self.categoria_combo.addItems(nombres_categorias)
                if not nombres_categorias:
                    print("No se encontraron categorías. El combo estará vacío.")
        except Exception as e:
            print(f"Error al cargar categorías: {e}")
            QMessageBox.critical(self, "Error", "No se pudieron cargar las categorías.")

    def guardar_tarea(self):
        try:
            print("💾 Iniciando el proceso para guardar la tarea...")

            if not self.titulo_input.text().strip():
                raise ValueError("❗ El título de la tarea es obligatorio.")
            if not self.description.toPlainText().strip():
                raise ValueError("❗ La descripción de la tarea es obligatoria.")

            nueva_tarea = {
                "titulo": self.titulo_input.text().strip(),
                "descripcion": self.description.toPlainText().strip(),
                "categoria": self.categoria_combo.currentText(),
                "prioridad": self.prioridad_combo.currentText(),
                "estado": self.estado_combo.currentText(),
                "fecha": self.date_edit.date().toString("yyyy-MM-dd"),
                "user_id": self.user_id
            }
            print("Datos de tarea a guardar:", nueva_tarea)

        
            with next(get_db()) as db:
                tarea_repository = TareaRepository(db)
                tarea_creada = tarea_repository.crear_tarea(
                    user_id=nueva_tarea["user_id"],
                    titulo=nueva_tarea["titulo"],
                    descripcion=nueva_tarea["descripcion"],
                    categoria=nueva_tarea["categoria"],
                    prioridad=nueva_tarea["prioridad"],
                    estado=nueva_tarea["estado"],
                    fecha=nueva_tarea["fecha"]
                )
                
                nueva_tarea["id"] = tarea_creada.id if hasattr(tarea_creada, "id") else None

            QMessageBox.information(self, "Éxito", "✅ Tarea guardada exitosamente.")
            self.tarea_guardada.emit(nueva_tarea)
            self.limpiar_formulario()
            self.close()

        except ValueError as ve:
            QMessageBox.warning(self, "Campos Obligatorios", str(ve))
        except Exception as e:
            print(f"Error: {e}")
            QMessageBox.critical(self, "Error Inesperado", f"❌ Error inesperado: {str(e)}")

    def limpiar_formulario(self):
        self.titulo_input.clear()
        self.description.clear()
        self.categoria_combo.setCurrentIndex(0)
        self.prioridad_combo.setCurrentIndex(0)
        self.estado_combo.setCurrentIndex(0)
        self.date_edit.setDate(QDate.currentDate())

    def closeEvent(self, event):
        event.accept()
