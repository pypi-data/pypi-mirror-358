# Distribution & Compatibility Guide

## Overview

This guide covers distributing USDZ content across different platforms, ensuring cross-platform compatibility, and optimizing delivery for web, mobile, and desktop environments. Learn about platform-specific requirements, fallback strategies, and distribution best practices.

## Platform Compatibility Matrix

### iOS Ecosystem

**ARKit Quick Look Support:**
- **iOS 12+**: Basic USDZ viewing and AR placement
- **iOS 13+**: Improved rendering, better performance
- **iOS 14+**: LiDAR support, enhanced occlusion
- **iOS 15+**: Object Capture integration
- **iOS 16+**: AVIF texture support, improved materials

**Device Requirements:**
- **iPhone 6s and later**: Basic AR support
- **iPad (5th generation) and later**: Basic AR support  
- **iPhone 12 Pro/iPad Pro**: LiDAR-enhanced features
- **Apple Vision Pro**: Native 3D viewing (iOS 17+)

```swift
// iOS compatibility check
func checkARCompatibility() -> ARCompatibilityLevel {
    if ARWorldTrackingConfiguration.isSupported {
        if #available(iOS 14.0, *), ARWorldTrackingConfiguration.supportsSceneReconstruction(.mesh) {
            return .lidarEnabled
        }
        return .basicAR
    }
    return .viewerOnly
}

enum ARCompatibilityLevel {
    case viewerOnly    // 3D model viewing only
    case basicAR       // Basic AR placement
    case lidarEnabled  // Advanced AR with occlusion
}
```

### Android Ecosystem

**ARCore Support:**
- **Android 7.0+ (API 24)**: ARCore compatible devices
- **Limited USDZ Support**: No native USDZ viewer
- **Requires Conversion**: USDZ → glTF/GLB for Android

**Alternative Formats:**
```bash
# Convert USDZ to glTF for Android
usdcat input.usdz -o output.gltf

# Or use FBX as intermediate format
usdcat input.usdz -o temp.fbx
# Then convert FBX to glTF using tools like Blender
```

### Web Browsers

**USDZ Support:**
- **Safari (iOS/macOS)**: Native USDZ support
- **Chrome/Firefox**: Limited support, requires AR viewer apps
- **WebXR**: Use glTF format with model-viewer

**Web Implementation:**
```html
<!-- iOS Safari with USDZ -->
<a href="model.usdz" rel="ar">
    <img src="preview.jpg" alt="AR Model">
</a>

<!-- Universal web AR with model-viewer -->
<model-viewer 
    src="model.gltf" 
    ios-src="model.usdz"
    ar 
    auto-rotate 
    camera-controls>
</model-viewer>
```

## Multi-Format Distribution Strategy

### Universal Asset Pipeline

