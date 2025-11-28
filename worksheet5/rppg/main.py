"""
rPPG Heart Rate Monitor - Main Application
Modern fullscreen UI with advanced signal processing and quality metrics.

Author: Muhammad Yusuf
Version: 2.0
Date: November 2025
"""

import cv2
import numpy as np
import time
from collections import deque

# Import our modules
from face_detector import FaceDetector
from roi_selector import AdaptiveROISelector
from signal_processor import AdvancedSignalProcessor
from visualizer import FullscreenVisualizer


class FullscreenRPPGSystem:
    """
    Complete rPPG system dengan modern fullscreen UI.
    Mengintegrasikan semua komponen: detection, processing, dan visualization.
    """
    
    def __init__(self, camera_index=0, fps=30):
        """
        Initialize sistem rPPG.
        
        Args:
            camera_index: Index kamera (default 0 untuk webcam utama)
            fps: Frame rate target (default 30)
        """
        print("=" * 70)
        print("Initializing rPPG Heart Rate Monitor System...")
        print("=" * 70)
        
        # Initialize components
        print("Loading face detector...")
        self.face_detector = FaceDetector()
        
        print("Loading ROI selector...")
        self.roi_selector = AdaptiveROISelector()
        
        print("Loading signal processor...")
        self.signal_processor = AdvancedSignalProcessor(fps=fps)
        
        print("Loading fullscreen visualizer...")
        # Use 720p for better performance
        self.visualizer = FullscreenVisualizer(width=1280, height=720)
        
        # Camera settings
        self.camera_index = camera_index
        self.fps = fps
        
        # Signal buffer
        self.signal_buffer = deque(maxlen=300)  # 10 detik di 30 FPS
        self.timestamp_buffer = deque(maxlen=300)
        
        # Frame quality tracking
        self.quality_buffer = deque(maxlen=100)
        
        # State
        self.running = False
        self.bpm = None
        self.confidence = None
        self.sqi = None
        self.motion_detected = False
        self.roi_quality = None
        
        # Statistics
        self.total_frames = 0
        self.successful_frames = 0
        
        print("✅ System initialized successfully!")
        print()
        print("📌 Instructions:")
        print("   - Position your face in the camera")
        print("   - Ensure good lighting conditions")
        print("   - Stay still for accurate measurements")
        print("   - SPACE: Toggle instructions overlay")
        print("   - F: Toggle fullscreen mode")
        print("   - Q or ESC: Quit application")
        print("=" * 70)
    
    def process_frame(self, frame):
        """
        Process single frame dan return visualization.
        
        Args:
            frame: Input frame dari camera
            
        Returns:
            Processed canvas untuk display
        """
        self.total_frames += 1
        
        # Face detection
        face_mesh = self.face_detector.detect(frame)
        
        if face_mesh is None:
            # No face detected
            canvas = self.visualizer.update(
                video_frame=frame,
                bpm=None,
                confidence=None,
                sqi=None,
                motion_detected=False,
                roi_quality=None
            )
            return canvas
        
        # Extract ROIs
        forehead_roi, left_cheek_roi, right_cheek_roi = self.face_detector.extract_roi(frame, face_mesh)
        
        if forehead_roi is None:
            canvas = self.visualizer.update(
                video_frame=frame,
                bpm=None,
                confidence=None,
                sqi=None,
                motion_detected=False,
                roi_quality=None
            )
            return canvas
        
        # Multi-ROI Fusion: Assess quality dan combine signals
        roi_signals = []
        roi_qualities = []
        
        for roi in [forehead_roi, left_cheek_roi, right_cheek_roi]:
            if roi is not None:
                # Extract signal
                rgb = self.signal_processor.extract_signal(roi)
                if rgb is not None:
                    # Assess quality
                    quality = self.roi_selector.assess_roi_quality(roi)
                    roi_signals.append(rgb)
                    roi_qualities.append(quality)
        
        # Draw ROI pada video frame untuk feedback
        frame_with_roi = frame.copy()
        if face_mesh is not None:
            frame_with_roi = self.face_detector.draw_face_mesh(frame_with_roi, face_mesh)
        
        # Fuse multi-ROI dengan weighted average
        current_time = time.time()
        if len(roi_signals) == 0:
            rgb_signal = None
            self.roi_quality = 0.0
        elif len(roi_signals) == 1:
            rgb_signal = roi_signals[0]
            self.roi_quality = roi_qualities[0]
        else:
            # Weighted fusion
            qualities = np.array(roi_qualities)
            qualities = qualities / (np.sum(qualities) + 1e-8)  # Normalize weights
            
            rgb_signal = np.zeros(3)
            for sig, weight in zip(roi_signals, qualities):
                rgb_signal += sig * weight
            
            self.roi_quality = np.mean(roi_qualities)  # Average quality
        
        if rgb_signal is not None:
            self.successful_frames += 1
            
            # Add to processor buffer
            self.signal_processor.add_values(
                rgb_signal[0], rgb_signal[1], rgb_signal[2]
            )
            
            # Process jika buffer cukup (minimal 6 detik - balanced)
            if len(self.signal_processor.red_buffer) >= self.fps * 6:
                # Get pulse signal
                pulse_signal = self.signal_processor.pos_method()
                
                if pulse_signal is not None:
                    # Estimate BPM dengan advanced metrics
                    result = self.signal_processor.estimate_bpm_with_confidence(pulse_signal)
                    
                    if result[0] is not None:
                        self.bpm, self.confidence, self.sqi = result
                        self.motion_detected = self.signal_processor.motion_detected
        
        # Update visualization
        canvas = self.visualizer.update(
            video_frame=frame_with_roi,
            bpm=self.bpm,
            confidence=self.confidence,
            sqi=self.sqi,
            motion_detected=self.motion_detected,
            roi_quality=self.roi_quality
        )
        
        return canvas
    
    def start(self):
        """
        Start real-time system dengan fullscreen UI.
        """
        self.running = True
        cap = cv2.VideoCapture(self.camera_index)
        
        if not cap.isOpened():
            print("❌ Error: Cannot access camera!")
            print("   Please check:")
            print("   - Camera is connected and working")
            print("   - No other application is using the camera")
            print("   - Camera permissions are granted")
            return
        
        # Set camera resolution (reduced for better performance)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Create fullscreen window
        window_name = "rPPG Heart Rate Monitor - Fullscreen"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        print("\n🚀 System started!")
        print("Camera initialized - Processing frames...")
        print()
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while self.running:
                ret, frame = cap.read()
                
                if not ret:
                    print("⚠ Warning: Failed to grab frame")
                    continue
                
                # Flip frame untuk mirror effect
                frame = cv2.flip(frame, 1)
                
                frame_count += 1
                
                # Process frame
                canvas = self.process_frame(frame)
                
                # Display
                cv2.imshow(window_name, canvas)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == 27:  # Q or ESC
                    print("\n🛑 Stopping system...")
                    break
                elif key == ord(' '):  # SPACE
                    self.visualizer.show_instructions = not self.visualizer.show_instructions
                    status = "shown" if self.visualizer.show_instructions else "hidden"
                    print(f"ℹ Instructions {status}")
                elif key == ord('f'):  # F untuk toggle fullscreen
                    is_fullscreen = cv2.getWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN)
                    if is_fullscreen == cv2.WINDOW_FULLSCREEN:
                        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                        print("ℹ Windowed mode")
                    else:
                        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                        print("ℹ Fullscreen mode")
        
        except KeyboardInterrupt:
            print("\n⚠ Interrupted by user")
        
        except Exception as e:
            print(f"\n❌ Error occurred: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup
            self.cleanup(cap, start_time, frame_count)
    
    def cleanup(self, cap, start_time, frame_count):
        """
        Cleanup resources dan print session summary.
        """
        self.running = False
        
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()
        
        # Statistics
        elapsed_time = time.time() - start_time
        avg_fps = frame_count / elapsed_time if elapsed_time > 0 else 0
        success_rate = (self.successful_frames / self.total_frames * 100) if self.total_frames > 0 else 0
        
        print("\n" + "=" * 70)
        print("📊 SESSION SUMMARY")
        print("=" * 70)
        print(f"Total Runtime: {elapsed_time:.1f} seconds")
        print(f"Frames Processed: {self.total_frames}")
        print(f"Average FPS: {avg_fps:.1f}")
        print(f"Successful Detections: {self.successful_frames} ({success_rate:.1f}%)")
        
        if self.bpm is not None and self.confidence is not None:
            print(f"\nFinal Heart Rate Measurement:")
            print(f"  BPM: {self.bpm:.1f}")
            print(f"  Confidence: {self.confidence*100:.1f}%")
            print(f"  Signal Quality: {self.sqi*100:.1f}%" if self.sqi else "")
            
            # Reliability assessment
            if self.confidence > 0.7 and (self.sqi is None or self.sqi > 0.7):
                reliability = "✓ RELIABLE - Measurement is trustworthy"
            elif self.confidence > 0.5:
                reliability = "⚠ MODERATE - Use with caution"
            else:
                reliability = "✗ LOW - Take another measurement"
            
            print(f"  Reliability: {reliability}")
            
            # Health interpretation
            if self.confidence > 0.6:
                if 60 <= self.bpm <= 100:
                    print(f"  Interpretation: Normal resting heart rate")
                elif 50 <= self.bpm < 60:
                    print(f"  Interpretation: Below normal (athletic/bradycardia)")
                elif 100 < self.bpm <= 120:
                    print(f"  Interpretation: Above normal (tachycardia)")
                else:
                    print(f"  Interpretation: Abnormal - consult healthcare provider")
        else:
            print("\nNo reliable measurements obtained.")
            print("Tips for better results:")
            print("  - Ensure good lighting (natural light is best)")
            print("  - Position face clearly in camera view")
            print("  - Minimize movement during measurement")
            print("  - Wait at least 10 seconds for stabilization")
        
        print("=" * 70)
        print("✅ System stopped successfully")
        print("Thank you for using rPPG Heart Rate Monitor!")
        print("=" * 70)


def main():
    """
    Main entry point untuk aplikasi.
    """
    print()
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║          rPPG HEART RATE MONITOR - FULLSCREEN EDITION             ║")
    print("║                    Version 2.0 - November 2025                    ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print()
    
    # Create and start system
    try:
        system = FullscreenRPPGSystem(camera_index=0, fps=30)
        system.start()
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\nPress Enter to exit...")
    input()


if __name__ == "__main__":
    main()
