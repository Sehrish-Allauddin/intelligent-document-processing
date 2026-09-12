from src.database.crud import DocumentCRUD

crud = DocumentCRUD()


def get_dashboard_stats():

    records = crud.get_all()

    stats = {
        "total": len(records),
        "resume": 0,
        "invoice": 0,
        "receipt": 0,
        "form": 0,
        "records": records,
    }

    for record in records:

        doc_type = str(
            getattr(record, "document_type", "")
        ).strip().lower()

        if doc_type in (
            "resume",
            "invoice",
            "receipt",
            "form",
        ):
            stats[doc_type] += 1

    return stats