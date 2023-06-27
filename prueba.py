from flask import Flask,render_template, request,redirect,url_for,session
from datetime import datetime,timedelta
from functools import wraps
import hashlib
import hmac
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Preceptor,Padre,Curso,Estudiante,Asistencia


def is_authenticated():
    return session.get('logged_in', False)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/cerrar_sesión')
def cerrar_sesión():
    session.clear()
    return redirect(url_for('index'))

@app.route('/',methods=['POST','GET'])
def index():
    if request.method== 'POST':
        rol=request.form.get('rol')
        if rol=='preceptor':
            preceptor_actual= Preceptor.query.filter_by(correo=request.form['correo']).first()
            if preceptor_actual is None:
                return render_template('index.html', error="El correo no está registrado")
            else:
                clave = request.form['password'].encode('utf-8')
                hashed_password = hashlib.md5(clave).hexdigest()
                verificacion = hmac.compare_digest(hashed_password, preceptor_actual.clave)
                if (verificacion):           
                    session['rol']='preceptor'           
                    session['idpreceptor']=preceptor_actual.id
                    session['logged_in'] = True
                    return redirect(url_for('funciones'))
                else:
                    return render_template('index.html', error="Contraseña incorrecta")
        elif rol=='padre':
            padre_actual= Padre.query.filter_by(correo= request.form['correo']).first()
            if padre_actual is None:
                return render_template('index.html', error="El correo no está registrado")
            else:
                clave = request.form['password'].encode('utf-8')
                hashed_password = hashlib.md5(clave).hexdigest()
                verificacion = hmac.compare_digest(hashed_password, padre_actual.clave)
                if (verificacion):
                    session['rol']='padre'    
                    session['idpadre']=padre_actual.id
                    session['logged_in'] = True                
                    return redirect(url_for('funciones'))
                else:
                    return render_template('funciones.html', error="Contraseña incorrecta")
    else:
        return render_template('index.html')