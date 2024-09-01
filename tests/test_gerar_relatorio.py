import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from app import gerar_relatorio


def test_gerar_relatorio_emprestados():
    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [
            ('Livro 1', '2024-09-14'),
            ('Livro 2', '2024-09-15')
        ]

        result = gerar_relatorio('emprestados')

        assert result == {
            "success": True,
            "data": [
                ('Livro 1', '2024-09-14'),
                ('Livro 2', '2024-09-15')
            ]
        }


def test_gerar_relatorio_disponiveis():
    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [
            ('Livro 1',),
            ('Livro 3',)
        ]

        result = gerar_relatorio('disponiveis')

        assert result == {
            "success": True,
            "data": [
                ('Livro 1',),
                ('Livro 3',)
            ]
        }

def test_gerar_relatorio_atraso():
    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [
            ('Livro 1', '2024-08-28'),
            ('Livro 2', '2024-08-27')
        ]

        result = gerar_relatorio('atraso')

        assert result == {
            "success": True,
            "data": [
                ('Livro 1', '2024-08-28'),
                ('Livro 2', '2024-08-27')
            ]
        }


def test_gerar_relatorio_invalido():
    result = gerar_relatorio('invalido')

    assert result == {
        "success": False,
        "message": "Tipo de relatório inválido"
    }


def test_gerar_relatorio_sem_dados():
    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.execute.side_effect = [MagicMock()]
        mock_cursor.fetchall.return_value = []

        result = gerar_relatorio('emprestados')

        assert result["success"] is False
        assert result["message"] == "Nenhum dado disponível para o relatório solicitado"


def test_gerar_relatorio_erro_bd():
    with patch("app.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Erro de banco de dados")

        result = gerar_relatorio('emprestados')

        assert result["success"] is False
        assert result["message"].startswith("Erro de banco de dados")

