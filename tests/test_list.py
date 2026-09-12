from src.database.crud import DocumentCRUD

crud = DocumentCRUD()

documents = crud.get_all()

for doc in documents:

    print(

        doc.id,

        doc.file_name,

        doc.document_type,

        doc.confidence

    )

crud.close()