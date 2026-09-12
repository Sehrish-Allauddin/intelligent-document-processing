from pathlib import Path
import fitz  # PyMuPDF

# Source folder containing resume categories
SOURCE_DIR = Path("datasets/resumes/Resume/data")

# Output folder for converted images
OUTPUT_DIR = Path("datasets/resume_images")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

total_pdfs = 0
total_images = 0

for category in SOURCE_DIR.iterdir():

    if not category.is_dir():
        continue

    print(f"\nProcessing {category.name}")

    output_category = OUTPUT_DIR / category.name
    output_category.mkdir(parents=True, exist_ok=True)

    pdf_files = list(category.glob("*.pdf"))

    print(f"Found {len(pdf_files)} PDFs")

    for pdf_file in pdf_files:

        total_pdfs += 1

        try:
            doc = fitz.open(pdf_file)

            if len(doc) == 0:
                doc.close()
                continue

            page = doc.load_page(0)

            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

            image_path = output_category / f"{pdf_file.stem}.png"

            pix.save(image_path)

            doc.close()

            total_images += 1

        except Exception as e:
            print(f"Failed: {pdf_file.name}")
            print(e)

print("\n" + "=" * 50)
print("Conversion Completed")
print("=" * 50)
print(f"PDFs Processed : {total_pdfs}")
print(f"Images Created : {total_images}")
print(f"Saved To       : {OUTPUT_DIR.resolve()}")