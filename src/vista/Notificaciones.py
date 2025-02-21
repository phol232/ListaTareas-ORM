import sys
from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QWidget, QApplication
)
from PyQt6.QtCore import Qt
from src.logica.Notificaciones import NotificacionRepository, NotificationStatus
from src.Conexion.BaseDatos import get_db

def time_since(created_at: datetime) -> str:
    now = datetime.utcnow()
    diff = now - created_at
    seconds = diff.total_seconds()

    if seconds < 60:
        return f"hace {int(seconds)} seg"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"hace {minutes} min"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"hace {hours} h"
    else:
        days = int(seconds / 86400)
        return f"hace {days} d"

class NotificationItemWidget(QWidget):
    def __init__(self, notif, repo: NotificacionRepository, parent=None):
        super().__init__(parent)
        self.notif = notif
        self.repo = repo
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        tiempo_transcurrido = time_since(self.notif.created_at) if self.notif.created_at else "Sin fecha"
        self.label = QLabel(f"{self.notif.message} - {tiempo_transcurrido}", self)
        layout.addWidget(self.label)

        self.btnMarcarLeido = QPushButton(self)
        self.btnMarcarLeido.setFixedSize(120, 25)
        self.btnMarcarLeido.setStyleSheet("""
QPushButton {
font-size: 10px;
padding: 2px;
background-color: #FFD699;
color: black;
border: none;
border-radius: 3px;
}
QPushButton:disabled {
background-color: #FFD699;
}
        """)

        if self.notif.status == NotificationStatus.UNREAD:
            self.btnMarcarLeido.setText("Marcar como leído")
            self.btnMarcarLeido.setEnabled(True)
            self.btnMarcarLeido.clicked.connect(self.marcar_como_leido)
        else:
            self.btnMarcarLeido.setText("Leído")
            self.btnMarcarLeido.setEnabled(False)
            self.label.setStyleSheet("color: blue;")

        layout.addWidget(self.btnMarcarLeido)

    def marcar_como_leido(self):
        if self.repo.marcar_como_leido(self.notif.idNot):
            self.notif.status = NotificationStatus.READ
            self.label.setStyleSheet("color: blue;")
            self.btnMarcarLeido.setText("Leído")
            self.btnMarcarLeido.setEnabled(False)

class NotificacionesDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.repo = NotificacionRepository(session)
        self.setWindowTitle("")  # Se elimina el título
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(440, 300)
        self.setStyleSheet("QDialog { border: 2px solid blue; }")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.listWidget = QListWidget(self)
        layout.addWidget(self.listWidget)
        closeButton = QPushButton("Cerrar", self)
        closeButton.clicked.connect(self.close)
        layout.addWidget(closeButton)
        self.cargar_notificaciones()

    def cargar_notificaciones(self):
        self.listWidget.clear()
        notificaciones = self.repo.listar_notificaciones()
        for notif in notificaciones:
            item = QListWidgetItem(self.listWidget)
            widget = NotificationItemWidget(notif, self.repo, parent=self)
            item.setSizeHint(widget.sizeHint())
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    session = next(get_db())
    dialog = NotificacionesDialog(session)
    dialog.exec()