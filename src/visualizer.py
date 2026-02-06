"""
Visualization and output formatting utilities
"""

import streamlit as st


def display_fit_score(score: float):
    """
    Display match score with visual gauge.
    
    Args:
        score: Match score percentage (0-100)
    """
    # Determine color based on score
    if score >= 75:
        color = "green"
        status = "Excellent Match"
    elif score >= 50:
        color = "orange"
        status = "Good Match"
    elif score >= 25:
        color = "yellow"
        status = "Moderate Match"
    else:
        color = "red"
        status = "Low Match"
    
    # Display metric
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Fit Score", f"{score}%")
    with col2:
        st.write(f"**Status**: {status}")
    
    # Progress bar visualization
    st.progress(min(score / 100, 1.0))


def display_adjustments(adjustments: dict):
    """
    Display CV adjustments in a clear, scannable format.
    
    Args:
        adjustments: Dictionary containing missing_keywords and skills_to_bolster
    """
    col1, col2 = st.columns(2)
    
    # Missing Keywords
    with col1:
        st.subheader("🎯 Keywords to Add")
        if adjustments['missing_keywords']:
            # Display as a formatted list without underscores or hyphens
            keywords_clean = [kw.replace('_', ' ').replace('-', ' ') for kw in adjustments['missing_keywords'][:15]]
            for i, keyword in enumerate(keywords_clean, 1):
                st.write(f"{i}. **{keyword}**")
        else:
            st.info("No major keywords missing!")
    
    # Skills to Bolster
    with col2:
        st.subheader("📈 Skills to Bolster")
        if adjustments['skills_to_bolster']:
            for item in adjustments['skills_to_bolster'][:15]:
                skill_clean = item['skill'].replace('_', ' ').replace('-', ' ')
                gap = item['job_mentions'] - item['resume_mentions']
                st.write(
                    f"**{skill_clean}** "
                    f"(Job mentions: {item['job_mentions']}, "
                    f"Your resume: {item['resume_mentions']})"
                )
        else:
            st.info("Your resume covers most required skills!")
    
    # Summary section
    st.markdown("---")
    st.subheader("💡 Adjustment Strategy")
    
    missing_count = len(adjustments['missing_keywords'])
    skills_count = len(adjustments['skills_to_bolster'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Keywords to Add", missing_count)
    with col2:
        st.metric("Total Skills to Bolster", skills_count)
    
    st.write(f"""
    **Action Items:**
    1. Add top **{min(5, missing_count)}** missing keywords from the left column to your resume
    2. Increase prominence of **{min(5, skills_count)}** skills from the right column
    3. Tailor your experience descriptions to highlight these keywords naturally
    4. Generate a cover letter that weaves in these adjustments
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
