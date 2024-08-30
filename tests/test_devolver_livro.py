import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from datetime import datetime
from app import devolver_livro

def connect_db():
    return MagicMock()

# Cenário Principal: Devolução bem-sucedida
def test_devolver_livro_sucesso():
    usuario_id = 1
    livro_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.execute.side_effect = [
            MagicMock(),  # Para verificar o empréstimo
            MagicMock(),  # Para registrar a devolução
            MagicMock()   # Para atualizar o status do livro
        ]
        mock_cursor.fetchone.return_value = [1]  # Simula que o livro está emprestado

        result = devolver_livro(usuario_id, livro_id)
        
        assert result["success"] is True
        assert result["message"] == "Devolução registrada com sucesso"

# Cenário Alternativo: Livro não está emprestado para o usuário
def test_devolver_livro_nao_emprestado():
    usuario_id = 1
    livro_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = None  # Simula que o livro não está emprestado

        result = devolver_livro(usuario_id, livro_id)
        
        assert result["success"] is False
        assert result["message"] == "O livro não está registrado como emprestado para este usuário"

# Cenário Alternativo: Nenhum ID fornecido
def test_devolver_livro_sem_id():
    result = devolver_livro(None, None)
    
    assert result["success"] is False
    assert result["message"] == "ID do usuário e do livro são obrigatórios"

# Cenário Alternativo: Erro de banco de dados ao devolver
def test_devolver_livro_erro_bd():
    usuario_id = 1
    livro_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Erro de banco de dados")

        result = devolver_livro(usuario_id, livro_id)

        assert result["success"] is False
        assert result["message"].startswith("Erro de banco de dados")

if __name__ == "__main__":
    pytest.main()
