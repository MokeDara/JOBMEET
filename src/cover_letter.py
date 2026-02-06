"""
Cover letter generation utilities with LLM reasoning
Supports both template-based and AI-powered generation
"""

from typing import Optional, Dict
from llm_engine import get_llm_engine
from config import config


def _get_generic_cover_letter_template(fit_score: float) -> str:
    """Generate a generic cover letter template when no specific adjustments are available."""
    return f"""
COVER LETTER TEMPLATE
{'=' * 50}

Match Score: {fit_score}%

Dear Hiring Manager,

I am writing to express my strong interest in the [Job Title] position at [Company Name]. 
With my comprehensive professional background, I am confident that I am a strong fit for your team.

Throughout my career, I have developed expertise across multiple domains and consistently delivered 
results. My experience has equipped me with the ability to contribute meaningfully to your organization 
and drive success in key areas.

I am excited about the opportunity to bring my skills and dedication to [Company Name]. I have 
consistently demonstrated my commitment to excellence and am eager to contribute to your team's 
continued success.

I look forward to discussing how I can contribute to your company's goals and objectives.

Sincerely,
[Your Name]

{'=' * 50}

CUSTOMIZATION GUIDE:
1. Replace [Job Title], [Company Name], and [Your Name] with actual details
2. Add specific achievements and examples from your experience
3. Reference particular projects that demonstrate your qualifications
4. Maintain professional tone throughout
5. Keep cover letter to one page (3-4 paragraphs)
""".strip()


def generate_cover_letter_prompt(adjustments: dict, fit_score: float, job_description: str) -> str:
    """
    Generate a tailored cover letter prompt incorporating missing keywords and skills.
    
    Args:
        adjustments: Dictionary with missing_keywords and skills_to_bolster
        fit_score: The calculated match score
        job_description: The original job description
        
    Returns:
        A prompt template for cover letter generation
    """
    
    # Handle missing or empty adjustments
    if not adjustments:
        adjustments = {'missing_keywords': [], 'skills_to_bolster': []}
    
    missing_keywords = adjustments.get('missing_keywords', [])[:10]
    skills_to_bolster = adjustments.get('skills_to_bolster', [])[:10]
    
    # Ensure we have valid data
    if not missing_keywords and not skills_to_bolster:
        return _get_generic_cover_letter_template(fit_score)
    
    # Clean keywords for display (no underscores or hyphens)
    keywords_clean = [kw.replace('_', ' ').replace('-', ' ') for kw in missing_keywords if kw]
    
    skills_list = [item.get('skill', '').replace('_', ' ').replace('-', ' ') for item in skills_to_bolster if isinstance(item, dict) and item.get('skill')]
    
    # If we still don't have enough data, use generic template
    if not keywords_clean and not skills_list:
        return _get_generic_cover_letter_template(fit_score)
    
    # Build the prompt with safe access to list items
    top_skills = skills_list[:3] if len(skills_list) >= 3 else skills_list
    top_keywords = keywords_clean[:3] if len(keywords_clean) >= 3 else keywords_clean
    top_skill_single = skills_list[0] if skills_list else "[Your Primary Skill]"
    
    prompt = f"""
TAILORED COVER LETTER PROMPT
{'=' * 50}

Match Score: {fit_score}%

Key Keywords to Weave In:
{', '.join(keywords_clean[:5]) if keywords_clean else 'N/A'}

Skills to Emphasize:
{', '.join(skills_list[:5]) if skills_list else 'N/A'}

COVER LETTER TEMPLATE:

Dear Hiring Manager,

I am writing to express my strong interest in the [Job Title] position at [Company Name]. 
With my proven expertise in {', '.join(top_skills) if top_skills else 'my core competencies'}, I am confident that I am an excellent 
fit for your team.

Throughout my career, I have developed deep proficiency in {', '.join(top_keywords) if top_keywords else 'key industry skills'}, 
which directly aligns with the core requirements of this role. My experience has equipped me 
with the ability to [specific achievement related to top keyword], demonstrating my commitment 
to excellence in these critical areas.

In particular, I am excited about the opportunity to leverage my skills in {top_skill_single} 
to contribute meaningfully to your organization. I have consistently delivered results by 
[specific example], and I am eager to bring this same dedication to [Company Name].

I am confident that my background in {', '.join(top_skills[:2]) if len(top_skills) >= 2 else top_skill_single} makes me a valuable addition 
to your team. I look forward to discussing how I can contribute to your company's continued success.

Sincerely,
[Your Name]

{'=' * 50}

CUSTOMIZATION GUIDE:
1. Replace [Job Title], [Company Name], and [Your Name] with actual details
2. Add specific achievements that demonstrate the emphasized skills
3. Reference particular projects or experiences with the highlighted keywords
4. Maintain professional tone while naturally incorporating these terms
5. Keep cover letter to one page (3-4 paragraphs)
"""
    
    return prompt.strip()


