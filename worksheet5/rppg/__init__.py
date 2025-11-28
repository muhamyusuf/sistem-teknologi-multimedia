"""
rPPG Heart Rate Monitor - Package Root

Real-time contactless heart rate monitoring using webcam and computer vision.

This package provides a complete rPPG system with modular architecture:
    - Core processing modules (face detection, signal processing, BPM estimation)
    - Utility functions (signal quality, motion detection)
    - Modern user interface (fullscreen visualization)
    - Centralized configuration management

Quick Start:
    from app import RPPGApplication
    
    app = RPPGApplication()
    app.run()

Module Structure:
    - core/          : Core processing algorithms
    - utils/         : Helper functions and utilities
    - ui/            : User interface components
    - config.py      : Configuration management
    - app.py         : Main application

Author: Muhammad Yusuf
Version: 2.1.0
Date: November 2025
"""

__version__ = "2.1.0"
__author__ = "Muhammad Yusuf"

# Core modules - New modular imports
from core.face_detection import FaceDetector
from core.roi_selection import ROISelector
from core.signal_extraction import SignalExtractor
from core.signal_processing import SignalProcessor
from core.bpm_estimation import BPMEstimator

# Utils
from utils.signal_quality import SignalQuality

# UI
from ui.visualizer import FullscreenVisualizer

# Configuration
from config import DEFAULT_CONFIG, AppConfig

# Main application
from app import RPPGApplication

# Public API
__all__ = [
    '__version__',
    '__author__',
    'FaceDetector',
    'ROISelector',
    'SignalExtractor',
    'SignalProcessor',
    'BPMEstimator',
    'SignalQuality',
    'FullscreenVisualizer',
    'DEFAULT_CONFIG',
    'AppConfig',
    'RPPGApplication',
]
