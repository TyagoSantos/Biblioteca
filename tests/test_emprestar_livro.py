import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from app import emprestar_livro

def connect_db():
    return MagicMock()

# Cenário Principal: Empréstimo bem-sucedido
def test_emprestar_livro_sucesso():
    usuario_id = 1
    livro_id = 1
    data_emprestimo = datetime.now().date()
    data_devolucao = data_emprestimo + timedelta(days=14)

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.execute.side_effect = [
            MagicMock(),  # Para verificar o status do livro
            MagicMock(),  # Para inserir o empréstimo
            MagicMock()   # Para atualizar o status do livro
        ]
        mock_cursor.fetchone.return_value = ['Disponível']
        
        result = emprestar_livro(usuario_id, livro_id)
        
        assert result["success"] is True
        assert result["message"] == f"Empréstimo realizado com sucesso. Data de devolução: {data_devolucao}"

# Cenário Alternativo: Livro não encontrado
def test_emprestar_livro_nao_encontrado():
    usuario_id = 1
    livro_id = 999  # ID inexistente
    
    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = None  # Simula livro não encontrado
        
        result = emprestar_livro(usuario_id, livro_id)
        
        assert result["success"] is False
        assert result["message"] == "Livro não encontrado"

# Cenário Alternativo: Livro não disponível
def test_emprestar_livro_nao_disponivel():
    usuario_id = 1
    livro_id = 1
    
    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = ['Emprestado']  # Simula livro já emprestado
        
        result = emprestar_livro(usuario_id, livro_id)
        
        assert result["success"] is False
        assert result["message"] == "O livro não está disponível"

# Cenário Alternativo: Nenhum ID fornecido
def test_emprestar_livro_sem_id():
    result = emprestar_livro(None, None)
    
    assert result["success"] is False
    assert result["message"] == "ID do usuário e do livro são obrigatórios"

# Cenário Alternativo: Erro de banco de dados ao emprestar
def test_emprestar_livro_erro_bd():
    usuario_id = 1
    livro_id = 1
    
    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Erro de banco de dados")
        
        result = emprestar_livro(usuario_id, livro_id)
        
        assert result["success"] is False
        assert result["message"].startswith("Erro de banco de dados")

if __name__ == "__main__":
    pytest.main()
