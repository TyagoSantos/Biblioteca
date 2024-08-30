import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from app import remover_livro

def connect_db():
    return MagicMock()

# Cenário Principal: Remoção bem-sucedida de livro
def test_remover_livro_sucesso():
    livro_id = 1
    
    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.rowcount = 1  # Simula que um livro foi encontrado e removido
        
        result = remover_livro(livro_id)
        
        assert result["success"] is True
        assert result["message"] == "Livro removido com sucesso"

# Cenário Alternativo: Livro não encontrado
def test_remover_livro_nao_encontrado():
    livro_id = 999  # ID inexistente
    
    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.rowcount = 0  # Simula que nenhum livro foi encontrado
        
        result = remover_livro(livro_id)
        
        assert result["success"] is False
        assert result["message"] == "Livro não encontrado"

# Cenário Alternativo: Nenhum ID fornecido
def test_remover_livro_sem_id():
    result = remover_livro(None)
    
    assert result["success"] is False
    assert result["message"] == "ID do livro é obrigatório"

# Cenário Alternativo: Erro de banco de dados ao remover
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

if __name__ == "__main__":
    pytest.main()
