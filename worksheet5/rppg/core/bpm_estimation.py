"""
BPM Estimation Module - Multi-Method Heart Rate Calculation

Implements three complementary methods for BPM estimation:
  1. FFT-based frequency analysis (most accurate for stable signals)
  2. Autocorrelation for periodicity detection (robust to noise)
  3. Time-domain peak detection (validates other methods)

Multi-method fusion with confidence-weighted voting provides more robust
BPM estimates than any single method alone.

Author: Muhammad Yusuf
Version: 2.1
Date: November 2025
"""

import numpy as np
from scipy import signal
from typing import Tuple, Optional
from collections import deque


class BPMEstimator:
    """
    Multi-method BPM estimator with confidence scoring.
    
    Combines FFT, autocorrelation, and peak detection for robust heart rate
    estimation. Maintains history for temporal consistency checking.
    
    Attributes:
        fps: Frame rate (Hz)
        bpm_min: Minimum physiologically plausible BPM
        bpm_max: Maximum physiologically plausible BPM
        bpm_history: Recent BPM estimates for consistency checking
    """
    
    def __init__(
        self,
        fps: int = 30,
        bpm_min: int = 45,
        bpm_max: int = 150
    ):
        """
        Initialize BPM estimator.
        
        Args:
            fps: Signal sampling rate in Hz
            bpm_min: Minimum valid BPM (default 45)
            bpm_max: Maximum valid BPM (default 150)
        """
        self.fps = fps
        self.bpm_min = bpm_min
        self.bpm_max = bpm_max
        
        # Convert BPM range to Hz
        self.freq_min = bpm_min / 60.0
        self.freq_max = bpm_max / 60.0
        
        # BPM history for consistency checking
        self.bpm_history = deque(maxlen=30)
    
    def estimate(self, pulse_signal: np.ndarray) -> Tuple[Optional[float], float]:
        """
        Estimate BPM using multi-method fusion.
        
        Applies three independent estimation methods and combines their
        results using confidence-weighted averaging.
        
        Args:
            pulse_signal: Preprocessed pulse signal from POS method
            
        Returns:
            Tuple of (bpm, confidence) where:
              - bpm: Estimated heart rate in BPM (or None if failed)
              - confidence: Confidence score 0-1
        """
        if pulse_signal is None or len(pulse_signal) < self.fps * 3:
            return None, 0.0
        
        # Apply bandpass filter
        filtered_signal = self._bandpass_filter(pulse_signal)
        
        # Method 1: FFT-based estimation
        bpm_fft, conf_fft = self._estimate_fft(filtered_signal)
        
        # Method 2: Autocorrelation-based estimation
        bpm_autocorr, conf_autocorr = self._estimate_autocorrelation(filtered_signal)
        
        # Method 3: Peak detection
        bpm_peaks, conf_peaks = self._estimate_peaks(filtered_signal)
        
        # Collect valid estimates
        estimates = []
        confidences = []
        
        if bpm_fft is not None and conf_fft > 0.15:
            estimates.append(bpm_fft)
            confidences.append(conf_fft * 1.5)  # FFT gets higher weight
        
        if bpm_autocorr is not None and conf_autocorr > 0.15:
            estimates.append(bpm_autocorr)
            confidences.append(conf_autocorr * 0.8)
        
        if bpm_peaks is not None and conf_peaks > 0.15:
            estimates.append(bpm_peaks)
            confidences.append(conf_peaks * 1.0)
        
        # No valid estimates
        if len(estimates) == 0:
            return None, 0.0
        
        # Weighted average of estimates
        weights = np.array(confidences)
        weights = weights / np.sum(weights)
        
        bpm_final = np.average(estimates, weights=weights)
        
        # Consistency check
        consistency = self._check_consistency(bpm_final)
        
        # Final confidence
        base_confidence = np.mean(weights)
        final_confidence = base_confidence * consistency
        
        # Update history
        if final_confidence > 0.2:
            self.bpm_history.append(bpm_final)
        
        return bpm_final, final_confidence
    
    def _bandpass_filter(self, sig: np.ndarray) -> np.ndarray:
        """
        Apply adaptive bandpass filter.
        
        Filter range adapts based on BPM history for improved tracking.
        
        Args:
            sig: Input signal
            
        Returns:
            Bandpass filtered signal
        """
        # Adaptive frequency range based on history
        if len(self.bpm_history) > 5:
            median_bpm = np.median(list(self.bpm_history))
            # Narrow range around recent median
            freq_low = max(self.freq_min, (median_bpm - 20) / 60.0)
            freq_high = min(self.freq_max, (median_bpm + 20) / 60.0)
        else:
            # Default wide range
            freq_low = self.freq_min
            freq_high = self.freq_max
        
        # Normalize frequencies
        nyquist = self.fps / 2.0
        low_norm = freq_low / nyquist
        high_norm = freq_high / nyquist
        
        # Butterworth bandpass filter (4th order)
        b, a = signal.butter(4, [low_norm, high_norm], btype='band')
        filtered = signal.filtfilt(b, a, sig)
        
        return filtered
    
    def _estimate_fft(self, sig: np.ndarray) -> Tuple[Optional[float], float]:
        """
        FFT-based BPM estimation with parabolic interpolation.
        
        Finds dominant frequency in power spectrum and refines it using
        parabolic interpolation for sub-bin accuracy.
        
        Args:
            sig: Filtered pulse signal
            
        Returns:
            Tuple of (bpm, confidence)
        """
        # Compute FFT
        fft_vals = np.fft.rfft(sig)
        fft_freqs = np.fft.rfftfreq(len(sig), 1.0 / self.fps)
        fft_power = np.abs(fft_vals)
        
        # Valid frequency range
        valid_mask = (fft_freqs >= self.freq_min) & (fft_freqs <= self.freq_max)
        valid_power = fft_power[valid_mask]
        valid_freqs = fft_freqs[valid_mask]
        
        if len(valid_power) == 0:
            return None, 0.0
        
        # Find peak
        peak_idx = np.argmax(valid_power)
        peak_freq = valid_freqs[peak_idx]
        peak_power = valid_power[peak_idx]
        
        # Parabolic interpolation for sub-bin resolution
        if peak_idx > 0 and peak_idx < len(valid_power) - 1:
            alpha = valid_power[peak_idx - 1]
            beta = valid_power[peak_idx]
            gamma = valid_power[peak_idx + 1]
            
            # Parabola vertex offset
            p = 0.5 * (alpha - gamma) / (alpha - 2*beta + gamma + 1e-10)
            
            # Refined frequency
            freq_step = valid_freqs[1] - valid_freqs[0]
            peak_freq_refined = peak_freq + p * freq_step
            peak_freq = peak_freq_refined
        
        # Convert to BPM
        bpm = peak_freq * 60.0
        
        # Confidence from SNR
        noise_floor = np.median(valid_power)
        snr = peak_power / (noise_floor + 1e-10)
        confidence = min(snr / 12.0, 1.0)
        
        # Boost if harmonic detected
        harmonic_freq = peak_freq * 2
        if harmonic_freq <= self.freq_max:
            harmonic_mask = (valid_freqs >= harmonic_freq - 0.1) & (valid_freqs <= harmonic_freq + 0.1)
            if np.any(harmonic_mask):
                harmonic_power = np.max(valid_power[harmonic_mask])
                if harmonic_power > noise_floor * 2:
                    confidence *= 1.2
        
        confidence = min(confidence, 1.0)
        
        return bpm, confidence
    
    def _estimate_autocorrelation(self, sig: np.ndarray) -> Tuple[Optional[float], float]:
        """
        Autocorrelation-based BPM estimation.
        
        Finds periodicity in signal by computing autocorrelation and
        detecting the lag of maximum correlation.
        
        Args:
            sig: Filtered pulse signal
            
        Returns:
            Tuple of (bpm, confidence)
        """
        # Normalize signal
        sig_norm = (sig - np.mean(sig)) / (np.std(sig) + 1e-10)
        
        # Compute autocorrelation
        autocorr = np.correlate(sig_norm, sig_norm, mode='full')
        autocorr = autocorr[len(autocorr)//2:]  # Take positive lags only
        
        # Valid lag range (in samples)
        min_lag = int(60.0 / self.bpm_max * self.fps)
        max_lag = int(60.0 / self.bpm_min * self.fps)
        
        if max_lag >= len(autocorr):
            return None, 0.0
        
        # Find peak in valid range
        valid_autocorr = autocorr[min_lag:max_lag]
        peak_idx = np.argmax(valid_autocorr)
        peak_lag = min_lag + peak_idx
        
        # BPM from lag
        period_seconds = peak_lag / self.fps
        bpm = 60.0 / period_seconds
        
        # Confidence from peak height (normalized by zero-lag)
        peak_value = valid_autocorr[peak_idx]
        zero_lag_value = autocorr[0]
        confidence = peak_value / (zero_lag_value + 1e-10)
        
        # Rescale confidence
        confidence = max(confidence - 0.3, 0.0) / 0.7
        confidence = min(confidence, 1.0)
        
        return bpm, confidence
    
    def _estimate_peaks(self, sig: np.ndarray) -> Tuple[Optional[float], float]:
        """
        Peak detection-based BPM estimation.
        
        Detects peaks in pulse signal and computes average inter-beat interval.
        
        Args:
            sig: Filtered pulse signal
            
        Returns:
            Tuple of (bpm, confidence)
        """
        # Find peaks
        # Distance constraint: minimum 60/bpm_max seconds between peaks
        min_distance = int(60.0 / self.bpm_max * self.fps)
        
        peaks, properties = signal.find_peaks(
            sig,
            distance=min_distance,
            prominence=np.std(sig) * 0.3  # Adaptive threshold
        )
        
        if len(peaks) < 3:
            return None, 0.0
        
        # Compute inter-beat intervals
        intervals = np.diff(peaks) / self.fps  # Convert to seconds
        
        # Average interval
        mean_interval = np.mean(intervals)
        
        # BPM
        bpm = 60.0 / mean_interval
        
        # Confidence from consistency of intervals
        std_interval = np.std(intervals)
        cv = std_interval / (mean_interval + 1e-10)  # Coefficient of variation
        
        # Lower CV = higher confidence
        confidence = np.exp(-cv * 3.0)  # Exponential decay
        confidence = min(confidence, 1.0)
        
        return bpm, confidence
    
    def _check_consistency(self, bpm: float) -> float:
        """
        Check consistency with recent BPM history.
        
        Args:
            bpm: Current BPM estimate
            
        Returns:
            Consistency score 0-1
        """
        if len(self.bpm_history) < 5:
            return 1.0  # No history yet
        
        # Median of recent history
        median_bpm = np.median(list(self.bpm_history)[-5:])
        deviation = abs(bpm - median_bpm)
        
        # Penalize large jumps
        if deviation > 20:
            return 0.5
        elif deviation > 15:
            return 0.75
        elif deviation > 10:
            return 0.9
        else:
            return 1.0


if __name__ == "__main__":
    print("=" * 70)
    print("BPM Estimation Module - Test")
    print("=" * 70)
    print("✅ BPMEstimator class loaded successfully")
    print("\nMethods:")
    print("  1. FFT with parabolic interpolation")
    print("  2. Autocorrelation for periodicity")
    print("  3. Peak detection with IBI analysis")
    print("\nFeatures:")
    print("  • Multi-method fusion with confidence weighting")
    print("  • Adaptive bandpass filtering based on history")
    print("  • Temporal consistency checking")
    print("  • Harmonic validation for FFT")
    print("\nUsage Example:")
    print("  estimator = BPMEstimator(fps=30)")
    print("  bpm, confidence = estimator.estimate(pulse_signal)")
