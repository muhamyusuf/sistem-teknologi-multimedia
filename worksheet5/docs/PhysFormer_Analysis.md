# PhysFormer: Technical Analysis for rPPG Implementation
## Facial Video-Based Physiological Measurement With Temporal Difference Transformer (CVPR 2022)

> **Note**: This analysis is based on the PhysFormer paper by Zitong Yu et al. (CVPR 2022). The paper introduces a transformer-based architecture for remote photoplethysmography (rPPG) heart rate measurement from facial videos.

---

## 1. CORE INNOVATION: PhysFormer Architecture

### 1.1 Main Contribution
PhysFormer is an **end-to-end pure transformer architecture** that captures **long-range spatio-temporal dependencies** in facial videos for rPPG signal extraction. Unlike traditional methods (POS, CHROM) and CNN-based approaches, it:

- **Avoids hand-crafted ROI selection** - learns relevant facial regions automatically
- **Models long-range temporal dependencies** - considers relationships across entire video sequences, not just adjacent frames
- **Uses temporal difference features** - explicitly models subtle color changes over time

### 1.2 Key Improvements Over Traditional Methods

| Method Type | Limitation | PhysFormer Solution |
|------------|------------|---------------------|
| **POS/CHROM** | Fixed ROI (forehead, cheeks), manual color space selection | Learnable attention to any facial region |
| **CNN-based** | Limited receptive field, local features only | Global spatio-temporal attention |
| **Previous transformers** | Standard ViT lacks temporal modeling | Temporal Difference Multi-Head Self-Attention |

---

## 2. TEMPORAL DIFFERENCE TRANSFORMER

### 2.1 Architecture Overview

```
Input Video (T×H×W×3)
    ↓
[Stem] - Initial feature extraction
    ↓
[Tube Tokenizer] - Spatio-temporal patches
    ↓
[TD-Transformer Blocks] × N
    ├── Temporal Difference Multi-Head Self-Attention (TD-MHSA)
    ├── Spatio-Temporal Feed-Forward (ST-FF)
    └── Layer Normalization
    ↓
[rPPG Predictor Head]
    ↓
Output: rPPG Signal
```

### 2.2 Key Components

#### **A. Stem (Shallow Feature Extractor)**
- **Purpose**: Initial spatial feature extraction before tokenization
- **Architecture**: 2-3 convolutional layers
- **Why it matters**: Helps the transformer "see better" by providing better initial features
- **Ablation result**: Removing stem increased RMSE by +3.06 bpm

#### **B. Tube Tokenizer**
- **Concept**: Divides video into 3D spatio-temporal "tubes"
- **Tube size**: 4×4×4 (spatial × spatial × temporal)
- **Why "tubes"**: Same spatial region across consecutive frames
- **Benefit**: Captures local temporal dynamics before global attention

**Implementation Detail**:
```python
# Pseudo-code for tube tokenization
def tube_tokenize(video):
    # video: [T, H, W, C]
    T, H, W, C = video.shape
    
    # Spatial patches
    patch_h, patch_w = 4, 4
    # Temporal depth
    patch_t = 4
    
    # Extract tubes
    tubes = extract_patches_3d(video, 
                               patch_size=(patch_t, patch_h, patch_w))
    
    # Flatten each tube to tokens
    tokens = rearrange(tubes, 'n t h w c -> n (t h w c)')
    
    return tokens
```

#### **C. Temporal Difference Multi-Head Self-Attention (TD-MHSA)**

This is the **core innovation** of PhysFormer.

**Standard Self-Attention** (from vanilla transformer):
```
Q, K, V = Linear(X), Linear(X), Linear(X)
Attention = softmax(Q·K^T / √d) · V
```

**Temporal Difference Self-Attention**:
```
ΔX = X[t] - X[t-1]  # Temporal difference
Q, K, V = Linear(ΔX), Linear(ΔX), Linear(ΔX)
Attention = softmax(Q·K^T / √d) · V
```

**Why TD-MHSA is Better**:

1. **Emphasizes subtle color changes**: rPPG signals are based on tiny color variations (blood volume changes)
2. **Removes static background**: Only motion/change is attended to
3. **Quasi-periodic pattern enhancement**: Heartbeat has periodic color changes
4. **Robustness to illumination**: Difference features are less affected by lighting

