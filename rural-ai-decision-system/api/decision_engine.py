"""
Central Decision Orchestration Engine for Rural Agriculture Decision Support System.

This module coordinates all decision-making components to provide comprehensive,
explainable farming recommendations. It orchestrates yield prediction, disease
detection, and rule-based decision making into a single, coherent result.

Author: Agriculture Decision Support System
Version: 1.0
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path for importing modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from models.yield_predictor import predict_yield, validate_inputs as validate_yield_inputs
    from models.disease_detector import detect_disease, validate_inputs as validate_disease_inputs
    from rules.farming_rules import make_farming_decision, validate_inputs as validate_rules_inputs
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}")
    print("Some functionality may be limited in standalone mode.")


def run_decision_engine(inputs: dict) -> dict:
    """
    Run the complete decision engine pipeline to generate farming recommendations.
    
    Args:
        inputs (dict): Raw farmer inputs containing:
            - rainfall_mm (float): Recent rainfall in millimeters
            - temperature_c (float): Current temperature in Celsius
            - soil_type (str): Soil type ('CLAY', 'LOAM', 'SANDY', 'SILT')
            - crop_type (str): Type of crop being grown
            - humidity_percent (float): Current humidity percentage
            - available_water_mm (float): Available water for irrigation
            - leaf_image_provided (bool): Whether leaf image is available
            - farmer_id (str, optional): Farmer identification
            - region (str, optional): Geographic region
            - growing_stage (str, optional): Current crop growth stage
            
    Returns:
        dict: Comprehensive decision results containing:
            - final_decision (str): Main farming recommendation
            - overall_risk_level (str): Consolidated risk assessment
            - yield_summary (dict): Yield prediction summary
            - disease_summary (dict): Disease risk summary
            - explanation (str): Farmer-friendly explanation
            - technical_details (dict): Detailed technical information
            - recommendations (list): Actionable recommendations
            - processing_info (dict): Processing metadata
    """
    
    # Initialize processing metadata
    processing_start = datetime.now()
    processing_info = {
        'timestamp': processing_start.isoformat(),
        'engine_version': '1.0',
        'processing_steps': [],
        'warnings': [],
        'errors': []
    }
    
    try:
        # =============================================================================
        # STEP 1: INPUT VALIDATION AND PREPROCESSING
        # =============================================================================
        processing_info['processing_steps'].append('Input validation and preprocessing')
        
        # Validate and clean inputs
        cleaned_inputs, validation_warnings = _validate_and_clean_inputs(inputs)
        processing_info['warnings'].extend(validation_warnings)
        
        # Extract farmer metadata
        farmer_metadata = _extract_farmer_metadata(cleaned_inputs)
        
        # =============================================================================
        # STEP 2: YIELD PREDICTION
        # =============================================================================
        processing_info['processing_steps'].append('Yield prediction analysis')
        
        try:
            # Prepare inputs for yield predictor
            yield_inputs = {
                'rainfall_mm': cleaned_inputs['rainfall_mm'],
                'temperature_c': cleaned_inputs['temperature_c'],
                'soil_type': cleaned_inputs['soil_type'],
                'crop_type': cleaned_inputs['crop_type']
            }
            
            # Run yield prediction
            yield_result = predict_yield(yield_inputs)
            processing_info['processing_steps'].append('Yield prediction completed successfully')
            
        except Exception as e:
            # Graceful fallback for yield prediction failure
            yield_result = _create_fallback_yield_result(str(e))
            processing_info['errors'].append(f"Yield prediction failed: {e}")
            processing_info['warnings'].append("Using conservative fallback yield estimates")
        
        # =============================================================================
        # STEP 3: DISEASE RISK ASSESSMENT
        # =============================================================================
        processing_info['processing_steps'].append('Disease risk assessment')
        
        try:
            # Prepare inputs for disease detector
            disease_inputs = {
                'leaf_image_provided': cleaned_inputs['leaf_image_provided'],
                'humidity_percent': cleaned_inputs['humidity_percent'],
                'rainfall_mm': cleaned_inputs['rainfall_mm'],
                'temperature_c': cleaned_inputs['temperature_c'],
                'crop_type': cleaned_inputs['crop_type']
            }
            
            # Run disease detection
            disease_result = detect_disease(disease_inputs)
            processing_info['processing_steps'].append('Disease risk assessment completed successfully')
            
        except Exception as e:
            # Graceful fallback for disease detection failure
            disease_result = _create_fallback_disease_result(str(e))
            processing_info['errors'].append(f"Disease detection failed: {e}")
            processing_info['warnings'].append("Using conservative fallback disease risk estimates")
        
        # =============================================================================
        # STEP 4: RULE-BASED DECISION MAKING
        # =============================================================================
        processing_info['processing_steps'].append('Rule-based decision analysis')
        
        try:
            # Prepare inputs for farming rules
            rules_inputs = {
                'yield_result': yield_result,
                'disease_result': disease_result,
                'available_water_mm': cleaned_inputs['available_water_mm'],
                'rainfall_mm': cleaned_inputs['rainfall_mm'],
                'soil_type': cleaned_inputs['soil_type'],
                'crop_type': cleaned_inputs['crop_type']
            }
            
            # Run farming decision rules
            decision_result = make_farming_decision(rules_inputs)
            processing_info['processing_steps'].append('Rule-based decision completed successfully')
            
        except Exception as e:
            # Graceful fallback for decision making failure
            decision_result = _create_fallback_decision_result(str(e))
            processing_info['errors'].append(f"Decision making failed: {e}")
            processing_info['warnings'].append("Using conservative fallback decision")
        
        # =============================================================================
        # STEP 5: RESULT CONSOLIDATION AND EXPLANATION GENERATION
        # =============================================================================
        processing_info['processing_steps'].append('Result consolidation and explanation generation')
        
        # Create consolidated results
        consolidated_result = _consolidate_results(
            yield_result, disease_result, decision_result, 
            cleaned_inputs, farmer_metadata, processing_info
        )
        
        # Calculate processing time
        processing_end = datetime.now()
        processing_info['processing_time_seconds'] = (processing_end - processing_start).total_seconds()
        processing_info['processing_steps'].append('Decision engine processing completed')
        
        # Add processing info to final result
        consolidated_result['processing_info'] = processing_info
        
        return consolidated_result
        
    except Exception as e:
        # Ultimate fallback for complete system failure
        processing_info['errors'].append(f"Critical system failure: {e}")
        return _create_emergency_fallback_result(inputs, processing_info)


def _validate_and_clean_inputs(inputs: dict) -> tuple[dict, list]:
    """
    Validate and clean input parameters with graceful handling of missing data.
    
    Returns:
        tuple: (cleaned_inputs, warnings)
    """
    warnings = []
    cleaned = {}
    
    # Required numeric inputs with defaults
    numeric_defaults = {
        'rainfall_mm': 0.0,
        'temperature_c': 25.0,  # Reasonable default temperature
        'humidity_percent': 60.0,  # Moderate humidity default
        'available_water_mm': 30.0  # Conservative water default
    }
    
    for field, default in numeric_defaults.items():
        try:
            cleaned[field] = float(inputs.get(field, default))
            if field not in inputs:
                warnings.append(f"Missing {field}, using default value: {default}")
        except (ValueError, TypeError):
            cleaned[field] = default
            warnings.append(f"Invalid {field} value, using default: {default}")
    
    # Validate numeric ranges
    if cleaned['rainfall_mm'] < 0:
        cleaned['rainfall_mm'] = 0.0
        warnings.append("Negative rainfall corrected to 0")
    
    if cleaned['temperature_c'] < -20 or cleaned['temperature_c'] > 60:
        cleaned['temperature_c'] = 25.0
        warnings.append("Temperature outside realistic range, using default 25°C")
    
    if cleaned['humidity_percent'] < 0 or cleaned['humidity_percent'] > 100:
        cleaned['humidity_percent'] = 60.0
        warnings.append("Humidity outside valid range (0-100%), using default 60%")
    
    if cleaned['available_water_mm'] < 0:
        cleaned['available_water_mm'] = 0.0
        warnings.append("Negative water availability corrected to 0")
    
    # String inputs with defaults
    cleaned['soil_type'] = inputs.get('soil_type', 'LOAM').upper()
    if cleaned['soil_type'] not in ['CLAY', 'LOAM', 'SANDY', 'SILT']:
        cleaned['soil_type'] = 'LOAM'
        warnings.append("Unknown soil type, using default: LOAM")
    
    cleaned['crop_type'] = inputs.get('crop_type', 'wheat').lower()
    
    # Boolean inputs
    cleaned['leaf_image_provided'] = bool(inputs.get('leaf_image_provided', False))
    
    # Optional metadata
    cleaned['farmer_id'] = inputs.get('farmer_id', 'unknown')
    cleaned['region'] = inputs.get('region', 'unknown')
    cleaned['growing_stage'] = inputs.get('growing_stage', 'unknown')
    
    return cleaned, warnings


def _extract_farmer_metadata(inputs: dict) -> dict:
    """
    Extract farmer and contextual metadata from inputs.
    """
    return {
        'farmer_id': inputs.get('farmer_id', 'unknown'),
        'region': inputs.get('region', 'unknown'),
        'crop_type': inputs.get('crop_type', 'unknown'),
        'soil_type': inputs.get('soil_type', 'unknown'),
        'growing_stage': inputs.get('growing_stage', 'unknown')
    }


def _create_fallback_yield_result(error_msg: str) -> dict:
    """
    Create conservative fallback yield result when yield prediction fails.
    """
    return {
        'expected_yield_percentage': 30.0,  # Conservative estimate
        'confidence_score': 0.3,  # Low confidence
        'explanation': f"Yield prediction unavailable ({error_msg}). Using conservative estimate of 30% yield with low confidence for safety."
    }


def _create_fallback_disease_result(error_msg: str) -> dict:
    """
    Create conservative fallback disease result when disease detection fails.
    """
    return {
        'disease_risk_level': 'MEDIUM',  # Conservative assumption
        'disease_risk_score': 0.6,  # Moderate risk
        'explanation': f"Disease assessment unavailable ({error_msg}). Assuming medium disease risk for safety.",
        'recommendations': [
            "Monitor crops closely for disease symptoms",
            "Implement preventive disease management practices"
        ]
    }


def _create_fallback_decision_result(error_msg: str) -> dict:
    """
    Create conservative fallback decision when rule-based decision making fails.
    """
    return {
        'decision': 'REDUCE_INPUTS',  # Conservative decision
        'risk_level': 'HIGH',  # Conservative risk assessment
        'explanation': f"Decision analysis unavailable ({error_msg}). Recommending conservative approach with reduced inputs for farmer safety.",
        'reasoning': [
            "FALLBACK: System error requires conservative approach",
            "SAFETY: Reduced inputs minimize potential losses"
        ],
        'recommendations': [
            "Proceed with caution and reduced investment",
            "Consult local agricultural extension officer",
            "Monitor conditions closely"
        ]
    }


def _consolidate_results(yield_result: dict, disease_result: dict, decision_result: dict,
                        inputs: dict, metadata: dict, processing_info: dict) -> dict:
    """
    Consolidate all component results into a unified response.
    """
    # Extract key metrics
    final_decision = decision_result.get('decision', 'REDUCE_INPUTS')
    overall_risk_level = decision_result.get('risk_level', 'HIGH')
    
    # Create yield summary
    yield_summary = {
        'expected_yield_percentage': yield_result.get('expected_yield_percentage', 0.0),
        'confidence_score': yield_result.get('confidence_score', 0.0),
        'confidence_level': _get_confidence_description(yield_result.get('confidence_score', 0.0))
    }
    
    # Create disease summary
    disease_summary = {
        'risk_level': disease_result.get('disease_risk_level', 'HIGH'),
        'risk_score': disease_result.get('disease_risk_score', 1.0),
        'image_analysis': 'Completed' if inputs.get('leaf_image_provided') else 'Not available'
    }
    
    # Generate farmer-friendly explanation
    farmer_explanation = _generate_farmer_explanation(
        final_decision, overall_risk_level, yield_summary, disease_summary, inputs
    )
    
    # Compile all recommendations
    all_recommendations = []
    all_recommendations.extend(decision_result.get('recommendations', []))
    all_recommendations.extend(disease_result.get('recommendations', []))
    
    # Remove duplicates while preserving order
    unique_recommendations = []
    seen = set()
    for rec in all_recommendations:
        if rec not in seen:
            unique_recommendations.append(rec)
            seen.add(rec)
    
    # Create technical details for dashboards/evaluators
    technical_details = {
        'yield_analysis': yield_result,
        'disease_analysis': disease_result,
        'decision_analysis': decision_result,
        'input_parameters': inputs,
        'farmer_metadata': metadata,
        'risk_factors': _extract_risk_factors(yield_result, disease_result, decision_result),
        'confidence_metrics': {
            'yield_confidence': yield_result.get('confidence_score', 0.0),
            'overall_system_confidence': _calculate_system_confidence(yield_result, disease_result, processing_info)
        }
    }
    
    return {
        'final_decision': final_decision,
        'overall_risk_level': overall_risk_level,
        'yield_summary': yield_summary,
        'disease_summary': disease_summary,
        'explanation': farmer_explanation,
        'recommendations': unique_recommendations,
        'technical_details': technical_details
    }


def _generate_farmer_explanation(decision: str, risk_level: str, yield_summary: dict,
                               disease_summary: dict, inputs: dict) -> str:
    """
    Generate farmer-friendly explanation of the decision.
    """
    crop_type = inputs.get('crop_type', 'crop').title()
    
    # Start with decision summary
    decision_text = {
        'PROCEED': f"You can proceed with {crop_type} farming using standard practices.",
        'REDUCE_INPUTS': f"We recommend reducing your {crop_type} farming investment by 30-50% due to current conditions.",
        'AVOID_FARMING': f"We strongly advise postponing {crop_type} farming until conditions improve."
    }
    
    explanation_parts = [
        decision_text.get(decision, "We recommend a conservative approach to farming."),
        f"Overall risk level is {risk_level.lower()}."
    ]
    
    # Add yield information
    yield_pct = yield_summary.get('expected_yield_percentage', 0)
    confidence = yield_summary.get('confidence_level', 'low')
    explanation_parts.append(
        f"Expected yield is {yield_pct:.0f}% of maximum potential with {confidence.lower()} confidence."
    )
    
    # Add disease information
    disease_risk = disease_summary.get('risk_level', 'HIGH').lower()
    explanation_parts.append(f"Disease risk is currently {disease_risk}.")
    
    # Add key environmental factors
    temp = inputs.get('temperature_c', 0)
    rainfall = inputs.get('rainfall_mm', 0)
    water = inputs.get('available_water_mm', 0)
    
    explanation_parts.append(
        f"Current conditions: {temp:.1f}°C temperature, {rainfall:.1f}mm recent rainfall, "
        f"{water:.1f}mm water available for irrigation."
    )
    
    # Add safety note
    explanation_parts.append(
        "This recommendation prioritizes your safety and economic protection. "
        "Monitor conditions regularly and be prepared to adjust your approach if they change."
    )
    
    return " ".join(explanation_parts)


def _get_confidence_description(confidence_score: float) -> str:
    """
    Convert numerical confidence to descriptive text.
    """
    if confidence_score >= 0.8:
        return 'High'
    elif confidence_score >= 0.6:
        return 'Medium'
    elif confidence_score >= 0.4:
        return 'Low'
    else:
        return 'Very Low'


def _extract_risk_factors(yield_result: dict, disease_result: dict, decision_result: dict) -> list:
    """
    Extract and consolidate risk factors from all analyses.
    """
    risk_factors = []
    
    # Add yield-related risks
    yield_pct = yield_result.get('expected_yield_percentage', 0)
    yield_conf = yield_result.get('confidence_score', 0)
    
    if yield_pct < 40:
        risk_factors.append(f"Low expected yield ({yield_pct:.1f}%)")
    if yield_conf < 0.5:
        risk_factors.append(f"Low yield prediction confidence ({yield_conf:.2f})")
    
    # Add disease-related risks
    disease_level = disease_result.get('disease_risk_level', 'HIGH')
    if disease_level in ['HIGH', 'MEDIUM']:
        risk_factors.append(f"{disease_level.lower()} disease risk")
    
    # Add decision-related risks from reasoning
    reasoning = decision_result.get('reasoning', [])
    for reason in reasoning:
        if reason.startswith('AVOID:') or reason.startswith('RISK:') or reason.startswith('SAFETY:'):
            risk_factors.append(reason)
    
    return risk_factors


def _calculate_system_confidence(yield_result: dict, disease_result: dict, processing_info: dict) -> float:
    """
    Calculate overall system confidence based on component performance.
    """
    base_confidence = 0.8  # Base system confidence
    
    # Reduce confidence for errors
    error_count = len(processing_info.get('errors', []))
    confidence_penalty = error_count * 0.2
    
    # Factor in yield prediction confidence
    yield_confidence = yield_result.get('confidence_score', 0.5)
    
    # Calculate weighted confidence
    system_confidence = (base_confidence - confidence_penalty) * 0.7 + yield_confidence * 0.3
    
    return max(0.1, min(1.0, system_confidence))  # Clamp between 0.1 and 1.0


def _create_emergency_fallback_result(inputs: dict, processing_info: dict) -> dict:
    """
    Create emergency fallback result when entire system fails.
    """
    return {
        'final_decision': 'AVOID_FARMING',
        'overall_risk_level': 'HIGH',
        'yield_summary': {
            'expected_yield_percentage': 0.0,
            'confidence_score': 0.0,
            'confidence_level': 'Very Low'
        },
        'disease_summary': {
            'risk_level': 'HIGH',
            'risk_score': 1.0,
            'image_analysis': 'System Error'
        },
        'explanation': (
            "SYSTEM ERROR: The decision support system encountered critical errors and cannot "
            "provide reliable recommendations. For your safety, we strongly advise avoiding "
            "farming activities until the system is restored. Please consult your local "
            "agricultural extension officer for manual assessment."
        ),
        'recommendations': [
            "Do not proceed with farming until system is restored",
            "Consult local agricultural extension officer immediately",
            "Monitor weather and field conditions manually",
            "Wait for system recovery before making farming decisions"
        ],
        'technical_details': {
            'system_status': 'CRITICAL_ERROR',
            'error_details': processing_info.get('errors', []),
            'input_parameters': inputs
        },
        'processing_info': processing_info
    }


def validate_engine_inputs(inputs: dict) -> tuple[bool, str]:
    """
    Validate inputs for the decision engine.
    
    Args:
        inputs (dict): Input parameters to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(inputs, dict):
        return False, "Inputs must be a dictionary"
    
    # Check for at least some basic inputs
    basic_fields = ['rainfall_mm', 'temperature_c', 'soil_type', 'crop_type']
    missing_fields = [field for field in basic_fields if field not in inputs]
    
    if len(missing_fields) == len(basic_fields):
        return False, "At least some basic farming parameters must be provided"
    
    return True, "Inputs are acceptable for processing"


