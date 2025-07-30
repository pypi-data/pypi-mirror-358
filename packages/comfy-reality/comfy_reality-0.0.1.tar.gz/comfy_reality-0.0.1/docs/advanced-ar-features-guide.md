# Advanced AR Features Guide

## Overview

This guide covers advanced AR features including animations, physics simulations, interactions, audio integration, and cutting-edge AR capabilities. Learn how to create immersive, interactive AR experiences that go beyond static 3D models.

## Animation in USDZ

### Basic Transform Animations

```python
from pxr import Usd, UsdGeom, Sdf, Gf, UsdSkel
import math

def create_rotation_animation(stage, prim_path, duration=4.0, axis='Y'):
    """Create rotation animation around specified axis"""
    
    prim = stage.GetPrimAtPath(prim_path)
    if not prim:
        return None
    
    # Create Xformable
    xformable = UsdGeom.Xformable(prim)
    
    # Create rotation operation
    if axis == 'Y':
        rotate_op = xformable.AddRotateYOp()
    elif axis == 'X':
        rotate_op = xformable.AddRotateXOp()
    else:  # Z
        rotate_op = xformable.AddRotateZOp()
    
    # Set time code range
    fps = 24
    start_frame = 1
    end_frame = int(duration * fps)
    
    stage.SetStartTimeCode(start_frame)
    stage.SetEndTimeCode(end_frame)
    
    # Create keyframes for full rotation
    for frame in range(start_frame, end_frame + 1):
        time_code = float(frame)
        progress = (frame - start_frame) / (end_frame - start_frame)
        rotation_degrees = progress * 360.0
        
        rotate_op.Set(rotation_degrees, time_code)
    
    return rotate_op

def create_translation_animation(stage, prim_path, start_pos, end_pos, duration=2.0):
    """Create translation animation between two points"""
    
    prim = stage.GetPrimAtPath(prim_path)
    xformable = UsdGeom.Xformable(prim)
    
    translate_op = xformable.AddTranslateOp()
    
    fps = 24
    start_frame = 1
    end_frame = int(duration * fps)
    
    stage.SetStartTimeCode(start_frame)
    stage.SetEndTimeCode(end_frame)
    
    # Interpolate between positions
    for frame in range(start_frame, end_frame + 1):
        time_code = float(frame)
        progress = (frame - start_frame) / (end_frame - start_frame)
        
        # Linear interpolation
        current_pos = [
            start_pos[0] + (end_pos[0] - start_pos[0]) * progress,
            start_pos[1] + (end_pos[1] - start_pos[1]) * progress,
            start_pos[2] + (end_pos[2] - start_pos[2]) * progress
        ]
        
        translate_op.Set(Gf.Vec3d(*current_pos), time_code)
    
    return translate_op

def create_scale_animation(stage, prim_path, start_scale=1.0, end_scale=2.0, duration=1.0):
    """Create scale animation with easing"""
    
    prim = stage.GetPrimAtPath(prim_path)
    xformable = UsdGeom.Xformable(prim)
    
    scale_op = xformable.AddScaleOp()
    
    fps = 24
    start_frame = 1
    end_frame = int(duration * fps)
    
    stage.SetStartTimeCode(start_frame)
    stage.SetEndTimeCode(end_frame)
    
    for frame in range(start_frame, end_frame + 1):
        time_code = float(frame)
        progress = (frame - start_frame) / (end_frame - start_frame)
        
        # Ease-in-out interpolation
        eased_progress = 0.5 * (1 - math.cos(progress * math.pi))
        
        current_scale = start_scale + (end_scale - start_scale) * eased_progress
        scale_vector = Gf.Vec3f(current_scale, current_scale, current_scale)
        
        scale_op.Set(scale_vector, time_code)
    
    return scale_op
```

### Advanced Animation Patterns

```python
class AnimationComposer:
    """Compose complex animation sequences"""
    
    def __init__(self, stage):
        self.stage = stage
        self.animations = []
    
    def add_bounce_animation(self, prim_path, height=0.5, duration=1.0, bounces=3):
        """Create bouncing animation"""
        
        prim = self.stage.GetPrimAtPath(prim_path)
        xformable = UsdGeom.Xformable(prim)
        translate_op = xformable.AddTranslateOp()
        
        fps = 24
        total_frames = int(duration * fps)
        
        for frame in range(total_frames):
            time_code = float(frame + 1)
            progress = frame / (total_frames - 1)
            
            # Create bouncing motion using sine wave with decay
            bounce_amplitude = height * math.exp(-progress * 2)  # Decay over time
            y_offset = bounce_amplitude * abs(math.sin(progress * bounces * 2 * math.pi))
            
            translate_op.Set(Gf.Vec3d(0, y_offset, 0), time_code)
        
        return translate_op
    
    def add_orbit_animation(self, prim_path, radius=2.0, duration=4.0, axis='Y'):
        """Create orbital motion animation"""
        
        prim = self.stage.GetPrimAtPath(prim_path)
        xformable = UsdGeom.Xformable(prim)
        translate_op = xformable.AddTranslateOp()
        
        fps = 24
        total_frames = int(duration * fps)
        
        for frame in range(total_frames):
            time_code = float(frame + 1)
            progress = frame / (total_frames - 1)
            angle = progress * 2 * math.pi
            
            if axis == 'Y':
                x = radius * math.cos(angle)
                y = 0
                z = radius * math.sin(angle)
            elif axis == 'X':
                x = 0
                y = radius * math.cos(angle)
                z = radius * math.sin(angle)
            else:  # Z axis
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                z = 0
            
            translate_op.Set(Gf.Vec3d(x, y, z), time_code)
        
        return translate_op
    
    def add_pulsing_animation(self, prim_path, min_scale=0.8, max_scale=1.2, duration=2.0):
        """Create pulsing scale animation"""
        
        prim = self.stage.GetPrimAtPath(prim_path)
        xformable = UsdGeom.Xformable(prim)
        scale_op = xformable.AddScaleOp()
        
        fps = 24
        total_frames = int(duration * fps)
        
        for frame in range(total_frames):
            time_code = float(frame + 1)
            progress = frame / (total_frames - 1)
            
            # Sine wave for smooth pulsing
            scale_factor = min_scale + (max_scale - min_scale) * (0.5 + 0.5 * math.sin(progress * 4 * math.pi))
            scale_vector = Gf.Vec3f(scale_factor, scale_factor, scale_factor)
            
            scale_op.Set(scale_vector, time_code)
        
        return scale_op

# Material animation
def animate_material_properties(stage, material_path, property_name, start_value, end_value, duration=2.0):
    """Animate material properties like color or roughness"""
    
    from pxr import UsdShade
    
    material = UsdShade.Material.Get(stage, material_path)
    if not material:
        return None
    
    # Get surface shader
    surface_output = material.GetSurfaceOutput()
    if not surface_output.HasConnectedSource():
        return None
    
    source_info = surface_output.GetConnectedSource()[0]
    shader = UsdShade.Shader(source_info.GetPrim())
    
    # Get the property input
    property_input = shader.GetInput(property_name)
    if not property_input:
        return None
    
    fps = 24
    total_frames = int(duration * fps)
    
    for frame in range(total_frames):
        time_code = float(frame + 1)
        progress = frame / (total_frames - 1)
        
        # Interpolate between start and end values
        if isinstance(start_value, (list, tuple)) and len(start_value) == 3:
            # Color interpolation
            current_value = [
                start_value[0] + (end_value[0] - start_value[0]) * progress,
                start_value[1] + (end_value[1] - start_value[1]) * progress,
                start_value[2] + (end_value[2] - start_value[2]) * progress
            ]
        else:
            # Scalar interpolation
            current_value = start_value + (end_value - start_value) * progress
        
        property_input.Set(current_value, time_code)
    
    return property_input
```

