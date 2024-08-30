import sqlite3
import re
from datetime import datetime, timedelta

# Conectar ao banco de dados SQLite
def connect_db():
    conn = sqlite3.connect('biblioteca.db')
    return conn

# Criar tabelas
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

# Validação de CPF (exemplo básico)
def is_valid_cpf(cpf):
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    return len(cpf) == 11 and cpf.isdigit()

# Validação de e-mail
def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email) is not None

# Cadastro de usuário com validações
def cadastrar_usuario(nome, cpf, email, telefone):
    # Verificar se todos os campos estão preenchidos
    if not nome or not cpf or not email or not telefone:
        return "Todos os campos são obrigatórios"
    
    # Verificar validade do CPF
    if not is_valid_cpf(cpf):
        return "CPF inválido"
    
    # Verificar validade do e-mail
    if not is_valid_email(email):
        return "E-mail inválido"
    
    # Conectar ao banco de dados e inserir o usuário
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

# Atualização de informações do usuário
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

# Validação de ISBN (exemplo básico)
def is_valid_isbn(isbn):
    # Remove caracteres não numéricos
    isbn = re.sub(r'\D', '', isbn)
    return len(isbn) in [10, 13] and isbn.isdigit()

# Cadastro de livro com validações
def cadastrar_livro(titulo, autor, isbn, categoria):
    # Verificar se todos os campos estão preenchidos
    if not titulo or not autor or not isbn or not categoria:
        return {"success": False, "message": "Todos os campos são obrigatórios"}
    
    # Verificar validade do ISBN
    if not is_valid_isbn(isbn):
        return {"success": False, "message": "ISBN inválido"}

    # Conectar ao banco de dados e inserir o livro
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

# Empréstimo de livro
# Pensar se vale a pena pesquisar o livro pelo nome
def emprestar_livro(usuario_id, livro_id):
    if not usuario_id or not livro_id:
        return {"success": False, "message": "ID do usuário e do livro são obrigatórios"}

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Verificar se o livro está disponível
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

# Devolução de livro
def devolver_livro(usuario_id, livro_id):
    if not usuario_id or not livro_id:
        return {"success": False, "message": "ID do usuário e do livro são obrigatórios"}
    
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Verificar se o livro está emprestado
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


# Renovação de empréstimo
def renovar_emprestimo(usuario_id, livro_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, data_devolucao FROM emprestimos WHERE usuario_id = ? AND livro_id = ? AND data_devolucao IS NULL
    ''', (usuario_id, livro_id))
    emprestimo = cursor.fetchone()
    if emprestimo:
        nova_data_devolucao = datetime.strptime(emprestimo[1], '%Y-%m-%d') + timedelta(days=14)
        cursor.execute('UPDATE emprestimos SET data_devolucao = ? WHERE id = ?', (nova_data_devolucao.date(), emprestimo[0]))
        conn.commit()
        print(f'Renovação realizada com sucesso. Nova data de devolução: {nova_data_devolucao.date()}')
    else:
        print('O livro não pode ser renovado.')
    conn.close()

# Consulta de histórico de empréstimos
def consultar_historico(usuario_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT livros.titulo, emprestimos.data_emprestimo, emprestimos.data_devolucao
    FROM emprestimos
    JOIN livros ON emprestimos.livro_id = livros.id
    WHERE emprestimos.usuario_id = ?
    ''', (usuario_id,))
    historico = cursor.fetchall()
    if historico:
        for item in historico:
            print(f'Título: {item[0]}, Data de Empréstimo: {item[1]}, Data de Devolução: {item[2]}')
    else:
        print('Nenhum histórico encontrado.')
    conn.close()

# Consulta de disponibilidade de livro
def consultar_disponibilidade(livro_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM livros WHERE id = ?', (livro_id,))
    status = cursor.fetchone()
    if status:
        print(f'O livro está {status[0]}.')
    else:
        print('Livro não encontrado.')
    conn.close()

# Renovação de empréstimo
def renovar_emprestimo(usuario_id, livro_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, data_devolucao FROM emprestimos
    WHERE usuario_id = ? AND livro_id = ? AND data_devolucao IS NULL
    ''', (usuario_id, livro_id))
    emprestimo = cursor.fetchone()
    if emprestimo:
        max_renovacoes = 2  # Número máximo de renovações permitidas
        cursor.execute('SELECT COUNT(*) FROM emprestimos WHERE livro_id = ? AND data_devolucao IS NULL', (livro_id,))
        num_renovacoes = cursor.fetchone()[0]
        if num_renovacoes < max_renovacoes:
            nova_data_devolucao = datetime.now().date() + timedelta(days=14)
            cursor.execute('UPDATE emprestimos SET data_devolucao = ? WHERE id = ?', (nova_data_devolucao, emprestimo[0]))
            conn.commit()
            print(f'Renovação realizada com sucesso. Nova data de devolução: {nova_data_devolucao}')
        else:
            print('Número máximo de renovações atingido.')
    else:
        print('O livro não pode ser renovado.')
    conn.close()



# Geração de relatórios
def gerar_relatorio(tipo):
    conn = connect_db()
    cursor = conn.cursor()
    if tipo == 'emprestados':
        cursor.execute('''
        SELECT livros.titulo, COUNT(emprestimos.id) AS total
        FROM emprestimos
        JOIN livros ON emprestimos.livro_id = livros.id
        WHERE emprestimos.data_devolucao IS NULL
        GROUP BY livros.titulo
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
        AND emprestimos.data_devolucao IS NOT NULL
        ''', (datetime.now().date(),))
    else:
        print('Tipo de relatório inválido.')
        conn.close()
        return
    relatorio = cursor.fetchall()
    if relatorio:
        for item in relatorio:
            print(item)
    else:
        print('Nenhum dado disponível para o relatório solicitado.')
    conn.close()

# Função principal
def main():
    create_tables()
    # Exemplo de uso
    cadastrar_usuario('João Silva', '12345678901', 'joao.silva@example.com', '11987654321')
    cadastrar_livro('Python para Iniciantes', 'Jane Doe', '9781234567890', 'Tecnologia')
    emprestar_livro(1, 1)
    devolver_livro(1, 1)
    atualizar_usuario(1, telefone='11900000000')
    renovar_emprestimo(1, 1)
    consultar_historico(1)
    gerar_relatorio('emprestados')
    gerar_relatorio('disponiveis')
    gerar_relatorio('atraso')

if __name__ == "__main__":
    main()
