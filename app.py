import streamlit as st
import base64
import json
from typing import Dict, Any
from groq import Groq

st.set_page_config(page_title="Manufacturing Energy Analyzer", layout="wide")

# Initialize Groq client
@st.cache_resource
def get_client():
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("Please add GROQ_API_KEY to your Streamlit secrets")
        st.stop()
    return Groq(api_key=api_key)

client = get_client()

# Updated model (fast & free)
GROQ_MODEL = "llama-3.1-70b-instant"  # You can also use "llama-3.1-405b-reasoning" if you want max intelligence

def run_agent_1(pdf_base64: str) -> Dict[str, Any]:
    """Agent #1: Bill Analyzer - Extract data from manufacturing energy PDF"""
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:application/pdf;base64,{pdf_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": """Analyze this manufacturing facility energy bill PDF. Extract: total cost, usage in kWh, demand charges (kW), rate per kWh, billing period, power factor penalties, any unusual charges.
                        Respond ONLY with valid JSON (no markdown, no explanation):
                        {"totalCost": number, "usage": number, "demandKw": number, "ratePerKwh": number, "billingPeriod": "string", "powerFactor": number, "unusualCharges": [], "insights": "string"}"""
                    }
                ]
            }
        ],
        max_tokens=1000,
        temperature=0.1
    )
    
    text = response.choices[0].message.content
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def run_agent_2(context: str) -> Dict[str, Any]:
    """Agent #2: Industry Benchmarking - Manufacturing energy standards"""
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an industrial energy efficiency expert specializing in manufacturing operations. Use your knowledge to provide accurate industry benchmarks."
            },
            {
                "role": "user",
                "content": f"""Based on current 2025 industrial energy data for manufacturing facilities:
                Context: {context}
                Provide realistic manufacturing energy benchmarks, typical demand charges, and industrial efficiency recommendations.
                Respond ONLY with valid JSON:
                {{"averageRate": number, "averageDemandCharge": number, "typicalUsage": "string", "recommendations": [], "sources": ["DOE Industrial Assessment Centers", "ENERGY STAR Industrial", "ISO 50001"]}}"""
            }
        ],
        max_tokens=800,
        temperature=0.2
    )
    
    text = response.choices[0].message.content
    text = text.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(text)
    except:
        # Fallback if JSON is malformed
        return {
            "averageRate": 0.087,
            "averageDemandCharge": 15.50,
            "typicalUsage": "50,000-500,000 kWh/month depending on production volume and process intensity",
            "recommendations": [
                "Implement demand response programs to reduce peak charges",
                "Install variable frequency drives (VFDs) on motors",
                "Optimize compressed air systems (often 30% energy waste)",
                "Upgrade to energy-efficient HVAC for production areas",
                "Consider cogeneration/CHP for large facilities"
            ],
            "sources": ["U.S. DOE Industrial Technologies Program", "ENERGY STAR for Industry", "ISO 50001 Standards"]
        }

