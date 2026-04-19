# ================================================================
# MEMBER 1: MODEL CLASSES (Book, Member, Library)
# Topic: "OOP Business Logic - Core Classes"
# Concepts: Encapsulation, Properties, Validation, Composition
# ================================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import re


class Book:
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn
        self._available = True

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Invalid title")
        self._title = value.strip()

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Invalid author")
        self._author = value.strip()

    @property
    def isbn(self):
        return self._isbn

    @isbn.setter
    def isbn(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Invalid ISBN")
        clean = value.strip().replace("-", "")
        if not re.match(r'^\d{10}$|^\d{13}$', clean):
            raise ValueError("ISBN must be 10 or 13 digits")
        self._isbn = value.strip()

    @property
    def available(self):
        return self._available

    def borrow(self):
        if not self._available:
            raise Exception("Book is not available")
        self._available = False

    def return_book(self):
        self._available = True

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "available": self.available
        }


class Member:
    def __init__(self, name, member_id):
        self.name = name
        self.member_id = member_id
        self._borrowed_books = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Invalid name")
        self._name = value.strip()

    @property
    def member_id(self):
        return self._member_id

    @member_id.setter
    def member_id(self, value):
        if not re.match(r'^M\d+$', value):
            raise ValueError("Member ID must be like M001")
        self._member_id = value

    @property
    def borrowed_books(self):
        return self._borrowed_books.copy()

    def borrow_book(self, book):
        if len(self._borrowed_books) >= 3:
            raise Exception("Borrow limit reached")
        if not book.available:
            raise Exception("Book not available")
        book.borrow()
        self._borrowed_books.append(book)

    def return_book(self, book):
        if book not in self._borrowed_books:
            raise Exception("Book not borrowed by this member")
        book.return_book()
        self._borrowed_books.remove(book)

    def to_dict(self):
        return {
            "name": self.name,
            "member_id": self.member_id,
            "borrowed_count": len(self._borrowed_books)
        }


class Library:
    def __init__(self, name):
        self.name = name
        self._books = {}
        self._members = {}

    def add_book(self, book):
        if book.isbn in self._books:
            raise Exception("Book with this ISBN already exists")
        self._books[book.isbn] = book

    def remove_book(self, isbn):
        book = self._books.get(isbn)
        if not book:
            raise Exception("Book not found")
        if not book.available:
            raise Exception("Cannot delete a borrowed book")
        del self._books[isbn]

    def add_member(self, member):
        if member.member_id in self._members:
            raise Exception("Member with this ID already exists")
        self._members[member.member_id] = member

    def remove_member(self, member_id):
        member = self._members.get(member_id)
        if not member:
            raise Exception("Member not found")
        if member.borrowed_books:
            raise Exception("Member still has borrowed books")
        del self._members[member_id]

    def get_book(self, isbn):
        return self._books.get(isbn)

    def get_member(self, member_id):
        return self._members.get(member_id)

    def borrow_book(self, member_id, isbn):
        member = self._members.get(member_id)
        book = self._books.get(isbn)
        if not member:
            raise Exception("Member not found")
        if not book:
            raise Exception("Book not found")
        member.borrow_book(book)

    def return_book(self, member_id, isbn):
        member = self._members.get(member_id)
        book = self._books.get(isbn)
        if not member:
            raise Exception("Member not found")
        if not book:
            raise Exception("Book not found")
        member.return_book(book)

    def get_all_books(self):
        return list(self._books.values())

    def get_all_members(self):
        return list(self._members.values())

    def search_books(self, keyword):
        keyword = keyword.lower()
        return [book for book in self._books.values()
                if keyword in book.title.lower() or keyword in book.author.lower()]


# ================================================================
# MEMBER 2: DIALOG CLASSES (AddEditBookDialog, AddEditMemberDialog)
# Topic: "Modal Dialog Windows for CRUD Operations"
# Concepts: Inheritance (Toplevel), Modal Dialogs, Callbacks, Form Handling
# ================================================================

