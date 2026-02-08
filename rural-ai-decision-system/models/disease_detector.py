"""
Explainable Plant Disease Detection Module for Rural Agriculture Decision Support System.

This module provides rule-based disease risk assessment using environmental conditions
and optional visual inspection simulation. Designed to be conservative and prioritize
early warnings to protect farmer crops.

Author: Agriculture Decision Support System
Version: 1.0
"""

import sys
import os
import random

# Add config directory to path for importing settings
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from config.settings import (
        HUMIDITY_DISEASE_RISK, HUMIDITY_OPTIMAL_MIN, HUMIDITY_OPTIMAL_MAX,
        TEMP_OPTIMAL_MIN, TEMP_OPTIMAL_MAX, TEMP_CRITICAL_LOW, TEMP_CRITICAL_HIGH,
        RAINFALL_HIGH_THRESHOLD, RAINFALL_MEDIUM_THRESHOLD,
        DISEASE_RISK_HUMIDITY_HIGH, DISEASE_RISK_TEMP_OPTIMAL, DISEASE_RISK_RAINFALL_EXCESS,
        RISK_LOW, RISK_MEDIUM, RISK_HIGH
    )
except ImportError:
    # Fallback values if config is not available
    HUMIDITY_DISEASE_RISK = 80
    HUMIDITY_OPTIMAL_MIN = 40
    HUMIDITY_OPTIMAL_MAX = 70
    TEMP_OPTIMAL_MIN = 15.0
    TEMP_OPTIMAL_MAX = 30.0
    TEMP_CRITICAL_LOW = 5.0
    TEMP_CRITICAL_HIGH = 40.0
    RAINFALL_HIGH_THRESHOLD = 100.0
    RAINFALL_MEDIUM_THRESHOLD = 50.0
    DISEASE_RISK_HUMIDITY_HIGH = 1.5
    DISEASE_RISK_TEMP_OPTIMAL = 1.3
    DISEASE_RISK_RAINFALL_EXCESS = 1.4
    RISK_LOW = 0.25
    RISK_MEDIUM = 0.60
    RISK_HIGH = 0.85


def detect_disease(inputs: dict) -> dict:
    """
    Detect plant disease risk using environmental conditions and optional visual inspection.
    
    Args:
        inputs (dict): Dictionary containing:
            - leaf_image_provided (bool): Whether leaf image is available for analysis
            - humidity_percent (float): Current humidity percentage
            - rainfall_mm (float): Recent rainfall in millimeters
            - temperature_c (float): Current temperature in Celsius
            - crop_type (str, optional): Type of crop for specific disease patterns
            
    Returns:
        dict: Disease detection results containing:
            - disease_risk_level (str): Risk level ('LOW', 'MEDIUM', 'HIGH')
            - disease_risk_score (float): Risk score (0-1)
            - explanation (str): Plain English explanation of the assessment
            - recommendations (list): Specific action recommendations
    """
    
    # Extract and validate inputs
    leaf_image_provided = inputs.get('leaf_image_provided', False)
    humidity = inputs.get('humidity_percent', 50.0)
    rainfall = inputs.get('rainfall_mm', 0.0)
    temperature = inputs.get('temperature_c', 25.0)
    crop_type = inputs.get('crop_type', 'unknown').lower()
    
    # Initialize risk assessment components
    environmental_risk = 0.0
    visual_risk = 0.0
    crop_specific_risk = 0.0
    
    # Track explanation components
    risk_factors = []
    protective_factors = []
    recommendations = []
    
    # =============================================================================
    # ENVIRONMENTAL RISK ASSESSMENT (Primary method when no image available)
    # =============================================================================
    
    # Humidity-based risk assessment (40% weight)
    humidity_risk = _assess_humidity_risk(humidity, risk_factors, protective_factors)
    
    # Temperature-based risk assessment (30% weight)
    temperature_risk = _assess_temperature_risk(temperature, risk_factors, protective_factors)
    
    # Rainfall-based risk assessment (20% weight)
    rainfall_risk = _assess_rainfall_risk(rainfall, risk_factors, protective_factors)
    
    # Calculate base environmental risk
    environmental_risk = (
        humidity_risk * 0.40 +
        temperature_risk * 0.30 +
        rainfall_risk * 0.20 +
        0.10  # Base risk factor (diseases always present at low levels)
    )
    
    # =============================================================================
    # VISUAL INSPECTION SIMULATION (When image is provided)
    # =============================================================================
    if leaf_image_provided:
        visual_risk = _simulate_visual_inspection(
            environmental_risk, crop_type, risk_factors, recommendations
        )
        # Combine environmental and visual assessment (weighted average)
        combined_risk = (environmental_risk * 0.6) + (visual_risk * 0.4)
    else:
        combined_risk = environmental_risk
        recommendations.append("Consider providing leaf images for more accurate disease detection")
    
    # =============================================================================
    # CROP-SPECIFIC DISEASE PATTERNS (10% adjustment)
    # =============================================================================
    crop_specific_risk = _assess_crop_specific_risk(
        crop_type, humidity, temperature, rainfall, risk_factors
    )
    
    # Apply crop-specific adjustment
    final_risk_score = min(combined_risk + crop_specific_risk, 1.0)
    
    # =============================================================================
    # CONSERVATIVE ADJUSTMENT (Prioritize early warnings)
    # =============================================================================
    # Add conservative buffer to prevent false negatives
    conservative_buffer = 0.1
    final_risk_score = min(final_risk_score + conservative_buffer, 1.0)
    
    # =============================================================================
    # DETERMINE RISK LEVEL AND GENERATE RECOMMENDATIONS
    # =============================================================================
    disease_risk_level = _determine_risk_level(final_risk_score)
    
    # Generate risk-level specific recommendations
    _add_risk_level_recommendations(disease_risk_level, recommendations)
    
    # Add environmental management recommendations
    _add_environmental_recommendations(
        humidity, temperature, rainfall, recommendations
    )
    
    # =============================================================================
    # GENERATE EXPLANATION
    # =============================================================================
    explanation = _generate_explanation(
        disease_risk_level, final_risk_score, leaf_image_provided,
        risk_factors, protective_factors
    )
    
    return {
        'disease_risk_level': disease_risk_level,
        'disease_risk_score': round(final_risk_score, 2),
        'explanation': explanation,
        'recommendations': recommendations
    }


