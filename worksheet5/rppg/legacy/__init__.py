"""
Legacy Module - Backward Compatibility

This directory contains the original monolithic implementation files 
for backward compatibility. These files are kept for reference and 
to support existing code that might import from the old structure.

⚠️ DEPRECATED: Use the new modular structure instead
    - core/ - Core processing modules
    - utils/ - Utility functions
    - ui/ - User interface components
    - config.py - Configuration management
    - app.py - Main application entry point

Migration Guide:
    Old: from face_detector import FaceDetector
    New: from core.face_detection import FaceDetector
    
    Old: from signal_processor import SignalProcessor, BPMEstimator
    New: from core.signal_processing import SignalProcessor
         from core.bpm_estimation import BPMEstimator
    
    Old: from visualizer import FullscreenVisualizer
    New: from ui.visualizer import FullscreenVisualizer

Files in this directory:
    - main.py - Original monolithic application
    - face_detector.py - Original face detection
    - roi_selector.py - Original ROI selection
    - signal_processor.py - Original signal processing
    - visualizer.py - Original UI module (moved to ui/)

Author: Muhammad Yusuf
Version: 2.1
Date: November 2025
"""

__all__ = []  # Nothing exported from legacy module
__deprecated__ = True
