import pytest

# All API requests will go through this db_session (which is actually a TestClient)
# so we don’t need to create another TestClient

def test_create_book_api(client):
    book_data = {
        "title": "Test Book",
        "author": "Author A",
        "isbn": "ISBFEV",
        "publication_year": 2025,
        "total_copies": 5,
        "available_copies": 5
    }
    response = client.post("/books/", json=book_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Book"

def test_create_user_api(client):
    user_data = {
        "name": "new user",
        "email": "user1@gmail.com"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user1@gmail.com"




def test_create_loan_api(client):
    loan_data={
        "book_id": 1,
        "user_id": 1
    }
    response=client.post("/loans/",json=loan_data)
    assert response.status_code==200
    data = response.json()
    assert data["status"]=="borrowed"




def test_return_book_api(client):
    id=1
    response = client.put(f"/loan/{id}")

    assert response.status_code == 200
    data = response.json()

