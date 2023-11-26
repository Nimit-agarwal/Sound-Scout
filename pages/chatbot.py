import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import ai21
import streamlit as st
import requests
import json
import urllib.parse

st.set_page_config(page_title="Song Insights", page_icon="📝",initial_sidebar_state="collapsed")
with open("designing.css") as source_des:
    st.markdown(f'<style>{source_des.read()}</style>', unsafe_allow_html=True)
st.title("Song Insights")

# Set up Spotify API credentials
SPOTIPY_CLIENT_ID = '6c535639a5994b69be734012a94f0f94'
SPOTIPY_CLIENT_SECRET = '8552e374f87f4d64b3cf46a0d085624c'
client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)

# Create Spotify API object
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Set up AI21 API credentials
ai21.api_key = '6PEdkt0Qn9tYgwAUTuMp8XFevZOjeXAU'

# Set up Genius API credentials
def get_lyrics(music_name):
    url = f"https://lyrics.astrid.sh/api/search?q={music_name}"
    response = requests.get(url)
    data = json.loads(response.text)
    return data

def get_playlist_data(playlist_id):
    # Get playlist data
    results = sp.playlist(playlist_id, fields="tracks,next")
    tracks = results['tracks']
    spotify_url = f"https://open.spotify.com/embed/playlist/{playlist_id}"
    st.markdown(f"""
        <iframe style="border-radius:12px" src="{spotify_url}" width="100%" height="380" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
        <br><br>
        """, unsafe_allow_html=True)

    # Collect all tracks
    tracklist = tracks['items']
    while tracks['next']:
        tracks = sp.next(tracks)
        tracklist += tracks['items']

    # Extract track information and audio features
    playlist_info = []
    for track in tracklist:
        info = track['track']
        playlist_info.append((info['id'], info['name'], info['artists'][0]['name'], info['album']['name'], info['album']['id']))

    # Create DataFrame with track information
    data = pd.DataFrame(playlist_info, columns=['id', 'name', 'artist', 'album', 'album_id'])

    # Extract audio features for each song
    audio_features_ids = [track['track']['id'] for track in tracklist]
    audio_features = []

    for i in range(0, len(audio_features_ids), 50):
        audio_features_batch = sp.audio_features(audio_features_ids[i:i+50])
        audio_features += audio_features_batch

    # Create DataFrame with audio features
    audio_features_df = pd.DataFrame(audio_features)
    audio_features_df = audio_features_df[['id', 'danceability', 'energy', 'key', 'loudness', 'mode',
                                           'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence',
                                           'tempo', 'duration_ms', 'time_signature']]

    # Merge track information with audio features
    merged_df = pd.merge(data, audio_features_df, on='id')

    return merged_df

def get_track_data(track_id):
    # Get track data
    track = sp.track(track_id)
    spotify_url = f"https://open.spotify.com/embed/track/{track_id}"
    st.markdown(f"""
        <iframe style="border-radius:12px" src="{spotify_url}" width="100%" height="380" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
        <br><br>
        """, unsafe_allow_html=True)

    # Extract track information
    track_info = (track['id'], track['name'], track['artists'][0]['name'], track['album']['name'], track['album']['id'])

    # Create DataFrame with track information
    data = pd.DataFrame([track_info], columns=['id', 'name', 'artist', 'album', 'album_id'])

    # Extract audio features for the song
    audio_features = sp.audio_features([track_id])

    # Create DataFrame with audio features
    audio_features_df = pd.DataFrame(audio_features)
    audio_features_df = audio_features_df[['id', 'danceability', 'energy', 'key', 'loudness', 'mode',
                                           'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence',
                                           'tempo', 'duration_ms', 'time_signature']]

    # Merge track information with audio features
    merged_df = pd.merge(data, audio_features_df, on='id')

    return merged_df


def chatbot(df, selected_song_details):
    # Get user input
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "Hello,Ask me about the song"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Allow the user to ask further questions
    follow_up_question=st.chat_input("Ask question")
    if follow_up_question:
        st.session_state.messages.append({"role": "user", "content": follow_up_question})
        with st.chat_message("user"):
            st.write(follow_up_question)

    if follow_up_question:
        song = get_lyrics(selected_song_details['name'])
        if song:
                prompt = f"Lyrics: {song}\n"
        # Include the follow-up question in the prompt
        prompt += f"{follow_up_question}\n\n"
        
    # Add song features to the prompt
        song_features = df[df['id'] == selected_song_details['id']].iloc[0]
        for feature in ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']:
            prompt += f"{feature.capitalize()}: {song_features[feature]}\n"

        # Generate response using AI21
        response = ai21.Completion.execute(
            model="j2-ultra",
            prompt=prompt,
            numResults=1,
            maxTokens=1000,
            temperature=0.9,
            topKReturn=1,
            topP=1,
            presencePenalty={
                "scale": 1,
                "applyToNumbers": True,
                "applyToPunctuations": True,
                "applyToStopwords": True,
                "applyToWhitespaces": True,
                "applyToEmojis": True
            },
            countPenalty={
                "scale": 1,
                "applyToNumbers": True,
                "applyToPunctuations": True,
                "applyToStopwords": True,
                "applyToWhitespaces": True,
                "applyToEmojis": True
            },
            frequencyPenalty={
                "scale": 1,
                "applyToNumbers": True,
                "applyToPunctuations": True,
                "applyToStopwords": True,
                "applyToWhitespaces": True,
                "applyToEmojis": True
            },
            stopSequences=[]
        )
        res=response["completions"][0]["data"]["text"]
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    message = {"role": "assistant", "content": res}
            st.session_state.messages.append(message)


selector = st.selectbox("Choose an option:", ['Playlist', 'Song'])
if selector == 'Playlist':
    url = st.text_input('Enter the Spotify playlist link or playlist ID')
    parsed_url = urllib.parse.urlparse(url)
    playlist_id = parsed_url.path.split('/')[-1]
    if playlist_id:
        df = get_playlist_data(playlist_id)

        # Display tracklist
        selected_song = st.selectbox("Select a song:", df['name'].tolist())

        # Get the selected song's details
        selected_song_details = df[df['name'] == selected_song].iloc[0]
        st.write(f"Selected Song: {selected_song_details['name']} by {selected_song_details['artist']} from the album {selected_song_details['album']}")

        # Get lyrics for the selected song

        if selected_song:
            chatbot(df, selected_song_details)  # Pass the lyrics to the chatbot function
        else:
            st.write("Lyrics not found.")
else:

    url = st.text_input("Enter a Spotify track link or track ID:")
    parsed_url = urllib.parse.urlparse(url)
    track_id = parsed_url.path.split('/')[-1]
    if track_id:
        df = get_track_data(track_id)
        selected_song_details = df.iloc[0]
        chatbot(df, selected_song_details)
col1, col2, col3= st.columns(3)
with col1:
    pass
with col3:
    pass
with col2:
    for _ in range(25):
            st.write(" ")
    if st.button('Take me Home 🏠'):
        switch_page("🏠 Home")