## Skeletal Animation and Character Rigging

### Basic Skeletal Setup

```python
def create_skeletal_animation(stage, mesh_path, skeleton_path):
    """Create basic skeletal animation setup"""
    
    from pxr import UsdSkel
    
    # Create skeleton
    skeleton = UsdSkel.Skeleton.Define(stage, skeleton_path)
    
    # Define joint hierarchy
    joint_names = [
        "root",
        "spine1", "spine2", "spine3",
        "neck", "head",
        "left_shoulder", "left_arm", "left_forearm", "left_hand",
        "right_shoulder", "right_arm", "right_forearm", "right_hand",
        "left_thigh", "left_shin", "left_foot",
        "right_thigh", "right_shin", "right_foot"
    ]
    
    skeleton.CreateJointsAttr(joint_names)
    
    # Define joint hierarchy (parent indices)
    joint_hierarchy = [
        -1,  # root (no parent)
        0,   # spine1 -> root
        1,   # spine2 -> spine1
        2,   # spine3 -> spine2
        3,   # neck -> spine3
        4,   # head -> neck
        3,   # left_shoulder -> spine3
        6,   # left_arm -> left_shoulder
        7,   # left_forearm -> left_arm
        8,   # left_hand -> left_forearm
        3,   # right_shoulder -> spine3
        10,  # right_arm -> right_shoulder
        11,  # right_forearm -> right_arm
        12,  # right_hand -> right_forearm
        0,   # left_thigh -> root
        14,  # left_shin -> left_thigh
        15,  # left_foot -> left_shin
        0,   # right_thigh -> root
        17,  # right_shin -> right_thigh
        18   # right_foot -> right_shin
    ]
    
    # Set rest transforms
    bind_transforms = []
    for i, joint_name in enumerate(joint_names):
        # Create identity transform for each joint
        transform = Gf.Matrix4d(1.0)
        
        # Position joints appropriately (simplified positioning)
        if "spine" in joint_name:
            transform.SetTranslateOnly(Gf.Vec3d(0, i * 0.3, 0))
        elif "arm" in joint_name or "forearm" in joint_name:
            side_offset = 0.5 if "left" in joint_name else -0.5
            transform.SetTranslateOnly(Gf.Vec3d(side_offset, 1.5, 0))
        elif "thigh" in joint_name or "shin" in joint_name:
            side_offset = 0.3 if "left" in joint_name else -0.3
            transform.SetTranslateOnly(Gf.Vec3d(side_offset, -0.5, 0))
        
        bind_transforms.append(transform)
    
    skeleton.CreateBindTransformsAttr(bind_transforms)
    skeleton.CreateRestTransformsAttr(bind_transforms)
    
    # Bind mesh to skeleton
    mesh_prim = stage.GetPrimAtPath(mesh_path)
    mesh = UsdGeom.Mesh(mesh_prim)
    
    # Create skin weights (simplified uniform weighting)
    vertex_count = len(mesh.GetPointsAttr().Get() or [])
    joint_count = len(joint_names)
    
    # Each vertex influenced by one joint (for simplicity)
    joint_indices = []
    joint_weights = []
    
    for v in range(vertex_count):
        # Assign to spine joint for demo
        joint_indices.extend([1])  # spine1
        joint_weights.extend([1.0])
    
    # Create skinning binding
    binding_api = UsdSkel.BindingAPI.Apply(mesh_prim)
    binding_api.CreateSkeletonRel().SetTargets([skeleton_path])
    binding_api.CreateJointIndicesAttr(joint_indices)
    binding_api.CreateJointWeightsAttr(joint_weights)
    
    return skeleton

def animate_skeleton(stage, skeleton_path, animation_name="walk_cycle"):
    """Add animation to skeleton"""
    
    from pxr import UsdSkel
    
    skeleton = UsdSkel.Skeleton.Get(stage, skeleton_path)
    if not skeleton:
        return None
    
    # Get joint names
    joint_names = skeleton.GetJointsAttr().Get()
    
    # Create animation data
    fps = 24
    duration = 2.0  # 2 second walk cycle
    total_frames = int(duration * fps)
    
    # Create transforms for each frame
    for frame in range(total_frames):
        time_code = float(frame + 1)
        progress = frame / (total_frames - 1)
        
        transforms = []
        
        for i, joint_name in enumerate(joint_names):
            transform = Gf.Matrix4d(1.0)
            
            # Simple walk cycle animation
            if "thigh" in joint_name:
                # Leg rotation for walking
                angle = math.sin(progress * 4 * math.pi) * 30  # 30 degree swing
                if "right" in joint_name:
                    angle = -angle  # Opposite phase
                
                rotation = Gf.Rotation(Gf.Vec3d(1, 0, 0), angle)
                transform.SetRotateOnly(rotation)
            
            elif "arm" in joint_name:
                # Arm swing (opposite to legs)
                angle = math.sin(progress * 4 * math.pi) * 20  # 20 degree swing
                if "left" in joint_name:
                    angle = -angle
                
                rotation = Gf.Rotation(Gf.Vec3d(1, 0, 0), angle)
                transform.SetRotateOnly(rotation)
            
            transforms.append(transform)
        
        # Set transforms for this frame
        skeleton.CreateAnimTransformsAttr().Set(transforms, time_code)
    
    return skeleton
```