def _assess_humidity_risk(humidity: float, risk_factors: list, protective_factors: list) -> float:
    """
    Assess disease risk based on humidity levels.
    
    High humidity promotes fungal and bacterial diseases.
    """
    if humidity >= HUMIDITY_DISEASE_RISK:
        risk_factors.append(f"Very high humidity ({humidity}%) creates ideal conditions for fungal diseases")
        return 0.8
    elif humidity > HUMIDITY_OPTIMAL_MAX:
        risk_factors.append(f"High humidity ({humidity}%) increases disease risk")
        return 0.6
    elif humidity >= HUMIDITY_OPTIMAL_MIN:
        protective_factors.append(f"Moderate humidity ({humidity}%) is within acceptable range")
        return 0.2
    else:
        protective_factors.append(f"Low humidity ({humidity}%) reduces fungal disease risk")
        return 0.1


def _assess_temperature_risk(temperature: float, risk_factors: list, protective_factors: list) -> float:
    """
    Assess disease risk based on temperature conditions.
    
    Moderate temperatures often favor pathogen development.
    """
    if temperature < TEMP_CRITICAL_LOW:
        protective_factors.append(f"Very low temperature ({temperature}°C) inhibits most pathogens")
        return 0.1
    elif temperature < TEMP_OPTIMAL_MIN:
        protective_factors.append(f"Cool temperature ({temperature}°C) slows pathogen development")
        return 0.2
    elif temperature <= TEMP_OPTIMAL_MAX:
        risk_factors.append(f"Optimal temperature ({temperature}°C) favors pathogen activity")
        return 0.6
    elif temperature < TEMP_CRITICAL_HIGH:
        risk_factors.append(f"Warm temperature ({temperature}°C) may stress plants, increasing susceptibility")
        return 0.5
    else:
        protective_factors.append(f"Very high temperature ({temperature}°C) inhibits many pathogens")
        return 0.3


def _assess_rainfall_risk(rainfall: float, risk_factors: list, protective_factors: list) -> float:
    """
    Assess disease risk based on rainfall patterns.
    
    Excessive moisture promotes disease development and spread.
    """
    if rainfall >= RAINFALL_HIGH_THRESHOLD:
        risk_factors.append(f"Heavy rainfall ({rainfall}mm) creates wet conditions favoring disease spread")
        return 0.8
    elif rainfall >= RAINFALL_MEDIUM_THRESHOLD:
        risk_factors.append(f"Moderate rainfall ({rainfall}mm) increases moisture-related disease risk")
        return 0.5
    elif rainfall > 0:
        protective_factors.append(f"Light rainfall ({rainfall}mm) provides moisture without excess")
        return 0.2
    else:
        protective_factors.append("No recent rainfall reduces moisture-related disease risk")
        return 0.1


