"""
Conservative Rule-Based Farming Decision Engine for Rural Agriculture Decision Support System.

This module provides explainable, safety-first farming decisions based on yield predictions,
disease risk assessments, and water availability. Designed to prioritize farmer economic
safety and risk reduction over maximum output.

Author: Agriculture Decision Support System
Version: 1.0
"""

import sys
import os

# Add config directory to path for importing settings
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from config.settings import (
        YIELD_CONFIDENCE_HIGH, YIELD_CONFIDENCE_MEDIUM, YIELD_CONFIDENCE_LOW,
        IRRIGATION_MAX_WEEKLY, SOIL_MOISTURE_CRITICAL, SOIL_MOISTURE_LOW,
        ECONOMIC_RISK_THRESHOLD, PROFIT_MARGIN_MIN
    )
except ImportError:
    # Fallback values if config is not available
    YIELD_CONFIDENCE_HIGH = 0.85
    YIELD_CONFIDENCE_MEDIUM = 0.65
    YIELD_CONFIDENCE_LOW = 0.45
    IRRIGATION_MAX_WEEKLY = 100.0
    SOIL_MOISTURE_CRITICAL = 0.20
    SOIL_MOISTURE_LOW = 0.40
    ECONOMIC_RISK_THRESHOLD = 0.30
    PROFIT_MARGIN_MIN = 0.15


