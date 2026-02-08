"""
Conservative Irrigation Optimization Module for Rural Agriculture Decision Support System.

This module provides explainable, water-conservative irrigation recommendations based on
soil type, crop requirements, rainfall, and water availability. Designed to prioritize
water conservation and prevent over-irrigation while ensuring crop survival.

Author: Agriculture Decision Support System
Version: 1.0
"""

import sys
import os

# Add config directory to path for importing settings
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from config.settings import (
        SOIL_TYPES, IRRIGATION_MAX_DAILY, IRRIGATION_MAX_WEEKLY,
        IRRIGATION_RATE_CLAY, IRRIGATION_RATE_LOAM, IRRIGATION_RATE_SANDY, IRRIGATION_RATE_SILT,
        IRRIGATION_SAFETY_MARGIN, IRRIGATION_EFFICIENCY,
        RAINFALL_LOW_THRESHOLD, RAINFALL_MEDIUM_THRESHOLD, RAINFALL_HIGH_THRESHOLD
    )
except ImportError:
    # Fallback values if config is not available
    SOIL_TYPES = {
        'CLAY': {'water_retention': 0.45, 'irrigation_frequency': 7},
        'LOAM': {'water_retention': 0.35, 'irrigation_frequency': 5},
        'SANDY': {'water_retention': 0.15, 'irrigation_frequency': 3},
        'SILT': {'water_retention': 0.40, 'irrigation_frequency': 6}
    }
    IRRIGATION_MAX_DAILY = 25.0
    IRRIGATION_MAX_WEEKLY = 100.0
    IRRIGATION_RATE_CLAY = 5.0
    IRRIGATION_RATE_LOAM = 10.0
    IRRIGATION_RATE_SANDY = 15.0
    IRRIGATION_RATE_SILT = 7.0
    IRRIGATION_SAFETY_MARGIN = 0.15
    IRRIGATION_EFFICIENCY = 0.80
    RAINFALL_LOW_THRESHOLD = 10.0
    RAINFALL_MEDIUM_THRESHOLD = 50.0
    RAINFALL_HIGH_THRESHOLD = 100.0


