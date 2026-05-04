import streamlit as st
import plotly.graph_objects as go

def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        /* Global font */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Dark mode styling & glassmorphism */
        .stApp {
            background-color: #0E1117;
            background-image: radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.08), transparent 25%),
                              radial-gradient(circle at 85% 30%, rgba(16, 185, 129, 0.08), transparent 25%);
        }

        /* Metric Cards */
        .metric-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: transform 0.2s ease-in-out;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.08);
        }

        .metric-title {
            color: #A0AEC0;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }

        .metric-value {
            color: #FFFFFF;
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 4px;
        }

        .metric-subtitle {
            color: #718096;
            font-size: 0.85rem;
        }

        /* Feedback styling */
        .feedback-box {
            padding: 16px;
            border-radius: 12px;
            margin-top: 12px;
            background: rgba(255, 255, 255, 0.03);
            border-left: 4px solid #6366F1;
        }
        .feedback-positive { border-left-color: #10B981; }
        .feedback-warning { border-left-color: #F59E0B; }
        .feedback-negative { border-left-color: #EF4444; }
        
        /* Buttons */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s;
        }
        </style>
    """, unsafe_allow_html=True)

def metric_card(title, value, subtitle=""):
    html = f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-subtitle">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def create_donut_chart(value, title, color="#6366F1"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20, 'color': '#FFFFFF'}},
        number={'font': {'color': '#FFFFFF', 'size': 40}, 'suffix': "%"},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color},
            'bgcolor': "rgba(255,255,255,0.1)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 100], 'color': "rgba(0,0,0,0)"}
            ],
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Inter"},
        height=250,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def feedback_box(text, type="info"):
    types = {
        "positive": "feedback-positive",
        "warning": "feedback-warning",
        "negative": "feedback-negative",
        "info": ""
    }
    html = f"""
    <div class="feedback-box {types.get(type, '')}">
        <div style="color: #E2E8F0; font-size: 0.95rem; line-height: 1.5;">{text}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
