import json

from src.database.database import SessionLocal
from src.database.models import Document


class DocumentCRUD:

    def __init__(self):

        self.db = SessionLocal()

    # ---------------------------------------
    # Create
    # ---------------------------------------

    def create(
        self,
        file_name,
        document_type,
        confidence,
        raw_text,
        json_data
    ):

        document = Document(

            file_name=file_name,

            document_type=document_type,

            confidence=confidence,

            raw_text=raw_text,

            json_data=json.dumps(
                json_data,
                indent=4,
                ensure_ascii=False
            )

        )

        self.db.add(document)

        self.db.commit()

        self.db.refresh(document)

        return document

    # ---------------------------------------
    # Read by ID
    # ---------------------------------------

    def get(self, document_id):

        return (

            self.db.query(Document)

            .filter(
                Document.id == document_id
            )

            .first()

        )

    # ---------------------------------------
    # Get All Documents
    # ---------------------------------------

    def get_all(self):

        return (

            self.db.query(Document)

            .order_by(Document.id.desc())

            .all()

        )

    # ---------------------------------------
    # Search by Document Type
    # ---------------------------------------

    def get_by_type(self, document_type):

        return (

            self.db.query(Document)

            .filter(

                Document.document_type == document_type

            )

            .order_by(Document.id.desc())

            .all()

        )

    # ---------------------------------------
    # Delete
    # ---------------------------------------

    def delete(self, document_id):

        document = self.get(document_id)

        if document is None:

            return False

        self.db.delete(document)

        self.db.commit()

        return True

    # ---------------------------------------
    # Close Session
    # ---------------------------------------

    def close(self):

        self.db.close()