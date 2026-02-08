#!/usr/bin/env python3
"""
Simple Command-Line Interface for Rural Agriculture Decision Support System.

This CLI provides an easy-to-use interface for farmers and field workers to get
farming recommendations. Uses simple language and clear formatting suitable for
users with varying technical backgrounds.

Author: Agriculture Decision Support System
Version: 1.0
"""

import sys
import os

# Add project root to path for importing modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from api.decision_engine import run_decision_engine, validate_engine_inputs
except ImportError:
    print("Error: Could not load the decision engine. Please ensure all system files are present.")
    sys.exit(1)


def print_header():
    """Print the application header."""
    print("=" * 60)
    print("    RURAL AGRICULTURE DECISION SUPPORT SYSTEM")
    print("=" * 60)
    print("This tool helps you make safe farming decisions based on")
    print("current weather and field conditions.")
    print()


def print_separator():
    """Print a visual separator."""
    print("-" * 60)


def get_user_input(prompt: str, input_type: str = "string", 
                  valid_options: list = None, allow_empty: bool = False) -> any:
    """
    Get user input with validation and error handling.
    
    Args:
        prompt (str): The prompt to display to the user
        input_type (str): Type of input expected ('string', 'float', 'int', 'boolean')
        valid_options (list): List of valid string options (for string type)
        allow_empty (bool): Whether empty input is allowed
        
    Returns:
        Validated user input of the appropriate type
    """
    while True:
        try:
            user_input = input(prompt).strip()
            
            # Handle empty input
            if not user_input:
                if allow_empty:
                    return None
                else:
                    print("Please enter a value. This field is required.")
                    continue
            
            # Handle different input types
            if input_type == "float":
                value = float(user_input)
                return value
            
            elif input_type == "int":
                value = int(user_input)
                return value
            
            elif input_type == "boolean":
                user_input_lower = user_input.lower()
                if user_input_lower in ['yes', 'y', '1', 'true']:
                    return True
                elif user_input_lower in ['no', 'n', '0', 'false']:
                    return False
                else:
                    print("Please enter 'yes' or 'no'.")
                    continue
            
            elif input_type == "string":
                if valid_options:
                    user_input_upper = user_input.upper()
                    if user_input_upper in [opt.upper() for opt in valid_options]:
                        return user_input_upper
                    else:
                        print(f"Please choose from: {', '.join(valid_options)}")
                        continue
                return user_input
            
            else:
                return user_input
                
        except ValueError:
            if input_type == "float":
                print("Please enter a valid number (can include decimals).")
            elif input_type == "int":
                print("Please enter a valid whole number.")
            else:
                print("Invalid input. Please try again.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(0)
        except Exception as e:
            print(f"Error processing input: {e}")
            print("Please try again.")


def collect_farmer_inputs() -> dict:
    """
    Collect all required inputs from the farmer through interactive prompts.
    
    Returns:
        dict: Dictionary containing all farmer inputs
    """
    print("Please provide information about your current farming conditions:")
    print("(Press Ctrl+C at any time to exit)")
    print()
    
    inputs = {}
    
    # Basic identification (optional)
    print("BASIC INFORMATION (Optional)")
    print_separator()
    
    farmer_id = get_user_input(
        "Your farmer ID or name (press Enter to skip): ",
        allow_empty=True
    )
    if farmer_id:
        inputs['farmer_id'] = farmer_id
    
    region = get_user_input(
        "Your region/district (press Enter to skip): ",
        allow_empty=True
    )
    if region:
        inputs['region'] = region
    
    print()
    
    # Weather conditions
    print("WEATHER CONDITIONS")
    print_separator()
    
    while True:
        try:
            rainfall = get_user_input(
                "Recent rainfall in your area (in mm): ",
                input_type="float"
            )
            if rainfall < 0:
                print("Rainfall cannot be negative. Please enter a positive number.")
                continue
            if rainfall > 500:
                print("That seems like very high rainfall. Please double-check your input.")
                continue
            inputs['rainfall_mm'] = rainfall
            break
        except:
            continue
    
    while True:
        try:
            temperature = get_user_input(
                "Current temperature (in °C): ",
                input_type="float"
            )
            if temperature < -10 or temperature > 50:
                print("Temperature seems unusual. Please check your input (normal range: -10°C to 50°C).")
                continue
            inputs['temperature_c'] = temperature
            break
        except:
            continue
    
    while True:
        try:
            humidity = get_user_input(
                "Current humidity (in %): ",
                input_type="float"
            )
            if humidity < 0 or humidity > 100:
                print("Humidity must be between 0% and 100%.")
                continue
            inputs['humidity_percent'] = humidity
            break
        except:
            continue
    
    print()
    
    # Field conditions
    print("FIELD CONDITIONS")
    print_separator()
    
    soil_type = get_user_input(
        "Your soil type (CLAY, LOAM, SANDY, SILT): ",
        input_type="string",
        valid_options=['CLAY', 'LOAM', 'SANDY', 'SILT']
    )
    inputs['soil_type'] = soil_type
    
    crop_type = get_user_input(
        "Crop you want to grow (e.g., wheat, rice, cotton): ",
        input_type="string"
    )
    inputs['crop_type'] = crop_type.lower()
    
    growing_stage = get_user_input(
        "Current growth stage (seedling, vegetative, flowering, harvest) or press Enter to skip: ",
        input_type="string",
        allow_empty=True
    )
    if growing_stage:
        inputs['growing_stage'] = growing_stage.lower()
    
    print()
    
    # Water availability
    print("WATER AVAILABILITY")
    print_separator()
    
    while True:
        try:
            available_water = get_user_input(
                "Water available for irrigation (in mm): ",
                input_type="float"
            )
            if available_water < 0:
                print("Available water cannot be negative.")
                continue
            inputs['available_water_mm'] = available_water
            break
        except:
            continue
    
    print()
    
    # Leaf image availability
    print("CROP MONITORING")
    print_separator()
    
    leaf_image = get_user_input(
        "Do you have leaf images for disease checking? (yes/no): ",
        input_type="boolean"
    )
    inputs['leaf_image_provided'] = leaf_image
    
    return inputs


def display_results(result: dict):
    """
    Display the decision engine results in a farmer-friendly format.
    
    Args:
        result (dict): Results from the decision engine
    """
    print()
    print("=" * 60)
    print("           FARMING RECOMMENDATION")
    print("=" * 60)
    
    # Main decision
    decision = result.get('final_decision', 'UNKNOWN')
    risk_level = result.get('overall_risk_level', 'UNKNOWN')
    
    # Format decision for display
    decision_display = {
        'PROCEED': '✓ PROCEED WITH FARMING',
        'REDUCE_INPUTS': '⚠ PROCEED WITH CAUTION',
        'AVOID_FARMING': '✗ AVOID FARMING FOR NOW'
    }
    
    decision_text = decision_display.get(decision, decision)
    
    print(f"RECOMMENDATION: {decision_text}")
    print(f"RISK LEVEL: {risk_level}")
    print()
    
    # Risk level explanation with colors/symbols
    risk_symbols = {
        'LOW': '🟢',
        'MEDIUM': '🟡', 
        'HIGH': '🔴'
    }
    
    risk_symbol = risk_symbols.get(risk_level, '⚪')
    print(f"{risk_symbol} Risk Level: {risk_level}")
    
    print_separator()
    
    # Farmer-friendly explanation
    explanation = result.get('explanation', 'No explanation available.')
    print("EXPLANATION:")
    print(explanation)
    print()
    
    print_separator()
    
    # Yield and disease summary
    yield_summary = result.get('yield_summary', {})
    disease_summary = result.get('disease_summary', {})
    
    expected_yield = yield_summary.get('expected_yield_percentage', 0)
    disease_risk = disease_summary.get('risk_level', 'UNKNOWN')
    
    print("QUICK SUMMARY:")
    print(f"• Expected crop yield: {expected_yield:.0f}% of maximum potential")
    print(f"• Disease risk level: {disease_risk}")
    
    # Add confidence information
    confidence_level = yield_summary.get('confidence_level', 'Unknown')
    print(f"• Prediction confidence: {confidence_level}")
    print()
    
    print_separator()
    
    # Top recommendations
    recommendations = result.get('recommendations', [])
    if recommendations:
        print("TOP RECOMMENDATIONS:")
        # Show top 3 recommendations
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"{i}. {rec}")
        
        if len(recommendations) > 3:
            print(f"   ... and {len(recommendations) - 3} more recommendations")
    else:
        print("No specific recommendations available.")
    
    print()
    print_separator()


