import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from app import cadastrar_livro, is_valid_isbn

# Simulação de conexão ao banco de dados
def connect_db():
    return MagicMock()

# Cenário Principal: Cadastro bem-sucedido de livro
def test_cadastrar_livro_sucesso():
    titulo = "O Senhor dos Anéis"
    autor = "J.R.R. Tolkien"
    isbn = "978-3-16-148410-0"
    categoria = "Fantasia"
    
    with patch("app.connect_db") as mock_connect_db, \
         patch("app.is_valid_isbn", return_value=True):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        
        result = cadastrar_livro(titulo, autor, isbn, categoria)
        
        assert result["success"] is True
        assert result["message"] == "Livro cadastrado com sucesso"

# Cenário Alternativo: Tentativa de cadastro com campos obrigatórios faltando
def test_cadastrar_livro_campos_faltando():
    result = cadastrar_livro("", "J.K. Rowling", "978-3-16-148410-0", "Fantasia")
    
    assert result["success"] is False
    assert result["message"] == "Todos os campos são obrigatórios"

# Cenário Alternativo: Tentativa de cadastro com ISBN inválido
def test_cadastrar_livro_isbn_invalido():
    titulo = "Harry Potter e a Pedra Filosofal"
    autor = "J.K. Rowling"
    isbn = "978-3-16-148410-XYZ"  # ISBN inválido
    categoria = "Fantasia"
    
    with patch("app.is_valid_isbn", return_value=False):
        result = cadastrar_livro(titulo, autor, isbn, categoria)
    
    assert result["success"] is False
    assert result["message"] == "ISBN inválido"

# Cenário Alternativo: Erro de banco de dados ao cadastrar livro (ISBN já cadastrado)
def test_cadastrar_livro_isbn_ja_cadastrado():
    titulo = "O Hobbit"
    autor = "J.R.R. Tolkien"
    isbn = "978-0-345-33968-3"
    categoria = "Fantasia"
    
    with patch("app.connect_db") as mock_connect_db, \
         patch("app.is_valid_isbn", return_value=True):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.IntegrityError("ISBN já cadastrado")
        
        result = cadastrar_livro(titulo, autor, isbn, categoria)
        
        assert result["success"] is False
        assert result["message"] == "ISBN já cadastrado"

if __name__ == "__main__":
    pytest.main()