def make_farming_decision(inputs: dict) -> dict:
    """
    Make conservative farming decisions based on yield predictions, disease risk, and water availability.
    
    Args:
        inputs (dict): Dictionary containing:
            - yield_result (dict): Results from yield_predictor.predict_yield()
            - disease_result (dict): Results from disease_detector.detect_disease()
            - available_water_mm (float): Available water for irrigation
            - rainfall_mm (float): Recent rainfall amount
            - soil_type (str, optional): Soil type for water calculations
            - crop_type (str, optional): Crop type for specific considerations
            
    Returns:
        dict: Farming decision results containing:
            - decision (str): Main decision ('PROCEED', 'REDUCE_INPUTS', 'AVOID_FARMING')
            - risk_level (str): Overall risk level ('LOW', 'MEDIUM', 'HIGH')
            - explanation (str): Plain English explanation of the decision
            - reasoning (list): List of rule-based reasons for the decision
            - recommendations (list): Specific action recommendations
    """
    
    # Extract and validate inputs
    yield_result = inputs.get('yield_result', {})
    disease_result = inputs.get('disease_result', {})
    available_water = inputs.get('available_water_mm', 0.0)
    rainfall = inputs.get('rainfall_mm', 0.0)
    soil_type = inputs.get('soil_type', 'LOAM').upper()
    crop_type = inputs.get('crop_type', 'unknown').lower()
    
    # Initialize decision components
    decision_factors = []
    risk_factors = []
    safety_concerns = []
    recommendations = []
    
    # Extract key metrics from sub-module results
    yield_percentage = yield_result.get('expected_yield_percentage', 0.0)
    yield_confidence = yield_result.get('confidence_score', 0.0)
    disease_risk_level = disease_result.get('disease_risk_level', 'HIGH')
    disease_risk_score = disease_result.get('disease_risk_score', 1.0)
    
    # =============================================================================
    # RULE 1: CRITICAL SAFETY THRESHOLDS (Immediate AVOID_FARMING triggers)
    # =============================================================================
    
    # Rule 1a: Extremely high disease risk
    if disease_risk_level == 'HIGH' and disease_risk_score >= 0.8:
        safety_concerns.append("Critical disease risk detected - immediate crop protection needed")
        decision_factors.append("AVOID: Disease risk exceeds safe farming threshold")
        recommendations.extend([
            "Do not plant new crops until disease risk reduces",
            "Focus on treating existing crops if any",
            "Consult agricultural extension officer immediately"
        ])
    
    # Rule 1b: Severe water shortage
    water_shortage_threshold = 20.0  # Minimum water needed for basic farming (mm)
    if available_water < water_shortage_threshold and rainfall < 5.0:
        safety_concerns.append(f"Severe water shortage - only {available_water:.1f}mm available")
        decision_factors.append("AVOID: Insufficient water for safe crop cultivation")
        recommendations.extend([
            "Postpone planting until water situation improves",
            "Focus on water conservation and collection",
            "Consider drought-resistant crops for future planting"
        ])
    
    # Rule 1c: Extremely low yield with high uncertainty
    if yield_percentage < 20.0 and yield_confidence < YIELD_CONFIDENCE_LOW:
        safety_concerns.append("Extremely low yield prediction with high uncertainty")
        decision_factors.append("AVOID: Yield too low to justify farming investment")
        recommendations.append("Wait for more favorable conditions before investing in farming")
    
    # =============================================================================
    # RULE 2: MODERATE RISK THRESHOLDS (REDUCE_INPUTS triggers)
    # =============================================================================
    
    # Rule 2a: Medium disease risk with other concerns
    if disease_risk_level == 'MEDIUM' and (yield_confidence < YIELD_CONFIDENCE_MEDIUM or available_water < 40.0):
        risk_factors.append("Medium disease risk combined with other limiting factors")
        decision_factors.append("REDUCE: Multiple moderate risk factors present")
        recommendations.extend([
            "Reduce planting area by 30-50%",
            "Focus on disease-resistant crop varieties",
            "Implement enhanced monitoring protocols"
        ])
    
    # Rule 2b: Water stress conditions
    moderate_water_threshold = 50.0  # Water level requiring input reduction
    if available_water < moderate_water_threshold and rainfall < 15.0:
        risk_factors.append(f"Water stress conditions - {available_water:.1f}mm available, {rainfall:.1f}mm rainfall")
        decision_factors.append("REDUCE: Water availability requires conservative approach")
        recommendations.extend([
            "Reduce crop area to match water availability",
            "Prioritize high-value, water-efficient crops",
            "Implement water-saving irrigation techniques"
        ])
    
    # Rule 2c: Low yield with acceptable confidence
    if 20.0 <= yield_percentage < 40.0 and yield_confidence >= YIELD_CONFIDENCE_LOW:
        risk_factors.append(f"Low expected yield ({yield_percentage:.1f}%) but acceptable confidence")
        decision_factors.append("REDUCE: Low yield requires reduced investment")
        recommendations.extend([
            "Plant smaller area to minimize losses",
            "Choose low-input, hardy crop varieties",
            "Focus on soil improvement for future seasons"
        ])
    
    # =============================================================================
    # RULE 3: ECONOMIC VIABILITY ASSESSMENT
    # =============================================================================
    
    # Rule 3a: Economic risk calculation
    # Simplified economic model: higher yield and confidence = lower economic risk
    economic_risk = _calculate_economic_risk(yield_percentage, yield_confidence, disease_risk_score)
    
    if economic_risk > 0.7:  # High economic risk threshold
        safety_concerns.append(f"High economic risk ({economic_risk:.2f}) - potential significant losses")
        decision_factors.append("AVOID: Economic risk exceeds acceptable threshold")
        recommendations.append("Investment not recommended under current conditions")
    elif economic_risk > 0.4:  # Moderate economic risk threshold
        risk_factors.append(f"Moderate economic risk ({economic_risk:.2f}) - reduced investment advised")
        decision_factors.append("REDUCE: Economic conditions require conservative investment")
        recommendations.append("Reduce investment and focus on risk mitigation")
    
    # =============================================================================
    # RULE 4: POSITIVE INDICATORS (PROCEED conditions)
    # =============================================================================
    
    proceed_indicators = []
    
    # Rule 4a: Good yield prospects with high confidence
    if yield_percentage >= 60.0 and yield_confidence >= YIELD_CONFIDENCE_HIGH:
        proceed_indicators.append(f"Good yield prospects ({yield_percentage:.1f}%) with high confidence")
    
    # Rule 4b: Low disease risk
    if disease_risk_level == 'LOW':
        proceed_indicators.append("Low disease risk supports safe farming")
    
    # Rule 4c: Adequate water availability
    if available_water >= 60.0 or rainfall >= 25.0:
        proceed_indicators.append("Adequate water availability for crop cultivation")
    
    # Rule 4d: Moderate conditions with good confidence
    if (yield_percentage >= 45.0 and yield_confidence >= YIELD_CONFIDENCE_MEDIUM and 
        disease_risk_level != 'HIGH' and available_water >= 40.0):
        proceed_indicators.append("Moderate conditions with acceptable risk levels")
    
    # =============================================================================
    # RULE 5: FINAL DECISION LOGIC (Conservative hierarchy)
    # =============================================================================
    
    # Priority 1: Safety concerns override everything
    if safety_concerns:
        final_decision = 'AVOID_FARMING'
        overall_risk = 'HIGH'
        decision_factors.extend([f"SAFETY: {concern}" for concern in safety_concerns])
    
    # Priority 2: Multiple risk factors suggest input reduction
    elif len(risk_factors) >= 2 or (len(risk_factors) >= 1 and not proceed_indicators):
        final_decision = 'REDUCE_INPUTS'
        overall_risk = 'MEDIUM'
        decision_factors.extend([f"RISK: {factor}" for factor in risk_factors])
    
    # Priority 3: Proceed only with clear positive indicators
    elif len(proceed_indicators) >= 2:
        final_decision = 'PROCEED'
        overall_risk = 'LOW'
        decision_factors.extend([f"POSITIVE: {indicator}" for indicator in proceed_indicators])
        recommendations.extend([
            "Proceed with standard farming practices",
            "Maintain regular monitoring of crops and conditions",
            "Be prepared to adjust if conditions change"
        ])
    
    # Priority 4: Default to conservative approach when uncertain
    else:
        final_decision = 'REDUCE_INPUTS'
        overall_risk = 'MEDIUM'
        decision_factors.append("DEFAULT: Insufficient positive indicators for full farming recommendation")
        recommendations.append("Conservative approach recommended due to mixed conditions")
    
    # =============================================================================
    # RULE 6: DECISION-SPECIFIC RECOMMENDATIONS
    # =============================================================================
    
    _add_decision_specific_recommendations(
        final_decision, overall_risk, yield_percentage, disease_risk_level, 
        available_water, recommendations
    )
    
    # =============================================================================
    # RULE 7: SEASONAL AND TIMING CONSIDERATIONS
    # =============================================================================
    
    _add_timing_recommendations(
        crop_type, disease_risk_level, available_water, rainfall, recommendations
    )
    
    # =============================================================================
    # GENERATE EXPLANATION
    # =============================================================================
    
    explanation = _generate_decision_explanation(
        final_decision, overall_risk, yield_percentage, yield_confidence,
        disease_risk_level, available_water, rainfall
    )
    
    return {
        'decision': final_decision,
        'risk_level': overall_risk,
        'explanation': explanation,
        'reasoning': decision_factors,
        'recommendations': recommendations
    }


