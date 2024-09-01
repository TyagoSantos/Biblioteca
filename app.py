import sqlite3
import re
from datetime import datetime, timedelta

def connect_db():
    conn = sqlite3.connect('biblioteca.db')
    return conn

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        telefone TEXT NOT NULL
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        isbn TEXT UNIQUE NOT NULL,
        categoria TEXT NOT NULL,
        status TEXT NOT NULL
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emprestimos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        livro_id INTEGER,
        data_emprestimo DATE NOT NULL,
        data_devolucao DATE,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (livro_id) REFERENCES livros(id)
    )''')
    conn.commit()
    conn.close()


def is_valid_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    return len(cpf) == 11 and cpf.isdigit()


def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email) is not None


def cadastrar_usuario(nome, cpf, email, telefone):

    if not nome or not cpf or not email or not telefone:
        return "Todos os campos são obrigatórios"
    
    if not is_valid_cpf(cpf):
        return "CPF inválido"
    
    if not is_valid_email(email):
        return "E-mail inválido"
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO usuarios (nome, cpf, email, telefone) VALUES (?, ?, ?, ?)
        ''', (nome, cpf, email, telefone))
        conn.commit()
        return "Usuário cadastrado com sucesso"
    except sqlite3.IntegrityError:
        return "CPF ou e-mail já cadastrado"
    finally:
        conn.close()

def atualizar_usuario(user_id, nome=None, email=None, telefone=None):
    if nome is None and email is None and telefone is None:
        return {"success": False, "message": "Nenhuma informação para atualizar"}
    
    if email and not is_valid_email(email):
        return {"success": False, "message": "E-mail inválido"}

    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        if nome:
            cursor.execute('UPDATE usuarios SET nome = ? WHERE id = ?', (nome, user_id))
        if email:
            cursor.execute('UPDATE usuarios SET email = ? WHERE id = ?', (email, user_id))
        if telefone:
            cursor.execute('UPDATE usuarios SET telefone = ? WHERE id = ?', (telefone, user_id))
        conn.commit()
        return {"success": True, "message": "Usuário atualizado com sucesso"}
    except sqlite3.Error as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()


def is_valid_isbn(isbn):
    isbn = re.sub(r'\D', '', isbn)
    return len(isbn) in [10, 13] and isbn.isdigit()


