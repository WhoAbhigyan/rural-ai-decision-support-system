#!/usr/bin/env python3
"""
Streamlit Web Interface for Rural Agriculture Decision Support System.

This web interface provides an easy-to-use frontend for farmers and agricultural
advisors to get farming recommendations. It calls the existing decision engine
and displays results in a farmer-friendly format.

Usage:
    streamlit run streamlit_app.py

Author: Agriculture Decision Support System
Version: 1.0
"""

import streamlit as st
import sys
import os
from datetime import datetime
from io import BytesIO

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import PDF generation library
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    PDF_AVAILABLE = True
except ImportError:
    try:
        from fpdf import FPDF
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False

try:
    from api.decision_engine import run_decision_engine
except ImportError as e:
    st.error(f"System Error: Could not load decision engine - {e}")
    st.error("Please ensure all system files are present.")
    st.stop()


def main():
    """Main Streamlit application."""
    
    # =============================================================================
    # PAGE CONFIGURATION
    # =============================================================================
    st.set_page_config(
        page_title="Agriculture Decision Support",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # =============================================================================
    # APP TITLE AND DESCRIPTION
    # =============================================================================
    st.title("🌾 Rural Agriculture Decision Support System")
    st.markdown("---")
    
    st.markdown("""
    **Get safe, science-based farming recommendations for your crops.**
    
    This tool analyzes your current farming conditions and provides conservative recommendations 
    to help you make informed decisions that prioritize your safety and economic well-being.
    
    ⚠️ **Important**: This system prioritizes farmer safety over maximum profit. 
    Recommendations are designed to reduce risk and protect your investment.
    """)
    
    st.markdown("---")
    
    # =============================================================================
    # INPUT FORM
    # =============================================================================
    st.header("📝 Enter Your Farming Conditions")
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌤️ Weather Conditions")
        
        rainfall_mm = st.number_input(
            "Recent Rainfall (mm)",
            min_value=0.0,
            max_value=500.0,
            value=15.0,
            step=0.1,
            help="Amount of rainfall in your area over the past week"
        )
        
        temperature_c = st.number_input(
            "Current Temperature (°C)",
            min_value=-10.0,
            max_value=50.0,
            value=25.0,
            step=0.1,
            help="Current air temperature in your area"
        )
        
        humidity_percent = st.number_input(
            "Current Humidity (%)",
            min_value=0.0,
            max_value=100.0,
            value=65.0,
            step=1.0,
            help="Current air humidity percentage"
        )
    
    with col2:
        st.subheader("🌱 Field Conditions")
        
        soil_type = st.selectbox(
            "Soil Type",
            options=["CLAY", "LOAM", "SANDY", "SILT"],
            index=1,  # Default to LOAM
            help="Select your primary soil type:\n"
                 "• CLAY: Heavy soil, holds water well\n"
                 "• LOAM: Best soil type, good drainage\n"
                 "• SANDY: Light soil, drains quickly\n"
                 "• SILT: Fine soil, good water retention"
        )
        
        crop_type = st.text_input(
            "Crop Type",
            value="wheat",
            help="Enter the crop you want to grow (e.g., wheat, rice, cotton, maize)"
        ).lower().strip()
        
        available_water_mm = st.number_input(
            "Available Water for Irrigation (mm)",
            min_value=0.0,
            max_value=1000.0,
            value=50.0,
            step=1.0,
            help="Amount of water available for irrigation"
        )
        
        leaf_image_provided = st.checkbox(
            "Leaf Images Available for Disease Analysis ℹ️ Image-based disease detection is rule-based in this version. "
            "Advanced image analysis will be added in future updates.",
            value=False,
            help="Check if you have leaf images for disease detection"
            
        )
    
    # =============================================================================
    # OPTIONAL INPUTS
    # =============================================================================
    with st.expander("📋 Optional Information"):
        col3, col4 = st.columns(2)
        
        with col3:
            farmer_id = st.text_input(
                "Farmer ID/Name (Optional)",
                value="",
                help="Your identification or name"
            )
            
            region = st.text_input(
                "Region/District (Optional)",
                value="",
                help="Your geographic region or district"
            )
        
        with col4:
            growing_stage = st.selectbox(
                "Current Growing Stage (Optional)",
                options=["", "seedling", "vegetative", "flowering", "reproductive", "maturation", "harvest"],
                index=0,
                help="Current stage of crop growth"
            )
    
    # =============================================================================
    # RECOMMENDATION BUTTON
    # =============================================================================
    st.markdown("---")
    
    # Center the button
    col_center = st.columns([1, 2, 1])
    with col_center[1]:
        get_recommendation = st.button(
            "🔍 Get Farming Recommendation",
            type="primary",
            use_container_width=True
        )
    
    # =============================================================================
    # RESULTS DISPLAY
    # =============================================================================
    if get_recommendation:
        # Validate inputs
        if not crop_type:
            st.error("❌ Please enter a crop type.")
            st.stop()
        
        # Prepare inputs for decision engine
        inputs = {
            'rainfall_mm': rainfall_mm,
            'temperature_c': temperature_c,
            'humidity_percent': humidity_percent,
            'soil_type': soil_type,
            'crop_type': crop_type,
            'available_water_mm': available_water_mm,
            'leaf_image_provided': leaf_image_provided
        }
        
        # Add optional inputs if provided
        if farmer_id:
            inputs['farmer_id'] = farmer_id
        if region:
            inputs['region'] = region
        if growing_stage:
            inputs['growing_stage'] = growing_stage
        
        # Show processing message
        with st.spinner('🔄 Analyzing your farming conditions...'):
            try:
                # Call decision engine
                result = run_decision_engine(inputs)
                
                # Display results
                display_results(result, inputs)
                
            except Exception as e:
                st.error(f"❌ **System Error**: {str(e)}")
                st.error("Please check your inputs and try again. If the problem persists, contact technical support.")


def display_results(result, inputs):
    """
    Display the decision engine results in a user-friendly format.
    
    Args:
        result (dict): Results from the decision engine
        inputs (dict): Original input parameters
    """
    st.markdown("---")
    st.header("📊 Your Farming Recommendation")
    
    # Extract key information
    final_decision = result.get('final_decision', 'UNKNOWN')
    overall_risk_level = result.get('overall_risk_level', 'UNKNOWN')
    explanation = result.get('explanation', 'No explanation available.')
    yield_summary = result.get('yield_summary', {})
    disease_summary = result.get('disease_summary', {})
    recommendations = result.get('recommendations', [])
    
    # =============================================================================
    # MAIN DECISION DISPLAY
    # =============================================================================
    decision_config = {
        'PROCEED': {
            'message': '✅ **PROCEED WITH FARMING**',
            'type': 'success',
            'description': 'Conditions support farming with standard practices.'
        },
        'REDUCE_INPUTS': {
            'message': '⚠️ **PROCEED WITH CAUTION**',
            'type': 'warning', 
            'description': 'Reduce investment and implement enhanced risk management.'
        },
        'AVOID_FARMING': {
            'message': '🛑 **AVOID FARMING FOR NOW**',
            'type': 'error',
            'description': 'Current conditions pose significant risks. Wait for better conditions.'
        }
    }
    
    config = decision_config.get(final_decision, {
        'message': f'❓ **{final_decision}**',
        'type': 'info',
        'description': 'Unknown decision status.'
    })
    
    # Display main decision with appropriate styling
    if config['type'] == 'success':
        st.success(config['message'])
    elif config['type'] == 'warning':
        st.warning(config['message'])
    elif config['type'] == 'error':
        st.error(config['message'])
    else:
        st.info(config['message'])
    
    st.write(config['description'])
    
    # =============================================================================
    # RISK LEVEL AND SUMMARY
    # =============================================================================
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Risk level with color coding
        risk_colors = {
            'LOW': '🟢',
            'MEDIUM': '🟡',
            'HIGH': '🔴'
        }
        risk_icon = risk_colors.get(overall_risk_level, '⚪')
        st.metric(
            label="Overall Risk Level",
            value=f"{risk_icon} {overall_risk_level}"
        )
    
    with col2:
        # Expected yield
        expected_yield = yield_summary.get('expected_yield_percentage', 0)
        st.metric(
            label="Expected Yield",
            value=f"{expected_yield:.0f}%",
            help="Percentage of maximum potential yield"
        )
    
    with col3:
        # Disease risk
        disease_risk = disease_summary.get('risk_level', 'UNKNOWN')
        disease_colors = {
            'LOW': '🟢',
            'MEDIUM': '🟡', 
            'HIGH': '🔴'
        }
        disease_icon = disease_colors.get(disease_risk, '⚪')
        st.metric(
            label="Disease Risk",
            value=f"{disease_icon} {disease_risk}"
        )
    
    # =============================================================================
    # DETAILED EXPLANATION
    # =============================================================================
    st.subheader("📋 Detailed Explanation")
    st.write(explanation)
    
    # =============================================================================
    # RECOMMENDATIONS
    # =============================================================================
    if recommendations:
        st.subheader("💡 Key Recommendations")
        
        # Display top 5 recommendations
        for i, rec in enumerate(recommendations[:5], 1):
            st.write(f"**{i}.** {rec}")
        
        # Show additional recommendations if available
        if len(recommendations) > 5:
            with st.expander(f"View {len(recommendations) - 5} Additional Recommendations"):
                for i, rec in enumerate(recommendations[5:], 6):
                    st.write(f"**{i}.** {rec}")
    
    # =============================================================================
    # TECHNICAL DETAILS (EXPANDABLE)
    # =============================================================================
    with st.expander("🔧 Technical Details"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Yield Analysis:**")
            confidence_level = yield_summary.get('confidence_level', 'Unknown')
            confidence_score = yield_summary.get('confidence_score', 0)
            st.write(f"• Confidence: {confidence_level} ({confidence_score:.2f})")
            
            st.write("**Disease Analysis:**")
            disease_score = disease_summary.get('risk_score', 0)
            image_analysis = disease_summary.get('image_analysis', 'Not available')
            st.write(f"• Risk Score: {disease_score:.2f}")
            st.write(f"• Image Analysis: {image_analysis}")
        
        with col2:
            # Processing information
            processing_info = result.get('processing_info', {})
            processing_time = processing_info.get('processing_time_seconds', 0)
            st.write("**Processing Information:**")
            st.write(f"• Processing Time: {processing_time:.2f} seconds")
            
            # Show warnings if any
            warnings = processing_info.get('warnings', [])
            if warnings:
                st.write("**System Warnings:**")
                for warning in warnings[:3]:  # Show top 3 warnings
                    st.write(f"• {warning}")
            
            # Show errors if any
            errors = processing_info.get('errors', [])
            if errors:
                st.write("**System Alerts:**")
                for error in errors[:2]:  # Show top 2 errors
                    st.write(f"• {error}")
    
    # =============================================================================
    # SAFETY REMINDER
    # =============================================================================
    st.markdown("---")
    st.info("""
    🛡️ **Safety Reminder**: This system prioritizes your safety and economic protection. 
    Recommendations are conservative and designed to minimize risk. Always consider local 
    conditions and consult with agricultural extension officers for additional guidance.
    """)
    
    # =============================================================================
    # PDF DOWNLOAD BUTTON
    # =============================================================================
    if PDF_AVAILABLE:
        st.markdown("---")
        
        # Generate PDF report
        pdf_buffer = generate_pdf_report(result, inputs)
        
        if pdf_buffer:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"farming_report_{timestamp}.pdf"
            
            # Download button
            st.download_button(
                label="📄 Download Farming Report (PDF)",
                data=pdf_buffer.getvalue(),
                file_name=filename,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
    else:
        st.markdown("---")
        st.warning("📄 PDF download feature requires reportlab or fpdf library to be installed.")


def generate_pdf_report(result, inputs):
    """
    Generate a PDF report of the farming recommendation.
    
    Args:
        result (dict): Results from the decision engine
        inputs (dict): Original input parameters
        
    Returns:
        BytesIO: PDF buffer ready for download
    """
    if not PDF_AVAILABLE:
        return None
    
    try:
        # Try reportlab first
        if 'reportlab' in sys.modules:
            return generate_pdf_reportlab(result, inputs)
        else:
            return generate_pdf_fpdf(result, inputs)
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None


def generate_pdf_reportlab(result, inputs):
    """Generate PDF using reportlab library."""
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    # Title
    story.append(Paragraph("Rural Agriculture Decision Support Report", title_style))
    story.append(Spacer(1, 20))
    
    # Metadata section
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    farmer_id = inputs.get('farmer_id', 'Not provided')
    region = inputs.get('region', 'Not provided')
    
    story.append(Paragraph("Report Information", heading_style))
    story.append(Paragraph(f"<b>Generated on:</b> {current_time}", normal_style))
    story.append(Paragraph(f"<b>Farmer ID:</b> {farmer_id}", normal_style))
    story.append(Paragraph(f"<b>Region:</b> {region}", normal_style))
    
    # Input Summary section
    story.append(Paragraph("Input Summary", heading_style))
    story.append(Paragraph(f"<b>Crop type:</b> {inputs.get('crop_type', 'Not specified').title()}", normal_style))
    story.append(Paragraph(f"<b>Soil type:</b> {inputs.get('soil_type', 'Not specified')}", normal_style))
    story.append(Paragraph(f"<b>Rainfall:</b> {inputs.get('rainfall_mm', 0):.1f} mm", normal_style))
    story.append(Paragraph(f"<b>Temperature:</b> {inputs.get('temperature_c', 0):.1f} °C", normal_style))
    story.append(Paragraph(f"<b>Humidity:</b> {inputs.get('humidity_percent', 0):.1f} %", normal_style))
    story.append(Paragraph(f"<b>Available irrigation water:</b> {inputs.get('available_water_mm', 0):.1f} mm", normal_style))
    
    # Decision Summary section
    story.append(Paragraph("Decision Summary", heading_style))
    final_decision = result.get('final_decision', 'UNKNOWN').replace('_', ' ')
    overall_risk = result.get('overall_risk_level', 'UNKNOWN')
    expected_yield = result.get('yield_summary', {}).get('expected_yield_percentage', 0)
    disease_risk = result.get('disease_summary', {}).get('risk_level', 'UNKNOWN')
    
    story.append(Paragraph(f"<b>Final decision:</b> {final_decision}", normal_style))
    story.append(Paragraph(f"<b>Overall risk level:</b> {overall_risk}", normal_style))
    story.append(Paragraph(f"<b>Expected yield:</b> {expected_yield:.0f}%", normal_style))
    story.append(Paragraph(f"<b>Disease risk level:</b> {disease_risk}", normal_style))
    
    # Explanation section
    story.append(Paragraph("Explanation", heading_style))
    explanation = result.get('explanation', 'No explanation available.')
    story.append(Paragraph(explanation, normal_style))
    
    # Recommendations section
    recommendations = result.get('recommendations', [])
    if recommendations:
        story.append(Paragraph("Recommendations", heading_style))
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", normal_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_pdf_fpdf(result, inputs):
    """Generate PDF using fpdf library."""
    buffer = BytesIO()
    
    # Create PDF document
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 18)
    
    # Title
    pdf.cell(0, 15, 'Rural Agriculture Decision Support Report', 0, 1, 'C')
    pdf.ln(10)
    
    # Metadata section
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    farmer_id = inputs.get('farmer_id', 'Not provided')
    region = inputs.get('region', 'Not provided')
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, 'Report Information', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 6, f'Generated on: {current_time}', 0, 1)
    pdf.cell(0, 6, f'Farmer ID: {farmer_id}', 0, 1)
    pdf.cell(0, 6, f'Region: {region}', 0, 1)
    pdf.ln(5)
    
    # Input Summary section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, 'Input Summary', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 6, f'Crop type: {inputs.get("crop_type", "Not specified").title()}', 0, 1)
    pdf.cell(0, 6, f'Soil type: {inputs.get("soil_type", "Not specified")}', 0, 1)
    pdf.cell(0, 6, f'Rainfall: {inputs.get("rainfall_mm", 0):.1f} mm', 0, 1)
    pdf.cell(0, 6, f'Temperature: {inputs.get("temperature_c", 0):.1f} °C', 0, 1)
    pdf.cell(0, 6, f'Humidity: {inputs.get("humidity_percent", 0):.1f} %', 0, 1)
    pdf.cell(0, 6, f'Available irrigation water: {inputs.get("available_water_mm", 0):.1f} mm', 0, 1)
    pdf.ln(5)
    
    # Decision Summary section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, 'Decision Summary', 0, 1)
    pdf.set_font('Arial', '', 11)
    
    final_decision = result.get('final_decision', 'UNKNOWN').replace('_', ' ')
    overall_risk = result.get('overall_risk_level', 'UNKNOWN')
    expected_yield = result.get('yield_summary', {}).get('expected_yield_percentage', 0)
    disease_risk = result.get('disease_summary', {}).get('risk_level', 'UNKNOWN')
    
    pdf.cell(0, 6, f'Final decision: {final_decision}', 0, 1)
    pdf.cell(0, 6, f'Overall risk level: {overall_risk}', 0, 1)
    pdf.cell(0, 6, f'Expected yield: {expected_yield:.0f}%', 0, 1)
    pdf.cell(0, 6, f'Disease risk level: {disease_risk}', 0, 1)
    pdf.ln(5)
    
    # Explanation section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, 'Explanation', 0, 1)
    pdf.set_font('Arial', '', 11)
    
    explanation = result.get('explanation', 'No explanation available.')
    # Split long text into multiple lines
    explanation_lines = explanation.split('. ')
    for line in explanation_lines:
        if line.strip():
            # Handle long lines by splitting them
            words = line.split()
            current_line = ""
            for word in words:
                if len(current_line + word) < 80:  # Approximate character limit per line
                    current_line += word + " "
                else:
                    if current_line:
                        pdf.cell(0, 6, current_line.strip(), 0, 1)
                    current_line = word + " "
            if current_line:
                pdf.cell(0, 6, current_line.strip(), 0, 1)
    pdf.ln(5)
    
    # Recommendations section
    recommendations = result.get('recommendations', [])
    if recommendations:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, 'Recommendations', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        for i, rec in enumerate(recommendations, 1):
            # Handle long recommendations
            rec_text = f'{i}. {rec}'
            words = rec_text.split()
            current_line = ""
            for word in words:
                if len(current_line + word) < 80:
                    current_line += word + " "
                else:
                    if current_line:
                        pdf.cell(0, 6, current_line.strip(), 0, 1)
                    current_line = word + " "
            if current_line:
                pdf.cell(0, 6, current_line.strip(), 0, 1)
    
    # Save to buffer
    pdf_output = pdf.output(dest='S').encode('latin-1')
    buffer.write(pdf_output)
    buffer.seek(0)
    return buffer


# =============================================================================
# SIDEBAR (OPTIONAL INFORMATION)
# =============================================================================
def show_sidebar():
    """Display sidebar with additional information."""
    st.sidebar.title("ℹ️ About This System")
    
    st.sidebar.markdown("""
    **Rural Agriculture Decision Support System**
    
    This tool provides:
    • Crop yield predictions
    • Disease risk assessment
    • Irrigation recommendations
    • Overall farming risk evaluation
    
    **Key Features:**
    • Offline operation
    • Conservative recommendations
    • Explainable decisions
    • Farmer safety focus
    """)
    
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("""
    **How to Use:**
    1. Enter your current farming conditions
    2. Click "Get Recommendation"
    3. Review the results carefully
    4. Follow the safety recommendations
    """)
    
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("""
    **Need Help?**
    
    Contact your local agricultural extension officer for:
    • Soil testing guidance
    • Crop variety selection
    • Disease identification
    • Weather monitoring
    """)


if __name__ == "__main__":
    # Show sidebar
    show_sidebar()
    
    # Run main application
    main()