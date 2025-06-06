#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app.py

Módulo principal da aplicação: contém a classe BookApp (GUI + Controller)
e importa Database de database.py.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from database import Database  # importa a classe Database do módulo database.py

class BookApp:
    """
    Classe principal da aplicação: cria a interface Tkinter, manipula eventos e
    chama métodos da classe Database para realizar operações CRUD.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Catálogo de Livros – CSI-22")
        self.db = Database()

        # Configuração da janela principal
        self.root.configure(padx=10, pady=10)
        self._build_widgets()
        self._populate_listbox()

    def _build_widgets(self):
        """
        Cria todos os widgets (labels, entries, buttons e listbox) e posiciona-os na janela.
        """

        # ---------- Frame de entrada de dados ----------
        frame_form = ttk.LabelFrame(self.root, text="Dados do Livro", padding=(10, 10))
        frame_form.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Labels e Entry para cada campo: code, title, author, genre, publisher, year
        labels = ["Código (int):", "Título:", "Autor:", "Gênero:", "Editora:", "Ano (int):"]
        self.entries = {}  # irá mapear 'campo' → widget Entry

        for i, label_text in enumerate(labels):
            lbl = ttk.Label(frame_form, text=label_text)
            lbl.grid(row=i, column=0, sticky="e", pady=5)

            entry = ttk.Entry(frame_form)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="we")
            # Mapear o campo conforme seu índice
            if i == 0:
                self.entries["code"] = entry
            elif i == 1:
                self.entries["title"] = entry
            elif i == 2:
                self.entries["author"] = entry
            elif i == 3:
                self.entries["genre"] = entry
            elif i == 4:
                self.entries["publisher"] = entry
            elif i == 5:
                self.entries["year"] = entry

        # Configurar expansão horizontal dos entries
        frame_form.columnconfigure(1, weight=1)

        # ---------- Frame de botões ----------
        frame_buttons = ttk.Frame(self.root)
        frame_buttons.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        frame_buttons.columnconfigure((0,1,2,3,4), weight=1)

        btn_add = ttk.Button(frame_buttons, text="Adicionar Livro", command=self.add_book)
        btn_add.grid(row=0, column=0, padx=5, sticky="ew")

        btn_view_all = ttk.Button(frame_buttons, text="Visualizar Todos", command=self._populate_listbox)
        btn_view_all.grid(row=0, column=1, padx=5, sticky="ew")

        btn_update = ttk.Button(frame_buttons, text="Atualizar Livro", command=self.update_book)
        btn_update.grid(row=0, column=2, padx=5, sticky="ew")

        btn_delete = ttk.Button(frame_buttons, text="Deletar Livro", command=self.delete_book)
        btn_delete.grid(row=0, column=3, padx=5, sticky="ew")

        btn_clear = ttk.Button(frame_buttons, text="Limpar Campos", command=self.clear_entries)
        btn_clear.grid(row=0, column=4, padx=5, sticky="ew")

        # ---------- Frame de listagem ----------
        frame_list = ttk.LabelFrame(self.root, text="Catálogo de Livros", padding=(10, 10))
        frame_list.grid(row=2, column=0, sticky="nsew")
        self.root.rowconfigure(2, weight=1)
        frame_list.columnconfigure(0, weight=1)
        frame_list.rowconfigure(0, weight=1)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(frame_list, orient=tk.VERTICAL)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Listbox para exibir registros
        self.listbox = tk.Listbox(frame_list, height=10, yscrollcommand=scrollbar.set)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.listbox.yview)

        # Evento de seleção: popula campos quando um item for selecionado
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

    def _populate_listbox(self):
        """
        Busca todos os livros no banco e preenche a Listbox.
        """
        try:
            self.listbox.delete(0, tk.END)
            for row in self.db.fetch_all():
                code, title, author, genre, publisher, year = row
                display_text = f"{code} | {title} | {author} | {genre} | {publisher} | {year}"
                self.listbox.insert(tk.END, display_text)
        except RuntimeError as e:
            messagebox.showerror("Erro", str(e))

    def clear_entries(self):
        """
        Limpa todos os campos de entrada.
        """
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        # Remover qualquer seleção na listbox
        self.listbox.selection_clear(0, tk.END)

    def on_select(self, event):
        """
        Quando o usuário clica em um item da listbox, este método é chamado
        para preencher os campos com os dados do livro selecionado.
        """
        try:
            index = self.listbox.curselection()
            if not index:
                return  # nada selecionado
            selected_text = self.listbox.get(index)
            # Esperamos o formato: "code | title | author | genre | publisher | year"
            parts = [p.strip() for p in selected_text.split("|")]
            self.entries["code"].delete(0, tk.END)
            self.entries["code"].insert(tk.END, parts[0])
            self.entries["title"].delete(0, tk.END)
            self.entries["title"].insert(tk.END, parts[1])
            self.entries["author"].delete(0, tk.END)
            self.entries["author"].insert(tk.END, parts[2])
            self.entries["genre"].delete(0, tk.END)
            self.entries["genre"].insert(tk.END, parts[3])
            self.entries["publisher"].delete(0, tk.END)
            self.entries["publisher"].insert(tk.END, parts[4])
            self.entries["year"].delete(0, tk.END)
            self.entries["year"].insert(tk.END, parts[5])
        except Exception:
            # Em caso de qualquer erro de parsing, apenas ignore
            pass

    def _get_entry_values(self):
        """
        Lê todos os campos de entrada e retorna uma tupla validada:
        (code: int, title: str, author: str, genre: str, publisher: str, year: int)
        Lança ValueError em caso de falha na conversão de inteiros ou campo vazio.
        """
        try:
            code_str = self.entries["code"].get().strip()
            title = self.entries["title"].get().strip()
            author = self.entries["author"].get().strip()
            genre = self.entries["genre"].get().strip()
            publisher = self.entries["publisher"].get().strip()
            year_str = self.entries["year"].get().strip()

            # Verificar se todos os campos obrigatórios estão preenchidos
            if not (code_str and title and author and genre and publisher and year_str):
                raise ValueError("Preencha todos os campos.")

            try:
                code = int(code_str)
            except ValueError:
                raise ValueError("Código deve ser um número inteiro.")

            try:
                year = int(year_str)
            except ValueError:
                raise ValueError("Ano de publicação deve ser um número inteiro.")

            return code, title, author, genre, publisher, year

        except ValueError as ve:
            raise ve

    def add_book(self):
        """
        Handler para o botão 'Adicionar Livro'.
        Tenta ler os valores, chamar o método de inserção do DB e atualizar a listbox.
        """
        try:
            code, title, author, genre, publisher, year = self._get_entry_values()
            self.db.insert_book(code, title, author, genre, publisher, year)
            messagebox.showinfo("Sucesso", f"Livro com código {code} inserido.")
            self._populate_listbox()
            self.clear_entries()
        except ValueError as ve:
            messagebox.showwarning("Atenção", str(ve))
        except RuntimeError as re:
            messagebox.showerror("Erro", str(re))

    def update_book(self):
        """
        Handler para o botão 'Atualizar Livro'.
        Verifica se existe seleção e atualiza o registro correspondente.
        """
        try:
            # Garantir que um registro esteja selecionado
            index = self.listbox.curselection()
            if not index:
                raise ValueError("Selecione um livro na lista para atualizar.")

            code, title, author, genre, publisher, year = self._get_entry_values()
            updated = self.db.update_book(code, title, author, genre, publisher, year)
            if updated:
                messagebox.showinfo("Sucesso", f"Livro com código {code} atualizado.")
                self._populate_listbox()
                self.clear_entries()
            else:
                messagebox.showwarning("Atenção", f"Livro com código {code} não encontrado.")
        except ValueError as ve:
            messagebox.showwarning("Atenção", str(ve))
        except RuntimeError as re:
            messagebox.showerror("Erro", str(re))

    def delete_book(self):
        """
        Handler para o botão 'Deletar Livro'.
        Verifica seleção, pergunta confirmação e exclui o registro.
        """
        try:
            index = self.listbox.curselection()
            if not index:
                raise ValueError("Selecione um livro na lista para deletar.")

            selected_text = self.listbox.get(index)
            code = int(selected_text.split("|")[0].strip())

            confirm = messagebox.askyesno("Confirmação", f"Tem certeza que deseja deletar o livro com código {code}?")
            if not confirm:
                return

            deleted = self.db.delete_book(code)
            if deleted:
                messagebox.showinfo("Sucesso", f"Livro com código {code} deletado.")
                self._populate_listbox()
                self.clear_entries()
            else:
                messagebox.showwarning("Atenção", f"Livro com código {code} não encontrado.")
        except ValueError as ve:
            messagebox.showwarning("Atenção", str(ve))
        except RuntimeError as re:
            messagebox.showerror("Erro", str(re))

    def on_closing(self):
        """
        Chamado quando a janela principal é fechada.
        Fecha a conexão com o banco antes de sair.
        """
        try:
            self.db.close()
        finally:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = BookApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
