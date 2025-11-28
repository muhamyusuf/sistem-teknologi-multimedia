"""
Face Detection Module using MediaPipe Face Mesh

This module provides robust face detection and ROI (Region of Interest) extraction
for remote photoplethysmography (rPPG) analysis. It uses MediaPipe Face Mesh to
detect 468 facial landmarks and extract three key regions:
  - Forehead: Primary ROI with strong PPG signal
  - Left cheek: Secondary ROI for signal fusion
  - Right cheek: Secondary ROI for signal fusion

The multi-ROI approach improves robustness against occlusions, shadows, and
motion artifacts.

Author: Muhammad Yusuf
Version: 2.1
Date: November 2025
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, Tuple


class FaceDetector:
    """
    Face detector using MediaPipe Face Mesh for rPPG signal extraction.
    
    Detects facial landmarks and extracts regions optimized for pulse signal
    measurement. Uses MediaPipe's real-time face mesh solution with 468 landmarks.
    
    Attributes:
        mp_face_mesh: MediaPipe Face Mesh solution
        face_mesh: Configured Face Mesh instance
        forehead_indices: Landmark indices for forehead ROI
        left_cheek_indices: Landmark indices for left cheek ROI
        right_cheek_indices: Landmark indices for right cheek ROI
    """
    
    # ROI landmark mappings (optimized for PPG signal quality)
    FOREHEAD_LANDMARKS = [
        10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 
        361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 
        176, 149, 150, 136, 172, 58, 132, 93, 234, 127
    ]
    
    LEFT_CHEEK_LANDMARKS = [
        205, 137, 123, 50, 203, 177, 147, 187, 207, 216
    ]
    
    RIGHT_CHEEK_LANDMARKS = [
        425, 366, 426, 436, 416, 432, 422, 424, 418, 428
    ]
    
    def __init__(
        self, 
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5
    ):
        """
        Initialize MediaPipe Face Mesh detector.
        
        Args:
            min_detection_confidence: Minimum confidence (0-1) for initial face detection
            min_tracking_confidence: Minimum confidence (0-1) for landmark tracking
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,  # Video mode for better temporal consistency
            max_num_faces=1,           # Single person monitoring
            refine_landmarks=True,     # Enable iris landmarks for better accuracy
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Store ROI landmark indices
        self.forehead_indices = self.FOREHEAD_LANDMARKS
        self.left_cheek_indices = self.LEFT_CHEEK_LANDMARKS
        self.right_cheek_indices = self.RIGHT_CHEEK_LANDMARKS
    
    def detect(self, frame: np.ndarray) -> Optional[object]:
        """
        Detect face and extract 468 facial landmarks.
        
        Args:
            frame: Input BGR image from camera (H x W x 3)
            
        Returns:
            Face mesh landmarks object or None if no face detected
        """
        # Convert BGR to RGB (MediaPipe expects RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        results = self.face_mesh.process(rgb_frame)
        
        # Return first face if detected
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0]
        
        return None
    
    def extract_roi(
        self, 
        frame: np.ndarray, 
        face_landmarks: object
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Extract three ROI masks from detected face landmarks.
        
        Creates binary masks for forehead and both cheeks, then applies them
        to the input frame to extract colored ROI regions.
        
        Args:
            frame: Input BGR image
            face_landmarks: Face mesh landmarks from detect()
            
        Returns:
            Tuple of (forehead_roi, left_cheek_roi, right_cheek_roi)
            Each ROI is a masked BGR image or None if extraction failed
        """
        if face_landmarks is None:
            return None, None, None
        
        h, w = frame.shape[:2]
        
        # Extract each ROI with mask
        forehead_roi = self._extract_region_mask(
            frame, face_landmarks, self.forehead_indices, h, w
        )
        
        left_cheek_roi = self._extract_region_mask(
            frame, face_landmarks, self.left_cheek_indices, h, w
        )
        
        right_cheek_roi = self._extract_region_mask(
            frame, face_landmarks, self.right_cheek_indices, h, w
        )
        
        return forehead_roi, left_cheek_roi, right_cheek_roi
    
    def _extract_region_mask(
        self, 
        frame: np.ndarray, 
        face_landmarks: object, 
        indices: list, 
        h: int, 
        w: int
    ) -> Optional[np.ndarray]:
        """
        Extract ROI region using convex hull of landmark points.
        
        Args:
            frame: Input BGR image
            face_landmarks: Face mesh landmarks
            indices: List of landmark indices defining the ROI
            h: Frame height
            w: Frame width
            
        Returns:
            Masked BGR image or None if insufficient landmarks
        """
        # Convert normalized coordinates to pixel coordinates
        points = []
        for idx in indices:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            points.append([x, y])
        
        # Need at least 3 points for a polygon
        if len(points) < 3:
            return None
        
        # Create binary mask
        mask = np.zeros((h, w), dtype=np.uint8)
        points_array = np.array(points, dtype=np.int32)
        
        # Fill convex polygon
        cv2.fillConvexPoly(mask, points_array, 255)
        
        # Apply mask to frame
        roi = cv2.bitwise_and(frame, frame, mask=mask)
        
        return roi
    
    def draw_face_mesh(
        self, 
        frame: np.ndarray, 
        face_landmarks: object
    ) -> np.ndarray:
        """
        Visualize ROI regions on frame for debugging and user feedback.
        
        Draws colored boundaries around each ROI:
          - Green: Forehead (primary ROI)
          - Blue: Left cheek
          - Red: Right cheek
        
        Args:
            frame: Input BGR image
            face_landmarks: Face mesh landmarks
            
        Returns:
            Frame with ROI boundaries drawn
        """
        if face_landmarks is None:
            return frame
        
        h, w = frame.shape[:2]
        annotated_frame = frame.copy()
        
        # Draw each ROI with distinct color
        self._draw_roi_boundary(
            annotated_frame, face_landmarks, 
            self.forehead_indices, h, w, 
            color=(0, 255, 0),  # Green for forehead
            thickness=2
        )
        
        self._draw_roi_boundary(
            annotated_frame, face_landmarks, 
            self.left_cheek_indices, h, w, 
            color=(255, 0, 0),  # Blue for left cheek
            thickness=2
        )
        
        self._draw_roi_boundary(
            annotated_frame, face_landmarks, 
            self.right_cheek_indices, h, w, 
            color=(0, 0, 255),  # Red for right cheek
            thickness=2
        )
        
        return annotated_frame
    
    def _draw_roi_boundary(
        self, 
        frame: np.ndarray, 
        face_landmarks: object, 
        indices: list, 
        h: int, 
        w: int, 
        color: Tuple[int, int, int],
        thickness: int = 2
    ) -> None:
        """
        Draw polygon boundary for an ROI region.
        
        Args:
            frame: Image to draw on (modified in-place)
            face_landmarks: Face mesh landmarks
            indices: Landmark indices defining the ROI
            h: Frame height
            w: Frame width
            color: BGR color tuple
            thickness: Line thickness in pixels
        """
        # Convert landmarks to pixel coordinates
        points = []
        for idx in indices:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            points.append([x, y])
        
        # Draw closed polyline
        if len(points) >= 3:
            points_array = np.array(points, dtype=np.int32)
            cv2.polylines(frame, [points_array], True, color, thickness)
    
    def __del__(self):
        """Cleanup MediaPipe resources on object destruction."""
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()


if __name__ == "__main__":
    print("=" * 70)
    print("Face Detection Module - Test")
    print("=" * 70)
    print("✅ FaceDetector class loaded successfully")
    print("\nFeatures:")
    print("  • MediaPipe Face Mesh with 468 landmarks")
    print("  • Multi-ROI extraction (forehead + both cheeks)")
    print("  • Real-time tracking with temporal consistency")
    print("\nUsage Example:")
    print("  detector = FaceDetector()")
    print("  landmarks = detector.detect(frame)")
    print("  forehead, left_cheek, right_cheek = detector.extract_roi(frame, landmarks)")
    print("  annotated = detector.draw_face_mesh(frame, landmarks)")