**Temperature-scaled Attention**:
```
Attention = softmax(Q·K^T / (τ·√d)) · V
```
- Lower temperature τ → sparser attention (better for periodic signals)
- Ablation shows τ=0.1 works best for rPPG

#### **D. Spatio-Temporal Feed-Forward (ST-FF)**

Unlike standard FFN, ST-FF has **separable convolutions** to model:
- **Spatial correlations**: Between different facial regions
- **Temporal correlations**: Across time steps

```python
# Standard FFN
x = Linear(x)
x = GELU(x)
x = Linear(x)

# ST-FF (improved)
x = DepthwiseConv3D(x)  # Spatial-temporal local modeling
x = GELU(x)
x = PointwiseConv(x)    # Channel mixing
```

---

## 3. TECHNICAL IMPLEMENTATION DETAILS

### 3.1 Input Preprocessing

**Video Preprocessing Pipeline**:
1. **Face Detection**: Detect face bounding box in each frame
2. **Face Alignment**: Align faces to canonical position (optional but improves performance)
3. **Cropping**: Crop face region (typical size: 128×128 or 256×256)
4. **Normalization**: 
   - Mean subtraction: `(frame - mean) / std`
   - Temporal normalization across video
5. **Clip Extraction**: Extract T-frame clips (T=160 frames ≈ 10 seconds at 16fps)

**Key Insight**: PhysFormer does NOT require:
- Skin segmentation
- Pre-defined ROI masks
- Color space conversion (works in RGB)

### 3.2 ROI Selection Strategy

**Traditional Methods**:
- Fixed ROI: forehead, left cheek, right cheek
- Manual skin segmentation
- Hand-crafted features

**PhysFormer Approach**:
- **Learnable attention** to any facial region
- Attention maps show it focuses on:
  - Forehead (highest blood volume)
  - Cheeks
  - Nose (sometimes)
  - **Avoids**: eyes, mouth (high motion areas)

**Visualization Finding**:
- Attention is **sparse** (only a few tokens highly attended)
- Attention is **consistent** across time for periodic signals
- Different heads attend to **different spatial regions** (complementary)

### 3.3 Signal Extraction Technique

**Output Head**:
```
Tokens → Average Pooling → Linear Projection → rPPG Signal (T-dimensional)
```

**Signal Post-processing**:
1. **Detrending**: Remove low-frequency drift
   ```python
   from scipy import signal
   rppg_detrended = signal.detrend(rppg_signal)
   ```

2. **Bandpass Filtering**: 0.7-4 Hz (42-240 bpm)
   ```python
   from scipy.signal import butter, filtfilt
   
   def bandpass_filter(signal, lowcut=0.7, highcut=4.0, fs=30, order=5):
       nyq = 0.5 * fs
       low = lowcut / nyq
       high = highcut / nyq
       b, a = butter(order, [low, high], btype='band')
       return filtfilt(b, a, signal)
   ```

3. **HR Estimation**: FFT to find dominant frequency
   ```python
   fft_signal = np.fft.fft(rppg_filtered)
   freqs = np.fft.fftfreq(len(rppg_filtered), 1/fps)
   
   # Find peak in valid HR range
   valid_idx = np.where((freqs >= 0.7) & (freqs <= 4.0))
   peak_freq = freqs[valid_idx][np.argmax(np.abs(fft_signal[valid_idx]))]
   hr_bpm = peak_freq * 60
   ```

### 3.4 Temporal Modeling Approach

**Multi-scale Temporal Modeling**:
- **Short-term**: Tube tokenizer captures 4-frame local changes
- **Medium-term**: TD-MHSA within each block (~16 frames)
- **Long-term**: Stacked TD-Transformers (up to 160 frames)

**Temporal Hierarchy**:
```
Layer 1: Captures heartbeat peaks/valleys (0.5-1 sec)
Layer 2: Captures heartbeat cycles (1-2 sec)
Layer 3: Captures HR variability (5-10 sec)
```

### 3.5 Loss Functions

PhysFormer uses **dynamic curriculum learning** with multiple losses:

#### **A. Temporal Loss (Mean Squared Error)**
```python
L_time = MSE(predicted_rppg, ground_truth_rppg)
```
- Direct signal reconstruction
- Simple but effective for easy samples

#### **B. Frequency Loss (Cross-Entropy)**
```python
# Convert HR to label distribution (Gaussian)
def hr_to_distribution(hr_value, sigma=1.0):
    hr_range = np.arange(41, 181)  # 41-180 bpm
    p_k = np.exp(-((hr_range - hr_value)**2) / (2 * sigma**2))
    p_k = p_k / np.sum(p_k)  # Normalize
    return p_k

L_CE = CrossEntropy(predicted_distribution, hr_distribution)
```
- Treats HR estimation as classification (140 classes for 41-180 bpm)
- More robust than direct regression

#### **C. Label Distribution Loss (KL Divergence)**
```python
L_LD = KL_Divergence(predicted_dist, gaussian_dist_around_GT)
```
- Soft labels instead of hard labels
- Accounts for HR measurement uncertainty

#### **D. Dynamic Curriculum Loss**
```python
# Start with easy frequency domain, gradually add temporal loss
epoch_ratio = current_epoch / total_epochs

L_total = λ_time * (epoch_ratio) * L_time + 
          λ_CE * L_CE + 
          λ_LD * (1 - epoch_ratio) * L_LD
```

**Curriculum Strategy**:
- **Early training**: Focus on frequency domain (easier, more robust)
- **Late training**: Add temporal domain (harder, more precise)
- **Rationale**: Frequency-domain supervision is easier because HR has narrow valid range (40-180 bpm)

---

## 4. PERFORMANCE METRICS

### 4.1 Datasets Used

| Dataset | Videos | Subjects | Scenarios | Resolution |
|---------|--------|----------|-----------|------------|
| **VIPL-HR** | 2,378 | 107 | 9 scenarios (indoor/outdoor) | 960×720 |
| **PURE** | 60 | 10 | Steady, talking, head motion | 640×480 |
| **UBFC-rPPG** | 42 | 42 | Sitting, frontal face | 640×480 |
| **MAHNOB-HCI** | 527 | 27 | Emotion elicitation | 780×580 |

### 4.2 Performance Results

**VIPL-HR (Intra-dataset, most challenging)**:

| Method | RMSE (bpm) | MAE (bpm) | r |
|--------|-----------|----------|---|
| POS (traditional) | 17.02 | - | 0.27 |
| CHROM (traditional) | 26.14 | - | 0.13 |
| DeepPhys (CNN) | 13.00 | - | 0.36 |
| RhythmNet (CNN+Attention) | 8.48 | - | - |
| **PhysFormer** | **7.74** | **2.45** | **0.81** |

**Improvement**: ~9% better than previous SOTA

**PURE Dataset**:

| Method | RMSE (bpm) | MAE (bpm) | r |
|--------|-----------|----------|---|
| POS | 2.13 | 1.98 | 0.96 |
| PhysNet (CNN) | 1.04 | 0.76 | 0.99 |
| **PhysFormer** | **0.79** | **0.58** | **0.99** |

**Cross-dataset (Trained on VIPL-HR, tested on MMSE-HR)**:

| Method | RMSE (bpm) | r |
|--------|-----------|---|
| DeepPhys | 11.37 | 0.71 |
| ST-Attention | 7.21 | 0.86 |
| **PhysFormer** | **5.36** | **0.92** |

**Key Finding**: Strong generalization ability!

### 4.3 Robustness Analysis

**Motion Robustness**:
- Handles head movements better than CNN methods
- Long-range attention helps track face across frames

**Lighting Robustness**:
- Temporal difference features reduce illumination effects
- Performs well in both indoor and outdoor scenarios

**Skin Tone Robustness**:
- Tested across different subjects
- No explicit skin tone detection needed

---

## 5. PRACTICAL IMPROVEMENTS FOR REAL-WORLD IMPLEMENTATION

### 5.1 Lightweight Improvements (WITHOUT Deep Learning)

Even if you can't use the full PhysFormer, you can apply these concepts to traditional methods:

#### **A. Temporal Differencing**
```python
# Instead of using raw frames
# Use temporal differences
def compute_temporal_diff(video_clip):
    """
    video_clip: [T, H, W, 3] numpy array
    """
    diff_clip = np.zeros_like(video_clip[:-1])
    for t in range(len(video_clip) - 1):
        diff_clip[t] = video_clip[t+1] - video_clip[t]
    
    return diff_clip

# Then apply POS or CHROM on diff_clip
```

**Why this helps**:
- Removes static background
- Emphasizes color changes (which is what rPPG is!)
- Reduces illumination effects

#### **B. Multi-scale Temporal Aggregation**
```python
def multiscale_rppg(video, roi_mask):
    """
    Extract rPPG at multiple temporal scales and combine
    """
    # Short-term (2-3 seconds)
    short_rppg = extract_rppg(video[:60], roi_mask)  # 2 sec @ 30fps
    
    # Medium-term (5-6 seconds)
    mid_rppg = extract_rppg(video[:150], roi_mask)   # 5 sec
    
    # Long-term (10 seconds)
    long_rppg = extract_rppg(video, roi_mask)        # 10 sec
    
    # Weighted combination
    combined = 0.3*short_rppg + 0.3*mid_rppg + 0.4*long_rppg
    
    return combined
```

#### **C. Adaptive ROI Selection**
```python
def adaptive_roi(face_landmarks):
    """
    Instead of fixed ROI, use facial landmarks to define regions
    """
    # Get forehead (most reliable for rPPG)
    forehead = get_forehead_region(face_landmarks)
    
    # Get cheeks
    left_cheek = get_left_cheek_region(face_landmarks)
    right_cheek = get_right_cheek_region(face_landmarks)
    
    # Combine with weights (learned from attention maps)
    roi_mask = 0.5*forehead + 0.25*left_cheek + 0.25*right_cheek
    
    return roi_mask
```

### 5.2 Enhancing Traditional Methods (POS)

**Original POS**:
```python
def pos_method(video, roi_mask):
    # Spatial averaging in ROI
    C = np.mean(video * roi_mask, axis=(1,2))  # [T, 3]
    
    # Normalized RGB
    Cn = C / np.mean(C, axis=0)
    
    # Projection
    X_s = 3*Cn[:,0] - 2*Cn[:,1]
    Y_s = 1.5*Cn[:,0] + Cn[:,1] - 1.5*Cn[:,2]
    
    # Pulse signal
    S = X_s - (std(X_s)/std(Y_s)) * Y_s
    
    return S
```

**Enhanced POS (with PhysFormer insights)**:
```python
def enhanced_pos(video, roi_mask, use_temporal_diff=True):
    """
    Enhanced POS with temporal differencing and denoising
    """
    # 1. Temporal differencing (PhysFormer idea)
    if use_temporal_diff:
        video_processed = np.diff(video, axis=0)
    else:
        video_processed = video
    
    # 2. Spatial averaging in ROI
    C = np.mean(video_processed * roi_mask, axis=(1,2))
    
    # 3. Detrending (remove slow drifts)
    from scipy import signal
    C_detrended = signal.detrend(C, axis=0)
    
    # 4. Normalized RGB
    C_mean = np.mean(C_detrended, axis=0, keepdims=True)
    Cn = C_detrended / (C_mean + 1e-6)
    
    # 5. POS projection
    X_s = 3*Cn[:,0] - 2*Cn[:,1]
    Y_s = 1.5*Cn[:,0] + Cn[:,1] - 1.5*Cn[:,2]
    
    # 6. Adaptive std ratio (more robust)
    std_ratio = np.std(X_s) / (np.std(Y_s) + 1e-6)
    std_ratio = np.clip(std_ratio, 0.5, 2.0)  # Prevent extreme values
    
    S = X_s - std_ratio * Y_s
    
    # 7. Bandpass filtering
    S_filtered = bandpass_filter(S, lowcut=0.7, highcut=4.0, fs=30)
    
    return S_filtered
```

### 5.3 Post-processing Tricks

