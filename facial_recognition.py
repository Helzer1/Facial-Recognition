import face_recognition
import numpy as np
import cv2
from file_storage import Storage
import os

class FacialRecognition:
    def __init__(self, capture, name_cap):
        # Initialize LocalImageStorage to handle saving and loading images.
        self.storage = Storage(capture, name_cap)
        
        # Lists to hold the encodings of known faces and their corresponding names.
        self.known_face_encodings = []
        self.known_face_names = []
        
        # Load previously registered faces and their encodings from the storage
        self.load_known_faces()

    def load_known_faces(self):
        """
        This method loads all the images stored in the `LocalImageStorage`.
        For each image, we extract its face encoding and save it along with
        the person's name for later comparison.
        """
        self.known_face_encodings.clear()
        self.known_face_names.clear()
        images = self.storage.list_images()  # Get list of stored images with filenames and associated names
        for image_filename, person_name in images:
            # Get the full image path from the storage directory
            image_path = os.path.join(self.storage.storage_dir, image_filename)
            
            # Load the image using face_recognition
            image = face_recognition.load_image_file(image_path)
            
            # Get the face encodings from the image (this will return a list of encodings)
            encoding = face_recognition.face_encodings(image)
            
            if encoding:
                # Add the encoding and associated name to the lists
                self.known_face_encodings.append(encoding[0])
                self.known_face_names.append(person_name)

    def recognize_faces(self, frame):
        """
        Detects faces in the given frame, computes encodings for each face,
        and compares them with known encodings to identify the person.

        If a face's encoding computation fails, it is skipped (marked as "Unknown").

        Args:
            frame: The current frame captured from the webcam (in BGR format).

        Returns:
            face_locations: A list of bounding boxes for detected faces.
            face_names: A list of recognized names corresponding to each face.
        """
        # Convert frame from BGR (OpenCV's default) to RGB (required by face_recognition)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect face locations (bounding boxes) in the RGB frame.
        face_locations = face_recognition.face_locations(rgb_frame)
        
        # If no faces are detected, return empty lists.
        if not face_locations:
            return [], []

        # We'll compute face encodings one by one to catch any errors for a specific face.
        face_encodings = []
        for face_location in face_locations:
            try:
                # Compute the face encoding for this face.
                encoding_list = face_recognition.face_encodings(rgb_frame, [face_location], num_jitters=0)
                if encoding_list:
                    face_encodings.append(encoding_list[0])
                else:
                    # If encoding couldn't be computed, append None
                    face_encodings.append(None)
            except Exception as e:
                # Log the error and append None for this face so it can be marked as "Unknown"
                # print("Error computing encoding for face at", face_location, ":", e)
                face_encodings.append(None)

        # Initialize a list to hold the names for each face.
        face_names = []
        for encoding in face_encodings:
            if encoding is None:
                # If encoding failed, mark the face as "Unknown"
                face_names.append("Unknown")
            else:
                # Compare this encoding against known face encodings
                matches = face_recognition.compare_faces(self.known_face_encodings, encoding)
                name = "Unknown"
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]
                face_names.append(name)

        # Return the detected face locations and the corresponding names.
        return face_locations, face_names


