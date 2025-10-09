from sqlalchemy.orm import Session
import model
from sqlalchemy import func


#audit tables
def audit_record(db: Session):
    total_users = db.query(func.count(model.User.id)).scalar()
    total_books = db.query(func.count(model.Book.id)).scalar()
    total_loans = db.query(func.count(model.Loan.id)).scalar()
    active_loans = (
        db.query(func.count(model.Loan.id))
        .filter(model.Loan.status != model.LoanStatus.returned, model.Loan.Softdelete== 0)
        .scalar()
    )
    non_active_users = (
        db.query(func.count(model.User.id))
        .filter(model.User.Membership == 1)
        .scalar()
    )
    removed_books = (
        db.query(func.count(model.Book.id))
        .filter(model.Book.BookAvl== 0)
        .scalar()
    )
    new_audit = model.Audit(
        total_users=total_users,
        total_books=total_books,
        total_loans=total_loans,
        active_loans=active_loans,
        non_active_users=non_active_users,
        removed_books=removed_books
    )
    db.add(new_audit)
    db.commit()
    db.refresh(new_audit)
    return {
        "message": f"Audit record created successfully with id {new_audit.id}",
        "audit": {
            "total_users": total_users,
            "non_active_users": non_active_users,
            "total_books": total_books,
            "removed_books": removed_books,
            "total_loans": total_loans,
            "active_loans": active_loans,
            "audit_date": new_audit.audit_date
        }
    }
