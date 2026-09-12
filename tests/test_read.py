from src.database.crud import DocumentCRUD

crud = DocumentCRUD()

document = crud.get(1)

print(document.file_name)

print(document.document_type)

print(document.confidence)

print(document.raw_text)

print(document.json_data)

crud.close()