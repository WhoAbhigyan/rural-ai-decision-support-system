"""
Explainable Conservative Risk Assessment Module for Rural Agriculture Decision Support System.

This module provides comprehensive risk assessment by combining yield predictions, disease risks,
irrigation concerns, and weather uncertainties into a single, explainable risk score. Designed
to prioritize farmer safety through conservative risk estimation.

Author: Agriculture Decision Support System
Version: 1.0
"""

import sys
import os

# Add config directory to path for importing settings
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from config.settings import (
        RISK_LOW, RISK_MEDIUM, RISK_HIGH,
        YIELD_CONFIDENCE_HIGH, YIELD_CONFIDENCE_MEDIUM, YIELD_CONFIDENCE_LOW
    )
except ImportError:
    # Fallback values if config is not available
    RISK_LOW = 0.25
    RISK_MEDIUM = 0.60
    RISK_HIGH = 0.85
    YIELD_CONFIDENCE_HIGH = 0.85
    YIELD_CONFIDENCE_MEDIUM = 0.65
    YIELD_CONFIDENCE_LOW = 0.45


def assess_overall_risk(inputs: dict) -> dict:
    """
    Assess overall farming risk by combining multiple risk factors with conservative bias.
    
    Args:
        inputs (dict): Dictionary containing:
            - yield_result (dict): Results from yield predictor
            - disease_result (dict): Results from disease detector
            - irrigation_result (dict): Results from irrigation optimizer
            - weather_uncertainty (float, optional): Weather prediction uncertainty (0-1)
            - farmer_experience (str, optional): Farmer experience level
            - economic_buffer (float, optional): Economic safety buffer (0-1)
            
    Returns:
        dict: Risk assessment results containing:
            - overall_risk_score (float): Combined risk score (0-1)
            - overall_risk_level (str): Risk level ('LOW', 'MEDIUM', 'HIGH')
            - risk_breakdown (dict): Detailed breakdown of risk components
            - explanation (str): Plain English explanation of risk assessment
            - risk_mitigation_suggestions (list): Specific risk reduction recommendations
            - confidence_in_assessment (float): Confidence in the risk assessment itself
    """
    
    # Extract input components
    yield_result = inputs.get('yield_result', {})
    disease_result = inputs.get('disease_result', {})
    irrigation_result = inputs.get('irrigation_result', {})
    weather_uncertainty = inputs.get('weather_uncertainty', 0.2)  # Default moderate uncertainty
    farmer_experience = inputs.get('farmer_experience', 'medium').lower()
    economic_buffer = inputs.get('economic_buffer', 0.3)  # Default moderate buffer
    
    # Initialize risk calculation components
    risk_components = {}
    explanation_parts = []
    mitigation_suggestions = []
    calculation_steps = []
    
    # =============================================================================
    # COMPONENT 1: YIELD-BASED RISK ASSESSMENT (30% weight)
    # =============================================================================
    
    yield_risk_score, yield_explanation = _assess_yield_risk(yield_result, calculation_steps)
    risk_components['yield_risk'] = {
        'score': yield_risk_score,
        'weight': 0.30,
        'explanation': yield_explanation
    }
    
    # =============================================================================
    # COMPONENT 2: DISEASE-BASED RISK ASSESSMENT (35% weight - highest priority)
    # =============================================================================
    
    disease_risk_score, disease_explanation = _assess_disease_risk(disease_result, calculation_steps)
    risk_components['disease_risk'] = {
        'score': disease_risk_score,
        'weight': 0.35,
        'explanation': disease_explanation
    }
    
    # =============================================================================
    # COMPONENT 3: WATER/IRRIGATION RISK ASSESSMENT (25% weight)
    # =============================================================================
    
    water_risk_score, water_explanation = _assess_water_risk(irrigation_result, calculation_steps)
    risk_components['water_risk'] = {
        'score': water_risk_score,
        'weight': 0.25,
        'explanation': water_explanation
    }
    
    # =============================================================================
    # COMPONENT 4: WEATHER UNCERTAINTY RISK (10% weight)
    # =============================================================================
    
    weather_risk_score, weather_explanation = _assess_weather_uncertainty_risk(
        weather_uncertainty, calculation_steps
    )
    risk_components['weather_uncertainty_risk'] = {
        'score': weather_risk_score,
        'weight': 0.10,
        'explanation': weather_explanation
    }
    
    # =============================================================================
    # STEP 5: CALCULATE BASE WEIGHTED RISK SCORE
    # =============================================================================
    
    base_risk_score = 0.0
    for component_name, component_data in risk_components.items():
        weighted_contribution = component_data['score'] * component_data['weight']
        base_risk_score += weighted_contribution
        calculation_steps.append(
            f"{component_name}: {component_data['score']:.2f} × {component_data['weight']:.2f} = {weighted_contribution:.3f}"
        )
    
    calculation_steps.append(f"Base weighted risk score: {base_risk_score:.3f}")
    
    # =============================================================================
    # STEP 6: APPLY CONSERVATIVE ADJUSTMENTS
    # =============================================================================
    
    # Conservative Adjustment 1: High-risk dominance rule
    # If any component has very high risk, it should dominate the overall assessment
    max_component_risk = max(comp['score'] for comp in risk_components.values())
    if max_component_risk >= 0.8:
        dominance_adjustment = (max_component_risk - base_risk_score) * 0.5
        base_risk_score += dominance_adjustment
        calculation_steps.append(f"High-risk dominance adjustment: +{dominance_adjustment:.3f}")
    
    # Conservative Adjustment 2: Low confidence penalty
    # Increase risk when confidence in predictions is low
    confidence_penalty = _calculate_confidence_penalty(yield_result, disease_result, calculation_steps)
    base_risk_score += confidence_penalty
    
    # Conservative Adjustment 3: Farmer experience adjustment
    experience_adjustment = _calculate_experience_adjustment(farmer_experience, calculation_steps)
    base_risk_score += experience_adjustment
    
    # Conservative Adjustment 4: Economic buffer adjustment
    economic_adjustment = _calculate_economic_adjustment(economic_buffer, calculation_steps)
    base_risk_score += economic_adjustment
    
    # Conservative Adjustment 5: Base conservative bias
    # Always add small conservative buffer to account for unknown unknowns
    conservative_buffer = 0.05
    base_risk_score += conservative_buffer
    calculation_steps.append(f"Conservative safety buffer: +{conservative_buffer:.3f}")
    
    # Ensure risk score stays within bounds
    final_risk_score = max(0.0, min(1.0, base_risk_score))
    calculation_steps.append(f"Final risk score (clamped): {final_risk_score:.3f}")
    
    # =============================================================================
    # STEP 7: DETERMINE RISK LEVEL
    # =============================================================================
    
    overall_risk_level = _determine_risk_level(final_risk_score)
    
    # =============================================================================
    # STEP 8: GENERATE RISK MITIGATION SUGGESTIONS
    # =============================================================================
    
    mitigation_suggestions = _generate_mitigation_suggestions(
        risk_components, overall_risk_level, yield_result, disease_result, irrigation_result
    )
    
    # =============================================================================
    # STEP 9: CALCULATE ASSESSMENT CONFIDENCE
    # =============================================================================
    
    assessment_confidence = _calculate_assessment_confidence(
        yield_result, disease_result, irrigation_result, weather_uncertainty
    )
    
    # =============================================================================
    # STEP 10: GENERATE COMPREHENSIVE EXPLANATION
    # =============================================================================
    
    explanation = _generate_risk_explanation(
        final_risk_score, overall_risk_level, risk_components, 
        calculation_steps, assessment_confidence
    )
    
    return {
        'overall_risk_score': round(final_risk_score, 3),
        'overall_risk_level': overall_risk_level,
        'risk_breakdown': risk_components,
        'explanation': explanation,
        'risk_mitigation_suggestions': mitigation_suggestions,
        'confidence_in_assessment': round(assessment_confidence, 2)
    }


