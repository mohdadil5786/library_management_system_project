import streamlit as st

# --- OOP Classes ---
class Book:
    def __init__(self, book_id, title, author, copies):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.__copies = copies
        self.borrowed_by = []  # list of usernames who borrowed

    def is_available(self):
        return self.__copies > 0

    def borrow_book(self, username):
        if self.is_available():
            self.__copies -= 1
            self.borrowed_by.append(username)
            if self.__copies == 0:
                return f"Book '{self.title}' borrowed successfully! ⚠️ All copies are now borrowed."
            else:
                return f"Book '{self.title}' borrowed successfully! Remaining copies: {self.__copies}"
        else:
            return f"Book '{self.title}' is currently unavailable. ❌ No copies left."

    def return_book(self, username):
        if username in self.borrowed_by:
            self.__copies += 1
            self.borrowed_by.remove(username)
            return f"Book '{self.title}' returned successfully! Available copies: {self.__copies}"
        else:
            return f"You did not borrow '{self.title}'! ❌"

    def display_info(self):
        return {
            "ID": self.book_id,
            "Title": self.title,
            "Author": self.author,
            "Available Copies": self.__copies
        }

class EBook(Book):
    def __init__(self, book_id, title, author, file_size_mb):
        super().__init__(book_id, title, author, copies=1000)  # effectively unlimited
        self.file_size_mb = file_size_mb

    def display_info(self):
        return {
            "ID": self.book_id,
            "Title": f"{self.title} (E-Book)",
            "Author": self.author,
            "Available Copies": "Unlimited",
            "File Size (MB)": self.file_size_mb
        }

class Library:
    def __init__(self):
        self.books = {}

    def add_book(self, book):
        self.books[book.book_id] = book

    def borrow_book(self, book_id, username):
        if book_id in self.books:
            return self.books[book_id].borrow_book(username)
        else:
            return "Book ID not found! ❌"

    def return_book(self, book_id, username):
        if book_id in self.books:
            return self.books[book_id].return_book(username)
        else:
            return "Book ID not found! ❌"

    def get_all_books(self):
        return [book.display_info() for book in self.books.values()]

# --- Streamlit App ---
st.set_page_config(page_title="📚 Library Management App", layout="wide")
st.title("📚 Library Management System")

# In-memory storage for users
if "users" not in st.session_state:
    st.session_state.users = {}  # username -> password

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# Initialize library
if "library" not in st.session_state:
    lib = Library()
    lib.add_book(Book(101, "1984", "George Orwell", 3))
    lib.add_book(Book(102, "To Kill a Mockingbird", "Harper Lee", 2))
    lib.add_book(EBook(201, "Python Programming", "John Doe", 5))
    st.session_state.library = lib

library = st.session_state.library

# --- User Registration/Login ---
def register_user(username, password):
    if username in st.session_state.users:
        st.warning("Username already exists! ❌")
    else:
        st.session_state.users[username] = password
        st.success("Registration successful! ✅")

def login_user(username, password):
    if username in st.session_state.users and st.session_state.users[username] == password:
        st.session_state.logged_in_user = username
        st.success(f"Logged in as {username} ✅")
    else:
        st.error("Invalid username or password ❌")

# --- Login/Register Interface ---
if st.session_state.logged_in_user is None:
    st.subheader("👤 Login or Register")
    option = st.radio("Choose", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Register" and st.button("Register"):
        register_user(username, password)

    if option == "Login" and st.button("Login"):
        login_user(username, password)

# --- Logged-in User Operations ---
else:
    st.sidebar.write(f"Logged in as: **{st.session_state.logged_in_user}**")
    action = st.sidebar.selectbox("Choose Operation", ["View Books", "Borrow Book", "Return Book", "Logout"])

    def display_books():
        books = library.get_all_books()
        st.subheader("📖 Available Books")
        for book in books:
            st.write(f"ID: {book['ID']} | Title: {book['Title']} | Author: {book['Author']} | Available Copies: {book['Available Copies']}")

    if action == "Logout":
        st.session_state.logged_in_user = None
        st.experimental_rerun()

    elif action == "View Books":
        display_books()

    elif action == "Borrow Book":
        display_books()
        book_id = st.number_input("Enter Book ID to Borrow", min_value=1, step=1)
        if st.button("Borrow"):
            result = library.borrow_book(book_id, st.session_state.logged_in_user)
            st.success(result)
            display_books()  # show updated inventory

    elif action == "Return Book":
        book_id = st.number_input("Enter Book ID to Return", min_value=1, step=1, key="return_book")
        if st.button("Return"):
            result = library.return_book(book_id, st.session_state.logged_in_user)
            st.success(result)
            display_books()  # show updated inventory