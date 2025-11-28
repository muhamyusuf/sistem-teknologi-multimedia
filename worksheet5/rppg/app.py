"""
Main Application - rPPG Heart Rate Monitor

Integrates all modules into a complete real-time heart rate monitoring system:
  - Face detection and ROI extraction
  - Multi-ROI signal fusion
  - POS-based pulse signal extraction
  - Multi-method BPM estimation
  - Real-time visualization with quality metrics

This refactored version features modular architecture, improved code organization,
and enhanced documentation.

Author: Muhammad Yusuf
Version: 2.1
Date: November 2025
"""

import cv2
import numpy as np
import time
from collections import deque

# Core modules
from core.face_detection import FaceDetector
from core.roi_selection import ROISelector
from core.signal_extraction import SignalExtractor
from core.signal_processing import SignalProcessor
from core.bpm_estimation import BPMEstimator

# Utils
from utils.signal_quality import SignalQuality

# UI module
from ui.visualizer import FullscreenVisualizer

# Configuration
from config import DEFAULT_CONFIG


class RPPGApplication:
    """
    Main rPPG application class.
    
    Orchestrates all components for real-time heart rate monitoring.
    Handles camera capture, signal processing pipeline, and visualization.
    
    Attributes:
        config: Application configuration
        face_detector: Face and ROI detection
        roi_selector: ROI quality assessment
        signal_processor: POS signal extraction
        bpm_estimator: Multi-method BPM calculation
        visualizer: Real-time UI
        running: Application state
    """
    
    def __init__(self, config=None):
        """
        Initialize rPPG application.
        
        Args:
            config: AppConfig instance (uses DEFAULT_CONFIG if None)
        """
        self.config = config or DEFAULT_CONFIG
        
        print("=" * 70)
        print("rPPG Heart Rate Monitor - Starting...")
        print("=" * 70)
        
        # Initialize components
        print("📸 Loading face detector...")
        self.face_detector = FaceDetector()
        
        print("🎯 Loading ROI selector...")
        self.roi_selector = ROISelector()
        
        print("📊 Loading signal processor...")
        self.signal_processor = SignalProcessor(
            fps=self.config.camera.target_fps,
            window_size=self.config.signal.window_size_seconds
        )
        
        print("❤️  Loading BPM estimator...")
        self.bpm_estimator = BPMEstimator(
            fps=self.config.camera.target_fps,
            bpm_min=self.config.signal.bpm_min,
            bpm_max=self.config.signal.bpm_max
        )
        
        print("🖥️  Loading visualizer...")
        self.visualizer = FullscreenVisualizer(
            width=self.config.ui.window_width,
            height=self.config.ui.window_height
        )
        
        # Application state
        self.running = False
        self.bpm = None
        self.confidence = None
        self.sqi = None
        self.motion_detected = False
        self.roi_quality = None
        
        # Statistics
        self.total_frames = 0
        self.successful_frames = 0
        
        # Previous signal for motion detection
        self.previous_signal = None
        
        print("\n✅ Application initialized successfully!")
        self._print_instructions()
    
    def _print_instructions(self):
        """Print user instructions."""
        print("\n" + "=" * 70)
        print("📌 INSTRUCTIONS")
        print("=" * 70)
        print("  1. Position your face centered in the camera")
        print("  2. Ensure good lighting (avoid backlighting)")
        print("  3. Stay still for 6-10 seconds")
        print("  4. Wait for confidence to rise above 60%")
        print("\n🎮 CONTROLS")
        print("  SPACE: Toggle instructions overlay")
        print("  Q / ESC: Quit application")
        print("=" * 70)
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Process single video frame.
        
        Pipeline:
        1. Detect face and extract ROIs
        2. Assess ROI quality and fuse signals
        3. Extract and process pulse signal
        4. Estimate BPM with confidence
        5. Update visualization
        
        Args:
            frame: Input BGR frame from camera
            
        Returns:
            Visualization canvas
        """
        self.total_frames += 1
        
        # Step 1: Detect face
        face_landmarks = self.face_detector.detect(frame)
        
        if face_landmarks is None:
            # No face detected
            return self.visualizer.update(
                video_frame=frame,
                bpm=None,
                confidence=None,
                sqi=None,
                motion_detected=False,
                roi_quality=None
            )
        
        # Step 2: Extract ROIs
        forehead, left_cheek, right_cheek = self.face_detector.extract_roi(
            frame, face_landmarks
        )
        
        # Step 3: Multi-ROI fusion
        rois, weights = self.roi_selector.get_multi_roi_weights(
            forehead, left_cheek, right_cheek
        )
        
        if len(rois) == 0:
            # No valid ROIs
            return self.visualizer.update(
                video_frame=frame,
                bpm=None,
                confidence=None,
                sqi=None,
                motion_detected=False,
                roi_quality=0.0
            )
        
        # Average ROI quality
        self.roi_quality = np.mean(weights)
        
        # Extract fused RGB signal
        rgb_signal = SignalExtractor.extract_multi_roi_fusion(rois, weights)
        
        # Draw ROI visualization
        frame_annotated = self.face_detector.draw_face_mesh(frame, face_landmarks)
        
        # Step 4: Add signal to processor
        self.signal_processor.add_signal(rgb_signal)
        
        # Check if we have enough data
        min_frames = self.config.camera.target_fps * self.config.signal.min_buffer_seconds
        
        if len(self.signal_processor.red_buffer) >= min_frames:
            self.successful_frames += 1
            
            # Extract pulse signal
            pulse_signal = self.signal_processor.extract_pulse_signal()
            
            if pulse_signal is not None:
                # Compute signal quality
                self.sqi = SignalQuality.compute_sqi(pulse_signal)
                
                # Detect motion
                self.motion_detected = SignalQuality.assess_motion(
                    pulse_signal, self.previous_signal
                )
                self.previous_signal = pulse_signal.copy()
                
                # Estimate BPM
                self.bpm, self.confidence = self.bpm_estimator.estimate(pulse_signal)
                
                # Adjust confidence for motion
                if self.motion_detected:
                    self.confidence *= 0.7
        
        # Step 5: Visualize
        canvas = self.visualizer.update(
            video_frame=frame_annotated,
            bpm=self.bpm,
            confidence=self.confidence,
            sqi=self.sqi,
            motion_detected=self.motion_detected,
            roi_quality=self.roi_quality
        )
        
        return canvas
    
    def run(self):
        """
        Start real-time monitoring loop.
        
        Captures frames from camera, processes them, and displays results
        until user quits.
        """
        self.running = True
        
        # Open camera
        cap = cv2.VideoCapture(self.config.camera.device_index)
        
        if not cap.isOpened():
            print("\n❌ ERROR: Cannot open camera!")
            print("   Please check:")
            print("   - Camera is connected")
            print("   - No other app is using the camera")
            print("   - Camera permissions are granted")
            return
        
        # Configure camera
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera.capture_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera.capture_height)
        cap.set(cv2.CAP_PROP_FPS, self.config.camera.target_fps)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, self.config.camera.buffer_size)
        
        # Create window
        window_name = "rPPG Heart Rate Monitor"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        if self.config.ui.fullscreen:
            cv2.setWindowProperty(
                window_name,
                cv2.WND_PROP_FULLSCREEN,
                cv2.WINDOW_FULLSCREEN
            )
        
        print("\n🎥 Camera started. Press Q to quit.\n")
        
        try:
            while self.running:
                ret, frame = cap.read()
                
                if not ret:
                    print("⚠️  Warning: Failed to read frame")
                    continue
                
                # Process frame
                canvas = self.process_frame(frame)
                
                # Display
                cv2.imshow(window_name, canvas)
                
                # Handle keyboard
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == 27:  # Q or ESC
                    self.running = False
                elif key == ord(' '):  # SPACE
                    self.visualizer.show_instructions = not self.visualizer.show_instructions
        
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        
        finally:
            # Cleanup
            print("\n🛑 Shutting down...")
            cap.release()
            cv2.destroyAllWindows()
            
            # Print statistics
            self._print_statistics()
    
    def _print_statistics(self):
        """Print session statistics."""
        print("\n" + "=" * 70)
        print("📊 SESSION STATISTICS")
        print("=" * 70)
        print(f"  Total frames: {self.total_frames}")
        print(f"  Successful frames: {self.successful_frames}")
        
        if self.total_frames > 0:
            success_rate = (self.successful_frames / self.total_frames) * 100
            print(f"  Success rate: {success_rate:.1f}%")
        
        if self.bpm is not None:
            print(f"  Final BPM: {self.bpm:.1f}")
            print(f"  Final confidence: {self.confidence*100:.1f}%")
        
        print("=" * 70)
        print("\n✅ Application closed successfully!")


def main():
    """Main entry point."""
    app = RPPGApplication()
    app.run()


if __name__ == "__main__":
    main()
