"""
Visualization and output formatting utilities
Professional styling with responsive design
"""

import streamlit as st


def display_fit_score(score: float):
    """
    Display match score with visual gauge and interpretation.
    
    Args:
        score: Match score percentage (0-100)
    """
    # Determine color and status based on score
    if score >= 85:
        color = "🟢"
        status = "Excellent Match"
        recommendation = "Strong fit! Consider applying."
    elif score >= 70:
        color = "🔵"
        status = "Good Match"
        recommendation = "Solid match. Worth applying to."
    elif score >= 50:
        color = "🟡"
        status = "Fair Match"
        recommendation = "Some relevant skills. Tailor your application."
    elif score >= 25:
        color = "🟠"
        status = "Limited Match"
        recommendation = "Consider upskilling in key areas."
    else:
        color = "🔴"
        status = "Poor Match"
        recommendation = "May not be the right fit at this time."
    
    # Display score with styling
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Progress bar with custom HTML
        progress_html = f"""
        <div style="margin: 1rem 0;">
            <div style="font-size: 2.5rem; font-weight: bold; color: #0066cc; margin-bottom: 0.5rem;">
                {int(score)}%
            </div>
            <div style="background-color: #e2e8f0; height: 24px; border-radius: 12px; overflow: hidden; margin-bottom: 0.75rem;">
                <div style="background: linear-gradient(90deg, #0066cc, #0052a3); height: 100%; width: {score}%; transition: width 0.3s ease;"></div>
            </div>
            <div style="font-size: 1.1rem; font-weight: 600; color: #334155;">
                {status}
            </div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
        st.caption(f"💡 {recommendation}")
    
    with col2:
        st.metric("Score Range", f"{int(score)}/100")


def display_adjustments(adjustments: dict):
    """
    Display CV adjustments in professional card layout with responsive design.
    
    Args:
        adjustments: Dictionary containing missing_keywords and skills_to_bolster
    """
    
    # Keywords Section
    st.markdown("#### 🎯 Keywords to Add")
    
    if adjustments.get('missing_keywords'):
        # Create keyword badges
        keywords_clean = [kw.replace('_', ' ').replace('-', ' ') for kw in adjustments['missing_keywords'][:12]]
        
        # Display as responsive columns
        cols = st.columns(min(3, len(keywords_clean)))
        for idx, keyword in enumerate(keywords_clean):
            with cols[idx % len(cols)]:
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, #f0f4ff 0%, #e6f0ff 100%);
                        padding: 0.75rem 1rem;
                        border-radius: 0.5rem;
                        border-left: 3px solid #0066cc;
                        margin-bottom: 0.5rem;
                        font-weight: 500;
                        color: #0052a3;
                    ">
                    📌 {keyword}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.success("✅ No major keywords missing!")
    
    st.divider()
    
    # Skills Section
    st.markdown("#### 📈 Skills to Emphasize")
    
    if adjustments.get('skills_to_bolster'):
        # Create a professional table view
        skill_data = []
        for item in adjustments['skills_to_bolster'][:10]:
            skill = item.get('skill', 'Unknown').replace('_', ' ').replace('-', ' ')
            job_mentions = item.get('job_mentions', 0)
            resume_mentions = item.get('resume_mentions', 0)
            gap = job_mentions - resume_mentions if job_mentions > 0 else 0
            
            skill_data.append({
                "Skill": skill.title(),
                "Job Mentions": int(job_mentions),
                "Your Resume": int(resume_mentions),
                "Gap": int(gap)
            })
        
        # Display as cards for each skill
        for skill_item in skill_data:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1], gap="small")
            
            with col1:
                st.markdown(
                    f"**{skill_item['Skill']}**",
                )
            
            with col2:
                st.metric("Job Mentions", skill_item['Job Mentions'], label_visibility="collapsed")
            
            with col3:
                st.metric("Your Resume", skill_item['Your Resume'], label_visibility="collapsed")
            
            with col4:
                gap_text = f"+{skill_item['Gap']}" if skill_item['Gap'] > 0 else "0"
                st.metric("Gap", gap_text, label_visibility="collapsed")
    else:
        st.success("✅ Your resume covers most required skills!")
    
    st.divider()
    
    # Strategy Section
    st.markdown("#### 💡 Adjustment Strategy")
    
    missing_count = len(adjustments.get('missing_keywords', []))
    skills_count = len(adjustments.get('skills_to_bolster', []))
    
    # Key metrics
    metric_col1, metric_col2 = st.columns(2, gap="small")
    
    with metric_col1:
        st.metric("Keywords to Add", missing_count)
    
    with metric_col2:
        st.metric("Skills to Emphasize", skills_count)
    
    # Action plan
    st.markdown("""
    **Priority Actions:**
    
    1. **Add Keywords** — Incorporate the missing keywords naturally into your resume
    2. **Emphasize Skills** — Expand descriptions of skills mentioned in the job posting
    3. **Quantify Achievements** — Add metrics and results to your experience bullets
    4. **Update Summary** — Tailor your professional summary to match the role
    5. **Generate Cover Letter** — Use the AI generator to create a tailored cover letter
    """)


def format_keyword_list(keywords: list, max_items: int = 20) -> str:
    """
    Format a list of keywords for display.
    
    Args:
        keywords: List of keywords
        max_items: Maximum items to display
        
    Returns:
        Formatted string
    """
    keywords_clean = [kw.replace('_', ' ').replace('-', ' ') for kw in keywords[:max_items]]
    return ', '.join(keywords_clean)
