from flask import Flask,render_template, request,redirect,url_for,session
from functools import wraps
import hashlib
import hmac

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Preceptor,Padre,Curso,Asistencia


def is_authenticated():
    return session.get('logged_in', False)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def preceptor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session['rol']!='preceptor':
            return redirect(url_for('funcioneserror',error='No tiene los permisos necesarios para ingresar a esa opción'))
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

@app.route('/funciones/')
@login_required
def funciones():
    return render_template('funciones.html',rol=session.get('rol'))

@app.route('/funciones/<error>')
@login_required
def funcioneserror(error):
    return render_template('funciones.html',rol=session.get('rol'),error=error)

@app.route('/registrar_asistencia',methods=['GET','POST'])
@login_required
@preceptor_required
def registrar_asistencia():
    preceptor_id=session.get('idpreceptor')
    if preceptor_id:
        preceptor= Preceptor.query.get(preceptor_id)
        if Preceptor:
            if request.method == 'POST': 
                fecha_selec=request.form['fechas']
                curso_selec=request.form['cursos']
                clase=request.form['clase']
                return redirect(url_for('guardar_asistencia',fecha_selec=fecha_selec,curso_selec=curso_selec,clase=clase))
            else:
                return render_template('asistencia.html',cursos = preceptor.curso, curso_seleccionado = None) 
            
@app.route('/registrar_asistencia/<fecha_selec>/<curso_selec>/<clase>',methods=['GET','POST'])
@login_required
@preceptor_required
def guardar_asistencia(fecha_selec,curso_selec,clase):
    curso= Curso.query.get(curso_selec)
    estudiantes = sorted(curso.estudiante, key=lambda estudiante: (estudiante.apellido, estudiante.nombre))
    asistio=[]
    if request.method== 'POST':
        for estudiante in curso.estudiante:
            asistencia = request.form.get(f'asistio{estudiante.id}')
            asistio.append(asistencia)
        justificacion=request.form.getlist('justificacion[]')
        for i, estudiante in enumerate(estudiantes):
            asistencia_estudiante = Asistencia()
            asistencia_estudiante.fecha=fecha_selec
            asistencia_estudiante.codigoclase=clase
            asistencia_estudiante.asistio=asistio[i]
            asistencia_estudiante.justificacion=justificacion[i]
            asistencia_estudiante.idestudiante=estudiante.id
            db.session.add(asistencia_estudiante)
            db.session.commit()
        return render_template('aviso.html', aviso="Se ha guardado exitosamente la asistencia")
    else:
        return render_template('asistencia.html', cursos= None, fecha_selec=fecha_selec, estudiantes=estudiantes)

@app.route('/listar_asistencia',methods=['GET','POST'])
@login_required
@preceptor_required
def listar_asistencia():
    preceptor_id=session.get('idpreceptor')
    if preceptor_id:
        preceptor= Preceptor.query.get(preceptor_id)
        if Preceptor:
            if request.method == 'POST':      
                if not request.form['cursos']:
                    return render_template('asistencia.html', cursos = preceptor.curso, curso_seleccionado = None)
                else:
                    curso_selec=request.form['cursos']
                    return redirect(url_for('listar_alumnos',curso_selec=curso_selec))
            else:
                return render_template('l_asistencia.html',cursos = preceptor.curso, curso_seleccionado = None) 

@app.route('/listar_asistencia/<curso_selec>',methods=['GET','POST'])
@login_required
@preceptor_required
def listar_alumnos(curso_selec):
    curso= Curso.query.get(curso_selec)
    estudiantes=curso.estudiante
    estudiantes = sorted(curso.estudiante, key=lambda estudiante: (estudiante.apellido, estudiante.nombre))
    asist=[]
    for c in range (len(estudiantes)):
        asist.append([0,0,0,0,0,0,0])
    asistencias = Asistencia.query.all()
    i=0
    for estudiante in estudiantes:
        for asistencia in asistencias:
            if asistencia.idestudiante==estudiante.id:
                if asistencia.asistio=='s':
                    if asistencia.codigoclase==1:
                        asist[i][0]+=1
                    else:
                        asist[i][1]+=1
                else:
                    if asistencia.justificacion!='':
                        if asistencia.codigoclase==1:
                            asist[i][2]+=1
                        else:
                            asist[i][4]+=1
                    else:
                        if asistencia.codigoclase==1:
                            asist[i][6]+=1
                            asist[i][3]+=1
                        else:
                            asist[i][6]+=0.5
                            asist[i][5]+=0.5
        i+=1
    return render_template('l_asistencia.html',cursos=None,asistencia=asist, estudiantes=estudiantes)
                        
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug = False)