# app.py (updated version)
import streamlit as st
from datetime import datetime
from src.finbotics.query_processor import QueryProcessor
import re

# Page configuration
st.set_page_config(
    page_title="Finbotics - AI Financial Assistant",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stTextInput>div>div>input {
        font-size: 18px;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    .source-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
    }
    .error-box {
        background-color: #ffe0e0;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        color: #d00000;
    }
    .info-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        color: #856404;
    }
    .formatted-result {
        white-space: pre-wrap;
        font-family: monospace;
        font-size: 14px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize query processor
@st.cache_resource
def get_query_processor():
    return QueryProcessor()

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("💰 Finbotics")
    st.subheader("AI-Powered Financial Assistant")

# Create a horizontal line
st.markdown("---")

# Main content area
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    # Search box
    query = st.text_input(
        "Ask a financial question:",
        placeholder="e.g., How much did I spend on OpenAI in February?",
        key="query_input"
    )
    
    # Search button
    search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    # Results area
    if search_button and query:
        with st.spinner("Analyzing your query..."):
            try:
                processor = get_query_processor()
                
                # Process query
                result, sources, data_found = processor.process_query(query)
                
                # Add to history
                st.session_state.history.append({
                    'timestamp': datetime.now(),
                    'query': query,
                    'result': result,
                    'sources': sources,
                    'data_found': data_found
                })
                
                # Display result
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown("### 📊 Answer")
                
                if not data_found:
                    # Data not found - show referral message
                    st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    st.markdown("**ℹ️ Data Not Available**")
                    st.markdown(result)
                    st.markdown("\n**👤 Please contact your account executive for this information.**")
                    st.markdown("\n📧 **Email:** support@finbotics.ai")
                    st.markdown("📞 **Phone:** 1-800-FINBOTICS")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    # Display the formatted result
                    st.markdown('<div class="formatted-result">', unsafe_allow_html=True)
                    st.text(result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display sources
                    if sources:
                        st.markdown('<div class="source-box">', unsafe_allow_html=True)
                        st.markdown("#### 📁 Sources Referenced")
                        for source in sources:
                            st.markdown(f"• {source}")
                        st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.markdown(f"**❌ Error:** {str(e)}")
                st.markdown("\n**Please contact your account executive for assistance.**")
                st.markdown("\n📧 **Email:** support@finbotics.ai")
                st.markdown("📞 **Phone:** 1-800-FINBOTICS")
                st.markdown('</div>', unsafe_allow_html=True)

with main_col2:
    # Sidebar with example queries
    st.markdown("### 💡 Example Queries")
    
    examples = [
        "How much did I spend on OpenAI in February?",
        "What's my current runway?",
        "Show me my top 5 vendors by spending",
        "What are my total expenses for last month?",
        "How much did I spend on software?",
        "What are my biggest recurring expenses?",
    ]
    
    for example in examples:
        if st.button(example, key=f"example_{examples.index(example)}"):
            st.session_state.query_input = example
            st.rerun()
    
    # Query history
    if st.session_state.history:
        st.markdown("### 📜 Recent Queries")
        for item in reversed(st.session_state.history[-5:]):
            with st.expander(f"{item['timestamp'].strftime('%H:%M')} - {item['query'][:30]}..."):
                st.text(item['result'])
                if item.get('sources'):
                    st.markdown("**Sources:**")
                    for source in item['sources']:
                        st.markdown(f"• {source}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Powered by Finbotics AI | For assistance, contact your account executive</p>
    </div>
    """,
    unsafe_allow_html=True
)