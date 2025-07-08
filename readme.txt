AI Road Safety System 🚦
=========================

By: Anuda Sithsara  
Language: Python 3.11  
Interface: Streamlit Web App  
Model: YOLOv8 + PaddleOCR

Overview:
---------
This project is an AI-powered road safety system that detects red-light violations and recognizes license plates from uploaded traffic video footage. It uses computer vision models (YOLOv8 and PaddleOCR) to analyze vehicle behavior and log violations in a local database.

Key Features:
-------------
✅ Detects cars and motorbikes in uploaded videos  
✅ Simulates red-light signal detection  
✅ Identifies if vehicles cross the stop line during a red signal  
✅ Extracts and logs license plate numbers using OCR  
✅ Displays violation history in a user-friendly web UI

Requirements:
-------------
- Python 3.11  
- Dependencies listed in `requirements.txt`

How to Run:
-----------
1. Extract the ZIP folder.
2. Open the terminal (or Command Prompt) inside the folder.
3. Create a virtual environment : 1."python -m venv .venv"
						2.".venv\Scripts\activate"
4. Install dependencies:"pip install -r requirements.txt"
5. Run the app:"streamlit run app.py"


How to Use:
-----------
1. Upload any `.mp4`, `.avi`, or `.mov` traffic video.
2. The app will show the video and analyze for red-light violations.
3. License plates of violating vehicles are displayed in the log below.

File Descriptions:
------------------
- `app.py` : Main application script
- `yolov8n.pt` : Pretrained YOLOv8 model file
- `violations.db` : (Optional) Local SQLite database of detected violations
- `requirements.txt` : List of required Python libraries

Credits:
--------
Built by Anuda Sithsara as part of a student AI project.