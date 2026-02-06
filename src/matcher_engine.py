"""
Resume matching and CV adjustment engine using TF-IDF and Cosine Similarity
with optional LLM-powered intelligent analysis
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import re
from config import config
from llm_engine import get_llm_engine


def calculate_fit_score(resume_text: str, job_description_text: str) -> float:
    """
    Calculate match percentage between resume and job description using Cosine Similarity.
    
    Args:
        resume_text: Cleaned resume text
        job_description_text: Cleaned job description text
        
    Returns:
        Match score as percentage (0-100)
    """
    if not resume_text or not job_description_text:
        return 0.0
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
    
    try:
        # Fit and transform both texts
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description_text])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Convert to percentage
        fit_score = round(similarity * 100, 2)
        
        return fit_score
    except Exception as e:
        print(f"Error calculating fit score: {str(e)}")
        return 0.0


def get_cv_adjustments(resume_text: str, job_description_text: str) -> dict:
    """
    Identify CV adjustments needed: missing keywords and skills to bolster.
    
    Args:
        resume_text: Cleaned resume text
        job_description_text: Cleaned job description text
        
    Returns:
        Dictionary with missing_keywords and skills_to_bolster
    """
    # Extract tokens
    resume_tokens = set(resume_text.split())
    job_tokens = set(job_description_text.split())
    
    # Find missing keywords (in job description but not in resume)
    missing_keywords = sorted(job_tokens - resume_tokens)
    
    # Get top missing keywords (prioritize by frequency in job description)
    job_freq = Counter(job_description_text.split())
    missing_keywords_sorted = sorted(
        missing_keywords,
        key=lambda x: job_freq.get(x, 0),
        reverse=True
    )[:20]  # Top 20 missing keywords
    
    # Find skills to bolster (mentioned in both but more in job description)
    skills_to_bolster = []
    resume_freq = Counter(resume_text.split())
    
    for token in job_tokens.intersection(resume_tokens):
        job_count = job_freq.get(token, 0)
        resume_count = resume_freq.get(token, 0)
        
        # If mentioned 2+ times more in job description
        if job_count > resume_count and job_count >= 2:
            skills_to_bolster.append({
                'skill': token,
                'job_mentions': job_count,
                'resume_mentions': resume_count
            })
    
    # Sort by frequency gap
    skills_to_bolster = sorted(
        skills_to_bolster,
        key=lambda x: x['job_mentions'] - x['resume_mentions'],
        reverse=True
    )[:20]  # Top 20 skills to bolster
    
    return {
        'missing_keywords': missing_keywords_sorted,
        'skills_to_bolster': skills_to_bolster
    }


def get_tfidf_weights(text: str, top_n: int = 20) -> list:
    """
    Get top weighted words from text using TF-IDF.
    
    Args:
        text: Text to analyze
        top_n: Number of top words to return
        
    Returns:
        List of (word, weight) tuples
    """
    vectorizer = TfidfVectorizer(max_features=top_n)
    
    try:
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        
        scores = tfidf_matrix.toarray()[0]
        weighted_words = sorted(
            zip(feature_names, scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        return weighted_words
    except Exception as e:
        print(f"Error calculating TF-IDF weights: {str(e)}")
        return []


def calculate_fit_score_with_llm(resume_text: str, job_description_text: str) -> dict:
    """
    Calculate fit score using LLM reasoning (more accurate than TF-IDF alone)
    
    Args:
        resume_text: Resume text
        job_description_text: Job description text
        
    Returns:
        Dictionary with fit_score, analysis, and reasoning
    """
    if not config.is_llm_enabled():
        return {
            "success": False,
            "error": "LLM not configured",
            "fallback": True,
            "fit_score": calculate_fit_score(resume_text, job_description_text)
        }
    
    try:
        llm = get_llm_engine(
            api_key=config.app.llm.api_key,
            model=config.app.llm.model
        )
        
        result = llm.analyze_resume_fit(resume_text, job_description_text)
        
        if "error" in result:
            return {
                "success": False,
                "error": result.get("message", "LLM analysis failed"),
                "fallback": True,
                "fit_score": calculate_fit_score(resume_text, job_description_text)
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
            "fallback": True,
            "fit_score": calculate_fit_score(resume_text, job_description_text)
        }


def get_cv_adjustments_with_llm(resume_text: str, job_description_text: str) -> dict:
    """
    Get CV adjustments using LLM reasoning
    
    Args:
        resume_text: Resume text
        job_description_text: Job description text
        
    Returns:
        Dictionary with detailed improvement suggestions
    """
    if not config.is_llm_enabled():
        return {
            "success": False,
            "error": "LLM not configured",
            "fallback": True,
            "adjustments": get_cv_adjustments(resume_text, job_description_text)
        }
    
    try:
        llm = get_llm_engine(
            api_key=config.app.llm.api_key,
            model=config.app.llm.model
        )
        
        result = llm.suggest_cv_improvements(resume_text, job_description_text)
        
        if "error" in result:
            return {
                "success": False,
                "error": result.get("message", "LLM analysis failed"),
                "fallback": True,
                "missing_keywords": [],
                "skills_to_bolster": []
            }
        
        # Extract the required keys from LLM response
        missing_keywords = result.get("missing_keywords", [])
        skills_to_bolster = result.get("skills_to_bolster", [])
        
        # Validate skills_to_bolster has required structure
        valid_skills = []
        for skill_item in skills_to_bolster:
            if isinstance(skill_item, dict) and "skill" in skill_item and "job_mentions" in skill_item and "resume_mentions" in skill_item:
                valid_skills.append(skill_item)
        
        return {
            "success": True,
            "missing_keywords": missing_keywords,
            "skills_to_bolster": valid_skills,
            "model_used": config.app.llm.model
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fallback": True,
            "adjustments": get_cv_adjustments(resume_text, job_description_text)
        }
