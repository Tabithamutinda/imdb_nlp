# -*- coding: utf-8 -*-
"""Another copy of SentimentAnalysisOnMovieReviews (1).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vQk32ybsPVr2SILKDMUW9TIVUJpkWkq7

# Sentiment Analysis on Movie Reviews
This dataset contains two columns: review and sentiment. The review column includes text data **(movie reviews)**, and the sentiment column labels each review as either `"positive"` or `"negative."` The main aim is to develop a model that can predict positive or negative reviews of different movie sentiments.

## Import Libraries
Import all necessary libraries to be used in the analysis process.
"""

import pandas as pd
import numpy as np
import re
import nltk
import seaborn as sns
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn import preprocessing

# Download necessary NLTK resources

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

"""### Load the dataset"""

movie_df = pd.read_csv('/content/IMDB Dataset.csv')

movie_df.head(10)

"""## Quick overview of the data"""

print(movie_df.isnull().sum())

movie_df.dtypes

"""## Visualize the Distribution of Reviews (Positive vs. Negative)
This step visualizes how many reviews are positive and how many are negative.
"""

movie_df['sentiment'].value_counts().plot(kind='bar', color=['blue', 'orange'])
plt.title('Distribution of Reviews (Positive vs. Negative)')
plt.xlabel('Sentiment')
plt.ylabel('Count')
plt.xticks(rotation=0)
plt.show()

"""# Step 1: Text Preprocessing

### Remove named entities (NER)
Named entities(e.g., names of people, places) which may not contribute to meaningful classification are removed.
"""

import nltk
from nltk.tokenize import word_tokenize
from nltk import ne_chunk, pos_tag

# Function to remove named entities
def remove_named_entities(text):
    # Tokenization and Part-of-Speech tagging
    tokens = word_tokenize(text)
    pos_tags = pos_tag(tokens)

    # Named Entity Recognition
    named_entities = ne_chunk(pos_tags)

    # Remove named entities by skipping chunks that represent entities
    cleaned_tokens = []
    for chunk in named_entities:
        if isinstance(chunk, nltk.Tree):  # If it's a named entity
            entity_label = chunk.label()
            if entity_label not in ['PERSON', 'ORGANIZATION', 'GPE']:  # Skip these entity types
                # If it's not a target entity, add the tokens back
                cleaned_tokens.extend([token for token, pos in chunk.leaves()])
        else:
            # If it's not a named entity, add the token back
            token, pos = chunk
            cleaned_tokens.append(token)

    # Join tokens back into a string
    return ' '.join(cleaned_tokens)

# Apply the function to the DataFrame
movie_df['cleaned_review'] = movie_df['review'].apply(remove_named_entities)

# Display the results
movie_df.head(5)

"""### Convert all text to lowercase

This ensures that all text is uniform (e.g., "Great" and "great" are treated the same).
"""

movie_df['cleaned_review'] = movie_df['cleaned_review'].str.lower()

movie_df.head(5)

"""
### Remove HTML tags from text in the dataset"""

from bs4 import BeautifulSoup

def remove_html(text):
    if isinstance(text, str):
        # Remove HTML using BeautifulSoup
        clean_text = BeautifulSoup(text, "html.parser").get_text()

        # Remove any unwanted characters (like remaining HTML artifacts) using regex
        clean_text = re.sub(r'\s+', ' ', clean_text)  # Remove excessive whitespace
        clean_text = re.sub(r'[^\w\s]', '', clean_text)  # Remove punctuation except word characters and spaces

        return clean_text.lower()  # Convert to lowercase
    return text

# Apply the function to the cleaned_review column
movie_df['cleaned_review'] = movie_df['cleaned_review'].apply(remove_html)

# Display the first few rows to verify changes
movie_df.head(5)

"""### Remove URLs, measurements, numbers, filler words, special characters, and punctuation

### Remove URLs
URLs are not useful for sentiment analysis thus removing them ensures the dataset is cleaner
"""

def remove_urls(text):
    return re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

movie_df['cleaned_review'] = movie_df['cleaned_review'].apply(remove_urls)
movie_df.head(5)

