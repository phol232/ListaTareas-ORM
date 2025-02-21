import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout,
                             QSpacerItem, QSizePolicy, QMessageBox)
from PyQt6.QtGui import QFont, QIcon, QAction
from PyQt6.QtCore import Qt

class Register(QWidget):
    """
A simple Register window.  Crucially, it takes the login window
as an argument in its constructor.
"""

    WINDOW_TITLE = "Register"
    WINDOW_GEOMETRY = (100, 100, 400, 550)
    RESOURCES_PATH = "../Resources"  

    def __init__(self, login_window=None):  
        super().__init__()
        self.login_window = login_window  
        self.init_window()
        self.setup_ui_components()

    def init_window(self):
        """Initialize the main window properties."""
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setGeometry(*self.WINDOW_GEOMETRY)

    def setup_ui_components(self):
        """Set up all UI components and layouts."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self._setup_header_section(main_layout)
        self._setup_input_section(main_layout)
        self._setup_footer_section(main_layout)

        self.setLayout(main_layout)

    def _setup_header_section(self, layout: QVBoxLayout):
        """Header section (logo and title)."""
        self._add_logo(layout)
        self._add_spacer(layout, height=10)
        self._add_title(layout)
        self._add_spacer(layout, height=30)

    def _add_logo(self, layout: QVBoxLayout):
        """Add the logo."""
        logo_label = QLabel("🔵 ToDO-LIST")  
        logo_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

    def _add_title(self, layout: QVBoxLayout):
        title_label = QLabel("Create your Account")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

    def _setup_input_section(self, layout: QVBoxLayout):
        """Input fields."""
        self.fullname_input = self._create_input_field("Full Name", "icons8-user-24.png")
        self.email_input = self._create_input_field("Email", "icons8-email-24.png")
        self.password_input = self._create_input_field("Password", "icons8-password-24.png", is_password=True)

        layout.addWidget(self.fullname_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)

    def _create_input_field(self, placeholder: str, icon_name: str, is_password: bool = False) -> QLineEdit:
        """Creates an input field with an icon INSIDE, using QAction."""
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setStyleSheet("""
QLineEdit {
border: 1px solid #ccc;
padding: 10px;
padding-left: 15px;
border-radius: 5px;
font-size: 14px;
height: 30px;
}
        """)
        if is_password:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)

        icon_path = os.path.join(self.RESOURCES_PATH, icon_name)
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            icon_action = QAction(icon, "", input_field)  
            input_field.addAction(icon_action, QLineEdit.ActionPosition.LeadingPosition)
        else:
            print(f"Warning: Icon file not found: {icon_path}")
            
        return input_field

    def _setup_footer_section(self, layout: QVBoxLayout):
        """Footer (register button and login link)."""
        self._add_spacer(layout, height=30)
        self._add_register_button(layout)
        self._add_spacer(layout)
        self._add_login_link(layout)

    def _add_register_button(self, layout: QVBoxLayout):
        """Add the register button."""
        register_button = QPushButton("SIGN UP")
        register_button.setStyleSheet("""
QPushButton {
background-color: #0078D7;
color: white;
padding: 12px;
border-radius: 5px;
font-weight: bold;
font-size: 14px;
}
QPushButton:hover {
background-color: #005BB5;
}
        """)
        register_button.clicked.connect(self.register_user)
        layout.addWidget(register_button)

    def _add_login_link(self, layout: QVBoxLayout):
        """Add the 'Already have an account?' link."""
        hbox = QHBoxLayout()
        hbox.addStretch()  
        login_label = QLabel("Already have an account? ")
        login_label.setStyleSheet("font-size: 14px;")
        hbox.addWidget(login_label)

        self.login_link = QLabel("<a href='#'>Login</a>")  
        self.login_link.setStyleSheet("font-size: 14px; color: #0078D7;")
        self.login_link.linkActivated.connect(self.go_to_login)  
        hbox.addWidget(self.login_link)
        hbox.addStretch() 
        layout.addLayout(hbox)

    @staticmethod
    def _add_spacer(layout: QVBoxLayout, width: int = 20, height: int = 20):
        """Add a spacer item."""
        spacer = QSpacerItem(width, height, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

    def register_user(self):
        """Placeholder for registration logic."""
        QMessageBox.information(self, "Registration", "Registration successful! (Placeholder)")

    def go_to_login(self):

        if self.login_window:
            self.login_window.show()
            self.hide()
        else:
            print("Error: No login window provided.")

