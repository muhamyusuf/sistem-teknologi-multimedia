"""
Signal Processing Module for rPPG
Implements POS (Plane-Orthogonal-to-Skin) method with advanced quality metrics.
"""

import numpy as np
import cv2
from scipy import signal, interpolate
from scipy.stats import kurtosis
from collections import deque


class SignalProcessor:
    """
    Basic signal processor dengan POS method.
    """
    
    def __init__(self, fps=30, window_size=10):
        """
        Initialize signal processor.
        
        Args:
            fps: Frame rate kamera (default 30)
            window_size: Window size dalam detik (default 10)
        """
        self.fps = fps
        self.window_size = window_size
        self.buffer_size = fps * window_size
        
        # Signal buffers - Multi ROI support
        self.red_buffer = deque(maxlen=self.buffer_size)
        self.green_buffer = deque(maxlen=self.buffer_size)
        self.blue_buffer = deque(maxlen=self.buffer_size)
        
        # Quality tracking untuk adaptive processing
        self.quality_buffer = deque(maxlen=100)
        self.bpm_history = deque(maxlen=30)  # Track untuk consistency
    
    def extract_signal(self, roi):
        """
        Extract RGB signal dari ROI.
        
        Args:
            roi: ROI image (BGR format)
            
        Returns:
            numpy array [R, G, B] atau None jika ROI invalid
        """
        if roi is None or roi.size == 0:
            return None
        
        # Get mask dari ROI (non-zero pixels)
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        mask = gray_roi > 0
        
        if np.sum(mask) == 0:
            return None
        
        # Extract mean RGB values dari ROI
        b, g, r = cv2.split(roi)
        
        r_mean = np.mean(r[mask]) if np.sum(mask) > 0 else 0
        g_mean = np.mean(g[mask]) if np.sum(mask) > 0 else 0
        b_mean = np.mean(b[mask]) if np.sum(mask) > 0 else 0
        
        return np.array([r_mean, g_mean, b_mean])
    
    def add_values(self, r, g, b):
        """
        Add RGB values ke buffer.
        
        Args:
            r, g, b: RGB values (bisa berupa nan untuk missing frames)
        """
        self.red_buffer.append(r)
        self.green_buffer.append(g)
        self.blue_buffer.append(b)
    
    def pos_method(self):
        """
        Plane-Orthogonal-to-Skin (POS) method untuk extract pulse signal.
        
        Returns:
            Pulse signal atau None jika buffer belum cukup
        """
        if len(self.red_buffer) < self.fps * 3:  # Minimal 3 detik
            return None
        
        # Convert buffers ke arrays
        red = np.array(list(self.red_buffer))
        green = np.array(list(self.green_buffer))
        blue = np.array(list(self.blue_buffer))
        
        # Handle NaN values dengan interpolation
        red = self._interpolate_nans(red)
        green = self._interpolate_nans(green)
        blue = self._interpolate_nans(blue)
        
        # Normalisasi signals
        red_norm = (red - np.mean(red)) / (np.std(red) + 1e-8)
        green_norm = (green - np.mean(green)) / (np.std(green) + 1e-8)
        blue_norm = (blue - np.mean(blue)) / (np.std(blue) + 1e-8)
        
        # POS algorithm
        X = np.vstack([red_norm, green_norm, blue_norm])
        
        # Projection matrix
        C = np.array([[0, 1, -1], [-2, 1, 1]])
        
        # Project signals
        S = np.dot(C, X)
        
        # Pulse signal dengan weighted combination
        alpha = np.std(S[0, :]) / (np.std(S[1, :]) + 1e-8)
        h = S[0, :] + alpha * S[1, :]
        
        # Advanced detrending: polynomial + linear
        # Remove polynomial trend (menghilangkan drift)
        z = np.polyfit(np.arange(len(h)), h, 2)
        p = np.poly1d(z)
        h = h - p(np.arange(len(h)))
        
        # Additional linear detrend
        h = signal.detrend(h, type='linear')
        
        # Temporal smoothing dengan moving average (reduce noise)
        kernel_size = max(3, int(self.fps / 10))  # ~0.1 detik
        if kernel_size % 2 == 0:
            kernel_size += 1
        h = signal.medfilt(h, kernel_size=kernel_size)
        
        return h
    
    def _interpolate_nans(self, signal_array):
        """
        Interpolate NaN values dalam signal.
        """
        nans = np.isnan(signal_array)
        if not np.any(nans):
            return signal_array
        
        x = np.arange(len(signal_array))
        signal_array[nans] = np.interp(x[nans], x[~nans], signal_array[~nans])
        
        return signal_array
    
    def estimate_bpm(self, pulse_signal):
        """
        Estimate BPM dari pulse signal menggunakan FFT.
        
        Args:
            pulse_signal: Pulse signal dari pos_method()
            
        Returns:
            BPM value atau None
        """
        if pulse_signal is None or len(pulse_signal) < self.fps:
            return None
        
        # Bandpass filter (0.67 - 4.0 Hz => 40 - 240 BPM)
        nyquist = self.fps / 2.0
        low = 0.67 / nyquist
        high = 4.0 / nyquist
        
        b, a = signal.butter(3, [low, high], btype='band')
        filtered = signal.filtfilt(b, a, pulse_signal)
        
        # FFT
        fft_result = np.fft.rfft(filtered)
        fft_freqs = np.fft.rfftfreq(len(filtered), 1.0 / self.fps)
        
        # Find peak frequency
        valid_indices = np.where((fft_freqs >= 0.67) & (fft_freqs <= 4.0))
        fft_magnitudes = np.abs(fft_result[valid_indices])
        fft_freqs_valid = fft_freqs[valid_indices]
        
        if len(fft_magnitudes) == 0:
            return None
        
        peak_idx = np.argmax(fft_magnitudes)
        peak_freq = fft_freqs_valid[peak_idx]
        
        # Convert ke BPM
        bpm = peak_freq * 60.0
        
        return bpm


