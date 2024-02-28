#from candidato import create_app
#from candidato.vistas.vistas import VistaPing, VistaBorrar, VistaCandidatosPerfiles, VistaCandidato
#from candidato.modelos.modelos import db, Candidato, Estado
from flask_restful import Api
from flask_jwt_extended import JWTManager
from faker import Faker
import random
import os
from flask_cors import CORS

from flask import Flask
def create_app(config_name, settings_module='config.ProductionConfig'):
    app=Flask(__name__)
    app.config.from_object(settings_module)
    return app

"""def create_app(config_name):
    app=Flask(__name__)
    app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'Proyecto2023'
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

    if 'RDS_HOSTNAME' in os.environ:
        NAME=os.environ['RDS_DB_NAME']
        USER=os.environ['RDS_USERNAME']
        PASSWORD=os.environ['RDS_PASSWORD']
        HOST=os.environ['RDS_HOSTNAME']
        PORT=os.environ['RDS_PORT']
        app.config['SQLALCHEMY_DATABASE_URI']=f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:5432/CandidatosBD'      
    return app                                   """

settings_module = os.getenv('APP_SETTINGS_MODULE','config.ProductionConfig')
#settings_module='config.StagingConfig'
application = create_app('default', settings_module)
#application = create_app('default')
app_context=application.app_context()
app_context.push()



import enum
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from sqlalchemy import DateTime, Date
from sqlalchemy.sql import func

db = SQLAlchemy()

class Estado(enum.Enum):
    ACTIVO = 1
    INACTIVO = 2

class Nivel_Estudios(enum.Enum):
    PREGRADO = 1
    ESPECIALIZACION = 2
    MAESTRIA = 3
    DOCTORADO = 4
    DIPLOMADOS = 5
    CURSOS = 6

class Sexo(enum.Enum):
    MASCULINO = 1
    FEMENINO = 2

class Candidato(db.Model):
    __tablename__ = 'candidato'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombres = db.Column(db.Unicode(128), nullable=False, default='MISSING')
    apellidos = db.Column(db.Unicode(128), nullable=False, default='MISSING')
    documento = db.Column(db.Integer, nullable=False, unique=True)
    fecha_nac = db.Column(Date(), nullable=True)
    sexo = db.Column(db.Enum(Sexo), nullable=True, default=None)  
    email = db.Column(db.Unicode(128), nullable=False, unique=True)
    phone = db.Column(db.Unicode(128))
    pais = db.Column(db.Unicode(128))
    ciudad = db.Column(db.Unicode(128))
    direccion = db.Column(db.Unicode(128))
    imagen = db.Column(db.Unicode(256), nullable=True, default='', unique=False)
    idioma = db.Column(db.Unicode(128))
    num_perfil = db.Column(db.Integer, nullable=False, default=0, unique=False)
    is_active = db.Column(db.Boolean, default=True)
    estado = db.Column(db.Enum(Estado), nullable=False, default=Estado.ACTIVO)  
    id_usuario = db.Column(db.Integer, nullable=False, default=0, unique=True)

    def __init__(self, *args, **kw):
        super(Candidato, self).__init__(*args, **kw)

    def get_id(self):
        return self.id

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Candidato.query.get(id)

    @staticmethod
    def get_by_email(email):
        return Candidato.query.filter_by(email=email).first()

    @staticmethod
    def get_count():
        return Candidato.query.count()
    
    @staticmethod
    def get_by_idUser(idUser):
        return Candidato.query.filter_by(id_usuario=idUser).first()
    
    @staticmethod
    def getAll():
        return Candidato.query.all()
    
class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        else:
            return value.name #{'llave':value.name, 'valor':value.value} #{value.name}  #{'llave':value.name, 'valor':value.value}
    
class CandidatoSchema(SQLAlchemyAutoSchema):
    estado=EnumADiccionario(attribute=('estado'))
    sexo=EnumADiccionario(attribute=('sexo'))
    class Meta:
        model = Candidato
        include_relationships = True
        load_instance = True

candidato_schema = CandidatoSchema()


