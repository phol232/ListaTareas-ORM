import sys
from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
        QTableWidget, QTableWidgetItem, QApplication, QHBoxLayout,
        QFrame, QHeaderView, QMessageBox, QCheckBox, QDateEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from datetime import datetime

from src.Conexion.BaseDatos import get_db
from src.logica.Categorias import CategoriaRepository

class CrearCategoria(QWidget):
        categoria_guardada = pyqtSignal(dict)

        def __init__(self, usuario_id=None, parent=None, *args, **kwargs):
                super().__init__(parent, *args, **kwargs)
                self.usuario_id = usuario_id
                self.initUI()
                self.cargar_categorias()

        def initUI(self):
                self.setWindowTitle("Categorías")
                self.resize(460, 450)
                main_layout = QVBoxLayout()
                title_label = QLabel("Categorías")
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
                main_layout.addWidget(title_label)
                top_bar_layout = QHBoxLayout()
                self.btn_crear = QPushButton("+ Crear Categoría")
                self.btn_crear.setStyleSheet("""
QPushButton {
background-color: #4CAF50;
color: white;
border: none;
padding: 8px 12px;
border-radius: 5px;
font-size: 12px;
}
QPushButton:hover {
background-color: #367c39;
}
                """)
                self.btn_crear.clicked.connect(self.abrir_formulario_categoria)
                top_bar_layout.addStretch()
                top_bar_layout.addWidget(self.btn_crear)
                main_layout.addLayout(top_bar_layout)

                # --- Tabla de Categorías ---
                self.table = QTableWidget()
                self.table.setColumnCount(5)
                self.table.setHorizontalHeaderLabels(["", "ID", "Nombre", "Fecha", "Acciones"])
                self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
                self.table.setColumnWidth(0, 40)
                self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
                self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
                self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
                self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
                self.table.setColumnWidth(4, 150)
                self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
                self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
                self.table.verticalHeader().setVisible(False)
                self.table.setStyleSheet("""
QTableWidget {
border: 1px solid #ddd;
border-radius: 8px;
}
QHeaderView::section {
background-color: #f0f0f0;
padding: 8px;
border: none;
border-bottom: 1px solid #ddd;
font-weight: bold;
}
                """)
                main_layout.addWidget(self.table)
                self.setLayout(main_layout)
                self.modal_frame = QFrame(self)
                self.modal_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
                self.modal_frame.setStyleSheet("background-color: rgba(0, 0, 0, 0.5);")
                modal_layout = QVBoxLayout(self.modal_frame)

                self.form_widget = QWidget()
                form_layout = QVBoxLayout()

                form_title = QLabel("Crear Categoría")
                form_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                form_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
                form_layout.addWidget(form_title)

                self.label_nombre = QLabel("Nombre:")
                self.input_nombre = QLineEdit()
                form_layout.addWidget(self.label_nombre)
                form_layout.addWidget(self.input_nombre)

                self.label_fecha = QLabel("Fecha:")
                form_layout.addWidget(self.label_fecha)
                self.input_fecha = QDateEdit(calendarPopup=True)
                self.input_fecha.setDate(QDate.currentDate())
                self.input_fecha.setDisplayFormat("yyyy-MM-dd")
                form_layout.addWidget(self.input_fecha)

                buttons_layout = QHBoxLayout()
                self.btn_guardar = QPushButton("Guardar")
                self.btn_guardar.setStyleSheet("""
QPushButton {
background-color: #007bff;
color: white;
padding: 6px 10px;
font-size: 12px;
}
QPushButton:hover {
background-color: #0056b3;
}
                """)
                self.btn_cancelar = QPushButton("Cancelar")
                self.btn_cancelar.setStyleSheet("""
QPushButton {
background-color: #6c757d;
color: white;
padding: 6px 10px;
font-size: 12px;
}
QPushButton:hover {
background-color: #545b62;
}
                """)
                self.btn_guardar.clicked.connect(self.guardar_categoria)
                self.btn_cancelar.clicked.connect(self.ocultar_formulario)
                buttons_layout.addWidget(self.btn_guardar)
                buttons_layout.addWidget(self.btn_cancelar)
                form_layout.addLayout(buttons_layout)

                self.form_widget.setLayout(form_layout)
                self.form_widget.setStyleSheet("""
QWidget {
background-color: white;
border-radius: 8px;
padding: 15px;
}
QLabel {
margin-bottom: 5px;
}
QLineEdit, QDateEdit {
padding: 5px;
border: 1px solid #ccc;
border-radius: 4px;
margin-bottom: 8px;
}
                """)
                modal_layout.addWidget(self.form_widget)
                self.modal_frame.hide()
                self.form_widget.hide()
                self.modal_frame_editar = QFrame(self)
                self.modal_frame_editar.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
                self.modal_frame_editar.setStyleSheet("background-color: rgba(0, 0, 0, 0.5);")
                modal_layout_editar = QVBoxLayout(self.modal_frame_editar)

                self.form_widget_editar = QWidget()
                form_layout_editar = QVBoxLayout()

                form_title_editar = QLabel("Editar Categoría")
                form_title_editar.setAlignment(Qt.AlignmentFlag.AlignCenter)
                form_title_editar.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
                form_layout_editar.addWidget(form_title_editar)

                self.label_id_editar = QLabel("ID Categoría:")
                self.input_id_editar = QLineEdit()
                self.input_id_editar.setReadOnly(True)
                form_layout_editar.addWidget(self.label_id_editar)
                form_layout_editar.addWidget(self.input_id_editar)

                self.label_nombre_editar = QLabel("Nombre:")
                self.input_nombre_editar = QLineEdit()
                form_layout_editar.addWidget(self.label_nombre_editar)
                form_layout_editar.addWidget(self.input_nombre_editar)

                self.label_fecha_editar = QLabel("Fecha:")
                form_layout_editar.addWidget(self.label_fecha_editar)
                self.input_fecha_editar = QDateEdit(calendarPopup=True)
                self.input_fecha_editar.setDisplayFormat("yyyy-MM-dd")
                form_layout_editar.addWidget(self.input_fecha_editar)

                buttons_layout_editar = QHBoxLayout()
                self.btn_guardar_editar = QPushButton("Guardar")
                self.btn_guardar_editar.setStyleSheet("""
QPushButton {
background-color: #007bff;
color: white;
padding: 6px 10px;
font-size: 12px;
}
QPushButton:hover {
background-color: #0056b3;
}
                """)
                self.btn_cancelar_editar = QPushButton("Cancelar")
                self.btn_cancelar_editar.setStyleSheet("""
QPushButton {
background-color: #6c757d;
color: white;
padding: 6px 10px;
font-size: 12px;
}
QPushButton:hover {
background-color: #545b62;
}
                """)
                self.btn_guardar_editar.clicked.connect(self.guardar_editar)
                self.btn_cancelar_editar.clicked.connect(self.ocultar_formulario_editar)
                buttons_layout_editar.addWidget(self.btn_guardar_editar)
                buttons_layout_editar.addWidget(self.btn_cancelar_editar)
                form_layout_editar.addLayout(buttons_layout_editar)

                self.form_widget_editar.setLayout(form_layout_editar)
                self.form_widget_editar.setStyleSheet("""
QWidget {
background-color: white;
border-radius: 8px;
padding: 15px;
}
QLabel {
margin-bottom: 5px;
}
QLineEdit, QDateEdit {
padding: 5px;
border: 1px solid #ccc;
border-radius: 4px;
margin-bottom: 8px;
}
                """)
                modal_layout_editar.addWidget(self.form_widget_editar)
                self.modal_frame_editar.hide()
                self.form_widget_editar.hide()

        def abrir_formulario_categoria(self):
                self.input_nombre.clear()
                self.input_fecha.setDate(QDate.currentDate())
                self.mostrar_modal(self.modal_frame, self.form_widget)

        def abrir_formulario_editar(self, id_cat, nombre, fecha_str):
                self.input_id_editar.setText(id_cat)
                self.input_nombre_editar.setText(nombre)
                fecha_qdate = QDate.fromString(fecha_str, "yyyy-MM-dd")
                if fecha_qdate.isValid():
                        self.input_fecha_editar.setDate(fecha_qdate)
                else:
                        self.input_fecha_editar.setDate(QDate.currentDate())
                self.mostrar_modal(self.modal_frame_editar, self.form_widget_editar)

        def mostrar_modal(self, modal_frame, form_widget):
                if self.parent():
                        main_window_geometry = self.parent().geometry()
                        main_x = main_window_geometry.x()
                        main_y = main_window_geometry.y()
                        main_width = main_window_geometry.width()
                        main_height = main_window_geometry.height()

                        modal_width = 350
                        modal_height = 250
                        x_position = main_x + (main_width - modal_width) // 2
                        y_position = main_y + (main_height - modal_height) // 2

                        modal_frame.setGeometry(main_x, main_y, main_width, main_height)
                        form_widget.setGeometry(x_position, y_position, modal_width, modal_height)
                        modal_frame.show()
                        form_widget.show()
                else:
                        modal_frame.setGeometry(0, 0, self.width(), self.height())
                        form_widget.setGeometry(0, 0, 350, 250)
                        form_widget.move((self.width() - form_widget.width()) // 2, (self.height() - form_widget.height()) // 2)
                        modal_frame.show()
                        form_widget.show()

        def ocultar_formulario(self):
                self.modal_frame.hide()
                self.form_widget.hide()

        def ocultar_formulario_editar(self):
                self.modal_frame_editar.hide()
                self.form_widget_editar.hide()

        def guardar_categoria(self):
                nombre = self.input_nombre.text().strip()
                if not nombre:
                        QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
                        return
                fecha_str = self.input_fecha.date().toString("yyyy-MM-dd")
                with next(get_db()) as session:
                        repo = CategoriaRepository(session)
                        categoria = repo.crear_categoria(nombre)
                if not categoria:
                        QMessageBox.warning(self, "Error", "La categoría ya existe o hubo un error.")
                        return
                self.categoria_guardada.emit({
                        "idCat": categoria.idCat,
                        "nombre": categoria.nombre,
                        "fecha": categoria.fecha.strftime("%Y-%m-%d") if categoria.fecha else ""
                })
                self.ocultar_formulario()
                self.agregar_categoria_a_tabla({
                        "idCat": categoria.idCat,
                        "nombre": categoria.nombre,
                        "fecha": categoria.fecha.strftime("%Y-%m-%d") if categoria.fecha else ""
                })

        def guardar_editar(self):
                id_cat = self.input_id_editar.text().strip()
                nombre = self.input_nombre_editar.text().strip()
                if not nombre:
                        QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
                        return

                # Get the edited date from QDateEdit (only date)
                nueva_fecha = self.input_fecha_editar.date().toString("yyyy-MM-dd")
                with next(get_db()) as session:
                        repo = CategoriaRepository(session)
                        resultado = repo.actualizar_categoria(id_cat, nombre)
                if not resultado:
                        QMessageBox.warning(self, "Error", "No se encontró la categoría.")
                        return
                for row in range(self.table.rowCount()):
                        if self.table.item(row, 1).text() == id_cat:
                                self.table.setItem(row, 2, QTableWidgetItem(nombre))
                                self.table.setItem(row, 3, QTableWidgetItem(nueva_fecha))
                                break
                self.ocultar_formulario_editar()

        def agregar_categoria_a_tabla(self, categoria_data):
                row = self.table.rowCount()
                self.table.insertRow(row)

                checkbox = QCheckBox()
                self.table.setCellWidget(row, 0, checkbox)
                self.table.setItem(row, 1, QTableWidgetItem(categoria_data['idCat']))
                self.table.setItem(row, 2, QTableWidgetItem(categoria_data['nombre']))
                self.table.setItem(row, 3, QTableWidgetItem(categoria_data['fecha']))

                btn_editar = QPushButton("Editar")
                btn_eliminar = QPushButton("Eliminar")

                btn_editar.setStyleSheet("""
QPushButton {
background-color: #17a2b8;
color: white;
padding: 4px 8px;
font-size: 12px;
border-radius: 4px;
}
QPushButton:hover {
background-color: #117a8b;
}
                """)
                btn_eliminar.setStyleSheet("""
QPushButton {
background-color: #dc3545;
color: white;
padding: 4px 8px;
font-size: 12px;
border-radius: 4px;
}
QPushButton:hover {
background-color: #c82333;
}
                """)
                btn_editar.clicked.connect(lambda _, r=row: self.editar_categoria(r))
                btn_eliminar.clicked.connect(lambda _, r=row: self.eliminar_categoria(r))

                acciones_widget = QWidget()
                acciones_layout = QHBoxLayout(acciones_widget)
                acciones_layout.addWidget(btn_editar)
                acciones_layout.addWidget(btn_eliminar)
                acciones_layout.setContentsMargins(0, 0, 0, 0)
                acciones_widget.setLayout(acciones_layout)
                self.table.setCellWidget(row, 4, acciones_widget)

        def cargar_categorias(self):
                with next(get_db()) as session:
                        repo = CategoriaRepository(session)
                        categorias = repo.listar_categorias()
                self.table.setRowCount(0)
                for cat in categorias:
                        self.agregar_categoria_a_tabla({
                                "idCat": cat.idCat,
                                "nombre": cat.nombre,
                                "fecha": cat.fecha.strftime("%Y-%m-%d") if cat.fecha else ""
                        })

        def editar_categoria(self, row):
                id_cat = self.table.item(row, 1).text()
                nombre = self.table.item(row, 2).text()
                fecha = self.table.item(row, 3).text()
                self.abrir_formulario_editar(id_cat, nombre, fecha)

        def eliminar_categoria(self, row):
                respuesta = QMessageBox.question(
                        self, "Confirmar Eliminación",
                        "¿Seguro que quieres eliminar esta categoría?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if respuesta == QMessageBox.StandardButton.Yes:
                        id_cat = self.table.item(row, 1).text()
                        with next(get_db()) as session:
                                repo = CategoriaRepository(session)
                                eliminado = repo.eliminar_categoria(id_cat)
                        if eliminado:
                                self.table.removeRow(row)
                                QMessageBox.information(self, "Éxito", "Categoría eliminada.")
                        else:
                                QMessageBox.warning(self, "Error", "No se pudo eliminar la categoría.")

        def resizeEvent(self, event):
                if self.modal_frame.isVisible() and self.parent():
                        main_window_geometry = self.parent().geometry()
                        main_x = main_window_geometry.x()
                        main_y = main_window_geometry.y()
                        main_width = main_window_geometry.width()
                        main_height = main_window_geometry.height()

                        modal_width = 350
                        modal_height = 250
                        x_position = main_x + (main_width - modal_width) // 2
                        y_position = main_y + (main_height - modal_height) // 2

                        self.modal_frame.setGeometry(main_x, main_y, main_width, main_height)
                        self.form_widget.setGeometry(x_position, y_position, modal_width, modal_height)
                elif self.modal_frame_editar.isVisible() and self.parent():
                        main_window_geometry = self.parent().geometry()
                        main_x = main_window_geometry.x()
                        main_y = main_window_geometry.y()
                        main_width = main_window_geometry.width()
                        main_height = main_window_geometry.height()

                        modal_width = 350
                        modal_height = 250
                        x_position = main_x + (main_width - modal_width) // 2
                        y_position = main_y + (main_height - modal_height) // 2

                        self.modal_frame_editar.setGeometry(main_x, main_y, main_width, main_height)
                        self.form_widget_editar.setGeometry(x_position, y_position, modal_width, modal_height)
                super().resizeEvent(event)


if __name__ == '__main__':
        app = QApplication(sys.argv)
        window = CrearCategoria()
        window.show()
        sys.exit(app.exec())