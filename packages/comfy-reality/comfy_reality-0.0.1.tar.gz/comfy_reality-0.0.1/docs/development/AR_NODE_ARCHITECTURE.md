# AR Node Architecture Design

This document outlines the new AR-focused nodes designed to complement the existing ComfyUI ecosystem for professional AR/3D content creation.

## 🎯 Design Philosophy

- **Composable**: Each node performs a specific AR/3D function that integrates with others
- **Mobile-First**: All nodes prioritize mobile AR performance optimization
- **Professional**: Enterprise-ready capabilities for AR development workflows
- **Cross-Platform**: Support for multiple AR platforms (iOS, Android, Web, Unity, Unreal)

## 🏗️ Node Architecture Overview

### Core AR Production Pipeline

```
[Image Generation] → [AR Optimizer] → [Material Composer] → [Spatial Positioner] 
                                                                      ↓
[Physics Integrator] ← [Animation Builder] ← [Reality Composer] ← [Here]
                                                                      ↓
                                                      [Cross-Platform Exporter]
```

## 📋 New Node Specifications

### 1. **AROptimizer** - Mobile Performance Optimization
- **Purpose**: Optimize 3D assets for mobile AR performance
- **Key Features**:
  - Texture compression (ASTC, ETC2, PVRTC, DXT)
  - LOD level generation (1-5 levels)
  - Polygon reduction with quality control
  - Memory budget management (10-500MB)
  - Platform-specific optimization (iOS/Android/Universal)

**INPUT_TYPES**:
- `image` (IMAGE) - Source texture
- `target_platform` (CHOICE) - iOS, Android, Universal
- `optimization_level` (CHOICE) - Aggressive, Balanced, Conservative
- `max_texture_size` (CHOICE) - 256, 512, 1024, 2048
- `compression_format` (CHOICE) - Auto, ASTC, ETC2, PVRTC, DXT

**RETURN_TYPES**: (IMAGE, GEOMETRY, OPTIMIZATION_REPORT)

### 2. **SpatialPositioner** - 3D Positioning & Scale
- **Purpose**: Precise 3D positioning, rotation, and scaling for AR objects
- **Key Features**:
  - World-space coordinate positioning
  - Multiple anchor points (center, bottom, top, custom)
  - Relative positioning to other objects
  - Auto ground-snapping
  - Collision bounds generation

**INPUT_TYPES**:
- `position_x/y/z` (FLOAT) - 3D position coordinates
- `rotation_x/y/z` (FLOAT) - Euler angles (-360 to 360)
- `scale` (FLOAT) - Uniform scale factor
- `anchor_point` (CHOICE) - Center, Bottom, Top, Custom
- `coordinate_system` (CHOICE) - World, Local, Camera Relative

**RETURN_TYPES**: (SPATIAL_TRANSFORM, MATRIX4X4, BOUNDS)

### 3. **MaterialComposer** - PBR Material Creation
- **Purpose**: Create physically-based rendering materials from textures
- **Key Features**:
  - Full PBR workflow (Albedo, Normal, Roughness, Metallic, Emission)
  - Material type presets (Standard, Unlit, Subsurface, Emission, Transparent)
  - UV tiling and material properties
  - AR-specific optimizations
  - Mobile compatibility checks

**INPUT_TYPES**:
- `albedo` (IMAGE) - Base color texture
- `material_type` (CHOICE) - Standard, Unlit, Subsurface, Emission, Transparent
- `normal_map` (IMAGE, Optional) - Normal/bump mapping
- `roughness_map` (IMAGE, Optional) - Surface roughness
- `metallic_map` (IMAGE, Optional) - Metallic properties
- Various material factors (roughness_factor, metallic_factor, etc.)

**RETURN_TYPES**: (MATERIAL, MATERIAL_PREVIEW, MATERIAL_PROPERTIES)

### 4. **RealityComposer** - Multi-Object Scene Assembly
- **Purpose**: Compose complete AR scenes with multiple objects and lighting
- **Key Features**:
  - Multi-object scene assembly (up to 3 objects initially)
  - Lighting setup (Auto, Three-point, Ambient, Directional)
  - Environment configuration (Indoor, Outdoor, Studio, Custom)
  - Shadow and ambient lighting control
  - AR anchor type selection

**INPUT_TYPES**:
- `scene_name` (STRING) - Scene identifier
- `environment_type` (CHOICE) - Indoor, Outdoor, Studio, Custom
- `lighting_setup` (CHOICE) - Auto, Three-point, Ambient, Directional, Custom
- `object_1/2/3` (GEOMETRY, Optional) - Scene objects
- `material_1/2/3` (MATERIAL, Optional) - Object materials
- `transform_1/2/3` (SPATIAL_TRANSFORM, Optional) - Object transforms

**RETURN_TYPES**: (AR_SCENE, SCENE_GRAPH, LIGHTING_SETUP, SCENE_BOUNDS)

### 5. **CrossPlatformExporter** - Multi-Format Export
- **Purpose**: Export AR scenes to multiple platform formats
- **Key Features**:
  - Multiple format support (USDZ, glTF, GLB, FBX, OBJ)
  - Platform targeting (iOS, Android, Web, Unity, Unreal)
  - Compression and optimization options
  - Draco geometry compression
  - Export report generation