## Physics Integration

### Collision Detection and Response

```python
class ARPhysicsSystem:
    """Physics system for AR objects"""
    
    def __init__(self, stage):
        self.stage = stage
        self.physics_objects = {}
        self.gravity = Gf.Vec3d(0, -9.81, 0)  # Earth gravity
        self.time_step = 1.0 / 60.0  # 60 FPS
    
    def add_physics_object(self, prim_path, mass=1.0, restitution=0.3, friction=0.5):
        """Add physics properties to an object"""
        
        prim = self.stage.GetPrimAtPath(prim_path)
        if not prim:
            return None
        
        # Add physics metadata
        prim.SetMetadata("physics:rigidBodyEnabled", True)
        prim.SetMetadata("physics:collisionEnabled", True)
        
        # Store physics properties
        self.physics_objects[prim_path] = {
            'prim': prim,
            'mass': mass,
            'restitution': restitution,
            'friction': friction,
            'velocity': Gf.Vec3d(0, 0, 0),
            'angular_velocity': Gf.Vec3d(0, 0, 0),
            'position': self._get_position(prim),
            'rotation': self._get_rotation(prim)
        }
        
        return prim
    
    def add_collision_shape(self, prim_path, shape_type="box", size=None):
        """Add collision shape to object"""
        
        prim = self.stage.GetPrimAtPath(prim_path)
        if not prim:
            return None
        
        # Create collision shape metadata
        if shape_type == "box":
            if size is None:
                size = [1.0, 1.0, 1.0]
            prim.SetMetadata("physics:collisionShape", "box")
            prim.SetMetadata("physics:collisionSize", size)
        
        elif shape_type == "sphere":
            radius = size[0] if size else 0.5
            prim.SetMetadata("physics:collisionShape", "sphere")
            prim.SetMetadata("physics:collisionRadius", radius)
        
        elif shape_type == "mesh":
            prim.SetMetadata("physics:collisionShape", "trimesh")
        
        return prim
    
    def simulate_physics_step(self, delta_time=None):
        """Simulate one physics step"""
        
        if delta_time is None:
            delta_time = self.time_step
        
        for prim_path, obj in self.physics_objects.items():
            # Apply gravity
            obj['velocity'] += self.gravity * delta_time
            
            # Update position
            new_position = obj['position'] + obj['velocity'] * delta_time
            
            # Simple ground collision
            if new_position[1] < 0:  # Hit ground
                new_position = Gf.Vec3d(new_position[0], 0, new_position[2])
                obj['velocity'] = Gf.Vec3d(
                    obj['velocity'][0] * obj['friction'],
                    -obj['velocity'][1] * obj['restitution'],
                    obj['velocity'][2] * obj['friction']
                )
            
            # Update object transform
            obj['position'] = new_position
            self._set_position(obj['prim'], new_position)
    
    def add_impulse(self, prim_path, force_vector):
        """Add impulse to physics object"""
        
        if prim_path in self.physics_objects:
            obj = self.physics_objects[prim_path]
            obj['velocity'] += force_vector / obj['mass']
    
    def _get_position(self, prim):
        """Get world position of prim"""
        xformable = UsdGeom.Xformable(prim)
        transform_matrix = xformable.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
        return transform_matrix.ExtractTranslation()
    
    def _set_position(self, prim, position):
        """Set world position of prim"""
        xformable = UsdGeom.Xformable(prim)
        
        # Create or get translate operation
        translate_ops = [op for op in xformable.GetOrderedXformOps() if op.GetOpType() == UsdGeom.XformOp.TypeTranslate]
        
        if translate_ops:
            translate_op = translate_ops[0]
        else:
            translate_op = xformable.AddTranslateOp()
        
        translate_op.Set(position)
    
    def _get_rotation(self, prim):
        """Get rotation of prim"""
        xformable = UsdGeom.Xformable(prim)
        transform_matrix = xformable.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
        return transform_matrix.ExtractRotation()

# Particle systems
class ParticleSystem:
    """Simple particle system for AR effects"""
    
    def __init__(self, stage, particle_count=100):
        self.stage = stage
        self.particle_count = particle_count
        self.particles = []
        self.emitter_position = Gf.Vec3d(0, 0, 0)
        
    def create_particle_effect(self, effect_type="explosion", duration=3.0):
        """Create particle effect"""
        
        if effect_type == "explosion":
            self._create_explosion_particles(duration)
        elif effect_type == "fire":
            self._create_fire_particles(duration)
        elif effect_type == "magic":
            self._create_magic_particles(duration)
    
    def _create_explosion_particles(self, duration):
        """Create explosion particle effect"""
        
        fps = 24
        total_frames = int(duration * fps)
        
        for i in range(self.particle_count):
            # Create particle prim
            particle_path = f"/Particles/Particle_{i:03d}"
            particle_prim = self.stage.DefinePrim(particle_path, "Sphere")
            sphere = UsdGeom.Sphere(particle_prim)
            
            # Small sphere
            sphere.CreateRadiusAttr(0.02)
            
            # Random velocity direction
            direction = Gf.Vec3d(
                random.uniform(-1, 1),
                random.uniform(0, 1),
                random.uniform(-1, 1)
            ).GetNormalized()
            
            speed = random.uniform(2, 5)
            velocity = direction * speed
            
            # Animate particle
            xformable = UsdGeom.Xformable(particle_prim)
            translate_op = xformable.AddTranslateOp()
            
            for frame in range(total_frames):
                time_code = float(frame + 1)
                progress = frame / (total_frames - 1)
                
                # Physics simulation
                gravity_effect = Gf.Vec3d(0, -9.81 * progress * progress, 0)
                position = self.emitter_position + velocity * progress + gravity_effect
                
                translate_op.Set(position, time_code)
```

