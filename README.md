# 🌾 Rural Agriculture Decision Support System

An **AI-powered, offline-first decision support system** designed to help rural farmers make **safe, explainable, and risk-aware farming decisions** using local conditions instead of guesswork.

This project prioritizes **farmer safety, water conservation, and economic risk reduction** over aggressive profit-maximizing predictions.

---

## 🧩 Official Problem Statement (Challenge Context)

**Problem Statement:**  
Build an **AI-powered solution** that supports **rural ecosystems, sustainability, or resource-efficient systems**.

### What you may build
- Systems that improve **access to information, markets, or services** in rural contexts  
- AI tools supporting **agriculture, supply chains, or local economies**  
- **Climate, resource, or sustainability intelligence** tools  
- Solutions that help communities make **better decisions around resources and livelihoods**

### Focus Areas
- **Practical innovation**
- **Scalability**
- **Long-term societal value**

---

## ✅ How This Project Solves the Problem

The **Rural Agriculture Decision Support System** directly addresses the problem statement by:

- 🌾 Supporting **rural agriculture** with explainable, farmer-first AI decisions  
- 💧 Promoting **resource-efficient irrigation and water conservation**  
- 🛡️ Reducing **economic risk and crop loss** for small and marginal farmers  
- 📡 Working **offline**, making it usable in low-connectivity rural regions  
- 🧠 Helping communities make **better, safer decisions** around farming and livelihoods  

This is a **production-grade system**, not a demo or toy model.

---

## 🚜 Project Overview

Farmers often rely on guesswork, incomplete advice, or generic recommendations, leading to:
- Crop failure
- Water wastage
- Financial losses

This system uses **local field conditions + conservative AI logic** to guide farmers safely.

### Inputs
- Rainfall
- Temperature
- Humidity
- Soil type
- Crop type
- Available irrigation water
- Optional leaf images (for disease risk)

### Outputs
- ✅ Expected crop yield (conservative estimate)
- 🦠 Disease risk assessment
- 💧 Optimized irrigation plan
- ⚠️ Overall farming risk level
- 📋 Clear, explainable recommendations
- 📄 Downloadable PDF farming report

---

## 🧠 Key Features

- Explainable AI (no black-box decisions)
- Rule-based + lightweight ML logic
- Offline-first architecture
- Conservative, farmer-safety-first decisions
- Water-efficient irrigation optimization
- Streamlit web interface + CLI
- PDF report generation for farmers and advisors

---

## 🏗️ System Architecture

rural-ai-decision-system/
│
├── api/
│ └── decision_engine.py
│
├── models/
│ ├── yield_predictor.py
│ ├── disease_detector.py
│ └── irrigation_optimizer.py
│
├── rules/
│ ├── farming_rules.py
│ └── risk_assessor.py
│
├── ui/
│ ├── cli_app.py
│ └── streamlit_app.py
│
├── data/
│ └── sample_inputs.json
│
├── main.py
├── README.md
└── requirements.txt

---

## 🖥️ How to Run the Project

### 1️⃣ Install Requirements

```bash
pip install streamlit reportlab

## For CLI interface python main.py

## To run using demo in CLI use python main.py --demo
