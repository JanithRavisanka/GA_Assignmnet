#!/usr/bin/env python3
"""
Utility functions for generating item configurations
"""
from typing import List, Dict, Any


def generate_full_230_items() -> List[Dict[str, Any]]:
    """
    Generate the complete 230-item configuration matching the Java code.
    
    Returns:
        List of 230 items with all types and sizes from the Java configuration
    """
    items = []
    item_id_counter = 0
    
    # Rectangles
    for i in range(15):
        items.append({
            "id": item_id_counter, 
            "type": "Rectangle A", 
            "width": 50, 
            "height": 50, 
            "shape": "RECTANGLE", 
            "price": 100
        })
        item_id_counter += 1
    
    for i in range(25):
        items.append({
            "id": item_id_counter, 
            "type": "Rectangle B", 
            "width": 35, 
            "height": 45, 
            "shape": "RECTANGLE", 
            "price": 150
        })
        item_id_counter += 1
    
    for i in range(40):
        items.append({
            "id": item_id_counter, 
            "type": "Rectangle C", 
            "width": 25, 
            "height": 30, 
            "shape": "RECTANGLE", 
            "price": 70
        })
        item_id_counter += 1
    
    for i in range(60):
        items.append({
            "id": item_id_counter, 
            "type": "Rectangle D", 
            "width": 30, 
            "height": 40, 
            "shape": "RECTANGLE", 
            "price": 300
        })
        item_id_counter += 1
    
    # Triangles
    for i in range(30):
        items.append({
            "id": item_id_counter, 
            "type": "Triangle Small", 
            "width": 30, 
            "height": 30, 
            "shape": "TRIANGLE", 
            "price": 120
        })
        item_id_counter += 1
    
    for i in range(20):
        items.append({
            "id": item_id_counter, 
            "type": "Triangle Large", 
            "width": 45, 
            "height": 45, 
            "shape": "TRIANGLE", 
            "price": 180
        })
        item_id_counter += 1
    
    # Circles
    for i in range(25):
        items.append({
            "id": item_id_counter, 
            "type": "Circle Small", 
            "width": 30, 
            "height": 30, 
            "shape": "CIRCLE", 
            "price": 90
        })
        item_id_counter += 1
    
    for i in range(15):
        items.append({
            "id": item_id_counter, 
            "type": "Circle Medium", 
            "width": 40, 
            "height": 40, 
            "shape": "CIRCLE", 
            "price": 200
        })
        item_id_counter += 1
    
    return items


def generate_standard_bins() -> List[Dict[str, Any]]:
    """
    Generate the standard 4-bin configuration.
    
    Returns:
        List of 4 bins with standard sizes
    """
    return [
        {"id": 0, "width": 220, "height": 220},
        {"id": 1, "width": 180, "height": 200},
        {"id": 2, "width": 200, "height": 180},
        {"id": 3, "width": 160, "height": 160}
    ]


def generate_sample_items() -> List[Dict[str, Any]]:
    """
    Generate a small sample of items for quick testing.
    
    Returns:
        List of 6 items representing different types
    """
    return [
        {"id": 0, "type": "Rectangle A", "width": 50, "height": 50, "shape": "RECTANGLE", "price": 100},
        {"id": 1, "type": "Rectangle A", "width": 50, "height": 50, "shape": "RECTANGLE", "price": 100},
        {"id": 2, "type": "Rectangle B", "width": 35, "height": 45, "shape": "RECTANGLE", "price": 150},
        {"id": 3, "type": "Circle Small", "width": 30, "height": 30, "shape": "CIRCLE", "price": 90},
        {"id": 4, "type": "Triangle Small", "width": 30, "height": 30, "shape": "TRIANGLE", "price": 120},
        {"id": 5, "type": "Circle Medium", "width": 40, "height": 40, "shape": "CIRCLE", "price": 200}
    ]


def print_item_distribution(items: List[Dict[str, Any]]) -> None:
    """
    Print a summary of item distribution.
    
    Args:
        items: List of items to analyze
    """
    item_counts = {}
    total_value = 0
    
    for item in items:
        item_type = item['type']
        item_counts[item_type] = item_counts.get(item_type, 0) + 1
        total_value += item['price']
    
    print(f"📦 Total Items: {len(items)}")
    print("📊 Item Distribution:")
    for item_type, count in item_counts.items():
        print(f"   {item_type}: {count} items")
    print(f"💰 Total Value: ${total_value:,.2f}")


if __name__ == "__main__":
    # Test the functions
    print("Testing item generation functions...")
    
    print("\n1. Sample items (6 items):")
    sample_items = generate_sample_items()
    print_item_distribution(sample_items)
    
    print("\n2. Full 230 items:")
    full_items = generate_full_230_items()
    print_item_distribution(full_items)
    
    print("\n3. Standard bins:")
    bins = generate_standard_bins()
    bin_sizes = [f"{b['width']}×{b['height']}" for b in bins]
    print(f"   {len(bins)} bins: {bin_sizes}")
