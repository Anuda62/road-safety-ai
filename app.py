# app.py
import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR
import tempfile
import os
import sqlite3
from datetime import datetime

# Initialize YOLO model and OCR
model = YOLO("yolov8n.pt")
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Database setup
conn = sqlite3.connect("violations.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_plate TEXT,
    timestamp TEXT,
    violation_type TEXT
)''')
conn.commit()

# Streamlit UI setup
st.set_page_config(page_title="AI Road Safety System", layout="centered", page_icon="🚦")
st.markdown("""
    <style>
        .main {background-color: #f5f7fa;}
        h1, h2, h3 {color: #2c3e50; text-align: center;}
        .stButton>button {width: 100%; background-color: #3498db; color: white; font-weight: bold; padding: 10px; border-radius: 8px;}
        .stFileUploader {margin: auto;}
        .data-box {padding: 1rem; border: 1px solid #ccc; border-radius: 10px; margin-top: 1rem; background-color: #fff;}
    </style>
""", unsafe_allow_html=True)

st.title("🚦 AI Road Safety System")
st.subheader("Upload a traffic video to detect red-light violations and identify license plates")

video_file = st.file_uploader("📤 Upload Traffic Video", type=["mp4", "avi", "mov"])

if video_file is not None:
    st.video(video_file)
    temp_video = tempfile.NamedTemporaryFile(delete=False)
    temp_video.write(video_file.read())
    temp_video.close()

    with st.spinner("🔍 Analyzing video... Please wait"):
        try:
            cap = cv2.VideoCapture(temp_video.name)
            frame_count = 0
            stframe = st.empty()

            stop_line_y = 300  # Y-position of stop line
            red_light_duration = 150  # Red light duration in frames

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1
                if frame_count % 2 != 0:
                    continue

                light_is_red = frame_count % 300 < red_light_duration
                results = model(frame)[0]
                annotated_frame = frame.copy()

                # Draw stop line and light status
                cv2.line(annotated_frame, (0, stop_line_y), (annotated_frame.shape[1], stop_line_y), (0, 0, 255), 2)
                status_text = "RED LIGHT" if light_is_red else "GREEN LIGHT"
                status_color = (0, 0, 255) if light_is_red else (0, 255, 0)
                cv2.putText(annotated_frame, f"{status_text}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, status_color, 3)

                for box in results.boxes.data.tolist():
                    x1, y1, x2, y2, score, cls = box
                    class_name = model.names[int(cls)]

                    if class_name in ["car", "motorbike"]:
                        center_y = (y1 + y2) / 2
                        if light_is_red and center_y < stop_line_y:
                            plate_crop = frame[int(y1):int(y2), int(x1):int(x2)]
                            if plate_crop.size == 0:
                                continue
                            try:
                                result = ocr.ocr(plate_crop, cls=True)
                                if result[0]:
                                    plate_text = result[0][0][1][0]
                                    cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                                    cv2.putText(annotated_frame, plate_text, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,0), 2)

                                    c.execute("INSERT INTO violations (license_plate, timestamp, violation_type) VALUES (?, ?, ?)",
                                              (plate_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Red Light Violation"))
                                    conn.commit()
                            except:
                                pass

                stframe.image(annotated_frame, channels="BGR")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            os.remove(temp_video.name)

st.markdown("---")
st.header("📋 Violation Log")
st.markdown("### Recent Violations:")
violation_data = c.execute("SELECT * FROM violations ORDER BY id DESC LIMIT 10").fetchall()

if violation_data:
    for row in violation_data:
        with st.container():
            st.markdown(f"""
                <div class="data-box">
                    <strong>🕒 {row[2]}</strong><br>
                    <strong>🚘 Plate:</strong> {row[1]}<br>
                    <strong>⚠️ Violation:</strong> {row[3]}
                </div>
            """, unsafe_allow_html=True)
else:
    st.info("No violations detected yet. Upload a video to start analysis.")