```python
class UniversalARDistributor:
    """Create and distribute AR content across multiple platforms"""
    
    def __init__(self, source_model_path, output_dir):
        self.source_path = source_model_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def create_universal_package(self, base_name):
        """Create packages for all major platforms"""
        
        outputs = {}
        
        # iOS USDZ (primary)
        usdz_path = self.create_usdz_package(base_name)
        outputs['ios'] = usdz_path
        
        # Android glTF
        gltf_path = self.create_gltf_package(base_name)
        outputs['android'] = gltf_path
        
        # Web viewer package
        web_path = self.create_web_package(base_name, usdz_path, gltf_path)
        outputs['web'] = web_path
        
        # Desktop viewers (OBJ/FBX)
        desktop_path = self.create_desktop_package(base_name)
        outputs['desktop'] = desktop_path
        
        return outputs
    
    def create_usdz_package(self, base_name):
        """Create iOS-optimized USDZ package"""
        
        output_path = self.output_dir / f"{base_name}.usdz"
        
        # Use existing USDZ creation pipeline
        # (Implementation from previous guides)
        
        return output_path
    
    def create_gltf_package(self, base_name):
        """Create Android-compatible glTF package"""
        
        import subprocess
        
        gltf_path = self.output_dir / f"{base_name}.gltf"
        
        # Convert via USD tools
        try:
            subprocess.run([
                'usdcat', str(self.source_path), 
                '-o', str(gltf_path)
            ], check=True)
            
            # Optimize for mobile
            self._optimize_gltf_for_mobile(gltf_path)
            
        except subprocess.CalledProcessError:
            print("Direct USD conversion failed, trying alternative method")
            self._convert_via_intermediate_format(gltf_path)
        
        return gltf_path
    
    def create_web_package(self, base_name, usdz_path, gltf_path):
        """Create web viewer package with HTML"""
        
        web_dir = self.output_dir / f"{base_name}_web"
        web_dir.mkdir(exist_ok=True)
        
        # Copy assets
        import shutil
        shutil.copy2(usdz_path, web_dir / f"{base_name}.usdz")
        shutil.copy2(gltf_path, web_dir / f"{base_name}.gltf")
        
        # Create HTML viewer
        html_content = self._generate_web_viewer_html(base_name)
        html_path = web_dir / "index.html"
        html_path.write_text(html_content)
        
        return web_dir
    
    def _optimize_gltf_for_mobile(self, gltf_path):
        """Optimize glTF for mobile performance"""
        
        # Use gltf-pipeline if available
        try:
            import subprocess
            subprocess.run([
                'gltf-pipeline', 
                '-i', str(gltf_path),
                '-o', str(gltf_path),
                '--draco.compressionLevel', '7'
            ], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("gltf-pipeline not available, skipping optimization")
    
    def _generate_web_viewer_html(self, base_name):
        """Generate HTML for universal web viewer"""
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>{base_name} - AR Viewer</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    <style>
        model-viewer {{
            width: 100%;
            height: 400px;
        }}
        .ar-button {{
            background: #007AFF;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            margin: 10px 0;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <h1>{base_name}</h1>
    
    <!-- Universal 3D viewer -->
    <model-viewer 
        src="{base_name}.gltf"
        ios-src="{base_name}.usdz"
        ar
        ar-modes="webxr scene-viewer quick-look"
        auto-rotate
        camera-controls
        shadow-intensity="1"
        alt="3D model of {base_name}">
        
        <button slot="ar-button" class="ar-button">
            View in AR
        </button>
    </model-viewer>
    
    <!-- Platform-specific instructions -->
    <div id="instructions"></div>
    
    <script>
        // Detect platform and show appropriate instructions
        function updateInstructions() {{
            const instructions = document.getElementById('instructions');
            const userAgent = navigator.userAgent;
            
            if (/iPad|iPhone|iPod/.test(userAgent)) {{
                instructions.innerHTML = '<p>Tap "View in AR" to open in AR Quick Look</p>';
            }} else if (/Android/.test(userAgent)) {{
                instructions.innerHTML = '<p>Tap "View in AR" to open in Scene Viewer or ARCore app</p>';
            }} else {{
                instructions.innerHTML = '<p>Use mouse to rotate, scroll to zoom. AR requires mobile device.</p>';
            }}
        }}
        
        updateInstructions();
    </script>
</body>
</html>'''
```

### Format Conversion Tools