"""### Remove both numerical and written numbers

This ensures that the numbers do not interfere with the text-based analysis.
"""

def remove_numbers(text):
    text = re.sub(r'\b\d+\b', '', text)  # Remove numerical digits
    text = re.sub(r'\b(one|two|three|four|five|six|seven|eight|nine|ten)\b', '', text)  # Remove written numbers
    return text

movie_df['cleaned_review'] = movie_df['cleaned_review'].apply(remove_numbers)
movie_df.head(5)

"""### Remove measurements
Irrelevant units of measurements that do not contribute to sentiment classification are removed.
"""

def remove_measurements(text):
    # Regular expression to match measurements (e.g., numbers followed by units)
    # Example units: kg, meters, cm, lb, g, etc.
    pattern = r'\b\d+\.?\d*\s?(kg|cm|meter|meters|mm|g|lb|oz|km|miles|inch|inches|feet|ft)\b'

    # Remove all measurements from the text
    cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return cleaned_text

movie_df['cleaned_review'] = movie_df['cleaned_review'].apply(remove_measurements)
movie_df.head(5)

"""### **Remove Emojis**
This ensures that reviews do not contain emojis or smileys that could interfere with accurate text processing and analysis.
"""

# pip install emoji

import emoji

def remove_emojis(text):
    return emoji.replace_emoji(text, replace='')

movie_df['cleaned_review'] = movie_df['cleaned_review'].apply(remove_emojis)
movie_df.head(5)

"""### **Remove Filler Words**"""

# Define a list of filler words to remove
filler_words = [
    "uh", "um", "er", "probably", "you know", "I mean", "well", "so", "like", "basically",
    "actually", "seriously", "really", "just", "sort of", "kind of", "whatever",
    "honestly", "literally", "right", "yeah", "okay", "alright"
]

# Create a regex pattern from the list of filler words
filler_pattern = r'\b(?:' + '|'.join(filler_words) + r')\b'

# Define a function to remove filler words
def remove_filler_words(text):
    # Substitute filler words with an empty string
    cleaned_text = re.sub(filler_pattern, '', text, flags=re.IGNORECASE)
    # Remove extra spaces left after removing filler words
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text

# Apply the function to the text data
movie_df['cleaned_review'] = movie_df['cleaned_review'].apply(remove_filler_words)

# Show the original and cleaned reviews
movie_df.head(5)

"""### Remove special characters and punctuation"""

import string

def remove_special_chars(text):
    # Remove all punctuation and special characters except letters and numbers
    return re.sub(r'[{}]'.format(re.escape(string.punctuation)), '', text)

# Apply the function to the review column
movie_df['cleaned_review'] = movie_df['cleaned_review'].apply(remove_special_chars)
movie_df.head(5)

import string

def remove_special_chars(text):
    # Remove all punctuation and special characters except letters and numbers
    return re.sub(r'[{}]'.format(re.escape(string.punctuation)), '', text)

# Apply the function to the review column
movie_df['cleaned_review'] = movie_df['cleaned_review'].apply(remove_special_chars)
movie_df.head(5)

"""### Tokenization and Removal of Stop Words"""

def remove_stop_words(text):
    stop_words = set(stopwords.words('english'))
    additional_stop_words = [
    'movie', 'film', 'one', 'like', 'story', 'character', 'characters', 'just',
    'time', 'really', 'get', 'good', 'much', 'even', 'make', 'way', 'well',
    'first', 'see', 'two', 'also', 'would', 'could', 'many', 'people'
]
    stop_words = stop_words.union(set(additional_stop_words))
    clean_text = ' '.join([word for word in text.split() if word.lower() not in stop_words])
    return clean_text
movie_df['cleaned_review'] = movie_df['cleaned_review'].apply(remove_stop_words)

def tokenize_text(text):
    return word_tokenize(text)
movie_df['tokens'] = movie_df['cleaned_review'].apply(tokenize_text)
movie_df.head()

"""### Add Custom Stopwords"""

# Define custom stopwords for positive and negative reviews
positive_stopwords = ["amazing", "great", "excellent", "best", "wonderful", "awesome", "fantastic", "brilliant"]
negative_stopwords = ["terrible", "horrible", "awful", "worst", "bad", "boring", "disappointing", "poor"]

