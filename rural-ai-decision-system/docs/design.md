# System Design Document  
## Rural AI Decision Support System

---

## 1. Design Philosophy

The system is designed with the following principles:

- **Farmer-first, not profit-first**
- **Explainable AI over black-box models**
- **Conservative decision-making to reduce risk**
- **Offline-first for rural deployment**
- **Modular architecture for easy extension**

---

## 2. High-Level Architecture

User Input (CLI / Streamlit UI)
↓
Input Validation Layer
↓
Decision Engine
├── Yield Predictor
├── Disease Risk Detector
├── Irrigation Optimizer
└── Risk Assessment Engine
↓
Final Decision Generator
↓
Explainable Output + Recommendations

---

## 3. Core Modules

### 3.1 Decision Engine (`api/decision_engine.py`)
- Central orchestrator of the system
- Calls all sub-modules
- Aggregates results into a final decision
- Handles warnings, errors, and processing metadata

---

### 3.2 Yield Prediction Module
- Combines:
  - Rule-based agronomic logic
  - Lightweight statistical assumptions
- Outputs:
  - Expected yield percentage
  - Confidence score
- Designed to be explainable and conservative

---

### 3.3 Disease Detection Module
- Evaluates disease risk using:
  - Crop type
  - Weather conditions
  - Optional image availability flag
- Produces:
  - Disease risk score
  - Risk level (LOW / MEDIUM / HIGH)
- Structured to support future image-based ML models

---

### 3.4 Irrigation Optimization Module
- Calculates irrigation needs using:
  - Soil water retention
  - Rainfall efficiency
  - Evapotranspiration estimates
  - Crop growth stage
- Enforces:
  - Daily and weekly water limits
  - Safety margins
- Generates clear irrigation schedules and tips

---

### 3.5 Risk Assessment Engine
- Combines all risk signals into a single score
- Uses weighted, conservative aggregation
- Applies additional penalties for:
  - Low confidence
  - High uncertainty
  - Low farmer experience
- Outputs final risk level and mitigation suggestions

---

## 4. Data Flow

1. User provides inputs via UI
2. Inputs are validated and normalized
3. Each analysis module runs independently
4. Results are combined conservatively
5. Final decision + explanation is generated
6. Output is displayed or exported

---

## 5. Explainability Layer

Each module returns:
- Numeric scores
- Human-readable explanations
- Key contributing factors

The final output merges these explanations into:
- Farmer-friendly summary
- Optional technical breakdown (for evaluators)

---

## 6. User Interface Design

### 6.1 CLI Interface
- Text-based
- Designed for low-literacy and low-tech environments
- Step-by-step prompts

### 6.2 Streamlit Web Interface
- Visual, form-based UI
- Suitable for demos, advisors, and training
- Expandable technical sections
- PDF-report-ready architecture

---

## 7. Storage & Persistence (Optional)
- No default persistent storage (privacy-first)
- Architecture supports:
  - Local file storage
  - Report downloads (PDF)
  - Backend databases if enabled later

---

## 8. Technology Stack

- **Language:** Python
- **UI:** Streamlit, CLI
- **AI Approach:** Rule-based + lightweight ML logic
- **Deployment:** Offline local execution
- **Extensibility:** Modular Python packages

---

## 9. Scalability & Future Enhancements

- Real ML models for disease detection
- Mobile app integration
- Regional language support
- Government weather API integration
- Farmer history tracking (opt-in)

---

## 10. Why This Design Works for Rural India

- Minimal infrastructure dependency
- Transparent recommendations build trust
- Conservative decisions reduce farmer losses
- Easily adaptable across crops and regions
- Suitable for NGOs, governments, and climate programs
