"""
Fullscreen Visualizer Module
Modern UI for 1280x720 resolution with comprehensive metrics display.

This module provides a clean, professional interface for real-time rPPG monitoring
with anti-aliased fonts, organized panels, and smooth animations.

Author: Muhammad Yusuf
Version: 2.1
Date: November 2025
"""

import cv2
import numpy as np
import time
from collections import deque


class FullscreenVisualizer:
    """
    Modern fullscreen UI untuk resolusi 1280x720 dengan layout yang user-friendly.
    
    Features:
        - Live camera feed with ROI quality indicator
        - Large, prominent BPM display with confidence meter
        - Real-time metrics panel (signal quality, motion, statistics)
        - Historical graphs (BPM and quality trends)
        - Interactive instructions overlay
        - Smooth anti-aliased fonts
    
    Attributes:
        width (int): Canvas width in pixels
        height (int): Canvas height in pixels
        colors (dict): Color palette for UI elements
        bpm_history (deque): Historical BPM values for graphing
        sqi_history (deque): Historical signal quality values
        confidence_history (deque): Historical confidence values
        show_instructions (bool): Toggle for instructions overlay
    """
    
    def __init__(self, width=1280, height=720):
        """
        Initialize visualizer with specified dimensions.
        
        Args:
            width: Canvas width (default: 1280)
            height: Canvas height (default: 720)
        """
        self.width = width
        self.height = height
        
        # Modern color palette
        self.colors = {
            'bg': (20, 20, 25),           # Dark background
            'panel': (35, 35, 40),        # Panel background
            'accent': (0, 150, 255),      # Orange accent
            'success': (0, 255, 100),     # Green
            'warning': (0, 200, 255),     # Yellow
            'danger': (60, 60, 255),      # Red
            'text': (255, 255, 255),      # White text
            'text_dim': (150, 150, 150),  # Dim text
        }
        
        # Historical data for graphs
        self.bpm_history = deque(maxlen=200)
        self.sqi_history = deque(maxlen=200)
        self.confidence_history = deque(maxlen=200)
        self.timestamp_history = deque(maxlen=200)
        
        # Timing for FPS calculation
        self.start_time = time.time()
        self.last_update_time = time.time()
        self.frame_times = deque(maxlen=30)
        
        # UI state
        self.show_instructions = True
        self.instructions_alpha = 1.0
        
    def create_canvas(self):
        """
        Create blank canvas with background color.
        
        Returns:
            np.ndarray: Blank canvas ready for drawing
        """
        canvas = np.full((self.height, self.width, 3), self.colors['bg'], dtype=np.uint8)
        return canvas
    
    def draw_header(self, canvas, fps_value):
        """
        Draw header bar with branding and system info.
        
        Args:
            canvas: Canvas to draw on
            fps_value: Current FPS to display
            
        Returns:
            np.ndarray: Canvas with header drawn
        """
        header_height = 70
        cv2.rectangle(canvas, (0, 0), (self.width, header_height), self.colors['panel'], -1)
        
        # Title with consistent 30px padding
        cv2.putText(canvas, "rPPG Heart Rate Monitor", (30, 48), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.2, self.colors['accent'], 3, cv2.LINE_AA)
        
        # System info (FPS and time)
        current_time = time.strftime("%H:%M:%S")
        info_text = f"FPS: {fps_value:.1f} | {current_time}"
        cv2.putText(canvas, info_text, (self.width - 320, 48), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.75, self.colors['text_dim'], 2, cv2.LINE_AA)
        
        return canvas
    
    def draw_video_panel(self, canvas, video_frame, roi_quality=None):
        """
        Draw video feed panel with adaptive quality border.
        
        Args:
            canvas: Canvas to draw on
            video_frame: Video frame to display
            roi_quality: ROI quality score (0-1) for border color
            
        Returns:
            np.ndarray: Canvas with video panel drawn
        """
        padding = 30
        panel_x = padding
        panel_y = 90
        panel_w = 600
        panel_h = 450
        
        # Resize and draw video
        if video_frame is not None:
            video_resized = cv2.resize(video_frame, (panel_w, panel_h))
            canvas[panel_y:panel_y+panel_h, panel_x:panel_x+panel_w] = video_resized
            
            # Border color based on ROI quality
            if roi_quality is not None:
                if roi_quality > 0.7:
                    border_color = self.colors['success']
                elif roi_quality > 0.4:
                    border_color = self.colors['warning']
                else:
                    border_color = self.colors['danger']
            else:
                border_color = self.colors['accent']
            
            cv2.rectangle(canvas, (panel_x-3, panel_y-3), 
                         (panel_x+panel_w+3, panel_y+panel_h+3), border_color, 3)
        
        # Label
        cv2.putText(canvas, "LIVE CAMERA", (panel_x, panel_y-8), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['text_dim'], 2, cv2.LINE_AA)
        
        return canvas
    
    def draw_bpm_display(self, canvas, bpm, confidence=None):
        """
        Draw large BPM display with confidence meter and health status.
        
        Args:
            canvas: Canvas to draw on
            bpm: Current BPM value
            confidence: Confidence score (0-1)
            
        Returns:
            np.ndarray: Canvas with BPM display drawn
        """
        gap = 20
        panel_x = 30 + 600 + gap
        panel_y = 90
        panel_w = 600
        panel_h = 200
        
        # Background panel
        cv2.rectangle(canvas, (panel_x, panel_y), 
                     (panel_x+panel_w, panel_y+panel_h), self.colors['panel'], -1)
        cv2.rectangle(canvas, (panel_x, panel_y), 
                     (panel_x+panel_w, panel_y+panel_h), (60, 60, 60), 1)
        
        # Title
        cv2.putText(canvas, "HEART RATE", (panel_x+25, panel_y+30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.75, self.colors['text_dim'], 2, cv2.LINE_AA)
        
        if bpm is not None and confidence is not None:
            # Color and status based on confidence
            if confidence > 0.8:
                bpm_color = self.colors['success']
                status = "EXCELLENT"
            elif confidence > 0.6:
                bpm_color = self.colors['accent']
                status = "GOOD"
            elif confidence > 0.4:
                bpm_color = self.colors['warning']
                status = "FAIR"
            else:
                bpm_color = self.colors['danger']
                status = "MEASURING..."
            
            # Large BPM value
            bpm_text = f"{int(bpm)}"
            cv2.putText(canvas, bpm_text, (panel_x+25, panel_y+90), 
                       cv2.FONT_HERSHEY_DUPLEX, 2.2, bpm_color, 4, cv2.LINE_AA)
            
            # BPM unit
            cv2.putText(canvas, "BPM", (panel_x+190, panel_y+90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, self.colors['text_dim'], 2, cv2.LINE_AA)
            
            # Confidence bar
            bar_x = panel_x + 25
            bar_y = panel_y + 110
            bar_w = 250
            bar_h = 16
            
            # Background
            cv2.rectangle(canvas, (bar_x, bar_y), (bar_x+bar_w, bar_y+bar_h), 
                         (50, 50, 50), -1)
            
            # Fill
            fill_w = int(bar_w * confidence)
            cv2.rectangle(canvas, (bar_x, bar_y), (bar_x+fill_w, bar_y+bar_h), 
                         bpm_color, -1)
            
            # Status text
            conf_text = f"{status} - {int(confidence*100)}%"
            cv2.putText(canvas, conf_text, (bar_x, bar_y+bar_h+22), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.colors['text'], 1, cv2.LINE_AA)
            
            # Health status indicator
            if confidence > 0.7:
                if 60 <= bpm <= 100:
                    health_text = "✓ Normal"
                    health_color = self.colors['success']
                elif 50 <= bpm < 60:
                    health_text = "↓ Below Normal"
                    health_color = self.colors['warning']
                elif 100 < bpm <= 120:
                    health_text = "↑ Above Normal"
                    health_color = self.colors['warning']
                else:
                    health_text = "⚠ Consult Doctor"
                    health_color = self.colors['danger']
                
                cv2.putText(canvas, health_text, (bar_x, bar_y+bar_h+45), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, health_color, 2, cv2.LINE_AA)
        else:
            # Waiting state
            cv2.putText(canvas, "---", (panel_x+25, panel_y+90), 
                       cv2.FONT_HERSHEY_DUPLEX, 2.2, self.colors['text_dim'], 4, cv2.LINE_AA)
            cv2.putText(canvas, "Initializing...", (panel_x+25, panel_y+130), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.colors['text_dim'], 1, cv2.LINE_AA)
        
        return canvas
    
    def draw_metrics_panel(self, canvas, sqi=None, motion_detected=False, avg_bpm=None, bpm_range=None):
        """
        Draw metrics panel with signal quality and statistics.
        
        Args:
            canvas: Canvas to draw on
            sqi: Signal quality index (0-1)
            motion_detected: Whether motion is detected
            avg_bpm: Average BPM over 30 seconds
            bpm_range: BPM standard deviation
            
        Returns:
            np.ndarray: Canvas with metrics panel drawn
        """
        gap = 20
        panel_x = 30 + 600 + gap
        panel_y = 90 + 200 + gap
        panel_w = 600
        panel_h = 160  # Increased from 130 to prevent overlap
        
        # Background
        cv2.rectangle(canvas, (panel_x, panel_y), 
                     (panel_x+panel_w, panel_y+panel_h), self.colors['panel'], -1)
        cv2.rectangle(canvas, (panel_x, panel_y), 
                     (panel_x+panel_w, panel_y+panel_h), (60, 60, 60), 1)
        
        # Title
        cv2.putText(canvas, "METRICS", (panel_x+25, panel_y+25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.colors['text_dim'], 2, cv2.LINE_AA)
        
        # Metrics in 2x2 grid
        metrics = [
            ("Signal Quality", f"{int(sqi*100)}%" if sqi else "---", 
             self.colors['success'] if sqi and sqi > 0.7 else self.colors['warning']),
            ("Motion Status", "STILL" if not motion_detected else "MOVING", 
             self.colors['success'] if not motion_detected else self.colors['danger']),
            ("Avg BPM (30s)", f"{int(avg_bpm)}" if avg_bpm else "---", 
             self.colors['text']),
            ("BPM Range", f"±{int(bpm_range)}" if bpm_range else "---", 
             self.colors['text_dim']),
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            col = i % 2
            row = i // 2
            
            # Proper spacing with increased vertical space
            x = panel_x + 30 + col * 290
            y = panel_y + 50 + row * 70  # Increased from 60 to 70
            
            # Labels and values with anti-aliasing
            cv2.putText(canvas, label, (x, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['text_dim'], 1, cv2.LINE_AA)
            cv2.putText(canvas, value, (x, y+30), 
                       cv2.FONT_HERSHEY_DUPLEX, 1.0, color, 2, cv2.LINE_AA)
        
        return canvas
    
    def draw_graph_panel(self, canvas):
        """
        Draw real-time graphs for BPM and signal quality history.
        
        Args:
            canvas: Canvas to draw on
            
        Returns:
            np.ndarray: Canvas with graph panel drawn
        """
        gap = 20
        panel_x = 30 + 600 + gap
        panel_y = 90 + 200 + gap + 160 + gap  # Updated for new metrics height
        panel_w = 600
        panel_h = 190
        
        # Background
        cv2.rectangle(canvas, (panel_x, panel_y), 
                     (panel_x+panel_w, panel_y+panel_h), self.colors['panel'], -1)
        cv2.rectangle(canvas, (panel_x, panel_y), 
                     (panel_x+panel_w, panel_y+panel_h), (60, 60, 60), 1)
        
        # Title
        cv2.putText(canvas, "REAL-TIME GRAPHS", (panel_x+25, panel_y+25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.colors['text_dim'], 2, cv2.LINE_AA)
        
        # Graph area
        graph_x = panel_x + 25
        graph_y = panel_y + 42
        graph_w = panel_w - 50
        graph_h = 118
        
        # BPM Graph (top half)
        if len(self.bpm_history) > 1:
            self._draw_line_graph(canvas, graph_x, graph_y, graph_w, graph_h//2, 
                                 list(self.bpm_history), "BPM", 
                                 self.colors['accent'], y_min=50, y_max=120)
        
        # SQI Graph (bottom half)
        if len(self.sqi_history) > 1:
            self._draw_line_graph(canvas, graph_x, graph_y + graph_h//2 + 20, 
                                 graph_w, graph_h//2 - 20, 
                                 list(self.sqi_history), "Quality", 
                                 self.colors['success'], y_min=0, y_max=1)
        
        return canvas
    
    def _draw_line_graph(self, canvas, x, y, w, h, data, label, color, y_min=0, y_max=100):
        """
        Helper method to draw line graphs.
        
        Args:
            canvas: Canvas to draw on
            x, y: Top-left position
            w, h: Width and height
            data: List of values to plot
            label: Graph label
            color: Line color (BGR)
            y_min, y_max: Y-axis range
        """
        # Background
        cv2.rectangle(canvas, (x, y), (x+w, y+h), (25, 25, 30), -1)
        
        # Label
        cv2.putText(canvas, label, (x+5, y+15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.colors['text_dim'], 1, cv2.LINE_AA)
        
        # Current value
        if data:
            current_val = data[-1]
            if y_max > 10:  # BPM
                val_text = f"{int(current_val)}"
            else:  # Quality (0-1)
                val_text = f"{current_val:.2f}"
            cv2.putText(canvas, val_text, (x+w-50, y+15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
        
        # Plot data
        if len(data) > 1:
            points = []
            for i, value in enumerate(data):
                # Normalize value to graph height
                norm_value = (value - y_min) / (y_max - y_min) if y_max > y_min else 0
                norm_value = max(0, min(1, norm_value))  # Clamp
                
                px = int(x + (i / len(data)) * w)
                py = int(y + h - norm_value * h)
                points.append([px, py])
            
            # Draw line
            points = np.array(points, dtype=np.int32)
            cv2.polylines(canvas, [points], False, color, 2, cv2.LINE_AA)
    
    def draw_instructions(self, canvas):
        """
        Draw instructions overlay (toggleable with SPACE).
        
        Args:
            canvas: Canvas to draw on
            
        Returns:
            np.ndarray: Canvas with instructions overlay
        """
        # Semi-transparent overlay
        overlay = canvas.copy()
        panel_x = self.width // 2 - 250
        panel_y = self.height // 2 - 200
        panel_w = 500
        panel_h = 400
        
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x+panel_w, panel_y+panel_h), (40, 40, 45), -1)
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x+panel_w, panel_y+panel_h), self.colors['accent'], 2)
        
        # Blend
        cv2.addWeighted(overlay, 0.95, canvas, 0.05, 0, canvas)
        
        # Title
        cv2.putText(canvas, "INSTRUCTIONS", (panel_x+60, panel_y+50), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.0, self.colors['accent'], 2, cv2.LINE_AA)
        
        # Instructions list
        instructions = [
            ("Position", "Face camera directly, well-lit"),
            ("Distance", "30-50cm from camera"),
            ("Stay Still", "Minimize head movement"),
            (None, None),  # Spacer
            ("Wait", "6-10s for initial reading"),
            ("Confidence", "70%+ for accurate results"),
            (None, None),
            ("SPACE", "Toggle this help"),
            ("Q / ESC", "Exit application"),
        ]
        
        y_offset = panel_y + 100
        for title, desc in instructions:
            if title:
                cv2.putText(canvas, title, (panel_x+60, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.colors['text'], 2, cv2.LINE_AA)
                if desc:
                    cv2.putText(canvas, desc, (panel_x+80, y_offset+25), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['text_dim'], 1, cv2.LINE_AA)
                y_offset += 55
            else:
                y_offset += 15
        
        return canvas
    
    def draw_footer(self, canvas):
        """
        Draw footer with keyboard controls.
        
        Args:
            canvas: Canvas to draw on
            
        Returns:
            np.ndarray: Canvas with footer drawn
        """
        footer_height = 35
        y_start = self.height - footer_height
        cv2.rectangle(canvas, (0, y_start), (self.width, self.height), 
                     self.colors['panel'], -1)
        
        # Controls
        controls = "SPACE: Toggle Instructions | Q: Quit | ESC: Exit Fullscreen"
        cv2.putText(canvas, controls, (30, y_start+23), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.colors['text_dim'], 1, cv2.LINE_AA)
        
        return canvas
    
    def update(self, video_frame, bpm=None, confidence=None, sqi=None, 
               motion_detected=False, roi_quality=None):
        """
        Update entire UI with latest data.
        
        Args:
            video_frame: Current camera frame
            bpm: Current BPM estimate
            confidence: Confidence score (0-1)
            sqi: Signal quality index (0-1)
            motion_detected: Motion detection flag
            roi_quality: ROI quality score (0-1)
            
        Returns:
            np.ndarray: Complete rendered canvas
        """
        # Create canvas
        canvas = self.create_canvas()
        
        # Calculate FPS
        current_time = time.time()
        if hasattr(self, 'last_update_time'):
            frame_time = current_time - self.last_update_time
            if frame_time > 0:
                self.frame_times.append(1.0 / frame_time)
        
        self.last_update_time = current_time
        fps_value = np.mean(list(self.frame_times)) if len(self.frame_times) > 0 else 0
        
        # Draw all components
        canvas = self.draw_header(canvas, fps_value)
        canvas = self.draw_video_panel(canvas, video_frame, roi_quality)
        canvas = self.draw_bpm_display(canvas, bpm, confidence)
        
        # Calculate statistics
        avg_bpm = np.mean(list(self.bpm_history)[-30:]) if len(self.bpm_history) >= 10 else None
        bpm_range = np.std(list(self.bpm_history)[-30:]) if len(self.bpm_history) >= 10 else None
        
        canvas = self.draw_metrics_panel(canvas, sqi, motion_detected, avg_bpm, bpm_range)
        canvas = self.draw_graph_panel(canvas)
        canvas = self.draw_footer(canvas)
        
        # Instructions overlay
        if self.show_instructions:
            canvas = self.draw_instructions(canvas)
        
        # Update histories
        if bpm is not None:
            self.bpm_history.append(bpm)
        if sqi is not None:
            self.sqi_history.append(sqi)
        if confidence is not None:
            self.confidence_history.append(confidence)
        
        return canvas


if __name__ == "__main__":
    print("✅ FullscreenVisualizer module loaded")
    print("\nUsage:")
    print("  from ui.visualizer import FullscreenVisualizer")
    print("  visualizer = FullscreenVisualizer()")
    print("  canvas = visualizer.update(frame, bpm, confidence, sqi, motion, quality)")