def _assess_yield_risk(yield_result: dict, calculation_steps: list) -> tuple[float, str]:
    """
    Assess risk based on yield predictions and confidence.
    
    Low yield or low confidence = higher risk
    """
    yield_percentage = yield_result.get('expected_yield_percentage', 0.0)
    yield_confidence = yield_result.get('confidence_score', 0.0)
    
    # Convert yield percentage to risk (inverse relationship)
    # 0% yield = 1.0 risk, 100% yield = 0.0 risk
    yield_risk_base = 1.0 - (yield_percentage / 100.0)
    
    # Adjust risk based on confidence
    # Low confidence increases risk
    confidence_adjustment = (1.0 - yield_confidence) * 0.3  # Up to 30% increase for low confidence
    
    yield_risk = min(1.0, yield_risk_base + confidence_adjustment)
    
    calculation_steps.append(
        f"Yield risk: base {yield_risk_base:.3f} + confidence penalty {confidence_adjustment:.3f} = {yield_risk:.3f}"
    )
    
    # Generate explanation
    if yield_percentage < 30:
        explanation = f"Very low expected yield ({yield_percentage:.1f}%) creates high risk"
    elif yield_percentage < 50:
        explanation = f"Low expected yield ({yield_percentage:.1f}%) increases risk"
    elif yield_percentage < 70:
        explanation = f"Moderate expected yield ({yield_percentage:.1f}%) presents manageable risk"
    else:
        explanation = f"Good expected yield ({yield_percentage:.1f}%) reduces risk"
    
    if yield_confidence < YIELD_CONFIDENCE_LOW:
        explanation += f" with very low confidence ({yield_confidence:.2f})"
    elif yield_confidence < YIELD_CONFIDENCE_MEDIUM:
        explanation += f" with low confidence ({yield_confidence:.2f})"
    
    return yield_risk, explanation


