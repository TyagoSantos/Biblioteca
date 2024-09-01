import pytest
import sqlite3
from app import connect_db, create_tables

def test_connect_db():
    conn = connect_db()
    assert isinstance(conn, sqlite3.Connection)
    conn.close()

def test_create_tables():
    create_tables()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
    assert cursor.fetchone() is not None, "Tabela 'usuarios' não foi criada"

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='livros'")
    assert cursor.fetchone() is not None, "Tabela 'livros' não foi criada"

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emprestimos'")
    assert cursor.fetchone() is not None, "Tabela 'emprestimos' não foi criada"

    conn.close()