def _simulate_visual_inspection(environmental_risk: float, crop_type: str, 
                              risk_factors: list, recommendations: list) -> float:
    """
    Simulate visual inspection of leaf images.
    
    This is a placeholder for future CNN integration. Currently uses
    environmental risk with some randomization to simulate visual findings.
    """
    # Simulate visual inspection results based on environmental conditions
    # In a real implementation, this would process actual leaf images
    
    # Base visual risk on environmental conditions with some variation
    base_visual_risk = environmental_risk
    
    # Add simulated visual indicators
    visual_indicators = []
    
    # Simulate common visual symptoms based on environmental risk
    if environmental_risk > 0.7:
        # High environmental risk - likely to see symptoms
        visual_indicators.extend([
            "Leaf discoloration patterns detected",
            "Possible fungal spots observed",
            "Leaf texture abnormalities noted"
        ])
        visual_risk_adjustment = 0.2
    elif environmental_risk > 0.4:
        # Medium environmental risk - some symptoms possible
        visual_indicators.extend([
            "Minor leaf discoloration observed",
            "Early stage symptoms possible"
        ])
        visual_risk_adjustment = 0.1
    else:
        # Low environmental risk - minimal symptoms
        visual_indicators.append("No obvious disease symptoms detected in leaf image")
        visual_risk_adjustment = -0.1
    
    # Add visual findings to risk factors
    for indicator in visual_indicators:
        risk_factors.append(f"Visual inspection: {indicator}")
    
    # Calculate final visual risk
    visual_risk = max(0.0, min(1.0, base_visual_risk + visual_risk_adjustment))
    
    # Add recommendation for professional diagnosis if high risk detected
    if visual_risk > 0.6:
        recommendations.append("Consider consulting agricultural extension officer for professional disease diagnosis")
    
    return visual_risk


def _assess_crop_specific_risk(crop_type: str, humidity: float, temperature: float, 
                             rainfall: float, risk_factors: list) -> float:
    """
    Assess crop-specific disease susceptibility patterns.
    
    Different crops have different disease vulnerabilities under specific conditions.
    """
    crop_disease_patterns = {
        'rice': {
            'high_humidity_diseases': ['blast', 'sheath_blight'],
            'wet_conditions_risk': 0.15,
            'description': 'susceptible to fungal diseases in wet conditions'
        },
        'wheat': {
            'moderate_temp_diseases': ['rust', 'powdery_mildew'],
            'moderate_conditions_risk': 0.10,
            'description': 'prone to rust diseases in moderate temperatures'
        },
        'cotton': {
            'high_humidity_diseases': ['bollworm', 'bacterial_blight'],
            'pest_disease_risk': 0.12,
            'description': 'susceptible to bollworm and bacterial diseases'
        },
        'tomato': {
            'wet_conditions_diseases': ['late_blight', 'early_blight'],
            'humidity_risk': 0.18,
            'description': 'highly susceptible to blight in humid conditions'
        },
        'potato': {
            'cool_wet_diseases': ['late_blight'],
            'cool_wet_risk': 0.20,
            'description': 'extremely susceptible to late blight in cool, wet conditions'
        }
    }
    
    if crop_type not in crop_disease_patterns:
        return 0.05  # Small risk adjustment for unknown crops
    
    pattern = crop_disease_patterns[crop_type]
    crop_risk = 0.0
    
    # Check for high humidity diseases
    if 'high_humidity_diseases' in pattern and humidity > HUMIDITY_DISEASE_RISK:
        crop_risk += pattern.get('wet_conditions_risk', 0.1)
        risk_factors.append(f"{crop_type.title()} is {pattern['description']}")
    
    # Check for moderate temperature diseases
    if ('moderate_temp_diseases' in pattern and 
        TEMP_OPTIMAL_MIN <= temperature <= TEMP_OPTIMAL_MAX):
        crop_risk += pattern.get('moderate_conditions_risk', 0.1)
        risk_factors.append(f"{crop_type.title()} is {pattern['description']}")
    
    # Check for cool, wet conditions
    if ('cool_wet_diseases' in pattern and 
        temperature < TEMP_OPTIMAL_MIN and rainfall > RAINFALL_MEDIUM_THRESHOLD):
        crop_risk += pattern.get('cool_wet_risk', 0.15)
        risk_factors.append(f"{crop_type.title()} is {pattern['description']}")
    
    return min(crop_risk, 0.25)  # Cap crop-specific risk adjustment


def _determine_risk_level(risk_score: float) -> str:
    """
    Convert numerical risk score to categorical risk level.
    """
    if risk_score >= RISK_HIGH:
        return 'HIGH'
    elif risk_score >= RISK_MEDIUM:
        return 'MEDIUM'
    else:
        return 'LOW'


def _add_risk_level_recommendations(risk_level: str, recommendations: list):
    """
    Add risk-level specific recommendations.
    """
    if risk_level == 'HIGH':
        recommendations.extend([
            "URGENT: Inspect crops immediately for disease symptoms",
            "Consider preventive fungicide application if available",
            "Improve air circulation around plants",
            "Avoid overhead watering to reduce leaf wetness"
        ])
    elif risk_level == 'MEDIUM':
        recommendations.extend([
            "Monitor crops closely for early disease symptoms",
            "Ensure good field drainage",
            "Consider preventive measures if weather continues"
        ])
    else:  # LOW risk
        recommendations.extend([
            "Continue regular crop monitoring",
            "Maintain good agricultural practices"
        ])