## Interactive AR Features

### Touch and Gesture Interactions

```python
class ARInteractionSystem:
    """Handle AR interactions and gestures"""
    
    def __init__(self, stage):
        self.stage = stage
        self.interactive_objects = {}
        self.interaction_callbacks = {}
    
    def make_object_interactive(self, prim_path, interaction_types=None):
        """Make object respond to interactions"""
        
        if interaction_types is None:
            interaction_types = ['tap', 'pinch', 'rotation']
        
        prim = self.stage.GetPrimAtPath(prim_path)
        if not prim:
            return None
        
        # Add interaction metadata
        prim.SetMetadata("interaction:enabled", True)
        prim.SetMetadata("interaction:types", interaction_types)
        
        self.interactive_objects[prim_path] = {
            'prim': prim,
            'types': interaction_types,
            'state': 'idle',
            'last_interaction': None
        }
        
        return prim
    
    def add_interaction_callback(self, prim_path, interaction_type, callback_function):
        """Add callback for specific interaction"""
        
        if prim_path not in self.interaction_callbacks:
            self.interaction_callbacks[prim_path] = {}
        
        self.interaction_callbacks[prim_path][interaction_type] = callback_function
    
    def handle_tap_interaction(self, prim_path, tap_position):
        """Handle tap interaction"""
        
        if prim_path in self.interactive_objects:
            obj = self.interactive_objects[prim_path]
            
            if 'tap' in obj['types']:
                obj['state'] = 'tapped'
                obj['last_interaction'] = 'tap'
                
                # Execute callback if available
                if (prim_path in self.interaction_callbacks and 
                    'tap' in self.interaction_callbacks[prim_path]):
                    self.interaction_callbacks[prim_path]['tap'](tap_position)
                
                # Default tap behavior: scale animation
                self._animate_tap_feedback(prim_path)
    
    def handle_pinch_interaction(self, prim_path, scale_factor, gesture_center):
        """Handle pinch (scale) interaction"""
        
        if prim_path in self.interactive_objects:
            obj = self.interactive_objects[prim_path]
            
            if 'pinch' in obj['types']:
                obj['state'] = 'scaling'
                
                # Apply scale transform
                self._apply_scale_transform(prim_path, scale_factor)
                
                # Execute callback
                if (prim_path in self.interaction_callbacks and 
                    'pinch' in self.interaction_callbacks[prim_path]):
                    self.interaction_callbacks[prim_path]['pinch'](scale_factor, gesture_center)
    
    def handle_rotation_interaction(self, prim_path, rotation_delta, gesture_center):
        """Handle rotation interaction"""
        
        if prim_path in self.interactive_objects:
            obj = self.interactive_objects[prim_path]
            
            if 'rotation' in obj['types']:
                obj['state'] = 'rotating'
                
                # Apply rotation transform
                self._apply_rotation_transform(prim_path, rotation_delta)
                
                # Execute callback
                if (prim_path in self.interaction_callbacks and 
                    'rotation' in self.interaction_callbacks[prim_path]):
                    self.interaction_callbacks[prim_path]['rotation'](rotation_delta, gesture_center)
    
    def _animate_tap_feedback(self, prim_path):
        """Animate tap feedback"""
        
        prim = self.stage.GetPrimAtPath(prim_path)
        xformable = UsdGeom.Xformable(prim)
        
        # Quick scale animation for feedback
        scale_op = xformable.AddScaleOp()
        
        # Frame setup
        fps = 24
        duration = 0.3  # 300ms feedback
        total_frames = int(duration * fps)
        
        for frame in range(total_frames):
            time_code = float(frame + 1)
            progress = frame / (total_frames - 1)
            
            # Quick scale up then down
            if progress < 0.5:
                scale_factor = 1.0 + 0.2 * (progress * 2)  # Scale up to 1.2
            else:
                scale_factor = 1.2 - 0.2 * ((progress - 0.5) * 2)  # Scale back to 1.0
            
            scale_vector = Gf.Vec3f(scale_factor, scale_factor, scale_factor)
            scale_op.Set(scale_vector, time_code)
    
    def _apply_scale_transform(self, prim_path, scale_factor):
        """Apply scale transform to object"""
        
        prim = self.stage.GetPrimAtPath(prim_path)
        xformable = UsdGeom.Xformable(prim)
        
        # Get or create scale operation
        scale_ops = [op for op in xformable.GetOrderedXformOps() if op.GetOpType() == UsdGeom.XformOp.TypeScale]
        
        if scale_ops:
            scale_op = scale_ops[0]
            current_scale = scale_op.Get()
            new_scale = Gf.Vec3f(current_scale) * scale_factor
        else:
            scale_op = xformable.AddScaleOp()
            new_scale = Gf.Vec3f(scale_factor, scale_factor, scale_factor)
        
        scale_op.Set(new_scale)
    
    def _apply_rotation_transform(self, prim_path, rotation_delta):
        """Apply rotation transform to object"""
        
        prim = self.stage.GetPrimAtPath(prim_path)
        xformable = UsdGeom.Xformable(prim)
        
        # Get or create rotation operation
        rotate_ops = [op for op in xformable.GetOrderedXformOps() if op.GetOpType() == UsdGeom.XformOp.TypeRotateY]
        
        if rotate_ops:
            rotate_op = rotate_ops[0]
            current_rotation = rotate_op.Get()
            new_rotation = current_rotation + rotation_delta
        else:
            rotate_op = xformable.AddRotateYOp()
            new_rotation = rotation_delta
        
        rotate_op.Set(new_rotation)

# Multi-touch gesture recognition
class GestureRecognizer:
    """Recognize complex multi-touch gestures"""
    
    def __init__(self):
        self.touch_points = {}
        self.gesture_threshold = 0.05  # Minimum movement for gesture
        self.gesture_history = []
    
    def add_touch_point(self, touch_id, position, timestamp):
        """Add or update touch point"""
        
        self.touch_points[touch_id] = {
            'position': position,
            'timestamp': timestamp,
            'start_position': position if touch_id not in self.touch_points else self.touch_points[touch_id]['start_position'],
            'last_position': self.touch_points[touch_id]['position'] if touch_id in self.touch_points else position
        }
    
    def remove_touch_point(self, touch_id):
        """Remove touch point when touch ends"""
        
        if touch_id in self.touch_points:
            del self.touch_points[touch_id]
    
    def detect_gesture(self):
        """Detect current gesture based on touch points"""
        
        touch_count = len(self.touch_points)
        
        if touch_count == 0:
            return None
        elif touch_count == 1:
            return self._detect_single_touch_gesture()
        elif touch_count == 2:
            return self._detect_two_touch_gesture()
        else:
            return {'type': 'multi_touch', 'touch_count': touch_count}
    
    def _detect_single_touch_gesture(self):
        """Detect single touch gestures"""
        
        touch_id = list(self.touch_points.keys())[0]
        touch = self.touch_points[touch_id]
        
        movement = self._calculate_distance(touch['start_position'], touch['position'])
        
        if movement < self.gesture_threshold:
            return {'type': 'tap', 'position': touch['position']}
        else:
            return {'type': 'drag', 'start': touch['start_position'], 'current': touch['position']}
    
    def _detect_two_touch_gesture(self):
        """Detect two-touch gestures (pinch, rotation)"""
        
        touches = list(self.touch_points.values())
        
        # Current distance and angle
        current_distance = self._calculate_distance(touches[0]['position'], touches[1]['position'])
        current_angle = self._calculate_angle(touches[0]['position'], touches[1]['position'])
        
        # Start distance and angle
        start_distance = self._calculate_distance(touches[0]['start_position'], touches[1]['start_position'])
        start_angle = self._calculate_angle(touches[0]['start_position'], touches[1]['start_position'])
        
        # Detect pinch
        scale_factor = current_distance / start_distance if start_distance > 0 else 1.0
        
        # Detect rotation
        rotation_delta = current_angle - start_angle
        
        # Determine primary gesture
        if abs(scale_factor - 1.0) > 0.1:
            return {'type': 'pinch', 'scale_factor': scale_factor, 'center': self._calculate_center(touches)}
        elif abs(rotation_delta) > 5:  # 5 degrees threshold
            return {'type': 'rotation', 'rotation_delta': rotation_delta, 'center': self._calculate_center(touches)}
        else:
            return {'type': 'two_finger_drag', 'touches': touches}
    
    def _calculate_distance(self, pos1, pos2):
        """Calculate distance between two points"""
        
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def _calculate_angle(self, pos1, pos2):
        """Calculate angle between two points"""
        
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        return math.degrees(math.atan2(dy, dx))
    
    def _calculate_center(self, touches):
        """Calculate center point of touches"""
        
        center_x = sum(touch['position'][0] for touch in touches) / len(touches)
        center_y = sum(touch['position'][1] for touch in touches) / len(touches)
        return [center_x, center_y]
```

