import streamlit as st
import json
import os
from datetime import datetime

# Custom CSS for styling and background image
st.markdown(
    """
    <style>
   

    /* Button styling */
    .stButton button {
        background-color: blue;
        color: black;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton button:hover {
        background-color: #45a049;
    }

    /* Input styling */
    .stTextInput input {
        border-radius: 5px;
        padding: 10px;
    }

    /* Selectbox styling */
    .stSelectbox select {
        border-radius: 5px;
        padding: 10px;
    }

    /* Heading styling */
    .stMarkdown h1 {
        color: #4CAF50;
    }
    .stMarkdown h2 {
        color: #45a049;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


class BookCollection:
    """A class to manage a collection of books, allowing users to store and organize their reading materials."""

    def __init__(self):
        """Initialize a new book collection with an empty list and set up file storage."""
        self.book_list = []
        self.storage_file = "books_data.json"
        self.upload_folder = "uploaded_books"
        self.read_from_file()

        # Create the upload folder if it doesn't exist
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def read_from_file(self):
        """Load saved books from a JSON file into memory. If the file does not exist or is corrupted, start with an empty collection."""
        try:
            with open(self.storage_file, "r") as file:
                self.book_list = json.load(file)
            
            # Ensure all books have the 'pdf_file' key
            for book in self.book_list:
                if "pdf_file" not in book:
                    book["pdf_file"] = None  # Add the key with a default value
        except (FileNotFoundError, json.JSONDecodeError):
            self.book_list = []

    def save_to_file(self):
        """Store the current book collection to a JSON file for permanent storage."""
        with open(self.storage_file, "w") as file:
            json.dump(self.book_list, file, indent=4)

    def create_new_book(self):
        """Add a new book to the collection by gathering information from the user."""
        st.subheader("Add a New Book")
        book_title = st.text_input("Title")
        book_author = st.text_input("Author")
        publication_year = st.text_input("Publication Year")
        book_genre = st.text_input("Genre")
        is_book_read = st.selectbox("Have you read this book?", ["No", "Yes"]) == "Yes"
        pdf_file = st.file_uploader("Upload PDF Book", type=["pdf"])

        if st.button("Add Book"):
            new_book = {
                "title": book_title,
                "author": book_author,
                "year": publication_year,
                "genre": book_genre,
                "read": is_book_read,
                "pdf_file": None,  # Initialize with None
            }

            # Save the uploaded PDF file
            if pdf_file is not None:
                file_path = os.path.join(self.upload_folder, pdf_file.name)
                with open(file_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                new_book["pdf_file"] = file_path  # Update if PDF is uploaded

            self.book_list.append(new_book)
            self.save_to_file()
            st.success("Book added successfully!")

    def delete_book(self):
        """Remove a book from the collection using its title."""
        st.subheader("Remove a Book")
        book_title = st.text_input("Enter the title of the book to remove")

        if st.button("Remove Book"):
            for book in self.book_list:
                if book["title"].lower() == book_title.lower():
                    # Delete the associated PDF file if it exists
                    if "pdf_file" in book and book["pdf_file"] and os.path.exists(book["pdf_file"]):
                        os.remove(book["pdf_file"])
                    self.book_list.remove(book)
                    self.save_to_file()
                    st.success("Book removed successfully!")
                    return
            st.error("Book not found!")

    def find_book(self):
        """Search for books in the collection by title or author name."""
        st.subheader("Search for Books")
        search_type = st.selectbox("Search by:", ["Title", "Author"])
        search_text = st.text_input("Enter the search term").lower()

        if st.button("Search"):
            found_books = [
                book
                for book in self.book_list
                if search_text in book["title"].lower() or search_text in book["author"].lower()
            ]

            if found_books:
                st.write("Matching Books:")
                for index, book in enumerate(found_books, 1):
                    reading_status = "Read" if book["read"] else "Unread"
                    st.write(f"{index}. **{book['title']}** by {book['author']} ({book['year']}) - {reading_status}")
                    if "pdf_file" in book and book["pdf_file"]:
                        with open(book["pdf_file"], "rb") as f:
                            st.download_button(
                                label="Download PDF",
                                data=f,
                                file_name=os.path.basename(book["pdf_file"]),
                                mime="application/pdf",
                            )
            else:
                st.warning("No matching books found!")

    def update_book(self):
        """Modify the details of an existing book in the collection."""
        st.subheader("Update Book Details")
        book_title = st.text_input("Enter the title of the book you want to edit")

        if st.button("Find Book"):
            for book in self.book_list:
                if book["title"].lower() == book_title.lower():
                    st.write("Leave blank to keep the existing value.")
                    book["title"] = st.text_input("New title", book["title"])
                    book["author"] = st.text_input("New author", book["author"])
                    book["year"] = st.text_input("New Year", book["year"])
                    book["genre"] = st.text_input("New genre", book["genre"])
                    book["read"] = st.selectbox("Have you read this book?", ["No", "Yes"], index=1 if book["read"] else 0) == "Yes"

                    # Allow updating the PDF file
                    new_pdf_file = st.file_uploader("Upload new PDF Book", type=["pdf"])
                    if new_pdf_file is not None:
                        # Delete the old PDF file if it exists
                        if "pdf_file" in book and book["pdf_file"] and os.path.exists(book["pdf_file"]):
                            os.remove(book["pdf_file"])
                        # Save the new PDF file
                        file_path = os.path.join(self.upload_folder, new_pdf_file.name)
                        with open(file_path, "wb") as f:
                            f.write(new_pdf_file.getbuffer())
                        book["pdf_file"] = file_path

                    if st.button("Update Book"):
                        self.save_to_file()
                        st.success("Book updated successfully!")
                        return
            st.error("Book not found!")

    def show_all_books(self):
        """Display all books in the collection with their details."""
        st.subheader("Your Book Collection")
        if not self.book_list:
            st.warning("Your collection is empty!")
            return

        for index, book in enumerate(self.book_list, 1):
            reading_status = "Read" if book["read"] else "Unread"
            st.write(f"{index}. **{book['title']}** by {book['author']} ({book['year']}) - {reading_status}")
            if "pdf_file" in book and book["pdf_file"]:
                with open(book["pdf_file"], "rb") as f:
                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name=os.path.basename(book["pdf_file"]),
                        mime="application/pdf",
                    )
                # Display PDF in the UI
                st.markdown(f'<iframe src="{book["pdf_file"]}" width="700" height="1000"></iframe>', unsafe_allow_html=True)

    def show_reading_progress(self):
        """Calculate and display statistics about your reading progress."""
        st.subheader("Reading Progress")
        total_books = len(self.book_list)
        completed_books = sum(1 for book in self.book_list if book["read"])
        completion_rate = (completed_books / total_books * 100) if total_books > 0 else 0
        st.write(f"Total books in collection: {total_books}")
        st.write(f"Reading Progress: {completion_rate:.2f}%")

    def start_application(self):
        """Run the main application loop with a user-friendly menu interface."""
        st.title("📚 Book Collection Manager 📚")
        menu = [
            "Add a New Book",
            "Remove a Book",
            "Search for Books",
            "Update Book Details",
            "View All Books",
            "View Reading Progress",
        ]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Add a New Book":
            self.create_new_book()
        elif choice == "Remove a Book":
            self.delete_book()
        elif choice == "Search for Books":
            self.find_book()
        elif choice == "Update Book Details":
            self.update_book()
        elif choice == "View All Books":
            self.show_all_books()
        elif choice == "View Reading Progress":
            self.show_reading_progress()


if __name__ == "__main__":
    book_manager = BookCollection()
    book_manager.start_application()



