from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from src.Conexion.Tablas import Categoria

class CategoriaRepository:
    def __init__(self, session: Session):
        self.session = session

    def generar_id_categoria(self):
        ultima_categoria = self.session.query(Categoria.idCat).order_by(desc(Categoria.idCat)).first()

        if ultima_categoria and ultima_categoria[0].startswith('CAT-'):
            ultimo_numero = int(ultima_categoria[0].split('-')[1])
            nuevo_id = f'CAT-{ultimo_numero + 1:03d}'
        else:
            nuevo_id = 'CAT-001'

        return nuevo_id

    def crear_categoria(self, nombre: str):

        existe = self.session.query(Categoria).filter(func.lower(Categoria.nombre) == func.lower(nombre)).first()
        if existe:
            return None

        nuevo_id = self.generar_id_categoria()
        categoria = Categoria(idCat=nuevo_id, nombre=nombre)
        self.session.add(categoria)
        self.session.commit()
        self.session.refresh(categoria) 
        return categoria

    def obtener_categoria_por_nombre(self, nombre:str):

        return self.session.query(Categoria).filter(func.lower(Categoria.nombre) == func.lower(nombre)).first()

    def obtener_categoria_por_id(self, id_cat: str):

        return self.session.query(Categoria).filter(Categoria.idCat == id_cat).first()


    def listar_categorias(self):

        return self.session.query(Categoria).all()

    def eliminar_categoria(self, id_cat):

        categoria = self.session.query(Categoria).filter_by(idCat=id_cat).first()
        if categoria:
            self.session.delete(categoria)
            self.session.commit()
            return True
        return False

    def actualizar_categoria(self, id_cat:str, nombre: str = None):

        categoria = self.session.query(Categoria).filter(Categoria.idCat == id_cat).first()

        if not categoria:
            return False

        if nombre:
            categoria.nombre = nombre

        self.session.commit()
        self.session.refresh(categoria)
        return True
