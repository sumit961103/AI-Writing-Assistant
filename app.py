import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Free tier compatible Gemini models
MODELS_TO_TRY = [
    "gemini-2.5-flash",        # Best free tier model (2026)
    "gemini-2.5-flash-lite",   # Lightweight fallback, highest RPD on free tier
    "gemini-2.5-pro",          # Most capable free tier model
]

st.set_page_config(
    page_title="AI Writing Assistant",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
    }

    /* Hide sidebar */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] { display: none !important; }

    /* Deep forest dark background */
    .stApp {
        background: #071a0f !important;
        background-image:
            radial-gradient(ellipse 80% 50% at 15% 5%, rgba(34,197,94,0.10) 0%, transparent 55%),
            radial-gradient(ellipse 60% 70% at 85% 95%, rgba(16,185,129,0.08) 0%, transparent 55%) !important;
        min-height: 100vh;
    }

    .block-container {
        max-width: 820px !important;
        padding: 2.5rem 1.5rem 5.5rem !important;
        margin: 0 auto !important;
    }

    /* ── Header ── */
    .header-wrap {
        text-align: center;
        margin-bottom: 2.5rem;
        padding: 1.5rem 1rem 1rem;
    }
    .main-title {
        font-family: 'DM Serif Display', serif !important;
        font-size: clamp(2rem, 6vw, 3rem);
        color: #86efac !important;
        margin: 0 0 0.4rem !important;
        line-height: 1.15;
        letter-spacing: -0.01em;
        text-shadow: 0 0 50px rgba(134,239,172,0.25);
    }
    .main-title em { color: #4ade80; font-style: italic; }
    .subtitle {
        color: #6ee7b7 !important;
        font-size: clamp(0.8rem, 2.5vw, 0.92rem);
        font-weight: 500;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        opacity: 0.75;
        margin-bottom: 1.2rem;
    }
    .pill-row {
        display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;
    }
    .pill {
        background: rgba(74,222,128,0.10);
        border: 1px solid rgba(74,222,128,0.22);
        color: #4ade80;
        padding: 4px 14px; border-radius: 999px;
        font-size: 0.75rem; font-weight: 600; letter-spacing: 0.05em;
    }

    /* ── Card ── */
    .card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(74,222,128,0.15);
        border-radius: 20px;
        padding: 2rem 2rem 1.5rem;
        backdrop-filter: blur(8px);
        box-shadow: 0 8px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05);
        margin-bottom: 1.5rem;
    }

    /* ── Widget labels ── */
    .stTextArea label p,
    .stSelectbox label p,
    label p {
        color: #a7f3d0 !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.09em !important;
        text-transform: uppercase !important;
    }

    /* ── Textarea ── */
    .stTextArea textarea {
        background: rgba(0,0,0,0.4) !important;
        border: 1.5px solid rgba(74,222,128,0.25) !important;
        border-radius: 14px !important;
        color: #ecfdf5 !important;
        font-size: 1rem !important;
        font-family: 'DM Sans', sans-serif !important;
        line-height: 1.75 !important;
        caret-color: #4ade80;
        transition: border-color 0.25s, box-shadow 0.25s !important;
    }
    .stTextArea textarea:focus {
        border-color: #4ade80 !important;
        box-shadow: 0 0 0 3px rgba(74,222,128,0.18) !important;
    }
    .stTextArea textarea::placeholder { color: rgba(167,243,208,0.3) !important; }

    /* ── Selectbox ── */
    .stSelectbox > div > div {
        background: rgba(0,0,0,0.4) !important;
        border: 1.5px solid rgba(74,222,128,0.25) !important;
        border-radius: 12px !important;
        color: #ecfdf5 !important;
    }
    .stSelectbox [data-baseweb="select"] span {
        color: #ecfdf5 !important;
    }
    .stSelectbox svg { fill: #4ade80 !important; }

    /* Dropdown popup */
    [data-baseweb="popover"] [role="listbox"] {
        background: #0d2818 !important;
        border: 1px solid rgba(74,222,128,0.25) !important;
        border-radius: 12px !important;
    }
    [data-baseweb="popover"] [role="option"] {
        color: #d1fae5 !important;
        background: transparent !important;
    }
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="popover"] [aria-selected="true"] {
        background: rgba(74,222,128,0.12) !important;
        color: #86efac !important;
    }

    /* ── Primary button ── */
    .stButton > button {
        background: linear-gradient(135deg, #15803d 0%, #22c55e 60%, #4ade80 100%) !important;
        color: #052e16 !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        width: 100% !important;
        letter-spacing: 0.02em;
        box-shadow: 0 4px 20px rgba(34,197,94,0.35), inset 0 1px 0 rgba(255,255,255,0.15) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(34,197,94,0.5) !important;
        color: #052e16 !important;
    }

    /* ── Result box ── */
    .result-box {
        background: rgba(20, 83, 45, 0.45);
        border: 1px solid rgba(74,222,128,0.3);
        border-radius: 14px;
        padding: 1.6rem 1.8rem;
        font-size: 1.05rem;
        line-height: 1.9;
        color: #ecfdf5;
        margin-top: 0.5rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
    }

    /* ── Original box ── */
    .original-box {
        background: rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        font-size: 0.97rem;
        line-height: 1.8;
        color: #a7f3d0;
        margin-top: 0.5rem;
    }

    /* ── Labels ── */
    .section-label {
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #4ade80;
        margin-bottom: 0.5rem;
        display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
    }
    .tone-badge {
        display: inline-block;
        background: linear-gradient(90deg, #15803d, #22c55e);
        color: #052e16;
        padding: 5px 18px; border-radius: 999px;
        font-size: 0.82rem; font-weight: 700;
        margin-bottom: 0.75rem;
    }
    .model-badge {
        background: rgba(74,222,128,0.12);
        border: 1px solid rgba(74,222,128,0.25);
        color: #4ade80;
        padding: 3px 12px; border-radius: 999px;
        font-size: 0.71rem; font-weight: 600;
    }

    /* ── Expander ── */
    details > summary {
        color: #4ade80 !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
    }
    .streamlit-expanderHeader p {
        color: #4ade80 !important;
        font-weight: 600 !important;
    }

    /* ── Download button ── */
    .stDownloadButton > button {
        background: transparent !important;
        color: #4ade80 !important;
        border: 1.5px solid rgba(74,222,128,0.35) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(74,222,128,0.1) !important;
        border-color: #4ade80 !important;
        color: #86efac !important;
    }

    /* ── Alerts ── */
    .stAlert { border-radius: 12px !important; }

    /* ── Spinner ── */
    .stSpinner > div { border-top-color: #22c55e !important; }

    /* ── Divider ── */
    hr { border-color: rgba(74,222,128,0.12) !important; margin: 1.5rem 0 !important; }

    /* ── Footer ── */
    .footer {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: rgba(7, 26, 15, 0.97);
        border-top: 1px solid rgba(74,222,128,0.12);
        backdrop-filter: blur(12px);
        text-align: center; padding: 0.65rem 1rem;
        font-size: 0.8rem; color: #6ee7b7; z-index: 999;
        letter-spacing: 0.04em;
    }

    /* ── Responsive ── */
    @media (max-width: 640px) {
        .block-container { padding: 1rem 0.8rem 5rem !important; }
        .card { padding: 1.2rem !important; }
        .main-title { font-size: 1.8rem !important; }
        .result-box, .original-box { padding: 1.1rem !important; }
        .pill-row { gap: 5px; }
    }
</style>
""", unsafe_allow_html=True)


def build_prompt(user_input: str, selected_tone: str) -> str:
    return f"""You are an expert writing assistant. Your task is to:

1. Correct all grammar, spelling, and punctuation errors in the given text.
2. Rewrite the text in the specified tone.
3. Keep the original meaning unchanged.
4. Make the text clear, natural, and fluent.

Tone options include: professional, casual, formal, friendly, persuasive, concise.

Instructions:
- Do not add new information.
- Do not remove important details.
- Keep the length similar unless asked to shorten.
- Ensure the output sounds natural and human-like.

Output format:
Corrected & Rewritten Text:
<your rewritten version here>

Original Text (for comparison):
<original input>

Tone Used:
<tone>

Text:
\"\"\"
{user_input}
\"\"\"

Tone:
{selected_tone}"""


def parse_response(response_text: str):
    sections = {"rewritten": "", "original": "", "tone": ""}
    try:
        if "Corrected & Rewritten Text:" in response_text:
            after_rewritten = response_text.split("Corrected & Rewritten Text:", 1)[1]
            if "Original Text (for comparison):" in after_rewritten:
                sections["rewritten"] = after_rewritten.split("Original Text (for comparison):", 1)[0].strip()
                after_original = after_rewritten.split("Original Text (for comparison):", 1)[1]
                if "Tone Used:" in after_original:
                    sections["original"] = after_original.split("Tone Used:", 1)[0].strip()
                    sections["tone"] = after_original.split("Tone Used:", 1)[1].strip()
                else:
                    sections["original"] = after_original.strip()
            else:
                sections["rewritten"] = after_rewritten.strip()
    except Exception:
        sections["rewritten"] = response_text.strip()
    return sections


# ── Header ──
st.markdown("""
<div class="header-wrap">
    <h1 class="main-title">✍️ AI <em>Writing</em> Assistant</h1>
    <p class="subtitle">Grammar Fix &nbsp;·&nbsp; Tone Rewrite &nbsp;·&nbsp; Powered by Gemini</p>
    <div class="pill-row">
        <span class="pill">✦ Professional</span>
        <span class="pill">✦ Casual</span>
        <span class="pill">✦ Formal</span>
        <span class="pill">✦ Friendly</span>
        <span class="pill">✦ Persuasive</span>
        <span class="pill">✦ Concise</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input Card ──
st.markdown("""
<div class='card'>
    <div style='text-align:center; margin-bottom:1.2rem;'>
        <span style='font-family: DM Serif Display, serif; font-size: clamp(1.1rem, 3vw, 1.5rem); color: #86efac; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; text-shadow: 0 0 30px rgba(134,239,172,0.3);'>🎓 NLP Mini Project</span>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1], gap="large")

with col1:
    user_text = st.text_area(
        "📝 Your Text",
        height=200,
        placeholder="Paste or type the text you want to improve here...",
    )

with col2:
    tone_options = ["Professional", "Casual", "Formal", "Friendly", "Persuasive", "Concise"]
    selected_tone = st.selectbox("🎙️ Tone", tone_options)
    st.markdown("<br>", unsafe_allow_html=True)
    run_button = st.button("✨ Rewrite Text")

st.markdown("</div>", unsafe_allow_html=True)

# ── Processing ──
if run_button:
    if not GEMINI_API_KEY:
        st.error("⚠️ GEMINI_API_KEY is not set. Please add it to your .env file.")
    elif not user_text.strip():
        st.warning("⚠️ Please enter some text to process.")
    else:
        with st.spinner("🔍 Finding best model & rewriting your text..."):
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                last_error = None
                success = False

                for model_name in MODELS_TO_TRY:
                    try:
                        model = genai.GenerativeModel(model_name)
                        prompt = build_prompt(user_text, selected_tone.lower())
                        response = model.generate_content(
                            prompt,
                            generation_config=genai.types.GenerationConfig(
                                temperature=0.7,
                                max_output_tokens=2048,
                            )
                        )
                        result = response.text
                        parsed = parse_response(result)

                        st.markdown("---")
                        st.markdown(
                            f"<div class='section-label'>✅ Corrected &amp; Rewritten"
                            f"&nbsp;<span class='model-badge'>via {model_name}</span></div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(f"<div class='tone-badge'>🎙 {selected_tone}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='result-box'>{parsed['rewritten']}</div>", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)

                        with st.expander("📄 View Original Text"):
                            st.markdown(
                                f"<div class='original-box'>{parsed['original'] or user_text}</div>",
                                unsafe_allow_html=True
                            )

                        combined = f"=== REWRITTEN ({selected_tone}) ===\n\n{parsed['rewritten']}\n\n=== ORIGINAL ===\n\n{user_text}"
                        st.download_button(
                            label="⬇️ Download Result",
                            data=combined,
                            file_name="rewritten_text.txt",
                            mime="text/plain",
                        )
                        success = True
                        break

                    except Exception as e:
                        last_error = str(e)
                        continue

                if not success:
                    st.error(f"❌ All models failed. Last error: {last_error}")
                    st.info("""
**To fix this:**
1. Visit [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Delete your old key and create a **new API key**
3. Paste the new key in your `.env` file as: `GEMINI_API_KEY=your_key_here`
4. Restart the app
""")

            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")


# ── Footer ──
st.markdown(
    "<div class='footer'>Made with ❤️ by Sumit TAU &nbsp;·&nbsp; All Rights Reserved © 2026</div>",
    unsafe_allow_html=True,
)