class AdvancedSignalProcessor(SignalProcessor):
    """
    Advanced signal processor dengan quality metrics dan robust peak detection.
    """
    
    def __init__(self, fps=30, window_size=10):
        super().__init__(fps, window_size)
        
        # Motion detection
        self.motion_detected = False
        self.previous_signal_chunk = None
    
    def estimate_bpm_with_confidence(self, pulse_signal):
        """
        Estimate BPM dengan confidence dan SQI menggunakan multi-method fusion.
        
        Returns:
            Tuple of (bpm, confidence, sqi)
        """
        if pulse_signal is None or len(pulse_signal) < self.fps * 3:
            return None, 0.0, 0.0
        
        # Compute SQI first untuk quality gating
        sqi = self.compute_sqi(pulse_signal)
        
        # Quality gating - reject low quality signals early (relaxed untuk real conditions)
        if sqi < 0.08:  # Threshold untuk minimum acceptable quality
            return None, 0.0, sqi
        
        # Adaptive bandpass filter berdasarkan expected BPM range
        nyquist = self.fps / 2.0
        
        # Jika ada history, use adaptive range
        if len(self.bpm_history) > 5:
            avg_bpm = np.median(list(self.bpm_history))
            low_bpm = max(40, avg_bpm - 20)
            high_bpm = min(200, avg_bpm + 20)
        else:
            low_bpm = 45  # Lebih narrow untuk lebih akurat
            high_bpm = 150
        
        low = (low_bpm / 60.0) / nyquist
        high = (high_bpm / 60.0) / nyquist
        
        # Higher order Butterworth untuk better frequency selectivity
        b, a = signal.butter(4, [low, high], btype='band')
        filtered = signal.filtfilt(b, a, pulse_signal)
        
        # Multi-method BPM estimation
        bpm_fft, conf_fft = self._estimate_bpm_fft(filtered)
        bpm_peak, conf_peak = self.robust_peak_detection(filtered)
        bpm_autocorr, conf_autocorr = self._estimate_bpm_autocorrelation(filtered)
        
        # Weighted voting based on method confidence
        bpm_estimates = []
        weights = []
        
        if bpm_fft is not None and conf_fft > 0.15:
            bpm_estimates.append(bpm_fft)
            weights.append(conf_fft * 1.5)  # FFT paling reliable
        
        if bpm_peak is not None and conf_peak > 0.15:
            bpm_estimates.append(bpm_peak)
            weights.append(conf_peak * 1.0)
        
        if bpm_autocorr is not None and conf_autocorr > 0.15:
            bpm_estimates.append(bpm_autocorr)
            weights.append(conf_autocorr * 0.8)
        
        if len(bpm_estimates) == 0:
            return None, 0.0, sqi
        
        # Weighted average
        weights = np.array(weights)
        weights = weights / np.sum(weights)
        bpm = np.average(bpm_estimates, weights=weights)
        
        # Consistency check dengan history (relaxed untuk early stage)
        consistency_score = 1.0
        if len(self.bpm_history) > 5:
            recent_median = np.median(list(self.bpm_history)[-5:])
            deviation = abs(bpm - recent_median)
            
            # Penalize large jumps (lebih permissive)
            if deviation > 20:
                consistency_score = 0.5
            elif deviation > 15:
                consistency_score = 0.75
            elif deviation > 10:
                consistency_score = 0.9
        
        # Final confidence calculation (balanced formula)
        base_confidence = np.mean(weights)  # Average of method confidences
        
        # Motion detection penalty
        self.detect_motion(filtered)
        motion_penalty = 0.7 if self.motion_detected else 1.0
        
        # Combine all factors dengan boosting untuk kompensasi low SQI
        # Formula: sqrt(base * sqi) untuk lebih gentle scaling
        confidence = np.sqrt(base_confidence * sqi) * consistency_score * motion_penalty
        confidence = min(confidence * 1.3, 1.0)  # Boost 30% untuk kompensasi
        
        # Update history untuk next iteration (lebih permissive)
        if confidence > 0.2:  # Lower threshold untuk track more data
            self.bpm_history.append(bpm)
        
        return bpm, confidence, sqi
    
    def _estimate_bpm_fft(self, filtered_signal):
        """
        Estimate BPM menggunakan FFT dengan peak refinement.
        
        Returns:
            Tuple of (bpm, confidence)
        """
        if len(filtered_signal) < self.fps * 3:
            return None, 0.0
        
        # FFT
        fft_result = np.fft.rfft(filtered_signal)
        fft_freqs = np.fft.rfftfreq(len(filtered_signal), 1.0 / self.fps)
        fft_magnitudes = np.abs(fft_result)
        
        # Valid frequency range (0.75 - 2.5 Hz => 45 - 150 BPM)
        valid_mask = (fft_freqs >= 0.75) & (fft_freqs <= 2.5)
        valid_mags = fft_magnitudes[valid_mask]
        valid_freqs = fft_freqs[valid_mask]
        
        if len(valid_mags) == 0:
            return None, 0.0
        
        # Find primary peak
        peak_idx = np.argmax(valid_mags)
        peak_freq = valid_freqs[peak_idx]
        peak_mag = valid_mags[peak_idx]
        
        # Parabolic interpolation untuk sub-bin resolution
        if peak_idx > 0 and peak_idx < len(valid_mags) - 1:
            alpha = valid_mags[peak_idx - 1]
            beta = valid_mags[peak_idx]
            gamma = valid_mags[peak_idx + 1]
            
            # Parabolic peak refinement
            p = 0.5 * (alpha - gamma) / (alpha - 2*beta + gamma)
            peak_freq_refined = valid_freqs[peak_idx] + p * (valid_freqs[1] - valid_freqs[0])
            peak_freq = peak_freq_refined
        
        bpm = peak_freq * 60.0
        
        # Confidence dari SNR di frequency domain
        noise_floor = np.median(valid_mags)
        snr = peak_mag / (noise_floor + 1e-8)
        confidence = min(snr / 12.0, 1.0)  # More generous threshold
        
        # Check for harmonic consistency
        # Look for 2nd harmonic
        harmonic_freq = peak_freq * 2
        harmonic_mask = (valid_freqs >= harmonic_freq - 0.1) & (valid_freqs <= harmonic_freq + 0.1)
        if np.any(harmonic_mask):
            harmonic_mag = np.max(valid_mags[harmonic_mask])
            if harmonic_mag > noise_floor * 2:
                confidence *= 1.2  # Boost confidence jika harmonic detected
        
        confidence = min(confidence, 1.0)
        
        return bpm, confidence
    
    def _estimate_bpm_autocorrelation(self, filtered_signal):
        """
        Estimate BPM menggunakan autocorrelation untuk periodicitas.
        
        Returns:
            Tuple of (bpm, confidence)
        """
        if len(filtered_signal) < self.fps * 3:
            return None, 0.0
        
        # Normalize signal
        normalized = (filtered_signal - np.mean(filtered_signal)) / (np.std(filtered_signal) + 1e-8)
        
        # Compute autocorrelation
        autocorr = np.correlate(normalized, normalized, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Expected lag range (0.4 - 1.33 sec => 45 - 150 BPM)
        min_lag = int(0.4 * self.fps)
        max_lag = int(1.33 * self.fps)
        
        if max_lag >= len(autocorr):
            return None, 0.0
        
        # Find peak dalam valid range
        valid_autocorr = autocorr[min_lag:max_lag]
        peak_idx = np.argmax(valid_autocorr)
        peak_lag = min_lag + peak_idx
        
        # BPM dari peak lag
        period_seconds = peak_lag / self.fps
        bpm = 60.0 / period_seconds
        
        # Confidence dari autocorrelation peak height
        peak_value = valid_autocorr[peak_idx]
        confidence = min(peak_value / autocorr[0], 1.0)  # Normalize by zero-lag
        confidence = max(confidence - 0.3, 0.0) / 0.7  # Rescale
        
        return bpm, confidence
    
    def compute_sqi(self, pulse_signal):
        """
        Compute Signal Quality Index dengan multiple quality metrics.
        
        Returns:
            SQI value between 0 and 1
        """
        if pulse_signal is None or len(pulse_signal) < 10:
            return 0.0
        
        # 1. SNR (Signal-to-Noise Ratio) - most important
        signal_power = np.var(pulse_signal)
        
        # Noise estimate dari high-frequency components
        noise_estimate = np.var(np.diff(pulse_signal)) / 2.0
        snr = signal_power / (noise_estimate + 1e-8)
        snr_score = min(snr / 10.0, 1.0)  # Relaxed threshold
        
        # 2. Kurtosis (peakedness - should be periodic)
        kurt = kurtosis(pulse_signal)
        kurt_score = np.exp(-abs(kurt) / 8.0)  # More tolerant
        
        # 3. Signal variance (should be significant)
        variance_score = min(signal_power / 300.0, 1.0)  # Lower threshold
        
        # Combined SQI - simplified, weighted toward SNR
        weights = [0.5, 0.25, 0.25]  # SNR dominan
        scores = [snr_score, kurt_score, variance_score]
        sqi = np.average(scores, weights=weights)
        
        # Boost SQI untuk kompensasi low light conditions
        sqi = min(sqi * 1.2, 1.0)
        
        return sqi
    
    def robust_peak_detection(self, filtered_signal):
        """
        Robust peak detection dengan multi-criteria dan harmonic analysis.
        
        Returns:
            Tuple of (bpm, confidence)
        """
        # FFT method
        fft_result = np.fft.rfft(filtered_signal)
        fft_freqs = np.fft.rfftfreq(len(filtered_signal), 1.0 / self.fps)
        fft_magnitudes = np.abs(fft_result)
        
        # Valid range (40-180 BPM)
        valid_indices = np.where((fft_freqs >= 0.67) & (fft_freqs <= 3.0))
        fft_mags_valid = fft_magnitudes[valid_indices]
        fft_freqs_valid = fft_freqs[valid_indices]
        
        if len(fft_mags_valid) == 0:
            return None, 0.0
        
        # Find peaks dengan prominence
        peaks, properties = signal.find_peaks(
            fft_mags_valid,
            prominence=np.max(fft_mags_valid) * 0.2,
            width=1
        )
        
        if len(peaks) == 0:
            # Fallback ke simple peak
            peak_idx = np.argmax(fft_mags_valid)
            peak_freq = fft_freqs_valid[peak_idx]
            bpm = peak_freq * 60.0
            
            # Low confidence karena tidak ada prominent peak
            confidence = 0.3
        else:
            # Ambil peak tertinggi
            highest_peak_idx = peaks[np.argmax(properties['prominences'])]
            peak_freq = fft_freqs_valid[highest_peak_idx]
            bpm = peak_freq * 60.0
            
            # Confidence based on prominence
            prominence = properties['prominences'][np.argmax(properties['prominences'])]
            max_magnitude = np.max(fft_mags_valid)
            confidence = min(prominence / max_magnitude, 1.0)
        
        return bpm, confidence
    
    def detect_motion(self, filtered_signal):
        """
        Detect motion artifacts dengan comparing signal chunks.
        """
        chunk_size = self.fps * 2  # 2 detik
        
        if len(filtered_signal) < chunk_size * 2:
            self.motion_detected = False
            return
        
        # Recent chunk
        recent_chunk = filtered_signal[-chunk_size:]
        
        # Older chunk
        older_chunk = filtered_signal[-chunk_size*2:-chunk_size]
        
        # Compare variance
        recent_var = np.var(recent_chunk)
        older_var = np.var(older_chunk)
        
        # Motion detected jika variance difference besar
        variance_ratio = abs(recent_var - older_var) / (older_var + 1e-8)
        
        self.motion_detected = variance_ratio > 2.0


# Import cv2 untuk extract_signal
import cv2

if __name__ == "__main__":
    print("✅ SignalProcessor modules loaded")
    print("\nBasic usage:")
    print("  processor = SignalProcessor(fps=30)")
    print("  signal = processor.extract_signal(roi)")
    print("  processor.add_values(r, g, b)")
    print("  pulse = processor.pos_method()")
    print("  bpm = processor.estimate_bpm(pulse)")
    print("\nAdvanced usage:")
    print("  adv_processor = AdvancedSignalProcessor(fps=30)")
    print("  bpm, conf, sqi = adv_processor.estimate_bpm_with_confidence(pulse)")
