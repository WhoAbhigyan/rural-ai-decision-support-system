# Requirements Document  
## Rural AI Decision Support System

---

## 1. Problem Statement

Build an AI-powered solution that supports **rural ecosystems, sustainability, and resource-efficient systems**.

The solution should help rural communities—especially farmers—make **better, safer, and more informed decisions** around agriculture, resources, and livelihoods using accessible technology.

**Focus Areas:**
- Practical innovation (usable in real rural settings)
- Scalability across regions and crops
- Long-term societal and environmental value

---

## 2. Project Objective

The Rural AI Decision Support System aims to assist farmers in making **conservative, explainable, and risk-aware farming decisions** using local field and weather conditions instead of guesswork.

The system prioritizes:
- Farmer safety over profit maximization
- Water conservation and sustainability
- Reduction of economic risk in uncertain conditions

---

## 3. Key Functional Requirements

### 3.1 Input Collection
The system shall accept the following inputs:
- Rainfall (mm)
- Temperature (°C)
- Humidity (%)
- Soil type (Clay, Loam, Sandy, Silt)
- Crop type
- Available irrigation water (mm)
- Crop growth stage (optional)
- Leaf image availability for disease detection (optional)
- Farmer metadata (optional: region, farmer ID)

---

### 3.2 Crop Yield Prediction
- Predict expected crop yield as a **percentage of maximum potential**
- Provide a **confidence score** for the prediction
- Use lightweight, explainable ML + rule-based logic
- Avoid black-box or opaque models

---

### 3.3 Disease Risk Assessment
- Detect disease risk based on:
  - Environmental conditions
  - Crop type
  - Optional leaf image availability (simulated / extensible)
- Output:
  - Disease risk level (LOW / MEDIUM / HIGH)
  - Disease risk score
- Prefer conservative disease estimates to prevent crop loss

---

### 3.4 Irrigation Optimization
- Recommend **water-conservative irrigation amounts**
- Adjust recommendations based on:
  - Soil water retention
  - Rainfall credit
  - Crop growth stage
  - Environmental evaporation factors
- Enforce daily and weekly safety limits
- Explain why each irrigation recommendation is made

---

### 3.5 Overall Risk Assessment
- Combine:
  - Yield risk
  - Disease risk
  - Water stress risk
  - Weather uncertainty
- Produce:
  - Overall risk score (0–1)
  - Risk level (LOW / MEDIUM / HIGH)
- Apply conservative bias to protect farmers from uncertainty

---

### 3.6 Decision Recommendation
The system shall output one of the following decisions:
- **PROCEED** – Conditions are suitable for farming
- **REDUCE_INPUTS** – Farm cautiously with reduced investment
- **AVOID_FARMING** – Risk is too high under current conditions

Each decision must include a **plain-language explanation**.

---

### 3.7 Explainability
- Every recommendation must include:
  - Human-readable explanation
  - Key factors influencing the decision
- Explanations must be understandable by non-technical users

---

### 3.8 User Interfaces
- Command-Line Interface (CLI) for offline rural usage
- Streamlit-based web interface for demos and advisors
- Downloadable report support (PDF-ready architecture)

---

## 4. Non-Functional Requirements

### 4.1 Offline-First Operation
- System must run without internet access
- All logic executed locally

---

### 4.2 Scalability
- Easily extendable to:
  - New crops
  - New regions
  - Additional sensors or data sources

---

### 4.3 Safety & Ethics
- Conservative defaults to avoid financial harm
- No dependency on private or sensitive data
- Transparent decision-making

---

### 4.4 Performance
- Single request processing under a few seconds
- Lightweight models suitable for low-resource devices

---

## 5. Target Users
- Small and marginal farmers
- Agricultural field officers
- NGOs and rural development agencies
- Sustainability and climate-tech programs

---

## 6. Constraints
- Uses only synthetic or publicly acceptable logic
- No real farmer data storage by default
- Designed for explainability, not aggressive optimization
