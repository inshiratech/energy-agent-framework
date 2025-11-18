import streamlit as st
import anthropic
import base64
import json
from typing import Dict, Any

st.set_page_config(page_title="Multi-Agent Energy Analyzer", layout="wide")

# Initialize Anthropic client
@st.cache_resource
def get_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.error("Please add ANTHROPIC_API_KEY to your Streamlit secrets")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

client = get_client()

def run_agent_1(pdf_base64: str) -> Dict[str, Any]:
    """Agent #1: Bill Analyzer - Extract data from PDF"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": """Analyze this energy bill. Extract: total cost, usage (kWh), rate per kWh, billing period, any unusual charges. 
                        Respond ONLY with valid JSON (no markdown):
                        {"totalCost": number, "usage": number, "ratePerKwh": number, "billingPeriod": "string", "unusualCharges": [], "insights": "string"}"""
                    }
                ]
            }
        ]
    )
    
    response_text = message.content[0].text
    # Clean any markdown formatting
    response_text = response_text.replace("```json", "").replace("```", "").strip()
    return json.loads(response_text)

def run_agent_2(context: str) -> Dict[str, Any]:
    """Agent #2: Web Researcher - Find industry benchmarks"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""Research industry benchmarks for: {context}
                Find average rates, typical usage patterns, and cost-saving recommendations.
                Respond ONLY with valid JSON (no markdown):
                {{"averageRate": number, "typicalUsage": "string", "recommendations": [], "sources": []}}"""
            }
        ],
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search"
            }
        ]
    )
    
    # Extract text from response
    response_text = ""
    for block in message.content:
        if block.type == "text":
            response_text += block.text
    
    response_text = response_text.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(response_text)
    except:
        # Fallback if parsing fails
        return {
            "averageRate": 0.13,
            "typicalUsage": "Based on industry standards",
            "recommendations": ["Monitor peak usage", "Consider energy-efficient appliances"],
            "sources": ["Industry data"]
        }

def run_agent_3(bill_data: Dict, research_data: Dict) -> Dict[str, Any]:
    """Agent #3: Report Generator - Compile findings"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""Generate a concise energy analysis report.
                Bill data: {json.dumps(bill_data)}
                Research data: {json.dumps(research_data)}
                Respond ONLY with valid JSON (no markdown):
                {{"summary": "string", "comparison": "string", "savings": [], "nextSteps": []}}"""
            }
        ]
    )
    
    response_text = message.content[0].text.replace("```json", "").replace("```", "").strip()
    return json.loads(response_text)

# UI Layout
st.title("🤖 Multi-Agent Energy Analyzer")
st.markdown("Three specialized AI agents working together to analyze your energy bills")

# Agent descriptions
col1, col2, col3 = st.columns(3)
with col1:
    st.info("**Agent #1: Bill Analyzer**\n\nExtracts costs, usage, and rates from PDF bills")
with col2:
    st.success("**Agent #2: Web Researcher**\n\nFinds industry benchmarks and trends")
with col3:
    st.warning("**Agent #3: Report Generator**\n\nCompiles insights into actionable report")

st.markdown("---")

# File upload
uploaded_file = st.file_uploader("Upload Energy Bill (PDF)", type=['pdf'])

if uploaded_file:
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    
    if st.button("🚀 Run Analysis with All 3 Agents", type="primary"):
        try:
            # Convert PDF to base64
            pdf_bytes = uploaded_file.read()
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Agent 1: Analyze bill
            with st.spinner("🔍 Agent #1 analyzing bill..."):
                bill_analysis = run_agent_1(pdf_base64)
                st.session_state['bill_analysis'] = bill_analysis
            
            # Agent 2: Research benchmarks
            with st.spinner("🌐 Agent #2 researching industry benchmarks..."):
                search_query = f"energy rate {bill_analysis['ratePerKwh']} kWh industry benchmark"
                web_research = run_agent_2(search_query)
                st.session_state['web_research'] = web_research
            
            # Agent 3: Generate report
            with st.spinner("📊 Agent #3 generating final report..."):
                final_report = run_agent_3(bill_analysis, web_research)
                st.session_state['final_report'] = final_report
            
            st.success("✅ Analysis complete!")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display results
if 'bill_analysis' in st.session_state:
    st.markdown("---")
    st.header("📊 Results")
    
    # Agent 1 Results
    with st.expander("🔍 Agent #1: Bill Analysis", expanded=True):
        data = st.session_state['bill_analysis']
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Cost", f"${data['totalCost']}")
        col2.metric("Usage", f"{data['usage']} kWh")
        col3.metric("Rate per kWh", f"${data['ratePerKwh']}")
        col4.metric("Billing Period", data['billingPeriod'])
        
        if data.get('insights'):
            st.info(f"**Insights:** {data['insights']}")
    
    # Agent 2 Results
    if 'web_research' in st.session_state:
        with st.expander("🌐 Agent #2: Industry Research", expanded=True):
            data = st.session_state['web_research']
            
            st.metric("Average Industry Rate", f"${data['averageRate']}/kWh")
            
            st.subheader("Recommendations")
            for rec in data['recommendations']:
                st.markdown(f"- {rec}")
    
    # Agent 3 Results
    if 'final_report' in st.session_state:
        with st.expander("📋 Agent #3: Final Report", expanded=True):
            data = st.session_state['final_report']
            
            st.subheader("Executive Summary")
            st.write(data['summary'])
            
            st.subheader("Comparison")
            st.write(data['comparison'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💰 Potential Savings")
                for saving in data['savings']:
                    st.success(saving)
            
            with col2:
                st.subheader("📝 Next Steps")
                for step in data['nextSteps']:
                    st.info(step)

# Footer
st.markdown("---")
st.markdown("Built with Claude API | Three specialized agents working in sequence")
