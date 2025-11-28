"""
Core Package - Signal Processing and Detection Modules

This package contains the core functionality for rPPG heart rate monitoring:
- Face detection and landmark extraction
- ROI (Region of Interest) selection and quality assessment  
- Signal extraction from facial regions
- Signal processing with POS method
- BPM estimation using multiple methods

Author: Muhammad Yusuf
Version: 2.1
"""

__all__ = [
    'FaceDetector',
    'ROISelector',
    'SignalExtractor',
    'SignalProcessor',
    'BPMEstimator',
]
