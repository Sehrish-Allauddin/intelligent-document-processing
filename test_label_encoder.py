from src.dataset.label_encoder import LabelEncoder

encoder = LabelEncoder("datasets/rvl_cdip/RVL-CDIP", split="test")

print("Classes:")
print(encoder.classes)

print("\nInvoice ID:", encoder.encode("invoice"))

print("Decode 5:", encoder.decode(5))