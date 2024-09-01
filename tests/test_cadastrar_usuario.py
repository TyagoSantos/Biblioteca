import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from app import cadastrar_usuario


def test_cadastrar_usuario_sucesso():
    nome = "João da Silva"
    cpf = "12345678901"
    email = "joao.silva@example.com"
    telefone = "(11) 91234-5678"
    
    with patch("app.connect_db") as mock_connect_db, \
         patch("app.is_valid_cpf", return_value=True), \
         patch("app.is_valid_email", return_value=True):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        
        result = cadastrar_usuario(nome, cpf, email, telefone)
        
        assert result == "Usuário cadastrado com sucesso"


def test_cadastrar_usuario_campos_faltando():
    result = cadastrar_usuario("", "12345678901", "joao.silva@example.com", "(11) 91234-5678")
    
    assert result == "Todos os campos são obrigatórios"


def test_cadastrar_usuario_cpf_invalido():
    nome = "João da Silva"
    cpf = "123"  
    email = "joao.silva@example.com"
    telefone = "(11) 91234-5678"
    
    with patch("app.is_valid_cpf", return_value=False):
        result = cadastrar_usuario(nome, cpf, email, telefone)
    
    assert result == "CPF inválido"


def test_cadastrar_usuario_email_invalido():
    nome = "João da Silva"
    cpf = "12345678901"
    email = "joao.silvaexample.com"  
    telefone = "(11) 91234-5678"
    
    with patch("app.is_valid_email", return_value=False):
        result = cadastrar_usuario(nome, cpf, email, telefone)
    
    assert result == "E-mail inválido"


def test_cadastrar_usuario_erro_bd():
    nome = "João da Silva"
    cpf = "12345678901"
    email = "joao.silva@example.com"
    telefone = "(11) 91234-5678"
    
    with patch("app.connect_db") as mock_connect_db, \
         patch("app.is_valid_cpf", return_value=True), \
         patch("app.is_valid_email", return_value=True):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.IntegrityError("CPF ou e-mail já cadastrado")
        
        result = cadastrar_usuario(nome, cpf, email, telefone)
        
        assert result == "CPF ou e-mail já cadastrado"