#### **A. Kalman Filtering for HR Tracking**
```python
from filterpy.kalman import KalmanFilter

class HRKalmanTracker:
    def __init__(self, initial_hr=70):
        self.kf = KalmanFilter(dim_x=2, dim_z=1)
        
        # State: [HR, HR_velocity]
        self.kf.x = np.array([initial_hr, 0.0])
        
        # State transition (constant velocity model)
        self.kf.F = np.array([[1.0, 1.0],
                              [0.0, 1.0]])
        
        # Measurement function
        self.kf.H = np.array([[1.0, 0.0]])
        
        # Covariances
        self.kf.R = 2.0  # Measurement noise
        self.kf.Q = np.array([[0.1, 0.0],
                              [0.0, 0.1]])  # Process noise
        
    def update(self, measured_hr):
        self.kf.predict()
        self.kf.update(measured_hr)
        return self.kf.x[0]  # Smoothed HR

# Usage
tracker = HRKalmanTracker(initial_hr=70)
smoothed_hrs = []
for raw_hr in raw_hr_estimates:
    smoothed_hr = tracker.update(raw_hr)
    smoothed_hrs.append(smoothed_hr)
```

#### **B. Peak Detection for Quality Assessment**
```python
from scipy.signal import find_peaks

def quality_assessment(rppg_signal):
    """
    Assess signal quality based on peak characteristics
    """
    # Find peaks
    peaks, properties = find_peaks(rppg_signal, 
                                   height=np.std(rppg_signal)*0.5,
                                   distance=15)  # Minimum 15 frames between peaks
    
    # Quality metrics
    peak_heights = properties['peak_heights']
    
    # 1. SNR (signal-to-noise ratio)
    signal_power = np.mean(peak_heights**2)
    noise_power = np.var(rppg_signal)
    snr = 10 * np.log10(signal_power / (noise_power + 1e-6))
    
    # 2. Peak regularity (should be quasi-periodic)
    peak_intervals = np.diff(peaks)
    regularity = 1.0 / (np.std(peak_intervals) + 1e-6)
    
    # 3. Overall quality score
    quality = (snr > 5.0) and (regularity > 0.1)
    
    return quality, snr, regularity
```

#### **C. Outlier Rejection**
```python
def outlier_rejection(hr_estimates, window_size=5):
    """
    Reject outlier HR estimates using moving median
    """
    cleaned_hrs = []
    
    for i, hr in enumerate(hr_estimates):
        # Get window
        start = max(0, i - window_size//2)
        end = min(len(hr_estimates), i + window_size//2 + 1)
        window = hr_estimates[start:end]
        
        # Compute median and MAD (median absolute deviation)
        median_hr = np.median(window)
        mad = np.median(np.abs(window - median_hr))
        
        # Reject if too far from median
        if abs(hr - median_hr) > 3 * mad:
            cleaned_hrs.append(median_hr)  # Replace with median
        else:
            cleaned_hrs.append(hr)
    
    return np.array(cleaned_hrs)
```

---

## 6. KEY TAKEAWAYS FOR PRACTICAL rPPG SYSTEM

### Top 5 Insights from PhysFormer

#### **1. Temporal Difference is Crucial**
- **What**: Use frame-to-frame differences instead of raw frames
- **Why**: Emphasizes subtle color changes, removes static background
- **How to implement**: `diff = frame[t] - frame[t-1]`
- **Impact**: Can improve traditional methods by 10-15% without any deep learning

#### **2. Long-range Temporal Context Matters**
- **What**: Consider relationships across entire video (10+ seconds), not just adjacent frames
- **Why**: Heartbeat has periodic patterns over multiple cycles
- **How to implement (without transformers)**:
  - Use longer temporal windows (10-15 seconds)
  - Multi-scale temporal pooling
  - Temporal smoothing with Kalman filter

#### **3. Frequency-domain Supervision is More Robust**
- **What**: Optimize for correct HR in frequency domain, not just signal reconstruction
- **Why**: HR has limited valid range (40-180 bpm), easier to constrain
- **How to implement**:
  - Add FFT loss during training
  - Use bandpass filtering aggressively
  - Cross-entropy loss over HR bins

#### **4. Adaptive Attention to Facial Regions**
- **What**: Don't use fixed ROI; let the model/algorithm find best regions
- **Why**: Different people have different optimal ROI (due to skin tone, facial hair, etc.)
- **How to implement (without deep learning)**:
  - Test multiple ROI configurations
  - Weight ROIs based on signal quality
  - Exclude high-motion areas (mouth during talking)

