"""
Main Streamlit application for Resume Matcher with LLM Integration
"""

import streamlit as st
from text_processor import extract_resume_text, clean_text
from matcher_engine import calculate_fit_score, get_cv_adjustments, calculate_fit_score_with_llm, get_cv_adjustments_with_llm
from visualizer import display_fit_score, display_adjustments
from cover_letter import generate_cover_letter_prompt, generate_cover_letter_with_llm, analyze_fit_with_llm
from config import config

st.set_page_config(
    page_title="JOBMEET - Resume Matcher",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for resume
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "resume_filename" not in st.session_state:
    st.session_state.resume_filename = None
if "use_llm" not in st.session_state:
    st.session_state.use_llm = config.is_llm_enabled()

# Sidebar: Resume Upload
st.sidebar.title("📄 Resume Upload")
st.sidebar.write("Upload your resume once per session")

uploaded_file = st.sidebar.file_uploader(
    "Choose a PDF resume",
    type="pdf",
    help="Supported format: PDF"
)

if uploaded_file is not None:
    st.session_state.resume_filename = uploaded_file.name
    st.session_state.resume_text = extract_resume_text(uploaded_file)
    st.sidebar.success(f"✓ Resume loaded: {uploaded_file.name}")
else:
    st.sidebar.info("No resume uploaded yet")

# Sidebar: Analysis Mode Selection
st.sidebar.markdown("---")
st.sidebar.title("🎯 Analysis Mode")

if config.is_llm_enabled():
    # Create a more prominent toggle
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        st.sidebar.write("**Choose Analysis Method**")
        st.sidebar.caption("LLM Mode: AI-powered intelligent analysis")
        st.sidebar.caption("Normal Mode: Fast TF-IDF matching")
    
    # Toggle button using radio for better UX
    analysis_mode = st.sidebar.radio(
        "Mode:",
        options=["🤖 LLM Mode", "⚡ Normal Mode"],
        help="LLM Mode: Uses OpenAI/Claude for intelligent analysis. Normal Mode: Uses TF-IDF algorithm.",
        index=0 if st.session_state.use_llm else 1
    )
    st.session_state.use_llm = (analysis_mode == "🤖 LLM Mode")
    
    # Show status
    if st.session_state.use_llm:
        st.sidebar.info(f"✓ Running in LLM Mode\nModel: {config.app.llm.model}")
    else:
        st.sidebar.info("✓ Running in Normal Mode (TF-IDF)")
else:
    st.sidebar.warning("⚠️ LLM not configured")
    st.sidebar.caption("Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env to enable LLM mode")
    st.sidebar.info("✓ Running in Normal Mode (TF-IDF)")
    st.session_state.use_llm = False

# Main Panel
st.title("🎯 Resume Matcher & Optimization Dashboard")
st.write("Analyze your resume against job descriptions and get actionable adjustments")

# Check if resume is loaded
if st.session_state.resume_text is None:
    st.warning("⚠️ Please upload a resume in the sidebar to get started")
else:
    st.success(f"✓ Resume ready: {st.session_state.resume_filename}")
    
    # Job Description Input
    st.subheader("Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=200,
        placeholder="Paste the job description text here...",
        help="The system will analyze how well your resume matches this job"
    )
    
    # Analysis Buttons - Two Options
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    analysis_type = None
    
    with col1:
        if st.button("🤖 LLM Analysis", use_container_width=True, type="primary"):
            analysis_type = "llm"
    
    with col2:
        if st.button("⚡ Module Analysis", use_container_width=True):
            analysis_type = "module"
    
    # Execute Analysis
    if analysis_type and job_description.strip():
        with st.spinner("Analyzing your resume against the job description..."):
            # Clean texts
            clean_resume = clean_text(st.session_state.resume_text)
            clean_job_desc = clean_text(job_description)
            
            # Choose analysis type
            if analysis_type == "llm":
                llm_result = calculate_fit_score_with_llm(clean_resume, clean_job_desc)
                if llm_result.get("success"):
                    fit_score = llm_result.get("fit_score", 0)
                    # Use LLM-powered adjustments if available (structured with mention counts)
                    adjustments_result = get_cv_adjustments_with_llm(clean_resume, clean_job_desc)
                    if adjustments_result.get("success"):
                        adjustments = {
                            "missing_keywords": adjustments_result.get("missing_keywords", []),
                            "skills_to_bolster": adjustments_result.get("skills_to_bolster", [])
                        }
                    else:
                        # Fallback to basic mapping from LLM score output
                        adjustments = {
                            "missing_keywords": llm_result.get("missing_keywords", []),
                            "skills_to_bolster": [{"skill": skill, "job_mentions": 0, "resume_mentions": 0} for skill in llm_result.get("missing_skills", [])]
                        }
                    llm_insights = llm_result
                    using_llm = True
                else:
                    st.error(f"❌ LLM Analysis failed: {llm_result.get('error', 'Unknown error')}")
                    fit_score = None
                    adjustments = None
                    llm_insights = None
                    using_llm = False
            else:  # module analysis
                # Traditional matching
                fit_score = calculate_fit_score(clean_resume, clean_job_desc)
                adjustments = get_cv_adjustments(clean_resume, clean_job_desc)
                llm_insights = None
                using_llm = False
            
            # Display results
            if fit_score is not None:
                st.markdown("---")
                st.subheader("📊 Results")
                
                if using_llm:
                    st.info("🤖 Results from LLM Analysis")
                else:
                    st.info("⚡ Results from Module Analysis (TF-IDF)")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("Match Score")
                    display_fit_score(fit_score)
                
                with col2:
                    st.subheader("Quick Stats")
                    st.metric("Missing Keywords", len(adjustments["missing_keywords"]))
                    st.metric("Skills to Bolster", len(adjustments["skills_to_bolster"]))
                
                # Display LLM insights if available
                if llm_insights and llm_insights.get("reasoning"):
                    st.markdown("---")
                    st.subheader("💡 AI Analysis")
                    st.write(llm_insights.get("reasoning", ""))
                    
                    if llm_insights.get("recommendations"):
                        st.markdown("**Key Recommendations:**")
                        for i, rec in enumerate(llm_insights.get("recommendations", [])[:5], 1):
                            st.write(f"{i}. {rec}")
                
                # Display adjustments
                st.markdown("---")
                display_adjustments(adjustments)
                
                # Cover Letter Section
                st.markdown("---")
                st.subheader("📝 Cover Letter Generation")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🤖 Generate with AI", use_container_width=True):
                        with st.spinner("Generating your cover letter with AI..."):
                            llm_result = generate_cover_letter_with_llm(
                                clean_resume,
                                clean_job_desc
                            )
                            if llm_result.get("success"):
                                st.success("✓ Cover letter generated!")
                                st.write(llm_result.get("cover_letter", ""))
                                
                                if llm_result.get("improvement_tips"):
                                    st.markdown("**Tips for Customization:**")
                                    for tip in llm_result.get("improvement_tips", [])[:3]:
                                        st.write(f"• {tip}")
                            else:
                                st.error(f"Failed to generate: {llm_result.get('error', 'Unknown error')}")
                
                with col2:
                    if st.button("📋 Generate Template", use_container_width=True):
                        prompt = generate_cover_letter_prompt(
                            adjustments,
                            fit_score,
                            job_description
                        )
                        st.info(prompt)
                        st.text_area(
                            "Your tailored cover letter prompt",
                            value=prompt,
                            height=200,
                            disabled=True
                        )
    elif job_description.strip() and not analysis_type:
        st.info("👆 Click on 'LLM Analysis' or 'Module Analysis' to analyze your resume")

# Footer
st.markdown("---")
footer_text = "JOBMEET v2.0 | AI-Powered Resume Matcher"
if config.is_llm_enabled():
    footer_text += f" | LLM: {config.app.llm.model}"
else:
    footer_text += " | Powered by TF-IDF & Cosine Similarity"
st.caption(footer_text)
