# JOBMEET - AI-Powered Resume Matcher & Optimizer

A modern web application that analyzes your resume against job descriptions using AI and provides intelligent, actionable recommendations to improve your fit.

**Built with**: Streamlit • Google Gemini API • Python

---

## ✨ Key Features

- **🤖 AI-Powered Resume Analysis**: Uses Google Gemini to intelligently analyze how well your resume matches a job description
- **📊 Dual Analysis Modes**:
  - **LLM Mode**: AI-driven intelligent analysis with detailed reasoning
  - **Normal Mode**: Fast TF-IDF algorithmic matching
- **🎯 Smart Recommendations**: Get specific keywords and skills to add to improve your fit score
- **📈 CV Adjustments**: Detailed suggestions for which skills to emphasize and what's missing
- **🔄 Session Persistence**: Upload your resume once and analyze multiple job descriptions without re-uploading
- **📑 Cover Letter Generation**: Auto-generate tailored cover letters (extensible for LLM integration)
- **⚡ Fallback Engine**: Automatically falls back to traditional TF-IDF matching if LLM is unavailable

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Gemini API key (free tier available at [makersuite.google.com](https://makersuite.google.com))

### 1. Clone & Setup

```bash
git clone <repository-url>
cd Jobmeet
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the root directory:

```env
# Google Gemini Configuration
GOOGLE_GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# LLM Provider Setting
LLM_PROVIDER=gemini

# Feature Flags
ENABLE_LLM=true
ENABLE_TRADITIONAL=true
```

Alternatively, copy from the template:
```bash
cp .env.example .env
# Then edit .env with your API key
```

### 3. Run the Application

```bash
streamlit run src/main.py
```

Your app will be available at `http://localhost:8501`

---

## 📖 How to Use

1. **Upload Resume** (Sidebar)
   - Click "Browse files" and select your PDF resume
   - Your resume will be loaded for the session

2. **Choose Analysis Mode** (Sidebar)
   - Select between **🤖 LLM Mode** (AI-powered) or **⚡ Normal Mode** (Fast TF-IDF)
   - Status shows which model is active

3. **Input Job Description**
   - Paste the job description text in the text area
   - The system will analyze the match

4. **Select Analysis Type**
   - **🤖 LLM Analysis**: Click for AI-powered detailed analysis with fit reasoning
   - **⚡ Module Analysis**: Click for TF-IDF algorithmic matching

5. **View Results**
   - **Fit Score**: Your match percentage (0-100)
   - **Keywords to Add**: Top missing keywords from the job description
   - **Skills to Bolster**: Skills mentioned in the job but underemphasized in your resume
   - **Detailed Insights** (LLM mode): AI reasoning, recommendations, and actionable improvements

---

## 🏗️ Project Structure

```
Jobmeet/
├── src/
│   ├── main.py              # Main Streamlit application interface
│   ├── config.py            # Configuration & API key management
│   ├── llm_engine.py        # LLM API integration (Google Gemini, OpenAI, Claude)
│   ├── matcher_engine.py    # Resume matching & CV adjustment logic
│   ├── text_processor.py    # PDF extraction & text cleaning
│   ├── visualizer.py        # Streamlit UI components & visualizations
│   └── cover_letter.py      # Cover letter generation (placeholder)
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── README.md                 # This file
└── .gitignore
```

---

## 🔧 Technical Details

### Analysis Engines

**LLM Mode (AI-Powered)**
- Uses Google Gemini API for intelligent analysis
- Provides fit scoring with detailed reasoning
- Returns key strengths, missing skills, and recommendations
- Model: `gemini-2.5-flash` (fast, cost-effective)

**Normal Mode (Traditional ML)**
- TF-IDF vectorization + Cosine Similarity
- Token-based keyword extraction
- Skill frequency analysis
- No API calls required

### Text Processing
- PDF text extraction via `pdfplumber`
- Text cleaning: lowercasing, stopword handling, tokenization
- Supports multi-page PDFs

### Dependencies

```
streamlit>=1.28.0
pdfplumber>=0.10.0
scikit-learn>=1.3.0
nltk>=3.8.1
python-dotenv>=1.0.0
google-generativeai>=0.3.0
```

---

## 🔌 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_GEMINI_API_KEY` | API key for Google Gemini | Required for LLM mode |
| `GEMINI_MODEL` | Gemini model to use | `gemini-2.5-flash` |
| `LLM_PROVIDER` | LLM provider (gemini/openai/anthropic) | `gemini` |
| `ENABLE_LLM` | Enable LLM analysis | `true` |
| `ENABLE_TRADITIONAL` | Enable traditional TF-IDF fallback | `true` |

---

## 🐛 Troubleshooting

**"LLM Analysis failed: Google Generative AI library not installed"**
```bash
pip install google-generativeai
```

**"Failed to call Google Gemini API"**
- Check your API key in `.env`
- Verify the key has proper permissions at [makersuite.google.com](https://makersuite.google.com)
- Ensure `ENABLE_LLM=true` in `.env`

**"Resume not loading"**
- Ensure the PDF is not corrupt
- Try a different resume file
- Check file size (limit: ~200MB per Streamlit default)

**Streamlit not starting**
```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/
# Reinstall dependencies
pip install --upgrade streamlit
streamlit run src/main.py
```

---

## 🚀 Future Enhancements

- [ ] Support for additional LLM providers (OpenAI GPT-4, Anthropic Claude)
- [ ] Cover letter generation with LLM integration
- [ ] Resume formatting/styling recommendations
- [ ] Batch job description processing
- [ ] Resume score history & tracking
- [ ] LinkedIn profile integration
- [ ] Interactive resume editor

---

## 📝 License

This project is open source and available under the MIT License.

---

## 💬 Support

For issues, questions, or suggestions:
1. Check the troubleshooting section above
2. Verify your `.env` configuration
3. Review Streamlit's documentation at [docs.streamlit.io](https://docs.streamlit.io)
4. Check Google Gemini API status and documentation

---

**Made with ❤️ to help you land your next opportunity**
