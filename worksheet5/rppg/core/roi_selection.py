"""
ROI Selection Module - Adaptive Region of Interest Selection

This module assesses the quality of multiple ROI regions and selects the best
one(s) for rPPG signal extraction. Quality is determined by:
  - Exposure: Proper brightness range (not under/overexposed)
  - Saturation: Color intensity (indicates good skin tone capture)
  - Green prominence: Green channel strength (PPG signal carrier)

Multi-ROI fusion with weighted averaging provides more robust signal extraction
compared to single-ROI methods.

Author: Muhammad Yusuf
Version: 2.1
Date: November 2025
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List


class ROISelector:
    """
    Adaptive ROI selector based on quality metrics.
    
    Evaluates multiple facial regions and selects the best one(s) for PPG signal
    extraction. Can operate in single-ROI mode (best only) or multi-ROI mode
    (weighted fusion).
    
    Attributes:
        weight_exposure: Weight for exposure quality (default 0.4)
        weight_saturation: Weight for saturation quality (default 0.3)
        weight_green: Weight for green channel prominence (default 0.3)
    """
    
    def __init__(
        self,
        weight_exposure: float = 0.4,
        weight_saturation: float = 0.3,
        weight_green: float = 0.3
    ):
        """
        Initialize ROI selector with quality metric weights.
        
        Args:
            weight_exposure: Weight for exposure assessment (0-1)
            weight_saturation: Weight for saturation assessment (0-1)
            weight_green: Weight for green prominence (0-1)
        
        Note: Weights should sum to 1.0 for normalized quality scores
        """
        self.weight_exposure = weight_exposure
        self.weight_saturation = weight_saturation
        self.weight_green = weight_green
        
        # Quality thresholds
        self.exposure_min = 0.2
        self.exposure_max = 0.8
        self.saturation_min = 0.1
        self.green_ratio_min = 0.35
    
    def assess_roi_quality(self, roi: np.ndarray) -> float:
        """
        Assess quality of a single ROI region.
        
        Combines three quality metrics:
          1. Exposure: How well-lit the region is
          2. Saturation: Color intensity
          3. Green prominence: Relative green channel strength
        
        Args:
            roi: ROI image in BGR format
            
        Returns:
            Quality score between 0.0 (poor) and 1.0 (excellent)
        """
        if roi is None or roi.size == 0:
            return 0.0
        
        # Extract non-zero pixels (actual ROI region)
        mask = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) > 0
        if not np.any(mask):
            return 0.0
        
        # Convert to float for calculations
        roi_float = roi.astype(np.float32) / 255.0
        
        # 1. Exposure quality (optimal range: 0.2 - 0.8)
        mean_intensity = np.mean(roi_float[mask])
        
        if mean_intensity < self.exposure_min:
            # Underexposed
            exposure_quality = mean_intensity / self.exposure_min
        elif mean_intensity > self.exposure_max:
            # Overexposed
            exposure_quality = (1.0 - mean_intensity) / (1.0 - self.exposure_max)
        else:
            # Optimal range
            exposure_quality = 1.0
        
        # 2. Saturation quality (higher is better, up to a point)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1][mask].astype(np.float32) / 255.0
        mean_saturation = np.mean(saturation)
        
        if mean_saturation < self.saturation_min:
            saturation_quality = mean_saturation / self.saturation_min
        else:
            saturation_quality = min(mean_saturation * 2.0, 1.0)
        
        # 3. Green channel prominence (green is PPG signal carrier)
        b, g, r = cv2.split(roi_float)
        
        green_pixels = g[mask]
        total_intensity = np.mean(roi_float[mask])
        
        if total_intensity > 0:
            green_ratio = np.mean(green_pixels) / total_intensity
        else:
            green_ratio = 0.0
        
        if green_ratio < self.green_ratio_min:
            green_quality = green_ratio / self.green_ratio_min
        else:
            green_quality = 1.0
        
        # Weighted combination
        total_quality = (
            self.weight_exposure * exposure_quality +
            self.weight_saturation * saturation_quality +
            self.weight_green * green_quality
        )
        
        return total_quality
    
    def select_best_roi(
        self, 
        forehead: Optional[np.ndarray],
        left_cheek: Optional[np.ndarray],
        right_cheek: Optional[np.ndarray]
    ) -> Tuple[Optional[np.ndarray], float]:
        """
        Select the best single ROI from multiple options.
        
        Evaluates all provided ROIs and returns the one with highest quality.
        
        Args:
            forehead: Forehead ROI image
            left_cheek: Left cheek ROI image
            right_cheek: Right cheek ROI image
            
        Returns:
            Tuple of (best_roi, quality_score)
        """
        best_roi = None
        best_quality = 0.0
        
        # Evaluate each ROI
        for roi in [forehead, left_cheek, right_cheek]:
            if roi is not None:
                quality = self.assess_roi_quality(roi)
                if quality > best_quality:
                    best_quality = quality
                    best_roi = roi
        
        return best_roi, best_quality
    
    def get_multi_roi_weights(
        self,
        forehead: Optional[np.ndarray],
        left_cheek: Optional[np.ndarray],
        right_cheek: Optional[np.ndarray]
    ) -> Tuple[List[np.ndarray], List[float]]:
        """
        Get weighted ROIs for multi-ROI fusion.
        
        Assesses quality of all ROIs and returns them with normalized weights
        for signal fusion.
        
        Args:
            forehead: Forehead ROI image
            left_cheek: Left cheek ROI image
            right_cheek: Right cheek ROI image
            
        Returns:
            Tuple of (rois, weights) where weights sum to 1.0
        """
        rois = []
        qualities = []
        
        # Collect valid ROIs and their qualities
        for roi in [forehead, left_cheek, right_cheek]:
            if roi is not None:
                quality = self.assess_roi_quality(roi)
                if quality > 0.1:  # Minimum quality threshold
                    rois.append(roi)
                    qualities.append(quality)
        
        # Normalize weights
        if len(qualities) == 0:
            return [], []
        
        total_quality = sum(qualities)
        weights = [q / total_quality for q in qualities]
        
        return rois, weights


if __name__ == "__main__":
    print("=" * 70)
    print("ROI Selection Module - Test")
    print("=" * 70)
    print("✅ ROISelector class loaded successfully")
    print("\nFeatures:")
    print("  • Multi-metric quality assessment")
    print("  • Adaptive ROI selection")
    print("  • Multi-ROI fusion support")
    print("\nQuality Metrics:")
    print("  • Exposure: Optimal lighting (0.2-0.8 intensity)")
    print("  • Saturation: Color intensity")
    print("  • Green prominence: PPG signal carrier strength")
    print("\nUsage Example:")
    print("  selector = ROISelector()")
    print("  quality = selector.assess_roi_quality(roi)")
    print("  best_roi, score = selector.select_best_roi(forehead, left, right)")
    print("  rois, weights = selector.get_multi_roi_weights(forehead, left, right)")
