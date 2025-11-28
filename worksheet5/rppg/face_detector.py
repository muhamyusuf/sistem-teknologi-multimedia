"""
Face Detection Module using MediaPipe Face Mesh
Detects face and extracts ROI (forehead and cheeks) for rPPG analysis.
"""

import cv2
import numpy as np
import mediapipe as mp


class FaceDetector:
    """
    Detect face dan extract ROI menggunakan MediaPipe Face Mesh.
    """
    
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Initialize MediaPipe Face Mesh.
        
        Args:
            min_detection_confidence: Minimum confidence untuk deteksi wajah
            min_tracking_confidence: Minimum confidence untuk tracking
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Landmark indices untuk ROI
        # Forehead: region atas wajah
        self.forehead_indices = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 
                                  361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 
                                  176, 149, 150, 136, 172, 58, 132, 93, 234, 127]
        
        # Left cheek (kiri dari perspektif wajah, kanan dari perspektif kamera)
        self.left_cheek_indices = [205, 137, 123, 50, 203, 177, 147, 187, 207, 216]
        
        # Right cheek (kanan dari perspektif wajah, kiri dari perspektif kamera)
        self.right_cheek_indices = [425, 266, 426, 436, 416, 432, 422, 424, 418, 428]
    
    def detect(self, frame):
        """
        Detect face mesh dalam frame.
        
        Args:
            frame: Input BGR image dari webcam
            
        Returns:
            face_mesh results atau None jika tidak ada wajah terdeteksi
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0]  # Ambil wajah pertama
        return None
    
    def extract_roi(self, frame, face_landmarks):
        """
        Extract ROI (Region of Interest) untuk rPPG dari face landmarks.
        
        Args:
            frame: Input BGR image
            face_landmarks: Face mesh landmarks dari detect()
            
        Returns:
            Tuple of (forehead_roi, left_cheek_roi, right_cheek_roi)
            Masing-masing berupa mask atau None jika gagal
        """
        if face_landmarks is None:
            return None, None, None
        
        h, w = frame.shape[:2]
        
        # Extract forehead ROI
        forehead_roi = self._extract_region_mask(frame, face_landmarks, self.forehead_indices, h, w)
        
        # Extract cheek ROIs
        left_cheek_roi = self._extract_region_mask(frame, face_landmarks, self.left_cheek_indices, h, w)
        right_cheek_roi = self._extract_region_mask(frame, face_landmarks, self.right_cheek_indices, h, w)
        
        return forehead_roi, left_cheek_roi, right_cheek_roi
    
    def _extract_region_mask(self, frame, face_landmarks, indices, h, w):
        """
        Helper untuk extract region mask dari landmarks.
        """
        # Get pixel coordinates
        points = []
        for idx in indices:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            points.append([x, y])
        
        if len(points) < 3:
            return None
        
        # Create mask
        mask = np.zeros((h, w), dtype=np.uint8)
        points = np.array(points, dtype=np.int32)
        cv2.fillConvexPoly(mask, points, 255)
        
        # Extract region
        roi = cv2.bitwise_and(frame, frame, mask=mask)
        
        return roi
    
    def draw_face_mesh(self, frame, face_landmarks):
        """
        Draw face mesh pada frame untuk visualization.
        
        Args:
            frame: Input BGR image
            face_landmarks: Face mesh landmarks
            
        Returns:
            Frame dengan face mesh tergambar
        """
        if face_landmarks is None:
            return frame
        
        h, w = frame.shape[:2]
        annotated_frame = frame.copy()
        
        # Draw forehead ROI
        self._draw_roi_boundary(annotated_frame, face_landmarks, 
                                self.forehead_indices, h, w, (0, 255, 0))
        
        # Draw cheek ROIs
        self._draw_roi_boundary(annotated_frame, face_landmarks, 
                                self.left_cheek_indices, h, w, (255, 0, 0))
        self._draw_roi_boundary(annotated_frame, face_landmarks, 
                                self.right_cheek_indices, h, w, (0, 0, 255))
        
        return annotated_frame
    
    def _draw_roi_boundary(self, frame, face_landmarks, indices, h, w, color):
        """
        Helper untuk draw ROI boundary.
        """
        points = []
        for idx in indices:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            points.append([x, y])
        
        if len(points) >= 3:
            points = np.array(points, dtype=np.int32)
            cv2.polylines(frame, [points], True, color, 2)
    
    def __del__(self):
        """Cleanup MediaPipe resources."""
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()


if __name__ == "__main__":
    print("✅ FaceDetector module loaded")
    print("\nExample usage:")
    print("  detector = FaceDetector()")
    print("  face_mesh = detector.detect(frame)")
    print("  forehead, left_cheek, right_cheek = detector.extract_roi(frame, face_mesh)")
