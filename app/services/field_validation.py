from sqlalchemy import text
from sqlalchemy.orm import Session

def is_valid_field(session: Session, doctype: str, fieldname: str) -> bool:
    query = text("""
        SELECT 1 FROM docfield
        WHERE parent = :doctype AND fieldname = :fieldname
        LIMIT 1
    """)
    result = session.execute(query, {"doctype": doctype, "fieldname": fieldname})
    return result.scalar() is not None
