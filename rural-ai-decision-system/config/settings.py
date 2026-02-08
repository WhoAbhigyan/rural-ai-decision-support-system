"""
Configuration settings for Rural Agriculture Decision Support System.

This module contains all system constants used throughout the application.
Values are set conservatively to prioritize farmer safety, water conservation,
and economic risk reduction.

Author: Agriculture Decision Support System
Version: 1.0
"""

# =============================================================================
# RAINFALL THRESHOLDS (mm)
# =============================================================================
# Conservative thresholds to prevent overwatering and flooding risks
RAINFALL_LOW_THRESHOLD = 10.0      # Below 10mm - irrigation likely needed
RAINFALL_MEDIUM_THRESHOLD = 50.0   # 10-50mm - moderate rainfall
RAINFALL_HIGH_THRESHOLD = 100.0    # Above 100mm - high rainfall, potential flooding risk

# Monthly rainfall requirements for different crop stages (mm)
RAINFALL_SEEDLING_MIN = 25.0       # Minimum for seedling stage
RAINFALL_GROWTH_MIN = 75.0         # Minimum for active growth
RAINFALL_FLOWERING_MIN = 50.0      # Minimum for flowering stage
RAINFALL_HARVEST_MAX = 20.0        # Maximum during harvest to prevent crop damage

# =============================================================================
# TEMPERATURE RANGES (°C)
# =============================================================================
# Optimal temperature ranges for general farming activities
TEMP_OPTIMAL_MIN = 15.0            # Minimum optimal temperature
TEMP_OPTIMAL_MAX = 30.0            # Maximum optimal temperature
TEMP_CRITICAL_LOW = 5.0            # Below this - frost risk, crop damage
TEMP_CRITICAL_HIGH = 40.0          # Above this - heat stress, water loss

# Specific temperature thresholds for crop activities
TEMP_PLANTING_MIN = 10.0           # Minimum safe planting temperature
TEMP_PLANTING_MAX = 35.0           # Maximum safe planting temperature
TEMP_HARVEST_MAX = 38.0            # Maximum safe harvesting temperature

# =============================================================================
# SOIL TYPES AND WATER RETENTION CAPACITY
# =============================================================================
# Water retention capacity as percentage of field capacity
SOIL_TYPES = {
    'CLAY': {
        'water_retention': 0.45,    # 45% - high retention, slow drainage
        'drainage_rate': 0.1,       # Low drainage rate
        'irrigation_frequency': 7   # Days between irrigation
    },
    'LOAM': {
        'water_retention': 0.35,    # 35% - moderate retention, good drainage
        'drainage_rate': 0.3,       # Moderate drainage rate
        'irrigation_frequency': 5   # Days between irrigation
    },
    'SANDY': {
        'water_retention': 0.15,    # 15% - low retention, fast drainage
        'drainage_rate': 0.6,       # High drainage rate
        'irrigation_frequency': 3   # Days between irrigation
    },
    'SILT': {
        'water_retention': 0.40,    # 40% - good retention, moderate drainage
        'drainage_rate': 0.2,       # Low-moderate drainage rate
        'irrigation_frequency': 6   # Days between irrigation
    }
}

# Soil moisture thresholds (percentage of field capacity)
SOIL_MOISTURE_CRITICAL = 0.20      # Below 20% - immediate irrigation needed
SOIL_MOISTURE_LOW = 0.40           # Below 40% - irrigation recommended
SOIL_MOISTURE_OPTIMAL = 0.70       # 70% - optimal moisture level
SOIL_MOISTURE_SATURATED = 0.95     # Above 95% - risk of waterlogging

# =============================================================================
# CROP RISK LEVELS
# =============================================================================
# Risk assessment categories for decision making
RISK_LOW = 0.25                    # 25% - low risk threshold
RISK_MEDIUM = 0.60                 # 60% - medium risk threshold
RISK_HIGH = 0.85                   # 85% - high risk threshold

# Disease risk factors (probability multipliers)
DISEASE_RISK_HUMIDITY_HIGH = 1.5   # High humidity increases disease risk
DISEASE_RISK_TEMP_OPTIMAL = 1.3    # Optimal temps for pathogens
DISEASE_RISK_RAINFALL_EXCESS = 1.4 # Excess rainfall increases fungal risk

# Weather-related crop stress factors
STRESS_DROUGHT_MULTIPLIER = 2.0    # Drought stress factor
STRESS_FLOOD_MULTIPLIER = 1.8      # Flood stress factor
STRESS_HEAT_MULTIPLIER = 1.6       # Heat stress factor
STRESS_FROST_MULTIPLIER = 2.5      # Frost damage factor (highest risk)

# =============================================================================
# IRRIGATION SAFETY LIMITS
# =============================================================================
# Conservative irrigation limits to prevent overwatering and waste
IRRIGATION_MAX_DAILY = 25.0        # Maximum daily irrigation (mm)
IRRIGATION_MAX_WEEKLY = 100.0      # Maximum weekly irrigation (mm)
IRRIGATION_MIN_INTERVAL = 2        # Minimum hours between irrigation cycles

