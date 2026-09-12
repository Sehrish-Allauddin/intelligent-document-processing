from src.pipelines.document_pipeline import DocumentPipeline


def main():

    pipeline = DocumentPipeline()

    result = pipeline.process(
        "data/raw/invoices/sample_invoice.png"
    )

    print("\n===== FINAL RESULT =====\n")

    print(result)


if __name__ == "__main__":
    main()