import nltk
from nltk.corpus import stopwords

# Download stopwords from NLTK if necessary
nltk.download('stopwords')

# Get NLTK's standard English stopwords
nltk_stopwords = set(stopwords.words('english'))

# Combine NLTK stopwords with custom stopwords for good and bad reviews
positive_all_stopwords = nltk_stopwords.union(positive_stopwords)
negative_all_stopwords = nltk_stopwords.union(negative_stopwords)

# Define a function to remove links
def remove_links(text):
    return re.sub(r'http\S+|www\S+|https\S+', '', text)

# Define a function to remove stopwords based on sentiment
def remove_sentiment_stopwords(text, sentiment):
    words = text.split()
    if sentiment == 'positive':
        cleaned_text = ' '.join([word for word in words if word.lower() not in positive_all_stopwords])
    elif sentiment == 'negative':
        cleaned_text = ' '.join([word for word in words if word.lower() not in negative_all_stopwords])
    else:
        cleaned_text = text  # In case there is no sentiment label
    return cleaned_text


# Apply the cleaning functions (based on sentiment)
movie_df['review'] = movie_df.apply(lambda row: remove_sentiment_stopwords(remove_links(row['review']), row['sentiment']), axis=1)

# Show the cleaned reviews
movie_df[['review', 'cleaned_review', 'sentiment']].head()

"""### Stemming"""

from nltk.stem import PorterStemmer
stemmer = PorterStemmer()

movie_df['tokens'] = movie_df['tokens'].apply(lambda x: [stemmer.stem(word) for word in x])

# Display the cleaned tokens
# Display the cleaned tokens
movie_df[['review', 'tokens']].head()

movie_df.head(30)

"""<!-- #### Remove numbers -->

## Vectorization

### Convert Text into Numerical Format(TF-IDF vectorizer)
"""

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer(stop_words='english')

# Fit and transform the reviews into a sparse matrix
tfidf_matrix = vectorizer.fit_transform(movie_df['cleaned_review'])

# Get feature names (words in the vocabulary)
feature_names = vectorizer.get_feature_names_out()

# Example: Get the TF-IDF scores for the first review
first_review_scores = tfidf_matrix[0]

# Convert the sparse matrix for the first review to a dictionary
# Using first_review_scores.toarray() would cause MemoryError, so we avoid that
importance_scores = {feature_names[i]: first_review_scores[0, i] for i in first_review_scores.nonzero()[1]}

# Print the TF-IDF scores for the first review
print(importance_scores)

"""### Bag of Words(BoW)

The Bag of Words model is a way of representing text data where each unique word in the corpus is represented as a feature. The model doesn't consider grammar or word order, just the frequency of words in the text.

**Aim**: To convert the movie reviews into a numerical format by counting the frequency of words using the Bag of Words model.
"""

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
# Initialize CountVectorizer (BoW)
vectorizer = CountVectorizer(stop_words='english')

# Fit and transform the reviews to a BoW matrix (X)
X = vectorizer.fit_transform(movie_df['cleaned_review'])

# Define the target variable (y)
y = movie_df['sentiment']

"""### Word cloud
A Word Cloud visually represents the most frequent words in the text, where the size of each word indicates its frequency or importance.

**Aim**: To visualize the most frequent words in the movie reviews using a word cloud.

* CountVectorizer(): This function converts
the text into a bag of words model by counting the occurrences of each word.

* fit_transform(): This method is applied to fit the vectorizer on the text and transform it into a sparse matrix where each row corresponds to a document, and each column corresponds to a word.

* get_feature_names_out(): This retrieves the vocabulary (list of words) created by the vectorizer.
"""

# pip install wordcloud matplotlib nltk pandas
# Import required libraries
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Join all the cleaned reviews into one large text
all_text = ' '.join(movie_df['cleaned_review'].tolist())

# Create the word cloud object
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)

# Plot the word cloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # No axis to show
plt.show()

# Generate a word cloud for positive reviews
positive_reviews = ' '.join(movie_df[movie_df['sentiment'] == 'positive']['cleaned_review'].tolist())
positive_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(positive_reviews)