```python
class FormatConverter:
    """Utility for converting between different 3D formats"""
    
    @staticmethod
    def usdz_to_gltf(usdz_path, gltf_path):
        """Convert USDZ to glTF"""
        
        import subprocess
        import tempfile
        import zipfile
        
        # Extract USDZ
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(usdz_path, 'r') as zf:
                zf.extractall(temp_dir)
            
            # Find USD file
            usd_files = list(Path(temp_dir).glob("*.usd*"))
            if not usd_files:
                raise ValueError("No USD file found in USDZ package")
            
            usd_file = usd_files[0]
            
            # Convert USD to glTF
            try:
                subprocess.run([
                    'usdcat', str(usd_file),
                    '-o', str(gltf_path)
                ], check=True)
            except subprocess.CalledProcessError:
                # Fallback: convert via intermediate format
                FormatConverter._convert_via_blender(usd_file, gltf_path)
    
    @staticmethod
    def _convert_via_blender(input_path, output_path):
        """Convert via Blender (requires Blender with USD add-on)"""
        
        import subprocess
        
        blender_script = f'''
import bpy
import sys

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import USD
try:
    bpy.ops.wm.usd_import(filepath="{input_path}")
except:
    print("USD import failed")
    sys.exit(1)

# Export glTF
try:
    bpy.ops.export_scene.gltf(
        filepath="{output_path}",
        export_format='GLTF_EMBEDDED',
        export_materials='EXPORT',
        export_images=True
    )
    print("Conversion successful")
except Exception as e:
    print(f"Export failed: {{e}}")
    sys.exit(1)
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(blender_script)
            script_path = f.name
        
        try:
            subprocess.run([
                'blender', '--background', '--python', script_path
            ], check=True, capture_output=True)
        finally:
            os.unlink(script_path)
    
    @staticmethod
    def optimize_for_web(gltf_path, output_path=None):
        """Optimize glTF for web delivery"""
        
        if output_path is None:
            output_path = gltf_path
        
        # Use Draco compression if available
        try:
            import subprocess
            subprocess.run([
                'gltf-pipeline',
                '-i', str(gltf_path),
                '-o', str(output_path),
                '--draco.compressionLevel', '7',
                '--draco.compressMeshes',
                '--draco.quantizePositionBits', '11',
                '--draco.quantizeNormalBits', '8',
                '--draco.quantizeTexcoordBits', '10'
            ], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("gltf-pipeline not available for optimization")
```

## Web Deployment Strategies

### CDN-Optimized Delivery

