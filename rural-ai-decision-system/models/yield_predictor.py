"""
Lightweight Crop Yield Predictor for Rural Agriculture Decision Support System.

This module provides explainable, rule-based yield predictions using simple
scoring logic. Designed to be conservative and prioritize farmer safety over
maximum output predictions.

Author: Agriculture Decision Support System
Version: 1.0
"""

import sys
import os

# Add config directory to path for importing settings
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from config.settings import (
        TEMP_OPTIMAL_MIN, TEMP_OPTIMAL_MAX, TEMP_CRITICAL_LOW, TEMP_CRITICAL_HIGH,
        RAINFALL_LOW_THRESHOLD, RAINFALL_MEDIUM_THRESHOLD, RAINFALL_HIGH_THRESHOLD,
        SOIL_TYPES, YIELD_CONFIDENCE_HIGH, YIELD_CONFIDENCE_MEDIUM, YIELD_CONFIDENCE_LOW
    )
except ImportError:
    # Fallback values if config is not available
    TEMP_OPTIMAL_MIN = 15.0
    TEMP_OPTIMAL_MAX = 30.0
    TEMP_CRITICAL_LOW = 5.0
    TEMP_CRITICAL_HIGH = 40.0
    RAINFALL_LOW_THRESHOLD = 10.0
    RAINFALL_MEDIUM_THRESHOLD = 50.0
    RAINFALL_HIGH_THRESHOLD = 100.0
    YIELD_CONFIDENCE_HIGH = 0.85
    YIELD_CONFIDENCE_MEDIUM = 0.65
    YIELD_CONFIDENCE_LOW = 0.45
    SOIL_TYPES = {
        'CLAY': {'water_retention': 0.45},
        'LOAM': {'water_retention': 0.35},
        'SANDY': {'water_retention': 0.15},
        'SILT': {'water_retention': 0.40}
    }


