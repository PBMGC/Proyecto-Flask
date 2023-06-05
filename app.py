from flask import Flask,request,url_for,render_template,flash,session,redirect
from flask_mysqldb import MySQL
from datetime import date
app=Flask(__name__)

app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]="123"
app.config["MYSQL_DB"]="libro"

mysql=MySQL(app)

app.secret_key="123"

@app.route("/redireccion/<int:tp>")
def redireccion(tp):
    if tp==1:
        return render_template("register.html")
    elif tp==2:
        return redirect(url_for("index"))
    elif tp==3:
        return render_template("login.html")
    elif tp==4:
        return render_template("add.html")


@app.route("/")
def index():

    consulta=mysql.connection.cursor()
    consulta.execute("SELECT c.comentario as 'comentario', c.fecha as 'fecha', c.anonimo as 'anonimo', u.usuario as 'usuario' FROM comentarios c JOIN usuarios u ON c.IdUsuario = u.IdUsuario;")
    datos=consulta.fetchall()

    print(datos)

    return render_template("index.html",datos=datos)

@app.route("/add",methods=['POST'])
def add():
    if request.method=="POST":
        comentario=request.form["comentario"]
        anonimo= request.form.get("anonimo")
        id=request.form["id"]

        fecha=date.today()
        fecha_str = fecha.strftime('%Y-%m-%d')

        cur=mysql.connection.cursor()

        if anonimo:
            cur.execute("insert into comentarios (comentario,anonimo,fecha,IdUsuario) values (%s,'si',%s,%s)",(comentario,fecha_str,id))
        else:
            cur.execute("INSERT INTO comentarios (comentario, anonimo,fecha,IdUsuario) VALUES (%s, 'no',%s,%s)", (comentario,fecha_str,id))
        cur.execute("UPDATE usuarios SET comentarios = comentarios + 1 WHERE IdUsuario = %s", (id,))
        mysql.connection.commit()

        return redirect(url_for("index"))

        
        
@app.route("/login",methods=["POST"])
def login():
    if request.method=="POST":
        Usuario=request.form["usuario"]
        Contraseña=request.form["contraseña"]

        cn=mysql.connection.cursor()
        cn.execute("SELECT * FROM usuarios WHERE usuario='{0}' AND contraseña='{1}'".format(Usuario, Contraseña))
        datos = cn.fetchall()
        if datos:
            flash("Entraste Papu","exito")
            session["id"]=datos[0][0]
            session["usuario"]=Usuario
            return redirect(url_for("index"))
        else:
            flash("Intenta otra vez we","error")
            return redirect(url_for("redireccion",tp=3)) 

@app.route("/register",methods=["POST"])
def register():
    if request.method=="POST":
        Usuario=request.form["usuario"]
        Correo=request.form["email"]
        Contraseña=request.form["contraseña"]

        cn=mysql.connection.cursor()
        cn.execute("SELECT * FROM usuarios WHERE usuario = '{0}' AND correo = '{1}'".format(Usuario, Correo))
        datos=cn.fetchall()

        if datos:
            flash("Registro Existente","error")
            return  redirect(url_for('redireccion', tp=3))
        else:
            con=mysql.connection.cursor()
            con.execute("insert into usuarios(usuario,correo,contraseña) values (%s,%s,%s)",(Usuario,Correo,Contraseña))
            mysql.connection.commit()
            session["usuario"]=Usuario
            session["id"]=datos[0][0]

            flash("Registro Exitoso papure","exito")
            return redirect(url_for("index"))
        

@app.route("/usuario")
def usuario():
    cn=mysql.connection.cursor()
    cn.execute("SELECT * FROM comentarios WHERE idusuario={0} ORDER BY fecha DESC LIMIT 3".format(session["id"]))
    datosN=cn.fetchall()

    cn=mysql.connection.cursor()
    cn.execute("SELECT * FROM comentarios WHERE idusuario={0}".format(session["id"]))
    datosT=cn.fetchall()

    return render_template("usuario.html",datosN=datosN,datosT=datosT)
        

@app.route("/logout")
def logout():
    session.pop("usuario",None)
    session.pop("id",None)

    return redirect(url_for("index"))
        

if __name__ == '__main__':

    app.run(debug=True)