```python
class WebARDeployment:
    """Optimize USDZ/AR content for web delivery"""
    
    def __init__(self, cdn_base_url=""):
        self.cdn_base_url = cdn_base_url
    
    def generate_responsive_viewer(self, model_name, usdz_url, gltf_url, poster_url):
        """Generate responsive AR viewer with progressive loading"""
        
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{model_name} - AR Viewer</title>
    
    <!-- Preload critical resources -->
    <link rel="preload" href="{poster_url}" as="image">
    <link rel="preload" href="{gltf_url}" as="fetch" crossorigin>
    
    <script type="module" src="https://unpkg.com/@google/model-viewer@3.4.0/dist/model-viewer.min.js"></script>
    
    <style>
        body {{ margin: 0; font-family: system-ui; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        
        model-viewer {{
            width: 100%;
            height: 70vh;
            min-height: 400px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .ar-button {{
            background: linear-gradient(135deg, #007AFF, #5856D6);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 16px 32px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 16px rgba(0,122,255,0.3);
            transition: transform 0.2s;
        }}
        
        .ar-button:hover {{ transform: translateY(-2px); }}
        
        .platform-badge {{
            display: inline-block;
            background: rgba(0,0,0,0.1);
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 12px;
            margin: 8px 4px 0 0;
        }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 10px; }}
            model-viewer {{ height: 50vh; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{model_name}</h1>
        
        <model-viewer 
            src="{gltf_url}"
            ios-src="{usdz_url}"
            poster="{poster_url}"
            ar
            ar-modes="webxr scene-viewer quick-look"
            auto-rotate
            camera-controls
            shadow-intensity="0.7"
            environment-image="neutral"
            loading="lazy"
            reveal="auto"
            alt="3D model of {model_name}">
            
            <button slot="ar-button" class="ar-button">
                📱 View in AR
            </button>
            
            <div slot="progress-bar" style="display: none;"></div>
        </model-viewer>
        
        <div id="platform-info"></div>
        
        <script>
            // Enhanced platform detection and analytics
            const modelViewer = document.querySelector('model-viewer');
            const platformInfo = document.getElementById('platform-info');
            
            // Detect capabilities
            function detectCapabilities() {{
                const caps = [];
                
                if (navigator.xr) caps.push('WebXR');
                if (/iPad|iPhone|iPod/.test(navigator.userAgent)) caps.push('iOS AR Quick Look');
                if (/Android/.test(navigator.userAgent)) caps.push('ARCore Scene Viewer');
                
                return caps;
            }}
            
            // Update platform information
            function updatePlatformInfo() {{
                const capabilities = detectCapabilities();
                
                if (capabilities.length > 0) {{
                    platformInfo.innerHTML = '<h3>AR Capabilities:</h3>' + 
                        capabilities.map(cap => `<span class="platform-badge">${{cap}}</span>`).join('');
                }} else {{
                    platformInfo.innerHTML = '<p>🖥️ Desktop viewing mode - AR requires mobile device</p>';
                }}
            }}
            
            // Analytics and error handling
            modelViewer.addEventListener('load', () => {{
                console.log('Model loaded successfully');
                // Analytics: track model load
            }});
            
            modelViewer.addEventListener('error', (event) => {{
                console.error('Model load error:', event.detail);
                // Analytics: track load errors
            }});
            
            modelViewer.addEventListener('ar-status', (event) => {{
                console.log('AR status:', event.detail.status);
                // Analytics: track AR usage
            }});
            
            // Initialize
            updatePlatformInfo();
            
            // Progressive enhancement for file size
            const connectionType = navigator.connection?.effectiveType;
            if (connectionType === 'slow-2g' || connectionType === '2g') {{
                // Load lower quality model for slow connections
                console.log('Slow connection detected, consider loading lower quality model');
            }}
        </script>
    </div>
</body>
</html>'''
    
    def generate_embed_code(self, model_name, usdz_url, gltf_url, width="100%", height="400px"):
        """Generate embeddable iframe code"""
        
        embed_html = f'''
<iframe 
    src="{self.cdn_base_url}/viewer.html?model={model_name}&usdz={usdz_url}&gltf={gltf_url}"
    width="{width}" 
    height="{height}"
    frameborder="0"
    allowfullscreen
    allow="xr-spatial-tracking; camera; gyroscope; accelerometer">
</iframe>'''
        
        return embed_html
```

### Social Media Integration

```python
class SocialMediaOptimizer:
    """Optimize AR content for social media platforms"""
    
    @staticmethod
    def generate_open_graph_meta(model_name, description, preview_image_url, usdz_url):
        """Generate Open Graph meta tags for social sharing"""
        
        return f'''
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="{model_name} - View in AR">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{preview_image_url}">
    <meta property="og:url" content="{usdz_url}">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{model_name} - View in AR">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{preview_image_url}">
    
    <!-- Apple-specific -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="format-detection" content="telephone=no">'''
    
    @staticmethod
    def create_instagram_story_template(model_name, usdz_url):
        """Create Instagram Story-optimized AR link"""
        
        # Instagram Stories dimensions: 1080x1920
        story_html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{model_name} AR</title>
    <style>
        body {{ 
            margin: 0; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            color: white;
        }}
        
        .logo {{ font-size: 48px; margin-bottom: 20px; }}
        .title {{ font-size: 28px; font-weight: bold; margin-bottom: 12px; text-align: center; }}
        .subtitle {{ font-size: 16px; opacity: 0.8; margin-bottom: 40px; text-align: center; }}
        
        .ar-button {{
            background: white;
            color: #333;
            border: none;
            border-radius: 25px;
            padding: 16px 32px;
            font-size: 18px;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }}
    </style>
</head>
<body>
    <div class="logo">📱</div>
    <div class="title">{model_name}</div>
    <div class="subtitle">Tap to view in AR</div>
    <a href="{usdz_url}" rel="ar" class="ar-button">Open in AR</a>
</body>
</html>'''
        
        return story_html
```