def predict_yield(inputs: dict) -> dict:
    """
    Predict crop yield using rule-based scoring system.
    
    Args:
        inputs (dict): Dictionary containing:
            - rainfall_mm (float): Recent rainfall in millimeters
            - temperature_c (float): Current temperature in Celsius
            - soil_type (str): Soil type ('CLAY', 'LOAM', 'SANDY', 'SILT')
            - crop_type (str): Type of crop being grown
            
    Returns:
        dict: Prediction results containing:
            - expected_yield_percentage (float): Expected yield as percentage (0-100)
            - confidence_score (float): Confidence in prediction (0-1)
            - explanation (str): Plain English explanation of the prediction
    """
    
    # Extract and validate inputs
    rainfall = inputs.get('rainfall_mm', 0.0)
    temperature = inputs.get('temperature_c', 20.0)
    soil_type = inputs.get('soil_type', 'LOAM').upper()
    crop_type = inputs.get('crop_type', 'unknown').lower()
    
    # Initialize scoring components
    temperature_score = 0.0
    rainfall_score = 0.0
    soil_score = 0.0
    crop_bonus = 0.0
    
    # Track explanation components
    explanations = []
    warning_factors = []
    
    # =============================================================================
    # TEMPERATURE SCORING (40% weight in final calculation)
    # =============================================================================
    if temperature < TEMP_CRITICAL_LOW:
        temperature_score = 0.1  # Severe frost damage risk
        explanations.append(f"Critical low temperature ({temperature}°C) poses severe frost risk")
        warning_factors.append("frost_risk")
    elif temperature < TEMP_OPTIMAL_MIN:
        temperature_score = 0.4  # Below optimal but survivable
        explanations.append(f"Temperature ({temperature}°C) is below optimal range")
    elif temperature <= TEMP_OPTIMAL_MAX:
        temperature_score = 1.0  # Optimal temperature range
        explanations.append(f"Temperature ({temperature}°C) is in optimal range")
    elif temperature < TEMP_CRITICAL_HIGH:
        temperature_score = 0.6  # Above optimal but manageable
        explanations.append(f"Temperature ({temperature}°C) is above optimal but manageable")
    else:
        temperature_score = 0.2  # Extreme heat stress
        explanations.append(f"Critical high temperature ({temperature}°C) causes severe heat stress")
        warning_factors.append("heat_stress")
    
    # =============================================================================
    # RAINFALL SCORING (35% weight in final calculation)
    # =============================================================================
    if rainfall < RAINFALL_LOW_THRESHOLD:
        rainfall_score = 0.3  # Drought stress, irrigation needed
        explanations.append(f"Low rainfall ({rainfall}mm) indicates drought stress")
        warning_factors.append("drought_stress")
    elif rainfall < RAINFALL_MEDIUM_THRESHOLD:
        rainfall_score = 0.7  # Moderate rainfall, some irrigation may be needed
        explanations.append(f"Moderate rainfall ({rainfall}mm) may require supplemental irrigation")
    elif rainfall < RAINFALL_HIGH_THRESHOLD:
        rainfall_score = 1.0  # Good rainfall levels
        explanations.append(f"Good rainfall levels ({rainfall}mm) for crop growth")
    else:
        rainfall_score = 0.5  # Excessive rainfall, flooding risk
        explanations.append(f"High rainfall ({rainfall}mm) poses flooding and disease risks")
        warning_factors.append("flood_risk")
    
    # =============================================================================
    # SOIL TYPE SCORING (20% weight in final calculation)
    # =============================================================================
    if soil_type in SOIL_TYPES:
        water_retention = SOIL_TYPES[soil_type]['water_retention']
        
        if soil_type == 'LOAM':
            soil_score = 1.0  # Best soil type for most crops
            explanations.append("Loam soil provides excellent growing conditions")
        elif soil_type == 'CLAY':
            soil_score = 0.8  # Good water retention but drainage issues
            explanations.append("Clay soil has good water retention but may have drainage issues")
        elif soil_type == 'SILT':
            soil_score = 0.9  # Good fertility and water retention
            explanations.append("Silt soil provides good fertility and water retention")
        elif soil_type == 'SANDY':
            soil_score = 0.6  # Poor water retention, frequent irrigation needed
            explanations.append("Sandy soil requires frequent irrigation due to poor water retention")
            warning_factors.append("high_irrigation_need")
    else:
        soil_score = 0.5  # Unknown soil type, conservative estimate
        explanations.append(f"Unknown soil type ({soil_type}), using conservative estimate")
        warning_factors.append("unknown_soil")
    
    # =============================================================================
    # CROP-SPECIFIC ADJUSTMENTS (5% weight in final calculation)
    # =============================================================================
    crop_adjustments = {
        'rice': 0.1,      # Water-intensive crop, bonus in high rainfall
        'wheat': 0.0,     # Standard crop, no adjustment
        'cotton': -0.05,  # Sensitive to water stress
        'sugarcane': 0.05, # Hardy crop with good yield potential
        'maize': 0.0,     # Standard crop, no adjustment
        'millet': 0.1,    # Drought-resistant crop
        'soybean': 0.0,   # Standard crop, no adjustment
        'groundnut': -0.05, # Sensitive to excess water
        'potato': 0.0,    # Standard crop, no adjustment
        'mustard': 0.0,   # Standard crop, no adjustment
        'jute': 0.05,     # Thrives in high humidity
        'chili': -0.1,    # Sensitive to weather extremes
        'coconut': 0.05,  # Hardy perennial crop
        'tea': 0.0        # Standard crop, no adjustment
    }
    
    crop_bonus = crop_adjustments.get(crop_type, -0.1)  # Unknown crops get penalty
    
    if crop_type in crop_adjustments:
        if crop_bonus > 0:
            explanations.append(f"{crop_type.title()} is well-suited to current conditions")
        elif crop_bonus < 0:
            explanations.append(f"{crop_type.title()} is sensitive to current weather conditions")
    else:
        explanations.append(f"Unknown crop type ({crop_type}), applying conservative penalty")
        warning_factors.append("unknown_crop")
    
    # =============================================================================
    # CALCULATE FINAL YIELD PERCENTAGE
    # =============================================================================
    # Weighted combination of all factors (conservative approach)
    base_yield = (
        temperature_score * 0.40 +  # Temperature has highest impact
        rainfall_score * 0.35 +     # Rainfall second most important
        soil_score * 0.20 +         # Soil type moderately important
        crop_bonus * 0.05           # Crop-specific minor adjustment
    )
    
    # Apply conservative safety margin (reduce by 10% for farmer safety)
    safety_margin = 0.90
    conservative_yield = base_yield * safety_margin
    
    # Convert to percentage (0-100) with conservative cap at 85%
    expected_yield_percentage = min(conservative_yield * 85.0, 85.0)
    
    # Ensure minimum yield is not negative
    expected_yield_percentage = max(expected_yield_percentage, 5.0)
    
    # =============================================================================
    # CALCULATE CONFIDENCE SCORE
    # =============================================================================
    confidence_factors = []
    
    # High confidence conditions
    if (TEMP_OPTIMAL_MIN <= temperature <= TEMP_OPTIMAL_MAX and
        RAINFALL_LOW_THRESHOLD <= rainfall <= RAINFALL_HIGH_THRESHOLD and
        soil_type in SOIL_TYPES and
        crop_type in crop_adjustments):
        base_confidence = YIELD_CONFIDENCE_HIGH
        confidence_factors.append("optimal_conditions")
    
    # Medium confidence conditions
    elif (TEMP_CRITICAL_LOW < temperature < TEMP_CRITICAL_HIGH and
          rainfall > 0 and
          soil_type in SOIL_TYPES):
        base_confidence = YIELD_CONFIDENCE_MEDIUM
        confidence_factors.append("acceptable_conditions")
    
    # Low confidence conditions
    else:
        base_confidence = YIELD_CONFIDENCE_LOW
        confidence_factors.append("suboptimal_conditions")
    
    # Reduce confidence for each warning factor
    confidence_penalty = len(warning_factors) * 0.1
    confidence_score = max(base_confidence - confidence_penalty, 0.2)
    
    # =============================================================================
    # GENERATE EXPLANATION
    # =============================================================================
    explanation_parts = [
        f"Predicted yield: {expected_yield_percentage:.1f}% of potential maximum.",
        f"Confidence level: {confidence_score:.2f} ({_get_confidence_level(confidence_score)})."
    ]
    
    # Add main factors explanation
    explanation_parts.append("Key factors:")
    explanation_parts.extend([f"• {exp}" for exp in explanations])
    
    # Add warnings if any
    if warning_factors:
        explanation_parts.append("Caution factors:")
        warning_messages = {
            'frost_risk': '• Risk of frost damage - consider protective measures',
            'heat_stress': '• Heat stress risk - ensure adequate irrigation and shade',
            'drought_stress': '• Drought conditions - irrigation strongly recommended',
            'flood_risk': '• Flooding risk - ensure proper drainage',
            'high_irrigation_need': '• Frequent irrigation required due to soil type',
            'unknown_soil': '• Soil type unknown - recommendation may be less accurate',
            'unknown_crop': '• Crop type unknown - using conservative estimates'
        }
        for factor in warning_factors:
            if factor in warning_messages:
                explanation_parts.append(warning_messages[factor])
    
    # Add conservative approach note
    explanation_parts.append(
        "Note: Predictions use conservative estimates to prioritize farmer safety and risk reduction."
    )
    
    final_explanation = " ".join(explanation_parts)
    
    return {
        'expected_yield_percentage': round(expected_yield_percentage, 1),
        'confidence_score': round(confidence_score, 2),
        'explanation': final_explanation
    }


