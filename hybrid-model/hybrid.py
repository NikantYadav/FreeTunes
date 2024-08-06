def hybrid_recommendation(user_id, song_id, alpha=0.5, top_n=10):
    cluster_recs = recommend_songs(song_id, top_n)
    collaborative_recs = recommend_songs_for_user(user_id, top_n)
    
    combined_scores = {}
    

    for idx, row in cluster_recs.iterrows():
        combined_scores[row['track_id']] = alpha * row['song_vector'] 

    for idx, row in collaborative_recs.iterrows():
        if row['track_id'] in combined_scores:
            combined_scores[row['track_id']] += (1 - alpha) * row['predicted_rating']
        else:
            combined_scores[row['track_id']] = (1 - alpha) * row['predicted_rating']


    combined_recs = pd.DataFrame.from_dict(combined_scores, orient='index', columns=['score'])
    return combined_recs.sort_values(by='score', ascending=False).head(top_n)