def optimize_irrigation(inputs: dict) -> dict:
    """
    Optimize irrigation recommendations using conservative, water-saving principles.
    
    Args:
        inputs (dict): Dictionary containing:
            - soil_type (str): Soil type ('CLAY', 'LOAM', 'SANDY', 'SILT')
            - crop_type (str): Type of crop being grown
            - rainfall_mm (float): Recent rainfall in millimeters
            - available_water_mm (float): Available water for irrigation
            - growing_stage (str, optional): Current crop growth stage
            - temperature_c (float, optional): Current temperature for evaporation estimates
            - humidity_percent (float, optional): Humidity for evaporation calculations
            
    Returns:
        dict: Irrigation optimization results containing:
            - recommended_irrigation_mm (float): Recommended irrigation amount
            - irrigation_frequency_days (int): Days between irrigation cycles
            - water_stress_level (str): Water stress assessment ('LOW', 'MEDIUM', 'HIGH')
            - explanation (str): Plain English explanation of recommendations
            - water_saving_tips (list): Specific water conservation recommendations
            - irrigation_schedule (dict): Detailed irrigation timing guidance
    """
    
    # Extract and validate inputs
    soil_type = inputs.get('soil_type', 'LOAM').upper()
    crop_type = inputs.get('crop_type', 'wheat').lower()
    rainfall = inputs.get('rainfall_mm', 0.0)
    available_water = inputs.get('available_water_mm', 0.0)
    growing_stage = inputs.get('growing_stage', 'vegetative').lower()
    temperature = inputs.get('temperature_c', 25.0)
    humidity = inputs.get('humidity_percent', 60.0)
    
    # Initialize calculation components
    base_water_need = 0.0
    soil_adjustment = 0.0
    crop_adjustment = 0.0
    stage_adjustment = 0.0
    rainfall_credit = 0.0
    
    # Track explanation components
    calculation_steps = []
    water_saving_tips = []
    warnings = []
    
    # =============================================================================
    # STEP 1: CALCULATE BASE WATER REQUIREMENTS
    # =============================================================================
    
    # Base daily water requirement by crop type (mm/day)
    crop_water_requirements = {
        'rice': 8.0,        # High water requirement
        'sugarcane': 7.0,   # High water requirement
        'cotton': 5.0,      # Moderate water requirement
        'wheat': 4.0,       # Moderate water requirement
        'maize': 4.5,       # Moderate water requirement
        'soybean': 4.0,     # Moderate water requirement
        'potato': 3.5,      # Lower water requirement
        'groundnut': 3.0,   # Lower water requirement
        'millet': 2.5,      # Drought-resistant, low requirement
        'sorghum': 2.5,     # Drought-resistant, low requirement
        'mustard': 3.0,     # Lower water requirement
        'chili': 4.0,       # Moderate water requirement
        'tomato': 5.0,      # Higher water requirement
        'jute': 6.0,        # High water requirement
        'coconut': 4.0,     # Moderate but consistent requirement
        'tea': 3.5          # Moderate water requirement
    }
    
    base_water_need = crop_water_requirements.get(crop_type, 4.0)  # Default to moderate requirement
    calculation_steps.append(f"Base water requirement for {crop_type}: {base_water_need} mm/day")
    
    # =============================================================================
    # STEP 2: SOIL TYPE ADJUSTMENTS
    # =============================================================================
    
    if soil_type in SOIL_TYPES:
        soil_properties = SOIL_TYPES[soil_type]
        water_retention = soil_properties['water_retention']
        base_frequency = soil_properties['irrigation_frequency']
        
        # Adjust irrigation amount based on soil water retention
        if soil_type == 'CLAY':
            soil_adjustment = 1.2  # Clay holds water longer, can irrigate more per session
            calculation_steps.append("Clay soil: Increased irrigation amount due to high water retention")
        elif soil_type == 'SANDY':
            soil_adjustment = 0.7  # Sandy soil drains quickly, smaller frequent applications
            calculation_steps.append("Sandy soil: Reduced irrigation amount due to poor water retention")
            warnings.append("Sandy soil requires frequent, light irrigation to prevent water loss")
        elif soil_type == 'LOAM':
            soil_adjustment = 1.0  # Optimal soil, no adjustment needed
            calculation_steps.append("Loam soil: Optimal water retention, no adjustment needed")
        elif soil_type == 'SILT':
            soil_adjustment = 1.1  # Good water retention, slight increase
            calculation_steps.append("Silt soil: Good water retention, slight increase in irrigation amount")
    else:
        soil_adjustment = 1.0
        base_frequency = 5
        calculation_steps.append(f"Unknown soil type ({soil_type}), using default adjustments")
        warnings.append("Unknown soil type may affect irrigation accuracy")
    
    # =============================================================================
    # STEP 3: GROWING STAGE ADJUSTMENTS
    # =============================================================================
    
    # Water requirements vary by growth stage
    stage_multipliers = {
        'seedling': 0.6,      # Lower water need, avoid overwatering young plants
        'vegetative': 1.0,    # Standard water requirement
        'flowering': 1.2,     # Critical stage, higher water need
        'reproductive': 1.2,  # Critical stage, maintain consistent moisture
        'fruiting': 1.1,      # Moderate increase for fruit development
        'maturation': 0.8,    # Reduced water to concentrate nutrients
        'harvest': 0.4,       # Minimal water to prevent crop damage
        'mature': 0.9         # Maintenance level for perennial crops
    }
    
    stage_multiplier = stage_multipliers.get(growing_stage, 1.0)
    stage_adjustment = base_water_need * stage_multiplier
    
    calculation_steps.append(
        f"Growth stage ({growing_stage}) adjustment: {stage_multiplier}x multiplier = {stage_adjustment:.1f} mm/day"
    )
    
    # =============================================================================
    # STEP 4: RAINFALL CREDIT CALCULATION
    # =============================================================================
    
    # Calculate effective rainfall (accounting for runoff and evaporation)
    if rainfall >= RAINFALL_HIGH_THRESHOLD:
        # Heavy rainfall - significant credit but account for runoff
        rainfall_efficiency = 0.6  # 40% lost to runoff in heavy rain
        rainfall_credit = rainfall * rainfall_efficiency
        calculation_steps.append(f"Heavy rainfall ({rainfall}mm): {rainfall_efficiency*100}% efficiency = {rainfall_credit:.1f}mm credit")
        warnings.append("Heavy rainfall may cause waterlogging - monitor field drainage")
    elif rainfall >= RAINFALL_MEDIUM_THRESHOLD:
        # Moderate rainfall - good efficiency
        rainfall_efficiency = 0.8  # 20% lost to runoff/evaporation
        rainfall_credit = rainfall * rainfall_efficiency
        calculation_steps.append(f"Moderate rainfall ({rainfall}mm): {rainfall_efficiency*100}% efficiency = {rainfall_credit:.1f}mm credit")
    elif rainfall >= RAINFALL_LOW_THRESHOLD:
        # Light rainfall - high efficiency but limited amount
        rainfall_efficiency = 0.9  # 10% lost to evaporation
        rainfall_credit = rainfall * rainfall_efficiency
        calculation_steps.append(f"Light rainfall ({rainfall}mm): {rainfall_efficiency*100}% efficiency = {rainfall_credit:.1f}mm credit")
    else:
        # Minimal or no rainfall
        rainfall_credit = rainfall * 0.5  # Very light rain has limited benefit
        calculation_steps.append(f"Minimal rainfall ({rainfall}mm): Limited benefit for irrigation needs")
    
    # =============================================================================
    # STEP 5: EVAPOTRANSPIRATION ADJUSTMENT
    # =============================================================================
    
    # Adjust for environmental conditions affecting water loss
    evaporation_factor = _calculate_evaporation_factor(temperature, humidity)
    environmental_adjustment = stage_adjustment * evaporation_factor
    
    calculation_steps.append(
        f"Environmental conditions (T:{temperature}°C, H:{humidity}%): {evaporation_factor:.2f}x factor = {environmental_adjustment:.1f} mm/day"
    )
    
    # =============================================================================
    # STEP 6: CALCULATE NET IRRIGATION REQUIREMENT
    # =============================================================================
    
    # Calculate daily irrigation need after rainfall credit
    daily_irrigation_need = max(0, environmental_adjustment - (rainfall_credit / 7))  # Spread rainfall over week
    
    # Apply soil adjustment
    adjusted_irrigation = daily_irrigation_need * soil_adjustment
    
    # Apply safety margin (conservative approach)
    safety_factor = 1.0 - IRRIGATION_SAFETY_MARGIN
    conservative_irrigation = adjusted_irrigation * safety_factor
    
    calculation_steps.append(f"Net daily irrigation need: {conservative_irrigation:.1f} mm/day (after safety margin)")
    
    # =============================================================================
    # STEP 7: DETERMINE IRRIGATION FREQUENCY AND AMOUNT
    # =============================================================================
    
    # Calculate irrigation per session based on soil type frequency
    irrigation_per_session = conservative_irrigation * base_frequency
    
    # Apply maximum limits for safety
    irrigation_per_session = min(irrigation_per_session, IRRIGATION_MAX_DAILY)
    
    # Ensure weekly limit is not exceeded
    weekly_irrigation = irrigation_per_session * (7 / base_frequency)
    if weekly_irrigation > IRRIGATION_MAX_WEEKLY:
        irrigation_per_session = IRRIGATION_MAX_WEEKLY / (7 / base_frequency)
        warnings.append("Irrigation reduced to stay within weekly safety limits")
    
    # =============================================================================
    # STEP 8: WATER AVAILABILITY CHECK
    # =============================================================================
    
    # Check if recommended irrigation exceeds available water
    if irrigation_per_session > available_water:
        original_recommendation = irrigation_per_session
        irrigation_per_session = available_water * 0.8  # Use 80% of available water for safety
        warnings.append(
            f"Limited water availability: Reduced from {original_recommendation:.1f}mm to {irrigation_per_session:.1f}mm"
        )
        calculation_steps.append("Irrigation limited by available water supply")
    
    # =============================================================================
    # STEP 9: DETERMINE WATER STRESS LEVEL
    # =============================================================================
    
    water_stress_level = _assess_water_stress(
        conservative_irrigation, irrigation_per_session, rainfall, available_water, crop_type
    )
    
    # =============================================================================
    # STEP 10: GENERATE WATER SAVING TIPS
    # =============================================================================
    
    water_saving_tips = _generate_water_saving_tips(
        soil_type, crop_type, water_stress_level, rainfall, temperature
    )
    
    # =============================================================================
    # STEP 11: CREATE IRRIGATION SCHEDULE
    # =============================================================================
    
    irrigation_schedule = _create_irrigation_schedule(
        irrigation_per_session, base_frequency, soil_type, growing_stage
    )
    
    # =============================================================================
    # GENERATE EXPLANATION
    # =============================================================================
    
    explanation = _generate_irrigation_explanation(
        irrigation_per_session, base_frequency, water_stress_level, 
        soil_type, crop_type, rainfall, available_water, calculation_steps, warnings
    )
    
    return {
        'recommended_irrigation_mm': round(irrigation_per_session, 1),
        'irrigation_frequency_days': base_frequency,
        'water_stress_level': water_stress_level,
        'explanation': explanation,
        'water_saving_tips': water_saving_tips,
        'irrigation_schedule': irrigation_schedule
    }