def _assess_disease_risk(disease_result: dict, calculation_steps: list) -> tuple[float, str]:
    """
    Assess risk based on disease predictions.
    
    Disease risk gets highest weight due to potential for total crop loss.
    """
    disease_risk_level = disease_result.get('disease_risk_level', 'HIGH')
    disease_risk_score = disease_result.get('disease_risk_score', 1.0)
    
    # Convert disease risk level to numerical risk
    level_risk_mapping = {
        'LOW': 0.2,
        'MEDIUM': 0.6,
        'HIGH': 0.9
    }
    
    base_disease_risk = level_risk_mapping.get(disease_risk_level, 0.9)
    
    # Use the higher of level-based risk or numerical score for conservative approach
    final_disease_risk = max(base_disease_risk, disease_risk_score)
    
    calculation_steps.append(
        f"Disease risk: level-based {base_disease_risk:.3f}, score-based {disease_risk_score:.3f}, "
        f"using max = {final_disease_risk:.3f}"
    )
    
    # Generate explanation
    explanation = f"{disease_risk_level.lower()} disease risk (score: {disease_risk_score:.2f})"
    
    if disease_risk_level == 'HIGH':
        explanation += " - immediate crop protection needed"
    elif disease_risk_level == 'MEDIUM':
        explanation += " - enhanced monitoring required"
    else:
        explanation += " - standard disease management sufficient"
    
    return final_disease_risk, explanation


def _assess_water_risk(irrigation_result: dict, calculation_steps: list) -> tuple[float, str]:
    """
    Assess risk based on water stress and irrigation requirements.
    
    Water stress can severely impact crop survival and yield.
    """
    water_stress_level = irrigation_result.get('water_stress_level', 'HIGH')
    recommended_irrigation = irrigation_result.get('recommended_irrigation_mm', 0.0)
    
    # Convert water stress level to risk
    stress_risk_mapping = {
        'LOW': 0.15,
        'MEDIUM': 0.5,
        'HIGH': 0.85
    }
    
    base_water_risk = stress_risk_mapping.get(water_stress_level, 0.85)
    
    # Adjust risk based on irrigation adequacy
    # Very low irrigation recommendations suggest severe water constraints
    if recommended_irrigation < 5.0:  # Very low irrigation
        irrigation_adjustment = 0.2
    elif recommended_irrigation < 15.0:  # Low irrigation
        irrigation_adjustment = 0.1
    else:  # Adequate irrigation possible
        irrigation_adjustment = 0.0
    
    final_water_risk = min(1.0, base_water_risk + irrigation_adjustment)
    
    calculation_steps.append(
        f"Water risk: stress-based {base_water_risk:.3f} + irrigation penalty {irrigation_adjustment:.3f} = {final_water_risk:.3f}"
    )
    
    # Generate explanation
    explanation = f"{water_stress_level.lower()} water stress"
    
    if recommended_irrigation < 10.0:
        explanation += f" with limited irrigation capacity ({recommended_irrigation:.1f}mm)"
    else:
        explanation += f" with {recommended_irrigation:.1f}mm recommended irrigation"
    
    return final_water_risk, explanation


