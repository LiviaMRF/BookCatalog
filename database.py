#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
database.py

Módulo responsável por toda a interação com o banco de dados SQLite.
Contém apenas a classe Database.
"""

import sqlite3
import tkinter as tk
from tkinter import messagebox

class Database:
    """
    Classe responsável por toda a interação com o banco de dados SQLite.
    Método de projeto: Singleton simples (uma única conexão por instância).
    """

    def __init__(self, db_name: str = "books.db"):
        """
        Inicializa a conexão com o banco e cria a tabela de livros se não existir.
        """
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self._create_table()
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco", f"Não foi possível conectar ao banco:\n{e}")

    def _create_table(self):
        """
        Cria a tabela 'books' caso ela não exista.
        Campos:
            code (INTEGER PRIMARY KEY),
            title (TEXT),
            author (TEXT),
            genre (TEXT),
            publisher (TEXT),
            year (INTEGER)
        """
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    code INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    publisher TEXT NOT NULL,
                    year INTEGER NOT NULL
                );
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco", f"Não foi possível criar a tabela:\n{e}")

    def insert_book(self, code: int, title: str, author: str, genre: str, publisher: str, year: int):
        """
        Insere um novo livro no banco.
        Lança exceção se o code já existir (violação de PRIMARY KEY).
        """
        try:
            self.cursor.execute(
                "INSERT INTO books (code, title, author, genre, publisher, year) VALUES (?, ?, ?, ?, ?, ?);",
                (code, title, author, genre, publisher, year)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Código {code} já está em uso.")
        except sqlite3.Error as e:
            raise RuntimeError(f"Erro ao inserir livro: {e}")

    def fetch_all(self) -> list:
        """
        Retorna uma lista de tuplas com todos os registros na tabela books,
        ordenada por code.
        """
        try:
            self.cursor.execute("SELECT * FROM books ORDER BY code;")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            raise RuntimeError(f"Erro ao buscar livros: {e}")

    def update_book(self, code: int, title: str, author: str, genre: str, publisher: str, year: int):
        """
        Atualiza os dados de um livro identificado pelo code.
        Retorna True se a atualização afetar alguma linha, False caso contrário.
        """
        try:
            self.cursor.execute(
                """
                UPDATE books
                SET title = ?, author = ?, genre = ?, publisher = ?, year = ?
                WHERE code = ?;
                """,
                (title, author, genre, publisher, year, code)
            )
            self.conn.commit()
            return (self.cursor.rowcount > 0)
        except sqlite3.Error as e:
            raise RuntimeError(f"Erro ao atualizar livro: {e}")

    def delete_book(self, code: int) -> bool:
        """
        Exclui o livro com o código informado.
        Retorna True se alguma linha foi removida, False caso contrário.
        """
        try:
            self.cursor.execute("DELETE FROM books WHERE code = ?;", (code,))
            self.conn.commit()
            return (self.cursor.rowcount > 0)
        except sqlite3.Error as e:
            raise RuntimeError(f"Erro ao deletar livro: {e}")

    def close(self):
        """
        Fecha a conexão com o banco de dados.
        """
        try:
            self.conn.close()
        except sqlite3.Error:
            pass
