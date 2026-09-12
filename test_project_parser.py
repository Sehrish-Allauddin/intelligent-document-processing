from src.extraction.project_parser import ProjectParser

parser = ProjectParser()

text = """Al-Based Fraud Detection System
Built an end-to-end fraud detection system using multiple models including Random Forest;
XGBoost, DNN, Autoencoder, and LSTM
Processed and analyzed data points to improve fraud detection performance
Applied feature engineering and data preprocessing techniques to enhance model accuracy
Al-Based Patient Fall Detection System
Technologies: Python, OpenCV, MediaPipe, Computer Vision, SMTP
Developed a real-time patient fall detection system
computer vision and pose estimation.
Implemented human pose detection model (MediaPipe PoseLandmarker)
"""

result = parser.parse(text)

print("\nPROJECT COUNT =", len(result))

for i, project in enumerate(result, 1):

    print("\nPROJECT", i)
    print("TITLE:", project["title"])
    print("DESCRIPTION:")

    for line in project["description"]:
        print(" -", line)