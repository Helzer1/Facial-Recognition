from pymongo import MongoClient
from datetime import datetime
import numpy as np
import cv2
import os

class MongoStorage:
    def __init__(self, uri, cap, name_cap, recognition):
        self.client = MongoClient(uri)
        self.db = self.client["face_db"]
        self.collection = self.db["known_faces"]

        self.cap = cap
        self.name_cap = name_cap
        self.recognition = recognition

        self.load_known_faces()

    def take_picture(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            return None, None

        name = self.name_cap.get("1.0", "end-1c").strip()
        if not name:
            print("Error: Name field is empty.")
            return None, None

        os.makedirs("images", exist_ok=True)
        img_path = f"images/{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        cv2.imwrite(img_path, frame)

        face_encoding = self.recognition.get_face_encoding_from_image(frame)
        if face_encoding is None:
            print("Error: No face found.")
            return None, None

        self.collection.insert_one({
            "name": name,
            "encoding": face_encoding.tolist(),
            "image_path": img_path,
            "timestamp": datetime.utcnow()
        })

        print(f"[INFO] Saved face for {name} to MongoDB.")
        return name, img_path

    def load_known_faces(self):
        known_encodings = []
        known_names = []

        for doc in self.collection.find():
            known_encodings.append(np.array(doc["encoding"]))
            known_names.append(doc["name"])

        self.recognition.set_known_faces(known_encodings, known_names)