def _calculate_evaporation_factor(temperature: float, humidity: float) -> float:
    """
    Calculate evaporation factor based on temperature and humidity.
    
    Higher temperature and lower humidity increase evaporation.
    """
    # Base evaporation factor
    base_factor = 1.0
    
    # Temperature adjustment (higher temp = more evaporation)
    if temperature > 35:
        temp_factor = 1.3  # High evaporation in hot weather
    elif temperature > 30:
        temp_factor = 1.15  # Moderate increase
    elif temperature > 25:
        temp_factor = 1.0  # Normal evaporation
    elif temperature > 20:
        temp_factor = 0.9  # Slightly reduced evaporation
    else:
        temp_factor = 0.8  # Low evaporation in cool weather
    
    # Humidity adjustment (lower humidity = more evaporation)
    if humidity < 40:
        humidity_factor = 1.2  # High evaporation in dry air
    elif humidity < 60:
        humidity_factor = 1.1  # Moderate increase
    elif humidity < 80:
        humidity_factor = 1.0  # Normal evaporation
    else:
        humidity_factor = 0.9  # Reduced evaporation in humid air
    
    return base_factor * temp_factor * humidity_factor


def _assess_water_stress(daily_need: float, available_irrigation: float, 
                        rainfall: float, total_water: float, crop_type: str) -> str:
    """
    Assess water stress level based on water supply vs. demand.
    """
    # Calculate water deficit
    water_deficit_ratio = (daily_need - available_irrigation) / daily_need if daily_need > 0 else 0
    
    # Drought-resistant crops have lower stress thresholds
    drought_resistant = crop_type in ['millet', 'sorghum', 'groundnut']
    
    if water_deficit_ratio <= 0.1:  # Less than 10% deficit
        return 'LOW'
    elif water_deficit_ratio <= 0.3 or (drought_resistant and water_deficit_ratio <= 0.4):
        return 'MEDIUM'
    else:
        return 'HIGH'


