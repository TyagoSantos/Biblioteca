import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from app import renovar_emprestimo

def test_renovar_emprestimo_sucesso():
    usuario_id = 1
    livro_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.execute.side_effect = [
            MagicMock(), 
            MagicMock(),  
            MagicMock()  
        ]
        mock_cursor.fetchone.side_effect = [['Emprestado'], [1, '2024-08-30']] 

        result = renovar_emprestimo(usuario_id, livro_id)

        assert result["success"] is True
        assert result["message"] == "Empréstimo renovado com sucesso"

def test_renovar_emprestimo_nao_encontrado():
    usuario_id = 1
    livro_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.execute.side_effect = [MagicMock()]
        mock_cursor.fetchone.return_value = None

        result = renovar_emprestimo(usuario_id, livro_id)

        assert result["success"] is False
        assert result["message"] == 'Livro não encontrado'

def test_renovar_emprestimo_livro_disponivel():
    usuario_id = 1
    livro_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.execute.side_effect = [MagicMock()]
        mock_cursor.fetchone.side_effect = ['Disponível'] 

        result = renovar_emprestimo(usuario_id, livro_id)
        
        assert result["success"] is False
        assert result["message"] == "O livro não está marcado como emprestado"


def test_renovar_emprestimo_nao_emprestado():
    usuario_id = 1
    livro_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.execute.side_effect = [
            MagicMock(),  
            MagicMock()  
        ]
        mock_cursor.fetchone.side_effect = [['Emprestado'], None]  

        result = renovar_emprestimo(usuario_id, livro_id)
        
        assert result["success"] is False
        assert result["message"] == "O livro não está registrado como emprestado para este usuário"


def test_renovar_emprestimo_sem_id():
    result = renovar_emprestimo(None, None)

    assert result["success"] is False
    assert result["message"] == "ID do usuário e do livro são obrigatórios"


def test_renovar_emprestimo_erro_bd():
    usuario_id = 1
    livro_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Erro de banco de dados")

        result = renovar_emprestimo(usuario_id, livro_id)

        assert result["success"] is False
        assert result["message"].startswith("Erro de banco de dados")

