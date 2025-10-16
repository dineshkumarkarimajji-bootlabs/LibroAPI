import threading
import requests


url_1="http://127.0.0.1:8000/loans/"
url_2="http://127.0.0.1:8000/loans/"

token_1="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyZGluZXNoMDRAZXhhbXBsZS5jb20iLCJpZCI6Nywicm9sZSI6InVzZXIiLCJleHAiOjE3NjA2MDg2MTJ9.9BfV5N4CFlInBmJb-5gSsGhpT5CdIsPtDeLUtzQt9tI"
token_2="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYXlhbnRoQGV4YW1wbGUuY29tIiwiaWQiOjksInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzYwNjA4ODAzfQ.RFi2Nck5JKFN504l6sNvH3-gq-mAVj358tSH82UAPi0"

def borrow_book(url, data, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.post(url, json=data, headers=headers)
        print(f"{url} -> {r.status_code}, {r.json()}")
    except Exception as e:
        print(f"Error calling {url}: {e}")

t1 = threading.Thread(target=borrow_book, args=(url_1, { "book_id": 5,"user_id": 7}, token_1)) 
t2 = threading.Thread(target=borrow_book, args=(url_2, {"book_id": 5,"user_id": 9},token_2))

t1.start()
t2.start()
t1.join()
t2.join()