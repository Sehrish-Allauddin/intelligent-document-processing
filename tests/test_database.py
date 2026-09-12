from src.database.database import Base
from src.database.database import engine

from src.database.models import Document


Base.metadata.create_all(

    bind=engine

)

print()

print("=" * 60)

print("DATABASE CREATED SUCCESSFULLY")

print("=" * 60)