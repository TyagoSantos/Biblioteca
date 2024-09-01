import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from app import consultar_disponibilidade


def test_consultar_disponibilidade_sucesso():
    livro_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.execute.side_effect = [MagicMock()]
        mock_cursor.fetchone.return_value = ['Disponível']

        result = consultar_disponibilidade(livro_id)

        assert result["success"] is True
        assert result["status"] == 'Disponível'


def test_consultar_disponibilidade_livro_nao_encontrado():
    livro_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.execute.side_effect = [MagicMock()]
        mock_cursor.fetchone.return_value = None

        result = consultar_disponibilidade(livro_id)

        assert result["success"] is False
        assert result["message"] == "Livro não encontrado"


def test_consultar_disponibilidade_sem_id():
    result = consultar_disponibilidade(None)

    assert result["success"] is False
    assert result["message"] == "ID do livro é obrigatório"


def test_consultar_disponibilidade_erro_bd():
    livro_id = 1

    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Erro de banco de dados")

        result = consultar_disponibilidade(livro_id)

        assert result["success"] is False
        assert result["message"].startswith("Erro de banco de dados")


