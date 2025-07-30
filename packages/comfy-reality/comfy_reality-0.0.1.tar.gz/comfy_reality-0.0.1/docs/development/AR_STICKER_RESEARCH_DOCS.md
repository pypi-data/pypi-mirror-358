# AR Sticker Factory: Research & Enhancement Guide

## Executive Summary

This document provides comprehensive research on AR sticker formats, Y-axis coordinate system issues, and TensorRT performance optimization for the ComfyUI AR Sticker Factory project.

## 🎯 Key Findings

### AR Sticker Format Research

**USDZ Coordinate System Standards:**
- Both glTF and USDZ use **+Y world up**, **+Z world front**, **right-hand coordinate system**
- **Meter-based scale** is the standard for AR applications
- Apple's AR Quick Look requires specific orientation for proper display

**Current Implementation Issues:**
- UV coordinates are flipped for AR compatibility: `[(0, 1), (1, 1), (1, 0), (0, 0)]`
- Billboard mode uses Y-axis for height, fixed mode uses Z-axis
- The correct implementation is in `cyberpunk_flipped_face_order.usdz`

### TensorRT Performance Optimization

**ComfyUI TensorRT Integration:**
- **2-3x speedup** on NVIDIA RTX GPUs for Stable Diffusion inference
- Supports SD 1.5, SD 2.1, SDXL, SDXL Turbo, SD3, SVD, and SVD XT
- Official implementation available at: https://github.com/comfyanonymous/ComfyUI_TensorRT
- Can be installed via comfy-cli or direct git clone

## 🔧 Implementation Plan

### Phase 1: TensorRT Integration

1. **Install TensorRT Custom Node**
   ```bash
   cd custom_nodes
   git clone https://github.com/comfyanonymous/ComfyUI_TensorRT.git
   ```

2. **Update AR Sticker Generator Node**
   - Integrate TensorRT loader for SDXL models
   - Add performance monitoring
   - Maintain backward compatibility

### Phase 2: Y-Axis Coordinate System Fix

**Problem Analysis:**
Current USDZ export has Y-axis orientation issues causing AR stickers to display incorrectly.

**Solution:**
- Standardize on +Y world up coordinate system
- Fix UV coordinate mapping
- Ensure proper orientation for AR Quick Look

## 📋 Technical Specifications

### Current USDZ Implementation Analysis

