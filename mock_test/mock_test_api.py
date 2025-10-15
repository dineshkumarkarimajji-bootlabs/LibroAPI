from mock_conftest import client, mock_db

def test_create_and_return_loan_flow(client, mock_db):
    # 1️ Add a user
    user = {"name": "admin", "email": "a@b.com", "role": "admin", "password": "123456"}
    resp_user = client.post("/users/", json=user)
    assert resp_user.status_code in [200, 201]

    # Add a book
    book = {
        "title": "Test Book3",
        "author": "Author",
        "isbn": "isbn03",
        "publication_year": 2020,
        "total_copies": 2
    }
    resp_book = client.post("/books/", json=book)
    assert resp_book.status_code in [200, 201]

    #  Get IDs from MockDB
    user_id = mock_db.query("users").first()["id"]
    book_id = mock_db.query("books").first()["id"]

    #  Create a loan via MockDB
    loan = {"user_id": user_id, "book_id": book_id}
    mock_db.add_loan(loan)

    # Verify loan created
    loan_data = mock_db.query("loans").first()
    book_data = mock_db.query("books").first()
    assert loan_data["status"] == "BORROWED"
    assert book_data["available_copies"] == book_data["total_copies"] - 1

    #  Return the loan
    returned_loan = mock_db.return_loan(loan_data["id"])

    #  Verify returned state
    loan_data = mock_db.query("loans").first()
    book_data = mock_db.query("books").first()
    assert loan_data["status"] == "RETURNED"
    assert book_data["available_copies"] == book_data["total_copies"]

    # Persist changes to JSON
    mock_db.commit()
