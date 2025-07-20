import streamlit as st
import anthropic
from datetime import datetime
import json

# ============================================
# INITIAL SETUP
# ============================================

# Page configuration
st.set_page_config(
    page_title="Find Your Meditation Teaching Niche",
    page_icon="🎯",
    layout="centered"
)

# Custom CSS with Tergar brand colors
st.markdown("""
<style>
    /* Primary button - Tergar orange */
    .stButton > button[kind="primary"] {
        background-color: #E39F24;
        border-color: #E39F24;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #C11F3C;
        border-color: #C11F3C;
    }
    
    /* Progress bar - Tergar green */
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    
    /* Success messages - Tergar green */
    .stSuccess {
        background-color: rgba(76, 175, 80, 0.1);
        border-left-color: #4CAF50;
    }
    
    /* Info messages - Tergar orange */
    .stInfo {
        background-color: rgba(227, 159, 36, 0.1);
        border-left-color: #E39F24;
    }
    
    /* Warning messages - Tergar red */
    .stWarning {
        background-color: rgba(193, 31, 60, 0.1);
        border-left-color: #C11F3C;
    }
    
    /* Headers - Tergar orange */
    h1, h2, h3 {
        color: #E39F24;
    }
    
    /* Radio buttons and checkboxes */
    .stRadio > div[role="radiogroup"] label:hover {
        color: #E39F24;
    }
    
    /* Text input focus */
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #E39F24;
        box-shadow: 0 0 0 0.2rem rgba(227, 159, 36, 0.25);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Claude with correct model
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# Initialize session state (the app's memory)
if 'stage' not in st.session_state:
    st.session_state.stage = 'welcome'
    st.session_state.responses = {}
    st.session_state.conversation = []
    st.session_state.niche_statement = ""
    st.session_state.groups = []

# ============================================
# HEADER SECTION (appears on every page)
# ============================================

# Title
st.title("🎯 Find Your Meditation Teaching Niche")

# Progress bar
stages = ['welcome', 'story', 'groups', 'select_group', 'narrow', 'test', 'offerings', 'complete']
stage_names = ['Welcome', 'Your Story', 'Groups You Know', 'Select Focus', 'Get Specific', 'Test Viability', 'Design Offerings', 'Complete']

if st.session_state.stage != 'welcome':
    current_index = stages.index(st.session_state.stage)
    progress = current_index / (len(stages) - 1)
    st.progress(progress)
    st.caption(f"Step {current_index} of {len(stages)-1}: {stage_names[current_index]}")

# ============================================
# CLAUDE AI HELPER FUNCTION
# ============================================

def ask_claude(prompt, context=""):
    """Talk to Claude and get a response"""
    try:
        # Build conversation history (last 5 messages)
        history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.conversation[-5:]])
        
        # Create the full context for Claude
        full_context = f"""You are helping a meditation teacher find their specific teaching niche. 
        
Previous conversation:
{history}

Current stage: {st.session_state.stage}
User data collected: {json.dumps(st.session_state.responses, indent=2)}

{context}

Respond conversationally and guide them based on the current stage."""

        # Call Claude API with correct model
        message = client.messages.create(
            model="claude-sonnet-4-20250514",  # Correct model name
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"{full_context}\n\nUser input: {prompt}"
                }
            ]
        )
        response = message.content[0].text
        
        # Save to conversation history
        st.session_state.conversation.append({"role": "user", "content": prompt})
        st.session_state.conversation.append({"role": "assistant", "content": response})
        
        return response
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"

# ============================================
# STAGE 1: WELCOME
# ============================================

if st.session_state.stage == 'welcome':
    st.write("""
    Welcome! This tool will help you:
    - 🎯 Find a specific group you're uniquely positioned to serve
    - 💬 Create messages that speak directly to them
    - 📦 Design offerings that meet their needs
    - 💰 Build a sustainable teaching practice
    
    This process takes about 15-20 minutes.
    """)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Let's Begin! →", type="primary", use_container_width=True):
            st.session_state.stage = 'story'
            st.rerun()

# ============================================
# STAGE 2: YOUR STORY
# ============================================

elif st.session_state.stage == 'story':
    st.header("📖 Your Story")
    st.write("Your most powerful teaching often comes from your own transformation.")
    
    challenge = st.text_area(
        "What life challenge led you to meditation?",
        placeholder="Be specific: Not just 'stress' but 'panic attacks before presentations' or 'couldn't sleep after my divorce'",
        height=100
    )
    
    transformation = st.text_area(
        "What transformation did you experience?",
        placeholder="How is your daily life different now? What specific changes occurred?",
        height=100
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.stage = 'welcome'
            st.rerun()
    with col2:
        if st.button("Continue →", type="primary"):
            if challenge and transformation:
                st.session_state.responses['challenge'] = challenge
                st.session_state.responses['transformation'] = transformation
                st.session_state.stage = 'groups'
                st.rerun()
            else:
                st.error("Please fill in both fields")

# ============================================
# STAGE 3: GROUPS YOU KNOW
# ============================================

elif st.session_state.stage == 'groups':
    st.header("👥 Groups You Know Well")
    st.write("""
    List 3-5 groups whose struggles you understand deeply. These can be:
    - Groups you currently belong to
    - Groups you used to be part of (but meditation transformed you)
    - Groups you know intimately through family or experience
    """)
    
    with st.expander("See examples"):
        st.write("""
        - New parents
        - Burned out healthcare workers
        - People with anxiety
        - Recent retirees
        - Perfectionists
        - Grieving individuals
        - Empty nesters
        - Corporate executives
        """)
    
    # Create 5 input fields for groups
    groups = []
    for i in range(5):
        group = st.text_input(
            f"Group {i+1}" + (" (optional)" if i > 2 else ""),
            key=f"group_{i}"
        )
        if group:
            groups.append(group)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.stage = 'story'
            st.rerun()
    with col2:
        if st.button("Continue →", type="primary"):
            if len(groups) >= 3:
                st.session_state.groups = groups
                st.session_state.responses['groups'] = groups
                st.session_state.stage = 'select_group'
                st.rerun()
            else:
                st.error("Please list at least 3 groups")

# ============================================
# STAGE 4: SELECT YOUR GROUP
# ============================================

elif st.session_state.stage == 'select_group':
    st.header("🎯 Choose Your Focus")
    st.write("Select the group you'd like to explore further:")
    
    selected = st.radio(
        "Which group do you feel most called to serve?",
        st.session_state.groups,
        index=None
    )
    
    if selected:
        st.info(f"You selected: **{selected}**")
        
        # Ask Claude for insight about this choice
        with st.spinner("Getting insights..."):
            insight = ask_claude(
                f"The user wants to focus on helping '{selected}'. Ask one brief, conversational follow-up question to understand why they connect with this group. Keep it under 2 sentences."
            )
        st.write(insight)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.stage = 'groups'
            st.rerun()
    with col2:
        if st.button("Continue →", type="primary"):
            if selected:
                st.session_state.responses['selected_group'] = selected
                st.session_state.stage = 'narrow'
                st.rerun()
            else:
                st.error("Please select a group")

# ============================================
# STAGE 5: NARROW YOUR NICHE
# ============================================

elif st.session_state.stage == 'narrow':
    st.header("🔍 Let's Get Specific")
    
    selected_group = st.session_state.responses['selected_group']
    st.write(f"You want to help: **{selected_group}**")
    st.write("Now let's make this more specific.")
    
    specific_struggle = st.text_area(
        "What specific struggle does this group face?",
        placeholder="Not just 'stress' but the specific flavor of their struggle",
        height=80
    )
    
    acute_moment = st.text_area(
        "When is this struggle most acute?",
        placeholder="Specific moments, times, or situations when they most need help",
        height=80
    )
    
    specific_who = st.text_area(
        "Can you be even more specific about WHO in this group?",
        placeholder=f"Add details that narrow '{selected_group}' further (age, stage, situation, etc.)",
        height=80
    )
    
    # Show emerging niche statement if fields are filled
    if specific_struggle and acute_moment:
        who = specific_who if specific_who else selected_group
        niche = f"I help {who} who struggle with {specific_struggle}, especially {acute_moment}"
        
        st.success("**Your emerging niche:**")
        st.write(niche)
        st.session_state.niche_statement = niche
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.stage = 'select_group'
            st.rerun()
    with col2:
        if st.button("Continue →", type="primary"):
            if specific_struggle and acute_moment:
                st.session_state.responses['specific_struggle'] = specific_struggle
                st.session_state.responses['acute_moment'] = acute_moment
                st.session_state.responses['specific_who'] = specific_who
                st.session_state.stage = 'test'
                st.rerun()
            else:
                st.error("Please fill in at least the first two fields")

# ============================================
# STAGE 6: TEST YOUR NICHE
# ============================================

elif st.session_state.stage == 'test':
    st.header("✅ Test Your Niche")
    
    st.success(f"**Your niche:** {st.session_state.niche_statement}")
    
    st.write("Let's make sure this niche is viable:")
    
    # Size check
    size_check = st.radio(
        "Can you think of at least 50 people who fit this description?",
        ["Yes - I can name 50+ people",
         "No - fewer than 50 people", 
         "Too broad - millions would fit"],
        index=None
    )
    
    # Recognition test
    recognition = st.text_area(
        "Write one sentence that would make someone in your niche say 'That's exactly me!'",
        placeholder="Example: 'Do you lie awake at 3am replaying every conversation from work?'",
        height=80
    )
    
    # Get Claude's feedback if both are filled
    if size_check and recognition:
        with st.spinner("Analyzing your niche..."):
            feedback = ask_claude(
                f"Analyze this niche: '{st.session_state.niche_statement}'. Size assessment: {size_check}. Recognition phrase: {recognition}. Give brief, encouraging feedback on whether this niche is well-defined and viable."
            )
        
        st.info("**AI Feedback:**")
        st.write(feedback)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.stage = 'narrow'
            st.rerun()
    with col2:
        if st.button("Continue →", type="primary"):
            if size_check and recognition:
                st.session_state.responses['size_check'] = size_check
                st.session_state.responses['recognition'] = recognition
                
                # Handle different size scenarios
                if "fewer than 50" in size_check:
                    st.warning("Your niche might be too narrow. Consider broadening slightly.")
                elif "millions" in size_check:
                    st.warning("Your niche might be too broad. Consider being more specific.")
                else:
                    st.session_state.stage = 'offerings'
                    st.rerun()
            else:
                st.error("Please complete both questions")

# ============================================
# STAGE 7: CREATE OFFERINGS
# ============================================

elif st.session_state.stage == 'offerings':
    st.header("🎁 Design Your Offerings")
    
    st.write(f"Now let's create offerings for: **{st.session_state.niche_statement}**")
    
    # Collect offering preferences
    availability = st.text_input(
        "When are your people most available?",
        placeholder="e.g., Weekday mornings, Weekend afternoons, Evening after kids' bedtime"
    )
    
    format_pref = st.selectbox(
        "What format would work best for them?",
        ["", "6-week series", "Drop-in classes", "Monthly membership", "Weekend workshop", "1-on-1 sessions"],
        index=0
    )
    
    location = st.text_input(
        "Where would they feel most comfortable?",
        placeholder="e.g., Online via Zoom, Local yoga studio, Community center"
    )
    
    # Generate offerings when all fields are filled
    if availability and format_pref and location:
        if st.button("Generate My Three Offerings", type="primary"):
            with st.spinner("Creating your custom offerings..."):
                offerings_prompt = f"""
                Create 3 specific offerings for someone who helps: {st.session_state.niche_statement}
                
                Their availability: {availability}
                Preferred format: {format_pref}
                Location preference: {location}
                
                Create:
                1. Entry Level - Low commitment, accessible
                2. Funded/Sponsored - Who might pay for this group to get help?
                3. Premium - Higher touch, funds scholarships
                
                Be specific and practical. No pricing - they'll use calculator for that.
                """
                
                offerings = ask_claude(offerings_prompt)
                st.session_state.responses['offerings'] = offerings
                st.session_state.stage = 'complete'
                st.rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.stage = 'test'
            st.rerun()

# ============================================
# STAGE 8: COMPLETE - SHOW RESULTS
# ============================================

elif st.session_state.stage == 'complete':
    st.header("🎉 Your Meditation Teaching Plan")
    
    st.success(f"**Your Niche:** {st.session_state.niche_statement}")
    
    st.write("### Your Three Offerings:")
    st.write(st.session_state.responses.get('offerings', ''))
    
    st.write("### Next Steps:")
    st.write("""
    1. **Choose ONE offering to start with** (recommend starting with entry level)
    2. **Use the Income Calculator** to determine sustainable pricing
    3. **Find 5-10 people** in your niche for a pilot program
    4. **Gather feedback** and refine your approach
    """)
    
    # Download button for results
    results_text = f"""
MEDITATION TEACHING NICHE PLAN
Generated: {datetime.now().strftime('%B %d, %Y')}

YOUR STORY:
Challenge: {st.session_state.responses.get('challenge', '')}
Transformation: {st.session_state.responses.get('transformation', '')}

YOUR NICHE:
{st.session_state.niche_statement}

Recognition Phrase:
{st.session_state.responses.get('recognition', '')}

YOUR OFFERINGS:
{st.session_state.responses.get('offerings', '')}

NEXT STEPS:
1. Choose ONE offering to pilot
2. Use Income Calculator for pricing
3. Find 5-10 beta students
4. Run pilot and gather feedback
5. Refine and officially launch
    """
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📄 Download Your Plan",
            data=results_text,
            file_name=f"niche_plan_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
    
    with col2:
        if st.button("🔄 Start Over", type="secondary", key="main_start_over"):
            # Clear everything and start fresh
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
    
    # Link to calculator
    st.info("**Ready to price your offerings?** Use the Income Calculator to ensure sustainability.")

# ============================================
# SIDEBAR (appears on all pages)
# ============================================

with st.sidebar:
    st.header("📍 Your Progress")
    
    # Show completed information
    if st.session_state.responses.get('challenge'):
        st.write("✅ **Story captured**")
    
    if st.session_state.groups:
        st.write(f"✅ **{len(st.session_state.groups)} groups identified**")
    
    if st.session_state.responses.get('selected_group'):
        st.write(f"✅ **Focus:** {st.session_state.responses['selected_group']}")
    
    if st.session_state.niche_statement:
        st.write("✅ **Niche defined**")
        with st.expander("See your niche"):
            st.write(st.session_state.niche_statement)
    
    # Reset button at bottom
    st.divider()
    if st.button("🔄 Start Over", key="sidebar_start_over"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()