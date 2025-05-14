import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
from collections import Counter
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import re
from transformers import pipeline
import openai

# Page configuration
st.set_page_config(
    page_title="EmailFlow Pro | Enterprise Email Management",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main app styling */
    .main {
        padding: 0;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1.5rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 30px 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 30px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1rem;
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    
    .status-high {
        background-color: #ff6b6b;
        color: white;
    }
    
    .status-medium {
        background-color: #feca57;
        color: #333;
    }
    
    .status-low {
        background-color: #5f27cd;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'emails' not in st.session_state:
    st.session_state.emails = []
if 'categories' not in st.session_state:
    st.session_state.categories = {}
if 'replies' not in st.session_state:
    st.session_state.replies = {}
if 'processed_emails' not in st.session_state:
    st.session_state.processed_emails = set()

# Email categories
CATEGORIES = [
    "Customer Support",
    "Technical Issue",
    "Billing Inquiry",
    "Feature Request",
    "General Inquiry",
    "Complaint",
    "Partnership Request",
    "Bug Report",
    "Account Management",
    "Sales Inquiry"
]

# Load AI models (mock function - in production, use actual models)
@st.cache_resource
def load_models():
    # In production, load actual models
    # For demo, we'll use mock functions
    return {
        'classifier': None,  # Use actual model
        'reply_generator': None  # Use actual model
    }

# Mock email fetching function
def fetch_emails_mock():
    """Mock function to simulate email fetching"""
    subjects = [
        "Issue with login functionality",
        "Billing question about subscription",
        "Feature request: Dark mode",
        "Cannot access dashboard",
        "Partnership opportunity",
        "Bug report: Data export failing",
        "Account upgrade inquiry",
        "Technical support needed",
        "Complaint about service",
        "General inquiry about pricing"
    ]
    
    mock_emails = []
    for i in range(5):
        email_data = {
            'id': f"mock_{int(time.time())}_{i}",
            'subject': np.random.choice(subjects),
            'sender': f"user{np.random.randint(1000, 9999)}@example.com",
            'body': f"This is a mock email body for testing purposes. {np.random.choice(['Urgent!', 'Please help.', 'Thank you.', 'ASAP'])}",
            'timestamp': datetime.now() - timedelta(hours=np.random.randint(0, 48)),
            'priority': np.random.choice(['High', 'Medium', 'Low'], p=[0.2, 0.5, 0.3])
        }
        mock_emails.append(email_data)
    
    return mock_emails

# Mock categorization function
def categorize_email_mock(email_data):
    """Mock function to categorize emails"""
    subject_keywords = {
        'login': 'Technical Issue',
        'billing': 'Billing Inquiry',
        'feature': 'Feature Request',
        'bug': 'Bug Report',
        'partnership': 'Partnership Request',
        'support': 'Customer Support',
        'complaint': 'Complaint',
        'account': 'Account Management',
        'sales': 'Sales Inquiry'
    }
    
    subject_lower = email_data['subject'].lower()
    for keyword, category in subject_keywords.items():
        if keyword in subject_lower:
            return category
    
    return np.random.choice(CATEGORIES)

# Mock reply generation function
def generate_reply_mock(email_data, category):
    """Mock function to generate email replies"""
    templates = {
        'Technical Issue': "Thank you for reporting this technical issue. Our engineering team has been notified and will investigate immediately. We'll update you within 24 hours.",
        'Billing Inquiry': "Thank you for your billing inquiry. Our finance team will review your account and respond within 2 business days.",
        'Feature Request': "Thank you for your feature suggestion! We've added it to our product roadmap for consideration.",
        'Customer Support': "Thank you for contacting support. A specialist will review your request and respond within 4 hours.",
        'Bug Report': "Thank you for the bug report. We've logged this issue and our team is working on a fix.",
        'Partnership Request': "Thank you for your partnership inquiry. Our business development team will review and respond within 3 business days.",
        'Complaint': "We sincerely apologize for your experience. A senior manager will personally review your complaint and respond within 24 hours.",
        'Account Management': "Thank you for your account inquiry. An account manager will assist you shortly.",
        'Sales Inquiry': "Thank you for your interest! A sales representative will contact you within 24 hours to discuss your needs.",
        'General Inquiry': "Thank you for contacting us. We'll review your inquiry and respond within 48 hours."
    }
    
    return f"""
Subject: Re: {email_data['subject']}

Dear Customer,

{templates.get(category, templates['General Inquiry'])}

Best regards,
EmailFlow Pro Support Team
    """

# Dashboard header
st.markdown("""
<div class="app-header">
    <h1 style="margin: 0; font-size: 2.5rem;">📧 EmailFlow Pro</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Enterprise Email Management & Analytics Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    # Email settings (mock)
    st.text_input("Email Server", value="mail.company.com", disabled=True)
    st.text_input("Email Account", value="support@company.com", disabled=True)
    
    st.markdown("### 📊 Monitor Settings")
    refresh_interval = st.slider("Refresh Interval (seconds)", 5, 60, 30)
    auto_refresh = st.checkbox("Auto Refresh", value=True)
    
    st.markdown("### 🤖 AI Settings")
    auto_categorize = st.checkbox("Auto-Categorize Emails", value=True)
    auto_draft = st.checkbox("Auto-Generate Replies", value=True)
    
    if st.button("🔄 Manual Refresh"):
        st.rerun()

# Main dashboard
col1, col2, col3, col4 = st.columns(4)

# Fetch new emails
new_emails = fetch_emails_mock()
for email_data in new_emails:
    if email_data['id'] not in st.session_state.processed_emails:
        st.session_state.emails.append(email_data)
        st.session_state.processed_emails.add(email_data['id'])
        
        # Auto-categorize
        if auto_categorize:
            category = categorize_email_mock(email_data)
            st.session_state.categories[email_data['id']] = category
            
            # Auto-generate reply
            if auto_draft:
                reply = generate_reply_mock(email_data, category)
                st.session_state.replies[email_data['id']] = reply

# Calculate metrics
total_emails = len(st.session_state.emails)
high_priority = len([e for e in st.session_state.emails if e.get('priority') == 'High'])
processed = len(st.session_state.categories)
pending = total_emails - processed

# Display metrics
with col1:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #2a5298; margin: 0;">Total Emails</h3>
        <h1 style="margin: 0.5rem 0; color: #1e3c72;">{}</h1>
        <p style="color: #666; margin: 0;">Last 48 hours</p>
    </div>
    """.format(total_emails), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #ff6b6b; margin: 0;">High Priority</h3>
        <h1 style="margin: 0.5rem 0; color: #ff6b6b;">{}</h1>
        <p style="color: #666; margin: 0;">Requires attention</p>
    </div>
    """.format(high_priority), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #5f27cd; margin: 0;">Processed</h3>
        <h1 style="margin: 0.5rem 0; color: #5f27cd;">{}</h1>
        <p style="color: #666; margin: 0;">Categorized & replied</p>
    </div>
    """.format(processed), unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #feca57; margin: 0;">Pending</h3>
        <h1 style="margin: 0.5rem 0; color: #feca57;">{}</h1>
        <p style="color: #666; margin: 0;">Awaiting processing</p>
    </div>
    """.format(pending), unsafe_allow_html=True)

# Charts section
st.markdown("<br>", unsafe_allow_html=True)
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 📈 Issue Categories Distribution")
    
    if st.session_state.categories:
        category_counts = Counter(st.session_state.categories.values())
        df_categories = pd.DataFrame(
            list(category_counts.items()),
            columns=['Category', 'Count']
        )
        
        fig = px.pie(
            df_categories, 
            values='Count', 
            names='Category',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No categorized emails yet. Waiting for data...")
    st.markdown('</div>', unsafe_allow_html=True)

with col_chart2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 📊 Email Volume Trend")
    
    if st.session_state.emails:
        # Create time series data
        df_emails = pd.DataFrame(st.session_state.emails)
        df_emails['hour'] = pd.to_datetime(df_emails['timestamp']).dt.floor('H')
        hourly_counts = df_emails.groupby('hour').size().reset_index(name='count')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_counts['hour'],
            y=hourly_counts['count'],
            mode='lines+markers',
            line=dict(color='#2a5298', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(42, 82, 152, 0.2)'
        ))
        fig.update_layout(
            title='',
            xaxis_title='Time',
            yaxis_title='Email Count',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No email data yet. Waiting for incoming emails...")
    st.markdown('</div>', unsafe_allow_html=True)

# Email list section
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📬 Recent Emails")

if st.session_state.emails:
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["All Emails", "High Priority", "Processed"])
    
    with tab1:
        for email_data in sorted(st.session_state.emails, key=lambda x: x['timestamp'], reverse=True)[:10]:
            with st.expander(f"📧 {email_data['subject']} - {email_data['sender']}", expanded=False):
                col_info, col_action = st.columns([3, 1])
                
                with col_info:
                    st.write(f"**From:** {email_data['sender']}")
                    st.write(f"**Time:** {email_data['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Priority:** {email_data['priority']}")
                    
                    if email_data['id'] in st.session_state.categories:
                        category = st.session_state.categories[email_data['id']]
                        st.write(f"**Category:** {category}")
                    
                    st.write(f"**Content:** {email_data['body'][:200]}...")
                
                with col_action:
                    if email_data['id'] in st.session_state.replies:
                        if st.button("View Reply", key=f"view_{email_data['id']}"):
                            st.text_area("Generated Reply", st.session_state.replies[email_data['id']], height=200)
                    else:
                        if st.button("Generate Reply", key=f"gen_{email_data['id']}"):
                            category = st.session_state.categories.get(email_data['id'], 'General Inquiry')
                            reply = generate_reply_mock(email_data, category)
                            st.session_state.replies[email_data['id']] = reply
                            st.rerun()
    
    with tab2:
        high_priority_emails = [e for e in st.session_state.emails if e['priority'] == 'High']
        if high_priority_emails:
            for email_data in sorted(high_priority_emails, key=lambda x: x['timestamp'], reverse=True):
                st.error(f"🚨 {email_data['subject']} - {email_data['sender']}")
        else:
            st.info("No high priority emails")
    
    with tab3:
        processed_emails = [e for e in st.session_state.emails if e['id'] in st.session_state.categories]
        if processed_emails:
            df_processed = pd.DataFrame([
                {
                    'Subject': e['subject'],
                    'Sender': e['sender'],
                    'Category': st.session_state.categories[e['id']],
                    'Time': e['timestamp'].strftime('%Y-%m-%d %H:%M'),
                    'Priority': e['priority']
                }
                for e in processed_emails
            ])
            st.dataframe(df_processed, use_container_width=True)
        else:
            st.info("No processed emails yet")
else:
    st.info("No emails in the system yet. The dashboard will update as emails arrive.")

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()