class Datos_Laborales(db.Model):
    __tablename__ = 'datos_laborales'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    num_cand = db.Column(db.Integer, nullable=False)

    empresa = db.Column(db.Unicode(128), nullable=False, default='MISSING')
    cargo = db.Column(db.Unicode(128), nullable=False, default='MISSING')
    funciones = db.Column(db.Unicode(128), nullable=False, default='MISSING')
    fecha_ing = db.Column(Date(), nullable=True)
    fecha_sal = db.Column(Date(), nullable=True)

    def __init__(self, *args, **kw):
        super(Datos_Laborales, self).__init__(*args, **kw)

    def get_id(self):
        return self.id

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Datos_Laborales.query.get(id)

 
class Datos_LaboralesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Datos_Laborales
        include_relationships = True
        load_instance = True

datos_laborales_schema = Datos_LaboralesSchema()



class Datos_Academicos(db.Model):
    __tablename__ = 'datos_academicos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    num_cand = db.Column(db.Integer, nullable=False)
    institucion = db.Column(db.Unicode(128), nullable=False, default='MISSING')
    titulo = db.Column(db.Unicode(128), nullable=False, default='MISSING')
    anio = db.Column(db.Integer, nullable=False, default=2023)
    nivel = db.Column(db.Enum(Nivel_Estudios), nullable=False, default=Nivel_Estudios.CURSOS)  

    def __init__(self, *args, **kw):
        super(Datos_Academicos, self).__init__(*args, **kw)

    def get_id(self):
        return self.id

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Datos_Academicos.query.get(id)

    @staticmethod
    def get_count():
        return Datos_Academicos.query.count()

    
class Datos_AcademicosSchema(SQLAlchemyAutoSchema):
    nivel=EnumADiccionario(attribute=('nivel'))
    class Meta:
        model = Datos_Academicos
        include_relationships = True
        load_instance = True

datos_academicos_schema = Datos_AcademicosSchema()

db.init_app(application)
db.create_all()

CORS(application)

from datetime import datetime
from datetime import timedelta
from dateutil import parser
import math
import random
import uuid
from flask import request, current_app
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
#from candidato.modelos.modelos import db, Candidato, CandidatoSchema, Estado
from sqlalchemy import desc, asc

import os
import requests
import json
from faker import Faker

from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token, verify_jwt_in_request
from flask_jwt_extended import get_jwt
from flask_jwt_extended.exceptions import NoAuthorizationError
from functools import wraps
from jwt import InvalidSignatureError, ExpiredSignatureError, InvalidTokenError

candidato_schema = CandidatoSchema()
access_token_expires = timedelta(minutes=120)

def authorization_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            print("Authorization Required")
            try:
                verify_jwt_in_request()  
                try:
                    req_headers = request.headers  #{"Authorization": f"Bearer {lst[1]}"}
                    roles= {"roles":["CANDIDATO","EMPLEADO_ABC"]}
                    r = requests.post(f"{current_app.config['HOST_PORT_AUTH']}/auth/me", headers=req_headers, json=roles)
                    if r.json().get("authorization") is None:
                        return {"Error:": "Autorizacion Negada por Autoridad. "}, 401
                    else:
                        lstTokens=request.path.split(sep='/')    
                        lstTokens[len(lstTokens)-1]
                        user_url=lstTokens[len(lstTokens)-1]
                        if r.json().get("id")==int(user_url):
                            return fn(*args, **kwargs)       
                        else:
                            return {"Error:": "Inconsistencia en la peticion"}, 401
                except Exception as inst:
                    print(type(inst))    # the exception instance
                    print(inst)
                    return {"Error:": "Usuario Desautorizado. No se pudo verificar con Autoridad."}, 401
            except ExpiredSignatureError:
                return {"Error:": "Token Expired"}, 401
            except InvalidSignatureError:
                return {"Error:": "Signature verification failed"}, 401
            except NoAuthorizationError:
                return {"Error:": "Missing JWT"}, 401
            except Exception as inst:
                print("excepcion")
                print(type(inst))    # the exception instance
                print(inst)
                return {"Error:": "Usuario desautorizado. Error General."}, 401
        return decorator
    return wrapper

def candidato_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()  
                claims = get_jwt()  #claims = get_jwt_claims()
                try:
                    print(claims)
                    if claims['MyUserType'] != 'CANDIDATO':
                        return {"Error:": "Usuario Desautorizado"}, 401
                    else:
                        return fn(*args, **kwargs)                
                except Exception as inst:
                   return {"Error:": "Usuario Desautorizado"}, 401
            except ExpiredSignatureError:
                return {"Error:": "Token Expired"}, 401
            except InvalidSignatureError:
                return {"Error:": "Signature verification failed"}, 401
            except NoAuthorizationError:
                return {"Error:": "Missing JWT"}, 401
            except Exception as inst:
                print("excepcion")
                print(type(inst))    # the exception instance
                print(inst)
                return {"Error:": "Usuario Desautorizado"}, 401
        return decorator
    return wrapper

