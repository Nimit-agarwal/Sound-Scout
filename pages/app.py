from pathlib import Path
import streamlit as st
from st_pages import Page, Section, add_page_title, show_pages

    ## Declaring the pages in your app 📄:

show_pages(
    [
        Page("pages/home.py", "🏠 Home"),
        Page("pages/analysis.py","🎶 Analysis of Songs"),
        Page("pages/top_5.py", "🎤 Top Artists"),
        Page("pages/analysisofgenre.py","🎧 Genre Analysis"),
        Page("pages/linear.py","🔍 Genre Prediction"),  
    ]
)
add_page_title()
