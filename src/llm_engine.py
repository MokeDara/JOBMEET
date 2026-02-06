"""
LLM Integration Engine for AI-powered resume analysis and cover letter generation
Supports OpenAI (GPT-4, GPT-3.5-turbo), Anthropic Claude, and Google Gemini APIs
"""

import os
from typing import Optional
import json


class LLMEngine:
    """Base class for LLM interactions"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize LLM Engine
        
        Args:
            api_key: API key for the LLM service (defaults to env variables)
            model: Model to use (gpt-3.5-turbo, gpt-4, claude-3-sonnet, etc)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.provider = self._detect_provider(model)
        
    def _detect_provider(self, model: str) -> str:
        """Detect which provider to use based on model name"""
        if model.startswith("gpt") or model.startswith("text-"):
            return "openai"
        elif model.startswith("claude"):
            return "anthropic"
        elif model.startswith("gemini"):
            return "gemini"
        else:
            return "openai"  # default
    
    def analyze_resume_fit(self, resume: str, job_description: str) -> dict:
        """
        Use LLM to analyze resume-to-job fit with intelligent reasoning
        
        Args:
            resume: Resume text
            job_description: Job description text
            
        Returns:
            Dictionary with fit analysis, score, and recommendations
        """
        if not self.api_key:
            raise ValueError("API key not found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
        
        prompt = f"""Analyze the following resume against the job description and provide intelligent insights:

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

Please provide a JSON response with:
1. "fit_score" (0-100): How well the resume matches the job
2. "key_strengths" (list): What resume strengths align with the job
3. "missing_skills" (list): Important skills from the job not in the resume
4. "missing_keywords" (list): Key terms to add to resume
5. "reasoning" (string): Detailed explanation of the fit analysis
6. "recommendations" (list): Specific actionable improvements

Return ONLY a raw JSON object. Do not use markdown code blocks, backticks, or any formatting. Start directly with {{ and end with }}."""

        if self.provider == "openai":
            return self._call_openai(prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt)
        elif self.provider == "gemini":
            return self._call_gemini(prompt)
        else:
            return self._call_openai(prompt)  # fallback
    
    def generate_cover_letter(self, resume: str, job_description: str, company_name: str = "[Company Name]") -> dict:
        """
        Generate a tailored cover letter using LLM reasoning
        
        Args:
            resume: Resume text
            job_description: Job description text
            company_name: Company name for personalization
            
        Returns:
            Dictionary with cover letter content and tips
        """
        if not self.api_key:
            raise ValueError("API key not found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
        
        prompt = f"""Write a professional, personalized cover letter based on:

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

COMPANY: {company_name}

Please provide a JSON response with:
1. "cover_letter" (string): A 3-4 paragraph professional cover letter
2. "key_themes" (list): Main themes emphasized in the letter
3. "improvement_tips" (list): Tips for further customization
4. "opening_paragraph" (string): Strong opening that hooks the reader

Return ONLY a raw JSON object. Do not use markdown code blocks, backticks, or any formatting. Start directly with {{ and end with }}."""

        if self.provider == "openai":
            return self._call_openai(prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt)
        elif self.provider == "gemini":
            return self._call_gemini(prompt)
        else:
            return self._call_openai(prompt)  # fallback
    
    def suggest_cv_improvements(self, resume: str, job_description: str) -> dict:
        """
        Get specific, actionable CV improvement suggestions from LLM
        
        Args:
            resume: Resume text
            job_description: Job description text
            
        Returns:
            Dictionary with improvement suggestions
        """
        if not self.api_key:
            raise ValueError("API key not found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
        
        prompt = f"""Analyze this resume against the job description and identify missing keywords and skills that need more emphasis.

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

Return ONLY valid JSON with these exact keys (no markdown, no code blocks):
{{
  "missing_keywords": [list of 10-15 important keywords from job description that are NOT in the resume],
  "skills_to_bolster": [list of objects with format {{"skill": "name", "job_mentions": number, "resume_mentions": number}} for skills appearing more in job description than in resume]
}}

Reply with ONLY the raw JSON object. Do not add any text before or after."""

        if self.provider == "openai":
            return self._call_openai(prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt)
        elif self.provider == "gemini":
            return self._call_gemini(prompt)
        else:
            return self._call_openai(prompt)  # fallback
    
    def _call_openai(self, prompt: str) -> dict:
        """Call OpenAI API"""
        try:
            import openai
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert career coach and resume specialist. Provide detailed, actionable insights in JSON format. Reply with raw JSON only, no markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Strip markdown code blocks if present
            if content.startswith("```"):
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines).strip()
            
            return json.loads(content)
        
        except json.JSONDecodeError:
            # If response isn't valid JSON, return error
            return {"error": "Failed to parse JSON response", "message": "Invalid JSON format from OpenAI API"}
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
        except Exception as e:
            return {"error": str(e), "message": "Failed to call OpenAI API"}
    
    def _call_anthropic(self, prompt: str) -> dict:
        """Call Anthropic Claude API"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            message = client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = message.content[0].text
            
            # Strip markdown code blocks if present
            if content.startswith("```"):
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines).strip()
            
            return json.loads(content)
        
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response", "message": "Invalid JSON format from Anthropic API"}
        except ImportError:
            raise ImportError("Anthropic library not installed. Install with: pip install anthropic")
        except Exception as e:
            return {"error": str(e), "message": "Failed to call Anthropic API"}
    
    def _call_gemini(self, prompt: str) -> dict:
        """Call Google Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            content = response.text
            
            # Strip markdown code blocks if present
            if content.startswith("```"):
                # Remove ```json or ``` at the start
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                # Remove ``` at the end
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines)
            
            return json.loads(content)
        
        except json.JSONDecodeError as e:
            # If response isn't valid JSON, return error
            return {"error": f"Failed to parse JSON response: {str(e)}", "message": "Invalid JSON format from Gemini API"}
        except ImportError:
            raise ImportError("Google Generative AI library not installed. Install with: pip install google-generativeai")
        except Exception as e:
            return {"error": str(e), "message": "Failed to call Google Gemini API"}


def get_llm_engine(api_key: Optional[str] = None, model: str = "gpt-3.5-turbo") -> LLMEngine:
    """
    Factory function to get LLM engine instance
    
    Args:
        api_key: Optional API key (defaults to environment variables)
        model: Model name (gpt-3.5-turbo, gpt-4, claude-3-sonnet, etc)
        
    Returns:
        LLMEngine instance ready to use
    """
    return LLMEngine(api_key=api_key, model=model)
