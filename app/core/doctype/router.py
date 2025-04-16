import traceback
import logging
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from core.config import get_db
from core.registry import model_registry, schema_registry
from core.doctype.engine import list_documents, get_document, delete_document, create_document

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Adjust logging level as needed

def build_crud_router(model_key: str, route_prefix: str = "", hooks=None):
    model = model_registry.get(model_key)
    read_schema = schema_registry.get(f"{model_key}.read")
    create_schema = schema_registry.get(f"{model_key}.create")

    if not model or not read_schema or not create_schema:
        raise HTTPException(
            status_code=404,
            detail=f"Model or schema not found for '{model_key}'"
        )

    # Normalize prefix like /crm/customer
    router = APIRouter(prefix=route_prefix or f"/{model_key.replace('.', '/')}")

    @router.get("/", response_model=list[read_schema])
    async def get_items(db: Session = Depends(get_db)):
        try:
            return list_documents(db, model)
        except Exception as e:
            logger.error(f"Error fetching items: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching items: {str(e)}")

    @router.get("/{item_id}", response_model=read_schema)
    async def get_item(item_id: str, db: Session = Depends(get_db)):
        try:
            return get_document(db, model, item_id)
        except Exception as e:
            logger.error(f"Error fetching item with ID {item_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching item: {str(e)}")

    @router.delete("/{item_id}", response_model=read_schema)
    async def delete_item(item_id: str, db: Session = Depends(get_db)):
        try:
            return delete_document(db, model, item_id)
        except Exception as e:
            logger.error(f"Error deleting item with ID {item_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting item: {str(e)}")

    @router.post("/", response_model=read_schema)
    async def create_item(payload: dict = Body(...), db: Session = Depends(get_db)):
        try:
            logger.info(f"📥 Received payload: {payload}")

        # Validate against dynamic schema
            item = create_schema(**payload)
            logger.info(f"✅ Pydantic model created: {item}")

        # Create DB record
            created = create_document(db, model, item.dict())
            logger.info(f"✅ Document created: {created}")

            return created

        except Exception as e:
            logger.error("❌ Exception during create_item")
            logger.error(traceback.format_exc())  # Full traceback
            raise HTTPException(status_code=500, detail=f"Error creating item: {str(e)}")

    return router