**File:** [`custom_nodes/ar_sticker_factory/utils/usdz_creation.py`](file:///Users/gerred/dev/hackathon/custom_nodes/ar_sticker_factory/utils/usdz_creation.py)

**Key Issues Identified:**
1. **Billboard Mode Geometry** (Lines 75-84):
   ```python
   # Current - may cause orientation issues
   points = [
       (-scale, -scale * aspect_ratio, 0),
       (scale, -scale * aspect_ratio, 0),
       (scale, scale * aspect_ratio, 0),
       (-scale, scale * aspect_ratio, 0),
   ]
   ```

2. **UV Coordinate Flipping** (Line 105):
   ```python
   # Flipped for AR compatibility - verify this is correct
   texCoords = [(0, 1), (1, 1), (1, 0), (0, 0)]
   ```

### Recommended Y-Axis Fixes

**Billboard Mode Enhancement:**
```python
# Ensure proper Y-up orientation for AR
if ar_behavior == "billboard":
    # Y-up, Z-forward (correct for AR Quick Look)
    points = [
        (-scale, 0, -scale * aspect_ratio),  # Bottom-left
        (scale, 0, -scale * aspect_ratio),   # Bottom-right  
        (scale, 0, scale * aspect_ratio),    # Top-right
        (-scale, 0, scale * aspect_ratio),   # Top-left
    ]
    # Normal pointing toward camera (+Y)
    normals = [(0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0)]
```

**Fixed Mode Enhancement:**
```python
else:
    # Fixed orientation - maintain Y-up standard
    points = [
        (-scale, -scale * aspect_ratio, 0),
        (scale, -scale * aspect_ratio, 0),
        (scale, scale * aspect_ratio, 0),
        (-scale, scale * aspect_ratio, 0),
    ]
    # Normal pointing toward viewer (+Z)
    normals = [(0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1)]
```

## 🚀 TensorRT Integration Details

### Performance Benefits
- **SDXL Generation**: 2-3x faster inference on RTX GPUs
- **Memory Optimization**: Reduced VRAM usage through engine optimization
- **Batch Processing**: Improved throughput for multiple sticker generation

### Integration Steps

1. **Add TensorRT Loader to AR Sticker Generator:**
   ```python
   # In ar_sticker_generator.py
   def load_tensorrt_model(self):
       """Load TensorRT optimized SDXL model"""
       try:
           from custom_nodes.ComfyUI_TensorRT import TensorRTLoader
           self.tensorrt_loader = TensorRTLoader()
           return True
       except ImportError:
           print("TensorRT not available, using standard models")
           return False
   ```

2. **Update Generation Pipeline:**
   ```python
   def generate_sticker(self, prompt, **kwargs):
       # Try TensorRT first, fallback to standard
       if hasattr(self, 'tensorrt_loader'):
           return self._generate_with_tensorrt(prompt, **kwargs)
       else:
           return self._generate_standard(prompt, **kwargs)
   ```

### TensorRT Requirements
- NVIDIA RTX GPU (20 series or newer)
- CUDA 11.8+ or 12.x
- TensorRT 8.6+
- Sufficient VRAM (8GB+ recommended for SDXL)

## 🔍 Validation & Testing

### Y-Axis Orientation Test
1. Generate test sticker with known orientation markers
2. Export to USDZ with both old and new coordinate systems
3. Test in AR Quick Look on iOS device
4. Verify correct orientation matches `cyberpunk_flipped_face_order.usdz`

### TensorRT Performance Test
1. Benchmark current SDXL generation times
2. Install and configure TensorRT nodes
3. Run identical generation tasks
4. Measure speedup and quality retention

## 📝 Implementation Checklist

### TensorRT Integration
- [x] Clone ComfyUI_TensorRT repository
- [ ] Install TensorRT dependencies
- [ ] Integrate TensorRT loader into AR Sticker Generator
- [ ] Add performance monitoring
- [ ] Test with sample workflows
- [ ] Document performance improvements

### Y-Axis Coordinate Fix
- [ ] Analyze `cyberpunk_flipped_face_order.usdz` structure
- [ ] Update billboard mode geometry calculations
- [ ] Fix UV coordinate mapping if needed
- [ ] Test AR Quick Look compatibility
- [ ] Validate with iOS AR testing
- [ ] Update documentation

### Quality Assurance
- [ ] Unit tests for coordinate transformations
- [ ] Integration tests with TensorRT
- [ ] Performance benchmarks
- [ ] AR compatibility testing
- [ ] Documentation updates

## 🎨 Expected Outcomes

### Performance Improvements
- **2-3x faster** SDXL sticker generation
- **Reduced inference time** from ~15s to ~5s per sticker
- **Better GPU utilization** through TensorRT optimization

### AR Compatibility
- **Correct orientation** in AR Quick Look
- **Proper scaling** in AR environment
- **Consistent behavior** across iOS devices

### Developer Experience
- **Simplified workflow** with optimized nodes
- **Better error handling** and fallbacks
- **Comprehensive documentation** for troubleshooting

## 🔗 References

- [USDZ Format Documentation](https://developer.apple.com/forums/thread/104042)
- [3D Coordinate System Standards](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/full-version/sec02_CoordinateSystemAndScaleUnit/CoordinateSystemAndScaleUnit.md)
- [ComfyUI TensorRT Performance](https://github.com/comfyanonymous/ComfyUI_TensorRT)
- [AR Quick Look Guidelines](https://www.netguru.com/blog/ar-quick-look-and-usdz)

---

*This document serves as the technical foundation for enhancing the AR Sticker Factory with TensorRT optimization and proper Y-axis coordinate handling.*
