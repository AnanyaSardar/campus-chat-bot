import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY not found in environment variables. Please set it in a .env file.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(
    page_title="CampusConnect - Your AI Campus Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #7f8c8d;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    .quick-info-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .quick-info-card h3 {
        margin-top: 0;
        margin-bottom: 1rem;
        font-size: 1.3rem;
    }
    
    .menu-item {
        background: rgba(255,255,255,0.2);
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        backdrop-filter: blur(10px);
    }
    
    .events-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .event-item {
        background: rgba(255,255,255,0.2);
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        backdrop-filter: blur(10px);
    }
    
    .contact-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .contact-item {
        background: rgba(255,255,255,0.2);
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
    }
    
    .stChatMessage {
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .sidebar .stSelectbox {
        background: white;
        border-radius: 10px;
        padding: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .time-display {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# System prompt
SYSTEM_PROMPT = """You are a smart virtual assistant for a college website called "CampusConnect." Your role is to help students by answering questions about:

1. *Upcoming and ongoing events* – e.g., cultural fests, workshops, seminars, club meetings.
2. *Mess menu* – daily meals like breakfast, lunch, dinner with veg/non-veg options.
3. *Campus locations* – where departments, buildings, or blocks are located (e.g., "Where is the admin block?")
4. *General student queries* – about clubs, facilities, common timings, or notices.
5. *Support contact information* – guide students to the correct cell or authority for their issue.

You must always reply in a clear, friendly, and helpful tone like you're guiding a new student. If you're unsure of an answer, say: "I'm not sure about that at the moment, but you can check with the student council or admin."

Here is today's context:
- *Mess Menu (July 15)*:  
  - Breakfast: Poha, Tea  
  - Lunch: Rajma Chawal, Roti, Salad  
  - Dinner: Paneer Butter Masala, Jeera Rice

- *Upcoming Events*:  
  - AI Workshop on July 16 at 2 PM, Seminar Hall  
  - Cultural Fest on July 20 at 5 PM, Main Ground  
  - Coding Marathon on July 22 at 10 AM, Lab Block

- *Popular Locations*:  
  - Admin Block: Near Main Gate  
  - Hostel C: Behind Library  
  - Library: 2nd floor, Academic Building  
  - Seminar Hall: Ground floor of Academic Block A

- *Student Support & Emergency Contact Numbers*:  
  If a student needs help, direct them to the appropriate cell:

  1. *Anti-Ragging Cell* – 📞 99094778929  
  2. *Women's Safety Cell* – 📞 9821234567  
  3. *Medical Emergency* – 📞 9112233445  
  4. *Hostel Issues* – 📞 9123456789  
  5. *Academic Issues* – 📞 9876543210  
  6. *On-Campus Psychologist* – 📞 9001122334

Be polite, helpful, and respectful. Offer relevant information only, and do not make assumptions beyond the data provided unless it's common college knowledge."""

def get_chat_session():
    if "chat" not in st.session_state:
        model = genai.GenerativeModel('gemini-2.0-flash')
        st.session_state.chat = model.start_chat(history=[])
        st.session_state.chat.send_message(SYSTEM_PROMPT)
    return st.session_state.chat

# Main header
st.markdown("""
<div class="main-header">
    <h1>🎓 CampusConnect</h1>
    <p>Your AI-Powered Campus Assistant</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with quick info
with st.sidebar:
    st.markdown("### 🕒 Current Time")
    current_time = datetime.now().strftime("%I:%M %p")
    current_date = datetime.now().strftime("%B %d, %Y")
    st.markdown(f"""
    <div class="time-display">
        <strong>{current_time}</strong><br>
        {current_date}
    </div>
    """, unsafe_allow_html=True)
    
    # Today's Menu
    st.markdown("""
    <div class="quick-info-card">
        <h3>🍽️ Today's Menu</h3>
        <div class="menu-item">
            <strong>Breakfast:</strong> Poha, Tea
        </div>
        <div class="menu-item">
            <strong>Lunch:</strong> Rajma Chawal, Roti, Salad
        </div>
        <div class="menu-item">
            <strong>Dinner:</strong> Paneer Butter Masala, Jeera Rice
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Upcoming Events
    st.markdown("""
    <div class="events-card">
        <h3>📅 Upcoming Events</h3>
        <div class="event-item">
            <strong>AI Workshop</strong><br>
            July 16, 2 PM - Seminar Hall
        </div>
        <div class="event-item">
            <strong>Cultural Fest</strong><br>
            July 20, 5 PM - Main Ground
        </div>
        <div class="event-item">
            <strong>Coding Marathon</strong><br>
            July 22, 10 AM - Lab Block
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Emergency Contacts
    st.markdown("""
    <div class="contact-card">
        <h3>🚨 Emergency Contacts</h3>
        <div class="contact-item">
            <span style="margin-right: 10px;">👥</span>
            <div>
                <strong>Anti-Ragging Cell</strong><br>
                📞 99094778929
            </div>
        </div>
        <div class="contact-item">
            <span style="margin-right: 10px;">👩</span>
            <div>
                <strong>Women's Safety</strong><br>
                📞 9821234567
            </div>
        </div>
        <div class="contact-item">
            <span style="margin-right: 10px;">🏥</span>
            <div>
                <strong>Medical Emergency</strong><br>
                📞 9112233445
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main content area
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Feature cards
    st.markdown("### 🤖 What I Can Help You With")
    
    features = [
        {
            "icon": "📅",
            "title": "Events Information",
            "desc": "Get details about upcoming cultural fests, workshops, seminars, and club meetings"
        },
        {
            "icon": "🍽️",
            "title": "Mess Menu",
            "desc": "Check today's breakfast, lunch, and dinner options with veg/non-veg details"
        },
        {
            "icon": "🗺️",
            "title": "Campus Navigation",
            "desc": "Find locations of departments, buildings, and get directions around campus"
        },
        {
            "icon": "❓",
            "title": "General Queries",
            "desc": "Ask about clubs, facilities, timings, notices, and student services"
        },
        {
            "icon": "📞",
            "title": "Support Contacts",
            "desc": "Get emergency numbers and contact information for various departments"
        }
    ]
    
    for feature in features:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{feature["icon"]}</div>
            <div class="feature-title">{feature["title"]}</div>
            <div class="feature-desc">{feature["desc"]}</div>
        </div>
        """, unsafe_allow_html=True)

# Chat Interface
st.markdown("### 💬 Chat with Campus Assistant")
# st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Initialize chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about campus life... 💬"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 Thinking...")
        
        try:
            chat = get_chat_session()
            response = chat.send_message(prompt)
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        
        except Exception as e:
            error_msg = f"❌ Sorry, I encountered an error: {str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 1rem;">
    <p>🎓 CampusConnect AI Assistant | Helping students navigate campus life</p>
    <p>Need technical support? Contact the IT Help Desk</p>
</div>
""", unsafe_allow_html=True)