## File Size Optimization

### Asset Compression Strategies

```python
class AssetOptimizer:
    """Optimize USDZ and related assets for delivery"""
    
    @staticmethod
    def optimize_usdz_size(usdz_path, target_size_mb=10):
        """Optimize USDZ file size"""
        
        import zipfile
        import tempfile
        from PIL import Image
        
        current_size = os.path.getsize(usdz_path) / (1024 * 1024)  # MB
        
        if current_size <= target_size_mb:
            print(f"File already within target size: {current_size:.2f}MB")
            return usdz_path
        
        print(f"Optimizing USDZ: {current_size:.2f}MB -> target: {target_size_mb}MB")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract USDZ
            with zipfile.ZipFile(usdz_path, 'r') as zf:
                zf.extractall(temp_dir)
            
            # Optimize textures
            for texture_path in Path(temp_dir).glob("*.png"):
                AssetOptimizer._optimize_texture(texture_path, target_size_mb)
            
            for texture_path in Path(temp_dir).glob("*.jpg"):
                AssetOptimizer._optimize_texture(texture_path, target_size_mb)
            
            # Repackage
            optimized_path = usdz_path.with_suffix('.optimized.usdz')
            AssetOptimizer._repackage_usdz(temp_dir, optimized_path)
            
            new_size = os.path.getsize(optimized_path) / (1024 * 1024)
            print(f"Optimization complete: {new_size:.2f}MB")
            
            return optimized_path
    
    @staticmethod
    def _optimize_texture(texture_path, target_size_mb):
        """Optimize individual texture file"""
        
        with Image.open(texture_path) as img:
            # Calculate target resolution based on file size
            if target_size_mb < 5:
                max_size = 512
            elif target_size_mb < 15:
                max_size = 1024
            else:
                max_size = 2048
            
            # Resize if too large
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Optimize compression
            if texture_path.suffix.lower() == '.png':
                img.save(texture_path, 'PNG', optimize=True, compress_level=9)
            else:
                img.save(texture_path, 'JPEG', optimize=True, quality=85)
    
    @staticmethod
    def _repackage_usdz(temp_dir, output_path):
        """Repackage optimized files into USDZ"""
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_STORED) as zf:
            for file_path in Path(temp_dir).rglob('*'):
                if file_path.is_file():
                    zf.write(file_path, file_path.name)
    
    @staticmethod
    def create_progressive_loading_package(base_name, models_dir):
        """Create package with multiple quality levels"""
        
        qualities = {
            'low': {'max_vertices': 5000, 'texture_size': 512},
            'medium': {'max_vertices': 15000, 'texture_size': 1024},
            'high': {'max_vertices': 50000, 'texture_size': 2048}
        }
        
        packages = {}
        
        for quality, params in qualities.items():
            output_path = models_dir / f"{base_name}_{quality}.usdz"
            
            # Create quality-specific version
            # (Implementation would involve mesh decimation and texture resizing)
            packages[quality] = output_path
        
        return packages
```

### Bandwidth-Aware Delivery

```javascript
// Client-side adaptive loading
class AdaptiveARLoader {
    constructor() {
        this.connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        this.deviceMemory = navigator.deviceMemory || 4; // GB
    }
    
    selectOptimalModel(modelUrls) {
        const networkSpeed = this.getNetworkSpeed();
        const deviceCapability = this.getDeviceCapability();
        
        // Select model quality based on capabilities
        if (networkSpeed === 'slow' || deviceCapability === 'low') {
            return modelUrls.low;
        } else if (networkSpeed === 'medium' || deviceCapability === 'medium') {
            return modelUrls.medium;
        } else {
            return modelUrls.high;
        }
    }
    
    getNetworkSpeed() {
        if (!this.connection) return 'unknown';
        
        const effectiveType = this.connection.effectiveType;
        
        if (effectiveType === 'slow-2g' || effectiveType === '2g') {
            return 'slow';
        } else if (effectiveType === '3g') {
            return 'medium';
        } else {
            return 'fast';
        }
    }
    
    getDeviceCapability() {
        // Estimate device capability
        if (this.deviceMemory < 2) {
            return 'low';
        } else if (this.deviceMemory < 4) {
            return 'medium';
        } else {
            return 'high';
        }
    }
    
    preloadModel(url) {
        // Preload model based on network conditions
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = url;
        document.head.appendChild(link);
    }
}

// Usage example
const loader = new AdaptiveARLoader();
const modelUrls = {
    low: 'model_low.usdz',
    medium: 'model_medium.usdz', 
    high: 'model_high.usdz'
};

const selectedModel = loader.selectOptimalModel(modelUrls);
document.querySelector('model-viewer').src = selectedModel;
```

