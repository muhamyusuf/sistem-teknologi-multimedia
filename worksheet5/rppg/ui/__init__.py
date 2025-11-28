"""
UI Package - User Interface Components

Modern fullscreen UI with real-time visualization of heart rate data,
signal quality metrics, and live camera feed.

Features:
    - FullscreenVisualizer: Main UI class for rPPG monitoring
    - Anti-aliased fonts and smooth animations
    - Real-time graphs and metrics panels
    - Adaptive color-coded quality indicators

Author: Muhammad Yusuf
Version: 2.1
Date: November 2025
"""

from .visualizer import FullscreenVisualizer

__all__ = [
    'FullscreenVisualizer',
]

__version__ = '2.1.0'