def _generate_water_saving_tips(soil_type: str, crop_type: str, stress_level: str, 
                               rainfall: float, temperature: float) -> list:
    """
    Generate specific water saving recommendations based on conditions.
    """
    tips = []
    
    # Universal water saving tips
    tips.extend([
        "Apply mulch around plants to reduce evaporation",
        "Irrigate early morning or late evening to minimize water loss",
        "Use drip irrigation or soaker hoses for efficient water delivery"
    ])
    
    # Soil-specific tips
    if soil_type == 'SANDY':
        tips.extend([
            "Add organic matter to improve water retention in sandy soil",
            "Use frequent, light irrigation to prevent water runoff",
            "Consider installing subsurface irrigation for better efficiency"
        ])
    elif soil_type == 'CLAY':
        tips.extend([
            "Ensure proper drainage to prevent waterlogging",
            "Allow soil to dry slightly between irrigations",
            "Break up soil crust to improve water infiltration"
        ])
    
    # Temperature-based tips
    if temperature > 30:
        tips.extend([
            "Provide shade cloth during hottest part of day",
            "Increase irrigation frequency in hot weather",
            "Monitor plants for heat stress signs"
        ])
    
    # Stress-level specific tips
    if stress_level == 'HIGH':
        tips.extend([
            "Prioritize irrigation for most valuable crops",
            "Consider deficit irrigation strategies",
            "Harvest rainwater for supplemental irrigation"
        ])
    elif stress_level == 'MEDIUM':
        tips.append("Monitor soil moisture regularly to optimize irrigation timing")
    
    # Rainfall-based tips
    if rainfall < RAINFALL_LOW_THRESHOLD:
        tips.extend([
            "Install rainwater harvesting systems for future use",
            "Consider drought-resistant crop varieties for next season"
        ])
    elif rainfall > RAINFALL_HIGH_THRESHOLD:
        tips.extend([
            "Improve field drainage to prevent waterlogging",
            "Reduce irrigation frequency after heavy rainfall"
        ])
    
    return tips