def _assess_weather_uncertainty_risk(weather_uncertainty: float, calculation_steps: list) -> tuple[float, str]:
    """
    Assess risk based on weather prediction uncertainty.
    
    Higher uncertainty increases risk due to unpredictable conditions.
    """
    # Weather uncertainty directly translates to risk
    # Cap at 0.8 to prevent weather uncertainty from dominating
    weather_risk = min(0.8, weather_uncertainty)
    
    calculation_steps.append(f"Weather uncertainty risk: {weather_risk:.3f}")
    
    # Generate explanation
    if weather_uncertainty > 0.7:
        explanation = f"High weather uncertainty ({weather_uncertainty:.2f}) increases unpredictability"
    elif weather_uncertainty > 0.4:
        explanation = f"Moderate weather uncertainty ({weather_uncertainty:.2f}) adds some risk"
    else:
        explanation = f"Low weather uncertainty ({weather_uncertainty:.2f}) provides stable conditions"
    
    return weather_risk, explanation


def _calculate_confidence_penalty(yield_result: dict, disease_result: dict, calculation_steps: list) -> float:
    """
    Calculate penalty for low confidence in predictions.
    
    Low confidence in critical predictions increases overall risk.
    """
    yield_confidence = yield_result.get('confidence_score', 0.5)
    
    # Calculate confidence penalty (higher penalty for lower confidence)
    confidence_penalty = 0.0
    
    if yield_confidence < YIELD_CONFIDENCE_LOW:
        confidence_penalty += 0.15  # Significant penalty for very low confidence
    elif yield_confidence < YIELD_CONFIDENCE_MEDIUM:
        confidence_penalty += 0.08  # Moderate penalty for low confidence
    
    calculation_steps.append(f"Low confidence penalty: {confidence_penalty:.3f}")
    
    return confidence_penalty


def _calculate_experience_adjustment(farmer_experience: str, calculation_steps: list) -> float:
    """
    Adjust risk based on farmer experience level.
    
    Less experienced farmers face higher risk due to potential management errors.
    """
    experience_adjustments = {
        'beginner': 0.1,    # Higher risk for beginners
        'novice': 0.08,     # Moderate increase for novices
        'medium': 0.0,      # No adjustment for medium experience
        'experienced': -0.05, # Slight reduction for experienced farmers
        'expert': -0.08     # Larger reduction for experts
    }
    
    adjustment = experience_adjustments.get(farmer_experience, 0.05)  # Default to slight increase
    
    calculation_steps.append(f"Farmer experience ({farmer_experience}) adjustment: {adjustment:+.3f}")
    
    return adjustment


def _calculate_economic_adjustment(economic_buffer: float, calculation_steps: list) -> float:
    """
    Adjust risk based on farmer's economic safety buffer.
    
    Lower economic buffer increases risk as farmer has less resilience to losses.
    """
    # Inverse relationship: lower buffer = higher risk adjustment
    if economic_buffer < 0.2:
        adjustment = 0.1  # High risk adjustment for very low buffer
    elif economic_buffer < 0.4:
        adjustment = 0.05  # Moderate adjustment for low buffer
    else:
        adjustment = 0.0  # No adjustment for adequate buffer
    
    calculation_steps.append(f"Economic buffer ({economic_buffer:.2f}) adjustment: +{adjustment:.3f}")
    
    return adjustment


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