def _add_environmental_recommendations(humidity: float, temperature: float, 
                                     rainfall: float, recommendations: list):
    """
    Add environment-specific management recommendations.
    """
    if humidity > HUMIDITY_DISEASE_RISK:
        recommendations.append("Improve field ventilation to reduce humidity")
    
    if rainfall > RAINFALL_HIGH_THRESHOLD:
        recommendations.extend([
            "Ensure proper field drainage",
            "Avoid working in wet fields to prevent disease spread"
        ])
    
    if TEMP_OPTIMAL_MIN <= temperature <= TEMP_OPTIMAL_MAX and humidity > HUMIDITY_OPTIMAL_MAX:
        recommendations.append("Current conditions favor disease development - increase monitoring frequency")


def _generate_explanation(risk_level: str, risk_score: float, image_provided: bool,
                         risk_factors: list, protective_factors: list) -> str:
    """
    Generate comprehensive explanation of disease risk assessment.
    """
    explanation_parts = [
        f"Disease risk assessment: {risk_level} ({risk_score:.2f}/1.0)."
    ]
    
    # Add assessment method
    if image_provided:
        explanation_parts.append("Assessment based on environmental conditions and simulated visual inspection.")
    else:
        explanation_parts.append("Assessment based on environmental conditions only.")
    
    # Add risk factors
    if risk_factors:
        explanation_parts.append("Risk factors identified:")
        explanation_parts.extend([f"• {factor}" for factor in risk_factors])
    
    # Add protective factors
    if protective_factors:
        explanation_parts.append("Protective factors:")
        explanation_parts.extend([f"• {factor}" for factor in protective_factors])
    
    # Add conservative approach note
    explanation_parts.append(
        "Note: Assessment uses conservative estimates to prioritize early disease detection and crop protection."
    )
    
    return " ".join(explanation_parts)


def validate_inputs(inputs: dict) -> tuple[bool, str]:
    """
    Validate input parameters for disease detection.
    
    Args:
        inputs (dict): Input parameters to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['leaf_image_provided', 'humidity_percent', 'rainfall_mm', 'temperature_c']
    
    # Check for required fields
    for field in required_fields:
        if field not in inputs:
            return False, f"Missing required field: {field}"
    
    # Validate data types and ranges
    try:
        humidity = float(inputs['humidity_percent'])
        rainfall = float(inputs['rainfall_mm'])
        temperature = float(inputs['temperature_c'])
        image_provided = bool(inputs['leaf_image_provided'])
        
        if humidity < 0 or humidity > 100:
            return False, "Humidity must be between 0 and 100 percent"
        
        if rainfall < 0:
            return False, "Rainfall cannot be negative"
        
        if rainfall > 500:
            return False, "Rainfall value seems unrealistic (>500mm)"
        
        if temperature < -20 or temperature > 60:
            return False, "Temperature value outside realistic range (-20°C to 60°C)"
            
    except (ValueError, TypeError):
        return False, "Numeric fields must contain valid numbers"
    
    return True, "Inputs are valid"


# Example usage and testing function
def test_disease_detector():
    """
    Test function to demonstrate disease detector functionality.
    """
    test_cases = [
        {
            'name': 'High Risk - Humid Conditions',
            'inputs': {
                'leaf_image_provided': True,
                'humidity_percent': 85.0,
                'rainfall_mm': 120.0,
                'temperature_c': 26.0,
                'crop_type': 'rice'
            }
        },
        {
            'name': 'Medium Risk - No Image',
            'inputs': {
                'leaf_image_provided': False,
                'humidity_percent': 65.0,
                'rainfall_mm': 35.0,
                'temperature_c': 28.0,
                'crop_type': 'wheat'
            }
        },
        {
            'name': 'Low Risk - Dry Conditions',
            'inputs': {
                'leaf_image_provided': False,
                'humidity_percent': 45.0,
                'rainfall_mm': 5.0,
                'temperature_c': 32.0,
                'crop_type': 'millet'
            }
        }
    ]
    
    print("Disease Detector Test Results:")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\nTest Case: {test_case['name']}")
        print("-" * 30)
        
        # Validate inputs
        is_valid, message = validate_inputs(test_case['inputs'])
        if not is_valid:
            print(f"Input validation failed: {message}")
            continue
        
        # Detect disease risk
        result = detect_disease(test_case['inputs'])
        
        print(f"Risk Level: {result['disease_risk_level']}")
        print(f"Risk Score: {result['disease_risk_score']}")
        print(f"Explanation: {result['explanation']}")
        print("Recommendations:")
        for rec in result['recommendations']:
            print(f"  • {rec}")


if __name__ == "__main__":
    test_disease_detector()