def _create_irrigation_schedule(irrigation_amount: float, frequency_days: int, 
                               soil_type: str, growing_stage: str) -> dict:
    """
    Create detailed irrigation scheduling guidance.
    """
    # Determine optimal irrigation times
    optimal_times = ["Early morning (5-7 AM)", "Late evening (6-8 PM)"]
    
    # Calculate application rate based on soil type
    application_rates = {
        'CLAY': IRRIGATION_RATE_CLAY,
        'LOAM': IRRIGATION_RATE_LOAM,
        'SANDY': IRRIGATION_RATE_SANDY,
        'SILT': IRRIGATION_RATE_SILT
    }
    
    rate = application_rates.get(soil_type, IRRIGATION_RATE_LOAM)
    application_duration = irrigation_amount / rate if rate > 0 else 1.0
    
    schedule = {
        'irrigation_amount_per_session': round(irrigation_amount, 1),
        'frequency_days': frequency_days,
        'optimal_timing': optimal_times,
        'application_rate_mm_per_hour': rate,
        'estimated_duration_hours': round(application_duration, 1),
        'next_irrigation_days': frequency_days
    }
    
    # Add stage-specific guidance
    if growing_stage in ['flowering', 'reproductive']:
        schedule['special_notes'] = [
            "Critical growth stage - maintain consistent soil moisture",
            "Avoid water stress during this period"
        ]
    elif growing_stage == 'harvest':
        schedule['special_notes'] = [
            "Reduce irrigation to prevent crop quality issues",
            "Stop irrigation 3-5 days before harvest"
        ]
    
    return schedule


def _generate_irrigation_explanation(irrigation_amount: float, frequency: int, stress_level: str,
                                   soil_type: str, crop_type: str, rainfall: float, 
                                   available_water: float, calculation_steps: list, warnings: list) -> str:
    """
    Generate comprehensive explanation of irrigation recommendations.
    """
    explanation_parts = [
        f"Irrigation recommendation: {irrigation_amount:.1f}mm every {frequency} days for {crop_type} in {soil_type.lower()} soil."
    ]
    
    # Add water stress assessment
    explanation_parts.append(f"Current water stress level: {stress_level.lower()}.")
    
    # Add key factors
    explanation_parts.append(
        f"Based on {rainfall:.1f}mm recent rainfall and {available_water:.1f}mm available water."
    )
    
    # Add calculation summary
    if calculation_steps:
        explanation_parts.append("Key calculation factors:")
        explanation_parts.extend([f"• {step}" for step in calculation_steps[:3]])  # Show top 3 steps
    
    # Add warnings if any
    if warnings:
        explanation_parts.append("Important considerations:")
        explanation_parts.extend([f"• {warning}" for warning in warnings])
    
    # Add conservative approach note
    explanation_parts.append(
        "Recommendations use conservative water amounts to prevent over-irrigation and promote water conservation."
    )
    
    return " ".join(explanation_parts)