def _generate_mitigation_suggestions(risk_components: dict, overall_risk_level: str,
                                   yield_result: dict, disease_result: dict, 
                                   irrigation_result: dict) -> list:
    """
    Generate specific risk mitigation suggestions based on risk components.
    """
    suggestions = []
    
    # Overall risk level suggestions
    if overall_risk_level == 'HIGH':
        suggestions.extend([
            "Consider postponing farming until conditions improve",
            "If proceeding, reduce investment and crop area significantly",
            "Implement all available risk mitigation measures"
        ])
    elif overall_risk_level == 'MEDIUM':
        suggestions.extend([
            "Proceed with caution and enhanced monitoring",
            "Consider reducing crop area by 30-50%",
            "Implement preventive measures proactively"
        ])
    
    # Component-specific suggestions
    for component_name, component_data in risk_components.items():
        if component_data['score'] > 0.7:  # High risk in this component
            if component_name == 'disease_risk':
                suggestions.extend([
                    "Implement immediate disease prevention measures",
                    "Consider disease-resistant crop varieties",
                    "Increase crop monitoring frequency"
                ])
            elif component_name == 'water_risk':
                suggestions.extend([
                    "Secure additional water sources if possible",
                    "Implement water-saving irrigation techniques",
                    "Consider drought-resistant crops"
                ])
            elif component_name == 'yield_risk':
                suggestions.extend([
                    "Focus on proven, low-risk farming practices",
                    "Consider crop insurance if available",
                    "Diversify crops to spread risk"
                ])
    
    # Remove duplicates while preserving order
    unique_suggestions = []
    seen = set()
    for suggestion in suggestions:
        if suggestion not in seen:
            unique_suggestions.append(suggestion)
            seen.add(suggestion)
    
    return unique_suggestions


def _calculate_assessment_confidence(yield_result: dict, disease_result: dict,
                                   irrigation_result: dict, weather_uncertainty: float) -> float:
    """
    Calculate confidence in the risk assessment itself.
    
    Higher confidence when input data is reliable and comprehensive.
    """
    base_confidence = 0.8
    
    # Reduce confidence based on input quality
    yield_confidence = yield_result.get('confidence_score', 0.5)
    confidence_factors = [yield_confidence]
    
    # Weather uncertainty reduces assessment confidence
    weather_confidence = 1.0 - weather_uncertainty
    confidence_factors.append(weather_confidence)
    
    # Calculate weighted average confidence
    assessment_confidence = sum(confidence_factors) / len(confidence_factors) * base_confidence
    
    return max(0.1, min(1.0, assessment_confidence))


def _generate_risk_explanation(risk_score: float, risk_level: str, risk_components: dict,
                             calculation_steps: list, assessment_confidence: float) -> str:
    """
    Generate comprehensive explanation of risk assessment.
    """
    explanation_parts = [
        f"Overall farming risk: {risk_level} ({risk_score:.3f}/1.0)."
    ]
    
    # Add component breakdown
    explanation_parts.append("Risk breakdown:")
    for component_name, component_data in risk_components.items():
        component_display_name = component_name.replace('_', ' ').title()
        weighted_contribution = component_data['score'] * component_data['weight']
        explanation_parts.append(
            f"• {component_display_name}: {component_data['score']:.2f} "
            f"(weight: {component_data['weight']:.0%}, contribution: {weighted_contribution:.3f})"
        )
    
    # Add key calculation insights
    if calculation_steps:
        explanation_parts.append("Key calculation factors:")
        # Show most important steps
        important_steps = [step for step in calculation_steps if 'adjustment' in step or 'penalty' in step]
        for step in important_steps[:3]:  # Show top 3 adjustments
            explanation_parts.append(f"• {step}")
    
    # Add assessment confidence
    confidence_description = "high" if assessment_confidence > 0.7 else "medium" if assessment_confidence > 0.5 else "low"
    explanation_parts.append(
        f"Assessment confidence: {confidence_description} ({assessment_confidence:.2f})."
    )
    
    # Add conservative approach note
    explanation_parts.append(
        "This assessment uses conservative estimates and safety margins to prioritize farmer protection over profit maximization."
    )
    
    return " ".join(explanation_parts)


