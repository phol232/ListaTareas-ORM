import sys
import os
import hashlib

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QCheckBox, QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon, QAction
from PyQt6.QtCore import Qt
from src.logica.Usuarios import UserRepository
from src.Conexion.BaseDatos import get_db
from src.vista.Menu import ModernTodoListApp

class ModernLogin(QWidget):

    WINDOW_TITLE = "Login"
    WINDOW_GEOMETRY = (100, 100, 400, 550)
    RESOURCES_PATH = "../Resources"

    STYLES = {
        'WINDOW': "background-color: white;",
        'BUTTON': """
QPushButton {
background-color: white;
border: 1px solid #D1D5DB;
padding: 10px;
border-radius: 5px;
font-size: 14px;
}
QPushButton:hover {
background-color: #F3F4F6;
}
        """,
        'INPUT': """
QLineEdit {
border: 1px solid #D1D5DB;
padding: 10px;
padding-left: 15px; /*  ESPACIO para el icono */
border-radius: 5px;
font-size: 14px;
height: 30px;
}
QLineEdit:focus {
border: 1px solid #0078D7;
}
        """,
        'LOGIN_BUTTON': """
QPushButton {
background-color: #0078D7;
color: white;
font-size: 16px;
padding: 14px;
border-radius: 5px;
}
QPushButton:hover {
background-color: #005BB5;
}
            """
    }

    def __init__(self, register_window=None):  # Recibe la ventana de registro
        super().__init__()
        self.register_window = register_window  # Guarda la referencia
        self.init_window()
        self.setup_ui_components()

        # --- Inicialización CORRECTA de la base de datos ---
        self.db = next(get_db())  # Obtiene una sesión
        self.user_repository = UserRepository(self.db)
        # ---------------------------------------------------
        self.logged_in_user_id = None

    def init_window(self):
        """Initialize the main window properties."""
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setGeometry(*self.WINDOW_GEOMETRY)
        self.setStyleSheet(self.STYLES['WINDOW'])

    def setup_ui_components(self):
        """Set up all UI components and layouts."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self._setup_header_section(main_layout)
        self._setup_social_login_section(main_layout)
        self._setup_email_login_section(main_layout)
        self._setup_footer_section(main_layout)
        self.setLayout(main_layout)

    def _setup_header_section(self, layout: QVBoxLayout):
        """Set up the header section with logo and titles."""
        self._add_logo(layout)
        self._add_spacer(layout)
        self._add_titles(layout)
        self._add_spacer(layout)

    def _add_logo(self, layout: QVBoxLayout):
        """Add the logo to the layout."""
        logo_label = QLabel("🔵 ToDO-LIST")
        logo_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

    def _add_titles(self, layout: QVBoxLayout):
        """Add titles to the layout."""
        title_label = QLabel("Log in to your Account")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel("Welcome back! Select method to log in:")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)

    def _setup_social_login_section(self, layout: QVBoxLayout):
        """Set up the social login buttons section."""
        social_layout = QHBoxLayout()
        self._create_social_button(social_layout, "Google", "Google.png")
        self._create_social_button(social_layout, "Facebook", "Facebook.png")
        layout.addLayout(social_layout)
        self._add_separator(layout)

    def _create_social_button(self, layout: QHBoxLayout, text: str, icon_name: str):
        """Create a social login button."""
        button = QPushButton(text)
        button.setIcon(QIcon(self._get_resource_path(icon_name)))
        button.setStyleSheet(self.STYLES['BUTTON'])
        layout.addWidget(button)


    def _add_separator(self, layout: QVBoxLayout):
        """Add a separator label."""
        separator_label = QLabel("OR CONTINUE WITH EMAIL")
        separator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator_label.setStyleSheet("color: gray; margin-top: 10px; margin-bottom: 10px;")
        layout.addWidget(separator_label)

    def _setup_email_login_section(self, layout: QVBoxLayout):
        """Set up the email login section with input fields."""
        self.email_input = self._create_input_field("Email", "icons8-email-24.png")  # Iconos
        self.password_input = self._create_input_field("Password", "icons8-password-24.png", is_password=True)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        self._setup_login_options(layout)

    def _create_input_field(self, placeholder: str, icon_name: str, is_password: bool = False) -> QLineEdit:
        """Create an input field with the specified properties."""
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setStyleSheet(self.STYLES['INPUT'])
        if is_password:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)
        icon_path = self._get_resource_path(icon_name)
        icon_action = QAction(QIcon(icon_path), "", input_field)
        input_field.addAction(icon_action, QLineEdit.ActionPosition.LeadingPosition)
        return input_field

    def _setup_login_options(self, layout: QVBoxLayout):
        """Set up the remember me checkbox and forgot password link."""
        options_layout = QHBoxLayout()
        self.remember_me = QCheckBox("Remember me")
        self.forgot_password = self._create_link_label("Forgot Password?", margin_left="68px")
        options_layout.addWidget(self.remember_me)
        options_layout.addWidget(self.forgot_password)
        layout.addLayout(options_layout)

    def _create_link_label(self, text: str, margin_left: str = "0px") -> QLabel:
        """Create a clickable link label."""
        label = QLabel(f'<a href="#">{text}</a>')
        label.setOpenExternalLinks(True)
        label.setStyleSheet(f"color: #0078D7; font-size: 14px; margin-left: {margin_left};")
        return label

    def _setup_footer_section(self, layout: QVBoxLayout):
        """Set up the footer section with login button and create account link."""
        self._add_login_button(layout)
        self._add_create_account_link(layout)

    def _add_login_button(self, layout: QVBoxLayout):
        """Add the login button to the layout."""
        self.login_button = QPushButton("Log in")
        self.login_button.setStyleSheet(self.STYLES['LOGIN_BUTTON'])
        self.login_button.clicked.connect(self.on_login_clicked)
        layout.addWidget(self.login_button)

    def _add_create_account_link(self, layout: QVBoxLayout):
        """Add the create account link."""
        hbox = QHBoxLayout()
        hbox.addStretch()
        create_account_label = QLabel("Don't have an account? ")
        create_account_label.setStyleSheet("font-size: 14px;")
        hbox.addWidget(create_account_label)

        self.register_link = QLabel("<a href='#'>SIGN UP</a>")
        self.register_link.setStyleSheet("font-size: 14px; color: #0078D7;")
        self.register_link.linkActivated.connect(self.go_to_register)
        hbox.addWidget(self.register_link)

        hbox.addStretch()
        layout.addLayout(hbox)

    @staticmethod
    def _add_spacer(layout: QVBoxLayout, width: int = 20, height: int = 20):
        """Add a spacer item to the layout."""
        spacer = QSpacerItem(width, height, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

    def _get_resource_path(self, resource_name: str) -> str:
        """Get the full path for a resource file."""
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, self.RESOURCES_PATH, resource_name)


    def _validate_login_input(self, email: str, password: str) -> bool:
        if not email or not password:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos.")
            return False
        return True


    def on_login_clicked(self):
        """Handle login button click event."""
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not self._validate_login_input(email, password):
            return

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user_id = self.user_repository.validar_usuario(email, password_hash)

        if user_id:
            self.logged_in_user_id = user_id
            QMessageBox.information(self, "Éxito", "Inicio de sesión exitoso.")
            self._open_menu(user_id)  # Pasa el ID a _open_menu
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Credenciales inválidas.")

    def _process_login(self, email: str, password: str):
        # Ya no se usa
        pass

    def _open_menu(self, user_id):
        """Open the main menu after successful login."""
        try:
            print(f"🔑 Abriendo el menú principal para ID de usuario: {user_id}")
            usuario = self.user_repository.obtener_usuario_por_id(user_id)  # Obtiene el OBJETO User
            if usuario is None:
                QMessageBox.critical(self, "Error", "Usuario no encontrado.")
                return

            self.menu_window = ModernTodoListApp(usuario=usuario)  # Pasa el OBJETO USUARIO
            self.menu_window.show()
            self.hide()
        except Exception as e:
            print(f"❌ Error al abrir el menú principal: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo abrir el menú: {e}")


    def go_to_register(self):

        if self.register_window:
            self.register_window.show()
            self.hide()
        else:
            print("Error: Register window not set.")

    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana."""
        if hasattr(self, 'db') and self.db:
            self.db.close()
        event.accept()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    from Register import Register  # Importa Register
    register_window = Register()  # Crea una instancia de Register.
    login_window = ModernLogin(register_window=register_window)
    login_window.show()
    sys.exit(app.exec())