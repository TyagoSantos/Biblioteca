import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from app import remover_livro


def test_remover_livro_sucesso():
    livro_id = 1
    
    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.rowcount = 1  
        
        result = remover_livro(livro_id)
        
        assert result["success"] is True
        assert result["message"] == "Livro removido com sucesso"


def test_remover_livro_nao_encontrado():
    livro_id = 999  
    
    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.rowcount = 0 
        
        result = remover_livro(livro_id)
        
        assert result["success"] is False
        assert result["message"] == "Livro não encontrado"


def test_remover_livro_sem_id():
    result = remover_livro(None)
    
    assert result["success"] is False
    assert result["message"] == "ID do livro é obrigatório"


def test_remover_livro_erro_bd():
    livro_id = 1
    
    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Erro de banco de dados")
        
        result = remover_livro(livro_id)
        
        assert result["success"] is False
        assert result["message"].startswith("Erro de banco de dados")
