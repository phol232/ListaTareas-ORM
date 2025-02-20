from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text  # Import ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum  # Importa enum
from src.Conexion.BaseDatos import Base

# Enum para el estado de la notificación
class NotificationStatus(str, enum.Enum): # Usar str como base
    UNREAD = 'Unread'
    READ = 'Read'

# Modelo de Usuario
class User(Base):
    __tablename__ = 'users'

    id = Column(String(12), primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    tareas = relationship('Tarea', back_populates='user', cascade="all, delete")
    notifications = relationship('Notification', back_populates='user', cascade="all, delete")

# Modelo de Categoría
class Categoria(Base):
    __tablename__ = 'categorias'

    idCat = Column(String(12), primary_key=True, nullable=False)  # String para el ID
    nombre = Column(String(20), nullable=False, unique=True)  # Importante: unique=True
    fecha = Column(DateTime, default=datetime.utcnow)

    tareas = relationship('Tarea', back_populates='categoria_obj', cascade="all, delete") # Cambio en back_populates

# Modelo de Tarea
class Tarea(Base):
    __tablename__ = 'tareas'

    idTarea = Column(String(12), primary_key=True, nullable=False)
    id_usuario = Column(String(12), ForeignKey('users.id'), nullable=False)  # ForeignKey a User
    titulo = Column(String(120), nullable=False)  # Aumenté la longitud
    descripcion = Column(String(500))  # Usar Text es mejor, pero String con longitud suficiente vale.
    id_categoria = Column(String(12), ForeignKey('categorias.idCat'), nullable=True)  # ForeignKey a Categoria, permite nulos
    prioridad = Column(String(255), nullable=False)  # String, NO Enum
    estado = Column(String(255), nullable=False)  # String, NO Enum
    fecha = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='tareas')
    categoria_obj = relationship('Categoria', back_populates='tareas') # Cambio en el nombre.

# Modelo de Notificación
class Notification(Base):
    __tablename__ = 'notifications'

    idNot = Column(String(12), primary_key=True, nullable=False)
    user_id = Column(String(12), ForeignKey('users.id'), nullable=False)
    task_id = Column(String(12), ForeignKey('tareas.idTarea'), nullable=False)  # ForeignKey a Tarea
    message = Column(Text, nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.UNREAD)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='notifications')
    tarea = relationship('Tarea')  # No necesitas back_populates aquí