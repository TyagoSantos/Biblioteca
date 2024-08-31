import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from app import consultar_historico

# Cenário Principal: Histórico encontrado com sucesso
def test_consultar_historico_sucesso():
    usuario_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.execute.side_effect = [MagicMock()]
        mock_cursor.fetchall.return_value = [
            ('Livro A', '2024-08-01', '2024-08-15'),
            ('Livro B', '2024-08-10', '2024-08-24')
        ]

        result = consultar_historico(usuario_id)

        assert result["success"] is True
        assert len(result["historico"]) == 2
        assert result["historico"][0] == ('Livro A', '2024-08-01', '2024-08-15')

# Cenário Alternativo: Histórico não encontrado
def test_consultar_historico_vazio():
    usuario_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.execute.side_effect = [MagicMock()]
        mock_cursor.fetchall.return_value = []

        result = consultar_historico(usuario_id)

        assert result["success"] is False
        assert result["message"] == "Nenhum histórico encontrado"

# Cenário Alternativo: Nenhum ID fornecido
def test_consultar_historico_sem_id():
    result = consultar_historico(None)

    assert result["success"] is False
    assert result["message"] == "ID do usuário é obrigatório"

# Cenário Alternativo: Erro de banco de dados ao consultar
def test_consultar_historico_erro_bd():
    usuario_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Erro de banco de dados")

        result = consultar_historico(usuario_id)

        assert result["success"] is False
        assert result["message"].startswith("Erro de banco de dados")

if __name__ == "__main__":
    pytest.main()
