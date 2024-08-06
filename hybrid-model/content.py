import pandas as pd
import numpy as np
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')

conn = sqlite3.connect('output.db')

words_df = pd.read_sql_query("SELECT ROWID, word FROM words", conn)
words_df.columns = ['word_id', 'word']

lyrics_df = pd.read_sql_query("SELECT track_id, word, count FROM lyrics WHERE is_test=0", conn)

conn.close()

lyrics_df['word'] = pd.to_numeric(lyrics_df['word'], errors='coerce')
lyrics_df.dropna(subset=['word'], inplace=True)
lyrics_df['word'] = lyrics_df['word'].astype(int)

lyrics_df = lyrics_df.merge(words_df, left_on='word', right_on='word_id', how='left')
track_lyrics = lyrics_df.groupby('track_id').apply(lambda x: ' '.join(x['word_y'] * x['count'])).reset_index()
track_lyrics.columns = ['track_id', 'lyrics']

stop_words = set(stopwords.words('english'))

def clean_lyrics(lyrics):
    tokens = lyrics.split()
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

track_lyrics['cleaned_lyrics'] = track_lyrics['lyrics'].apply(clean_lyrics)

tfidf_vectorizer = TfidfVectorizer(max_features=5000)
tfidf_matrix = tfidf_vectorizer.fit_transform(track_lyrics['cleaned_lyrics'])

from gensim.models import Word2Vec
from sklearn.cluster import KMeans

lyrics_tokens = track_lyrics['cleaned_lyrics'].apply(lambda x: x.split())
word2vec_model = Word2Vec(lyrics_tokens, vector_size=100, window=5, min_count=1, workers=4)

def get_song_vector(lyrics):
    words = lyrics.split()
    vectors = [word2vec_model.wv[word] for word in words if word in word2vec_model.wv]
    return np.mean(vectors, axis=0) if vectors else np.zeros(100)

track_lyrics['song_vector'] = track_lyrics['cleaned_lyrics'].apply(get_song_vector)

kmeans = KMeans(n_clusters=6, random_state=0)
track_lyrics['mood_cluster'] = kmeans.fit_predict(np.stack(track_lyrics['song_vector']))

mood_labels = {0: 'happy', 1: 'sad', 2: 'angry', 3: 'calm', 4:'idk1', 5:'idk2'}
track_lyrics['mood'] = track_lyrics['mood_cluster'].map(mood_labels)

from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

pca = PCA(n_components=2)
pca_components = pca.fit_transform(np.stack(track_lyrics['song_vector']))

track_lyrics['pca_component_1'] = pca_components[:, 0]
track_lyrics['pca_component_2'] = pca_components[:, 1]
