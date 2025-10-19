#!/usr/bin/env python3
"""
Results storage system for optimization outputs
"""
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional


def save_optimization_result(result: Dict[str, Any], filename: Optional[str] = None) -> str:
    """
    Save optimization result to a JSON file.
    
    Args:
        result: The optimization result dictionary to save
        filename: Optional custom filename. If None, generates timestamped filename.
        
    Returns:
        Path to the saved file
        
    Raises:
        IOError: If file cannot be written
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"optimization_result_{timestamp}.json"
    
    # Use temp directory for results
    results_dir = os.path.join(tempfile.gettempdir(), "bin_packing_results")
    os.makedirs(results_dir, exist_ok=True)
    
    file_path = os.path.join(results_dir, filename)
    
    try:
        with open(file_path, 'w') as f:
            json.dump(result, f, indent=2)
        return file_path
    except Exception as e:
        raise IOError(f"Failed to save optimization result to {file_path}: {e}")


def load_optimization_result(file_path: str) -> Dict[str, Any]:
    """
    Load optimization result from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing the optimization result
        
    Returns:
        The optimization result dictionary
        
    Raises:
        IOError: If file cannot be read
        json.JSONDecodeError: If file contains invalid JSON
    """
    if not os.path.exists(file_path):
        raise IOError(f"Optimization result file not found: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            result = json.load(f)
        return result
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in optimization result file {file_path}: {e}")
    except Exception as e:
        raise IOError(f"Failed to load optimization result from {file_path}: {e}")


def cleanup_old_results(max_age_hours: int = 24) -> int:
    """
    Clean up old optimization result files.
    
    Args:
        max_age_hours: Maximum age of files to keep (in hours)
        
    Returns:
        Number of files cleaned up
    """
    results_dir = os.path.join(tempfile.gettempdir(), "bin_packing_results")
    
    if not os.path.exists(results_dir):
        return 0
    
    current_time = datetime.now().timestamp()
    max_age_seconds = max_age_hours * 3600
    cleaned_count = 0
    
    try:
        for filename in os.listdir(results_dir):
            if filename.startswith("optimization_result_") and filename.endswith(".json"):
                file_path = os.path.join(results_dir, filename)
                file_age = current_time - os.path.getmtime(file_path)
                
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    cleaned_count += 1
    except Exception:
        # Ignore cleanup errors
        pass
    
    return cleaned_count
