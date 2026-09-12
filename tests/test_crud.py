from src.database.crud import DocumentCRUD


crud = DocumentCRUD()

document = crud.create(

    file_name="invoice.jpg",

    document_type="invoice",

    confidence=99.91,

    raw_text="Invoice OCR Text",

    json_data={

        "vendor": "ABC Store",

        "total": 500

    }

)

print()

print("=" * 60)

print("DOCUMENT SAVED")

print("=" * 60)

print(document.id)

crud.close()