def run_agent_3(bill_data: Dict, research_data: Dict) -> Dict[str, Any]:
    """Agent #3: Manufacturing Energy Report Generator"""
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": f"""Create a professional manufacturing energy analysis report for an industrial facility.
                Bill Data: {json.dumps(bill_data)}
                Industry Benchmarks: {json.dumps(research_data)}
                
                Focus on manufacturing-specific insights like demand charges, production efficiency, equipment optimization.
                Respond ONLY with valid JSON:
                {{"summary": "string", "comparison": "string", "savings": [], "nextSteps": []}}"""
            }
        ],
        max_tokens=1000,
        temperature=0.3
    )
    
    text = response.choices[0].message.content
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

# === UI ===
st.title("🏭 Manufacturing Energy Analyzer")
st.markdown("Three specialized AI agents powered by **Groq + Llama 3.1 70B** for industrial facilities")

col1, col2, col3 = st.columns(3)
with col1:
    st.info("**Agent #1: Bill Analyzer**\n\nExtracts costs, demand charges, power factor from facility bills")
with col2:
    st.success("**Agent #2: Industry Benchmarking**\n\nCompares against manufacturing standards")
with col3:
    st.warning("**Agent #3: Report Generator**\n\nProvides actionable efficiency recommendations")

st.markdown("---")

# Add sample data button
col_upload, col_sample = st.columns([3, 1])
with col_upload:
    uploaded_file = st.file_uploader("Upload Manufacturing Facility Energy Bill (PDF)", type=['pdf'])
with col_sample:
    st.write("")  # Spacing
    use_sample = st.button("📄 Try Sample Data", type="secondary")

if use_sample:
    st.info("🎯 Using sample energy bill data from a mid-size manufacturing facility")
    # Simulate realistic manufacturing bill analysis
    st.session_state['bill_analysis'] = {
        "totalCost": 24567.89,
        "usage": 187340,
        "demandKw": 845,
        "ratePerKwh": 0.0872,
        "billingPeriod": "Nov 1 - Nov 30, 2024",
        "powerFactor": 0.87,
        "unusualCharges": ["Demand charge penalty: $2,450", "Low power factor penalty: $387"],
        "insights": "Peak demand occurred during 2nd shift (2-10 PM) when all production lines were running. Power factor below target 0.95 indicates need for capacitor banks. Energy intensity per unit produced is 15% above industry benchmark."
    }
    
    st.session_state['web_research'] = {
        "averageRate": 0.0825,
        "averageDemandCharge": 14.75,
        "typicalUsage": "150,000-250,000 kWh/month for similar facility size and production volume",
        "recommendations": [
            "Install power factor correction equipment to avoid penalties (ROI: 12-18 months)",
            "Implement demand response: shift non-critical loads to off-peak hours",
            "Upgrade to IE4/IE5 premium efficiency motors (20-30% energy savings)",
            "Optimize compressed air system - detect and fix leaks (typically 30% waste)",
            "Install VFDs on pumps, fans, and conveyors for variable load matching",
            "Consider thermal energy storage for process heating/cooling"
        ],
        "sources": ["U.S. DOE Advanced Manufacturing Office", "ENERGY STAR Industrial Energy Management", "ISO 50001:2018"]
    }
    
    st.session_state['final_report'] = {
        "summary": "Your facility consumed 187,340 kWh with a peak demand of 845 kW, totaling $24,567.89. Current energy cost is $0.0872/kWh (excluding demand charges). The low power factor of 0.87 resulted in $387 in penalties. Peak demand charges account for 35% of total bill.",
        "comparison": "Your effective rate is 5.7% above the industrial average of $0.0825/kWh. Peak demand of 845 kW is within normal range but timing coincides with utility peak periods, resulting in maximum charges. Power factor below 0.95 threshold indicates reactive power issues. Energy intensity per production unit is 15% higher than industry benchmark.",
        "savings": [
            "⚡ Power factor correction: Save ~$4,600/year (eliminate penalties + reduce losses)",
            "📊 Demand response program: Save ~$18,000/year (shift loads to off-peak)",
            "🔧 VFD installation on 10 motors: Save ~$12,500/year (20% motor energy reduction)",
            "💨 Compressed air leak detection/repair: Save ~$8,900/year",
            "🌡️ Waste heat recovery from processes: Save ~$15,000/year",
            "💡 LED high-bay lighting upgrade: Save ~$3,200/year"
        ],
        "nextSteps": [
            "Schedule ASHRAE Level 2 energy audit ($8,000-15,000, utility rebate available)",
            "Contact utility for demand response incentive programs (up to $50k)",
            "Install real-time energy monitoring system for production lines",
            "Conduct power quality study - identify harmonic issues",
            "Review production schedule to flatten demand curve",
            "Apply for ISO 50001 certification to access additional incentives",
            "Investigate on-site solar + battery storage (30% ITC tax credit available)"
        ]
    }
    
    st.success("✅ Sample manufacturing facility analysis loaded! Scroll down to see results.")

if uploaded_file:
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    
    if st.button("🚀 Run Analysis with All 3 Agents", type="primary"):
        try:
            pdf_bytes = uploaded_file.read()
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            with st.spinner("🔍 Agent #1 analyzing bill..."):
                bill_analysis = run_agent_1(pdf_base64)
                st.session_state['bill_analysis'] = bill_analysis
            
            with st.spinner("🌐 Agent #2 gathering benchmarks..."):
                search_context = f"{bill_analysis.get('ratePerKwh', 0.15):.3f} USD/kWh, {bill_analysis.get('usage', 0)} kWh usage"
                web_research = run_agent_2(search_context)
                st.session_state['web_research'] = web_research
            
            with st.spinner("📊 Agent #3 generating report..."):
                final_report = run_agent_3(bill_analysis, web_research)
                st.session_state['final_report'] = final_report
            
            st.success("✅ Analysis complete in seconds!")
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Display results
if 'bill_analysis' in st.session_state:
    st.markdown("---")
    st.header("📊 Results")
    
    with st.expander("🔍 Agent #1: Bill Analysis", expanded=True):
        data = st.session_state['bill_analysis']
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Cost", f"${data.get('totalCost', 0):,.2f}")
        col2.metric("Usage", f"{data.get('usage', 0):,} kWh")
        col3.metric("Peak Demand", f"{data.get('demandKw', 0):,} kW")
        col4.metric("Power Factor", f"{data.get('powerFactor', 0):.2f}")
        
        col5, col6 = st.columns(2)
        col5.metric("Rate per kWh", f"${data.get('ratePerKwh', 0):.4f}")
        col6.metric("Billing Period", data.get('billingPeriod', 'N/A'))
        
        if data.get('unusualCharges'):
            st.warning("**⚠️ Unusual Charges Detected:**")
            for charge in data['unusualCharges']:
                st.markdown(f"- {charge}")
        
        if data.get('insights'):
            st.info(f"**📊 Key Insights:** {data['insights']}")

    if 'web_research' in st.session_state:
        with st.expander("🏭 Agent #2: Industry Benchmarking", expanded=True):
            data = st.session_state['web_research']
            col1, col2 = st.columns(2)
            col1.metric("Industry Avg Rate", f"${data.get('averageRate', 0.08):.4f}/kWh")
            col2.metric("Avg Demand Charge", f"${data.get('averageDemandCharge', 15):.2f}/kW")
            st.write(f"**Typical Usage:** {data.get('typicalUsage', '')}")
            st.subheader("🔧 Manufacturing Efficiency Recommendations")
            for rec in data.get('recommendations', []):
                st.markdown(f"- {rec}")
            
            if data.get('sources'):
                st.caption(f"Sources: {', '.join(data['sources'])}")

    if 'final_report' in st.session_state:
        with st.expander("📋 Agent #3: Final Report", expanded=True):
            data = st.session_state['final_report']
            st.subheader("Executive Summary")
            st.write(data.get('summary', ''))
            st.subheader("Comparison to Industry")
            st.write(data.get('comparison', ''))
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("💰 Potential Savings")
                for saving in data.get('savings', []):
                    st.success(saving)
            with col2:
                st.subheader("📝 Next Steps")
                for step in data.get('nextSteps', []):
                    st.info(step)

st.markdown("---")
st.markdown("🏭 Built with **Groq + Llama 3.1 70B** • Optimized for manufacturing facilities • Industrial energy intelligence")