class VistaCandidatoDetalleUsuario(Resource):
    def get(self, id_usuario):
        print("Consultar Detalle Candidato de un Usuario")
        try:
            candidato = Candidato.get_by_idUser(id_usuario)
            candidatoJSON = candidato_schema.dump(candidato)
        except Exception as inst:
            print(type(inst))    # the exception instance
            #print(inst)
            print("No se pudo obtener la informacion del Candidato.")
            return {"Mensaje: ":"Error: No se pudo obtener la informacion del Candidato."}, 50
        return candidatoJSON, 200


class VistaCandidatoUsuario(Resource):
    @authorization_required()
    def get(self, id_usuario):
        print("Consulta Candidato Usuario")
        try:
            candidato = Candidato.get_by_idUser(id_usuario)
            print(candidato)
            print(candidato.nombres)
        except Exception as inst:
            print("excepcion")
            print(type(inst))    # the exception instance
            print(inst)
            return {"Error:": "Error en el Servidor"}, 500
        return candidato_schema.dump(candidato), 200

class VistaBorrar(Resource):
    def delete(self):
        print("Borrando Datos.")
        lstCandidatos=Candidato.query.all()
        registros=0
        for c in lstCandidatos:
            try:
                db.session.delete(c)
                db.session.commit()
            except Exception as inst:
                db.session.rollback()
                print(type(inst))    # the exception instance
                #print(inst)
                print("registro no se pudo borrar.")
        return {"Mensaje":"registros borrados: "+str(registros)}, 200

class VistaCandidatos(Resource):
    def post(self):
        print("Creando Candidato")
        print(request.json)
        try:
            nc=Candidato()
            nc.nombres=request.json.get("nombres")
            nc.apellidos=request.json.get("apellidos")
            tempFecha=request.json.get("fecha_nac", "")
            if tempFecha!="":
                nc.fecha_nac=datetime.strptime(tempFecha, '%Y-%m-%d')
            nc.documento=request.json.get("documento")
            candidato = Candidato.query.filter(Candidato.documento == nc.documento).first()
            if candidato is not None:
               return {"mensaje": "Candidato no se pudo crear: El documento suministrado ya existe."}, 400
            nc.email=request.json.get("email")
            candidato = Candidato.query.filter(Candidato.email == nc.email).first()
            if candidato is not None:
               return {"mensaje": "Candidato no se pudo crear: El e-mail suministrado ya existe."}, 400
            nc.phone=request.json.get("phone")
            nc.ciudad=request.json.get("ciudad")
            nc.direccion=request.json.get("direccion")
            nc.num_perfil=request.json.get("num_perfil")
            nc.id_usuario=request.json.get("id_usuario")
            candidato = Candidato.query.filter(Candidato.id_usuario == nc.id_usuario).first()
            if candidato is not None:
               return {"mensaje": "Candidato no se pudo crear: El usuario suministrado ya existe."}, 400
            nc.imagen=request.json.get("imagen", "")
            db.session.add(nc)
            db.session.commit()
            return {"Candidato":candidato_schema.dump(nc)}, 201
        except Exception as inst:
            db.session.rollback()
            print(type(inst))    # the exception instance
            print(inst)
            print("Candidato no se pudo crear.")
            return {"Mensaje: ":"Error: Candidato no se pudo crear."+str(type(inst))}, 500
    
