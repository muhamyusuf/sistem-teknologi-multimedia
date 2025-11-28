"""
Configuration Module for rPPG Heart Rate Monitor

Contains all system-wide configuration parameters, constants, and settings.
This centralized configuration makes it easy to tune the system without 
modifying core logic.

Author: Muhammad Yusuf
Version: 2.1
Date: November 2025
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class CameraConfig:
    """Camera and video capture settings."""
    
    # Camera device
    device_index: int = 0
    
    # Resolution settings
    capture_width: int = 640
    capture_height: int = 480
    target_fps: int = 30
    
    # Buffer size (prevents frame lag)
    buffer_size: int = 1


@dataclass
class UIConfig:
    """User interface display settings."""
    
    # Window dimensions
    window_width: int = 1280
    window_height: int = 720
    fullscreen: bool = True
    
    # Panel layout
    padding: int = 30
    gap: int = 20
    
    # Video panel
    video_panel_width: int = 600
    video_panel_height: int = 450
    
    # Color scheme (BGR format)
    color_bg: Tuple[int, int, int] = (20, 20, 25)
    color_panel: Tuple[int, int, int] = (35, 35, 40)
    color_accent: Tuple[int, int, int] = (0, 150, 255)  # Orange
    color_success: Tuple[int, int, int] = (0, 255, 100)  # Green
    color_warning: Tuple[int, int, int] = (0, 200, 255)  # Yellow
    color_danger: Tuple[int, int, int] = (60, 60, 255)  # Red
    color_text: Tuple[int, int, int] = (255, 255, 255)  # White
    color_text_dim: Tuple[int, int, int] = (150, 150, 150)  # Gray


@dataclass
class SignalConfig:
    """Signal processing parameters."""
    
    # Temporal settings
    window_size_seconds: int = 10
    min_buffer_seconds: int = 6
    
    # BPM range constraints (in BPM)
    bpm_min: int = 45
    bpm_max: int = 150
    
    # Frequency range (in Hz, for filtering)
    freq_min: float = 0.75  # 45 BPM
    freq_max: float = 2.5   # 150 BPM
    
    # Quality thresholds
    sqi_threshold: float = 0.08
    confidence_threshold: float = 0.15
    
    # Filter parameters
    butterworth_order: int = 4
    median_kernel_ratio: float = 0.1  # Relative to FPS


@dataclass
class ROIConfig:
    """Region of Interest selection settings."""
    
    # Quality assessment weights
    weight_exposure: float = 0.4
    weight_saturation: float = 0.3
    weight_green_prominence: float = 0.3
    
    # Quality thresholds
    exposure_min: float = 0.2
    exposure_max: float = 0.8
    saturation_min: float = 0.1
    green_ratio_min: float = 0.35


@dataclass
class PerformanceConfig:
    """Performance and optimization settings."""
    
    # History buffer sizes
    bpm_history_size: int = 30
    quality_history_size: int = 100
    frame_time_history: int = 30
    
    # Graph display settings
    graph_history_points: int = 200
    
    # Consistency checking
    bpm_jump_threshold_large: int = 20
    bpm_jump_threshold_medium: int = 15
    bpm_jump_threshold_small: int = 10


class AppConfig:
    """
    Main application configuration class.
    Aggregates all configuration modules for easy access.
    """
    
    def __init__(self):
        self.camera = CameraConfig()
        self.ui = UIConfig()
        self.signal = SignalConfig()
        self.roi = ROIConfig()
        self.performance = PerformanceConfig()
    
    def __repr__(self):
        """String representation for debugging."""
        return (
            f"AppConfig(\n"
            f"  Camera: {self.camera.capture_width}x{self.camera.capture_height} @ {self.camera.target_fps}fps\n"
            f"  UI: {self.ui.window_width}x{self.ui.window_height}\n"
            f"  BPM Range: {self.signal.bpm_min}-{self.signal.bpm_max}\n"
            f"  Window: {self.signal.window_size_seconds}s\n"
            f")"
        )


# Default configuration instance
DEFAULT_CONFIG = AppConfig()


if __name__ == "__main__":
    # Configuration test
    print("=" * 70)
    print("rPPG System Configuration")
    print("=" * 70)
    print(DEFAULT_CONFIG)
    print("\n✅ Configuration module loaded successfully!")