class AddEditBookDialog(tk.Toplevel):
    def __init__(self, parent, book=None, callback=None):
        super().__init__(parent)
        self.parent = parent
        self.book = book
        self.callback = callback
        self.result = None
        
        self.title("Add Book" if book is None else "Edit Book")
        self.geometry("400x200")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
        self._create_widgets()
        
        if book:
            self.entry_title.insert(0, book.title)
            self.entry_author.insert(0, book.author)
            self.entry_isbn.insert(0, book.isbn)
            self.entry_isbn.config(state="disabled")
        
        self.center_window()
        self.wait_window()
    
    def _create_widgets(self):
        tk.Label(self, text="Title:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry_title = tk.Entry(self, width=35)
        self.entry_title.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(self, text="Author:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.entry_author = tk.Entry(self, width=35)
        self.entry_author.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(self, text="ISBN:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.entry_isbn = tk.Entry(self, width=35)
        self.entry_isbn.grid(row=2, column=1, padx=10, pady=10)
        
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        tk.Button(btn_frame, text="Save", command=self.save,
                 bg="#27ae60", fg="white", width=10).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancel", command=self.cancel,
                 bg="#e74c3c", fg="white", width=10).pack(side="left", padx=10)
        
        self.entry_title.focus()
    
    def center_window(self):
        self.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        self.geometry(f"+{x}+{y}")
    
    def save(self):
        title = self.entry_title.get().strip()
        author = self.entry_author.get().strip()
        isbn = self.entry_isbn.get().strip()
        
        if not title or not author or not isbn:
            messagebox.showwarning("Missing Information", 
                                  "All fields are required.", parent=self)
            return
        
        self.result = (title, author, isbn)
        if self.callback:
            self.callback(title, author, isbn)
        self.destroy()
    
    def cancel(self):
        self.result = None
        self.destroy()


class AddEditMemberDialog(tk.Toplevel):
    def __init__(self, parent, member=None, callback=None):
        super().__init__(parent)
        self.parent = parent
        self.member = member
        self.callback = callback
        self.result = None
        
        self.title("Add Member" if member is None else "Edit Member")
        self.geometry("350x150")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
        self._create_widgets()
        
        if member:
            self.entry_name.insert(0, member.name)
            self.entry_id.insert(0, member.member_id)
            self.entry_id.config(state="disabled")
        
        self.center_window()
        self.wait_window()
    
    def _create_widgets(self):
        tk.Label(self, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry_name = tk.Entry(self, width=30)
        self.entry_name.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(self, text="Member ID:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.entry_id = tk.Entry(self, width=30)
        self.entry_id.grid(row=1, column=1, padx=10, pady=10)
        
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        tk.Button(btn_frame, text="Save", command=self.save,
                 bg="#27ae60", fg="white", width=10).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancel", command=self.cancel,
                 bg="#e74c3c", fg="white", width=10).pack(side="left", padx=10)
        
        self.entry_name.focus()
    
    def center_window(self):
        self.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        self.geometry(f"+{x}+{y}")
    
    def save(self):
        name = self.entry_name.get().strip()
        member_id = self.entry_id.get().strip()
        
        if not name or not member_id:
            messagebox.showwarning("Missing Information",
                                  "All fields are required.", parent=self)
            return
        
        self.result = (name, member_id)
        if self.callback:
            self.callback(name, member_id)
        self.destroy()
    
    def cancel(self):
        self.result = None
        self.destroy()


# ================================================================
# MEMBER 3: TRANSACTION DIALOG + MAIN APP SETUP
# Topic: "BorrowReturnDialog + LibraryApp Initialization"
# Concepts: Combobox, Dynamic Data Loading, Inheritance (tk.Tk), Menu Bar, Notebook Tabs
# ================================================================

class BorrowReturnDialog(tk.Toplevel):
    def __init__(self, parent, library, is_borrow=True, callback=None):
        super().__init__(parent)
        self.parent = parent
        self.library = library
        self.is_borrow = is_borrow
        self.callback = callback
        
        self.title("Borrow Book" if is_borrow else "Return Book")
        self.geometry("400x200")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
        self._create_widgets()
        self.center_window()
        self.wait_window()
    
    def _create_widgets(self):
        tk.Label(self, text="Select Member:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.member_combo = ttk.Combobox(self, width=30, state="readonly")
        members = self.library.get_all_members()
        self._member_list = members
        self.member_combo["values"] = [f"{m.name} ({m.member_id})" for m in members]
        self.member_combo.grid(row=0, column=1, padx=10, pady=10)
        self.member_combo.bind("<<ComboboxSelected>>", self._update_book_list)

        tk.Label(self, text="Select Book:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.book_combo = ttk.Combobox(self, width=30, state="readonly")
        if self.is_borrow:
            books = [b for b in self.library.get_all_books() if b.available]
            self.book_combo["values"] = [f"{b.title} ({b.isbn})" for b in books]
        else:
            self.book_combo["values"] = []
        self.book_combo.grid(row=1, column=1, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

        action_text = "Borrow" if self.is_borrow else "Return"
        color = "#e74c3c" if self.is_borrow else "#27ae60"

        tk.Button(btn_frame, text=action_text, command=self.process,
                 bg=color, fg="white", width=12).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancel", command=self.cancel,
                 bg="#95a5a6", fg="white", width=12).pack(side="left", padx=10)

    def _update_book_list(self, event=None):
        if self.is_borrow:
            return
        idx = self.member_combo.current()
        member = self._member_list[idx]
        self.book_combo["values"] = [f"{b.title} ({b.isbn})" for b in member.borrowed_books]
        self.book_combo.set("")
    
    def center_window(self):
        self.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        self.geometry(f"+{x}+{y}")
    
    def process(self):
        member_sel = self.member_combo.get()
        book_sel = self.book_combo.get()
        
        if not member_sel or not book_sel:
            messagebox.showwarning("Selection Required",
                                  "Please select both member and book.", parent=self)
            return
        
        
        
        idx = self.member_combo.current()
        member_id = self._member_list[idx].member_id
        isbn = book_sel.split("(")[-1].rstrip(")")
        
        try:
            if self.is_borrow:
                self.library.borrow_book(member_id, isbn)
                messagebox.showinfo("Success", "Book borrowed successfully!", parent=self)
            else:
                self.library.return_book(member_id, isbn)
                messagebox.showinfo("Success", "Book returned successfully!", parent=self)
            
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
    
    def cancel(self):
        self.destroy()


class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("900x600")
        
        self.library = Library("City Library")
        
        self._add_sample_data()
        self._create_menu()
        self._create_widgets()
        
        self.status = tk.Label(self, text="Ready", anchor="w", 
                              relief="sunken", bg="#ecf0f1")
        self.status.pack(side="bottom", fill="x")
        
        self._update_books_tree()
        self._update_members_tree()
    
    def _add_sample_data(self):
        try:
            self.library.add_book(Book("1984", "George Orwell", "9780451524935"))
            self.library.add_book(Book("To Kill a Mockingbird", "Harper Lee", "9780061935466"))
            self.library.add_book(Book("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565"))
            self.library.add_book(Book("Pride and Prejudice", "Jane Austen", "9780141439518"))
            self.library.add_book(Book("The Catcher in the Rye", "J.D. Salinger", "9780316769174"))
            
            self.library.add_member(Member("Alice Johnson", "M001"))
            self.library.add_member(Member("Bob Smith", "M002"))
            self.library.add_member(Member("Charlie Brown", "M003"))
        except Exception as e:
            print(f"Sample data error: {e}")
    
    def _create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Books", command=self.export_books)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        books_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Books", menu=books_menu)
        books_menu.add_command(label="Add Book", command=self.add_book)
        books_menu.add_command(label="Edit Selected", command=self.edit_book)
        books_menu.add_command(label="Delete Selected", command=self.delete_book)
        
        members_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Members", menu=members_menu)
        members_menu.add_command(label="Add Member", command=self.add_member)
        members_menu.add_command(label="Edit Selected", command=self.edit_member)
        members_menu.add_command(label="Delete Selected", command=self.delete_member)
        
        trans_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Transactions", menu=trans_menu)
        trans_menu.add_command(label="Borrow Book", command=self.borrow_book)
        trans_menu.add_command(label="Return Book", command=self.return_book)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def _create_widgets(self):
        title_frame = tk.Frame(self, bg="#3498db")
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="Library Management System",
                font=("Arial", 18, "bold"), bg="#3498db", fg="white").pack(pady=10)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.books_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.books_frame, text="Books")
        self._create_books_tab()
        
        self.members_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.members_frame, text="Members")
        self._create_members_tab()
        
        self.trans_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.trans_frame, text="Transactions")
        self._create_transactions_tab()


