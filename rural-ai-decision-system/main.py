#!/usr/bin/env python3
"""
Main Entry Point for Rural Agriculture Decision Support System.

This is the primary entry point for the agriculture decision support system.
It provides access to the interactive CLI interface and demo mode for testing.

Usage:
    python main.py              # Run interactive CLI
    python main.py --demo       # Run demo with sample data
    python main.py --help       # Show help information

Author: Agriculture Decision Support System
Version: 1.0
"""

import sys
import os
import json
import argparse

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_welcome():
    """Print welcome message and system information."""
    print("=" * 70)
    print("    RURAL AGRICULTURE DECISION SUPPORT SYSTEM")
    print("    Version 1.0 - Offline Agriculture Advisory Tool")
    print("=" * 70)
    print()
    print("This system helps farmers make informed decisions about:")
    print("• Crop yield predictions")
    print("• Disease risk assessment") 
    print("• Irrigation optimization")
    print("• Overall farming risk evaluation")
    print()
    print("Designed for offline use in rural areas.")
    print()


def run_interactive_mode():
    """Run the interactive CLI interface."""
    try:
        print("Starting interactive mode...")
        print("You will be asked questions about your farming conditions.")
        print()
        
        # Import and run CLI app
        from ui.cli_app import main as cli_main
        cli_main()
        
    except ImportError as e:
        print(f"Error: Could not load CLI interface - {e}")
        print("Please ensure all system files are present.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running interactive mode: {e}")
        sys.exit(1)


def run_demo_mode():
    """Run demo mode using sample data."""
    try:
        print("Starting demo mode...")
        print("Using sample farming scenarios from data/sample_inputs.json")
        print()
        
        # Load sample data
        sample_file = os.path.join(os.path.dirname(__file__), 'data', 'sample_inputs.json')
        
        if not os.path.exists(sample_file):
            print(f"Error: Sample data file not found at {sample_file}")
            print("Please ensure the data/sample_inputs.json file exists.")
            sys.exit(1)
        
        with open(sample_file, 'r') as f:
            sample_data = json.load(f)
        
        # Import decision engine
        from api.decision_engine import run_decision_engine
        
        # Run demo scenarios
        scenarios = sample_data.get('sample_scenarios', [])
        special_scenarios = [
            ('Drought Scenario', sample_data.get('drought_scenario')),
            ('Flood Scenario', sample_data.get('flood_scenario')),
            ('Optimal Scenario', sample_data.get('optimal_scenario'))
        ]
        
        print(f"Running {len(scenarios)} sample scenarios plus 3 special scenarios...")
        print("=" * 50)
        
        # Process first 3 regular scenarios
        for i, scenario in enumerate(scenarios[:3], 1):
            print(f"\nDEMO SCENARIO {i}:")
            print(f"Farmer: {scenario.get('farmer_id', 'Unknown')}")
            print(f"Region: {scenario.get('region', 'Unknown')}")
            print(f"Crop: {scenario.get('crop_type', 'Unknown').title()}")
            print(f"Conditions: {scenario.get('temperature_c', 0)}°C, {scenario.get('rainfall_mm', 0)}mm rain")
            print("-" * 30)
            
            # Run decision engine
            result = run_decision_engine(scenario)
            
            # Display key results
            decision = result.get('final_decision', 'UNKNOWN')
            risk_level = result.get('overall_risk_level', 'UNKNOWN')
            yield_pct = result.get('yield_summary', {}).get('expected_yield_percentage', 0)
            
            print(f"RECOMMENDATION: {decision.replace('_', ' ')}")
            print(f"RISK LEVEL: {risk_level}")
            print(f"EXPECTED YIELD: {yield_pct:.0f}%")
            
            # Show top 2 recommendations
            recommendations = result.get('recommendations', [])
            if recommendations:
                print("KEY RECOMMENDATIONS:")
                for j, rec in enumerate(recommendations[:2], 1):
                    print(f"  {j}. {rec}")
            
            print()
        
        # Process special scenarios
        for scenario_name, scenario_data in special_scenarios:
            if scenario_data:
                print(f"\n{scenario_name.upper()}:")
                print(f"Conditions: {scenario_data.get('temperature_c', 0)}°C, {scenario_data.get('rainfall_mm', 0)}mm rain")
                print("-" * 30)
                
                result = run_decision_engine(scenario_data)
                decision = result.get('final_decision', 'UNKNOWN')
                risk_level = result.get('overall_risk_level', 'UNKNOWN')
                
                print(f"RECOMMENDATION: {decision.replace('_', ' ')}")
                print(f"RISK LEVEL: {risk_level}")
                print()
        
        print("=" * 50)
        print("Demo completed successfully!")
        print("To run interactive mode, use: python main.py")
        print()
        
    except FileNotFoundError:
        print("Error: Sample data file not found.")
        print("Please ensure data/sample_inputs.json exists.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in sample data file.")
        sys.exit(1)
    except ImportError as e:
        print(f"Error: Could not load decision engine - {e}")
        print("Please ensure all system files are present.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running demo: {e}")
        sys.exit(1)


def show_help():
    """Show help information."""
    print("USAGE:")
    print("  python main.py              Run interactive CLI interface")
    print("  python main.py --demo       Run demo with sample data")
    print("  python main.py --help       Show this help message")
    print()
    print("INTERACTIVE MODE:")
    print("  - Prompts you for farming conditions")
    print("  - Provides personalized recommendations")
    print("  - Suitable for real farming decisions")
    print()
    print("DEMO MODE:")
    print("  - Uses pre-loaded sample scenarios")
    print("  - Shows system capabilities")
    print("  - Good for testing and training")
    print()
    print("SYSTEM REQUIREMENTS:")
    print("  - Python 3.6 or higher")
    print("  - No internet connection required")
    print("  - All system files must be present")
    print()


def main():
    """Main entry point function."""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description='Rural Agriculture Decision Support System',
            add_help=False  # We'll handle help ourselves
        )
        parser.add_argument('--demo', action='store_true', 
                          help='Run demo mode with sample data')
        parser.add_argument('--help', '-h', action='store_true',
                          help='Show help information')
        
        args = parser.parse_args()
        
        # Print welcome message
        print_welcome()
        
        # Handle different modes
        if args.help:
            show_help()
        elif args.demo:
            run_demo_mode()
        else:
            run_interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        print("Goodbye!")
    except SystemExit:
        # Re-raise SystemExit to preserve exit codes
        raise
    except Exception as e:
        print(f"\nCritical system error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure all system files are present")
        print("2. Check that Python 3.6+ is installed")
        print("3. Verify file permissions")
        print("4. Contact technical support if problem persists")
        sys.exit(1)


if __name__ == "__main__":
    main()