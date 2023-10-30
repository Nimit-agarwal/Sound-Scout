from pathlib import Path
import streamlit as st
from st_pages import Page, Section, add_page_title, show_pages

    ## Declaring the pages in your app 📄:
from st_lottie import st_lottie
with st.sidebar:
    st_lottie("https://lottie.host/4f9ac901-e5a7-4197-8e7a-c082c526cc21/4J94W1TV2f.json")

show_pages(
    [
        Page("pages/home.py", "🏠 Home"),
        Page("pages/analysisofsongs.py","🎶 Analysis of Songs"),
        Page("pages/analysisofartists.py", "🎤 Analysis of Artists"),
        Page("pages/analysisofgenre.py","🎧 Genre Analysis"),
        Page("pages/genreprediction.py","🔍 Genre Prediction"),  
    ]
)
add_page_title()