## Cross-Platform Testing

### Automated Testing Pipeline

```python
class CrossPlatformTester:
    """Test AR content across different platforms and devices"""
    
    def __init__(self):
        self.test_devices = [
            {'platform': 'ios', 'version': '15.0', 'device': 'iPhone 12'},
            {'platform': 'ios', 'version': '16.0', 'device': 'iPhone 14 Pro'},
            {'platform': 'android', 'version': '11', 'device': 'Pixel 5'},
            {'platform': 'web', 'browser': 'safari', 'version': '15.0'},
            {'platform': 'web', 'browser': 'chrome', 'version': '100.0'},
        ]
    
    def run_compatibility_tests(self, content_package):
        """Run compatibility tests across platforms"""
        
        results = {}
        
        for device in self.test_devices:
            platform = device['platform']
            test_result = self._test_platform(content_package, device)
            
            if platform not in results:
                results[platform] = []
            results[platform].append(test_result)
        
        return self._generate_test_report(results)
    
    def _test_platform(self, content_package, device):
        """Test content on specific platform/device"""
        
        test_result = {
            'device': device,
            'tests': {
                'file_size': self._test_file_size(content_package),
                'format_support': self._test_format_support(content_package, device),
                'rendering': self._test_rendering_quality(content_package, device),
                'performance': self._test_performance(content_package, device),
                'ar_features': self._test_ar_features(content_package, device)
            }
        }
        
        test_result['overall_score'] = self._calculate_score(test_result['tests'])
        
        return test_result
    
    def _test_file_size(self, content_package):
        """Test file size constraints"""
        
        size_mb = os.path.getsize(content_package['usdz']) / (1024 * 1024)
        
        if size_mb <= 10:
            return {'status': 'pass', 'size_mb': size_mb, 'note': 'Optimal size'}
        elif size_mb <= 25:
            return {'status': 'warning', 'size_mb': size_mb, 'note': 'Large but acceptable'}
        else:
            return {'status': 'fail', 'size_mb': size_mb, 'note': 'Too large for Quick Look'}
    
    def _test_format_support(self, content_package, device):
        """Test format support on device"""
        
        platform = device['platform']
        
        if platform == 'ios':
            return {'status': 'pass', 'note': 'Native USDZ support'}
        elif platform == 'android':
            if 'gltf' in content_package:
                return {'status': 'pass', 'note': 'glTF alternative available'}
            else:
                return {'status': 'fail', 'note': 'No Android-compatible format'}
        elif platform == 'web':
            browser = device.get('browser', 'unknown')
            if browser == 'safari':
                return {'status': 'pass', 'note': 'Safari USDZ support'}
            else:
                return {'status': 'warning', 'note': 'Limited browser support'}
        
        return {'status': 'unknown', 'note': 'Platform not tested'}
    
    def _generate_test_report(self, results):
        """Generate comprehensive test report"""
        
        report = {
            'summary': {},
            'platform_results': results,
            'recommendations': []
        }
        
        # Calculate overall compatibility
        total_tests = sum(len(platform_results) for platform_results in results.values())
        passed_tests = sum(
            1 for platform_results in results.values()
            for result in platform_results
            if result['overall_score'] >= 0.8
        )
        
        report['summary']['compatibility_percentage'] = (passed_tests / total_tests) * 100
        
        # Generate recommendations
        if report['summary']['compatibility_percentage'] < 80:
            report['recommendations'].append("Consider creating platform-specific optimizations")
        
        if 'android' in results:
            android_results = results['android']
            if any(r['overall_score'] < 0.6 for r in android_results):
                report['recommendations'].append("Improve Android compatibility with glTF optimization")
        
        return report
```

