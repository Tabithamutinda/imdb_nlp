import streamlit as st
import pandas as pd
from run_notebook import load_notebook_data  # Import the function from the run_notebook.py

# Streamlit application
st.title("Movie Review Sentiment Analysis")

# Load DataFrame from the Jupyter notebook
notebook_path = '/Users/mac/Imdb/notebook/imdb_moview_reviews_(1)_(3).ipynb'
try:
    movie_df = load_notebook_data(notebook_path)
    st.write("DataFrame Loaded Successfully")
    
    # Display the DataFrame
    st.write(movie_df)

except Exception as e:
    st.error(f"Error loading the DataFrame: {e}")