from fastapi import FastAPI
from router.book_endpoint import router
from router.user_endpoint import router2
from router.loan_endpoint import router3
from router.audit_endpoint import router4

app = FastAPI()


app.include_router(router)
app.include_router(router2)
app.include_router(router3)
app.include_router(router4)