#### **5. Multi-task Learning Helps**
- **What**: Train for HR, HRV, respiratory rate simultaneously
- **Why**: Shared features improve generalization
- **How to implement**: Extract multiple signals from same rPPG:
  - HR: 0.7-4 Hz
  - Respiration: 0.1-0.5 Hz
  - HRV: Time-domain and frequency-domain features

### Trade-offs

| Aspect | Accuracy | Computational Cost | Real-time Capability |
|--------|----------|-------------------|---------------------|
| **PhysFormer (full)** | ⭐⭐⭐⭐⭐ | 🔥🔥🔥🔥 | ❌ (needs GPU) |
| **Enhanced POS** | ⭐⭐⭐⭐ | 🔥 | ✅ (CPU real-time) |
| **Traditional POS** | ⭐⭐⭐ | 🔥 | ✅ |

### Suggestions for Real-time Implementation

#### **For CPU-only (embedded devices)**:
1. Use **Enhanced POS** with temporal differencing
2. Implement **Kalman filtering** for smoothing
3. Use **simple peak detection** for quality assessment
4. **Framerate**: 15-20 FPS is sufficient (downsampling from 30 FPS)
5. **Resolution**: 64×64 face crop is enough for ROI averaging

#### **For GPU-available (desktop/cloud)**:
1. Use **lightweight CNN** (e.g., PhysNet, EfficientPhys)
2. Implement **sliding window** inference
3. **Batch processing** for multiple faces
4. Consider **model quantization** for speed

#### **Hybrid Approach** (Recommended):
```python
def hybrid_rppg_system(video, face_detector):
    """
    Combines traditional and learning-based methods
    """
    # 1. Quick POS estimate (always runs)
    pos_signal, quality = enhanced_pos_with_quality(video)
    
    # 2. If quality is poor, fallback to learning-based
    if quality < QUALITY_THRESHOLD:
        cnn_signal = run_physnet(video)
        return cnn_signal
    else:
        return pos_signal
```

---

## 7. IMPLEMENTATION ROADMAP

### Phase 1: Improve Current POS Implementation
- [ ] Add temporal differencing
- [ ] Implement better detrending
- [ ] Add Kalman filter for HR tracking
- [ ] Implement quality assessment
- [ ] Add outlier rejection

### Phase 2: Multi-scale Processing
- [ ] Extract rPPG at multiple temporal scales
- [ ] Weighted combination of scales
- [ ] Adaptive ROI based on face landmarks

### Phase 3: Advanced Post-processing
- [ ] FFT-based HR estimation with peak refinement
- [ ] HRV feature extraction
- [ ] Respiratory rate estimation

### Phase 4: (Optional) Learning-based Enhancement
- [ ] Collect/download public rPPG dataset
- [ ] Train lightweight CNN (PhysNet)
- [ ] Implement PhysFormer-lite (fewer layers)
- [ ] Ensemble traditional + learned methods

---

## 8. REFERENCES & RESOURCES

### Papers to Read
1. **PhysFormer** (Yu et al., CVPR 2022) - Main paper
2. **POS** (Wang et al., IEEE TBE 2017) - Traditional baseline
3. **CHROM** (De Haan & Jeanne, IEEE TBE 2013) - Another baseline
4. **PhysNet** (Yu et al., BMVC 2019) - Strong CNN baseline
5. **Attention Mechanisms for rPPG** (various)

### Datasets
- **PURE**: Small, clean, good for testing
- **UBFC-rPPG**: Medium-sized, realistic
- **VIPL-HR**: Large-scale, diverse scenarios
- **MMSE-HR**: Cross-dataset evaluation

### Code Resources
- PhysFormer official code: (Check GitHub)
- rPPG-Toolbox: Comprehensive implementation of many methods
- PyVHR: Python library for video-based heart rate estimation

---

## CONCLUSION

PhysFormer demonstrates that **long-range spatio-temporal modeling** with **temporal difference features** significantly improves rPPG measurement. Even without implementing the full transformer architecture, you can apply these insights to enhance traditional methods like POS.

**Key takeaway**: Focus on **temporal differencing**, **multi-scale processing**, and **frequency-domain optimization** for maximum impact with minimal computational cost.