## Audio Integration

### Spatial Audio for AR

```python
class ARSpatialAudio:
    """Spatial audio system for AR experiences"""
    
    def __init__(self, stage):
        self.stage = stage
        self.audio_sources = {}
        self.listener_position = Gf.Vec3d(0, 0, 0)
        self.listener_orientation = Gf.Vec3d(0, 0, -1)  # Forward vector
    
    def add_audio_source(self, prim_path, audio_file_path, spatial=True):
        """Add spatial audio source to object"""
        
        prim = self.stage.GetPrimAtPath(prim_path)
        if not prim:
            return None
        
        # Add audio metadata
        prim.SetMetadata("audio:enabled", True)
        prim.SetMetadata("audio:file", audio_file_path)
        prim.SetMetadata("audio:spatial", spatial)
        
        self.audio_sources[prim_path] = {
            'prim': prim,
            'audio_file': audio_file_path,
            'spatial': spatial,
            'volume': 1.0,
            'pitch': 1.0,
            'loop': False,
            'distance_model': 'linear',
            'max_distance': 10.0,
            'reference_distance': 1.0
        }
        
        return prim
    
    def set_audio_properties(self, prim_path, volume=None, pitch=None, loop=None):
        """Set audio properties for source"""
        
        if prim_path in self.audio_sources:
            source = self.audio_sources[prim_path]
            
            if volume is not None:
                source['volume'] = volume
                source['prim'].SetMetadata("audio:volume", volume)
            
            if pitch is not None:
                source['pitch'] = pitch
                source['prim'].SetMetadata("audio:pitch", pitch)
            
            if loop is not None:
                source['loop'] = loop
                source['prim'].SetMetadata("audio:loop", loop)
    
    def create_ambient_soundscape(self, soundscape_config):
        """Create ambient soundscape with multiple layers"""
        
        soundscape_prim = self.stage.DefinePrim("/Audio/Soundscape", "Scope")
        
        for layer_name, config in soundscape_config.items():
            layer_path = f"/Audio/Soundscape/{layer_name}"
            layer_prim = self.stage.DefinePrim(layer_path, "Scope")
            
            self.add_audio_source(layer_path, config['file'], spatial=False)
            self.set_audio_properties(
                layer_path,
                volume=config.get('volume', 0.5),
                loop=config.get('loop', True)
            )
        
        return soundscape_prim
    
    def create_audio_trigger(self, prim_path, trigger_type="proximity", trigger_distance=2.0):
        """Create audio trigger based on proximity or interaction"""
        
        prim = self.stage.GetPrimAtPath(prim_path)
        if not prim:
            return None
        
        # Add trigger metadata
        prim.SetMetadata("audio:trigger_type", trigger_type)
        prim.SetMetadata("audio:trigger_distance", trigger_distance)
        
        if trigger_type == "proximity":
            # Audio plays when user gets within distance
            prim.SetMetadata("audio:auto_play", False)
            prim.SetMetadata("audio:proximity_trigger", True)
        
        elif trigger_type == "interaction":
            # Audio plays on tap/touch
            prim.SetMetadata("audio:interaction_trigger", True)
        
        return prim
    
    def calculate_spatial_audio_parameters(self, source_prim_path, listener_position):
        """Calculate spatial audio parameters"""
        
        if source_prim_path not in self.audio_sources:
            return None
        
        source = self.audio_sources[source_prim_path]
        
        # Get source position
        source_position = self._get_world_position(source['prim'])
        
        # Calculate distance
        distance = (source_position - listener_position).GetLength()
        
        # Calculate volume based on distance
        ref_distance = source['reference_distance']
        max_distance = source['max_distance']
        
        if distance <= ref_distance:
            distance_volume = 1.0
        elif distance >= max_distance:
            distance_volume = 0.0
        else:
            # Linear falloff
            distance_volume = 1.0 - ((distance - ref_distance) / (max_distance - ref_distance))
        
        # Calculate pan (stereo positioning)
        direction_to_source = (source_position - listener_position).GetNormalized()
        pan = direction_to_source[0]  # X component for left/right
        
        return {
            'volume': source['volume'] * distance_volume,
            'pan': pan,
            'distance': distance,
            'pitch': source['pitch']
        }
    
    def _get_world_position(self, prim):
        """Get world position of prim"""
        xformable = UsdGeom.Xformable(prim)
        transform_matrix = xformable.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
        return transform_matrix.ExtractTranslation()

# Audio-triggered animations
def create_audio_reactive_animation(stage, prim_path, audio_source_path, animation_type="scale_pulse"):
    """Create animation that reacts to audio"""
    
    prim = stage.GetPrimAtPath(prim_path)
    xformable = UsdGeom.Xformable(prim)
    
    # Add audio-reactive metadata
    prim.SetMetadata("audio:reactive", True)
    prim.SetMetadata("audio:source", audio_source_path)
    prim.SetMetadata("audio:animation_type", animation_type)
    
    if animation_type == "scale_pulse":
        # Scale animation based on audio amplitude
        scale_op = xformable.AddScaleOp()
        
        # Create keyframes (would be driven by audio analysis in real implementation)
        fps = 24
        duration = 4.0
        total_frames = int(duration * fps)
        
        for frame in range(total_frames):
            time_code = float(frame + 1)
            progress = frame / (total_frames - 1)
            
            # Simulate audio-driven scaling
            amplitude = 0.5 + 0.5 * math.sin(progress * 8 * math.pi)  # Simulated audio amplitude
            scale_factor = 1.0 + amplitude * 0.3  # Scale between 1.0 and 1.3
            
            scale_vector = Gf.Vec3f(scale_factor, scale_factor, scale_factor)
            scale_op.Set(scale_vector, time_code)
    
    elif animation_type == "color_pulse":
        # Color animation based on audio
        # This would require material animation setup
        pass
    
    return prim
```