# Example usage and testing function
def test_decision_engine():
    """
    Test function to demonstrate decision engine functionality.
    """
    test_cases = [
        {
            'name': 'Complete Input Set - Good Conditions',
            'inputs': {
                'farmer_id': 'TEST001',
                'region': 'Punjab',
                'rainfall_mm': 25.0,
                'temperature_c': 26.0,
                'soil_type': 'LOAM',
                'crop_type': 'wheat',
                'humidity_percent': 65.0,
                'available_water_mm': 60.0,
                'leaf_image_provided': True,
                'growing_stage': 'vegetative'
            }
        },
        {
            'name': 'Minimal Input Set - Missing Data',
            'inputs': {
                'rainfall_mm': 5.0,
                'temperature_c': 38.0,
                'crop_type': 'millet'
            }
        },
        {
            'name': 'High Risk Conditions',
            'inputs': {
                'rainfall_mm': 150.0,
                'temperature_c': 28.0,
                'soil_type': 'CLAY',
                'crop_type': 'rice',
                'humidity_percent': 90.0,
                'available_water_mm': 200.0,
                'leaf_image_provided': True
            }
        }
    ]
    
    print("Decision Engine Test Results:")
    print("=" * 60)
    
    for test_case in test_cases:
        print(f"\nTest Case: {test_case['name']}")
        print("-" * 50)
        
        # Validate inputs
        is_valid, message = validate_engine_inputs(test_case['inputs'])
        if not is_valid:
            print(f"Input validation failed: {message}")
            continue
        
        # Run decision engine
        result = run_decision_engine(test_case['inputs'])
        
        print(f"Final Decision: {result['final_decision']}")
        print(f"Risk Level: {result['overall_risk_level']}")
        print(f"Expected Yield: {result['yield_summary']['expected_yield_percentage']:.1f}%")
        print(f"Disease Risk: {result['disease_summary']['risk_level']}")
        print(f"Explanation: {result['explanation']}")
        
        # Show processing info
        processing = result.get('processing_info', {})
        if processing.get('warnings'):
            print("Warnings:")
            for warning in processing['warnings']:
                print(f"  • {warning}")
        
        if processing.get('errors'):
            print("Errors:")
            for error in processing['errors']:
                print(f"  • {error}")


if __name__ == "__main__":
    test_decision_engine()