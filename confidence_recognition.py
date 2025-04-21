import face_recognition
import numpy as np
import cv2
import os
from file_storage import Storage

class ConfidenceRecognition(Storage):
    """
    Adds confidence scores to face matches with color coding.
    
    Green:  >=70%
    Yellow: >=50% but <70%
    Red: <50% match 
    """
    
    def __init__(self, capture=None, name_cap=None):
        super().__init__(capture, name_cap)
        
        # Initialize face encoding lists
        self.known_face_encodings = []
        self.known_face_names = []
        
        # Load known faces from storage
        self.load_known_faces()
        
        # Confidence thresholds for the color system
        self.confidence_threshold = 0.6  #60% for a match
        self.high_confidence_threshold = 0.7  # 70%+ gets green
        self.medium_confidence_threshold = 0.5  # 50-70% gets yellow
        
        # BGR colors for OpenCV
        self.high_confidence_color = (0, 255, 0)  # Green
        self.medium_confidence_color = (0, 255, 255)  # Yellow
        self.low_confidence_color = (0, 0, 255)  # Red
    
    def load_known_faces(self):
        """Load known faces from storage"""
        try:
            # Get list of stored images
            images = self.list_images()
            
            # Clear existing data
            self.known_face_encodings = []
            self.known_face_names = []
            
            # Process each image
            for filename, name in images:
                # Construct path to image file
                image_path = os.path.join(self.storage_dir, filename)
                
                try:
                    # Load the image
                    image = face_recognition.load_image_file(image_path)
                    
                    # Get face encoding
                    encodings = face_recognition.face_encodings(image)
                    
                    # If a face was found, add it
                    if encodings:
                        self.known_face_encodings.append(encodings[0])
                        self.known_face_names.append(name)
                except Exception as e:
                    print(f"Error loading face from {image_path}: {e}")
        except Exception as e:
            print(f"Error loading known faces: {e}")

    def recognize_faces_with_confidence(self, frame):
        """
        Finds faces in a frame and figures out how confident we are about who's who.
        """
        # Convert to RGB because face_recognition lib
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find all the faces
        face_locations = face_recognition.face_locations(rgb_frame)
        
        #  return empty results
        if not face_locations:
            return [], [], [], []
        
        face_names = []
        confidence_scores = []
        confidence_colors = []
        
        # Check each face we found
        for face_location in face_locations:
            try:
                #  encoding for this face
                encoding_list = face_recognition.face_encodings(rgb_frame, [face_location])
                
                if encoding_list:
                    encoding = encoding_list[0]
                    
                    #Default values if no match
                    name = "Unidentified"
                    confidence = 0.0
                    color = self.low_confidence_color
                    
                    if len(self.known_face_encodings) > 0:
                        # Calculation of similarity this face is to known faces
                        face_distances = face_recognition.face_distance(
                            self.known_face_encodings, encoding
                        )
                        
                        if len(face_distances) > 0:
                            # Find the best match
                            best_match_index = np.argmin(face_distances)
                            best_distance = face_distances[best_match_index]
                            
                            # the distance to get confidence 0 distance = 100% match
                            confidence = (1.0 - best_distance)
                            
                            # a color based on how confident we are
                            if confidence >= self.high_confidence_threshold:
                                color = self.high_confidence_color  # Green 
                            elif confidence >= self.medium_confidence_threshold:
                                color = self.medium_confidence_color  # Yellow 
                            else:
                                color = self.low_confidence_color  # Red 
                            
                            # Use name if confidence is high enough
                            if confidence >= self.confidence_threshold:
                                name = self.known_face_names[best_match_index]
                    
                    face_names.append(name)
                    confidence_scores.append(confidence * 100)  # People like percentages
                    confidence_colors.append(color)
                
                else:
                    # Couldn't get encoding for this face
                    face_names.append("Unidentified")
                    confidence_scores.append(0.0)
                    confidence_colors.append(self.low_confidence_color)
            
            except Exception as e:
                print(f"Error processing face: {e}")
                face_names.append("Unidentified")
                confidence_scores.append(0.0)
                confidence_colors.append(self.low_confidence_color)
        
        return face_locations, face_names, confidence_scores, confidence_colors
    
    def recognize_faces(self, frame):
        """
        UI - internally uses confidence scoring
        but returns results i
        """
        # confidence method internally
        face_locations, face_names, confidence_scores, confidence_colors = self.recognize_faces_with_confidence(frame)
        
        for (top, right, bottom, left), name, score, color in zip(face_locations, face_names, confidence_scores, confidence_colors):
            # Add confidence to the name
            name_with_confidence = f"{name} ({score:.1f}%)"
            
            # Draw with correct confidence color
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name_with_confidence, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
        
        return face_locations, face_names