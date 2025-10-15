from fastapi import FastAPI
from router.main_endpoint import router,router1,router2,router3,router4


app = FastAPI(title=("Library Management System"))


app.include_router(router)
app.include_router(router1)
app.include_router(router2)
app.include_router(router3)
app.include_router(router4)