def _calculate_economic_risk(yield_percentage: float, yield_confidence: float, disease_risk_score: float) -> float:
    """
    Calculate economic risk based on yield prospects and disease risk.
    
    Higher yield and confidence = lower economic risk
    Higher disease risk = higher economic risk
    """
    # Normalize yield percentage to 0-1 scale
    yield_factor = yield_percentage / 100.0
    
    # Calculate base economic risk (inverse of yield potential)
    base_risk = 1.0 - (yield_factor * yield_confidence)
    
    # Add disease risk component
    disease_impact = disease_risk_score * 0.3  # Disease contributes 30% to economic risk
    
    # Combine factors
    total_economic_risk = min(base_risk + disease_impact, 1.0)
    
    return total_economic_risk


def _add_decision_specific_recommendations(decision: str, risk_level: str, yield_percentage: float,
                                        disease_risk_level: str, available_water: float, 
                                        recommendations: list):
    """
    Add recommendations specific to the farming decision made.
    """
    if decision == 'PROCEED':
        recommendations.extend([
            "Monitor weather conditions regularly",
            "Maintain emergency water reserves",
            "Keep disease management supplies ready"
        ])
        
        if yield_percentage < 70.0:
            recommendations.append("Consider crop insurance to protect against losses")
    
    elif decision == 'REDUCE_INPUTS':
        recommendations.extend([
            "Start with 50-70% of planned crop area",
            "Choose proven, low-risk crop varieties",
            "Prioritize fields with best soil and water access"
        ])
        
        if disease_risk_level != 'LOW':
            recommendations.append("Implement preventive disease management from start")
    
    else:  # AVOID_FARMING
        recommendations.extend([
            "Focus on soil preparation and improvement",
            "Repair and maintain farming equipment",
            "Plan for better conditions in next season"
        ])
        
        if available_water < 30.0:
            recommendations.append("Invest in water harvesting and storage systems")


def _add_timing_recommendations(crop_type: str, disease_risk_level: str, 
                              available_water: float, rainfall: float, recommendations: list):
    """
    Add timing and seasonal recommendations based on conditions.
    """
    # Water-based timing recommendations
    if available_water < 40.0 and rainfall < 10.0:
        recommendations.append("Wait for better water conditions or monsoon arrival")
    
    # Disease-based timing recommendations
    if disease_risk_level == 'HIGH':
        recommendations.extend([
            "Delay planting until disease pressure reduces",
            "Consider off-season crops with lower disease susceptibility"
        ])
    
    # Crop-specific timing advice
    drought_resistant_crops = ['millet', 'sorghum', 'groundnut']
    water_intensive_crops = ['rice', 'sugarcane']
    
    if crop_type in water_intensive_crops and available_water < 60.0:
        recommendations.append(f"Consider switching from {crop_type} to more water-efficient crops")
    elif crop_type in drought_resistant_crops and available_water < 30.0:
        recommendations.append(f"{crop_type.title()} is suitable for current water conditions")