def display_error_message(error_msg: str):
    """
    Display error message in a user-friendly format.
    
    Args:
        error_msg (str): Error message to display
    """
    print()
    print("=" * 60)
    print("           ERROR")
    print("=" * 60)
    print("Sorry, there was a problem processing your request:")
    print(f"• {error_msg}")
    print()
    print("Please check your inputs and try again.")
    print("If the problem continues, contact your local agricultural officer.")
    print()


def ask_continue() -> bool:
    """
    Ask user if they want to make another assessment.
    
    Returns:
        bool: True if user wants to continue, False otherwise
    """
    print("=" * 60)
    try:
        continue_choice = get_user_input(
            "Would you like to make another farming assessment? (yes/no): ",
            input_type="boolean"
        )
        return continue_choice
    except:
        return False


def show_help():
    """Display help information."""
    print()
    print("HELP - How to use this tool:")
    print_separator()
    print("1. This tool asks you questions about your farming conditions")
    print("2. Answer each question as accurately as possible")
    print("3. The system will analyze your situation and give recommendations")
    print("4. Follow the recommendations to make safer farming decisions")
    print()
    print("SOIL TYPES:")
    print("• CLAY: Heavy soil that holds water well but drains slowly")
    print("• LOAM: Best soil type - good drainage and fertility")
    print("• SANDY: Light soil that drains quickly, needs frequent watering")
    print("• SILT: Fine soil with good water retention")
    print()
    print("If you're unsure about any input, ask your local agricultural officer.")
    print()