class VistaCandidatosParcial(Resource):
    def post(self):
        print("Obteniendo candidatos")
        print("json: ")
        print(request.json)
        max=request.json.get("max", 50)
        num_pag=request.json.get("num_pag", 1)
        order=request.json.get("order", "ASC")

        nombres=request.json.get("nombres", "")
        apellidos=request.json.get("apellidos", "")
        candidato=request.json.get("candidato", "")
        ciudad=request.json.get("ciudad", "")
        fechaInicio=request.json.get("inicio", "")
        fechaFin=request.json.get("fin", "")
        print("Inicio")
        print(fechaInicio)
        print("Fin")
        print(fechaFin)
        if fechaInicio==None or fechaInicio=='':
            fecha_inicio = datetime.strptime('1970-01-01',"%Y-%m-%d")
        if fechaFin==None or fechaFin=='':
            fecha_fin = datetime.strptime('3000-01-01',"%Y-%m-%d")
        if fechaInicio!=None and fechaFin!=None and fechaInicio!='' and fechaFin!='':
            fecha_inicio = parser.parse(fechaInicio)
            fecha_fin = parser.parse(fechaFin)
            #fecha_fin=fecha_fin+timedelta(hours=23)
            #fecha_fin=fecha_fin+timedelta(minutes=59)
        print("fecha_inicio")
        print(fecha_inicio)
        print("fecha_fin")
        print(fecha_fin)

        if (fechaInicio==None or fechaInicio=='') and (fechaFin==None or fechaFin==''):
            print("SINFECHAS")
            numCandidatos=db.session.query(Candidato.id, 
                                        Candidato.id_usuario,
                                        (Candidato.apellidos+' '+Candidato.nombres).label('candidato'),
                                        Candidato.documento,
                                        Candidato.fecha_nac,
                                        Candidato.direccion,
                                        Candidato.ciudad,
                                        Candidato.email,
                                        Candidato.phone,
                                        Candidato.num_perfil,
                                        Candidato.imagen,
                                        Candidato.estado,
                            ).filter(Candidato.apellidos.ilike(f'%{apellidos}%')
                            ).filter(Candidato.nombres.ilike(f'%{nombres}%')
                            ).filter(Candidato.ciudad.ilike(f'%{ciudad}%')
                            ).count()
            lstCandidatos=db.session.query(Candidato.id, 
                                        Candidato.id_usuario,
                                        (Candidato.apellidos+' '+Candidato.nombres).label('candidato'),
                                        Candidato.documento,
                                        Candidato.fecha_nac,
                                        Candidato.direccion,
                                        Candidato.ciudad,
                                        Candidato.email,
                                        Candidato.phone,
                                        Candidato.num_perfil,
                                        Candidato.imagen,
                                        Candidato.estado,
                            ).filter(Candidato.apellidos.ilike(f'%{apellidos}%')
                            ).filter(Candidato.nombres.ilike(f'%{nombres}%')
                            ).filter(Candidato.ciudad.ilike(f'%{ciudad}%')
                            ).order_by(Candidato.apellidos.asc(), Candidato.nombres.asc()
                            ).paginate(page=num_pag, per_page=max, error_out=False)
        else:
            print("CONFECHAS")
            numCandidatos=db.session.query(Candidato.id, 
                                        Candidato.id_usuario,
                                        (Candidato.apellidos+' '+Candidato.nombres).label('candidato'),
                                        Candidato.documento,
                                        Candidato.fecha_nac,
                                        Candidato.direccion,
                                        Candidato.ciudad,
                                        Candidato.email,
                                        Candidato.phone,
                                        Candidato.num_perfil,
                                        Candidato.imagen,
                                        Candidato.estado,
                            ).filter(Candidato.apellidos.ilike(f'%{apellidos}%')
                            ).filter(Candidato.nombres.ilike(f'%{nombres}%')
                            ).filter(Candidato.ciudad.ilike(f'%{ciudad}%')
                            ).filter(Candidato.fecha_nac>=fecha_inicio 
                            ).filter(Candidato.fecha_nac<=fecha_fin
                            ).count()
            lstCandidatos=db.session.query(Candidato.id, 
                                        Candidato.id_usuario,
                                        (Candidato.apellidos+' '+Candidato.nombres).label('candidato'),
                                        Candidato.documento,
                                        Candidato.fecha_nac,
                                        Candidato.direccion,
                                        Candidato.ciudad,
                                        Candidato.email,
                                        Candidato.phone,
                                        Candidato.num_perfil,
                                        Candidato.imagen,
                                        Candidato.estado,
                            ).filter(Candidato.apellidos.ilike(f'%{apellidos}%')
                            ).filter(Candidato.nombres.ilike(f'%{nombres}%')
                            ).filter(Candidato.ciudad.ilike(f'%{ciudad}%')
                            ).filter(Candidato.fecha_nac>=fecha_inicio 
                            ).filter(Candidato.fecha_nac<=fecha_fin
                            ).order_by(Candidato.apellidos.asc(), Candidato.nombres.asc()
                            ).paginate(page=num_pag, per_page=max, error_out=False)
   
        #print("Lista de Candidatos")
        #for c in lstCandidatos:
        #    print(c)
        data = []
        i=0
        for c in lstCandidatos:
            i=i+1
            ev_data = {
                'Num': (num_pag-1)*max + i,
                'id': c.id,
                'id_usuario': c.id_usuario,
                'candidato': c.candidato,
                'documento': c.documento,
                'fecha_nac': c.fecha_nac.isoformat() if c.fecha_nac else '',
                'direccion': c.direccion,
                'ciudad': c.ciudad,
                'email': c.email,
                'phone': c.phone,
                'estado': c.estado.name if c.estado else '',
                'num_perfil': c.num_perfil,
                'imagen': c.imagen,
            }
            data.append(ev_data)
        print("totalCount")
        print(numCandidatos)
        return {'Candidatos': data, 'totalCount': numCandidatos}, 200

