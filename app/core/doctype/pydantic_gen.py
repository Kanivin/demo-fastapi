import json
from typing import Optional
from pathlib import Path
from pydantic import BaseModel
from sqlalchemy import Column, String, Boolean, Float, Integer, Date
from sqlalchemy.dialects.postgresql import UUID as SAUUID
from uuid import uuid4, UUID as PyUUID


# Define the field type mappings for SQLAlchemy
FIELD_TYPE_MAP = {
    "Data": String,
    "Link": String,
    "Select": String,
    "Attach Image": String,
    "Text": String,
    "Read Only": String,
    "Email": String,
    "Check": Boolean,
    "Int": Integer,
    "Float": Float,
    "Currency": Float,
    "Date": Date,
}

# Map Pydantic types
PYDANTIC_TYPE_MAP = {
    "Data": str,
    "Link": str,
    "Select": str,
    "Attach Image": str,
    "Text": str,
    "Read Only": str,
    "Email": str,
    "Check": bool,
    "Int": int,
    "Float": float,
    "Currency": float,
    "Date": str,  # Date in Pydantic will use str or datetime
}
def parse_fields(fields):
    model_fields = []
    pydantic_fields = []
    for field in fields:
        fieldname = field.get("fieldname")
        fieldtype = field.get("fieldtype")
        required = field.get("reqd", 0)

        if not fieldname or fieldtype not in FIELD_TYPE_MAP:
            continue

        # SQLAlchemy model field type (use .__name__ to insert valid syntax)
        sql_type = FIELD_TYPE_MAP[fieldtype]
        nullable = required == 0
        model_fields.append(f"    {fieldname} = Column({sql_type.__name__}, nullable={nullable})")

        # Pydantic schema field type
        pydantic_type = PYDANTIC_TYPE_MAP[fieldtype]
        if not required:
            pydantic_type = f"Optional[{pydantic_type.__name__}]"
        else:
            pydantic_type = pydantic_type.__name__

        pydantic_fields.append(f"    {fieldname}: {pydantic_type}")

    return model_fields, pydantic_fields


def generate_model_and_schema(doctype_path: Path):
    # Load data from JSON file
    data = json.loads(doctype_path.read_text())
    model_name = data["name"]
    model_fields, pydantic_fields = parse_fields(data["fields"])

    # Generate the SQLAlchemy model code
    model_code = f"""from sqlalchemy import Column, String, Boolean, Float, Integer, Date
from sqlalchemy.dialects.postgresql import UUID
from core.config import Base
import uuid

class {model_name}(Base):
    __tablename__ = '{model_name.lower()}s'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
{chr(10).join(model_fields)}
"""

    # Generate the Pydantic schema code
    schema_code = f"""from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class {model_name}Base(BaseModel):
{chr(10).join(pydantic_fields)}

class {model_name}Create({model_name}Base):
    pass

class {model_name}Read({model_name}Base):
    id: UUID
    class Config:
        orm_mode = True
"""

    return model_code, schema_code
