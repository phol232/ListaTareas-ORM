import sys
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QComboBox, QApplication, QHBoxLayout, QListWidget,
    QFrame, QHeaderView, QToolButton, QListWidgetItem, QMenu, QAbstractItemView, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from src.vista.CrearTarea import CategoryForm
from src.vista.EditarTarea import EditarTarea
from src.logica.Tareas import TareaRepository
from src.Conexion.BaseDatos import get_db
from src.vista.Notificaciones import NotificacionesDialog

class ModernTodoListApp(QWidget):
    def __init__(self, usuario=None, login_window=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario
        self.login_window = login_window
        self.setWindowTitle("TODO - LIST")
        self.setGeometry(100, 100, 1250, 700)
        self.db = next(get_db())
        self.tarea_repository = TareaRepository(self.db)
        self.task_data = {}
        self.initUI()
        self.cargar_tareas()
        self.actualizar_totales_por_estado()

    def cargar_tareas(self):
        try:
            print("🔄 Cargando tareas...")
            if not self.usuario:
                QMessageBox.warning(self, "Advertencia", "❌ No hay un usuario logueado.")
                return
            # Use a new session to load tasks.
            with next(get_db()) as db:
                tarea_repository = TareaRepository(db)
                tareas = tarea_repository.obtener_tareas_de_usuario(self.usuario.id)
                self.actualizar_tabla(tareas)
        except Exception as e:
            print(f"❌ Error al cargar tareas: {e}")
            QMessageBox.critical(self, "Error", f"Error al cargar tareas: {e}")
        finally:
            self.actualizar_totales_por_estado()

    def filtrar_tareas_por_prioridad(self, prioridad):
        try:
            if prioridad.lower() == "todas":
                print("🔎 Se seleccionó la opción Todas. Se cargarán todas las tareas.")
                self.cargar_tareas()
                return

            print(f"🔎 Filtrando tareas de prioridad: {prioridad}")
            with next(get_db()) as db:
                tarea_repository = TareaRepository(db)
                todas = tarea_repository.listar_tareas_por_prioridad(prioridad)
                tareas = [t for t in todas if t.id_usuario == self.usuario.id]
                self.actualizar_tabla(tareas)
        except Exception as e:
            print(f"❌ Error al filtrar tareas: {e}")
            QMessageBox.critical(self, "Error", f"Error al filtrar tareas: {e}")
        finally:
            self.actualizar_totales_por_estado()

    def buscar_tareas(self):
        search_text = self.search_input.text().strip()
        if not search_text:
            self.cargar_tareas()
            return
        try:
            estado_options = ("pendiente", "completada", "en proceso", "terminada")
            categoria = None
            estado = None
            if search_text.lower() in estado_options:
                estado = search_text
            else:
                categoria = search_text
            with next(get_db()) as db:
                tarea_repository = TareaRepository(db)
                tareas = tarea_repository.buscar_tareas(categoria=categoria, estado=estado)
                tareas = [t for t in tareas if t.id_usuario == self.usuario.id]
                self.actualizar_tabla(tareas)
        except Exception as e:
            print(f"❌ Error al buscar tareas: {e}")
            QMessageBox.critical(self, "Error", f"Error al buscar tareas: {e}")
        finally:
            self.actualizar_totales_por_estado()

    def actualizar_tabla(self, tareas):
        self.task_table.setRowCount(0)
        self.task_data.clear()
        for tarea in tareas:
            id_tarea = str(tarea.idTarea)
            self.task_data[id_tarea] = tarea
            nombre_categoria = tarea.categoria_obj.nombre if tarea.categoria_obj else "Sin categoría"
            self.agregar_tarea(
                id_tarea,
                tarea.titulo,
                tarea.descripcion,
                nombre_categoria,
                tarea.prioridad,
                tarea.estado,
                tarea.fecha.strftime("%Y-%m-%d") if tarea.fecha else ""
            )

    def actualizar_totales_por_estado(self):
        with next(get_db()) as db:
            repo = TareaRepository(db)
            total_tasks = repo.obtener_total_tareas()
            totales = repo.obtener_totales_por_estado()
            self.total_tasks_label.setText(str(total_tasks))
            self.completed_tasks_label.setText(str(totales.get("Completada", 0)))
            self.inprocess_tasks_label.setText(str(totales.get("En Proceso", 0)))
            self.pending_tasks_label.setText(str(totales.get("Pendiente", 0)))

    def initUI(self):
        if self.usuario:
            welcome_label = QLabel(f"👋 Bienvenido de nuevo, {self.usuario.name}")
        else:
            welcome_label = QLabel("Bienvenido al TODO-LIST")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(250)
        sidebar_frame.setStyleSheet("""
QFrame {
background-color: #2965f1;
border-right: 1px solid #dcdde1;
}
        """)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(10)

        logo_label = QLabel("TODO - LIST")
        logo_label.setStyleSheet("""
font-size: 24px;
font-weight: bold;
color: white;
margin-bottom: 20px;
        """)
        sidebar_layout.addWidget(logo_label)

        self.sidebar = QListWidget()
        menu_items = [
            (" ALL TASKS", "☰"),
            (" CALENDAR", "📅"),
            (" SETTINGS", "⚙️")
        ]
        for text, icon in menu_items:
            item = QListWidgetItem(f"{icon} {text}")
            self.sidebar.addItem(item)
        self.sidebar.setStyleSheet("""
QListWidget {
border: none;
font-size: 14px;
background-color: #2965f1;
color: white;
}
QListWidget::item {
padding: 10px 10px;
margin: 0px;
}
QListWidget::item:selected {
background-color: white;
color: #6c5ce7;
font-weight: bold;
}
QListWidget::item:hover {
background-color: white;
color: black;
}
        """)
        sidebar_layout.addWidget(self.sidebar)
        sidebar_layout.addStretch()

        logout_button = QPushButton("Cerrar Sesión 🚪")
        logout_button.setStyleSheet("""
QPushButton {
background-color: #e74c3c;
color: white;
border: none;
padding: 10px 15px;
border-radius: 5px;
font-weight: bold;
font-size: 14px;
}
QPushButton:hover {
background-color: #c0392b;
}
        """)
        logout_button.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_button)
        sidebar_frame.setLayout(sidebar_layout)
        main_layout.addWidget(sidebar_frame)
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: #f5f6fa;")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        header_layout = QVBoxLayout()
        top_header = QHBoxLayout()
        welcome_header = QLabel(f"Welcome back {self.usuario.name if self.usuario else 'Usuario'}")
        welcome_header.setStyleSheet("font-size: 14px; color: #666666;")
        top_header.addWidget(welcome_header)
        top_header.addStretch()
        notification_button = QToolButton()
        notification_button.setText("🔔")
        notification_button.setStyleSheet("""
QToolButton {
font-size: 20px;
padding: 5px;
border-radius: 5px;
}
QToolButton:hover {
background-color: #e0e0e0;
}
        """)
        notification_button.clicked.connect(self.mostrar_notificaciones)
        top_header.addWidget(notification_button)
        header_layout.addLayout(top_header)
        status_layout = QHBoxLayout()
        total_frame = QFrame()
        total_frame.setFixedSize(200, 100)
        total_frame.setStyleSheet("""
background-color: white;
border: 3px solid #dcdde1;
border-radius: 5px;
        """)
        total_layout = QVBoxLayout()
        total_title = QLabel("Total Tareas")
        total_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_title = QFont()
        font_title.setPointSize(14)
        total_title.setFont(font_title)
        total_layout.addWidget(total_title)
        self.total_tasks_label = QLabel("0")
        self.total_tasks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_count = QFont()
        font_count.setPointSize(24)
        self.total_tasks_label.setFont(font_count)
        total_layout.addWidget(self.total_tasks_label)
        total_frame.setLayout(total_layout)
        status_layout.addWidget(total_frame)
        completed_frame = QFrame()
        completed_frame.setFixedSize(200, 100)
        completed_frame.setStyleSheet("""
background-color: white;
border: 3px solid #dcdde1;
border-radius: 5px;
        """)
        completed_layout = QVBoxLayout()
        completed_title = QLabel("Completadas")
        completed_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        completed_title.setFont(font_title)
        completed_layout.addWidget(completed_title)
        self.completed_tasks_label = QLabel("0")
        self.completed_tasks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.completed_tasks_label.setFont(font_count)
        completed_layout.addWidget(self.completed_tasks_label)
        completed_frame.setLayout(completed_layout)
        status_layout.addWidget(completed_frame)
        inprocess_frame = QFrame()
        inprocess_frame.setFixedSize(200, 100)
        inprocess_frame.setStyleSheet("""
background-color: white;
border: 3px solid #dcdde1;
border-radius: 5px;
        """)
        inprocess_layout = QVBoxLayout()
        inprocess_title = QLabel("En Proceso")
        inprocess_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inprocess_title.setFont(font_title)
        inprocess_layout.addWidget(inprocess_title)
        self.inprocess_tasks_label = QLabel("0")
        self.inprocess_tasks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.inprocess_tasks_label.setFont(font_count)
        inprocess_layout.addWidget(self.inprocess_tasks_label)
        inprocess_frame.setLayout(inprocess_layout)
        status_layout.addWidget(inprocess_frame)
        pending_frame = QFrame()
        pending_frame.setFixedSize(200, 100)
        pending_frame.setStyleSheet("""
background-color: white;
border: 3px solid #dcdde1;
border-radius: 5px;
        """)
        pending_layout = QVBoxLayout()
        pending_title = QLabel("Pendientes")
        pending_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pending_title.setFont(font_title)
        pending_layout.addWidget(pending_title)
        self.pending_tasks_label = QLabel("0")
        self.pending_tasks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pending_tasks_label.setFont(font_count)
        pending_layout.addWidget(self.pending_tasks_label)
        pending_frame.setLayout(pending_layout)
        status_layout.addWidget(pending_frame)

        header_layout.addLayout(status_layout)
        content_layout.addLayout(header_layout)
        filter_layout = QHBoxLayout()
        self.priority_button = QPushButton("PRIORIDAD")
        self.priority_button.setStyleSheet("""
QPushButton {
background-color: #ffd32a;
border-radius: 5px;
padding: 12px 20px;
font-size: 14px;
}
QPushButton:hover {
background-color: #d0d0d0;
}
        """)
        self.priority_menu = QMenu()
        todas_option = self.priority_menu.addAction("Todas")
        todas_option.triggered.connect(lambda: (
                                           self.priority_button.setText("Todas"),
                                           self.cargar_tareas()
                                       ))
        high_priority = self.priority_menu.addAction("Alta")
        high_priority.triggered.connect(lambda: (
                                            self.priority_button.setText("Alta 🔴"),
                                            self.filtrar_tareas_por_prioridad("Alta")
                                        ))
        medium_priority = self.priority_menu.addAction("Media")
        medium_priority.triggered.connect(lambda: (
                                              self.priority_button.setText("Media 🟡"),
                                              self.filtrar_tareas_por_prioridad("Media")
                                          ))
        low_priority = self.priority_menu.addAction("Baja")
        low_priority.triggered.connect(lambda: (
                                           self.priority_button.setText("Baja 🟢"),
                                           self.filtrar_tareas_por_prioridad("Baja")
                                       ))
        self.priority_button.setMenu(self.priority_menu)
        filter_layout.addWidget(self.priority_button)

        input_wrapper = QFrame()
        input_wrapper.setStyleSheet("""
QFrame {
background-color: white;
border-radius: 5px;
padding: 0px;
height: 20px;
border: 1px solid #dcdde1;
}
        """)
        input_layout = QHBoxLayout(input_wrapper)
        input_layout.setContentsMargins(2, 0, 2, 0)
        input_layout.setSpacing(2)
        icon_label = QLabel("🔍")
        icon_label.setStyleSheet("color: black; margin: 0px; font-size: 14px; border: none;")
        input_layout.addWidget(icon_label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Categorias o estado")
        self.search_input.setMinimumSize(140, 30)
        self.search_input.setFixedHeight(25)
        self.search_input.setStyleSheet("""
QLineEdit {
border: none;
background-color: white;
color: black;
padding: 0 8px;
font-size: 14px;
height: 25px;
}
        """)
        input_layout.addWidget(self.search_input)
        search_button = QPushButton("BUSCAR")
        search_button.setFixedHeight(30)
        search_button.setStyleSheet("""
QPushButton {
background-color: #ffc61a;
border-radius: 5px;
padding: 0 15px;
font-size: 14px;
font-weight: bold;
color: black;
height: 30px;
}
QPushButton:hover {
background-color: #e1a500;
color: white;
}
        """)
        search_button.clicked.connect(self.buscar_tareas)
        input_layout.addWidget(search_button)
        filter_layout.addWidget(input_wrapper)
        filter_layout.addStretch()

        self.category_button = QPushButton("🗂 CATEGORÍAS")
        self.category_button.setStyleSheet("""
QPushButton {
background-color: #a29bfe;
border: none;
padding: 10px 20px;
border-radius: 5px;
font-weight: bold;
font-size: 14px;
color: white;
}
QPushButton:hover {
background-color: #6c5ce7;
}
        """)
        self.category_button.clicked.connect(self.open_categories_form)
        filter_layout.addWidget(self.category_button)

        self.create_button = QPushButton("➕ CREAR TAREA")
        self.create_button.setStyleSheet("""
QPushButton {
background-color: #ffd32a;
border: none;
padding: 10px 20px;
border-radius: 5px;
font-weight: bold;
font-size: 14px;
}
QPushButton:hover {
background-color: #ffc61a;
}
        """)
        self.create_button.clicked.connect(self.open_new_task_form)
        filter_layout.addWidget(self.create_button)

        content_layout.addLayout(filter_layout)

        self.task_table = QTableWidget()
        self.task_table.setColumnCount(9)
        self.task_table.setHorizontalHeaderLabels([
            "", "NOMBRE", "DESCRIPCION", "CATEGORIA", "PRIORIDAD", "STATUS", "FECHA", "ACCIONES", ""
        ])
        self.task_table.setStyleSheet("""
QTableWidget {
background-color: white;
border: 2px solid #9c9c9c;
border-radius: 10px;
gridline-color: #f5f6fa;
outline: none;
}
QHeaderView::section {
background-color: white;
padding: 10px;
border: none;
border-bottom: 2px solid #dcdde1;
font-weight: bold;
color: #2f3640;
}
QTableWidget::item {
padding: 10px;
border: none;
}
QTableWidget::item:selected {
background: transparent;
color: black;
}
        """)
        self.task_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.task_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.task_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.task_table.setShowGrid(False)
        header = self.task_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.task_table.setColumnWidth(0, 40)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.task_table.setColumnWidth(7, 310)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)
        self.task_table.setColumnWidth(8, 0)
        self.task_table.setColumnHidden(8, True)
        content_layout.addWidget(self.task_table)
        content_frame.setLayout(content_layout)
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)
        self.task_table.verticalHeader().setDefaultSectionSize(50)

    def mostrar_notificaciones(self):
        session = next(get_db())
        dialog = NotificacionesDialog(session, parent=self)
        dialog.resize(440, 300)
        parent_geo = self.geometry()
        x = parent_geo.x() + parent_geo.width() - dialog.width() - 10
        y = parent_geo.y() + 10
        dialog.move(x, y)
        dialog.exec()

    def open_new_task_form(self):
        if self.usuario and self.usuario.id:
            self.new_task_window = CategoryForm(self.usuario.id)
            self.new_task_window.tarea_guardada.connect(self.agregar_tarea_desde_formulario)
            main_window_geometry = self.geometry()
            main_x = main_window_geometry.x()
            main_y = main_window_geometry.y()
            main_width = main_window_geometry.width()
            window_width = 350  # Width for CategoryForm
            window_height = 500  # Height for CategoryForm
            x_position = main_x + (main_width - window_width) // 2
            y_position = main_y + (700 - window_height) // 2
            self.new_task_window.resize(window_width, window_height)
            self.new_task_window.move(x_position, y_position)
            self.new_task_window.show()
        else:
            QMessageBox.critical(self, "Error", "No se pudo determinar el usuario actual.")

    def open_categories_form(self):
        if self.usuario and self.usuario.id:
            from src.vista.CrearCategoria import CrearCategoria
            self.categories_window = CrearCategoria(self.usuario.id)
            main_window_geometry = self.geometry()
            main_x = main_window_geometry.x()
            main_y = main_window_geometry.y()
            main_width = main_window_geometry.width()
            window_width = 450
            window_height = 450
            x_position = main_x + (main_width - window_width) // 2
            y_position = main_y + (700 - window_height) // 2
            self.categories_window.resize(window_width, window_height)
            self.categories_window.move(x_position, y_position)
            self.categories_window.show()
        else:
            QMessageBox.critical(self, "Error", "No se pudo determinar el usuario actual.")

    def agregar_tarea_desde_formulario(self, tarea):
        print("✅ Tarea guardada. Se actualizará la lista de tareas.")
        self.cargar_tareas()
        self.actualizar_totales_por_estado()
        QMessageBox.information(self, "Éxito", "✅ Tarea guardada exitosamente.")

    def agregar_tarea(self, id_tarea, nombre, descripcion, categoria, prioridad, estado, fecha):
        row = self.task_table.rowCount()
        self.task_table.insertRow(row)
        checkbox = QCheckBox()
        checkbox.setChecked(True if estado == "Completada" else False)
        checkbox.stateChanged.connect(lambda state, tid=id_tarea: self.actualizar_estado_tarea(tid, state))
        self.task_table.setCellWidget(row, 0, checkbox)
        self.task_table.setItem(row, 1, QTableWidgetItem(nombre))
        self.task_table.setItem(row, 2, QTableWidgetItem(descripcion))
        self.task_table.setItem(row, 3, QTableWidgetItem(categoria))
        self.task_table.setItem(row, 4, QTableWidgetItem(prioridad))
        self.task_table.setItem(row, 5, QTableWidgetItem(estado))
        self.task_table.setItem(row, 6, QTableWidgetItem(fecha))
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(5, 2, 5, 2)
        action_layout.setSpacing(5)
        btn_edit = QPushButton("Editar")
        btn_edit.setStyleSheet("""
QPushButton {
background-color: white;
color: black;
border: 1px solid #6c5ce7;
padding: 5px 10px;
border-radius: 5px;
font-weight: bold;
}
QPushButton:hover {
background-color: #6c5ce7;
color: white;
}
        """)
        btn_edit.clicked.connect(lambda checked, r=row: self.editar_tarea(r))
        btn_delete = QPushButton("Eliminar")
        btn_delete.setStyleSheet("""
QPushButton {
background-color: white;
color: red;
border: 1px solid red;
padding: 5px 10px;
border-radius: 5px;
font-weight: bold;
}
QPushButton:hover {
background-color: red;
color: white;
}
        """)
        btn_delete.clicked.connect(lambda checked, r=row: self.eliminar_tarea(r))
        action_layout.addWidget(btn_edit)
        action_layout.addWidget(btn_delete)
        action_widget.setMinimumWidth(200)
        self.task_table.setCellWidget(row, 7, action_widget)
        id_item = QTableWidgetItem(id_tarea)
        self.task_table.setItem(row, 8, id_item)
        self.task_table.setColumnHidden(8, True)

    def actualizar_estado_tarea(self, id_tarea, state):
        nuevo_estado = "Completada" if state == 2 else "Pendiente"
        print(f"Actualizando estado de la tarea {id_tarea} a {nuevo_estado}")
        try:
            if self.tarea_repository.actualizar_tarea(tarea_id=id_tarea, estado=nuevo_estado):
                row = self.obtener_fila_por_id(id_tarea)
                if row is not None:
                    self.task_table.item(row, 5).setText(nuevo_estado)
                self.actualizar_totales_por_estado()
            else:
                QMessageBox.critical(self, "Error", "No se pudo actualizar el estado en la base de datos.")
        except Exception as e:
            print(f"Error al actualizar estado: {e}")
            QMessageBox.critical(self, "Error", f"Error al actualizar estado: {e}")

    def obtener_fila_por_id(self, id_tarea):
        for row in range(self.task_table.rowCount()):
            id_item = self.task_table.item(row, 8)
            if id_item and id_item.text() == id_tarea:
                return row
        return None

    def editar_tarea(self, row):
        id_item = self.task_table.item(row, 8)
        if id_item is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID de la tarea.")
            return
        id_tarea = id_item.text()
        tarea_obj = self.task_data.get(id_tarea)
        if not tarea_obj:
            QMessageBox.warning(self, "Error", "Tarea no encontrada en memoria.")
            return
        tarea_data = {
            "idTarea": tarea_obj.idTarea,
            "titulo": tarea_obj.titulo,
            "descripcion": tarea_obj.descripcion,
            "categoria": (tarea_obj.categoria_obj.nombre if tarea_obj.categoria_obj else "Sin categoría"),
            "prioridad": tarea_obj.prioridad,
            "estado": tarea_obj.estado,
            "fecha": tarea_obj.fecha.strftime("%Y-%m-%d") if tarea_obj.fecha else ""
        }
        self.editar_tarea_window = EditarTarea(tarea_data)
        self.editar_tarea_window.tarea_guardada.connect(self.actualizar_tarea_editada)
        self.editar_tarea_window.show()

    def actualizar_tarea_editada(self, tarea_actualizada):
        print("Tarea actualizada desde el formulario de edición:", tarea_actualizada)
        self.cargar_tareas()
        QMessageBox.information(self, "Éxito", "✅ Tarea actualizada exitosamente.")

    def eliminar_tarea(self, row):
        confirm_dialog = QMessageBox()
        confirm_dialog.setIcon(QMessageBox.Icon.Warning)
        confirm_dialog.setWindowTitle("Confirmar Eliminación")
        confirm_dialog.setText("¿Estás seguro de que deseas eliminar esta tarea?")
        confirm_dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirm_dialog.setDefaultButton(QMessageBox.StandardButton.No)
        respuesta = confirm_dialog.exec()

        if respuesta == QMessageBox.StandardButton.Yes:
            id_item = self.task_table.item(row, 8)
            if id_item is not None:
                id_tarea = id_item.text()
                if self.tarea_repository.eliminar_tarea(id_tarea):
                    del self.task_data[id_tarea]
                    self.task_table.removeRow(row)
                    print(f"Tarea eliminada en la fila {row}")
                else:
                    QMessageBox.critical(self, "Error", "No se pudo eliminar la tarea de la base de datos.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo obtener el ID de la tarea")
        else:
            print("Eliminación cancelada.")
        self.actualizar_totales_por_estado()

    def logout(self):
        message_box = QMessageBox()
        message_box.setWindowTitle("Cerrar Sesión")
        message_box.setText("Sesión cerrada exitosamente.")
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.exec()
        self.usuario = None
        self.logged_in_user_id = None
        self.hide()
        if hasattr(self, 'login_window') and self.login_window:
            self.login_window.show()
        else:
            from src.vista.login import ModernLogin
            self.login_window = ModernLogin()
            self.login_window.show()

    def closeEvent(self, event):
        if hasattr(self, 'db') and self.db:
            self.db.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ModernTodoListApp()
    window.show()
    sys.exit(app.exec())