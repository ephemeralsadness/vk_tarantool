import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class Recommender:

    def __init__(self, tuples):
        self.data = {'user_id': [], 'link_id': [], 'values': []}
        self.counter = dict()
        for tuple_ in tuples:
            self.data['user_id'].append(tuple_[0])
            self.data['link_id'].append(tuple_[1])
            self.data['values'].append(1)
            if tuple_[1] not in self.counter.keys():
                self.counter[tuple_[1]] = 1
            else:
                self.counter[tuple_[1]] += 1

        self.data = pd.DataFrame(self.data)
        self.data = self.data.pivot(index='user_id', columns='link_id', values='values').fillna(0)
        self.similarity_matrix = cosine_similarity(self.data, self.data)
        self.similarity_matrix = pd.DataFrame(self.similarity_matrix, index=self.data.index, columns=self.data.index)

        self.popular_links = np.array([x[0] for x in sorted(self.counter.items(), key=lambda x: x[1], reverse=True)[:25]])

    def recommend(self, user_id):
        recommendation = []
        for link_id in self.popular_links:
            if link_id in self.data and user_id in self.similarity_matrix:
                cosine_scores = self.similarity_matrix[user_id]
                ratings_scores = self.data[user_id]
                index_not_rated = ratings_scores[ratings_scores.isnull()].index
                ratings_scores = ratings_scores.dropna()
                cosine_scores = cosine_scores.drop(index_not_rated)
                ratings_link = np.dot(ratings_scores, cosine_scores)/cosine_scores.sum()
                recommendation.append(ratings_link)
            else:
                recommendation.append(0)
        if sum(recommendation) == 0:
            return np.array([x[0] for x in sorted(self.counter.items(), key=lambda x: x[1], reverse=True)[:5]])
        else:
            return self.popular_links[np.array(recommendation).argsort()[-5:][::-1]]
