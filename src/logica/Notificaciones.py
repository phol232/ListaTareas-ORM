from sqlalchemy.orm import Session
from sqlalchemy import asc
from src.Conexion.Tablas import Notification, NotificationStatus

class NotificacionRepository:
    def __init__(self, session: Session):
        self.session = session

    def listar_notificaciones(self):
      
        return self.session.query(Notification).order_by(asc(Notification.created_at)).all()

    def marcar_como_leido(self, idNot: str) -> bool:

        notif = self.session.query(Notification).filter_by(idNot=idNot).first()
        if notif:
            notif.status = NotificationStatus.READ
            self.session.commit()
            return True
        return False