
from flask import Flask, app
from flask import render_template,request,redirect,url_for, flash
from flaskext.mysql import MySQL
from flask import  send_from_directory
from datetime import datetime
import os 

app=Flask(__name__)
app.secret_key="Walter"

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']= 'localhost'
app.config['MYSQL_DATABASE_USER']= 'root'
app.config['MYSQL_DATABASE_PASSWORD']= 'root'
app.config['MYSQL_DATABASE_DB']= 'sistema'
mysql.init_app(app)

# referencia de la carpeta donde se guarda fotos y guardamos en una variable el valor de la ruta
CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

# funcion que se mueve en el index principal 
@app.route("/")
def index():    
    #sql = "SELECT * FROM empleados;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados;")    
    empleados=cursor.fetchall()    
    print(empleados)   
    conn.commit()
         
    return render_template('empleados/index.html', empleados=empleados)

# funcion de borrado de registro
@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    # se borra el registro de la foto
    cursor.execute("SELECT foto FROM empleados WHERE id=%s", (id))
    fila= cursor.fetchall() 
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) 
    # se borra el registro de los datos 
    cursor.execute("DELETE FROM empleados  WHERE id=%s",(id))
    conn.commit()
    return redirect('/') 

# funcion de editar un registro
@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()   
    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id))    
    empleados=cursor.fetchall()
    conn.commit()
    #print(empleados)   
    return render_template('empleados/edit.html', empleados=empleados) 

# funcion de actualización de registro
@app.route('/update', methods=['POST'] )
def update():
    _nombre=request.form['nombre']
    _correo=request.form['correo']
    _foto=request.files['foto']    
    id=request.form['id']
    
    sql = "UPDATE empleados SET nombre=%s, correo=%s  WHERE id=%s;"
    datos=(_nombre, _correo,id)
    
    conn = mysql.connect()
    cursor = conn.cursor()
    # codigo para actualizar la foto del registro
    now=datetime.now()
    tiempo=now.strftime("%Y%H%M%S")
    
    if _foto.filename != '':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)            
        cursor.execute("SELECT foto FROM empleados WHERE id=%s", (id))
        fila= cursor.fetchall() 
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) 
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(nuevoNombreFoto, id))
        conn.commit()
    
    cursor.execute(sql, datos)
    conn.commit()        
    return redirect('/') 

# funcion de crear un registro 
@app.route('/create')
def create():
    
    return render_template('empleados/create.html')

# funcion que ingresa los datos al registro y verifica que la foto no este duplicada 
@app.route('/store', methods=['POST'])
def storage():
    _nombre=request.form['nombre']
    _correo=request.form['correo']
    _foto=request.files['foto']
    # verificamos que el usuario no deje los campos sin ingresar datos 
    if _nombre == '' or _correo == '' or _foto == '':
        flash('Recuerda llenar todos los campos de información solicitada..')
        return  redirect(url_for('create'))  
    
    now=datetime.now()
    tiempo=now.strftime("%Y%H%M%S")
    
    if _foto.filename != '':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)      
    
    
    sql = "INSERT INTO empleados (id, 'nombre', 'correo', 'foto') VALUES (NULL, %s, %s, %s);"
    datos=(_nombre, _correo,nuevoNombreFoto)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    
    return render_template("empleados/index.html")
    #return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
    
    