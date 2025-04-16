from core.config import engine, Base

# Create tables at startup
def init_db():
    Base.metadata.create_all(bind=engine)
