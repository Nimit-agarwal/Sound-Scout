import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Wikipedia API endpoint
WIKIPEDIA_API_URL = 'https://en.wikipedia.org/w/api.php'

# Load data
df = pd.read_csv("charts.csv")

# Load the BART model
bart_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
bart_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")

def get_artist_info(artist_name):
  params = {
    'action': 'query',
    'format': 'json',
    'prop': 'extracts',
    'exintro': True,
    'explaintext': True,
    'titles': artist_name
  }
  response = requests.get(WIKIPEDIA_API_URL, params=params).json()
  pages = response.get('query', {}).get('pages', {})
  page = next(iter(pages.values()))
  description = page.get('extract', '')

  return description

def summarize_description(description):
  """Summarizes the given description using the BART model."""

  input_ids = bart_tokenizer(description, return_tensors="pt").input_ids
  outputs = bart_model.generate(input_ids, max_length=100, early_stopping=True)
  summary = bart_tokenizer.decode(outputs[0], skip_special_tokens=True)

  return summary

# Convert the 'Week' column to datetime format
df['Year'] = pd.to_datetime(df['Week'], format='%d-%m-%Y')

analysis_option = st.radio("Choose an analysis option:", ("Artist Discography over Time", "Artist Comparison"))

if analysis_option == "Artist Discography over Time":
  st.subheader("Artist Discography over Time")
  # Calculate the frequency of each artist
  artist_counts = df['Artists'].value_counts()

  # Get the top 5 artists
  top_5_artists = artist_counts.head(5).index.tolist()

  # Filter the dataset for the top 5 artists
  top_5_artists_data = df[df['Artists'].isin(top_5_artists)]

  # Group and aggregate data at the yearly level for the top 5 artists
  grouped = top_5_artists_data.groupby(['Year', 'Artists']).size().reset_index(name='Count')

  selected_artist = st.selectbox("Select an artist:", top_5_artists)

  # Plot the graph for the selected artist
  chart_data = grouped[grouped['Artists'] == selected_artist]
  fig = px.line(chart_data, x='Year', y='Count', title=f'Artist Count Over the Years - {selected_artist}')
  fig.update_traces(line=dict(color='green'))

  # Display the image and about section for the selected artist
  if selected_artist in top_5_artists:
    description = get_artist_info(selected_artist)
    summary = summarize_description(description)

    # Display the image
    st.image(f"https://en.wikipedia.org/wiki/{selected_artist}")

    # Display the description and summary
    st.markdown(f'## About {selected_artist}')
    st.markdown(description)
    st.markdown(f'**Summary:** {summary}')

    st.plotly_chart(fig)

elif analysis_option == "Artist Comparison":
  st.subheader("Artist Comparison")
  
  # Get the unique list of artists
  unique_artists = df['Artists'].unique().tolist()

  # Ask the user to select artists using multiselect dropdown
  selected_artists = st.multiselect("Select artists:", unique_artists)

  
  if len(selected_artists) > 0:
    # Filter the dataset for the selected artists
    artists_data = df[df['Artists'].isin(selected_artists)]

    # Group and aggregate data at the yearly level for the selected artists
    grouped = artists_data.groupby(['Year', 'Artists']).size().reset_index(name='Count')

    st.header("Comparison")

    # Create the Plotly line chart for the selected artists
    fig = px.line(grouped, x='Year', y='Count', color='Artists', title='Artist Comparison Over the Years')
    st.plotly_chart(fig)
    
else:
   st.write("Please select at least one artist.")
