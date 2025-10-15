import os
import sys
import json
import enum
import pytest
from fastapi import Depends
from passlib.context import CryptContext

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import app
from config import get_db
import model

from auth import admin_required,get_current_user

# ---------------- Global constants ----------------
MOCK_FILE = "mock_db.json"

# ---------------- Mock Query Class ----------------
class MockQuery:
    def __init__(self, data):
        self.data = data
        self._filters = []

    def filter(self, *conditions):
        for cond in conditions:
            try:
                key = cond.left.name
                val = cond.right.value
                self._filters.append(lambda item, key=key, val=val: item.get(key) == val)
            except AttributeError:
                self._filters.append(cond)
        return self

    def first(self):
        results = self.data
        for f in self._filters:
            results = list(filter(f, results))
        return results[0] if results else None

    def all(self):
        results = self.data
        for f in self._filters:
            results = list(filter(f, results))
        return results


# ---------------- MockDB Class ----------------
class MockDB:
    def __init__(self, file_path=MOCK_FILE):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"books": [], "users": [], "loans": []}, f, indent=4)
        self.load()

    def load(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.db = json.load(f)

    def save(self):
        def default(o):
            if isinstance(o, enum.Enum):
                return o.value
            raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.db, f, indent=4, default=default)

    def _get_next_id(self, table_name):
        data = self.db.get(table_name, [])
        if not data:
            return 1
        return max(item.get("id", 0) for item in data) + 1

    def to_dict(self, record):
        if hasattr(record, "model_dump"):
            return record.model_dump()
        elif hasattr(record, "__dict__"):
            d = dict(record.__dict__)
            d.pop("_sa_instance_state", None)
            return d
        elif isinstance(record, dict):
            return record
        else:
            raise TypeError(f"Unsupported record type: {type(record)}")

    def add(self, record, table_name=None):
        if table_name is None:
            if isinstance(record, model.User):
                table_name = "users"
            elif isinstance(record, model.Book):
                table_name = "books"
            elif isinstance(record, model.Loan):
                table_name = "loans"
            else:
                raise ValueError("Unknown record type. Provide table_name.")

        if table_name not in self.db:
            self.db[table_name] = []

        record_dict = self.to_dict(record)

        # ✅ Password hashing for users
        if table_name == "users":
            pwd = record_dict.get("password")
            if pwd:
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                # Only hash if not already hashed
                if not record_dict.get("hashed_password") or not pwd_context.identify(record_dict["password"]):
                    record_dict["hashed_password"] = pwd_context.hash(pwd.encode("utf-8")[:72])
                record_dict.pop("password", None)

        # ✅ Assign ID
        if not record_dict.get("id"):
            record_dict["id"] = self._get_next_id(table_name)

        # ✅ Derived fields
        if table_name == "books" and "available_copies" not in record_dict:
            record_dict["available_copies"] = record_dict.get("total_copies", 1)
        if table_name == "loans" and "status" not in record_dict:
            record_dict["status"] = "BORROWED"

        self.db[table_name].append(record_dict)
        self.save()

        if hasattr(record, "__dict__"):
            record.id = record_dict["id"]

        return record

    def commit(self):
        self.save()

    def refresh(self, obj, table_name=None):
        return obj

    def query(self, table_name):
        data = self.db.get(table_name, [])
        return MockQuery(data)

    def update(self, table_name, record_id, updates):
        for item in self.db.get(table_name, []):
            if item["id"] == record_id:
                item.update(updates)
                self.save()
                return item
        return None

    def add_loan(self, loan_record):
        book_id = loan_record["book_id"]
        book = next((b for b in self.db["books"] if b["id"] == book_id), None)
        if not book:
            raise ValueError("Book not found")
        if book["available_copies"] <= 0:
            raise ValueError("No copies available")
        book["available_copies"] -= 1
        if "status" not in loan_record:
            loan_record["status"] = "BORROWED"
        return self.add(loan_record, table_name="loans")

    def return_loan(self, loan_id):
        loan = next((l for l in self.db["loans"] if l["id"] == loan_id), None)
        if not loan:
            raise ValueError("Loan not found")
        if loan["status"] != "BORROWED":
            raise ValueError("Loan already returned")
        loan["status"] = "RETURNED"
        book_id = loan["book_id"]
        book = next((b for b in self.db["books"] if b["id"] == book_id), None)
        if book:
            book["available_copies"] += 1
        self.save()
        return loan


# ---------------- Fixtures ----------------
@pytest.fixture(scope="function")
def mock_db():
    if os.path.exists(MOCK_FILE):
        os.remove(MOCK_FILE)
    db = MockDB(MOCK_FILE)
    db.db = {"books": [], "users": [], "loans": []}
    db.save()
    return db


@pytest.fixture(scope="function")
def client(mock_db):
    mock_db.db = {"books": [], "users": [], "loans": []}
    mock_db.save()

    # ✅ Skip authentication if get_current_user exists
    try:

        class MockUser:
            def __init__(self):
                self.id = 1
                self.name = "test_user"
                self.role = model.Roles.ADMIN
        app.dependency_overrides[get_current_user] = lambda: MockUser()
        app.dependency_overrides[admin_required] = lambda: MockUser()
    except ImportError:
        pass

    # ✅ Inject mock DB
    app.dependency_overrides[get_db] = lambda: mock_db

    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c

    # ✅ Clean up overrides
    app.dependency_overrides = {}
