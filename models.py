from __main__ import app
from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy(app)
class Preceptor (db.Model):
    __tablename__='preceptor'
    id = db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(50),nullable=False)
    apellido=db.Column(db.String(50),nullable=False)
    correo=db.Column(db.String(120),unique=True, nullable=False)
    clave=db.Column(db.String(50), nullable=False)
    curso=db.relationship('Curso', backref='preceptor')

class Padre (db.Model):
    __tablename__='padre'
    id = db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(50),nullable=False)
    apellido=db.Column(db.String(50),nullable=False)
    correo=db.Column(db.String(120),unique=True, nullable=False)
    clave=db.Column(db.String(120), nullable=False)
    estudiante=db.relationship('Estudiante',backref='padre')

class Estudiante (db.Model):
    __tablename__='estudiante'
    id = db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(50),nullable=False)
    apellido=db.Column(db.String(50),nullable=False)
    dni=db.Column(db.String(50),nullable=False)
    idcurso=db.Column(db.Integer, db.ForeignKey('curso.id'))
    idpadre=db.Column(db.Integer, db.ForeignKey('padre.id'))
    asistencia=db.relationship('Asistencia',backref='estudiante')

class Curso (db.Model):
    __tablename__='curso'
    id = db.Column(db.Integer, primary_key=True)
    anio=db.Column(db.Integer, nullable=False)
    division=db.Column(db.Integer, nullable=False)
    idpreceptor=db.Column(db.Integer, db.ForeignKey('preceptor.id'))
    estudiante=db.relationship('Estudiante',backref='curso')
    asistencia=db.relationship('Asistencia',backref='curso')

class Asistencia (db.Model):
    __tablename__='asistencia'
    id=db.Column(db.Integer, primary_key=True)
    fecha=db.Column(db.String(30), nullable=False)
    codigoclase=db.Column(db.Integer,db.ForeignKey('curso.id'))
    asistio=db.Column(db.String(5), nullable=False)
    justificacion=db.Column(db.String(50))
    idestudiante=db.Column(db.Integer,db.ForeignKey('estudiante.id'))