## Advanced Lighting and Environment

### Dynamic Lighting Systems

```python
class ARLightingSystem:
    """Advanced lighting system for AR scenes"""
    
    def __init__(self, stage):
        self.stage = stage
        self.lights = {}
        self.environment_lighting = None
    
    def create_dynamic_lighting(self, lighting_scenario="outdoor_day"):
        """Create dynamic lighting setup"""
        
        scenarios = {
            "outdoor_day": {
                "sun_intensity": 3.0,
                "sun_angle": 45,
                "sky_intensity": 0.8,
                "ambient_color": [0.6, 0.7, 1.0]
            },
            "outdoor_sunset": {
                "sun_intensity": 2.0,
                "sun_angle": 15,
                "sky_intensity": 0.5,
                "ambient_color": [1.0, 0.6, 0.3]
            },
            "indoor_warm": {
                "sun_intensity": 0.0,
                "sun_angle": 90,
                "sky_intensity": 0.3,
                "ambient_color": [1.0, 0.9, 0.7]
            }
        }
        
        config = scenarios.get(lighting_scenario, scenarios["outdoor_day"])
        
        # Create sun light
        sun_light = self._create_sun_light(config)
        
        # Create environment lighting
        env_light = self._create_environment_light(config)
        
        # Create fill lights if needed
        if lighting_scenario == "indoor_warm":
            fill_lights = self._create_indoor_fill_lights()
        
        return {
            'sun': sun_light,
            'environment': env_light,
            'scenario': lighting_scenario
        }
    
    def _create_sun_light(self, config):
        """Create directional sun light"""
        
        sun_path = "/Lights/SunLight"
        sun_prim = self.stage.DefinePrim(sun_path, "DistantLight")
        sun_light = UsdLux.DistantLight(sun_prim)
        
        # Set sun properties
        sun_light.CreateIntensityAttr(config["sun_intensity"])
        sun_light.CreateColorAttr(Gf.Vec3f(1.0, 0.95, 0.8))  # Slightly warm white
        
        # Set sun angle
        xformable = UsdGeom.Xformable(sun_prim)
        rotate_op = xformable.AddRotateXOp()
        rotate_op.Set(config["sun_angle"])
        
        self.lights["sun"] = sun_light
        return sun_light
    
    def _create_environment_light(self, config):
        """Create environment/sky lighting"""
        
        env_path = "/Lights/EnvironmentLight"
        env_prim = self.stage.DefinePrim(env_path, "SphereLight")
        env_light = UsdLux.SphereLight(env_prim)
        
        # Set environment properties
        env_light.CreateIntensityAttr(config["sky_intensity"])
        env_light.CreateColorAttr(Gf.Vec3f(*config["ambient_color"]))
        env_light.CreateRadiusAttr(100.0)  # Large radius for environment
        
        self.lights["environment"] = env_light
        return env_light
    
    def _create_indoor_fill_lights(self):
        """Create fill lights for indoor scenarios"""
        
        fill_lights = []
        
        # Key light
        key_path = "/Lights/KeyLight"
        key_prim = self.stage.DefinePrim(key_path, "RectLight")
        key_light = UsdLux.RectLight(key_prim)
        
        key_light.CreateIntensityAttr(2.0)
        key_light.CreateColorAttr(Gf.Vec3f(1.0, 0.9, 0.8))
        key_light.CreateWidthAttr(2.0)
        key_light.CreateHeightAttr(2.0)
        
        # Position key light
        xformable = UsdGeom.Xformable(key_prim)
        translate_op = xformable.AddTranslateOp()
        translate_op.Set(Gf.Vec3d(2, 3, 2))
        
        fill_lights.append(key_light)
        
        # Fill light
        fill_path = "/Lights/FillLight"
        fill_prim = self.stage.DefinePrim(fill_path, "SphereLight")
        fill_light = UsdLux.SphereLight(fill_prim)
        
        fill_light.CreateIntensityAttr(0.5)
        fill_light.CreateColorAttr(Gf.Vec3f(0.8, 0.9, 1.0))  # Cooler fill
        fill_light.CreateRadiusAttr(0.5)
        
        # Position fill light
        xformable = UsdGeom.Xformable(fill_prim)
        translate_op = xformable.AddTranslateOp()
        translate_op.Set(Gf.Vec3d(-1, 2, 1))
        
        fill_lights.append(fill_light)
        
        return fill_lights
    
    def animate_lighting_transition(self, from_scenario, to_scenario, duration=3.0):
        """Animate transition between lighting scenarios"""
        
        fps = 24
        total_frames = int(duration * fps)
        
        # Get scenario configurations
        scenarios = {
            "outdoor_day": {"sun_intensity": 3.0, "sun_angle": 45, "ambient_color": [0.6, 0.7, 1.0]},
            "outdoor_sunset": {"sun_intensity": 2.0, "sun_angle": 15, "ambient_color": [1.0, 0.6, 0.3]},
            "night": {"sun_intensity": 0.1, "sun_angle": -10, "ambient_color": [0.2, 0.2, 0.4]}
        }
        
        from_config = scenarios[from_scenario]
        to_config = scenarios[to_scenario]
        
        # Animate sun light
        if "sun" in self.lights:
            sun_light = self.lights["sun"]
            intensity_attr = sun_light.GetIntensityAttr()
            color_attr = sun_light.GetColorAttr()
            
            for frame in range(total_frames):
                time_code = float(frame + 1)
                progress = frame / (total_frames - 1)
                
                # Interpolate intensity
                intensity = from_config["sun_intensity"] + (to_config["sun_intensity"] - from_config["sun_intensity"]) * progress
                intensity_attr.Set(intensity, time_code)
                
                # Interpolate color
                from_color = from_config["ambient_color"]
                to_color = to_config["ambient_color"]
                
                interpolated_color = [
                    from_color[0] + (to_color[0] - from_color[0]) * progress,
                    from_color[1] + (to_color[1] - from_color[1]) * progress,
                    from_color[2] + (to_color[2] - from_color[2]) * progress
                ]
                
                color_attr.Set(Gf.Vec3f(*interpolated_color), time_code)
    
    def create_volumetric_lighting(self, light_path, volume_density=0.1):
        """Create volumetric lighting effects"""
        
        light_prim = self.stage.GetPrimAtPath(light_path)
        if not light_prim:
            return None
        
        # Add volumetric properties
        light_prim.SetMetadata("lighting:volumetric", True)
        light_prim.SetMetadata("lighting:volume_density", volume_density)
        light_prim.SetMetadata("lighting:scattering", 0.8)
        
        return light_prim

# Real-time lighting adaptation
class AdaptiveLighting:
    """Adapt lighting to real-world conditions"""
    
    def __init__(self, lighting_system):
        self.lighting_system = lighting_system
        self.current_conditions = {}
    
    def update_environmental_conditions(self, time_of_day, weather, indoor=False):
        """Update lighting based on environmental conditions"""
        
        self.current_conditions = {
            'time_of_day': time_of_day,  # 0-24 hours
            'weather': weather,          # 'sunny', 'cloudy', 'rainy', 'night'
            'indoor': indoor
        }
        
        # Calculate appropriate lighting
        if indoor:
            scenario = "indoor_warm"
        else:
            if time_of_day < 6 or time_of_day > 20:
                scenario = "night"
            elif time_of_day < 8 or time_of_day > 18:
                scenario = "outdoor_sunset"
            else:
                scenario = "outdoor_day"
        
        # Adjust for weather
        if weather == "cloudy" and not indoor:
            # Reduce sun intensity, increase ambient
            pass
        elif weather == "rainy":
            # Much reduced sun, cool color temperature
            pass
        
        return self.lighting_system.create_dynamic_lighting(scenario)
```

