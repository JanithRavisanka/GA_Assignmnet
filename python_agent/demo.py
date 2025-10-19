#!/usr/bin/env python3
"""
Quick demo of the Bin Packing Agent System
"""
import os
from agent_system import BinPackingAgent


def main():
    """Run a quick demo"""
    print("🚀 Bin Packing Agent Demo")
    print("=" * 40)
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY=your_api_key_here")
        return
    
    print("🤖 Creating agent...")
    agent = BinPackingAgent()
    
    print("📝 Sending request to agent...")
    request = """
    Please run a quick bin packing optimization with a smaller set of items 
    (around 20-30 items) and then show me the simulation. I want to see 
    how the genetic algorithm works and watch the items being placed.
    """
    
    print("⏳ Agent is processing...")
    result = agent.run(request)
    
    print("\n" + "=" * 40)
    print("🤖 Agent Response:")
    print("=" * 40)
    print(result)


if __name__ == "__main__":
    main()
