import streamlit as st
import anthropic
from datetime import datetime
import json

# ============================================
# INITIAL SETUP
# ============================================

# Page configuration
st.set_page_config(
    page_title="Meditation Teacher Business Tools",
    page_icon="🎯",
    layout="centered"
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'stage' not in st.session_state:
    st.session_state.stage = 'welcome'
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'niche_statement' not in st.session_state:
    st.session_state.niche_statement = ""
if 'groups' not in st.session_state:
    st.session_state.groups = []

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
    
    /* Text input focus */
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #E39F24;
        box-shadow: 0 0 0 0.2rem rgba(227, 159, 36, 0.25);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HOME PAGE
# ============================================

if st.session_state.page == 'home':
    st.title("🙏 Meditation Teacher Business Tools")
    st.subheader("Build a sustainable practice that serves your community")
    
    st.write("""
    Welcome to the Tergar Meditation Teacher Business Toolkit! These tools will help you 
    create a meditation teaching practice that is both spiritually fulfilling and financially sustainable.
    
    Remember: **Sustainable pricing = More teaching = More benefit to the world**
    """)
    
    # If they've completed niche finder, show their niche
    if st.session_state.niche_statement:
        st.success(f"✅ Your niche: {st.session_state.niche_statement}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Find Your Niche")
        st.write("""
        Discover the specific group you're uniquely positioned to serve. 
        This AI-powered tool will help you:
        - Identify your ideal students
        - Create messages that resonate
        - Design targeted offerings
        
        *Takes about 15-20 minutes*
        """)
        if st.button("Start Niche Finder", type="primary", use_container_width=True, key="niche_btn"):
            st.session_state.page = 'niche'
            st.session_state.stage = 'welcome'
            st.rerun()
    
    with col2:
        st.markdown("### 💰 Income Calculator")
        st.write("""
        See how different pricing and volume combinations 
        create sustainable income. Calculate:
        - Your true costs (including time)
        - Break-even pricing
        - Multiple income scenarios
        
        *Takes about 10 minutes*
        """)
        if st.button("Open Calculator", type="primary", use_container_width=True, key="calc_btn"):
            st.session_state.page = 'calculator'
            st.rerun()
    
    # Suggested flow
    st.divider()
    st.markdown("### 🚀 Suggested Path")
    if not st.session_state.niche_statement:
        st.write("1️⃣ **Start with the Niche Finder** to identify who you'll serve")
        st.write("2️⃣ Then use the **Income Calculator** to price your offerings sustainably")
    else:
        st.write("✅ Niche defined! Now use the **Income Calculator** to price your offerings sustainably")

# ============================================
# NICHE FINDER
# ============================================

elif st.session_state.page == 'niche':
    # Add home button
    if st.button("🏠 Back to Home", key="home_from_niche"):
        st.session_state.page = 'home'
        st.rerun()
    
    # Initialize Claude
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    
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

    # Helper function to talk to Claude
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

            # Call Claude API
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
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

    # STAGE: Welcome
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

    # STAGE: Your Story
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

    # STAGE: Groups You Know
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

    # STAGE: Select Your Group
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

    # STAGE: Narrow Your Niche
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

    # STAGE: Test Your Niche
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

    # STAGE: Create Offerings
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

    # STAGE: Complete - Show Results
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
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                label="📄 Download Your Plan",
                data=results_text,
                file_name=f"niche_plan_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
        
        with col2:
            if st.button("💰 Go to Calculator", type="primary"):
                st.session_state.page = 'calculator'
                st.rerun()
        
        with col3:
            if st.button("🔄 Start Over", type="secondary", key="main_start_over"):
                # Clear niche-related state
                st.session_state.stage = 'welcome'
                st.session_state.responses = {}
                st.session_state.conversation = []
                st.session_state.niche_statement = ""
                st.session_state.groups = []
                st.rerun()

# ============================================
# INCOME CALCULATOR
# ============================================

elif st.session_state.page == 'calculator':
    # Add home button
    if st.button("🏠 Back to Home", key="home_from_calc"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.title("💰 Meditation Teaching Income Calculator")
    st.write("See how different combinations create sustainable income")
    
    # If they have a niche, show it
    if st.session_state.niche_statement:
        st.info(f"📍 Calculating for: {st.session_state.niche_statement}")
    
    # Currency selector with data
    currency_data = {
        "USD ($)": {"symbol": "$", "min_income": 15000, "side_income": 30000, "full_income": 60000},
        "EUR (€)": {"symbol": "€", "min_income": 13000, "side_income": 25000, "full_income": 50000},
        "GBP (£)": {"symbol": "£", "min_income": 11000, "side_income": 22000, "full_income": 45000},
        "CNY (¥)": {"symbol": "¥", "min_income": 100000, "side_income": 200000, "full_income": 400000},
        "BRL (R$)": {"symbol": "R$", "min_income": 18000, "side_income": 36000, "full_income": 72000},
        "MXN ($)": {"symbol": "$", "min_income": 75000, "side_income": 150000, "full_income": 300000},
        "RUB (₽)": {"symbol": "₽", "min_income": 450000, "side_income": 900000, "full_income": 1800000},
        "ZAR (R)": {"symbol": "R", "min_income": 120000, "side_income": 240000, "full_income": 480000}
    }
    
    currency = st.selectbox(
        "Select your currency:",
        list(currency_data.keys())
    )
    
    currency_info = currency_data[currency]
    symbol = currency_info["symbol"]
    
    # Create tabs for organization
    tab1, tab2, tab3 = st.tabs(["📚 Teaching Plan", "💸 Costs", "🎯 Goals & Results"])
    
    with tab1:
        st.header("Your Teaching Plan")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Core Teaching")
            price_per_student = st.slider(f"Price per student (6-week series) {symbol}", 0, 500, 100)
            students_per_series = st.slider("Students per series", 3, 50, 10)
            series_per_year = st.slider("Series per year", 1, 20, 4)
            scholarships = st.slider("Full scholarships per year", 0, 50, 0)
        
        with col2:
            st.subheader("Additional Income")
            monthly_members = st.slider("Monthly subscription members", 0, 100, 0)
            monthly_price = st.slider(f"Monthly subscription price {symbol}", 0, 100, 30)
            corporate_workshops = st.slider("Corporate workshops/year", 0, 52, 0)
            corporate_price = st.slider(f"Price per workshop {symbol}", 500, 10000, 2000, step=500)
    
    with tab2:
        st.header("Your Costs")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Monthly Cash Costs")
            venue_cost = st.number_input(f"Venue/Zoom {symbol}", 0, 1000, 50)
            insurance_cost = st.number_input(f"Insurance {symbol}", 0, 500, 40)
            marketing_cost = st.number_input(f"Marketing/Website {symbol}", 0, 500, 30)
        
        with col2:
            st.subheader("Time Investment")
            practice_hours = st.slider("Personal practice (hrs/week)", 0, 20, 7)
            education_hours = st.slider("Continuing education (hrs/week)", 0, 10, 2)
            time_value = st.slider(f"Your time value ({symbol}/hour)", 10, 100, 30)
    
    with tab3:
        st.header("Income Goals & Results")
        
        # Goals
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Your Income Goals")
            min_income_goal = st.number_input(
                f"Minimum income needed {symbol}", 
                value=currency_info["min_income"]
            )
            side_income_goal = st.number_input(
                f"Solid side business {symbol}", 
                value=currency_info["side_income"]
            )
            full_income_goal = st.number_input(
                f"Full-time income {symbol}", 
                value=currency_info["full_income"]
            )
        
        # Calculations
        # Income
        series_income = price_per_student * students_per_series * series_per_year
        subscription_income = monthly_members * monthly_price * 12
        corporate_income = corporate_workshops * corporate_price
        scholarship_cost = scholarships * price_per_student
        total_income = series_income + subscription_income + corporate_income - scholarship_cost
        
        # Costs
        monthly_cash_costs = venue_cost + insurance_cost + marketing_cost
        annual_cash_costs = monthly_cash_costs * 12
        
        # Teaching hours calculation
        series_hours = series_per_year * 6 * 1.5  # 6 weeks, 1.5 hours each
        monthly_hours = 52 if monthly_members > 0 else 0  # Weekly if active
        corporate_hours = corporate_workshops * 2
        total_teaching_hours = series_hours + monthly_hours + corporate_hours
        teaching_hours_per_week = total_teaching_hours / 52
        
        # Prep hours with diminishing returns
        base_prep = 5
        series_prep_ratio = max(0.5, 2 - (series_per_year - 1) * 0.2)
        prep_hours_per_week = base_prep + (teaching_hours_per_week * series_prep_ratio)
        
        # Total time costs
        total_hours_per_week = teaching_hours_per_week + prep_hours_per_week + practice_hours + education_hours
        annual_time_costs = total_hours_per_week * 52 * time_value
        
        # Net calculations
        total_costs = annual_cash_costs + annual_time_costs
        net_income = total_income - total_costs
        monthly_net = net_income / 12
        effective_hourly = net_income / (total_hours_per_week * 52) if total_hours_per_week > 0 else 0
        
        # Display results
        with col2:
            st.subheader("Your Results")
            
            # Income summary
            st.success(f"**Total Income:** {symbol}{total_income:,.0f}")
            with st.expander("Income breakdown"):
                st.write(f"From series: {symbol}{series_income:,.0f}")
                st.write(f"From subscriptions: {symbol}{subscription_income:,.0f}")
                st.write(f"From corporate: {symbol}{corporate_income:,.0f}")
                st.write(f"Less scholarships: -{symbol}{scholarship_cost:,.0f}")
            
            # Cost summary
            st.error(f"**Total Costs:** {symbol}{total_costs:,.0f}")
            with st.expander("Cost breakdown"):
                st.write(f"Cash costs: {symbol}{annual_cash_costs:,.0f}")
                st.write(f"Time costs: {symbol}{annual_time_costs:,.0f}")
            
            # Net income
            if net_income > 0:
                st.success(f"**Net Income:** {symbol}{net_income:,.0f}/year")
                st.write(f"Monthly: {symbol}{monthly_net:,.0f}")
                st.write(f"Hourly rate: {symbol}{effective_hourly:.0f}")
            else:
                st.error(f"**Net Loss:** {symbol}{abs(net_income):,.0f}/year")
                st.write("Adjust pricing or reduce costs to break even")
            
            # Progress toward goals
            st.subheader("Progress Toward Goals")
            min_progress = min(100, int((net_income / min_income_goal) * 100)) if min_income_goal > 0 else 0
            side_progress = min(100, int((net_income / side_income_goal) * 100)) if side_income_goal > 0 else 0
            full_progress = min(100, int((net_income / full_income_goal) * 100)) if full_income_goal > 0 else 0
            
            st.progress(min_progress / 100)
            st.caption(f"Minimum income: {min_progress}%")
            
            st.progress(side_progress / 100)
            st.caption(f"Side business: {side_progress}%")
            
            st.progress(full_progress / 100)
            st.caption(f"Full-time: {full_progress}%")
        
        # Insights
        st.divider()
        st.subheader("💡 Quick Insights")
        
        # Students served
        total_students = (students_per_series * series_per_year) + monthly_members + scholarships
        st.write(f"**Students served:** {int(total_students)} people annually")
        
        # Time commitment
        st.write(f"**Total time commitment:** {total_hours_per_week:.0f} hours/week")
        st.write(f"- Teaching: {teaching_hours_per_week:.0f} hrs")
        st.write(f"- Prep/admin: {prep_hours_per_week:.0f} hrs")
        st.write(f"- Practice & education: {practice_hours + education_hours} hrs")
        
        # Recommendations
        if net_income < min_income_goal:
            st.warning("**Suggestions to reach minimum income:**")
            if corporate_workshops == 0:
                st.write("• Add just one corporate workshop per month")
            if monthly_members == 0:
                st.write("• Start a monthly membership program")
            if price_per_student < 150:
                st.write("• Consider raising prices - even small increases help")
            if students_per_series < 15:
                st.write("• Work on filling your classes more")

# ============================================
# SIDEBAR (appears on all pages)
# ============================================

with st.sidebar:
    st.header("📍 Your Progress")
    
    # Show current page
    if st.session_state.page == 'home':
        st.write("📌 **Home**")
    elif st.session_state.page == 'niche':
        st.write("🎯 **Niche Finder**")
        if st.session_state.stage != 'welcome':
            current_stage = stages.index(st.session_state.stage) + 1
            st.write(f"Stage {current_stage} of {len(stages)}")
    elif st.session_state.page == 'calculator':
        st.write("💰 **Income Calculator**")
    
    # Show completed information
    if st.session_state.niche_statement:
        st.success("✅ **Niche defined!**")
        with st.expander("Your niche"):
            st.write(st.session_state.niche_statement)
    
    # Navigation
    st.divider()
    st.write("**Quick Navigation:**")
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = 'home'
        st.rerun()
    if st.button("🎯 Niche Finder", use_container_width=True):
        st.session_state.page = 'niche'
        st.rerun()
    if st.button("💰 Calculator", use_container_width=True):
        st.session_state.page = 'calculator'
        st.rerun()
    
    # Reset button at bottom
    st.divider()
    if st.button("🔄 Start Fresh", key="sidebar_start_over"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()