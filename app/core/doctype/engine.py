from sqlalchemy.orm import Session
from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

def create_document(db: Session, model_cls, data: dict):
    try:
        # Print the data and model class for debugging
        print(f"Creating document with model: {model_cls.__name__} and data: {data}")

        # Ensure the data matches the model's expected fields
        doc = model_cls(**data)

        # Add and commit the document to the database
        db.add(doc)
        db.commit()
        
        # Refresh to get the latest state of the document
        db.refresh(doc)
        
        # Return the created document
        return doc

    except SQLAlchemyError as e:
        # Catch SQLAlchemy specific errors
        db.rollback()
        print(f"❌ SQLAlchemyError occurred: {str(e)}")
        raise Exception(f"Error while committing to database: {str(e)}")
    
    except Exception as e:
        # Catch other general errors
        db.rollback()
        print(f"❌ Error occurred: {str(e)}")
        raise Exception(f"Unexpected error: {str(e)}")


def get_document(db: Session, model_cls, doc_id):
    doc = db.query(model_cls).get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

def list_documents(db: Session, model_cls, skip=0, limit=100):
    return db.query(model_cls).offset(skip).limit(limit).all()

def update_document(db: Session, model_cls, doc_id, data: dict):
    doc = get_document(db, model_cls, doc_id)
    for key, value in data.items():
        setattr(doc, key, value)
    db.commit()
    db.refresh(doc)
    return doc

def delete_document(db: Session, model_cls, doc_id):
    doc = get_document(db, model_cls, doc_id)
    db.delete(doc)
    db.commit()