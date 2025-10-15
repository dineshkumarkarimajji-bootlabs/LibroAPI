from mock_conftest import MockDB

def test_add_book():
    db = MockDB()
    db.add({
        "title": "test_book1",
        "author": "abc",
        "isbn": "isbn001",
        "publication_year": 2000,
        "total_copies": 2,
        "available_copies": 2
    },
    table_name="books")
    data = db.query("books").all()
    assert any(b["title"] == "test_book1" for b in data)

def test_add_user():
    db = MockDB()
    db.add({"name": "Dinesh", "email": "dinesh@gmail.com"}, table_name="users")
    data = db.query("users").all()
    assert any(u["email"] == "dinesh@gmail.com" for u in data)

def test_add_loan():
    db = MockDB()
    db.add_loan({"book_id": 1, "user_id": 1})
    data = db.query("loans").all()
    assert any(l["user_id"] == 1 for l in data)

    books = db.query("books").all()
    assert books[0]["available_copies"] == 1

def test_return_loan():
    db = MockDB()

    # First, make sure we have a book and a user to create a loan
    book = db.add({
        "title": "Test Book2",
        "author": "Author",
        "isbn": "isbn002",
        "publication_year": 2025,
        "total_copies": 2
    }, table_name="books")

    user = db.add({
        "name": "test",
        "email": "test@gmail.com"
    }, table_name="users")

    # Add a loan
    loan = db.add_loan({"book_id": book["id"], "user_id": user["id"]})

    # Return the loan
    returned_loan = db.return_loan(loan["id"])
    assert returned_loan["status"] == "RETURNED"

    # Check that the book's available copies increased
    books = db.query("books").all()
    book_after = next(b for b in books if b["id"] == book["id"])
    assert book_after["available_copies"] == book["total_copies"]