class VistaCandidatosAsignaPerfil(Resource):
    def post(self, id_cand):
        print("Asigna perfil a Candidato")
        print('json')
        print(request.json)
        id_perfil=request.json.get("id_perfil")
        try:
            candidato = Candidato.query.get_or_404(id_cand)
            candidato.num_perfil=id_perfil
            db.session.add(candidato)
            db.session.commit()
            return candidato_schema.dump(candidato)
        except Exception as inst:
            db.session.rollback()
            print(type(inst))    # the exception instance
            #print(inst)
            print("No se pudo actualizar el perfil del candidato del candidato.")
            return {"Mensaje: ":"Error: No se pudo actualizar el perfil del candidato del candidato."}, 200

class VistaCandidato(Resource):
    def get(self, id_cand):
        print("Consultar Candidato")
        try:
            candidato = Candidato.query.get_or_404(id_cand)
            return candidato_schema.dump(candidato)
        except Exception as inst:
            print(type(inst))    # the exception instance
            #print(inst)
            print("No se pudo obtener la informacion del candidato.")
            return {"Mensaje: ":"Error: No se pudo obtener la informacion del candidato."}, 200

class VistaListaCandidatos(Resource):
    def post(self):
        print("Consulta Lista de Candidatos")
        lstCandidatos=request.get_json().get("lstCandidatos", None)
        if lstCandidatos is not None and len(lstCandidatos)!=0:
            lstDetCandidatos=[]
            for c in lstCandidatos:
                candidato=Candidato.get_by_id(c)
                if candidato is not None:
                    candidatoJSON=candidato_schema.dump(candidato)
                    lstDetCandidatos.append(candidatoJSON)
            return {"lstDetCandidatos":lstDetCandidatos}, 200
        else:
            return {"Mensaje":"Falta la lista de candidatos.", "lstDetCandidatos":[]}, 400

class VistaCandidatoLike(Resource):
    def post(self):
        print("Seleccion de candidatos segun like")
        patron=request.json.get("patron","")
        print("patron")
        print(patron)
        lstCand = db.session.query(Candidato.id, (Candidato.nombres+' '+Candidato.apellidos).label('nom_cand')).filter((Candidato.nombres+' '+Candidato.apellidos).ilike(f'%{patron}%')).order_by(asc(Candidato.id)).all()
        print(lstCand)
        data = []
        lstNumCand = []
        for c in lstCand:
            lstNumCand.append(c.id)
            cand_data = {
                'id_cand': c.id,
                'nom_cand': c.nom_cand
            }
            data.append(cand_data)
        return {'lstNumCandidatos': lstNumCand, 'totalCount': len(lstNumCand)}, 200

class VistaCandidatosPerfiles(Resource):
    def post(self):
        print("Seleccion de candidatos segun perfiles")
        lstPerfiles=request.json.get("lstPerfiles")
        print(lstPerfiles)
        lstCandidatos = db.session.query(Candidato.id, Candidato.nombres, Candidato.apellidos,  Candidato.direccion,
                                         Candidato.email, Candidato.phone, Candidato.ciudad, Candidato.num_perfil,
                                         Candidato.fecha_nac, Candidato.imagen).filter(Candidato.num_perfil.in_(lstPerfiles)).order_by(asc(Candidato.num_perfil)).all()
        data = []
        for c in lstCandidatos:
            cand_data = {
                'id_cand': c.id,
                'nombres': c.nombres,
                'apellidos': c.apellidos,
                'direccion': c.direccion,
                'email': c.email,
                'phone': c.phone,
                'ciudad': c.ciudad,
                'id_perfil': c.num_perfil,
                'fecha_nac': c.fecha_nac.strftime('%Y-%m-%d'),
                'imagen': c.imagen
            }
            data.append(cand_data)

        #for c in lstCandidatos:
        #    cand_data = {
        #        'id_cand': c.id,
        #        'nombres': c.nombres,
        #        'apellidos': c.apellidos,
        #        'direccion': c.direccion,
        #        'email': c.email,
        #        'phone': c.phone,
        #        'ciudad': c.ciudad,
        #        'id_perfil': c.num_perfil
        #    }
        #    data.append(cand_data)
        return {'Candidatos': data, 'totalCount': len(data)}, 200


