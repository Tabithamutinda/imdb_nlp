import streamlit as st
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Load the trained models and TF-IDF vectorizer
logistic_model = joblib.load('logistic_regression_model.pkl')
nb_model = joblib.load('naive_bayes_model.pkl')
# rf_model = joblib.load('random_forest_model.pkl')
dt_model = joblib.load('decision_tree_model.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

# Define a function to predict sentiment using the selected model
def predict_sentiment(review, model):
    review_vector = vectorizer.transform([review])
    prediction = model.predict(review_vector)
    probability = model.predict_proba(review_vector)
    return prediction[0], np.max(probability)

# Streamlit UI
st.title("Movie Reviews Sentiment Analysis")
st.write("Enter a movie review and get its sentiment classified as Positive or Negative.")

# Dropdown to select the model
model_choice = st.selectbox("Choose a model:", 
                            ("Logistic Regression", "Naive Bayes", "Decision Tree"))

# Dictionary to map model names to the actual model objects
model_dict = {
    "Logistic Regression": logistic_model,
    "Naive Bayes": nb_model,
    # "Random Forest": rf_model,
    "Decision Tree": dt_model
}

# Text input
user_input = st.text_area("Enter your movie review:")

if st.button("Predict Sentiment"):
    if user_input:
        # Get the selected model
        selected_model = model_dict[model_choice]
        
        # Predict sentiment
        sentiment, confidence = predict_sentiment(user_input, selected_model)
        
        # Display results
        if sentiment == 1:
            st.success(f"The review is **Positive** with a confidence of {confidence:.2f}")
        else:
            st.error(f"The review is **Negative** with a confidence of {confidence:.2f}")
    else:
        st.write("Please enter a review to analyze.")
