import streamlit as st
import src.extraction.receipt_extractor as r

st.write("FILE:", r.__file__)
st.write("HAS CLASS:", hasattr(r, "ReceiptExtractor"))
st.write("CLASS:", r.ReceiptExtractor)