**INPUT_TYPES**:
- `scene` (AR_SCENE) - Complete AR scene
- `export_formats` (CHOICE) - USDZ, glTF, GLB, FBX, OBJ, All
- `target_platforms` (CHOICE) - iOS, Android, Web, Unity, Unreal, All
- `compression_level` (CHOICE) - None, Low, Medium, High, Maximum
- `draco_compression` (BOOLEAN) - Enable Draco compression

**RETURN_TYPES**: (EXPORT_RESULTS, FILE_PATHS, EXPORT_REPORT)

### 6. **AnimationBuilder** - Keyframe Animation
- **Purpose**: Create simple keyframe animations for AR objects
- **Key Features**:
  - Animation types (Transform, Material, Visibility, Scale Pulse, Rotation)
  - Easing functions (Linear, Ease In/Out, Bounce, Elastic)
  - Loop modes (None, Loop, Ping-pong, Reverse)
  - Trigger types (Auto, Tap, Proximity, Time)
  - Timeline generation

**INPUT_TYPES**:
- `animation_name` (STRING) - Animation identifier
- `animation_type` (CHOICE) - Transform, Material, Visibility, Scale Pulse, Rotation, Custom
- `duration` (FLOAT) - Animation duration in seconds
- `loop_mode` (CHOICE) - None, Loop, Ping-pong, Reverse
- `easing_function` (CHOICE) - Linear, Ease In, Ease Out, Ease In/Out, Bounce, Elastic

**RETURN_TYPES**: (ANIMATION, ANIMATION_TIMELINE, ANIMATION_PROPERTIES)

### 7. **PhysicsIntegrator** - Physics & Collision
- **Purpose**: Add physics properties and collision detection to AR objects
- **Key Features**:
  - Physics body types (Static, Kinematic, Dynamic, Ghost)
  - Collision shapes (Auto, Box, Sphere, Capsule, Cylinder, Mesh, Convex Hull)
  - Material physics (Friction, Restitution, Damping)
  - Collision layers and masks
  - Physics constraints

**INPUT_TYPES**:
- `physics_type` (CHOICE) - Static, Kinematic, Dynamic, Ghost
- `collision_shape` (CHOICE) - Auto, Box, Sphere, Capsule, Cylinder, Mesh, Convex Hull
- `mass` (FLOAT) - Object mass (0-1000kg)
- `friction` (FLOAT) - Surface friction (0-2.0)
- `restitution` (FLOAT) - Bounciness (0-1.0)
- Various physics properties and constraints

**RETURN_TYPES**: (PHYSICS_BODY, COLLISION_SHAPE, PHYSICS_PROPERTIES)

## 🔗 Node Integration Patterns

### Basic AR Sticker Workflow
```
Image → AROptimizer → MaterialComposer → SpatialPositioner → USDZExporter
```

### Complex AR Scene Workflow
```
Multiple Objects → AROptimizer → MaterialComposer → SpatialPositioner
                                                            ↓
AnimationBuilder → PhysicsIntegrator → RealityComposer → CrossPlatformExporter
```

### Performance-Optimized Workflow
```
Assets → AROptimizer (Aggressive) → MaterialComposer (Mobile-optimized) → CrossPlatformExporter (High compression)
```

## 🎯 Key Data Types

### Custom Data Types
- **SPATIAL_TRANSFORM**: 3D positioning and transformation data
- **MATERIAL**: PBR material definition with textures and properties
- **AR_SCENE**: Complete AR scene with objects, lighting, and metadata
- **PHYSICS_BODY**: Physics simulation properties and collision data
- **ANIMATION**: Keyframe animation data with timing and easing
- **GEOMETRY**: 3D mesh data (vertices, faces, normals)
- **BOUNDS**: 3D bounding box information

## 🚀 Performance Characteristics

### Mobile Optimization Features
- **Texture Compression**: Platform-specific formats (ASTC, ETC2, PVRTC)
- **LOD Generation**: Multiple detail levels for distance-based rendering
- **Memory Management**: Budget-aware optimization (10-500MB targets)
- **Polygon Reduction**: Quality-controlled mesh simplification
- **Physics Optimization**: Simple collision shapes for mobile performance

### Cross-Platform Compatibility
- **iOS/ARKit**: USDZ with iOS Quick Look support
- **Android/ARCore**: glTF/GLB with Draco compression
- **WebXR**: Optimized glTF for web browsers
- **Unity/Unreal**: FBX with full feature support

## 🔧 Implementation Status

All nodes are currently implemented with:
- ✅ Complete ComfyUI interface definitions
- ✅ Proper INPUT_TYPES and RETURN_TYPES
- ✅ Placeholder functionality for rapid prototyping
- ⏳ Full implementation planned for production release

## 🎨 UI Integration

### Node Categories
- **🔧 ComfyReality/Optimization**: AROptimizer
- **📐 ComfyReality/Spatial**: SpatialPositioner
- **🎨 ComfyReality/Materials**: MaterialComposer
- **🏗️ ComfyReality/Scene**: RealityComposer
- **🚀 ComfyReality/Export**: CrossPlatformExporter
- **🎬 ComfyReality/Animation**: AnimationBuilder
- **⚛️ ComfyReality/Physics**: PhysicsIntegrator

This architecture provides a comprehensive, professional-grade AR content creation pipeline that seamlessly integrates with the existing ComfyUI ecosystem while focusing on mobile AR performance and cross-platform compatibility.
