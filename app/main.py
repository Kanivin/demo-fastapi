from fastapi import FastAPI
from api.register import load_dynamic_routes
from db import db

app = FastAPI()

# Register DB tables at startup
@app.on_event("startup")
def startup():
    db.init_db()

# Include dynamic API routers
app.include_router(load_dynamic_routes())
