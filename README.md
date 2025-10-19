# 2D Bin Packing Genetic Algorithm with AI Agent System

[![Java](https://img.shields.io/badge/Java-11+-orange.svg)](https://openjdk.java.net/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Maven](https://img.shields.io/badge/Maven-3.6+-red.svg)](https://maven.apache.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Agents-green.svg)](https://openai.github.io/openai-agents-python/)

A sophisticated 2D bin packing optimization system that combines a Java-based genetic algorithm with an AI-powered agent system for intelligent problem solving and visualization.

## 🚀 Key Features

- **Genetic Algorithm Optimization**: High-performance Java implementation using the Jenetics library
- **AI Agent Integration**: OpenAI Agents SDK for intelligent problem solving and automation
- **Real-time Visualization**: Interactive GUI simulation showing step-by-step item placement
- **File-based Architecture**: Efficient data passing to avoid API limitations
- **Multiple Item Types**: Support for rectangles, triangles, and circles with various sizes
- **Configurable Parameters**: Customizable population size, generations, and mutation rates

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Java GA       │    │  Python Agent    │    │  GUI Simulation │
│   (Jenetics)    │◄──►│  (OpenAI SDK)    │◄──►│   (Tkinter)     │
│                 │    │                  │    │                 │
│ • Optimization  │    │ • Tool Management│    │ • Visualization │
│ • Fitness Calc  │    │ • File Handling  │    │ • Real-time     │
│ • Chromosomes   │    │ • Error Handling │    │ • Interactive   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Results Storage │
                    │   (File-based)   │
                    │                 │
                    │ • JSON Files    │
                    │ • Temp Storage  │
                    │ • Data Passing  │
                    └─────────────────┘
```

### Component Interaction Flow

1. **Agent System** receives user request for bin packing optimization
2. **Optimization Tool** calls Java genetic algorithm with item configuration
3. **Java GA** processes optimization and saves results to JSON file
4. **File Storage** manages result persistence and data passing
5. **Simulation Tool** loads results and triggers GUI visualization
6. **GUI System** displays real-time step-by-step placement process

## 📁 Project Structure

```
GA_Assignment/
├── 📄 pom.xml                          # Maven configuration for Java GA
├── 📄 .gitignore                       # Git ignore rules (includes .env)
├── 📄 README.md                        # This documentation
│
├── 📁 src/main/java/                   # Java Genetic Algorithm
│   └── 📄 Code2.java                   # Main GA implementation
│
├── 📁 target/                          # Maven build output
│   └── 📁 classes/                     # Compiled Java classes
│
└── 📁 python_agent/                    # Python AI Agent System
    ├── 📄 __init__.py
    ├── 📄 agent_system.py              # Main agent orchestrator
    ├── 📄 agent_cli.py                 # Command-line interface
    ├── 📄 demo.py                      # Demo script
    ├── 📄 simple_simulation.py         # Standalone simulation
    ├── 📄 requirements.txt             # Python dependencies
    ├── 📄 .env.example                 # Environment template
    │
    ├── 📁 tools/                       # Agent Tools
    │   ├── 📄 __init__.py
    │   └── 📄 optimization_tools.py    # GA and simulation tools
    │
    ├── 📁 simulation/                  # GUI Simulation
    │   ├── 📄 __init__.py
    │   └── 📄 gui.py                   # Tkinter visualization
    │
    ├── 📁 utils/                       # Utilities
    │   ├── 📄 __init__.py
    │   └── 📄 item_generator.py        # Item generation logic
    │
    └── 📄 results_storage.py           # File-based data management
```

### Component Purposes

- **`Code2.java`**: Core genetic algorithm implementation using Jenetics library
- **`agent_system.py`**: Main orchestrator that manages AI agent and tool coordination
- **`optimization_tools.py`**: Standalone tools for GA execution and simulation
- **`gui.py`**: Interactive visualization system for real-time placement display
- **`item_generator.py`**: Item configuration and generation utilities
- **`results_storage.py`**: File-based data persistence to avoid API limitations

## 🔧 Prerequisites

### Java Requirements
- **JDK 11+** (OpenJDK or Oracle JDK)
- **Maven 3.6+** for dependency management
- **Git** for version control

### Python Requirements
- **Python 3.12+** with pip
- **Virtual Environment** (recommended)
- **OpenAI API Key** for agent functionality

### System Requirements
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: 500MB free space

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/JanithRavisanka/GA_Assignmnet.git
cd GA_Assignmnet
```

### 2. Java Setup

```bash
# Verify Java installation
java -version
javac -version

# Verify Maven installation
mvn -version

# Build the Java project
mvn clean compile
```

### 3. Python Setup

```bash
# Navigate to Python agent directory
cd python_agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your OpenAI API key
# OPENAI_API_KEY=your_actual_api_key_here
```

## 🚀 Usage Guide

### Running the Java Genetic Algorithm Standalone

```bash
# From project root
mvn exec:java -Dexec.args="--input input.json --headless"

# With custom input file
mvn exec:java -Dexec.args="--input my_items.json --headless"
```

### Running the Python Agent System

```bash
# From python_agent directory
cd python_agent

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Run the agent system
python agent_system.py
```

### Running the Simple Simulation

```bash
# From python_agent directory
python simple_simulation.py
```

### Command Line Interface

```bash
# Interactive CLI
python agent_cli.py

# Demo mode
python demo.py
```

## 🔬 Component Documentation

### Java Genetic Algorithm

**Technology**: Jenetics Library v7.2.0

**Key Features**:
- **Chromosome Encoding**: Integer-based representation of item-bin assignments
- **Fitness Function**: Multi-objective optimization (space utilization + value maximization)
- **Selection**: Tournament selection with elitism
- **Crossover**: Single-point crossover with repair mechanisms
- **Mutation**: Random mutation with constraint handling

**Configuration**:
- Population Size: 100 individuals
- Generations: 1000 iterations
- Mutation Rate: 0.1 (10%)
- Crossover Rate: 0.8 (80%)

### Python Agent System

**Technology**: OpenAI Agents SDK v0.4.0

**Architecture**:
- **Agent Orchestrator**: Manages tool coordination and workflow
- **Tool System**: Modular functions for specific tasks
- **File-based Data Passing**: Avoids API payload limitations
- **Error Handling**: Custom error handlers for user-friendly messages

**Tools**:
- `optimize_bin_packing()`: Executes Java GA and saves results
- `simulate_bin_packing()`: Loads results and triggers GUI simulation

### GUI Simulation

**Technology**: Tkinter (Python standard library)

**Features**:
- **Real-time Visualization**: Step-by-step item placement display
- **Interactive Controls**: Play/pause/speed controls
- **Multi-bin Support**: Visual representation of multiple bins
- **Item Types**: Different shapes and colors for various item types
- **Statistics Display**: Real-time fitness and utilization metrics

### Results Storage

**Purpose**: File-based data persistence to avoid API limitations

**Features**:
- **JSON Format**: Human-readable result storage
- **Temporary Files**: Automatic cleanup after processing
- **Metadata Extraction**: Lightweight data for API transmission
- **Error Handling**: Robust file operation management

## ⚙️ API & Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (with defaults)
JAVA_GA_TIMEOUT=300          # 5 minutes
SIMULATION_DELAY=0.1         # 100ms between steps
RESULTS_CLEANUP_HOURS=24     # Cleanup old results
```

### Input Format

```json
{
  "items": [
    {
      "id": 1,
      "type": "Rectangle A",
      "width": 25.0,
      "height": 30.0,
      "shape": "RECTANGLE",
      "price": 100.0
    }
  ],
  "bins": [
    {
      "id": 0,
      "width": 200.0,
      "height": 200.0
    }
  ]
}
```

### Output Format

```json
{
  "fitness": 22449.83,
  "packed_value": 22370.0,
  "unplaced_items": 111,
  "plan": [
    {
      "step": 1,
      "item_id": 146,
      "item_type": "Triangle Small",
      "bin_id": 0,
      "x": 0.0,
      "y": 0.0,
      "width": 30.0,
      "height": 30.0,
      "shape": "TRIANGLE"
    }
  ]
}
```

## 🔧 Troubleshooting

### Common Issues

**1. Java Compilation Errors**
```bash
# Solution: Ensure JDK 11+ is installed and JAVA_HOME is set
export JAVA_HOME=/path/to/jdk11
mvn clean compile
```

**2. Python Import Errors**
```bash
# Solution: Ensure virtual environment is activated and dependencies installed
source .venv/bin/activate
pip install -r requirements.txt
```

**3. OpenAI API Errors**
```bash
# Solution: Verify API key is set correctly
echo $OPENAI_API_KEY
# or check .env file
cat .env
```

**4. Maven Build Failures**
```bash
# Solution: Clean and rebuild
mvn clean
mvn compile
mvn package
```

### GitHub Secret Scanning Fix

If you encounter GitHub push protection due to exposed API keys:

```bash
# Remove sensitive files from git history
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch python_agent/.env' --prune-empty --tag-name-filter cat -- --all

# Force push cleaned history
git push --force-with-lease origin main

# Clean up local references
git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### API Key Management

**Best Practices**:
- Never commit `.env` files to version control
- Use `.env.example` as a template
- Rotate API keys regularly
- Use environment variables in production

## 💻 Development Notes

### Code Organization Principles

1. **Separation of Concerns**: Java handles optimization, Python handles AI and visualization
2. **Modular Design**: Each component has a specific responsibility
3. **File-based Communication**: Avoids API payload limitations
4. **Error Handling**: Comprehensive error management throughout
5. **Documentation**: Extensive inline and external documentation

### Best Practices Followed

- **OpenAI Agents SDK**: Following official best practices for tool configuration
- **Type Safety**: Proper type hints and TypedDict usage
- **Error Handling**: Custom error handlers for user-friendly messages
- **Security**: Proper API key management and git ignore rules
- **Performance**: Efficient file-based data passing

### Future Improvements

- **Web Interface**: Browser-based GUI for remote access
- **Database Integration**: Persistent storage for optimization results
- **Advanced Algorithms**: Additional optimization techniques (simulated annealing, particle swarm)
- **Real-time Collaboration**: Multi-user optimization sessions
- **Cloud Deployment**: Containerized deployment with Docker
- **Machine Learning**: AI-powered parameter tuning

## 📊 Performance Metrics

### Optimization Results (230 Items)
- **Typical Fitness**: 22,000-23,000
- **Packed Value**: $22,000-$23,000
- **Items Placed**: 110-125 items
- **Execution Time**: 2-5 minutes
- **Memory Usage**: <500MB

### System Requirements
- **Java Heap**: 1GB recommended
- **Python Memory**: 256MB for agent system
- **Disk Space**: 50MB for temporary files
- **Network**: Required for OpenAI API calls

## 📄 License & Credits

### Project Information
- **Author**: Janith Ravisanka
- **Course**: L3S2 Evolutionary Computing
- **Institution**: University Assignment
- **Year**: 2025

### Dependencies & Attribution

**Java Dependencies**:
- [Jenetics](https://jenetics.io/) v7.2.0 - Genetic algorithm library
- [Gson](https://github.com/google/gson) v2.10.1 - JSON processing

**Python Dependencies**:
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) v0.4.0 - AI agent framework
- [Pydantic](https://pydantic.dev/) v2.0.0+ - Data validation

**Built-in Libraries**:
- Tkinter - GUI framework
- JSON - Data serialization
- Subprocess - Java process management
- Threading - Concurrent execution

### Acknowledgments

- **OpenAI**: For providing the Agents SDK and API
- **Jenetics Team**: For the excellent genetic algorithm library
- **Python Community**: For comprehensive documentation and tools
- **Maven Community**: For robust dependency management

---

## 🤝 Contributing

This is an academic project, but suggestions and improvements are welcome! Please ensure any contributions maintain the educational focus and code quality standards.

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the component documentation
3. Examine the example configurations
4. Check GitHub issues (if applicable)

---

**Happy Optimizing! 🎯**
