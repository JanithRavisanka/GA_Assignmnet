import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class PlacedItem:
    item_id: int
    item_type: str
    bin_id: int
    x: float
    y: float
    width: float
    height: float
    shape: str


class BinPackingSimulation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("2D Bin Packing Simulation")
        self.root.geometry("1200x800")
        
        # Simulation state
        self.bins = {
            0: {"width": 220, "height": 220, "items": []},
            1: {"width": 180, "height": 200, "items": []},
            2: {"width": 200, "height": 180, "items": []},
            3: {"width": 160, "height": 160, "items": []}
        }
        
        # Color mapping for item types
        self.colors = {
            "Rectangle A": "#FF6347",  # Red
            "Rectangle B": "#6495ED",  # Blue
            "Rectangle C": "#90EE90",  # Green
            "Rectangle D": "#FFA500",  # Orange
            "Triangle Small": "#9370DB",  # Purple
            "Triangle Large": "#FFB6C1",  # Pink
            "Circle Small": "#FFD700",  # Gold
            "Circle Medium": "#40E0D0"   # Turquoise
        }
        
        # Command queue for thread-safe communication
        self.command_queue = queue.Queue()
        
        self.setup_ui()
        self.setup_command_processor()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="2D Bin Packing Simulation", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Canvas frame
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg="white", width=1000, height=600)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_text = tk.Text(stats_frame, height=6, width=80, font=("Courier", 10))
        self.stats_text.pack(fill=tk.X)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Reset Simulation", 
                  command=self.reset_simulation).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Get State", 
                  command=self.print_state).pack(side=tk.LEFT)
        
        # Draw initial bins
        self.draw_bins()
        
    def setup_command_processor(self):
        """Set up command processing for thread-safe updates"""
        def process_commands():
            try:
                while True:
                    command = self.command_queue.get(timeout=0.1)
                    if command is None:
                        break
                    self.execute_command(command)
            except queue.Empty:
                pass
            # Schedule next check
            self.root.after(100, process_commands)
        
        process_commands()
    
    def execute_command(self, command: Dict[str, Any]):
        """Execute a command from the queue"""
        cmd_type = command.get("type")
        
        if cmd_type == "place_item":
            self.place_item_sync(
                command["item_id"],
                command["bin_id"],
                command["x"],
                command["y"],
                command["width"],
                command["height"],
                command["shape"],
                command["item_type"]
            )
        elif cmd_type == "reset":
            self.reset_simulation_sync()
        elif cmd_type == "update_stats":
            self.update_stats_sync()
    
    def draw_bins(self):
        """Draw the bin boundaries"""
        self.canvas.delete("all")
        
        scale = 2
        padding = 20
        bin_spacing = 20
        
        x_offset = padding
        for bin_id, bin_data in self.bins.items():
            x1 = x_offset
            y1 = padding
            x2 = x1 + bin_data["width"] * scale
            y2 = y1 + bin_data["height"] * scale
            
            # Draw bin boundary
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", width=2, fill="lightgray")
            
            # Draw bin label
            self.canvas.create_text(x1 + 5, y1 + 5, text=f"Bin {bin_id}", 
                                  anchor="nw", font=("Arial", 10, "bold"))
            
            # Draw items in this bin
            for item in bin_data["items"]:
                self.draw_item(item, x_offset, padding, scale)
            
            x_offset += bin_data["width"] * scale + bin_spacing
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def draw_item(self, item: PlacedItem, bin_x_offset: float, bin_y_offset: float, scale: float):
        """Draw an item in the canvas"""
        x1 = bin_x_offset + item.x * scale
        y1 = bin_y_offset + item.y * scale
        x2 = x1 + item.width * scale
        y2 = y1 + item.height * scale
        
        color = self.colors.get(item.item_type, "gray")
        
        if item.shape == "RECTANGLE":
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=1)
        elif item.shape == "CIRCLE":
            # Draw circle using oval
            diameter = min(item.width, item.height) * scale
            self.canvas.create_oval(x1, y1, x1 + diameter, y1 + diameter, 
                                  fill=color, outline="black", width=1)
        elif item.shape == "TRIANGLE":
            # Draw triangle
            points = [
                x1, y2,  # bottom left
                x2, y2,  # bottom right
                x1 + (x2 - x1) // 2, y1  # top center
            ]
            self.canvas.create_polygon(points, fill=color, outline="black", width=1)
        
        # Draw item ID
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        self.canvas.create_text(center_x, center_y, text=str(item.item_id), 
                              font=("Arial", 8, "bold"), fill="white")
    
    def place_item(self, item_id: int, bin_id: int, x: float, y: float, 
                   width: float, height: float, shape: str, item_type: str = "Unknown") -> str:
        """Place an item in the simulation (thread-safe)"""
        command = {
            "type": "place_item",
            "item_id": item_id,
            "bin_id": bin_id,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "shape": shape,
            "item_type": item_type
        }
        self.command_queue.put(command)
        return f"Placed item {item_id} in bin {bin_id} at ({x}, {y})"
    
    def place_item_sync(self, item_id: int, bin_id: int, x: float, y: float, 
                       width: float, height: float, shape: str, item_type: str):
        """Place an item synchronously (called from main thread)"""
        if bin_id not in self.bins:
            return f"Error: Bin {bin_id} does not exist"
        
        # Check if item fits in bin
        bin_data = self.bins[bin_id]
        if x + width > bin_data["width"] or y + height > bin_data["height"]:
            return f"Error: Item {item_id} does not fit in bin {bin_id}"
        
        # Check for overlaps
        new_item = PlacedItem(item_id, item_type, bin_id, x, y, width, height, shape)
        for existing_item in bin_data["items"]:
            if self.items_overlap(new_item, existing_item):
                return f"Error: Item {item_id} overlaps with existing item {existing_item.item_id}"
        
        # Add item to bin
        bin_data["items"].append(new_item)
        
        # Redraw canvas
        self.draw_bins()
        self.update_stats_sync()
        
        return f"Successfully placed item {item_id} in bin {bin_id}"
    
    def items_overlap(self, item1: PlacedItem, item2: PlacedItem) -> bool:
        """Check if two items overlap"""
        return not (item1.x + item1.width <= item2.x or 
                   item2.x + item2.width <= item1.x or
                   item1.y + item1.height <= item2.y or 
                   item2.y + item2.height <= item1.y)
    
    def reset_simulation(self) -> str:
        """Reset the simulation (thread-safe)"""
        command = {"type": "reset"}
        self.command_queue.put(command)
        return "Simulation reset"
    
    def reset_simulation_sync(self):
        """Reset simulation synchronously"""
        for bin_data in self.bins.values():
            bin_data["items"].clear()
        self.draw_bins()
        self.update_stats_sync()
    
    def get_simulation_state(self) -> Dict[str, Any]:
        """Get current simulation state"""
        state = {
            "bins": {},
            "total_items": 0,
            "total_utilization": 0.0
        }
        
        for bin_id, bin_data in self.bins.items():
            items = bin_data["items"]
            used_area = sum(item.width * item.height for item in items)
            total_area = bin_data["width"] * bin_data["height"]
            utilization = (used_area / total_area * 100) if total_area > 0 else 0
            
            state["bins"][bin_id] = {
                "width": bin_data["width"],
                "height": bin_data["height"],
                "items": [
                    {
                        "item_id": item.item_id,
                        "item_type": item.item_type,
                        "x": item.x,
                        "y": item.y,
                        "width": item.width,
                        "height": item.height,
                        "shape": item.shape
                    }
                    for item in items
                ],
                "utilization": utilization
            }
            state["total_items"] += len(items)
            state["total_utilization"] += utilization
        
        state["total_utilization"] /= len(self.bins)
        return state
    
    def update_stats_sync(self):
        """Update statistics display"""
        state = self.get_simulation_state()
        
        stats_text = "SIMULATION STATISTICS\n"
        stats_text += "=" * 50 + "\n\n"
        
        for bin_id, bin_data in state["bins"].items():
            stats_text += f"Bin {bin_id} ({bin_data['width']}x{bin_data['height']}):\n"
            stats_text += f"  Items: {len(bin_data['items'])}\n"
            stats_text += f"  Utilization: {bin_data['utilization']:.1f}%\n"
            stats_text += f"  Item types: {', '.join(set(item['item_type'] for item in bin_data['items']))}\n\n"
        
        stats_text += f"Total Items: {state['total_items']}\n"
        stats_text += f"Average Utilization: {state['total_utilization']:.1f}%\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def print_state(self):
        """Print current state to console"""
        state = self.get_simulation_state()
        print("Current Simulation State:")
        print(json.dumps(state, indent=2))
    
    def run(self):
        """Start the simulation GUI"""
        self.root.mainloop()
    
    def close(self):
        """Close the simulation"""
        self.root.quit()


# Global simulation instance
_simulation_instance: Optional[BinPackingSimulation] = None


def get_simulation() -> BinPackingSimulation:
    """Get the global simulation instance"""
    global _simulation_instance
    if _simulation_instance is None:
        _simulation_instance = BinPackingSimulation()
    return _simulation_instance


def start_simulation():
    """Start the simulation in a separate thread"""
    def run_simulation():
        sim = get_simulation()
        sim.run()
    
    thread = threading.Thread(target=run_simulation, daemon=True)
    thread.start()
    return thread