def _get_confidence_level(confidence_score: float) -> str:
    """
    Convert numerical confidence score to descriptive level.
    
    Args:
        confidence_score (float): Confidence score between 0 and 1
        
    Returns:
        str: Descriptive confidence level
    """
    if confidence_score >= YIELD_CONFIDENCE_HIGH:
        return "High"
    elif confidence_score >= YIELD_CONFIDENCE_MEDIUM:
        return "Medium"
    elif confidence_score >= YIELD_CONFIDENCE_LOW:
        return "Low"
    else:
        return "Very Low"


def validate_inputs(inputs: dict) -> tuple[bool, str]:
    """
    Validate input parameters for yield prediction.
    
    Args:
        inputs (dict): Input parameters to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['rainfall_mm', 'temperature_c', 'soil_type', 'crop_type']
    
    # Check for required fields
    for field in required_fields:
        if field not in inputs:
            return False, f"Missing required field: {field}"
    
    # Validate data types and ranges
    try:
        rainfall = float(inputs['rainfall_mm'])
        temperature = float(inputs['temperature_c'])
        
        if rainfall < 0:
            return False, "Rainfall cannot be negative"
        
        if rainfall > 500:  # Extremely high rainfall threshold
            return False, "Rainfall value seems unrealistic (>500mm)"
        
        if temperature < -20 or temperature > 60:
            return False, "Temperature value outside realistic range (-20°C to 60°C)"
            
    except (ValueError, TypeError):
        return False, "Rainfall and temperature must be numeric values"
    
    # Validate soil type
    soil_type = inputs['soil_type'].upper()
    valid_soils = ['CLAY', 'LOAM', 'SANDY', 'SILT']
    if soil_type not in valid_soils and soil_type != 'UNKNOWN':
        return False, f"Invalid soil type. Must be one of: {', '.join(valid_soils)}"
    
    return True, "Inputs are valid"


# Example usage and testing function
def test_yield_predictor():
    """
    Test function to demonstrate yield predictor functionality.
    """
    test_cases = [
        {
            'name': 'Optimal Conditions',
            'inputs': {
                'rainfall_mm': 25.0,
                'temperature_c': 25.0,
                'soil_type': 'LOAM',
                'crop_type': 'wheat'
            }
        },
        {
            'name': 'Drought Conditions',
            'inputs': {
                'rainfall_mm': 2.0,
                'temperature_c': 38.0,
                'soil_type': 'SANDY',
                'crop_type': 'millet'
            }
        },
        {
            'name': 'Flood Conditions',
            'inputs': {
                'rainfall_mm': 150.0,
                'temperature_c': 26.0,
                'soil_type': 'CLAY',
                'crop_type': 'rice'
            }
        }
    ]
    
    print("Yield Predictor Test Results:")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\nTest Case: {test_case['name']}")
        print("-" * 30)
        
        # Validate inputs
        is_valid, message = validate_inputs(test_case['inputs'])
        if not is_valid:
            print(f"Input validation failed: {message}")
            continue
        
        # Make prediction
        result = predict_yield(test_case['inputs'])
        
        print(f"Expected Yield: {result['expected_yield_percentage']}%")
        print(f"Confidence: {result['confidence_score']}")
        print(f"Explanation: {result['explanation']}")


if __name__ == "__main__":
    test_yield_predictor()