def validate_inputs(inputs: dict) -> tuple[bool, str]:
    """
    Validate input parameters for risk assessment.
    
    Args:
        inputs (dict): Input parameters to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['yield_result', 'disease_result', 'irrigation_result']
    
    # Check for required fields
    for field in required_fields:
        if field not in inputs:
            return False, f"Missing required field: {field}"
    
    # Validate yield_result structure
    yield_result = inputs.get('yield_result', {})
    if not isinstance(yield_result, dict):
        return False, "yield_result must be a dictionary"
    
    # Validate disease_result structure
    disease_result = inputs.get('disease_result', {})
    if not isinstance(disease_result, dict):
        return False, "disease_result must be a dictionary"
    
    # Validate irrigation_result structure
    irrigation_result = inputs.get('irrigation_result', {})
    if not isinstance(irrigation_result, dict):
        return False, "irrigation_result must be a dictionary"
    
    # Validate optional numeric parameters
    if 'weather_uncertainty' in inputs:
        try:
            uncertainty = float(inputs['weather_uncertainty'])
            if uncertainty < 0 or uncertainty > 1:
                return False, "weather_uncertainty must be between 0 and 1"
        except (ValueError, TypeError):
            return False, "weather_uncertainty must be a numeric value"
    
    if 'economic_buffer' in inputs:
        try:
            buffer = float(inputs['economic_buffer'])
            if buffer < 0 or buffer > 1:
                return False, "economic_buffer must be between 0 and 1"
        except (ValueError, TypeError):
            return False, "economic_buffer must be a numeric value"
    
    return True, "Inputs are valid"


# Example usage and testing function
def test_risk_assessor():
    """
    Test function to demonstrate risk assessor functionality.
    """
    test_cases = [
        {
            'name': 'Low Risk Scenario',
            'inputs': {
                'yield_result': {
                    'expected_yield_percentage': 75.0,
                    'confidence_score': 0.85
                },
                'disease_result': {
                    'disease_risk_level': 'LOW',
                    'disease_risk_score': 0.2
                },
                'irrigation_result': {
                    'water_stress_level': 'LOW',
                    'recommended_irrigation_mm': 20.0
                },
                'weather_uncertainty': 0.2,
                'farmer_experience': 'experienced',
                'economic_buffer': 0.6
            }
        },
        {
            'name': 'High Risk Scenario',
            'inputs': {
                'yield_result': {
                    'expected_yield_percentage': 25.0,
                    'confidence_score': 0.3
                },
                'disease_result': {
                    'disease_risk_level': 'HIGH',
                    'disease_risk_score': 0.9
                },
                'irrigation_result': {
                    'water_stress_level': 'HIGH',
                    'recommended_irrigation_mm': 5.0
                },
                'weather_uncertainty': 0.8,
                'farmer_experience': 'beginner',
                'economic_buffer': 0.1
            }
        },
        {
            'name': 'Medium Risk Scenario',
            'inputs': {
                'yield_result': {
                    'expected_yield_percentage': 50.0,
                    'confidence_score': 0.6
                },
                'disease_result': {
                    'disease_risk_level': 'MEDIUM',
                    'disease_risk_score': 0.5
                },
                'irrigation_result': {
                    'water_stress_level': 'MEDIUM',
                    'recommended_irrigation_mm': 15.0
                },
                'weather_uncertainty': 0.4
            }
        }
    ]
    
    print("Risk Assessor Test Results:")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\nTest Case: {test_case['name']}")
        print("-" * 40)
        
        # Validate inputs
        is_valid, message = validate_inputs(test_case['inputs'])
        if not is_valid:
            print(f"Input validation failed: {message}")
            continue
        
        # Assess risk
        result = assess_overall_risk(test_case['inputs'])
        
        print(f"Overall Risk: {result['overall_risk_level']} ({result['overall_risk_score']:.3f})")
        print(f"Assessment Confidence: {result['confidence_in_assessment']:.2f}")
        print("Risk Breakdown:")
        for component, data in result['risk_breakdown'].items():
            print(f"  • {component.replace('_', ' ').title()}: {data['score']:.3f}")
        print(f"Explanation: {result['explanation']}")
        print("Mitigation Suggestions:")
        for suggestion in result['risk_mitigation_suggestions'][:3]:
            print(f"  • {suggestion}")


if __name__ == "__main__":
    test_risk_assessor()