## Performance Monitoring for Advanced Features

### Real-time Performance Analytics

```python
class AdvancedARPerformanceMonitor:
    """Monitor performance of advanced AR features"""
    
    def __init__(self):
        self.metrics = {
            'animation_performance': [],
            'physics_performance': [],
            'audio_performance': [],
            'interaction_latency': [],
            'lighting_performance': []
        }
        self.frame_budget = 33.33  # ms for 30 FPS
    
    def track_animation_performance(self, animation_count, frame_time_ms):
        """Track animation system performance"""
        
        self.metrics['animation_performance'].append({
            'timestamp': time.time(),
            'animation_count': animation_count,
            'frame_time_ms': frame_time_ms,
            'performance_score': self._calculate_animation_score(animation_count, frame_time_ms)
        })
    
    def track_physics_performance(self, physics_objects, simulation_time_ms):
        """Track physics simulation performance"""
        
        self.metrics['physics_performance'].append({
            'timestamp': time.time(),
            'physics_objects': physics_objects,
            'simulation_time_ms': simulation_time_ms,
            'performance_score': self._calculate_physics_score(physics_objects, simulation_time_ms)
        })
    
    def track_interaction_latency(self, interaction_type, latency_ms):
        """Track interaction response latency"""
        
        self.metrics['interaction_latency'].append({
            'timestamp': time.time(),
            'interaction_type': interaction_type,
            'latency_ms': latency_ms,
            'acceptable': latency_ms < 50  # 50ms threshold for good responsiveness
        })
    
    def get_performance_recommendations(self):
        """Generate performance optimization recommendations"""
        
        recommendations = []
        
        # Analyze animation performance
        if self.metrics['animation_performance']:
            avg_anim_score = sum(m['performance_score'] for m in self.metrics['animation_performance'][-30:]) / min(30, len(self.metrics['animation_performance']))
            
            if avg_anim_score < 70:
                recommendations.append("Reduce animation complexity or frequency")
        
        # Analyze physics performance
        if self.metrics['physics_performance']:
            recent_physics = self.metrics['physics_performance'][-10:]
            if recent_physics:
                avg_sim_time = sum(m['simulation_time_ms'] for m in recent_physics) / len(recent_physics)
                
                if avg_sim_time > 10:  # 10ms physics budget
                    recommendations.append("Reduce physics object count or simulation complexity")
        
        # Analyze interaction latency
        if self.metrics['interaction_latency']:
            recent_interactions = self.metrics['interaction_latency'][-20:]
            high_latency_count = sum(1 for m in recent_interactions if not m['acceptable'])
            
            if high_latency_count > len(recent_interactions) * 0.2:  # More than 20% high latency
                recommendations.append("Optimize interaction handling for better responsiveness")
        
        return recommendations
    
    def _calculate_animation_score(self, animation_count, frame_time_ms):
        """Calculate animation performance score"""
        
        # Base score on frame time efficiency
        frame_efficiency = min(100, (self.frame_budget / frame_time_ms) * 100)
        
        # Adjust for animation complexity
        complexity_penalty = min(20, animation_count * 2)  # 2 points per animation
        
        return max(0, frame_efficiency - complexity_penalty)
    
    def _calculate_physics_score(self, physics_objects, simulation_time_ms):
        """Calculate physics performance score"""
        
        target_sim_time = 5  # 5ms target for physics
        time_efficiency = min(100, (target_sim_time / simulation_time_ms) * 100) if simulation_time_ms > 0 else 100
        
        return time_efficiency
```

