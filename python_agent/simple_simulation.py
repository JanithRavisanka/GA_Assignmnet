#!/usr/bin/env python3
"""
Simple simulation that runs optimization and shows GUI
"""
import json
import subprocess
import tempfile
import os
import threading
import time
from simulation.gui import BinPackingSimulation
from utils.item_generator import generate_full_230_items, generate_standard_bins, print_item_distribution


def run_optimization():
    """Run Java optimization and return results"""
    print("🔍 Running Java optimization...")
    
    # Generate the full item configuration (230 items total)
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
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
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
                print(f"❌ Java optimization failed: {result.stderr}")
                return None
            
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
                print("❌ No JSON output found!")
                return None
            
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
                print("❌ Incomplete JSON output found!")
                return None
            
            # Extract JSON part
            json_output = '\n'.join(output_lines[json_start:json_end])
            optimization_result = json.loads(json_output)
            
            print("✅ Optimization completed!")
            print(f"   Fitness: {optimization_result.get('fitness', 'N/A'):.2f}")
            print(f"   Packed Value: ${optimization_result.get('packed_value', 'N/A'):,.2f}")
            print(f"   Items Placed: {len(optimization_result.get('plan', []))}")
            
            return optimization_result
            
        finally:
            os.unlink(temp_file_path)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def simulate_placement(sim, plan):
    """Simulate placing items in the GUI"""
    print("🎯 Starting simulation...")
    
    for i, step in enumerate(plan):
        print(f"Placing item {i+1}/{len(plan)}: {step['item_type']} in Bin {step['bin_id']}")
        
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


def main():
    """Main simulation function"""
    print("🚀 Java GA + Python Simulation")
    print("=" * 50)
    
    # Run optimization
    result = run_optimization()
    if not result:
        print("❌ Optimization failed!")
        return
    
    # Create simulation GUI
    print("📱 Opening simulation GUI...")
    sim = BinPackingSimulation()
    
    # Start simulation in a separate thread
    plan = result.get('plan', [])
    if plan:
        print(f"📋 Executing {len(plan)} placement steps...")
        
        # Start simulation thread
        sim_thread = threading.Thread(target=lambda: simulate_placement(sim, plan))
        sim_thread.daemon = True
        sim_thread.start()
    
    # Run GUI (this will block until window is closed)
    sim.run()


if __name__ == "__main__":
    main()
