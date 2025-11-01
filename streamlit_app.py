import streamlit as st
from dotenv import load_dotenv
load_dotenv()  

import pandas as pd
from protocol_extractor.pdfparser import PDFParserAgent
from protocol_extractor.llm_extractor import ExtractorAgent

st.set_page_config(page_title="Protocol Extractor", layout="wide")
st.title("Protocol Objective Extractor")

uploaded = st.file_uploader("Upload a protocol PDF", type=["pdf"])

if uploaded:
    pdf_path = f"/tmp/{uploaded.name}"
    with open(pdf_path, "wb") as f:
        f.write(uploaded.getbuffer())
    st.session_state.pdf_path = pdf_path

if st.button("Run Extraction"):
    if "pdf_path" in st.session_state:
        with st.spinner("Running neurosymbolic extraction......"):
            parser = PDFParserAgent()
            data = parser.extract_sections(st.session_state.pdf_path)
            st.session_state.data = data
        st.success("Symbolic extraction complete!")

if "data" in st.session_state:
    if st.button("Run LLM Extraction"):
        data = st.session_state.data
        if data.get("objectives_section_raw"):
            with st.spinner("Running LLM extraction..."):
                agent = ExtractorAgent()
                result = agent.extract_objectives_json(data)
                st.session_state.result = result
            st.success("LLM extraction done!")

if "result" in st.session_state:
    result = st.session_state.result
    st.subheader("Extraction Results")

    objs = result.get("objectives", [])
    if objs:
        for obj in objs:
            with st.expander(obj.get("objective_type", "Objective")):
                st.markdown(f"**Objective:** {obj.get('objective_text','')}")
                if obj.get("endpoints"):
                    st.dataframe(pd.DataFrame(obj["endpoints"]))