def validate_inputs(inputs: dict) -> tuple[bool, str]:
    """
    Validate input parameters for irrigation optimization.
    
    Args:
        inputs (dict): Input parameters to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['soil_type', 'crop_type', 'rainfall_mm', 'available_water_mm']
    
    # Check for required fields
    for field in required_fields:
        if field not in inputs:
            return False, f"Missing required field: {field}"
    
    # Validate data types and ranges
    try:
        rainfall = float(inputs['rainfall_mm'])
        available_water = float(inputs['available_water_mm'])
        
        if rainfall < 0:
            return False, "Rainfall cannot be negative"
        
        if available_water < 0:
            return False, "Available water cannot be negative"
        
        if rainfall > 500:
            return False, "Rainfall value seems unrealistic (>500mm)"
        
        if available_water > 1000:
            return False, "Available water value seems unrealistic (>1000mm)"
            
    except (ValueError, TypeError):
        return False, "Rainfall and available water must be numeric values"
    
    # Validate soil type
    soil_type = inputs['soil_type'].upper()
    valid_soils = ['CLAY', 'LOAM', 'SANDY', 'SILT']
    if soil_type not in valid_soils:
        return False, f"Invalid soil type. Must be one of: {', '.join(valid_soils)}"
    
    return True, "Inputs are valid"


# Example usage and testing function
def test_irrigation_optimizer():
    """
    Test function to demonstrate irrigation optimizer functionality.
    """
    test_cases = [
        {
            'name': 'Normal Conditions - Loam Soil',
            'inputs': {
                'soil_type': 'LOAM',
                'crop_type': 'wheat',
                'rainfall_mm': 15.0,
                'available_water_mm': 80.0,
                'growing_stage': 'vegetative',
                'temperature_c': 25.0,
                'humidity_percent': 65.0
            }
        },
        {
            'name': 'Water Stress - Sandy Soil',
            'inputs': {
                'soil_type': 'SANDY',
                'crop_type': 'millet',
                'rainfall_mm': 2.0,
                'available_water_mm': 20.0,
                'growing_stage': 'flowering',
                'temperature_c': 35.0,
                'humidity_percent': 40.0
            }
        },
        {
            'name': 'High Rainfall - Clay Soil',
            'inputs': {
                'soil_type': 'CLAY',
                'crop_type': 'rice',
                'rainfall_mm': 120.0,
                'available_water_mm': 150.0,
                'growing_stage': 'reproductive',
                'temperature_c': 28.0,
                'humidity_percent': 80.0
            }
        }
    ]
    
    print("Irrigation Optimizer Test Results:")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\nTest Case: {test_case['name']}")
        print("-" * 40)
        
        # Validate inputs
        is_valid, message = validate_inputs(test_case['inputs'])
        if not is_valid:
            print(f"Input validation failed: {message}")
            continue
        
        # Optimize irrigation
        result = optimize_irrigation(test_case['inputs'])
        
        print(f"Recommended Irrigation: {result['recommended_irrigation_mm']}mm")
        print(f"Frequency: Every {result['irrigation_frequency_days']} days")
        print(f"Water Stress Level: {result['water_stress_level']}")
        print(f"Explanation: {result['explanation']}")
        print("Water Saving Tips:")
        for tip in result['water_saving_tips'][:3]:  # Show first 3 tips
            print(f"  • {tip}")


if __name__ == "__main__":
    test_irrigation_optimizer()