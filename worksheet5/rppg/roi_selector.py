"""
ROI Selection Module
Implements adaptive ROI selection based on quality metrics.
"""

import cv2
import numpy as np


class AdaptiveROISelector:
    """
    Adaptive ROI selector yang memilih ROI terbaik berdasarkan quality metrics.
    """
    
    def __init__(self):
        """Initialize adaptive ROI selector."""
        pass
    
    def assess_roi_quality(self, roi):
        """
        Assess quality dari ROI berdasarkan multiple metrics.
        
        Args:
            roi: ROI image (BGR format)
            
        Returns:
            Quality score (0-1)
        """
        if roi is None or roi.size == 0:
            return 0.0
        
        # Get mask
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        mask = gray_roi > 0
        
        if np.sum(mask) < 10:  # Terlalu kecil
            return 0.0
        
        # 1. Exposure quality (brightness)
        brightness = np.mean(gray_roi[mask])
        if brightness < 50 or brightness > 200:
            exposure_score = 0.3
        else:
            # Optimal range: 80-180
            exposure_score = 1.0 - abs(brightness - 130) / 130.0
            exposure_score = max(0, min(1, exposure_score))
        
        # 2. Saturation (color richness)
        b, g, r = cv2.split(roi)
        saturation = np.std(r[mask]) + np.std(g[mask]) + np.std(b[mask])
        saturation_score = min(saturation / 100.0, 1.0)
        
        # 3. Green channel prominence (important for blood volume changes)
        green_mean = np.mean(g[mask])
        red_mean = np.mean(r[mask])
        blue_mean = np.mean(b[mask])
        
        # Green should be prominent
        green_prominence = green_mean / (red_mean + blue_mean + 1e-8)
        green_score = min(green_prominence / 2.0, 1.0)
        
        # Combined quality score
        quality = (exposure_score * 0.4 + saturation_score * 0.3 + green_score * 0.3)
        
        return quality
    
    def select_best_roi(self, forehead_roi, left_cheek_roi, right_cheek_roi):
        """
        Select best ROI dari available options.
        
        Args:
            forehead_roi, left_cheek_roi, right_cheek_roi: ROI images
            
        Returns:
            Tuple of (best_roi, quality_score)
        """
        rois = [
            ('forehead', forehead_roi),
            ('left_cheek', left_cheek_roi),
            ('right_cheek', right_cheek_roi)
        ]
        
        best_roi = None
        best_quality = 0.0
        best_name = None
        
        for name, roi in rois:
            if roi is not None:
                quality = self.assess_roi_quality(roi)
                if quality > best_quality:
                    best_quality = quality
                    best_roi = roi
                    best_name = name
        
        return best_roi, best_quality


if __name__ == "__main__":
    print("✅ AdaptiveROISelector module loaded")
    print("\nUsage:")
    print("  selector = AdaptiveROISelector()")
    print("  best_roi, quality = selector.select_best_roi(forehead, left_cheek, right_cheek)")
    print("  quality_score = selector.assess_roi_quality(roi)")
