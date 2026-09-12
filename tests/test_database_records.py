from src.database.crud import DocumentCRUD

crud = DocumentCRUD()

documents = crud.get_all()

print()

print("=" * 60)
print("DATABASE RECORDS")
print("=" * 60)

for doc in documents:

    print(f"ID        : {doc.id}")
    print(f"File      : {doc.file_name}")
    print(f"Type      : {doc.document_type}")
    print(f"Confidence: {doc.confidence}")
    print("-" * 40)

crud.close()