def _generate_decision_explanation(decision: str, risk_level: str, yield_percentage: float,
                                 yield_confidence: float, disease_risk_level: str,
                                 available_water: float, rainfall: float) -> str:
    """
    Generate comprehensive explanation of the farming decision.
    """
    explanation_parts = [
        f"Farming Decision: {decision.replace('_', ' ')} (Risk Level: {risk_level})."
    ]
    
    # Add key factors summary
    explanation_parts.append(
        f"Key factors: {yield_percentage:.1f}% expected yield "
        f"(confidence: {yield_confidence:.2f}), "
        f"{disease_risk_level.lower()} disease risk, "
        f"{available_water:.1f}mm water available, "
        f"{rainfall:.1f}mm recent rainfall."
    )
    
    # Add decision rationale
    if decision == 'PROCEED':
        explanation_parts.append(
            "Conditions support farming with standard practices and regular monitoring."
        )
    elif decision == 'REDUCE_INPUTS':
        explanation_parts.append(
            "Mixed conditions require conservative approach with reduced investment and enhanced risk management."
        )
    else:  # AVOID_FARMING
        explanation_parts.append(
            "Current conditions pose significant risks that outweigh potential benefits. "
            "Postponing farming activities is recommended for farmer safety and economic protection."
        )
    
    # Add conservative approach note
    explanation_parts.append(
        "This recommendation prioritizes farmer safety and economic risk reduction over maximum output potential."
    )
    
    return " ".join(explanation_parts)


def validate_inputs(inputs: dict) -> tuple[bool, str]:
    """
    Validate input parameters for farming decision making.
    
    Args:
        inputs (dict): Input parameters to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['yield_result', 'disease_result', 'available_water_mm', 'rainfall_mm']
    
    # Check for required fields
    for field in required_fields:
        if field not in inputs:
            return False, f"Missing required field: {field}"
    
    # Validate yield_result structure
    yield_result = inputs.get('yield_result', {})
    required_yield_fields = ['expected_yield_percentage', 'confidence_score']
    for field in required_yield_fields:
        if field not in yield_result:
            return False, f"Missing field in yield_result: {field}"
    
    # Validate disease_result structure
    disease_result = inputs.get('disease_result', {})
    required_disease_fields = ['disease_risk_level', 'disease_risk_score']
    for field in required_disease_fields:
        if field not in disease_result:
            return False, f"Missing field in disease_result: {field}"
    
    # Validate numeric ranges
    try:
        available_water = float(inputs['available_water_mm'])
        rainfall = float(inputs['rainfall_mm'])
        
        if available_water < 0:
            return False, "Available water cannot be negative"
        
        if rainfall < 0:
            return False, "Rainfall cannot be negative"
        
        if available_water > 1000:  # Unrealistic water availability
            return False, "Available water value seems unrealistic (>1000mm)"
            
    except (ValueError, TypeError):
        return False, "Water and rainfall values must be numeric"
    
    return True, "Inputs are valid"


# Example usage and testing function
def test_farming_rules():
    """
    Test function to demonstrate farming rules functionality.
    """
    test_cases = [
        {
            'name': 'Optimal Conditions - Should Proceed',
            'inputs': {
                'yield_result': {
                    'expected_yield_percentage': 75.0,
                    'confidence_score': 0.85
                },
                'disease_result': {
                    'disease_risk_level': 'LOW',
                    'disease_risk_score': 0.2
                },
                'available_water_mm': 80.0,
                'rainfall_mm': 30.0,
                'crop_type': 'wheat'
            }
        },
        {
            'name': 'High Disease Risk - Should Avoid',
            'inputs': {
                'yield_result': {
                    'expected_yield_percentage': 60.0,
                    'confidence_score': 0.70
                },
                'disease_result': {
                    'disease_risk_level': 'HIGH',
                    'disease_risk_score': 0.85
                },
                'available_water_mm': 50.0,
                'rainfall_mm': 15.0,
                'crop_type': 'rice'
            }
        },
        {
            'name': 'Water Shortage - Should Reduce',
            'inputs': {
                'yield_result': {
                    'expected_yield_percentage': 45.0,
                    'confidence_score': 0.60
                },
                'disease_result': {
                    'disease_risk_level': 'MEDIUM',
                    'disease_risk_score': 0.5
                },
                'available_water_mm': 25.0,
                'rainfall_mm': 5.0,
                'crop_type': 'cotton'
            }
        }
    ]
    
    print("Farming Rules Test Results:")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\nTest Case: {test_case['name']}")
        print("-" * 40)
        
        # Validate inputs
        is_valid, message = validate_inputs(test_case['inputs'])
        if not is_valid:
            print(f"Input validation failed: {message}")
            continue
        
        # Make farming decision
        result = make_farming_decision(test_case['inputs'])
        
        print(f"Decision: {result['decision']}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Explanation: {result['explanation']}")
        print("Reasoning:")
        for reason in result['reasoning']:
            print(f"  • {reason}")
        print("Recommendations:")
        for rec in result['recommendations']:
            print(f"  • {rec}")


if __name__ == "__main__":
    test_farming_rules()