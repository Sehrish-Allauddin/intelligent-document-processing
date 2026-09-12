from src.database.crud import DocumentCRUD

crud = DocumentCRUD()

crud.delete(1)

print("Deleted")

crud.close()