def cadastrar_livro(titulo, autor, isbn, categoria):
    if not titulo or not autor or not isbn or not categoria:
        return {"success": False, "message": "Todos os campos são obrigatórios"}
    

    if not is_valid_isbn(isbn):
        return {"success": False, "message": "ISBN inválido"}

    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO livros (titulo, autor, isbn, categoria, status) VALUES (?, ?, ?, ?, ?)
        ''', (titulo, autor, isbn, categoria, 'Disponível'))
        conn.commit()
        return {"success": True, "message": "Livro cadastrado com sucesso"}
    except sqlite3.IntegrityError:
        return {"success": False, "message": "ISBN já cadastrado"}
    finally:
        conn.close()

def remover_livro(livro_id):
    if not livro_id:
        return {"success": False, "message": "ID do livro é obrigatório"}

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM livros WHERE id = ?', (livro_id,))
        if cursor.rowcount == 0:
            return {"success": False, "message": "Livro não encontrado"}
        conn.commit()
        return {"success": True, "message": "Livro removido com sucesso"}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro de banco de dados: {str(e)}"}
    finally:
        conn.close()


def emprestar_livro(usuario_id, livro_id):
    if not usuario_id or not livro_id:
        return {"success": False, "message": "ID do usuário e do livro são obrigatórios"}

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT status FROM livros WHERE id = ?', (livro_id,))
        livro = cursor.fetchone()

        if livro is None:
            return {"success": False, "message": "Livro não encontrado"}

        status = livro[0]
        if status == 'Disponível':
            data_emprestimo = datetime.now().date()
            data_devolucao = data_emprestimo + timedelta(days=14)  # 2 semanas para devolução

            cursor.execute('''
            INSERT INTO emprestimos (usuario_id, livro_id, data_emprestimo, data_devolucao)
            VALUES (?, ?, ?, ?)
            ''', (usuario_id, livro_id, data_emprestimo, data_devolucao))

            cursor.execute('UPDATE livros SET status = ? WHERE id = ?', ('Emprestado', livro_id))
            conn.commit()
            return {"success": True, "message": f"Empréstimo realizado com sucesso. Data de devolução: {data_devolucao}"}
        else:
            return {"success": False, "message": "O livro não está disponível"}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro de banco de dados: {str(e)}"}
    finally:
        conn.close()


def devolver_livro(usuario_id, livro_id):
    if not usuario_id or not livro_id:
        return {"success": False, "message": "ID do usuário e do livro são obrigatórios"}
    
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT status FROM livros WHERE id = ?', (livro_id,))
        livro = cursor.fetchone()

        if livro is None:
            return {"success": False, "message": "Livro não encontrado"}

        status = livro[0]
        if status == 'Emprestado':
            cursor.execute('''
            SELECT id FROM emprestimos WHERE usuario_id = ? AND livro_id = ?
            ''', (usuario_id, livro_id))
            emprestimo_id = cursor.fetchone()

            if emprestimo_id:
                cursor.execute('UPDATE emprestimos SET data_devolucao = ? WHERE id = ?', (datetime.now().date(), emprestimo_id[0]))
                cursor.execute('UPDATE livros SET status = ? WHERE id = ?', ('Disponível', livro_id))
                conn.commit()
                return {"success": True, "message": "Devolução registrada com sucesso"}
            else:
                return {"success": False, "message": "O livro não está registrado como emprestado para este usuário"}
        else:
            return {"success": False, "message": "O livro não está marcado como emprestado"}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro de banco de dados: {str(e)}"}
    finally:
        conn.close()


def renovar_emprestimo(usuario_id, livro_id):
    if not usuario_id or not livro_id:
        return {"success": False, "message": "ID do usuário e do livro são obrigatórios"}

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT status FROM livros WHERE id = ?', (livro_id,))
        livro = cursor.fetchone()

        if livro is None:
            return {"success": False, "message": "Livro não encontrado"}

        status = livro[0]
        if status == 'Emprestado':
            cursor.execute('''
            SELECT id, data_devolucao FROM emprestimos WHERE usuario_id = ? AND livro_id = ? 
            ''', (usuario_id, livro_id))
            emprestimo = cursor.fetchone()

            if emprestimo:
                emprestimo_id = emprestimo[0]
                nova_data_devolucao = datetime.strptime(emprestimo[1], '%Y-%m-%d') + timedelta(days=7)

                cursor.execute('UPDATE emprestimos SET data_devolucao = ? WHERE id = ?', (nova_data_devolucao.date(), emprestimo_id))
                conn.commit()
                return {"success": True, "message": "Empréstimo renovado com sucesso"}
            else:
                return {"success": False, "message": "O livro não está registrado como emprestado para este usuário"}
        else:
            return {"success": False, "message": "O livro não está marcado como emprestado"}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro de banco de dados: {str(e)}"}
    finally:
        conn.close()


def consultar_historico(usuario_id):
    if not usuario_id:
        return {"success": False, "message": "ID do usuário é obrigatório"}

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT livros.titulo, emprestimos.data_emprestimo, emprestimos.data_devolucao
        FROM emprestimos
        JOIN livros ON emprestimos.livro_id = livros.id
        WHERE emprestimos.usuario_id = ?
        ''', (usuario_id,))
        historico = cursor.fetchall()

        if historico:
            return {"success": True, "historico": historico}
        else:
            return {"success": False, "message": "Nenhum histórico encontrado"}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro de banco de dados: {str(e)}"}
    finally:
        conn.close()


def consultar_disponibilidade(livro_id):
    if not livro_id:
        return {"success": False, "message": "ID do livro é obrigatório"}

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT status FROM livros WHERE id = ?', (livro_id,))
        status = cursor.fetchone()
        
        if status:
            return {"success": True, "status": status[0]}
        else:
            return {"success": False, "message": "Livro não encontrado"}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro de banco de dados: {str(e)}"}
    finally:
        conn.close()


def gerar_relatorio(tipo):
    if tipo not in ['emprestados', 'disponiveis', 'atraso']:
        return {"success": False, "message": "Tipo de relatório inválido"}
    
    conn = connect_db()
    cursor = conn.cursor()

    try:
        if tipo == 'emprestados':
            cursor.execute('''
            SELECT livros.titulo, emprestimos.data_devolucao
            FROM emprestimos
            JOIN livros ON emprestimos.livro_id = livros.id
            WHERE livros.status = 'Emprestado'
            ''')
        elif tipo == 'disponiveis':
            cursor.execute('''
            SELECT titulo FROM livros WHERE status = 'Disponível'
            ''')
        elif tipo == 'atraso':
            cursor.execute('''
            SELECT livros.titulo, emprestimos.data_devolucao
            FROM emprestimos
            JOIN livros ON emprestimos.livro_id = livros.id
            WHERE emprestimos.data_devolucao < ?
            AND livros.status = 'Emprestado'
            ''', (datetime.now().date(),))

        relatorio = cursor.fetchall()
        if relatorio:
            return {"success": True, "data": relatorio}
        else:
            return {"success": False, "message": "Nenhum dado disponível para o relatório solicitado"}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro de banco de dados: {str(e)}"}
    finally:
        conn.close()