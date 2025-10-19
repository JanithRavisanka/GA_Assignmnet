#!/usr/bin/env python3
"""
Agent-based bin packing optimization and simulation system
"""
from agents import Agent, Runner
from tools.optimization_tools import optimize_bin_packing, simulate_bin_packing


class BinPackingAgent:
    """Main agent for bin packing optimization and simulation"""
    
    def __init__(self):
        self.agent = Agent(
            name="BinPackingOptimizer",
            instructions="""You are a specialized agent for 2D bin packing optimization and simulation. 
            You have two main capabilities:
            1. Run genetic algorithm optimization to find the best packing plan
            2. Execute and visualize the packing plan in a GUI simulation
            
            When given a bin packing problem, you should:
            1. First run the optimization to get the best packing plan (this saves results to a file)
            2. Then execute the simulation using the result file path from step 1
            
            IMPORTANT: The optimization tool saves results to a file and returns a file path. 
            You must pass this file path to the simulation tool, not the raw data.
            
            Always provide clear feedback about what you're doing and the results.""",
            model="gpt-4o-mini"
        )
        
        # Add tools to the agent
        self.agent.tools = [
            optimize_bin_packing,
            simulate_bin_packing
        ]
    
    
    def run(self, user_input: str) -> str:
        """Run the agent with user input"""
        print(f"Running agent with input: {user_input}")
        result = Runner.run_sync(self.agent, user_input)
        return result.final_output


def main():
    """Main function to run the agent system"""
    print("🚀 Bin Packing Agent System")
    print("=" * 50)
    
    # Create and run the agent
    agent_system = BinPackingAgent()
    
    # Example usage - you can modify this or make it interactive
    user_request = """
    Please optimize the bin packing problem and then simulate the results. 
    Use the default 230 items configuration and show me the step-by-step placement process.
    """
    
    print("🤖 Agent processing request...")
    result = agent_system.run(user_request)
    print("\n" + "=" * 50)
    print("🤖 Agent Response:")
    print(result)


if __name__ == "__main__":
    main()
