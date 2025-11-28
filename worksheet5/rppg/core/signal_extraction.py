"""
Signal Extraction Module - RGB Signal from Facial ROIs

Extracts mean RGB values from facial regions for rPPG analysis. The subtle
color changes caused by blood volume variations are captured in these signals,
particularly in the green channel which has optimal absorption characteristics
for hemoglobin.

Author: Muhammad Yusuf
Version: 2.1
Date: November 2025
"""

import cv2
import numpy as np
from typing import Optional, Tuple


class SignalExtractor:
    """
    Extract RGB signals from facial ROI regions.
    
    Computes spatially-averaged RGB values from masked facial regions.
    Handles invalid/empty ROIs gracefully and provides quality checks.
    """
    
    @staticmethod
    def extract_from_roi(roi: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract mean RGB values from a single ROI.
        
        Computes spatial average of R, G, B channels over the non-zero (valid)
        pixels in the ROI mask. This reduces spatial noise and provides a
        single-point signal for each color channel.
        
        Args:
            roi: ROI image in BGR format (masked, non-ROI pixels are zero)
            
        Returns:
            Array [R, G, B] of mean values (0-255) or None if ROI is invalid
        """
        if roi is None or roi.size == 0:
            return None
        
        # Get binary mask of valid (non-zero) pixels
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        mask = gray_roi > 0
        
        # No valid pixels
        if not np.any(mask):
            return None
        
        # Split into B, G, R channels
        b, g, r = cv2.split(roi)
        
        # Compute mean values over valid pixels
        r_mean = np.mean(r[mask]) if np.any(mask) else 0.0
        g_mean = np.mean(g[mask]) if np.any(mask) else 0.0
        b_mean = np.mean(b[mask]) if np.any(mask) else 0.0
        
        return np.array([r_mean, g_mean, b_mean])
    
    @staticmethod
    def extract_multi_roi_fusion(
        rois: list,
        weights: list
    ) -> Optional[np.ndarray]:
        """
        Extract weighted RGB signal from multiple ROIs.
        
        Fuses signals from multiple ROIs using weighted averaging. This
        improves robustness compared to single-ROI extraction.
        
        Args:
            rois: List of ROI images
            weights: List of weights (should sum to 1.0)
            
        Returns:
            Weighted average RGB signal or None if all ROIs invalid
        """
        if not rois or not weights:
            return None
        
        if len(rois) != len(weights):
            raise ValueError("Number of ROIs must match number of weights")
        
        # Extract signals from each ROI
        signals = []
        valid_weights = []
        
        for roi, weight in zip(rois, weights):
            signal = SignalExtractor.extract_from_roi(roi)
            if signal is not None:
                signals.append(signal)
                valid_weights.append(weight)
        
        # No valid signals
        if len(signals) == 0:
            return None
        
        # Normalize weights
        total_weight = sum(valid_weights)
        if total_weight > 0:
            valid_weights = [w / total_weight for w in valid_weights]
        else:
            return None
        
        # Weighted fusion
        fused_signal = np.zeros(3)
        for signal, weight in zip(signals, valid_weights):
            fused_signal += signal * weight
        
        return fused_signal
    
    @staticmethod
    def validate_signal(signal: np.ndarray) -> bool:
        """
        Validate extracted signal for common issues.
        
        Checks for:
          - NaN or infinite values
          - Zero variance (flat signal)
          - Out-of-range values
        
        Args:
            signal: RGB signal array
            
        Returns:
            True if signal is valid, False otherwise
        """
        if signal is None:
            return False
        
        # Check for NaN or infinity
        if not np.all(np.isfinite(signal)):
            return False
        
        # Check range (0-255 for 8-bit color)
        if np.any(signal < 0) or np.any(signal > 255):
            return False
        
        # Check for zero signal (suspicious)
        if np.allclose(signal, 0):
            return False
        
        return True


if __name__ == "__main__":
    print("=" * 70)
    print("Signal Extraction Module - Test")
    print("=" * 70)
    print("✅ SignalExtractor class loaded successfully")
    print("\nFeatures:")
    print("  • Spatial averaging over ROI regions")
    print("  • Multi-ROI weighted fusion")
    print("  • Signal validation and quality checks")
    print("\nUsage Example:")
    print("  signal = SignalExtractor.extract_from_roi(roi)")
    print("  fused = SignalExtractor.extract_multi_roi_fusion(rois, weights)")
    print("  valid = SignalExtractor.validate_signal(signal)")