class VistaRaiz(Resource):
    def get(self):
        print("Hola")
        return {"Mensaje":"Hola, Bienvenido De Nuevo v3.3 Inmutable"}, 200

class VistaPing(Resource):
    def get(self):
        print("pong")
        return {"Mensaje":"Pong Candidato v1"}, 200

class VistaEnv(Resource):
    def get(self):
        print("Environment")
        return {
            "RDS_DB_NAME":os.environ['RDS_DB_NAME'],
            "RDS_USERNAME":os.environ['RDS_USERNAME'],
            "RDS_PASSWORD":os.environ['RDS_PASSWORD'],
            "RDS_HOSTNAME":os.environ['RDS_HOSTNAME'],
            "RDS_PORT":os.environ['RDS_PORT'],
            "URL_DATABASE":application.config['SQLALCHEMY_DATABASE_URI'],
        }, 200

api = Api(application)
api.add_resource(VistaRaiz, '/')
api.add_resource(VistaEnv, '/env')
api.add_resource(VistaBorrar, '/candidatos/borrar')
api.add_resource(VistaCandidatosPerfiles, '/candidatos/perfiles')
api.add_resource(VistaCandidato, '/candidato/<int:id_cand>')
api.add_resource(VistaCandidatoUsuario, '/micandidato/<int:id_usuario>')
api.add_resource(VistaPing, '/candidato/ping')
api.add_resource(VistaListaCandidatos, '/candidatos/lista')
api.add_resource(VistaCandidatos, '/candidatos')
api.add_resource(VistaCandidatoDetalleUsuario, '/candidatoUsuarioDetalle/<int:id_usuario>')
api.add_resource(VistaCandidatoLike, '/candidatos/like')
api.add_resource(VistaCandidatosParcial, '/candidatos/parcial')
api.add_resource(VistaCandidatosAsignaPerfil, '/candidatos/asignaPerfil/<int:id_cand>')


jwt = JWTManager(application)

print("From application.py")
print(settings_module)

if Candidato.get_count()==0:
    print("Creando Candidatos.")
    regT=0
    with open("./candidatos.txt") as archivo:
        for linea in archivo:
            try:
                campos=linea.split(sep='|')
                cn=Candidato()
                cn.nombres=campos[0]
                cn.apellidos=campos[1]
                cn.documento=int(campos[2])
                cn.fecha_nac=datetime.strptime(campos[3], '%Y-%m-%d')
                #if campos[4]=='Male':
                #    cn.sexo=Sexo.MASCULINO
                #elif campos[4]=='Female':
                #    cn.sexo=Sexo.FEMENINO
                #else:
                #    cn.sexo=None
                cn.sexo=Sexo.MASCULINO if campos[4]=='Male' else Sexo.FEMENINO
                cn.email=campos[5]
                cn.phone=campos[6]
                cn.ciudad=campos[7]
                cn.direccion=campos[8]
                cn.pais=campos[9]
                cn.idioma=campos[10]
                cn.imagen=campos[11]
                cn.estado=Estado.ACTIVO
                cn.num_perfil=(regT+1) % 4000  #random.randint(1, 300)
                db.session.add(cn)
                db.session.commit()
                cn.id_usuario=cn.id
                db.session.add(cn)
                db.session.commit()
                regT=regT+1
                print("===================")
                print(regT)
            except Exception as inst:
                db.session.rollback()
                print(type(inst))    # the exception instance
                print(inst)
                print("Candidato no se pudo crear.")