## Analytics and Performance Monitoring

### Usage Analytics

```javascript
class ARAnalytics {
    constructor(analyticsEndpoint) {
        this.endpoint = analyticsEndpoint;
        this.sessionId = this.generateSessionId();
        this.startTime = Date.now();
    }
    
    trackModelLoad(modelUrl, loadTime, fileSize) {
        this.sendEvent('model_load', {
            model_url: modelUrl,
            load_time_ms: loadTime,
            file_size_bytes: fileSize,
            user_agent: navigator.userAgent,
            connection_type: navigator.connection?.effectiveType,
            device_memory: navigator.deviceMemory
        });
    }
    
    trackARSession(duration, interactions) {
        this.sendEvent('ar_session', {
            duration_ms: duration,
            interactions: interactions,
            platform: this.detectPlatform(),
            ar_mode: this.detectARMode()
        });
    }
    
    trackError(errorType, errorMessage, context) {
        this.sendEvent('error', {
            error_type: errorType,
            error_message: errorMessage,
            context: context,
            user_agent: navigator.userAgent
        });
    }
    
    detectPlatform() {
        const ua = navigator.userAgent;
        if (/iPad|iPhone|iPod/.test(ua)) return 'ios';
        if (/Android/.test(ua)) return 'android';
        return 'desktop';
    }
    
    detectARMode() {
        if (navigator.xr) return 'webxr';
        if (/iPad|iPhone|iPod/.test(navigator.userAgent)) return 'arkit';
        if (/Android/.test(navigator.userAgent)) return 'arcore';
        return 'none';
    }
    
    sendEvent(eventType, data) {
        const eventData = {
            event_type: eventType,
            session_id: this.sessionId,
            timestamp: Date.now(),
            ...data
        };
        
        // Send to analytics endpoint
        fetch(this.endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(eventData)
        }).catch(console.error);
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }
}

// Usage integration
const analytics = new ARAnalytics('/api/analytics');
const modelViewer = document.querySelector('model-viewer');

modelViewer.addEventListener('load', (event) => {
    const loadTime = event.detail.loadTime || 0;
    const fileSize = event.detail.totalSize || 0;
    analytics.trackModelLoad(modelViewer.src, loadTime, fileSize);
});

modelViewer.addEventListener('ar-status', (event) => {
    if (event.detail.status === 'session-started') {
        analytics.arSessionStart = Date.now();
    } else if (event.detail.status === 'not-presenting') {
        const duration = Date.now() - (analytics.arSessionStart || 0);
        analytics.trackARSession(duration, analytics.interactions || 0);
    }
});
```

## Security and Privacy Considerations

### Content Protection

