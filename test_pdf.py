from src.pdf.pdf_pipeline import PDFPipeline

pipeline = PDFPipeline()

result = pipeline.process("sample_resume.pdf")

print(result)