if False:
    host=f"{application.config['HOST_PORT_PERFILES']}"
    headers={} #headers = {"Authorization": f"Bearer {os.environ.get('TRUE_NATIVE_TOKEN')}"}
    with open("./pruebas.txt", "xt+") as archivo:
        #id_cand, id_habil, nota, resultado
        for i in range(33000):         
            c=Candidato.get_by_id(i+1)
            if c.num_perfil!=0:
                url=host+'/perfil/'+str(c.num_perfil)
                response = requests.get(url=url, headers=headers, timeout=5000)
                lstHabils=response.json().get("Habilidades")
                for h in lstHabils:
                    if h["tipo_habil"]=="TECNICA":
                        linea=str(c.id)+"|"+str(h["id_habil"])+"|"+str(random.randint(65, 100))+"|"+"APROBADO"+"\n"
                        print(linea)
                        archivo.write(linea)
        archivo.close()    


if Candidato.get_count()==0 and False:
    faker=Faker(['es_CO'])
    registros=0
    for i in range(500):
        try:
            cn=Candidato()
            cn.nombres=faker.first_name()
            cn.apellidos=faker.last_name()
            cn.documento=faker.unique.random_int(min=1000000, max=2000000000) 
            cn.direccion=faker.street_address()
            cn.ciudad=faker.city()
            cn.email=faker.email()
            cn.phone=faker.phone_number()
            cn.fecha_nac=faker.date_between(start_date= "-80y" ,end_date= "-18y" )
            cn.estado=Estado.ACTIVO
            cn.num_perfil=(registros+1) % 250  #random.randint(1, 300)
            cn.imagen = 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fes.wikipedia.org%2Fwiki%2FUsuario_%2528inform%25C3%25A1tica%2529&psig=AOvVaw0dRqR7bAL3F4rog29S7HWH&ust=1699224620965000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCJDRmpG3q4IDFQAAAAAdAAAAABAJ'
            db.session.add(cn)
            db.session.commit()
            cn.id_usuario=cn.id
            db.session.add(cn)
            db.session.commit()
            registros=registros+1
        except Exception as inst:
            db.session.rollback()
            print(type(inst))    # the exception instance
            print(inst)
            print("registro no se pudo guardar.")
    
    faker=Faker(['en_US'])
    for i in range(300):
        try:
            cn=Candidato()
            cn.nombres=faker.first_name()
            cn.apellidos=faker.last_name()
            cn.documento=faker.unique.random_int(min=1000000, max=2000000000) 
            cn.direccion=faker.street_address()
            cn.ciudad=faker.city()
            cn.email=faker.email()
            cn.phone=faker.phone_number()
            cn.fecha_nac=faker.date_between(start_date= "-80y" ,end_date= "-18y" )
            cn.estado=Estado.ACTIVO
            cn.num_perfil=(registros+1) % 250  #random.randint(1, 300)
            cn.imagen = 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fes.wikipedia.org%2Fwiki%2FUsuario_%2528inform%25C3%25A1tica%2529&psig=AOvVaw0dRqR7bAL3F4rog29S7HWH&ust=1699224620965000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCJDRmpG3q4IDFQAAAAAdAAAAABAJ'
            db.session.add(cn)
            db.session.commit()
            cn.id_usuario=cn.id
            db.session.add(cn)
            db.session.commit()
            registros=registros+1
        except Exception as inst:
            db.session.rollback()
            print(type(inst))    # the exception instance
            #print(inst)
            print("registro no se pudo guardar.")
    
    faker=Faker(['it_IT'])
    for i in range(200):
        try:
            cn=Candidato()
            cn.nombres=faker.first_name()
            cn.apellidos=faker.last_name()
            cn.documento=faker.unique.random_int(min=1000000, max=2000000000) 
            cn.direccion=faker.street_address()
            cn.ciudad=faker.city()
            cn.email=faker.email()
            cn.phone=faker.phone_number()
            cn.fecha_nac=faker.date_between(start_date= "-80y" ,end_date= "-18y" )
            cn.estado=Estado.ACTIVO
            cn.num_perfil=(registros+1) % 250  #random.randint(1, 300)
            cn.imagen = 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fes.wikipedia.org%2Fwiki%2FUsuario_%2528inform%25C3%25A1tica%2529&psig=AOvVaw0dRqR7bAL3F4rog29S7HWH&ust=1699224620965000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCJDRmpG3q4IDFQAAAAAdAAAAABAJ'
            db.session.add(cn)
            db.session.commit()
            cn.id_usuario=cn.id
            db.session.add(cn)
            db.session.commit()            
            registros=registros+1
        except Exception as inst:
            db.session.rollback()
            print(type(inst))    # the exception instance
            #print(inst)
            print("registro no se pudo guardar.")

#if __name__ == "__main__":
#    application.run(port = 5000, debug = True)