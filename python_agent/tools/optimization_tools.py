#!/usr/bin/env python3
"""
Bin Packing Optimization Tools for OpenAI Agents SDK

This module provides standalone tools for 2D bin packing optimization and simulation
following OpenAI Agents SDK best practices. The tools use a file-based data passing
approach to avoid API payload limitations.

Architecture:
- optimize_bin_packing(): Runs Java genetic algorithm and saves results to file
- simulate_bin_packing(): Loads results from file and runs GUI simulation
- File-based data passing prevents large data structures from being sent through API
- Custom error handlers provide user-friendly error messages

The tools return simple strings instead of complex objects to ensure API compatibility.
"""
import json
import subprocess
import tempfile
import os
import threading
import time
from typing import Dict, Any, List, Optional, TypedDict
from agents import function_tool, RunContextWrapper
from simulation.gui import BinPackingSimulation
from utils.item_generator import generate_full_230_items, generate_standard_bins, print_item_distribution
from results_storage import save_optimization_result, load_optimization_result


class ItemsConfig(TypedDict, total=False):
    """Configuration for custom items and bins."""
    items: List[Dict[str, Any]]
    bins: List[Dict[str, Any]]




def optimization_error_handler(context: RunContextWrapper[Any], error: Exception) -> str:
    """Custom error handler for optimization tool failures."""
    print(f"Optimization tool failed: {error}")
    return f"Optimization failed: {str(error)}. Please check your Java environment and try again."


def simulation_error_handler(context: RunContextWrapper[Any], error: Exception) -> str:
    """Custom error handler for simulation tool failures."""
    print(f"Simulation tool failed: {error}")
    return f"Simulation failed: {str(error)}. Please check the result file and try again."


@function_tool(failure_error_function=optimization_error_handler, strict_mode=False)
def optimize_bin_packing(items_config: Optional[ItemsConfig] = None) -> str:
    """
    Run Java genetic algorithm optimization to find the best bin packing solution.
    
    This tool executes the Java genetic algorithm to optimize 2D bin packing.
    It can use either a custom configuration or the default 230-item setup.
    The results are saved to a file and metadata is returned.
    
    Args:
        items_config: Optional custom items and bins configuration. 
                     If None, uses the default 230 items configuration.
                     
    Returns:
        String containing the result file path for the simulation tool to use.
    """
    print("🔍 Running Java optimization...")
    
    # Use provided config or generate default
    if items_config:
        items = items_config.get('items', generate_full_230_items())
        bins = items_config.get('bins', generate_standard_bins())
    else:
        items = generate_full_230_items()
        bins = generate_standard_bins()
    
    print_item_distribution(items)
    
    input_data = {"items": items, "bins": bins}
    
    try:
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(input_data, temp_file, indent=2)
            temp_file_path = temp_file.name
        
        try:
            # Get the project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Run Java GA optimization
            cmd = [
                "mvn", "exec:java", 
                f"-Dexec.args=--input {temp_file_path} --headless"
            ]
            
            print(f"📦 Optimizing {len(items)} items...")
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                error_msg = f"Java optimization failed: {result.stderr}"
                print(f"❌ {error_msg}")
                raise RuntimeError(error_msg)
            
            # Parse JSON output
            output_lines = result.stdout.split('\n')
            json_start = -1
            json_end = -1
            
            # Find the first complete JSON object
            for i, line in enumerate(output_lines):
                if line.strip().startswith('{'):
                    json_start = i
                    break
            
            if json_start == -1:
                error_msg = "No JSON output found!"
                print(f"❌ {error_msg}")
                raise RuntimeError(error_msg)
            
            # Find where the JSON ends
            brace_count = 0
            for i in range(json_start, len(output_lines)):
                line = output_lines[i]
                for char in line:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                if json_end != -1:
                    break
            
            if json_end == -1:
                error_msg = "Incomplete JSON output found!"
                print(f"❌ {error_msg}")
                raise RuntimeError(error_msg)
            
            # Extract JSON part
            json_output = '\n'.join(output_lines[json_start:json_end])
            optimization_result = json.loads(json_output)
            
            print("✅ Optimization completed!")
            print(f"   Fitness: {optimization_result.get('fitness', 'N/A'):.2f}")
            print(f"   Packed Value: ${optimization_result.get('packed_value', 'N/A'):,.2f}")
            print(f"   Items Placed: {len(optimization_result.get('plan', []))}")
            
            # Save full result to file and return simplified metadata
            try:
                result_file_path = save_optimization_result(optimization_result)
                print(f"💾 Results saved to: {result_file_path}")
                
                # Return only the file path as a string
                return str(result_file_path)
            except Exception as e:
                print(f"⚠️ Warning: Could not save results to file: {e}")
                # Fallback to returning full result if file save fails
                raise RuntimeError(f"Failed to save optimization results: {e}")
            
        finally:
            os.unlink(temp_file_path)
            
    except Exception as e:
        error_msg = f"Error during optimization: {e}"
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg)


@function_tool(failure_error_function=simulation_error_handler, strict_mode=False)
def simulate_bin_packing(result_file_path: str) -> str:
    """
    Execute and visualize the packing plan in a GUI simulation.
    
    This tool loads the optimization results from a file and runs a step-by-step
    GUI simulation showing how items are placed in bins. The simulation provides
    visual feedback of the packing process.
    
    Args:
        result_file_path: Path to the JSON file containing the optimization result.
                         This file should be created by the optimize_bin_packing tool.
                         
    Returns:
        String message indicating simulation completion status.
    """
    if not result_file_path:
        raise ValueError("No result file path provided for simulation")
    
    # Load the full optimization result from file
    try:
        optimization_result = load_optimization_result(result_file_path)
        packing_plan = optimization_result.get('plan', [])
    except Exception as e:
        raise RuntimeError(f"Failed to load optimization result from {result_file_path}: {e}")
    
    if not packing_plan:
        raise ValueError("No packing plan found in optimization result")
    
    print("🎯 Starting simulation...")
    
    try:
        # Create simulation GUI
        sim = BinPackingSimulation()
        
        # Start simulation in a separate thread
        def run_simulation():
            for i, step in enumerate(packing_plan):
                print(f"Placing item {i+1}/{len(packing_plan)}: {step['item_type']} in Bin {step['bin_id']}")
                
                # Place the item
                result = sim.place_item(
                    step['item_id'],
                    step['bin_id'],
                    step['x'],
                    step['y'],
                    step['width'],
                    step['height'],
                    step['shape'],
                    step['item_type']
                )
                
                if "Error" in result:
                    print(f"   ❌ {result}")
                else:
                    print(f"   ✅ {result}")
                
                # Small delay for visual effect
                time.sleep(0.1)
            
            print("🎉 Simulation completed!")
        
        # Start simulation thread
        sim_thread = threading.Thread(target=run_simulation)
        sim_thread.daemon = True
        sim_thread.start()
        
        # Run GUI (this will block until window is closed)
        sim.run()
        
        return f"Simulation completed successfully! Executed {len(packing_plan)} placement steps."
        
    except Exception as e:
        error_msg = f"Error during simulation: {e}"
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg)
