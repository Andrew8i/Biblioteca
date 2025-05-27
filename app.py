db_path = 'base.db'
from flask import Flask, render_template, url_for, request, redirect 
import sqlite3
import os
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect(app)

app.secret_key = 'minha_chave'
app.WTF_CSRF_SECRET_KEY = 'minha_chave_segura'

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
            capa BLOB,
            cat_id INTEGER,
            ativo INTEGER,
            FOREIGN KEY(cat_id)REFERENCES categoria(id))
            ''')
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
        return render_template('editar_categoria.html')

@app.route("/cadastrar_livro", methods=['GET','POST'])
def novoLivro():
    conn = conexao()
    categoria = conn.execute('SELECT * FROM categoria').fetchall()
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        conn = conexao()  
        conn.execute('INSERT INTO livro (nome,descricao) VALUES (?,?)',(nome,descricao,))
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



if  (__name__) == "__main__":
    app.run(debug=True, host='0.0.0.0')