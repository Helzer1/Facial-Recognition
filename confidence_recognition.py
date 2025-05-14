import face_recognition
import numpy as np
import cv2
import os
import logging
from facial_recognition import FacialRecognition

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfidenceRecognition(FacialRecognition):
    """
    Extends FacialRecognition to add confidence scores to face matches.
    
    Confidence levels:
    - High confidence (>=70%)
    - Medium confidence (>=50% but <70%)
    - Low confidence (<50%)
    """
    
    def __init__(self, capture, name_cap):
        # Initialize parent class FacialRecognition
        super().__init__()
        
        # Confidence thresholds
        self.confidence_threshold = 0.6
        self.high_confidence_threshold = 0.7
        self.medium_confidence_threshold = 0.5
    
    def _calculate_confidence_ensemble(self, unknown_encoding):
        """Calculate confidence based on face distance and mathematical scaling."""
        if not self.known_face_encodings:
            return []
        
        # Calculate face distances
        face_distances = face_recognition.face_distance(self.known_face_encodings, unknown_encoding)
        
        # Convert distances to confidence scores using a sigmoid function
      
        confidence_scores = []
        for distance in face_distances:
            # Standard sigmoid function scaling for more realistic distribution
            if distance >= 0.9:  # Very poor match
                confidence = 0
            else:
                # Sigmoid function: 1/(1+e^(scale*(x-midpoint)))
                # Scale = 15 controls steepness, midpoint = 0.5 centers the curve
                confidence = 100 * (1 / (1 + np.exp(15 * (distance - 0.5))))
            
            confidence_scores.append(confidence)
        
        return confidence_scores
    
    def calculate_confidence_for_face(self, frame, face_location):
        """
        Calculate confidence score for a single face.
        
        Args:
            frame: Video frame containing the face
            face_location: (top, right, bottom, left) tuple for the face
            
        Returns:
            Tuple of (confidence_score, confidence_level)
        """
        try:
            # Convert to RGB for face_recognition library
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Extract face encoding
            encoding_list = face_recognition.face_encodings(rgb_frame, [face_location], num_jitters=0)
            
            if not encoding_list or not self.known_face_encodings:
                return 0.0, "LOW"
                
            face_encoding = encoding_list[0]
            
            # Calculate confidence based on face encoding
            confidence_values = self._calculate_confidence_ensemble(face_encoding)
            
            if not confidence_values:
                return 0.0, "LOW"
                
            # Find best match
            best_match_index = np.argmax(confidence_values)
            base_confidence = confidence_values[best_match_index]
            
            # mathematical proportion
            top, right, bottom, left = face_location
            face_width = right - left
            face_height = bottom - top
            
            # Calculate relative face size percentage of frame
            frame_height, frame_width = frame.shape[:2]
            face_area_ratio = (face_width * face_height) / (frame_width * frame_height)
            
            # logarithmic scaling for distance estimation
            if face_area_ratio > 0.15:  # Very close to camera
                size_factor = 1.0
            else:
                # Log scale gives  returns as you get farther
                size_factor = max(0.5, min(1.0, np.log(face_area_ratio + 0.01) / np.log(0.15)))
            
            # Apply size factor to confidence
            confidence = base_confidence * size_factor
            
            # Determine confidence level
            if confidence >= self.high_confidence_threshold * 100:
                level = "HIGH"
            elif confidence >= self.medium_confidence_threshold * 100:
                level = "MEDIUM"
            else:
                level = "LOW"
                
            return confidence, level
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.0, "LOW"
    
    def get_confidence_scores(self, frame, face_locations):
        """
        Get confidence scores for all faces in the frame.
        
        Args:
            frame: Video frame containing faces
            face_locations: List of face location tuples
            
        Returns:
            List of confidence scores
        """
        confidence_scores = []
        
        for face_location in face_locations:
            score, _ = self.calculate_confidence_for_face(frame, face_location)
            confidence_scores.append(score)
            
        return confidence_scores
    
    def recognize_faces(self, frame):
        """
         parent method to add confidence calculation.
        
        Returns:
            face_locations: List of face locations
            face_names: List of names
        """
        # Get face locations and encodings using parent method first
        face_locations, face_names = super().recognize_faces(frame)
        
        # Calculate the confidence scores for each face 
       
        self.current_confidence_scores = self.get_confidence_scores(frame, face_locations)
        
     
        return face_locations, face_names
    
    def get_last_confidence_scores(self):
        """Get the most recently calculated confidence scores."""
        if hasattr(self, 'current_confidence_scores'):
            return self.current_confidence_scores
        return []