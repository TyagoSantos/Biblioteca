import pytest
import re

# Funções fictícias para simular o comportamento real
def is_valid_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    return len(cpf) == 11 and cpf.isdigit()

def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email) is not None

def cadastrar_usuario(nome, cpf, email, telefone):
    if not nome or not cpf or not email or not telefone:
        return {"success": False, "message": "Todos os campos são obrigatórios"}
    
    if not is_valid_cpf(cpf):
        return {"success": False, "message": "CPF inválido"}
    
    if not is_valid_email(email):
        return {"success": False, "message": "E-mail inválido"}
    
    # Simulação de sucesso na inserção
    return {"success": True, "message": "Usuário cadastrado com sucesso"}

# Cenário Principal: Cadastro de Usuário Válido
def test_cadastrar_usuario_valido():
    nome = "João Silva"
    cpf = "123.456.789-09" 
    email = "joao.silva@example.com"
    telefone = "(11) 91234-5678"
    
    result = cadastrar_usuario(nome, cpf, email, telefone)
    
    assert result["success"] is True
    assert result["message"] == "Usuário cadastrado com sucesso"

# Cenário Alternativo: Cadastro de Usuário com Dados Incompletos
def test_cadastrar_usuario_dados_incompletos():
    nome = "João Silva"
    cpf = "123.456.789-09"
    email = ""  # E-mail está faltando
    telefone = "(11) 91234-5678"
    
    result = cadastrar_usuario(nome, cpf, email, telefone)
    
    assert result["success"] is False
    assert result["message"] == "Todos os campos são obrigatórios"

# Cenário Alternativo: Cadastro de Usuário com Dados Inválidos
def test_cadastrar_usuario_cpf_invalido():
    nome = "João Silva"
    cpf = "111.222.333-4g"
    email = "joao.silva@example.com"
    telefone = "(11) 91234-5678"
    
    result = cadastrar_usuario(nome, cpf, email, telefone)
    
    assert result["success"] is False
    assert result["message"] == "CPF inválido"

# Cenário Alternativo: Cadastro de Usuário com Dados Inválidos
def test_cadastrar_usuario_email_invalido():
    nome = "João Silva"
    cpf = "111.222.333-44"
    email = "joao.silvaexample.com"
    telefone = "(11) 91234-5678"
    
    result = cadastrar_usuario(nome, cpf, email, telefone)
    
    assert result["success"] is False
    assert result["message"] == "E-mail inválido"

# Mais testes podem ser adicionados para outros cenários, como e-mail inválido, telefone inválido, etc.