# Plot the positive word cloud
plt.figure(figsize=(10, 5))
plt.imshow(positive_wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

# Generate a word cloud for negative reviews
negative_reviews = ' '.join(movie_df[movie_df['sentiment'] == 'negative']['cleaned_review'].tolist())
negative_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(negative_reviews)

# Plot the negative word cloud
plt.figure(figsize=(10, 5))
plt.imshow(negative_wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

"""### Convert sentiment to numerical values (binary: 1 for positive, 0 for negative)"""

y = pd.get_dummies(movie_df['sentiment'], drop_first=True).values.ravel()  # Positive = 1, Negative = 0

"""## Training

### Train-test split
"""

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Show the sizes of the training and testing sets
print(f"Training set size: {X_train.shape}")
print(f"Testing set size: {X_test.shape}")

"""### Naive Bayes"""

nb_model = MultinomialNB()
nb_model.fit(X_train, y_train)
y_pred_nb = nb_model.predict(X_test)
print(f'Naive Bayes Accuracy: {accuracy_score(y_test, y_pred_nb)}')

"""### Logistic Regression"""

log_reg = LogisticRegression(max_iter=1000)
log_reg.fit(X_train, y_train)
y_pred_log = log_reg.predict(X_test)
print(f'Logistic Regression Accuracy: {accuracy_score(y_test, y_pred_log)}')

"""### Random Forest"""

# rf_model = RandomForestClassifier()
# rf_model.fit(X_train, y_train)
# y_pred_rf = rf_model.predict(X_test)
# rf_accuracy = accuracy_score(y_test, y_pred_rf)
# print(f'Random Forest Accuracy: {rf_accuracy:.4f}')

"""### Decision Tree"""

tree_model = DecisionTreeClassifier()
tree_model.fit(X_train, y_train)
y_pred_tree = tree_model.predict(X_test)
tree_accuracy = accuracy_score(y_test, y_pred_tree)
print(f'Decision Tree Accuracy: {tree_accuracy:.4f}')

"""### Confusion matrix for Naive Bayes"""

cm_nb = confusion_matrix(y_test, y_pred_nb)
plt.figure(figsize=(6, 4))
sns.heatmap(cm_nb, annot=True, fmt="d", cmap="Blues")
plt.title('Naive Bayes Confusion Matrix')
plt.ylabel('Actual Label')
plt.xlabel('Predicted Label')
plt.show()

"""### Confusion matrix for Logistic Regression"""

cm_log = confusion_matrix(y_test, y_pred_log)
plt.figure(figsize=(6, 4))
sns.heatmap(cm_log, annot=True, fmt="d", cmap="Blues")
plt.title('Logistic Regression Confusion Matrix')
plt.ylabel('Actual Label')
plt.xlabel('Predicted Label')
plt.show()

"""### Confusion matrix for Random Forest"""

# cm_rf = confusion_matrix(y_test, y_pred_rf)
# plt.figure(figsize=(6, 4))
# sns.heatmap(cm_rf, annot=True, fmt="d", cmap="Blues")
# plt.title('Random Forest Confusion Matrix')
# plt.ylabel('Actual Label')
# plt.xlabel('Predicted Label')
# plt.show()

"""### Confusion matrix for Decision Tree"""

cm_tree = confusion_matrix(y_test, y_pred_tree)
plt.figure(figsize=(6, 4))
sns.heatmap(cm_tree, annot=True, fmt="d", cmap="Blues")
plt.title('Decision Tree Confusion Matrix')
plt.ylabel('Actual Label')
plt.xlabel('Predicted Label')
plt.show()

"""### Sentiment Classification Model Results

#### 1. Model Performance
- **Logistic Regression Accuracy**: 88.27%
- **Naive Bayes Accuracy**: 86.09%
- **Random Forest Accuracy**: 86.43%
- **Decision Tree Accuracy**: 74.00%

Logistic Regression achieved the best performance, with an accuracy of 88.27%, followed by Random Forest and Naive Bayes.

| Model              | Accuracy  |
|--------------------|-----------|
| Logistic Regression | 88.27%    |
| Naive Bayes         | 86.09%    |
| Random Forest       | 86.43%    |
| Decision Tree       | 74.00%    |

#### 2. Key Insights
- **Text Preprocessing**: Techniques such as cleaning text (removal of numbers, punctuation, and stop words) significantly improved the quality of the data.
- **TF-IDF Representation**: Helped highlight important words, minimizing the influence of frequently occurring, less meaningful terms.
- **Class Imbalance**: Slight class imbalance may have affected the performance of the Naive Bayes model.

#### 3. Challenges
- **Overfitting**: Certain models, particularly Decision Tree and Random Forest, showed signs of overfitting, which led to decreased generalization on unseen data.

#### 4. Conclusion
Logistic Regression provided the highest accuracy and demonstrated reliability for sentiment classification. Future improvements could involve hyperparameter tuning and feature engineering (such as incorporating bigrams or word embeddings) to boost model performance further.

# Create a Simple UI

Install the Required Libraries: First, install the required libraries for packaging and creating the UI.

#### Install Required Libraries
"""

# pip install ipywidgets joblib

"""#### Import Necessary Libraries"""

import joblib
import numpy as np
import ipywidgets as widgets
from IPython.display import display
from sklearn.feature_extraction.text import TfidfVectorizer

"""#### Function to Predict Sentiment
Create a function that will predict the sentiment based on the selected model and the user’s input:
"""

def predict_sentiment(review, model_choice):
    # Transform the input review using the vectorizer
    review_vector = vectorizer.transform([review])

    # Predict based on the selected model
    if model_choice == "Logistic Regression":
        model = log_reg
    elif model_choice == "Naive Bayes":
        model = nb_model
    elif model_choice == "Random Forest":
        model = rf_model
    elif model_choice == "Decision Tree":
        model = tree_model

    # Make the prediction
    prediction = model.predict(review_vector)
    probability = model.predict_proba(review_vector)

    sentiment = "Positive" if prediction[0] == 1 else "Negative"
    confidence = np.max(probability)

    return sentiment, confidence

"""#### Create the UI with Widgets
Now, you will create an interactive UI using ipywidgets:
"""

# Text area with custom layout
review_input = widgets.Textarea(
    value='',
    placeholder='Type your movie review here...',
    description='Review:',
    layout=widgets.Layout(width='100%', height='150px', border='2px solid black', padding='10px')
)

# Dropdown with improved styling
model_dropdown = widgets.Dropdown(
    options=['Logistic Regression', 'Naive Bayes', 'Random Forest', 'Decision Tree'],
    value='Logistic Regression',
    description='Model:',
    disabled=False,
    layout=widgets.Layout(width='50%', padding='5px')
)

# Submit button with custom style
submit_button = widgets.Button(
    description="Predict Sentiment",
    button_style='success',  # Colors: 'success', 'info', 'warning', 'danger' for styling
    layout=widgets.Layout(width='30%', padding='10px'),
    icon='check'  # Add icon
)

# Output area with styled border
output = widgets.Output(layout={'border': '2px solid green', 'padding': '10px'})

# Display the styled widgets
display(review_input, model_dropdown, submit_button, output)

"""### 6. How the Code Works
**Text Area (review_input):** This allows the user to type in their movie review.

**Dropdown (model_dropdown):** Lets the user select which model they want to use for the sentiment prediction.

**Submit Button (submit_button):** When clicked, it triggers the prediction function.

**Output Area (output):** Displays the result (sentiment and confidence score).

**Event Handler (on_submit_clicked):** This function gets called when the button is clicked. It reads the review, calls predict_sentiment(), and displays the result.

#### Adding Error Handling
To ensure a smoother user experience, we can add error handling for invalid inputs (like empty reviews). We will also add informative messages when input is not provided.

Here’s how you can improve the error handling:
"""

# Enhanced function to handle invalid inputs and prediction
def on_submit_clicked(b):
    with output:
        output.clear_output()  # Clear previous output
        review = review_input.value.strip()  # Remove extra spaces
        selected_model = model_dropdown.value

        if not review:
            display("⚠️ Please enter a review before submitting.")
            return

        try:
            # Predict the sentiment
            sentiment, confidence = predict_sentiment(review, selected_model)
            display(f"✅ Sentiment: **{sentiment}** with confidence: {confidence:.2f}")
        except Exception as e:
            display(f"❌ Error: {e}")

# pip install streamlit

"""## Set Up the Models and Save Them:

Save the trained models using joblib or pickle to later load them in the UI.
"""

import joblib

# Save models
joblib.dump(log_reg, 'logistic_regression_model.pkl')
joblib.dump(nb_model, 'naive_bayes_model.pkl')
joblib.dump(rf_model, 'random_forest_model.pkl')
joblib.dump(tree_model, 'decision_tree_model.pkl')

joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')

"""#### Load the Pre-trained Models and TF-IDF Vectorizer"""

# Load the saved models
log_reg = joblib.load('logistic_regression_model.pkl')
nb_model = joblib.load('naive_bayes_model.pkl')
rf_model = joblib.load('random_forest_model.pkl')
tree_model = joblib.load('decision_tree_model.pkl')

# Load the TF-IDF vectorizer
vectorizer = joblib.load('tfidf_vectorizer.pkl')



# pip install streamlit

"""## Create the Streamlit App:"""

import streamlit as st
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Load the trained models and TF-IDF vectorizer
logistic_model = joblib.load('logistic_regression_model.pkl')
nb_model = joblib.load('naive_bayes_model.pkl')
rf_model = joblib.load('random_forest_model.pkl')
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
                            ("Logistic Regression", "Naive Bayes", "Random Forest", "Decision Tree"))

# Dictionary to map model names to the actual model objects
model_dict = {
    "Logistic Regression": logistic_model,
    "Naive Bayes": nb_model,
    "Random Forest": rf_model,
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

# streamlit run /usr/local/lib/python3.10/dist-packages/colab_kernel_launcher.py

# !pip install streamlit pyngrok

# Commented out IPython magic to ensure Python compatibility.
# %%writefile app.py
# import streamlit as st
# st.title('My Streamlit App')
# st.write("This is a simple Streamlit app running in Colab!")

import streamlit as st
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
import re

# Load the models
log_reg = joblib.load('logistic_regression_model.pkl')
nb_model = joblib.load('naive_bayes_model.pkl')
rf_model = joblib.load('random_forest_model.pkl')
tree_model = joblib.load('decision_tree_model.pkl')

# Load the TF-IDF vectorizer
vectorizer = joblib.load('tfidf_vectorizer.pkl')

# Preprocessing function
def preprocess_text(text):
    # Same preprocessing steps you used before training
    text = re.sub(r'[^\w\s]', '', text.lower())
    return text

# Set up the Streamlit app
st.title("Sentiment Analysis of Movie Reviews")

# Input text for sentiment analysis
user_input = st.text_area("Enter a movie review")

# Dropdown for selecting the model
model_choice = st.selectbox("Choose a model", ("Logistic Regression", "Naive Bayes", "Random Forest", "Decision Tree"))

# Predict sentiment
if st.button("Analyze Sentiment"):
    if user_input:
        # Preprocess the input text
        cleaned_text = preprocess_text(user_input)
        transformed_text = vectorizer.transform([cleaned_text])

        # Make predictions based on the selected model
        if model_choice == "Logistic Regression":
            prediction = log_reg.predict(transformed_text)[0]
        elif model_choice == "Naive Bayes":
            prediction = nb_model.predict(transformed_text)[0]
        elif model_choice == "Random Forest":
            prediction = rf_model.predict(transformed_text)[0]
        else:
            prediction = tree_model.predict(transformed_text)[0]

        # Display the result
        sentiment = "Positive" if prediction == 1 else "Negative"
        st.write(f"Predicted Sentiment: **{sentiment}**")
    else:
        st.write("Please enter a review.")

"""## Run Streamlit in Google Colab:"""

from pyngrok import ngrok

# Start a Streamlit app
# !streamlit run app.py &

# Open a public URL using ngrok
public_url = ngrok.connect(port='8501')
public_url

"""## Save and Load the TF-IDF Vectorizer:

Along with the models, you also need to save the TfidfVectorizer to ensure the input text is transformed similarly to when the models were trained.
"""

# joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')