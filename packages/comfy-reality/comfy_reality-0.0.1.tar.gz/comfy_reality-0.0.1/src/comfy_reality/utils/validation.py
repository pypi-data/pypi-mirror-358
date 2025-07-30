"""Validation utilities for ComfyReality workflows."""

from pathlib import Path
from typing import Any

import numpy as np
import torch


def validate_workflow(workflow_data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a ComfyReality workflow.

    Args:
        workflow_data: Workflow configuration dictionary

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    # Check required fields
    required_fields = ["nodes", "connections"]
    for field in required_fields:
        if field not in workflow_data:
            errors.append(f"Missing required field: {field}")

    # Validate nodes
    if "nodes" in workflow_data:
        node_errors = _validate_nodes(workflow_data["nodes"])
        errors.extend(node_errors)

    # Validate connections
    if "connections" in workflow_data:
        connection_errors = _validate_connections(workflow_data["connections"])
        errors.extend(connection_errors)

    return len(errors) == 0, errors


def validate_usdz(file_path: str) -> tuple[bool, list[str]]:
    """Validate a USDZ file.

    Args:
        file_path: Path to USDZ file

    Returns:
        (is_valid, list_of_issues)
    """
    issues = []
    file_path_obj = Path(file_path)

    # Check if file exists
    if not file_path_obj.exists():
        issues.append("USDZ file does not exist")
        return False, issues

    # Check file extension
    if file_path_obj.suffix.lower() != ".usdz":
        issues.append("File must have .usdz extension")

    # Check file size (iOS has limits)
    file_size = file_path_obj.stat().st_size
    if file_size > 25 * 1024 * 1024:  # 25MB limit
        issues.append("USDZ file too large (>25MB)")

    if file_size == 0:
        issues.append("USDZ file is empty")

    # Basic validation - check if it's a ZIP file
    try:
        with open(file_path, "rb") as f:
            header = f.read(4)
            if header[:2] != b"PK":
                issues.append("Invalid USDZ format (not a ZIP file)")
    except Exception as e:
        issues.append(f"Error reading file: {e}")

    return len(issues) == 0, issues


def validate_image_tensor(tensor: Any) -> tuple[bool, list[str]]:
    """Validate image tensor format.

    Args:
        tensor: Image tensor to validate

    Returns:
        (is_valid, list_of_issues)
    """
    issues = []

    # Check tensor type
    if not isinstance(tensor, torch.Tensor):
        issues.append("Input must be a torch.Tensor")
        return False, issues

    # Check dimensions
    if tensor.dim() not in [3, 4]:
        issues.append(f"Tensor must have 3 or 4 dimensions, got {tensor.dim()}")

    # Check channels
    if tensor.dim() == 4:
        channels = tensor.shape[1]
    elif tensor.dim() == 3:
        channels = tensor.shape[0] if tensor.shape[0] <= 4 else tensor.shape[2]
    else:
        channels = 0

    if channels not in [1, 3, 4]:
        issues.append(f"Tensor must have 1, 3, or 4 channels, got {channels}")

    # Check value range
    if tensor.min() < 0 or tensor.max() > 1.0:
        issues.append("Tensor values should be in range [0, 1]")

    return len(issues) == 0, issues


def validate_mask_tensor(tensor: Any) -> tuple[bool, list[str]]:
    """Validate mask tensor format.

    Args:
        tensor: Mask tensor to validate

    Returns:
        (is_valid, list_of_issues)
    """
    issues = []

    # Check tensor type
    if not isinstance(tensor, torch.Tensor):
        issues.append("Input must be a torch.Tensor")
        return False, issues

    # Check dimensions (mask should be 2D or 3D)
    if tensor.dim() not in [2, 3, 4]:
        issues.append(f"Mask must have 2, 3, or 4 dimensions, got {tensor.dim()}")

    # Check value range (mask should be binary or probability)
    if tensor.min() < 0 or tensor.max() > 1.0:
        issues.append("Mask values should be in range [0, 1]")

    return len(issues) == 0, issues


def _validate_nodes(nodes: list[dict[str, Any]]) -> list[str]:
    """Validate workflow nodes."""
    errors = []

    required_node_fields = ["id", "type"]
    valid_node_types = [
        "USDZExporter",
        "AROptimizer",
        "SpatialPositioner",
        "MaterialComposer",
        "RealityComposer",
        "CrossPlatformExporter",
        "AnimationBuilder",
        "PhysicsIntegrator",
    ]

    for i, node in enumerate(nodes):
        # Check required fields
        for field in required_node_fields:
            if field not in node:
                errors.append(f"Node {i}: Missing required field '{field}'")

        # Check node type
        if "type" in node and node["type"] not in valid_node_types:
            errors.append(f"Node {i}: Invalid node type '{node['type']}'")

    return errors


def _validate_connections(connections: list[dict[str, Any]]) -> list[str]:
    """Validate workflow connections."""
    errors = []

    required_connection_fields = ["from_node", "to_node", "from_output", "to_input"]

    for i, connection in enumerate(connections):
        for field in required_connection_fields:
            if field not in connection:
                errors.append(f"Connection {i}: Missing required field '{field}'")

    return errors


def validate_ar_requirements(image: np.ndarray) -> tuple[bool, list[str]]:
    """Validate image meets AR requirements.

    Args:
        image: Input image array

    Returns:
        (meets_requirements, list_of_recommendations)
    """
    recommendations = []

    height, width = image.shape[:2]

    # Check aspect ratio
    aspect_ratio = width / height
    if not (0.5 <= aspect_ratio <= 2.0):
        recommendations.append("Extreme aspect ratios may not work well in AR")

    # Check resolution
    if max(height, width) < 512:
        recommendations.append("Low resolution images may appear pixelated in AR")

    if max(height, width) > 2048:
        recommendations.append("High resolution images may cause performance issues")

    # Check if square (preferred for AR stickers)
    if height != width:
        recommendations.append("Square images work best for AR stickers")

    return len(recommendations) == 0, recommendations