def main():
    """
    Main CLI application function.
    """
    try:
        # Print header
        print_header()
        
        # Check if user wants help
        if len(sys.argv) > 1 and sys.argv[1].lower() in ['-h', '--help', 'help']:
            show_help()
            return
        
        # Main application loop
        while True:
            try:
                # Collect inputs from user
                print("Starting new farming assessment...")
                print()
                
                farmer_inputs = collect_farmer_inputs()
                
                print()
                print("Processing your information...")
                print("Please wait...")
                
                # Validate inputs
                is_valid, validation_message = validate_engine_inputs(farmer_inputs)
                if not is_valid:
                    display_error_message(f"Input validation failed: {validation_message}")
                    if not ask_continue():
                        break
                    continue
                
                # Run decision engine
                result = run_decision_engine(farmer_inputs)
                
                # Display results
                display_results(result)
                
                # Check for processing warnings or errors
                processing_info = result.get('processing_info', {})
                warnings = processing_info.get('warnings', [])
                errors = processing_info.get('errors', [])
                
                if warnings:
                    print("SYSTEM NOTES:")
                    for warning in warnings[:3]:  # Show top 3 warnings
                        print(f"• {warning}")
                    print()
                
                if errors:
                    print("SYSTEM ALERTS:")
                    for error in errors[:2]:  # Show top 2 errors
                        print(f"• {error}")
                    print("Note: Results may be less accurate due to system issues.")
                    print()
                
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user.")
                break
            
            except Exception as e:
                display_error_message(f"System error: {str(e)}")
                print("This may be due to missing system files or configuration issues.")
            
            # Ask if user wants to continue
            if not ask_continue():
                break
        
        # Exit message
        print()
        print("Thank you for using the Rural Agriculture Decision Support System!")
        print("Farm safely and prosper!")
        print()
        
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nCritical system error: {e}")
        print("Please contact technical support.")
        sys.exit(1)


if __name__ == "__main__":
    main()