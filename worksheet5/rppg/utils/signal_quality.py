"""
Signal Quality Module - SQI (Signal Quality Index) Computation

Assesses the quality of extracted rPPG signals using multiple metrics:
  - SNR (Signal-to-Noise Ratio)
  - Kurtosis (peakedness for periodicity)
  - Variance (signal strength)

High-quality signals lead to more accurate BPM estimates. Low-quality signals
should be rejected early to prevent unreliable measurements.

Author: Muhammad Yusuf
Version: 2.1
Date: November 2025
"""

import numpy as np
from scipy.stats import kurtosis
from typing import Dict


class SignalQuality:
    """
    Signal quality assessment for rPPG signals.
    
    Computes multiple quality metrics and combines them into a unified
    Signal Quality Index (SQI) score between 0 and 1.
    """
    
    @staticmethod
    def compute_sqi(
        signal: np.ndarray,
        detailed: bool = False
    ) -> float | Dict[str, float]:
        """
        Compute Signal Quality Index.
        
        Combines multiple quality metrics into a single score:
          - SNR: Signal power vs noise power
          - Kurtosis: Distribution peakedness (periodic signals have low kurtosis)
          - Variance: Signal strength indicator
        
        Args:
            signal: Input pulse signal
            detailed: If True, return dict with individual metrics
            
        Returns:
            SQI score 0-1 (or dict if detailed=True)
        """
        if signal is None or len(signal) < 10:
            return 0.0 if not detailed else {
                'sqi': 0.0, 'snr': 0.0, 'kurtosis': 0.0, 'variance': 0.0
            }
        
        # 1. SNR (Signal-to-Noise Ratio)
        snr_score = SignalQuality._compute_snr_score(signal)
        
        # 2. Kurtosis score
        kurt_score = SignalQuality._compute_kurtosis_score(signal)
        
        # 3. Variance score
        var_score = SignalQuality._compute_variance_score(signal)
        
        # Weighted combination (SNR is most important)
        weights = [0.5, 0.25, 0.25]
        scores = [snr_score, kurt_score, var_score]
        sqi = np.average(scores, weights=weights)
        
        # Apply boost for low-light compensation
        sqi = min(sqi * 1.2, 1.0)
        
        if detailed:
            return {
                'sqi': sqi,
                'snr': snr_score,
                'kurtosis': kurt_score,
                'variance': var_score
            }
        
        return sqi
    
    @staticmethod
    def _compute_snr_score(signal: np.ndarray) -> float:
        """
        Compute SNR-based quality score.
        
        Estimates noise from high-frequency components (first derivative)
        and compares to signal power.
        
        Args:
            signal: Input signal
            
        Returns:
            SNR score 0-1
        """
        signal_power = np.var(signal)
        
        # Noise estimate from high-frequency components
        noise_estimate = np.var(np.diff(signal)) / 2.0
        
        snr = signal_power / (noise_estimate + 1e-10)
        
        # Normalize (threshold at 10)
        snr_score = min(snr / 10.0, 1.0)
        
        return snr_score
    
    @staticmethod
    def _compute_kurtosis_score(signal: np.ndarray) -> float:
        """
        Compute kurtosis-based quality score.
        
        Periodic signals have kurtosis close to 0 (normal distribution).
        High absolute kurtosis indicates non-periodic artifacts.
        
        Args:
            signal: Input signal
            
        Returns:
            Kurtosis score 0-1
        """
        kurt = kurtosis(signal)
        
        # Ideal kurtosis for periodic signal is close to 0
        # Use exponential decay for penalty
        kurt_score = np.exp(-abs(kurt) / 8.0)
        
        return kurt_score
    
    @staticmethod
    def _compute_variance_score(signal: np.ndarray) -> float:
        """
        Compute variance-based quality score.
        
        Higher variance indicates stronger signal (up to a threshold).
        
        Args:
            signal: Input signal
            
        Returns:
            Variance score 0-1
        """
        variance = np.var(signal)
        
        # Normalize (threshold at 300)
        var_score = min(variance / 300.0, 1.0)
        
        return var_score
    
    @staticmethod
    def assess_motion(signal: np.ndarray, previous: np.ndarray = None) -> bool:
        """
        Detect motion artifacts in signal.
        
        Compares current signal chunk with previous chunk. Large differences
        indicate motion.
        
        Args:
            signal: Current signal chunk
            previous: Previous signal chunk (if available)
            
        Returns:
            True if motion detected, False otherwise
        """
        if previous is None or len(previous) != len(signal):
            return False
        
        # Compute correlation between chunks
        corr = np.corrcoef(signal, previous)[0, 1]
        
        # Low correlation indicates motion
        motion_detected = corr < 0.7
        
        return motion_detected


if __name__ == "__main__":
    print("=" * 70)
    print("Signal Quality Module - Test")
    print("=" * 70)
    print("✅ SignalQuality class loaded successfully")
    print("\nMetrics:")
    print("  • SNR: Signal-to-Noise Ratio (weight: 0.5)")
    print("  • Kurtosis: Periodicity indicator (weight: 0.25)")
    print("  • Variance: Signal strength (weight: 0.25)")
    print("\nUsage Example:")
    print("  sqi = SignalQuality.compute_sqi(signal)")
    print("  details = SignalQuality.compute_sqi(signal, detailed=True)")
    print("  motion = SignalQuality.assess_motion(signal, previous)")
