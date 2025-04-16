from sqlalchemy import text
from sqlalchemy.orm import Session

def fetch_field_from_customer(
    session: Session,
    fieldname: str
):
    query = text(f"""
        SELECT
            name,
            data ->> :fieldname AS field_value,
            creation,
            modified
        FROM tabCustomer
        WHERE data ? :fieldname
    """)
    result = session.execute(query, {"fieldname": fieldname})
    return result.fetchall()
