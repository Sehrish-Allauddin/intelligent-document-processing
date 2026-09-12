from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Text

from src.database.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    document_type = Column(
        String(50),
        nullable=False
    )

    confidence = Column(
        Float,
        nullable=False
    )

    raw_text = Column(
        Text,
        nullable=True
    )

    json_data = Column(
        Text,
        nullable=False
    )