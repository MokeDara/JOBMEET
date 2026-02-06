"""
Main Streamlit application for Resume Matcher with LLM Integration
Professional UI with responsive design
"""

import streamlit as st
from text_processor import extract_resume_text, clean_text
from matcher_engine import calculate_fit_score, get_cv_adjustments, calculate_fit_score_with_llm, get_cv_adjustments_with_llm
from visualizer import display_fit_score, display_adjustments
from cover_letter import generate_cover_letter_prompt, generate_cover_letter_with_llm, analyze_fit_with_llm
from config import config

st.set_page_config(
    page_title="JOBMEET - AI Resume Matcher",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/yourusername/jobmeet",
        "About": "JOBMEET v2.0 - AI-Powered Resume Matcher"
    }
)

# Custom CSS for professional styling and responsiveness
st.markdown("""
    <style>
    /* Global Styling */
    :root {
        --primary-color: #0066cc;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
    }
    
    /* Typography */
    h1 {
        color: #0f172a;
        font-size: clamp(1.8rem, 5vw, 2.5rem);
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 1rem;
    }
    
    h2 {
        color: #1e293b;
        font-size: clamp(1.3rem, 4vw, 1.8rem);
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    h3 {
        color: #334155;
        font-size: clamp(1.1rem, 3vw, 1.4rem);
        font-weight: 500;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                     'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue';
        font-size: clamp(0.9rem, 2vw, 1rem);
        color: #475569;
        line-height: 1.6;
    }
    
    /* Main container responsiveness */
    .main {
        padding: clamp(1rem, 4vw, 2rem);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        font-size: clamp(0.875rem, 2vw, 1rem);
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.15);
    }
    
    /* Input fields */
    .stTextArea textarea {
        font-size: clamp(0.875rem, 2vw, 0.95rem);
        border-radius: 0.5rem;
        border: 2px solid #e2e8f0;
        transition: border-color 0.2s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #0066cc;
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: clamp(1.5rem, 4vw, 2.2rem);
        font-weight: 700;
        color: #0066cc;
    }
    
    /* Info/Warning/Error boxes */
    .stAlert {
        border-radius: 0.5rem;
        font-size: clamp(0.875rem, 2vw, 0.95rem);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: clamp(0.5rem, 2vw, 1rem);
    }
    
    /* Dividers */
    hr {
        margin: clamp(1rem, 4vw, 2rem) 0;
        border-color: #e2e8f0;
    }
    
    /* Responsive columns */
    @media (max-width: 768px) {
        .main {
            padding: 0.75rem;
        }
        
        h1 {
            font-size: 1.5rem;
        }
        
        h2 {
            font-size: 1.2rem;
        }
        
        [data-testid="column"] {
            width: 100% !important;
            margin-bottom: 1rem;
        }
    }
    
    /* File uploader styling */
    .stFileUploader {
        border-radius: 0.5rem;
    }
    
    /* Progress indicators */
    .stProgress > div > div {
        background-image: linear-gradient(90deg, #0066cc, #0052a3);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for resume
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "resume_filename" not in st.session_state:
    st.session_state.resume_filename = None
if "use_llm" not in st.session_state:
    st.session_state.use_llm = config.is_llm_enabled()

# ============================================================================
# SIDEBAR - Professional Resume Upload & Configuration
# ============================================================================
with st.sidebar:
    st.markdown("## 📄 Resume Upload")
    st.caption("Upload your resume once per session and reuse it for multiple job analyses")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF resume",
        type="pdf",
        help="Supported format: PDF files up to 200MB",
        key="resume_uploader"
    )
    
    if uploaded_file is not None:
        st.session_state.resume_filename = uploaded_file.name
        st.session_state.resume_text = extract_resume_text(uploaded_file)
        st.success(f"✅ Resume loaded\n**{uploaded_file.name}**")
    else:
        st.info("📤 No resume uploaded yet. Click to browse your files.")
    
    st.divider()
    
    # Analysis Mode Selection
    st.markdown("## 🎯 Analysis Mode")
    
    if config.is_llm_enabled():
        st.caption("Choose your preferred analysis approach")
        
        analysis_mode = st.radio(
            "Mode:",
            options=["🤖 LLM Mode (AI-Powered)", "⚡ Normal Mode (Fast Matching)"],
            help="**LLM Mode**: Uses Google Gemini AI for intelligent analysis\n\n**Normal Mode**: Uses TF-IDF algorithm - no API calls needed",
            index=0 if st.session_state.use_llm else 1,
            label_visibility="collapsed"
        )
        st.session_state.use_llm = (analysis_mode == "🤖 LLM Mode (AI-Powered)")
        
        # Status indicator
        if st.session_state.use_llm:
            st.success(f"✓ LLM Mode Active\n**Model:** {config.app.llm.model}")
        else:
            st.info("✓ Normal Mode Active (TF-IDF Matching)")
    else:
        st.warning("⚠️ LLM not configured")
        st.caption("Set `GOOGLE_GEMINI_API_KEY` in `.env` to enable AI mode")
        st.info("✓ Running in Normal Mode")
        st.session_state.use_llm = False
    
    st.divider()
    
    # Footer info
    st.caption("**JOBMEET v2.0**\nAI-Powered Resume Matcher")
    st.caption("[GitHub](https://github.com) • [Issues](https://github.com)")

# ============================================================================
# MAIN CONTENT - Header & Status
# ============================================================================
col1, col2 = st.columns([3, 1], gap="small")
with col1:
    st.markdown("# 🎯 Resume Matcher")
    st.markdown("Analyze your resume against job descriptions with AI-powered intelligence")

with col2:
    if st.session_state.resume_text:
        st.metric("Resume Status", "✅ Loaded", "Ready to analyze")
    else:
        st.metric("Resume Status", "⏳ Pending", "Upload to start")

st.divider()
# ============================================================================
# MAIN CONTENT - Resume Analysis Section
# ============================================================================

if st.session_state.resume_text is None:
    # Empty state
    st.warning("📤 Upload a resume to get started")
    st.info("👉 Click the upload button in the sidebar to begin your analysis")
    
else:  # Resume is loaded
    st.success(f"✅ Resume loaded: **{st.session_state.resume_filename}**")
    
    # Job Description Input Section
    st.markdown("### 📋 Job Description")
    st.caption("Paste the complete job description for analysis")
    
    job_description = st.text_area(
        "Job Description",
        height=min(300, max(150, len(st.session_state.resume_text) // 50)),
        placeholder="Paste the job description here...\n\nExample:\nWe are looking for a Senior Software Engineer with:\n- 5+ years of Python experience\n- Experience with AWS\n- Team leadership skills\n...",
        help="Include all job requirements, responsibilities, and qualifications",
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Analysis Actions
    st.markdown("### 🚀 Analysis Actions")
    
    col1, col2, col3 = st.columns([1, 1, 1], gap="small")
    
    analysis_type = None
    
    with col1:
        if st.button("🤖 AI Analysis", use_container_width=True, type="primary", key="btn_llm"):
            if job_description.strip():
                analysis_type = "llm"
            else:
                st.error("Please paste a job description first")
    
    with col2:
        if st.button("⚡ Quick Match", use_container_width=True, key="btn_module"):
            if job_description.strip():
                analysis_type = "module"
            else:
                st.error("Please paste a job description first")
    
    with col3:
        if st.button("🔄 Clear All", use_container_width=True, key="btn_clear"):
            st.rerun()
    
    st.divider()
    
    # ====================================================================
    # ANALYSIS RESULTS SECTION
    # ====================================================================
    
    if analysis_type and job_description.strip():
        with st.spinner("🔍 Analyzing your resume..."):
            # Clean texts
            clean_resume = clean_text(st.session_state.resume_text)
            clean_job_desc = clean_text(job_description)
            
            # Choose analysis type
            if analysis_type == "llm":
                llm_result = calculate_fit_score_with_llm(clean_resume, clean_job_desc)
                if llm_result.get("success"):
                    fit_score = llm_result.get("fit_score", 0)
                    # Use LLM-powered adjustments if available
                    adjustments_result = get_cv_adjustments_with_llm(clean_resume, clean_job_desc)
                    if adjustments_result.get("success"):
                        adjustments = {
                            "missing_keywords": adjustments_result.get("missing_keywords", []),
                            "skills_to_bolster": adjustments_result.get("skills_to_bolster", [])
                        }
                    else:
                        # Fallback to basic mapping
                        adjustments = {
                            "missing_keywords": llm_result.get("missing_keywords", []),
                            "skills_to_bolster": [{"skill": skill, "job_mentions": 0, "resume_mentions": 0} for skill in llm_result.get("missing_skills", [])]
                        }
                    llm_insights = llm_result
                    using_llm = True
                else:
                    st.error(f"❌ Analysis failed: {llm_result.get('error', 'Unknown error')}")
                    fit_score = None
                    adjustments = None
                    llm_insights = None
                    using_llm = False
            else:  # module analysis
                fit_score = calculate_fit_score(clean_resume, clean_job_desc)
                adjustments = get_cv_adjustments(clean_resume, clean_job_desc)
                llm_insights = None
                using_llm = False
            
            # Display results if analysis succeeded
            if fit_score is not None:
                st.success("✅ Analysis complete!")
                st.divider()
                
                # Results Header
                st.markdown("## 📊 Analysis Results")
                
                # Mode indicator
                if using_llm:
                    st.info("**🤖 AI-Powered Analysis** — Using Google Gemini for intelligent matching")
                else:
                    st.info("**⚡ TF-IDF Analysis** — Fast algorithmic matching")
                
                # Key Metrics Row
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4, gap="small")
                
                with metric_col1:
                    st.metric("Match Score", f"{int(fit_score)}%", delta="out of 100")
                
                with metric_col2:
                    st.metric("Missing Keywords", len(adjustments["missing_keywords"]))
                
                with metric_col3:
                    st.metric("Skills to Emphasize", len(adjustments["skills_to_bolster"]))
                
                with metric_col4:
                    match_quality = "Excellent" if fit_score >= 75 else "Good" if fit_score >= 50 else "Fair" if fit_score >= 25 else "Low"
                    st.metric("Match Quality", match_quality)
                
                st.divider()
                
                # Detailed Analysis
                col_left, col_right = st.columns([1, 1], gap="large")
                
                with col_left:
                    st.markdown("### 📈 Fit Score")
                    display_fit_score(fit_score)
                
                with col_right:
                    st.markdown("### 💡 Quick Insights")
                    if llm_insights and llm_insights.get("key_strengths"):
                        st.markdown("**Your Strengths:**")
                        for strength in llm_insights.get("key_strengths", [])[:3]:
                            st.write(f"✓ {strength}")
                
                st.divider()
                
                # AI Reasoning (if available)
                if llm_insights and llm_insights.get("reasoning"):
                    st.markdown("### 🧠 AI Analysis & Recommendations")
                    
                    with st.expander("📋 Detailed Analysis Report", expanded=True):
                        st.markdown(f"**Analysis:**\n{llm_insights.get('reasoning', '')}")
                        
                        if llm_insights.get("recommendations"):
                            st.markdown("**Action Items:**")
                            for i, rec in enumerate(llm_insights.get("recommendations", [])[:5], 1):
                                st.write(f"{i}. {rec}")
                    
                    st.divider()
                
                # Adjustments Section
                st.markdown("### ✏️ CV Adjustments & Improvements")
                display_adjustments(adjustments)
                
                st.divider()
                
                # Cover Letter Section
                st.markdown("### 📝 Cover Letter Generation")
                st.caption("Generate a tailored cover letter based on your analysis")
                
                col_letter1, col_letter2 = st.columns([1, 1], gap="small")
                
                with col_letter1:
                    if st.button("🤖 AI-Generated Letter", use_container_width=True, key="btn_ai_letter"):
                        with st.spinner("✨ Crafting your cover letter..."):
                            llm_result = generate_cover_letter_with_llm(clean_resume, clean_job_desc)
                            if llm_result.get("success"):
                                st.success("✅ Cover letter generated!")
                                st.text_area(
                                    "Your Cover Letter",
                                    value=llm_result.get("cover_letter", ""),
                                    height=300,
                                    disabled=True,
                                    label_visibility="collapsed"
                                )
                                
                                if llm_result.get("improvement_tips"):
                                    st.markdown("**Customization Tips:**")
                                    for tip in llm_result.get("improvement_tips", [])[:3]:
                                        st.write(f"💡 {tip}")
                            else:
                                st.error(f"Failed to generate: {llm_result.get('error', 'Error occurred')}")
                
                with col_letter2:
                    if st.button("📋 Template Prompt", use_container_width=True, key="btn_template"):
                        prompt = generate_cover_letter_prompt(adjustments, fit_score, job_description)
                        
                        with st.expander("Use this prompt in ChatGPT or Claude", expanded=True):
                            st.text_area(
                                "Copy this prompt",
                                value=prompt,
                                height=300,
                                disabled=True,
                                label_visibility="collapsed"
                            )
                            st.caption("💡 You can paste this into ChatGPT, Claude, or any LLM to generate a cover letter")
    
    elif job_description.strip() and not analysis_type:
        st.info("👆 Click **AI Analysis** or **Quick Match** to analyze your resume")
    else:
        st.info("📋 Paste a job description above and click an analysis button to get started")

# Footer
st.markdown("---")
footer_text = "JOBMEET v2.0 | AI-Powered Resume Matcher"
if config.is_llm_enabled():
    footer_text += f" | LLM: {config.app.llm.model}"
else:
    footer_text += " | Powered by TF-IDF & Cosine Similarity"
st.caption(footer_text)
