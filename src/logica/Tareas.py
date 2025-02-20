from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from src.Conexion.Tablas import Tarea, Categoria, User


class TareaRepository:
    def __init__(self, session: Session):
        self.session = session

    def generar_id_tarea(self):
        with self.session.begin_nested():
            ultima_tarea = self.session.query(Tarea.idTarea).order_by(desc(Tarea.idTarea)).with_for_update().first()
            if ultima_tarea and ultima_tarea[0].startswith('TAR-'):
                ultimo_numero = int(ultima_tarea[0].split('-')[1])
                nuevo_id = f'TAR-{ultimo_numero + 1:03d}'
            else:
                nuevo_id = 'TAR-001'
            return nuevo_id

    def crear_tarea(self, user_id: str, titulo: str, descripcion: str, categoria: str, prioridad: str, estado: str, fecha: str):
        nuevo_id = self.generar_id_tarea()  # Generate ID *in Python*

        # Buscar la categoría por nombre.
        categoria_obj = self.session.query(Categoria).filter(func.lower(Categoria.nombre) == func.lower(categoria)).first()
        if not categoria_obj:
            raise ValueError(f"Categoría '{categoria}' no encontrada.")

        tarea = Tarea(
            idTarea=nuevo_id,  #  <--  USE THE GENERATED ID
            titulo=titulo,
            descripcion=descripcion,
            prioridad=prioridad,
            estado=estado,
            fecha=fecha,
            id_usuario=user_id,
            id_categoria=categoria_obj.idCat
        )
        self.session.add(tarea)
        self.session.commit()
        self.session.refresh(tarea)
        return tarea

    def obtener_tarea_por_id(self, tarea_id: str):
        return self.session.query(Tarea).filter_by(idTarea=tarea_id).first()

    def obtener_tareas_de_usuario(self, user_id: str):
        return self.session.query(Tarea).filter_by(id_usuario=user_id).all()

    def actualizar_tarea(self, tarea_id: str, titulo: str = None, descripcion: str = None,
                         categoria: str = None, prioridad: str = None, estado: str = None, fecha: str = None):
        tarea = self.session.query(Tarea).get(tarea_id)
        if not tarea:
            return False

        if titulo:
            tarea.titulo = titulo
        if descripcion:
            tarea.descripcion = descripcion
        if categoria:
            categoria_obj = self.session.query(Categoria).filter(func.lower(Categoria.nombre) == func.lower(categoria)).first()
            if not categoria_obj:
                raise ValueError(f"Categoría '{categoria}' no encontrada.")
            tarea.id_categoria = categoria_obj.idCat

        if prioridad:
            tarea.prioridad = prioridad
        if estado:
            tarea.estado = estado
        if fecha:
            tarea.fecha = fecha

        self.session.commit()
        self.session.refresh(tarea)
        return True

    def eliminar_tarea(self, tarea_id: str):
        tarea = self.session.query(Tarea).filter_by(idTarea=tarea_id).first()
        if tarea:
            self.session.delete(tarea)
            self.session.commit()
            return True
        return False

    def listar_tareas_por_prioridad(self, prioridad: str):
        prioridad_lower = prioridad.lower()
        if prioridad_lower not in ("alta", "media", "baja"):
            raise ValueError("Prioridad inválida. Debe ser 'Alta', 'Media' o 'Baja'.")
        return self.session.query(Tarea).filter(func.lower(Tarea.prioridad) == prioridad_lower).all()

    def buscar_tareas(self, categoria: str = None, estado: str = None):
        query = self.session.query(Tarea)

        if categoria:
            query = query.join(Categoria).filter(func.lower(Categoria.nombre) == categoria.lower())
        if estado:
            query = query.filter(func.lower(Tarea.estado) == estado.lower())

        return query.all()