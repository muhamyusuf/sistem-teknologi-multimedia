"""
Signal Processing Module - POS Method Implementation

Implements the Plane-Orthogonal-to-Skin (POS) method for extracting pulse signals
from RGB color changes. POS is a blind source separation technique that projects
RGB signals onto a plane orthogonal to the skin tone, isolating the pulsatile
component caused by blood volume variations.

Reference:
  Wang, W., den Brinker, A. C., Stuijk, S., & de Haan, G. (2017).
  "Algorithmic principles of remote PPG."
  IEEE Transactions on Biomedical Engineering, 64(7), 1479-1491.

Author: Muhammad Yusuf
Version: 2.1
Date: November 2025
"""

import numpy as np
from scipy import signal
from collections import deque
from typing import Optional


class SignalProcessor:
    """
    POS-based signal processor for rPPG pulse extraction.
    
    Maintains temporal buffers of RGB signals and applies the POS algorithm
    to extract the underlying pulse signal. Includes advanced preprocessing
    (detrending, filtering) and interpolation for missing values.
    
    Attributes:
        fps: Frame rate (Hz)
        window_size: Analysis window duration (seconds)
        buffer_size: Maximum buffer length (frames)
        red_buffer: Red channel signal buffer
        green_buffer: Green channel signal buffer
        blue_buffer: Blue channel signal buffer
    """
    
    def __init__(self, fps: int = 30, window_size: int = 10):
        """
        Initialize signal processor with temporal buffers.
        
        Args:
            fps: Camera frame rate in Hz (default 30)
            window_size: Signal buffer window in seconds (default 10)
        """
        self.fps = fps
        self.window_size = window_size
        self.buffer_size = fps * window_size
        
        # RGB signal buffers (circular buffers)
        self.red_buffer = deque(maxlen=self.buffer_size)
        self.green_buffer = deque(maxlen=self.buffer_size)
        self.blue_buffer = deque(maxlen=self.buffer_size)
    
    def add_signal(self, rgb_signal: np.ndarray) -> None:
        """
        Add new RGB signal to buffers.
        
        Args:
            rgb_signal: Array [R, G, B] of signal values
        """
        if rgb_signal is None or len(rgb_signal) != 3:
            # Add NaN for missing frames (will be interpolated)
            rgb_signal = np.array([np.nan, np.nan, np.nan])
        
        self.red_buffer.append(rgb_signal[0])
        self.green_buffer.append(rgb_signal[1])
        self.blue_buffer.append(rgb_signal[2])
    
    def extract_pulse_signal(self) -> Optional[np.ndarray]:
        """
        Extract pulse signal using POS method.
        
        The POS algorithm:
        1. Normalize RGB signals (zero-mean, unit variance)
        2. Project onto plane orthogonal to skin tone
        3. Combine projections to extract pulse
        4. Apply advanced detrending and filtering
        
        Returns:
            Pulse signal array or None if insufficient data
        """
        # Need minimum 3 seconds of data
        min_length = self.fps * 3
        if len(self.red_buffer) < min_length:
            return None
        
        # Convert buffers to numpy arrays
        red = np.array(list(self.red_buffer))
        green = np.array(list(self.green_buffer))
        blue = np.array(list(self.blue_buffer))
        
        # Interpolate missing values (NaN)
        red = self._interpolate_nans(red)
        green = self._interpolate_nans(green)
        blue = self._interpolate_nans(blue)
        
        # Normalize signals (zero-mean, unit variance)
        red_norm = self._normalize_signal(red)
        green_norm = self._normalize_signal(green)
        blue_norm = self._normalize_signal(blue)
        
        # Stack into matrix [R, G, B] x N
        X = np.vstack([red_norm, green_norm, blue_norm])
        
        # POS projection matrix
        # C = [[0, 1, -1], [-2, 1, 1]]
        # This projects RGB onto plane orthogonal to skin tone vector
        C = np.array([[0, 1, -1], [-2, 1, 1]], dtype=np.float32)
        
        # Project signals
        S = np.dot(C, X)  # Shape: (2, N)
        
        # Combine projections with adaptive weighting
        # alpha balances the two projections based on their standard deviations
        std_s0 = np.std(S[0, :])
        std_s1 = np.std(S[1, :])
        alpha = std_s0 / (std_s1 + 1e-8)
        
        pulse_signal = S[0, :] + alpha * S[1, :]
        
        # Advanced preprocessing
        pulse_signal = self._advanced_detrending(pulse_signal)
        pulse_signal = self._temporal_smoothing(pulse_signal)
        
        return pulse_signal
    
    def _normalize_signal(self, sig: np.ndarray) -> np.ndarray:
        """
        Normalize signal to zero-mean and unit variance.
        
        Args:
            sig: Input signal
            
        Returns:
            Normalized signal
        """
        mean = np.mean(sig)
        std = np.std(sig)
        
        if std < 1e-8:
            return sig - mean
        
        return (sig - mean) / std
    
    def _interpolate_nans(self, sig: np.ndarray) -> np.ndarray:
        """
        Linearly interpolate NaN values in signal.
        
        Args:
            sig: Signal array possibly containing NaN
            
        Returns:
            Signal with NaN values interpolated
        """
        nans = np.isnan(sig)
        
        if not np.any(nans):
            return sig
        
        # Get valid indices
        x = np.arange(len(sig))
        valid_mask = ~nans
        
        if not np.any(valid_mask):
            # All NaN - return zeros
            return np.zeros_like(sig)
        
        # Linear interpolation
        sig[nans] = np.interp(x[nans], x[valid_mask], sig[valid_mask])
        
        return sig
    
    def _advanced_detrending(self, sig: np.ndarray) -> np.ndarray:
        """
        Remove polynomial and linear trends from signal.
        
        Eliminates slow drifts and baseline wander that can interfere
        with pulse detection.
        
        Args:
            sig: Input pulse signal
            
        Returns:
            Detrended signal
        """
        # Remove quadratic polynomial trend
        x = np.arange(len(sig))
        coeffs = np.polyfit(x, sig, deg=2)
        poly_trend = np.polyval(coeffs, x)
        sig_detrended = sig - poly_trend
        
        # Additional linear detrending
        sig_detrended = signal.detrend(sig_detrended, type='linear')
        
        return sig_detrended
    
    def _temporal_smoothing(self, sig: np.ndarray) -> np.ndarray:
        """
        Apply median filtering for temporal smoothing.
        
        Reduces high-frequency noise and impulse artifacts while
        preserving pulse shape.
        
        Args:
            sig: Input signal
            
        Returns:
            Smoothed signal
        """
        # Kernel size: ~0.1 seconds
        kernel_size = max(3, int(self.fps * 0.1))
        
        # Must be odd
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # Median filter (robust to outliers)
        smoothed = signal.medfilt(sig, kernel_size=kernel_size)
        
        return smoothed
    
    def reset(self) -> None:
        """Clear all signal buffers."""
        self.red_buffer.clear()
        self.green_buffer.clear()
        self.blue_buffer.clear()


if __name__ == "__main__":
    print("=" * 70)
    print("Signal Processing Module - Test")
    print("=" * 70)
    print("✅ SignalProcessor class loaded successfully")
    print("\nPOS Method Features:")
    print("  • Blind source separation technique")
    print("  • Projection onto plane orthogonal to skin tone")
    print("  • Advanced detrending (polynomial + linear)")
    print("  • Temporal smoothing with median filter")
    print("  • Automatic handling of missing values")
    print("\nUsage Example:")
    print("  processor = SignalProcessor(fps=30, window_size=10)")
    print("  processor.add_signal(rgb_signal)")
    print("  pulse = processor.extract_pulse_signal()")