def get_cover_letter_tips(fit_score: float) -> str:
    """
    Provide tips based on the fit score.
    
    Args:
        fit_score: The calculated match score
        
    Returns:
        Tips for improving the application
    """
    
    if fit_score >= 75:
        tips = """
EXCELLENT MATCH!
- Your resume strongly aligns with this job description
- Focus your cover letter on specific achievements matching the top keywords
- Highlight the unique value you bring to the organization
"""
    elif fit_score >= 50:
        tips = """
GOOD MATCH - With Minor Adjustments:
- Incorporate the suggested keywords into your resume
- Rewrite experience descriptions to emphasize the bolstered skills
- In your cover letter, explicitly connect your experience to their needs
"""
    else:
        tips = """
MODERATE TO LOW MATCH - Significant Adjustments Needed:
- Carefully review all suggested keywords and skills
- Consider if this role truly aligns with your background
- If pursuing it, substantially revise your resume to match requirements
- Use your cover letter to bridge major gaps with relevant examples
"""
    
    return tips.strip()


def generate_cover_letter_with_llm(resume: str, job_description: str, company_name: str = "[Company Name]") -> Dict:
    """
    Generate a professional cover letter using LLM reasoning
    
    Args:
        resume: Resume text
        job_description: Job description text
        company_name: Company name for personalization
        
    Returns:
        Dictionary with cover letter content and metadata
    """
    if not config.is_llm_enabled():
        return {
            "success": False,
            "error": "LLM not configured. Please set API key.",
            "fallback": True
        }
    
    try:
        llm = get_llm_engine(
            api_key=config.app.llm.api_key,
            model=config.app.llm.model
        )
        
        result = llm.generate_cover_letter(
            resume=resume,
            job_description=job_description,
            company_name=company_name
        )
        
        if "error" in result:
            return {
                "success": False,
                "error": result.get("message", "Failed to generate cover letter"),
                "fallback": True
            }
        
        return {
            "success": True,
            "cover_letter": result.get("cover_letter", ""),
            "key_themes": result.get("key_themes", []),
            "improvement_tips": result.get("improvement_tips", []),
            "opening_paragraph": result.get("opening_paragraph", ""),
            "model_used": config.app.llm.model
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fallback": True
        }


def analyze_fit_with_llm(resume: str, job_description: str) -> Dict:
    """
    Analyze resume-to-job fit using LLM reasoning
    
    Args:
        resume: Resume text
        job_description: Job description text
        
    Returns:
        Dictionary with detailed fit analysis
    """
    if not config.is_llm_enabled():
        return {
            "success": False,
            "error": "LLM not configured. Please set API key.",
            "fallback": True
        }
    
    try:
        llm = get_llm_engine(
            api_key=config.app.llm.api_key,
            model=config.app.llm.model
        )
        
        result = llm.analyze_resume_fit(
            resume=resume,
            job_description=job_description
        )
        
        if "error" in result:
            return {
                "success": False,
                "error": result.get("message", "Failed to analyze fit"),
                "fallback": True
            }
        
        return {
            "success": True,
            "fit_score": result.get("fit_score", 0),
            "key_strengths": result.get("key_strengths", []),
            "missing_skills": result.get("missing_skills", []),
            "missing_keywords": result.get("missing_keywords", []),
            "reasoning": result.get("reasoning", ""),
            "recommendations": result.get("recommendations", []),
            "model_used": config.app.llm.model
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fallback": True
        }


def get_cv_suggestions_with_llm(resume: str, job_description: str) -> Dict:
    """
    Get specific CV improvement suggestions using LLM
    
    Args:
        resume: Resume text
        job_description: Job description text
        
    Returns:
        Dictionary with specific improvement suggestions
    """
    if not config.is_llm_enabled():
        return {
            "success": False,
            "error": "LLM not configured. Please set API key.",
            "fallback": True
        }
    
    try:
        llm = get_llm_engine(
            api_key=config.app.llm.api_key,
            model=config.app.llm.model
        )
        
        result = llm.suggest_cv_improvements(
            resume=resume,
            job_description=job_description
        )
        
        if "error" in result:
            return {
                "success": False,
                "error": result.get("message", "Failed to get suggestions"),
                "fallback": True
            }
        
        return {
            "success": True,
            "section_improvements": result.get("section_improvements", {}),
            "skills_to_highlight": result.get("skills_to_highlight", []),
            "metrics_to_add": result.get("metrics_to_add", []),
            "wording_suggestions": result.get("wording_suggestions", []),
            "priority_score": result.get("priority_score", 0),
            "model_used": config.app.llm.model
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fallback": True
        }
