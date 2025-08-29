import streamlit as st
import google-generativeai as genai
import matplotlib.pyplot as plt
import matplotlib
import base64
import pandas as pd
import math
matplotlib.use('Agg')

# --- Configure Gemini API ---
GEMINI_API_KEY = "AIzaSyAhQIow3UGiTibLejjL1kAp1GEoqbkIvCY"
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Gemini API error: {e}")
    st.stop()

model = genai.GenerativeModel('gemini-2.5-flash')

# --- Page Config ---
st.set_page_config(page_title="Mula – Your Money Buddy", layout="wide", page_icon="🐷", initial_sidebar_state="expanded")

# --- Initialize session state ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# --- CSS Styling Function ---
def get_css_styles(is_dark_mode):
    theme_vars = {
        'bg_gradient': 'linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%)' if is_dark_mode else 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%)',
        'text_color': '#e8eaed' if is_dark_mode else '#1e293b',
        'sidebar_bg': 'linear-gradient(180deg, #1e2139 0%, #2a2d47 100%)' if is_dark_mode else 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)',
        'sidebar_border': '#3d4f99' if is_dark_mode else '#e2e8f0',
        'sidebar_text': '#e8eaed' if is_dark_mode else '#475569',
        'input_bg': 'rgba(255, 255, 255, 0.1)' if is_dark_mode else '#ffffff',
        'input_border': 'rgba(255, 255, 255, 0.2)' if is_dark_mode else '#e2e8f0',
        'history_bg': 'rgba(255, 255, 255, 0.05)' if is_dark_mode else 'rgba(102, 126, 234, 0.05)',
        'history_entry': f'linear-gradient(135deg, #2c3a7a 0%, #3d4f99 100%); color: #e8eaed;' if is_dark_mode else 'linear-gradient(135deg, #475569 0%, #64748b 100%); color: #ffffff;',
        'history_hover': f'linear-gradient(135deg, #3d4f99 0%, #4e61b8 100%); color: #ffffff;' if is_dark_mode else 'linear-gradient(135deg, #64748b 0%, #475569 100%); color: #ffffff;',
        'faq_bg': 'rgba(255, 255, 255, 0.1)' if is_dark_mode else '#ffffff',
        'faq_border': 'rgba(255, 255, 255, 0.2)' if is_dark_mode else '#e2e8f0',
        'faq_hover': 'rgba(255, 255, 255, 0.2)' if is_dark_mode else '#f1f5f9'
    }
    
    return f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            html, body, [data-testid="stAppViewContainer"] {{
                background: {theme_vars['bg_gradient']} !important;
                color: {theme_vars['text_color']} !important;
                font-family: 'Inter', 'Segoe UI', sans-serif !important;
            }}

            [data-testid="stSidebar"] {{
                background: {theme_vars['sidebar_bg']} !important;
                border-right: 2px solid {theme_vars['sidebar_border']} !important;
                box-shadow: 4px 0 20px rgba(0, 0, 0, {'0.3' if is_dark_mode else '0.1'}) !important;
            }}

            .sidebar-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: -1rem -1rem 1.5rem -1rem;
                padding: 1.5rem 1rem;
                text-align: center;
                border-radius: 0 0 15px 15px;
                box-shadow: 0 4px 15px rgba(102, 126, 234, {'0.2' if not is_dark_mode else '0.2'});
            }}

            .sidebar-logo {{
                font-size: 2.5rem;
                margin-bottom: 0.5rem;
                animation: bounce 2s ease-in-out infinite;
            }}

            @keyframes bounce {{
                0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
                40% {{ transform: translateY(-10px); }}
                60% {{ transform: translateY(-5px); }}
            }}

            .sidebar-title {{
                font-size: 1.4rem;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 0.5rem;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            }}

            .sidebar-subtitle {{
                font-size: 0.9rem;
                color: rgba(255, 255, 255, {'0.8' if is_dark_mode else '0.9'});
                font-weight: 400;
            }}

            .theme-toggle-container {{
                background: {'rgba(255, 255, 255, 0.1)' if is_dark_mode else 'rgba(102, 126, 234, 0.1)'};
                padding: 1rem;
                border-radius: 12px;
                margin: 1rem 0;
                backdrop-filter: blur(10px);
                border: 1px solid {'rgba(255, 255, 255, 0.2)' if is_dark_mode else 'rgba(102, 126, 234, 0.2)'};
            }}

            .nav-section {{ margin: 1.5rem 0; }}
            .nav-header {{
                font-size: 1rem;
                font-weight: 600;
                color: {'#a8b2d1' if is_dark_mode else '#64748b'};
                margin-bottom: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}

            .history-section {{
                background: {theme_vars['history_bg']};
                border-radius: 12px;
                padding: 1rem;
                margin-top: 1.5rem;
                {'backdrop-filter: blur(10px);' if is_dark_mode else 'border: 1px solid rgba(102, 126, 234, 0.1);'}
            }}

            .history-entry {{
                background: {theme_vars['history_entry']};
                padding: 0.6rem 0.8rem;
                border-radius: 8px;
                font-size: 0.85rem;
                margin-bottom: 0.6rem;
                color: {theme_vars['sidebar_text']};
                border: 1px solid {'rgba(255, 255, 255, 0.1)' if is_dark_mode else '#e2e8f0'};
                transition: all 0.2s ease;
                cursor: pointer;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}

            .history-entry:hover {{
                transform: translateX(5px);
                background: {theme_vars['history_hover']};
                box-shadow: 0 4px 12px rgba(0, 0, 0, {'0.3' if is_dark_mode else '0.1'});
            }}

            .user-msg {{
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                padding: 15px 18px;
                border-radius: 18px 18px 5px 18px;
                margin-bottom: 8px;
                margin-left: 25%;
                color: #ffffff;
                box-shadow: 0 4px 12px rgba(79, 70, 229, {'0.3' if is_dark_mode else '0.2'});
                font-weight: 500;
            }}

            .mula-msg {{
                background: linear-gradient(135deg, #059669 0%, #047857 100%);
                padding: 15px 18px;
                border-radius: 18px 18px 18px 5px;
                margin-bottom: 8px;
                margin-right: 25%;
                color: #ffffff;
                box-shadow: 0 4px 12px rgba(5, 150, 105, {'0.3' if is_dark_mode else '0.2'});
                font-weight: 500;
            }}

            .stTextInput > div > div > input {{
                background: {theme_vars['input_bg']} !important;
                border: 2px solid {theme_vars['input_border']} !important;
                border-radius: 12px !important;
                color: #000000 !important;
                font-size: 16px !important;
                padding: 12px 16px !important;
                transition: all 0.3s ease !important;
            }}

            .stTextInput > div > div > input:focus {{
                border-color: #667eea !important;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, {'0.2' if is_dark_mode else '0.1'}) !important;
            }}

            .stButton button {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 10px !important;
                padding: 0.6rem 1.5rem !important;
                font-weight: 600 !important;
                transition: all 0.3s ease !important;
            }}

            .stButton button:hover {{
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 25px rgba(102, 126, 234, {'0.4' if is_dark_mode else '0.3'}) !important;
            }}

            .stNumberInput input {{
                background: {theme_vars['input_bg']} !important;
                color: {theme_vars['text_color']} !important;
                border: 2px solid {theme_vars['input_border']} !important;
                border-radius: 10px !important;
            }}

            .stSlider > div {{ color: {theme_vars['text_color']} !important; }}
            
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] span,
            [data-testid="stSidebar"] div,
            [data-testid="stSidebar"] p {{ color: {theme_vars['sidebar_text']} !important; }}

            .stRadio > div {{
                background: {'rgba(255, 255, 255, 0.05)' if is_dark_mode else 'rgba(102, 126, 234, 0.05)'};
                border-radius: 10px;
                padding: 0.5rem;
            }}

            .main-content {{
                background: {'rgba(255, 255, 255, 0.02)' if is_dark_mode else 'rgba(255, 255, 255, 0.8)'};
                border-radius: 15px;
                padding: 2rem;
                margin: 1rem;
                backdrop-filter: blur(10px);
                border: 1px solid {'rgba(255, 255, 255, 0.1)' if is_dark_mode else 'rgba(226, 232, 240, 0.5)'};
            }}
        </style>
        """

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode()
    return b64_string

# Apply current theme CSS
st.markdown(get_css_styles(st.session_state.dark_mode), unsafe_allow_html=True)

# --- Enhanced Sidebar ---
with st.sidebar:
    # Sidebar Header with Logo
    image_base64 = get_base64_image('mula_avatar1.png')
    
    st.markdown(f"""
        <div class="sidebar-header">
            <div class="sidebar-logo">
                <img src="data:image/png;base64,{image_base64}" width="200" />
            </div>
            <div class="sidebar-subtitle">Your Smart Money Buddy</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Theme Toggle
    st.markdown('<div class="theme-toggle-container">', unsafe_allow_html=True)
    st.markdown('<div class="toggle-label">🎨 Appearance</div>', unsafe_allow_html=True)
    
    theme_toggle = st.checkbox(
        "🌙 Dark Mode" if not st.session_state.dark_mode else "🌞 Light Mode",
        value=st.session_state.dark_mode
    )
    
    if theme_toggle != st.session_state.dark_mode:
        st.session_state.dark_mode = theme_toggle
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    st.markdown('<div class="nav-section"><div class="nav-header">🛠️ Tools</div>', unsafe_allow_html=True)
    nav = st.radio("", ["💬 Chat with Mula", "📊 Budget Builder", "🧮 Loan Calculator"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # History Section
    if 'question_history' not in st.session_state:
        st.session_state.question_history = []
    
    st.markdown('<div class="history-section"><div class="nav-header">🕘 Recent Chats</div>', unsafe_allow_html=True)
    
    if st.session_state.question_history:
        for q in reversed(st.session_state.question_history[-8:]):
            display_q = q[:40] + "..." if len(q) > 40 else q
            st.markdown(f'<div class="history-entry" title="{q}">{display_q}</div>', unsafe_allow_html=True)
    else:
        no_chats_color = '#94a3b8' if st.session_state.dark_mode else '#64748b'
        st.markdown(f'<div style="color: {no_chats_color}; font-size: 0.85rem; text-align: center; padding: 1rem;">No recent chats</div>', unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    footer_color = '#94a3b8' if st.session_state.dark_mode else '#64748b'
    st.markdown(f'<div style="margin-top: 2rem; padding: 1rem; text-align: center; font-size: 0.75rem; color: {footer_color};">💡 Built with ❤️ for smart money habits</div>', unsafe_allow_html=True)

# --- Session Initialization ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[
        {"role": "user", "parts": "Act as Mula, a fun and friendly financial coach for teenagers. Keep responses engaging and use emojis appropriately."},
        {"role": "model", "parts": "Hey hey! I'm Mula, your money buddy! 🐷💸 Ready to build smart money habits together? Ask me anything about saving, budgeting, or making your money work smarter!"}
    ])
    st.session_state.chat_history.append(("Mula", "Hey hey! I'm Mula, your money buddy! 🐷💸 Ready to build smart money habits together? Ask me anything about saving, budgeting, or making your money work smarter!"))

# --- Main Content ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

if nav == "💬 Chat with Mula":
    st.title("💬 Chat with Mula")
    st.markdown("*Your personal financial advisor, always ready to help!*")
    
    # Chat History
    for role, msg in st.session_state.chat_history:
        bubble_class = "user-msg" if role == "You" else "mula-msg"
        st.markdown(f'<div class="{bubble_class}">{msg}</div>', unsafe_allow_html=True)

    # FAQ Section
    st.markdown("---\n#### 💡 Quick Questions to Get Started:")
    
    faq_questions = [
        "How can I start saving money?", "What's a simple budget I can use?",
        "Should I get a debit or credit card?", "How does compound interest work?",
        "What are some good money habits?", "How do I track my expenses?"
    ]
    
    faq_cols = st.columns(2)
    for i, q in enumerate(faq_questions):
        if faq_cols[i % 2].button(q, key=f"faq_{i}", use_container_width=True):
            st.session_state.question_history.append(q)
            st.session_state.chat_history.append(("You", q))
            
            with st.spinner("Mula is thinking... 💭"):
                try:
                    response = st.session_state.chat_session.send_message(q)
                    st.session_state.chat_history.append(("Mula", response.text))
                except Exception as e:
                    st.session_state.chat_history.append(("Mula", f"Oops! Something went wrong: {e}"))
                st.rerun()

    # Chat Input
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input("Ask Mula anything about money...", placeholder="e.g., How much should I save each month?")
    with col2:
        send_clicked = st.button("Send 🚀", use_container_width=True)

    if send_clicked and user_input.strip():
        st.session_state.question_history.append(user_input)
        st.session_state.chat_history.append(("You", user_input))
        
        with st.spinner("Mula is crafting a helpful response... 🧠"):
            try:
                response = st.session_state.chat_session.send_message(user_input)
                st.session_state.chat_history.append(("Mula", response.text))
            except Exception as e:
                st.session_state.chat_history.append(("Mula", f"Oops! Something went wrong: {e}"))
        st.rerun()

elif nav == "📊 Budget Builder":
    st.title("📊 Build Your Perfect Budget")
    st.markdown("*Create a balanced budget that works for your lifestyle!*")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 💰 Your Income")
        income = st.number_input("Monthly Income ($)", min_value=0.0, step=50.0, value=1000.0)
        
        st.markdown("### 🎯 Budget Categories\n*Adjust the sliders to allocate your income:*")
        
        categories = {
            "🏠 Needs (Housing, Food, Transport)": "needs",
            "🎮 Wants (Entertainment, Hobbies)": "wants", 
            "💎 Savings & Investments": "savings",
            "📚 Other (Education, Emergency)": "other"
        }
        
        budget_data = {key: st.slider(display_name, 0, 100, 25, key=key) for display_name, key in categories.items()}
    
    with col2:
        st.markdown("### 📈 Budget Breakdown")
        
        total_percent = sum(budget_data.values())
        
        if total_percent > 100:
            st.error("🚨 Oops! Your total is over 100%. Try adjusting the sliders!")
        elif total_percent < 100:
            st.warning(f"💡 You have {100 - total_percent}% unallocated. Consider increasing your savings!")
        else:
            st.success("🎯 Perfect! Your budget is perfectly balanced!")
            
            if income > 0:
                # Create pie chart
                labels, values, colors = [], [], ['#4f46e5', '#059669', '#dc2626', '#7c3aed']
                
                for i, (display_name, key) in enumerate(categories.items()):
                    if budget_data[key] > 0:
                        amount = income * budget_data[key] / 100
                        labels.append(f"{display_name.split(' ')[0]} ({budget_data[key]}%)")
                        values.append(amount)
                
                if values:
                    fig, ax = plt.subplots(figsize=(8, 6))
                    wedges, texts, autotexts = ax.pie(
                        values, labels=labels, 
                        autopct=lambda pct: f'${income * pct / 100:.0f}' if pct > 0 else '',
                        startangle=90, colors=colors[:len(values)]
                    )
                    
                    ax.set_title('Your Monthly Budget Breakdown', fontsize=14, fontweight='bold', pad=20)
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                    
                    st.pyplot(fig, use_container_width=True)
                    
                    # Budget summary
                    st.markdown("### 💡 Budget Summary")
                    for display_name, key in categories.items():
                        if budget_data[key] > 0:
                            amount = income * budget_data[key] / 100
                            st.markdown(f"**{display_name}**: ${amount:.2f}/month")

elif nav == "🧮 Loan Calculator":
    st.title("🧮 Smart Loan & Hire Purchase Calculator")
    st.markdown("*Make informed decisions about loans and payment plans!*")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 💳 Loan Details")
        loan_amount = st.number_input("Loan Amount ($)", min_value=0.0, step=100.0, value=5000.0)
        interest_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
        months = st.number_input("Repayment Period (months)", min_value=1, step=1, value=24)
        
        st.markdown("### ⚙️ Calculation Options")
        show_comparison = st.checkbox("📊 Show term comparison", value=True)
    
    with col2:
        st.markdown("### 📊 Payment Breakdown")
        
        if loan_amount > 0 and months > 0:
            # Calculate payments
            if interest_rate > 0:
                monthly_rate = interest_rate / 100 / 12
                try:
                    monthly_payment = loan_amount * monthly_rate / (1 - (1 + monthly_rate) ** -months)
                except (ZeroDivisionError, OverflowError):
                    monthly_payment = loan_amount / months
            else:
                monthly_payment = loan_amount / months
            
            total_payment = monthly_payment * months
            total_interest = total_payment - loan_amount
            
            # Display results
            st.success(f"📅 **Monthly Payment**: ${monthly_payment:.2f}")
            st.info(f"💰 **Total Amount**: ${total_payment:.2f}")
            st.warning(f"💸 **Total Interest**: ${total_interest:.2f}")
            
            if total_payment > 0:
                interest_percentage = (total_interest / loan_amount) * 100
                st.markdown(f"📈 **Interest as % of loan**: {interest_percentage:.1f}%")
            
            st.markdown("### 🎯 Affordability Tips")
            st.markdown("💡 **Tip**: Ensure this payment is less than 30% of your monthly income!")
            st.markdown(f"🛡️ **Safety buffer**: Consider if you can comfortably pay ${monthly_payment * 0.8:.2f}/month")

    # Term Comparison Chart
    if loan_amount > 0 and show_comparison:
        st.markdown("---\n### 📊 Compare Different Terms")
        
        terms = [6, 12, 18, 24, 36, 48, 60]
        monthly_payments, total_payments, total_interests = [], [], []
        
        for term in terms:
            if interest_rate > 0:
                monthly_rate = interest_rate / 100 / 12
                try:
                    mp = loan_amount * monthly_rate / (1 - (1 + monthly_rate) ** -term)
                except (ZeroDivisionError, OverflowError):
                    mp = loan_amount / term
            else:
                mp = loan_amount / term
            
            tp, ti = mp * term, (mp * term) - loan_amount
            monthly_payments.append(mp)
            total_payments.append(tp)
            total_interests.append(ti)
        
        # Create comparison chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Monthly payment chart
        bars1 = ax1.bar([str(t) for t in terms], monthly_payments, color='#4f46e5', alpha=0.8)
        ax1.set_xlabel('Loan Term (months)')
        ax1.set_ylabel('Monthly Payment ($)')
        ax1.set_title('Monthly Payment by Term')
        ax1.grid(axis='y', alpha=0.3)
        
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(monthly_payments)*0.01,
                    f'${height:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Total interest chart
        bars2 = ax2.bar([str(t) for t in terms], total_interests, color='#dc2626', alpha=0.8)
        ax2.set_xlabel('Loan Term (months)')
        ax2.set_ylabel('Total Interest ($)')
        ax2.set_title('Total Interest by Term')
        ax2.grid(axis='y', alpha=0.3)
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + max(total_interests)*0.01,
                    f'${height:.0f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        
        # Summary table
        st.markdown("### 📋 Detailed Comparison Table")
        comparison_df = pd.DataFrame({
            'Term (months)': terms,
            'Monthly Payment': [f'${mp:.2f}' for mp in monthly_payments],
            'Total Payment': [f'${tp:.2f}' for tp in total_payments],
            'Total Interest': [f'${ti:.2f}' for ti in total_interests],
            'Interest Rate': [f'{(ti/loan_amount)*100:.1f}%' for ti in total_interests]
        })
        
        st.dataframe(comparison_df, use_container_width=True)
        
        min_interest_idx = total_interests.index(min(total_interests))
        recommended_term = terms[min_interest_idx]
        st.success(f"💡 **Mula's Recommendation**: The {recommended_term}-month term offers the lowest total interest of ${total_interests[min_interest_idx]:.2f}!")
        
        # Detailed Explanation Section
        st.markdown("---")
        st.markdown("### 🎓 Understanding Your Loan Comparison")
        
        # Create explanation columns
        exp_col1, exp_col2 = st.columns([1, 1])
        
        with exp_col1:
            st.markdown("""
            #### 📊 **Chart Analysis**
            
            **Monthly Payment Chart (Left)**
            - **Higher bars** = Higher monthly payments
            - **Shorter loan terms** = Higher monthly payments but less total interest
            - **Pattern**: As loan term increases, monthly payment decreases
            
            **Total Interest Chart (Right)**
            - **Higher bars** = More money paid in interest over the loan's lifetime
            - **Longer loan terms** = More total interest paid
            - **Key insight**: Longer loans cost more overall, even with lower monthly payments
            """)
        
        with exp_col2:
            st.markdown("""
            #### 💡 **Smart Money Tips**
            
            **The Trade-off**
            - **Short loans**: Higher monthly payments, but you save money overall
            - **Long loans**: Lower monthly payments, but you pay much more in interest
            
            **What This Means for You**
            - Choose the **shortest term** you can comfortably afford
            - Consider your monthly budget vs. long-term savings
            - Even 6 months difference can save you hundreds of dollars!
            """)
        
        # Specific insights based on the data
        st.markdown("#### 🔍 **Your Loan Insights**")
        
        # Calculate insights
        shortest_term_payment = monthly_payments[0]  # 6 months
        longest_term_payment = monthly_payments[-1]  # 60 months
        shortest_term_interest = total_interests[0]
        longest_term_interest = total_interests[-1]
        
        savings_amount = longest_term_interest - shortest_term_interest
        payment_difference = shortest_term_payment - longest_term_payment
        
        # Create custom metric cards with better visibility
        insight_cols = st.columns(3)
        
        metric_style = """
        <div style="
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            color: white;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
            margin: 0.5rem 0;
        ">
            <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{value}</div>
            <div style="font-size: 1rem; opacity: 0.9;">{label}</div>
            <div style="font-size: 0.8rem; opacity: 0.7; margin-top: 0.3rem;">{help_text}</div>
        </div>
        """
        
        with insight_cols[0]:
            st.markdown(
                metric_style.format(
                    value=f"${savings_amount:.2f}",
                    label="💰 Interest Savings",
                    help_text=f"Save by choosing {terms[0]} vs {terms[-1]} months"
                ),
                unsafe_allow_html=True
            )
        
        with insight_cols[1]:
            st.markdown(
                metric_style.format(
                    value=f"${payment_difference:.2f}",
                    label="📈 Payment Difference",
                    help_text="Monthly payment difference (short vs long)"
                ),
                unsafe_allow_html=True
            )
        
        with insight_cols[2]:
            if savings_amount > 0:
                savings_percentage = (savings_amount / loan_amount) * 100
                st.markdown(
                    metric_style.format(
                        value=f"{savings_percentage:.1f}%",
                        label="📊 Savings Rate",
                        help_text="Interest savings as % of loan amount"
                    ),
                    unsafe_allow_html=True
                )
        
        # Final recommendations
        st.markdown("#### 🎯 **Mula's Smart Choice Guide**")
        
        # Find the best balance (lowest interest while keeping monthly payment reasonable)
        reasonable_payment_threshold = loan_amount * 0.25  # 25% of loan amount per month
        best_balance_options = []
        
        for i, (term, monthly_pay, total_int) in enumerate(zip(terms, monthly_payments, total_interests)):
            if monthly_pay <= reasonable_payment_threshold:
                best_balance_options.append((term, monthly_pay, total_int, i))
        
        if best_balance_options:
            # Find the option with lowest total interest among reasonable payments
            best_option = min(best_balance_options, key=lambda x: x[2])
            best_term, best_monthly, best_interest, best_idx = best_option
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #059669 0%, #047857 100%);
                padding: 1.5rem;
                border-radius: 12px;
                color: white;
                margin: 1rem 0;
                box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
            ">
                <div style="font-size: 1.2rem; font-weight: bold; margin-bottom: 1rem;">
                    🎯 <strong>Balanced Choice: {best_term} months</strong>
                </div>
                <div style="margin-bottom: 0.5rem;">• <strong>Monthly Payment:</strong> ${best_monthly:.2f}</div>
                <div style="margin-bottom: 0.5rem;">• <strong>Total Interest:</strong> ${best_interest:.2f}</div>
                <div style="margin-bottom: 0.5rem;">• <strong>Why this works:</strong> Good balance between affordability and total cost!</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
                padding: 1.5rem;
                border-radius: 12px;
                color: white;
                margin: 1rem 0;
                box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
            ">
                <div style="font-size: 1.1rem; font-weight: bold;">
                    💡 Consider increasing your down payment or choosing a smaller loan amount for better monthly payments.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Educational content
        with st.expander("🤓 Learn More: How Loan Interest Works"):
            st.markdown("""
            #### How Compound Interest Affects Your Loan
            
            **Simple Interest vs. Compound Interest**
            - Most loans use **compound interest**
            - Interest is calculated on the remaining balance
            - Early payments go mostly to interest, later payments to principal
            
            **Why Shorter Terms Save Money**
            1. **Less time** for interest to accumulate
            2. **Higher principal payments** each month
            3. **Faster payoff** means less total interest
            
            **The Math Behind It**
            - Monthly Payment = Loan Amount × [Interest Rate × (1 + Interest Rate)^Months] / [(1 + Interest Rate)^Months - 1]
            - This formula ensures you pay off the loan completely in the specified time
            
            **Pro Tips**
            - 💰 Make extra payments toward principal when possible
            - 📅 Even one extra payment per year can save significant interest
            - 🎯 Round up your payments (e.g., pay $255 instead of $247.83)
            """)
        
        # Interactive what-if scenario
        with st.expander("🧮 What-If Calculator"):
            st.markdown("#### See how extra payments affect your loan:")
            
            extra_payment = st.number_input(
                "Extra monthly payment ($)", 
                min_value=0.0, 
                step=10.0, 
                value=0.0,
                help="Additional amount you could pay each month"
            )
            
            if extra_payment > 0:
                # Calculate impact of extra payments (simplified calculation)
                new_monthly_payment = monthly_payment + extra_payment
                # Estimate new payoff time (simplified)
                if interest_rate > 0:
                    monthly_rate = interest_rate / 100 / 12
                    if new_monthly_payment > loan_amount * monthly_rate:  # Avoid division by zero
                        new_months = -(math.log(1 - (loan_amount * monthly_rate / new_monthly_payment))) / math.log(1 + monthly_rate)
                        new_months = max(1, int(new_months) + 1)  # Round up and ensure at least 1 month
                        
                        new_total_payment = new_monthly_payment * new_months
                        new_total_interest = new_total_payment - loan_amount
                        
                        time_saved = months - new_months
                        interest_saved = total_interest - new_total_interest
                        
                        if time_saved > 0 and interest_saved > 0:
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, #059669 0%, #047857 100%);
                                padding: 1.5rem;
                                border-radius: 12px;
                                color: white;
                                margin: 1rem 0;
                                box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
                            ">
                                <div style="font-size: 1.2rem; font-weight: bold; margin-bottom: 1rem;">
                                    🎉 <strong>Impact of ${extra_payment:.2f} extra monthly payment:</strong>
                                </div>
                                <div style="margin-bottom: 0.5rem;">⏱️ <strong>Time saved:</strong> {time_saved} months</div>
                                <div style="margin-bottom: 0.5rem;">💰 <strong>Interest saved:</strong> ${interest_saved:.2f}</div>
                                <div style="margin-bottom: 0.5rem;">🏁 <strong>New payoff time:</strong> {new_months} months</div>
                                <div>📊 <strong>New total interest:</strong> ${new_total_interest:.2f}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="
                                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                                padding: 1.5rem;
                                border-radius: 12px;
                                color: white;
                                margin: 1rem 0;
                                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                            ">
                                <div style="font-size: 1.1rem; font-weight: bold;">
                                    With this extra payment, you'd pay off the loan very quickly! 🚀
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    # For 0% interest loans
                    new_months = loan_amount / new_monthly_payment
                    new_months = int(new_months) + (1 if new_months % 1 > 0 else 0)
                    time_saved = months - new_months
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #059669 0%, #047857 100%);
                        padding: 1.5rem;
                        border-radius: 12px;
                        color: white;
                        margin: 1rem 0;
                        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
                    ">
                        <div style="font-size: 1.2rem; font-weight: bold;">
                            🎉 <strong>Time saved:</strong> {time_saved} months (No interest savings since rate is 0%)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                    padding: 1.5rem;
                    border-radius: 12px;
                    color: white;
                    margin: 1rem 0;
                    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
                ">
                    <div style="font-size: 1.1rem; font-weight: bold;">
                        💡 Try entering an extra payment amount to see the impact!
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 10px; text-align: center; color: white; margin: 1rem 0;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
            <strong>🎓 Remember: The best loan is the one that fits your budget and goals!</strong><br>
            <em>Don't just look at monthly payments - consider the total cost over time.</em>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
footer_color = '#94a3b8' if st.session_state.dark_mode else '#64748b'
st.markdown(f"""
---
<div style="text-align: center; padding: 2rem; color: {footer_color}; font-size: 0.9rem;">
    <strong>🐷 Mula - Your Smart Money Buddy</strong><br>
    <em>Building better financial habits, one conversation at a time!</em><br>
    <small style="opacity: 0.7;">Remember: This is educational content. Always consult with a financial advisor for major decisions.</small>
</div>
""", unsafe_allow_html=True)
