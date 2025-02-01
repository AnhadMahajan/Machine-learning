import cv2
import requests
import json
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolov8n.pt")  # Download YOLOv8 model weights from ultralytics

# Gemini API Configuration
GEMINI_API_KEY = "your_gemini_api_key"
GEMINI_API_URL = "https://api.gemini.com/analyze"

def detect_objects(frame):
    """
    Detect objects in the given frame using YOLOv8.
    """
    results = model(frame)  # Perform object detection
    detections = []
    
    for result in results[0].boxes.data:
        x1, y1, x2, y2, conf, cls = result.tolist()
        label = model.names[int(cls)]
        detections.append({
            "label": label,
            "confidence": round(conf, 2),
            "bbox": (int(x1), int(y1), int(x2), int(y2))
        })
    return detections

def analyze_with_gemini(objects):
    """
    Use Gemini API to analyze detected objects and generate recommendations.
    """
    payload = {
        "objects": objects,
        "task": "room_renovation_analysis"
    }
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # AI-based recommendations from Gemini
    else:
        print("Error with Gemini API:", response.text)
        return None

def main():
    """
    Main function to capture video, detect objects, and provide renovation suggestions.
    """
    cap = cv2.VideoCapture(0)  # Use the webcam
    print("Press 'q' to quit.")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Detect objects
        objects = detect_objects(frame)

        # Draw detections on the frame
        for obj in objects:
            x1, y1, x2, y2 = obj['bbox']
            label = f"{obj['label']} ({obj['confidence']})"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Display the frame
        cv2.imshow("Room Object Detection", frame)

        # Send data to Gemini API for analysis
        if cv2.waitKey(1) & 0xFF == ord('r'):  # Press 'r' to request recommendations
            print("Sending detected objects to Gemini API for recommendations...")
            recommendations = analyze_with_gemini(objects)
            if recommendations:
                print("\nRenovation Suggestions:\n", json.dumps(recommendations, indent=4))

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
