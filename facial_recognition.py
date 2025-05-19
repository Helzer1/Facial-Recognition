# facial_recognition.py

import face_recognition
import cv2
import numpy as np

class FacialRecognition:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []

    def set_known_faces(self, encodings, names):
        """Manually set known faces from storage (e.g. MongoDB)."""
        self.known_face_encodings = encodings
        self.known_face_names = names

    def recognize_faces(self, frame):
        """Detect and recognize faces in a video frame."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        face_names = []

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]

            face_names.append(name)

        return face_locations, face_names

    def get_face_encoding_from_image(self, image):
        """Extract a single face encoding from an image (used for new users)."""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        if face_encodings:
            return face_encodings[0]  # Return first face only
        return None
