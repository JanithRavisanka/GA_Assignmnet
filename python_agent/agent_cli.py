#!/usr/bin/env python3
"""
Interactive CLI for the Bin Packing Agent System
"""
import os
import sys
from agent_system import BinPackingAgent


def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🤖 BIN PACKING AGENT SYSTEM")
    print("=" * 60)
    print("This agent can:")
    print("  • Run genetic algorithm optimization")
    print("  • Simulate packing plans in GUI")
    print("  • Handle custom item configurations")
    print("=" * 60)


def print_menu():
    """Print available options"""
    print("\n📋 Available Commands:")
    print("  1. Optimize and simulate (default 230 items)")
    print("  2. Optimize only (no simulation)")
    print("  3. Simulate existing plan")
    print("  4. Custom optimization")
    print("  5. Help")
    print("  6. Exit")
    print()


def get_user_choice():
    """Get user choice"""
    while True:
        try:
            choice = input("Enter your choice (1-6): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6']:
                return choice
            else:
                print("❌ Invalid choice. Please enter 1-6.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)


def run_optimization_and_simulation(agent):
    """Run full optimization and simulation"""
    print("\n🚀 Running full optimization and simulation...")
    request = """
    Please optimize the bin packing problem using the default 230 items configuration 
    and then simulate the results in the GUI. Show me the step-by-step placement process.
    """
    result = agent.run(request)
    print(f"\n🤖 Agent Response:\n{result}")


def run_optimization_only(agent):
    """Run optimization only"""
    print("\n🔍 Running optimization only...")
    request = """
    Please optimize the bin packing problem using the default 230 items configuration. 
    Don't run the simulation, just provide the optimization results.
    """
    result = agent.run(request)
    print(f"\n🤖 Agent Response:\n{result}")


def run_simulation_only(agent):
    """Run simulation with existing plan"""
    print("\n🎯 Running simulation only...")
    print("Note: This requires a previously generated packing plan.")
    request = """
    I have a packing plan that I want to simulate. Please help me run the simulation 
    with the existing plan. If you don't have a plan, please run optimization first.
    """
    result = agent.run(request)
    print(f"\n🤖 Agent Response:\n{result}")


def run_custom_optimization(agent):
    """Run custom optimization"""
    print("\n⚙️ Custom optimization...")
    print("Available options:")
    print("  a. Different number of items")
    print("  b. Custom item types")
    print("  c. Different bin sizes")
    print("  d. Custom request")
    
    sub_choice = input("Choose option (a-d): ").strip().lower()
    
    if sub_choice == 'a':
        num_items = input("Enter number of items (default 230): ").strip()
        request = f"""
        Please optimize the bin packing problem with {num_items} items. 
        Generate the appropriate number of items and run optimization.
        """
    elif sub_choice == 'b':
        request = """
        Please create a custom item configuration with different types of items 
        (rectangles, triangles, circles) and run optimization.
        """
    elif sub_choice == 'c':
        request = """
        Please create custom bin sizes and run optimization with the default items.
        """
    elif sub_choice == 'd':
        custom_request = input("Enter your custom request: ")
        request = f"Please {custom_request}"
    else:
        print("❌ Invalid choice. Using default optimization.")
        request = "Please optimize the bin packing problem with default settings."
    
    result = agent.run(request)
    print(f"\n🤖 Agent Response:\n{result}")


def show_help():
    """Show help information"""
    print("\n📖 HELP")
    print("=" * 40)
    print("This agent system uses OpenAI's Agents SDK to provide intelligent")
    print("bin packing optimization and simulation capabilities.")
    print("\nThe agent has two main tools:")
    print("  1. optimize_packing: Runs Java genetic algorithm optimization")
    print("  2. simulate_packing: Executes and visualizes packing plans")
    print("\nThe agent can:")
    print("  • Automatically choose the best approach for your request")
    print("  • Handle complex multi-step workflows")
    print("  • Provide detailed feedback and results")
    print("  • Adapt to different problem configurations")
    print("\nMake sure you have:")
    print("  • OPENAI_API_KEY environment variable set")
    print("  • Java and Maven installed for optimization")
    print("  • All dependencies installed (pip install -r requirements.txt)")


def main():
    """Main CLI function"""
    print_banner()
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Create agent
    try:
        print("🤖 Initializing agent...")
        agent = BinPackingAgent()
        print("✅ Agent ready!")
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        sys.exit(1)
    
    # Main loop
    while True:
        print_menu()
        choice = get_user_choice()
        
        if choice == '1':
            run_optimization_and_simulation(agent)
        elif choice == '2':
            run_optimization_only(agent)
        elif choice == '3':
            run_simulation_only(agent)
        elif choice == '4':
            run_custom_optimization(agent)
        elif choice == '5':
            show_help()
        elif choice == '6':
            print("👋 Goodbye!")
            break
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
