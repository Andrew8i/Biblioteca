db_path = 'base.db'
from flask import Flask, render_template, url_for, request, redirect 
import sqlite3
import os
from flask_wtf.csrf import CSRFProtect
# from flask_login import LoginManager


app = Flask(__name__)
csrf = CSRFProtect(app)

app.secret_key = 'minha_chave'
app.WTF_CSRF_SECRET_KEY = 'minha_chave_segura'

# login_manager = LoginManager()
# login_maneger.login_view = 'login'
def init_db():
    conn = sqlite3.connect('base.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS categoria(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT)
            ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS livro(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            imagem TEXT,
            cat_id INTEGER,
            ativo INTEGER,
            FOREIGN KEY(cat_id)REFERENCES categoria(id))
            ''')
        
    # try:
    #     conn.execute("SELECT end_imagem FROM livro LIMIT 1")
    # except sqlite3.OperationalError:
    #     conn.execute("ALTER TABLE livro ADD COLUMN end_image TEXT DEFAULT ''")

    conn.commit()
    conn.close()

init_db()

def conexao():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn



@app.route("/")
def listarCategoria():
    conn = conexao()
    categoria = conn.execute('SELECT * FROM categoria ORDER BY nome').fetchall()
    conn.close()
    return render_template('listar_categoria.html',categoria=categoria)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        conn = conexao()
        user = conn.execute('SELECT * FROM usuario WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['senha'], senha):
            user_obj = User(user['id'], user['nome'], user['email'], user['senha'])
            login_user(user_obj)
            return redirect(url_for('listarLivro'))
        else:
            return render_template('login.html', erro='Email ou senha inválidos')
    return render_template('login.html')

@app.route("/nova_categoria", methods=['GET','POST'])
def criarCategoria():
    if request.method == 'POST':
        nome = request.form['nome']
        conn = conexao()  
       
        conn.execute('INSERT INTO categoria (nome) VALUES (?)',(nome,))
        conn.commit()
        conn.close()
        return redirect(url_for('listarCategoria'))
    return render_template("cadastrar_categoria.html")


@app.route("/editar/<int:id>", methods=['GET','POST'])
def editarCategoria(id):
        conn = conexao()
        categoria = conn.execute('''SELECT * FROM categoria WHERE id = ? ''', (id,)).fetchone()
        if not categoria:
            conn.close()
            return 'erro'
        if request.method == 'POST':
            nome = request.form['nome']
            conn.execute('''UPDATE categoria SET nome=? WHERE id=?''', (nome, id ))
            conn.commit()
            conn.close()
            return redirect(url_for('listarCategoria'))
        conn.close()
        return render_template('editar_categoria.html',categoria=categoria)


@app.route("/excluir/<int:id>", methods=['GET','POST'])
def excluirCategoria(id):
        conn = conexao()
        conn.execute('''DELETE FROM categoria WHERE id=? ''', (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('listarCategoria'))

@app.route("/cadastrar_livro", methods=['GET','POST'])
def novoLivro():
    conn = conexao()
    categoria = conn.execute('SELECT * FROM categoria').fetchall()
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        imagem = request.files["imagem"]


        from werkzeug.utils import secure_filename
        imagem_filename = secure_filename(imagem.filename)
        upload_path = os.path.join("static", "uploads")
        os.makedirs(upload_path, exist_ok=True)

        imagem.save(os.path.join(upload_path, imagem_filename))
        conn = conexao()  
        conn.execute('INSERT INTO livro (nome,descricao,end_image) VALUES (?,?,?)',(nome,descricao,imagem_filename))

        conn.commit()
        conn.close()

        return redirect(url_for('listarLivro'))
    return render_template("cadastrar_livro.html", categoria=categoria)

@app.route("/listar_livro")
def listarLivro():
    conn = conexao()
    livro = conn.execute('SELECT * FROM livro ORDER BY nome').fetchall()
    conn.close()
    return render_template('listar_livro.html', livro=livro)

# @app.route('/cadastrar_usuario', methods=['GET', 'POST'])
# def cadastrarUsuario():
#     if request.method == 'POST':
#         nome = request.form['nome']
#         email = request.form['email']
#         senha = generate_password_hash(request.form['senha'])
#         try:
#             conn = conexao()
#             conn.execute('INSERT INTO usuario (nome, email, senha) VALUES (?, ?, ?)', (nome, email, senha))
#             conn.commit()
#             conn.close()
#             return redirect(url_for('login'))
#         except:
#             return "Erro ao cadastrar usuario (e-mail pode estar duplicado)"
#     return render_template('cadastrar_usuario.html')



if  (__name__) == "__main__":
    app.run(debug=True, host='0.0.0.0')