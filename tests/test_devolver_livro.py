import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from app import devolver_livro


def test_devolver_livro_sucesso():
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
            MagicMock(),  
            MagicMock()   
        ]
        mock_cursor.fetchone.side_effect = [['Emprestado'], [1]]  

        result = devolver_livro(usuario_id, livro_id)
        
        assert result["success"] is True
        assert result["message"] == "Devolução registrada com sucesso"


def test_devolver_livro_nao_encontrado():
    usuario_id = 1
    livro_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.execute.side_effect = [MagicMock()]
        mock_cursor.fetchone.return_value = None

        result = devolver_livro(usuario_id, livro_id)
        
        assert result["success"] is False
        assert result["message"] == "Livro não encontrado"


def test_devolver_livro_nao_emprestado():
    usuario_id = 1
    livro_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.execute.side_effect = [MagicMock()]
        mock_cursor.fetchone.side_effect = None

        result = devolver_livro(usuario_id, livro_id)
        
        assert result["success"] is False
        assert result["message"] == "O livro não está marcado como emprestado"



def test_devolver_livro_nao_emprestado_para_este_usuario():
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

        result = devolver_livro(usuario_id, livro_id)
        
        assert result["success"] is False
        assert result["message"] == "O livro não está registrado como emprestado para este usuário"


def test_devolver_livro_sem_id():
    result = devolver_livro(None, None)
    
    assert result["success"] is False
    assert result["message"] == "ID do usuário e do livro são obrigatórios"


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

