import face_recognition
import numpy as np
from facial_recognition import FacialRecognition

class ConfidenceRecognition(FacialRecognition):
    """
    Extends FacialRecognition to add confidence scores to face matches.
    This helps show how reliable each identification is.
    """
    
    def __init__(self):
        # Initialize the parent class first
        super().__init__()
        
        # Set default threshold:  matches below this are considered Unidentified
        self.confidence_threshold = 0.6
    
    def recognize_faces_with_confidence(self, frame):
        # Convert to RGB 
        rgb_frame = frame[:, :, ::-1]
        
        # Find all faces in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        
        # If no faces are found, return empty results
        if not face_locations:
            return [], [], []
            
        face_names = []
        confidence_scores = []
        
        # Process each face
        for face_location in face_locations:
            try:
                # Get face encoding
                encoding_list = face_recognition.face_encodings(rgb_frame, [face_location])
                
                if encoding_list:
                    encoding = encoding_list[0]
                    
                    # Default values if no match
                    name = "Unidentified"
                    confidence = 0.0
                    
                    if len(self.known_face_encodings) > 0:
                        # Calculate how similar this face is to known faces
                        face_distances = face_recognition.face_distance(
                            self.known_face_encodings, encoding
                        )
                        
                        if len(face_distances) > 0:
                            # Find best match
                            best_match_index = np.argmin(face_distances)
                            best_distance = face_distances[best_match_index]
                            
                            # Convert distance to confidence percentage
                            # 0 distance = 100% confidence, 1 distance = 0% confidence
                            confidence = (1.0 - best_distance) * 100
                            
                            # Use name if confidence is high enough
                            if confidence/100 >= self.confidence_threshold:
                                name = self.known_face_names[best_match_index]
                    
                    face_names.append(name)
                    confidence_scores.append(confidence)
                else:
                    # Couldn't get encoding for this face
                    face_names.append("Unidentified")
                    confidence_scores.append(0.0)
            except Exception as e:
                # Handle any errors
                print(f"Error processing face: {e}")
                face_names.append("Unidentified")
                confidence_scores.append(0.0)
        
        return face_locations, face_names, confidence_scores