# Water application rates by soil type (mm/hour)
IRRIGATION_RATE_CLAY = 5.0         # Slow rate for clay soil
IRRIGATION_RATE_LOAM = 10.0        # Moderate rate for loam soil
IRRIGATION_RATE_SANDY = 15.0       # Fast rate for sandy soil
IRRIGATION_RATE_SILT = 7.0         # Slow-moderate rate for silt soil

# Safety margins for irrigation scheduling
IRRIGATION_SAFETY_MARGIN = 0.15    # 15% safety margin below optimal
IRRIGATION_EFFICIENCY = 0.80       # 80% irrigation efficiency assumption

# =============================================================================
# YIELD CONFIDENCE THRESHOLDS
# =============================================================================
# Confidence levels for yield predictions and recommendations
YIELD_CONFIDENCE_HIGH = 0.85       # 85% - high confidence in prediction
YIELD_CONFIDENCE_MEDIUM = 0.65     # 65% - medium confidence
YIELD_CONFIDENCE_LOW = 0.45        # 45% - low confidence threshold

# Yield prediction accuracy thresholds
YIELD_ACCURACY_ACCEPTABLE = 0.80   # 80% - acceptable prediction accuracy
YIELD_VARIANCE_MAX = 0.25          # 25% - maximum acceptable variance

# Economic thresholds for decision making
ECONOMIC_RISK_THRESHOLD = 0.30     # 30% - maximum acceptable economic risk
PROFIT_MARGIN_MIN = 0.15           # 15% - minimum profit margin required
INVESTMENT_PAYBACK_MAX = 3         # Maximum 3 years for investment payback

# =============================================================================
# SYSTEM OPERATIONAL LIMITS
# =============================================================================
# Conservative operational parameters for system reliability
MAX_PROCESSING_TIME = 30           # Maximum processing time (seconds)
DATA_FRESHNESS_HOURS = 6           # Maximum age of weather data (hours)
PREDICTION_HORIZON_DAYS = 14       # Maximum prediction horizon (days)

# Alert and notification thresholds
ALERT_CRITICAL_THRESHOLD = 0.90    # 90% - critical alert threshold
ALERT_WARNING_THRESHOLD = 0.70     # 70% - warning alert threshold
NOTIFICATION_FREQUENCY_HOURS = 12  # Minimum hours between notifications

# Data quality requirements
DATA_COMPLETENESS_MIN = 0.85       # 85% - minimum data completeness
SENSOR_ACCURACY_MIN = 0.90         # 90% - minimum sensor accuracy
MODEL_CONFIDENCE_MIN = 0.75        # 75% - minimum model confidence for recommendations

# =============================================================================
# CROP-SPECIFIC CONSTANTS
# =============================================================================
# Default crop parameters (can be overridden by specific crop data)
DEFAULT_GROWING_SEASON_DAYS = 120  # Default growing season length
DEFAULT_WATER_REQUIREMENT = 500    # Default seasonal water requirement (mm)
DEFAULT_FERTILIZER_EFFICIENCY = 0.70  # 70% fertilizer efficiency

# Critical growth stage durations (days)
SEEDLING_STAGE_DAYS = 21           # Seedling stage duration
VEGETATIVE_STAGE_DAYS = 45         # Vegetative growth stage
REPRODUCTIVE_STAGE_DAYS = 35       # Flowering/fruiting stage
MATURATION_STAGE_DAYS = 19         # Maturation stage

# =============================================================================
# ENVIRONMENTAL MONITORING LIMITS
# =============================================================================
# Air quality and environmental factors
HUMIDITY_OPTIMAL_MIN = 40          # 40% - minimum optimal humidity
HUMIDITY_OPTIMAL_MAX = 70          # 70% - maximum optimal humidity
HUMIDITY_DISEASE_RISK = 80         # 80% - humidity level increasing disease risk

WIND_SPEED_CALM = 5                # Below 5 km/h - calm conditions
WIND_SPEED_MODERATE = 20           # 5-20 km/h - moderate wind
WIND_SPEED_HIGH = 40               # Above 40 km/h - high wind, potential damage

# Solar radiation thresholds (MJ/m²/day)
SOLAR_RADIATION_LOW = 10           # Low solar radiation
SOLAR_RADIATION_OPTIMAL = 20       # Optimal solar radiation
SOLAR_RADIATION_HIGH = 30          # High solar radiation

# =============================================================================
# SAFETY AND COMPLIANCE CONSTANTS
# =============================================================================
# Regulatory and safety compliance values
PESTICIDE_SAFETY_BUFFER_DAYS = 7   # Days before harvest after pesticide application
WATER_QUALITY_PH_MIN = 6.0         # Minimum acceptable water pH
WATER_QUALITY_PH_MAX = 8.0         # Maximum acceptable water pH

# Emergency response thresholds
EMERGENCY_DROUGHT_DAYS = 21        # Consecutive days without rain = drought emergency
EMERGENCY_FLOOD_RAINFALL = 150     # Daily rainfall (mm) = flood emergency
EMERGENCY_TEMP_DURATION = 72       # Hours of extreme temperature = emergency

# System reliability constants
BACKUP_DATA_RETENTION_DAYS = 90    # Days to retain backup data
LOG_RETENTION_DAYS = 30            # Days to retain system logs
MAINTENANCE_INTERVAL_DAYS = 7      # Days between system maintenance checks