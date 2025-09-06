import streamlit as st
import pdfplumber
import random

st.set_page_config(page_title="랜덤 논문 피드", layout="wide")
st.markdown("""
<style>
body {
    background-color: #fdfcfb;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #111;
}
.stMarkdown blockquote {
    border-left: 4px solid #888;
    padding-left: 12px;
    margin: 10px 0;
    font-size: 16px;
    line-height: 1.6;
    background-color: #f7f5f2;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

st.title("📖 랜덤 논문 피드")
st.markdown("PDF/TXT에서 280자 단위로 잘라 랜덤으로 보여주는 논문 피드입니다. 최신 10개까지만 표시됩니다.")

# 세션 상태 초기화
if 'texts' not in st.session_state:
    st.session_state.texts = []
if 'feed' not in st.session_state:
    st.session_state.feed = []

# 글자수 기준 분할
def split_by_chars(text, max_len=280):
    return [text[i:i+max_len].strip() for i in range(0, len(text), max_len) if text[i:i+max_len].strip()]

# PDF 처리 + 캐싱
@st.cache_data(show_spinner=False)
def extract_from_pdf(file):
    chunks = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                chunks.extend(split_by_chars(text))
    return chunks

# TXT 처리 + 캐싱
@st.cache_data(show_spinner=False)
def extract_from_txt(file):
    text = file.read().decode("utf-8")
    return split_by_chars(text)

# 파일 업로드
uploaded_files = st.file_uploader(
    "📄 PDF 또는 TXT 업로드 (여러 개 가능)", 
    type=["pdf","txt"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.session_state.texts = []
    for uploaded_file in uploaded_files:
        if uploaded_file.type == "application/pdf":
            chunks = extract_from_pdf(uploaded_file)
        else:
            chunks = extract_from_txt(uploaded_file)
        st.session_state.texts.extend(chunks)
    st.success(f"{len(st.session_state.texts)} 텍스트 조각 준비 완료!")

# 랜덤 버튼
col1, col2 = st.columns(2)
with col1:
    if st.button("🎲 랜덤 텍스트 추가"):
        if st.session_state.texts:
            new_text = random.choice(st.session_state.texts)
            st.session_state.feed.insert(0, new_text)
            st.session_state.feed = st.session_state.feed[:10]

with col2:
    if st.button("🔁 연속 랜덤 5개 추가"):
        if st.session_state.texts:
            for _ in range(min(5, len(st.session_state.texts))):
                st.session_state.feed.insert(0, random.choice(st.session_state.texts))
            st.session_state.feed = st.session_state.feed[:10]

# 피드 출력: 카드 형태
if st.session_state.feed:
    st.markdown("### 📰 최신 랜덤 텍스트 (최대 10개)")
    for txt in st.session_state.feed:
        st.markdown(f"> {txt}")
else:
    st.info("PDF 또는 TXT 파일을 업로드하세요.")