## Best Practices for Advanced Features

### Feature Integration Guidelines

1. **Animation Optimization:**
   - ✅ Limit concurrent animations on mobile
   - ✅ Use transform animations over vertex animations
   - ✅ Implement LOD for distant animated objects
   - ✅ Cache animation data when possible

2. **Physics Integration:**
   - ✅ Use simplified collision shapes
   - ✅ Limit physics object count (<10 on mobile)
   - ✅ Implement physics sleeping for static objects
   - ✅ Use fixed timestep for consistent simulation

3. **Interactive Features:**
   - ✅ Minimize interaction latency (<50ms)
   - ✅ Provide visual feedback for all interactions
   - ✅ Handle gesture conflicts gracefully
   - ✅ Support accessibility features

4. **Audio Integration:**
   - ✅ Use compressed audio formats
   - ✅ Implement audio culling for distant sources
   - ✅ Provide audio settings for user control
   - ✅ Handle audio interruptions properly

5. **Performance Management:**
   - ✅ Monitor frame rate continuously
   - ✅ Implement adaptive quality systems
   - ✅ Profile advanced features regularly
   - ✅ Provide performance debugging tools

## Resources and Documentation

### Advanced AR Development
- **USD Animation Documentation**: Advanced animation techniques
- **ARKit Physics**: iOS physics integration
- **Spatial Audio Guidelines**: 3D audio best practices
- **Gesture Recognition**: Multi-touch interaction patterns

### Performance Optimization
- **Mobile AR Performance**: Device-specific optimization
- **Animation Profiling**: Performance analysis tools
- **Physics Optimization**: Simulation performance tuning

## Next Steps

Future advanced features to explore:
1. **Machine Learning Integration** - AI-powered interactions and adaptations
2. **Cloud-Connected AR** - Server-side processing and shared experiences
3. **Collaborative AR** - Multi-user shared AR sessions
4. **Advanced Computer Vision** - Object recognition and tracking
5. **Procedural Content** - Dynamic AR content generation