```python
class ContentProtection:
    """Implement content protection for AR assets"""
    
    @staticmethod
    def add_watermark_to_model(usd_stage, watermark_text):
        """Add invisible watermark to USD model"""
        
        # Add watermark as custom metadata
        root_prim = usd_stage.GetDefaultPrim()
        root_prim.SetCustomDataByKey("watermark", watermark_text)
        root_prim.SetCustomDataByKey("created_by", "AR Content System")
        root_prim.SetCustomDataByKey("creation_date", datetime.now().isoformat())
    
    @staticmethod
    def obfuscate_file_names(usdz_path):
        """Obfuscate internal file names in USDZ package"""
        
        import zipfile
        import tempfile
        import hashlib
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract
            with zipfile.ZipFile(usdz_path, 'r') as zf:
                zf.extractall(temp_dir)
            
            # Rename files with hash-based names
            file_mapping = {}
            for file_path in Path(temp_dir).iterdir():
                if file_path.is_file():
                    # Generate hash-based name
                    hash_name = hashlib.md5(file_path.name.encode()).hexdigest()
                    new_name = hash_name + file_path.suffix
                    new_path = file_path.parent / new_name
                    
                    file_path.rename(new_path)
                    file_mapping[file_path.name] = new_name
            
            # Update USD file references
            # (Implementation would update asset paths in USD files)
            
            # Repackage
            obfuscated_path = usdz_path.with_suffix('.protected.usdz')
            with zipfile.ZipFile(obfuscated_path, 'w', zipfile.ZIP_STORED) as zf:
                for file_path in Path(temp_dir).iterdir():
                    if file_path.is_file():
                        zf.write(file_path, file_path.name)
            
            return obfuscated_path
    
    @staticmethod
    def implement_domain_restrictions(html_content, allowed_domains):
        """Add domain restrictions to web AR viewer"""
        
        restriction_script = f'''
<script>
(function() {{
    const allowedDomains = {json.dumps(allowed_domains)};
    const currentDomain = window.location.hostname;
    
    if (!allowedDomains.includes(currentDomain)) {{
        document.body.innerHTML = '<h1>Access Denied</h1><p>This content is not authorized for this domain.</p>';
        return;
    }}
    
    // Prevent iframe embedding on unauthorized domains
    if (window.top !== window.self) {{
        const parentDomain = document.referrer ? new URL(document.referrer).hostname : '';
        if (!allowedDomains.includes(parentDomain)) {{
            window.top.location = window.location;
        }}
    }}
}})();
</script>'''
        
        # Insert before closing head tag
        return html_content.replace('</head>', restriction_script + '</head>')
```

## Best Practices Summary

### Distribution Checklist

1. **File Size Optimization:**
   - ✅ USDZ files under 25MB for Quick Look
   - ✅ Textures power-of-2 dimensions
   - ✅ Multiple quality levels for different connections

2. **Platform Coverage:**
   - ✅ USDZ for iOS devices
   - ✅ glTF for Android/Web
   - ✅ Fallback formats (OBJ/PNG)

3. **Web Integration:**
   - ✅ Progressive loading strategies
   - ✅ Responsive design for all screen sizes
   - ✅ SEO optimization with meta tags

4. **Performance Monitoring:**
   - ✅ Analytics for usage tracking
   - ✅ Error monitoring and reporting
   - ✅ Load time optimization

5. **Cross-Platform Testing:**
   - ✅ iOS devices (various models/versions)
   - ✅ Android ARCore compatibility
   - ✅ Web browser support verification

### Common Pitfalls to Avoid

- **Large File Sizes**: Keep USDZ under 25MB for Quick Look
- **Missing Fallbacks**: Always provide alternative formats
- **Poor Web Performance**: Implement progressive loading
- **Single Platform Focus**: Test across all target platforms
- **Ignoring Analytics**: Monitor usage and performance metrics

## Resources and Tools

### Validation Tools
- **usdchecker**: Validate USD/USDZ files
- **model-viewer**: Web AR testing
- **gltf-validator**: Validate glTF files

### Conversion Tools
- **usdcat**: Convert between USD formats
- **Blender**: USD/glTF conversion pipeline
- **Reality Converter**: Apple's USDZ conversion tool

### Analytics Platforms
- **Google Analytics**: Web AR tracking
- **Firebase**: Mobile app analytics
- **Custom solutions**: Platform-specific tracking

## Next Steps

1. **Mobile Optimization Guide** - Performance tuning for AR devices
2. **Advanced AR Features Guide** - Animations, physics, and interactions
3. **Enterprise Deployment** - Large-scale AR content management
4. **Future Standards** - WebXR and emerging AR technologies