# ================================================================
# MEMBER 4: MAIN APP TABS + ALL OPERATIONS
# Topic: "Tab Creation + CRUD Operations + Event Handling"
# Concepts: Treeview, Search, Add/Edit/Delete Operations, File Export, Event Binding
# ================================================================

    def _create_books_tab(self):
        toolbar = tk.Frame(self.books_frame)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        tk.Button(toolbar, text="Add Book", command=self.add_book,
                 bg="#27ae60", fg="white").pack(side="left", padx=2)
        tk.Button(toolbar, text="Edit", command=self.edit_book,
                 bg="#3498db", fg="white").pack(side="left", padx=2)
        tk.Button(toolbar, text="Delete", command=self.delete_book,
                 bg="#e74c3c", fg="white").pack(side="left", padx=2)
        
        tk.Label(toolbar, text="Search:").pack(side="left", padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.search_books())
        search_entry = tk.Entry(toolbar, textvariable=self.search_var, width=25)
        search_entry.pack(side="left", padx=2)
        
        tree_frame = tk.Frame(self.books_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        columns = ("Title", "Author", "ISBN", "Status")
        self.books_tree = ttk.Treeview(tree_frame, columns=columns, 
                                       show="headings", yscrollcommand=scrollbar.set)
        
        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=150)
        
        self.books_tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.books_tree.yview)
        self.books_tree.bind("<Double-Button-1>", lambda e: self.edit_book())
    
    def _create_members_tab(self):
        toolbar = tk.Frame(self.members_frame)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        tk.Button(toolbar, text="Add Member", command=self.add_member,
                 bg="#27ae60", fg="white").pack(side="left", padx=2)
        tk.Button(toolbar, text="Edit", command=self.edit_member,
                 bg="#3498db", fg="white").pack(side="left", padx=2)
        tk.Button(toolbar, text="Delete", command=self.delete_member,
                 bg="#e74c3c", fg="white").pack(side="left", padx=2)
        
        tree_frame = tk.Frame(self.members_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        columns = ("Name", "Member ID", "Books Borrowed")
        self.members_tree = ttk.Treeview(tree_frame, columns=columns,
                                         show="headings", yscrollcommand=scrollbar.set)
        
        for col in columns:
            self.members_tree.heading(col, text=col)
            self.members_tree.column(col, width=180)
        
        self.members_tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.members_tree.yview)
        self.members_tree.bind("<Double-Button-1>", lambda e: self.edit_member())
    
    def _create_transactions_tab(self):
        center_frame = tk.Frame(self.trans_frame)
        center_frame.place(relx=0.5, rely=0.4, anchor="center")
        
        tk.Label(center_frame, text="Book Transactions", 
                font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Button(center_frame, text="Borrow Book", command=self.borrow_book,
                 bg="#e74c3c", fg="white", font=("Arial", 12), 
                 width=20, height=2).pack(pady=10)
        
        tk.Button(center_frame, text="Return Book", command=self.return_book,
                 bg="#27ae60", fg="white", font=("Arial", 12),
                 width=20, height=2).pack(pady=10)
        
        stats_frame = tk.LabelFrame(self.trans_frame, text="Statistics", 
                                    font=("Arial", 10, "bold"))
        stats_frame.place(relx=0.5, rely=0.8, anchor="center")
        
        self.stats_label = tk.Label(stats_frame, text="", font=("Arial", 10))
        self.stats_label.pack(padx=20, pady=10)
        self._update_stats()
    
    def _update_books_tree(self):
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        for book in self.library.get_all_books():
            status = "Available" if book.available else "Borrowed"
            self.books_tree.insert("", "end", 
                                   values=(book.title, book.author, book.isbn, status))
        self._update_stats()
    
    def _update_members_tree(self):
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        for member in self.library.get_all_members():
            count = len(member.borrowed_books)
            self.members_tree.insert("", "end",
                                     values=(member.name, member.member_id, count))
        self._update_stats()
    
    def _update_stats(self):
        total_books = len(self.library.get_all_books())
        available = sum(1 for b in self.library.get_all_books() if b.available)
        borrowed = total_books - available
        members = len(self.library.get_all_members())
        stats = f"Total Books: {total_books} | Available: {available} | Borrowed: {borrowed} | Members: {members}"
        self.stats_label.config(text=stats)
    
    def search_books(self):
        keyword = self.search_var.get()
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        if keyword:
            books = self.library.search_books(keyword)
        else:
            books = self.library.get_all_books()
        for book in books:
            status = "Available" if book.available else "Borrowed"
            self.books_tree.insert("", "end",
                                   values=(book.title, book.author, book.isbn, status))
    
    def add_book(self):
        def on_save(title, author, isbn):
            try:
                book = Book(title, author, isbn)
                self.library.add_book(book)
                self._update_books_tree()
                self.status.config(text=f"Added: {title}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        AddEditBookDialog(self, callback=on_save)
    
    def edit_book(self):
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a book to edit.")
            return
        values = self.books_tree.item(selected[0])["values"]
        isbn = str(values[2])
        book = self.library.get_book(isbn)
        def on_save(title, author, isbn):
            book.title = title
            book.author = author
            self._update_books_tree()
            self.status.config(text=f"Updated: {title}")
        AddEditBookDialog(self, book=book, callback=on_save)
    
    def delete_book(self):
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a book to delete.")
            return
        values = self.books_tree.item(selected[0])["values"]
        title = values[0]
        isbn = str(values[2])
        if messagebox.askyesno("Confirm Delete", f"Delete '{title}'?"):
            try:
                self.library.remove_book(isbn)
                self._update_books_tree()
                self.status.config(text=f"Deleted: {title}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def add_member(self):
        def on_save(name, member_id):
            try:
                member = Member(name, member_id)
                self.library.add_member(member)
                self._update_members_tree()
                self.status.config(text=f"Added member: {name}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        AddEditMemberDialog(self, callback=on_save)
    
    def edit_member(self):
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a member to edit.")
            return
        values = self.members_tree.item(selected[0])["values"]
        member_id = values[1]
        member = self.library.get_member(member_id)
        def on_save(name, member_id):
            member.name = name
            self._update_members_tree()
            self.status.config(text=f"Updated member: {name}")
        AddEditMemberDialog(self, member=member, callback=on_save)
    
    def delete_member(self):
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a member to delete.")
            return
        values = self.members_tree.item(selected[0])["values"]
        name = values[0]
        member_id = values[1]
        if messagebox.askyesno("Confirm Delete", f"Delete member '{name}'?"):
            try:
                self.library.remove_member(member_id)
                self._update_members_tree()
                self.status.config(text=f"Deleted member: {name}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def borrow_book(self):
        def on_complete():
            self._update_books_tree()
            self._update_members_tree()
            self.status.config(text="Book borrowed successfully")
        BorrowReturnDialog(self, self.library, is_borrow=True, callback=on_complete)
    
    def return_book(self):
        def on_complete():
            self._update_books_tree()
            self._update_members_tree()
            self.status.config(text="Book returned successfully")
        BorrowReturnDialog(self, self.library, is_borrow=False, callback=on_complete)
    
    def export_books(self):
        filename = filedialog.asksaveasfilename(
            title="Export Books",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            try:
                data = [book.to_dict() for book in self.library.get_all_books()]
                with open(filename, "w") as f:
                    json.dump(data, f, indent=2)
                messagebox.showinfo("Success", f"Exported to {filename}")
                self.status.config(text=f"Exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def show_about(self):
        messagebox.showinfo("About", 
                           "Library Management System\n\n"
                           "Version: 1.0\n"
                           "OOP Project\n\n"
                           "Created with Python & Tkinter")


if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()