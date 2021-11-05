import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from surprise import SVD, Dataset, Reader
import operator
from collections import defaultdict


class Recommender():
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
        reader = Reader()
        self.svd_trainset = Dataset.load_from_df(self.data, reader=reader)

        self.popular_links = np.array(
            [x[0] for x in sorted(self.counter.items(), key=lambda x: x[1], reverse=True)[:25]])

    def get_top_n(self, predictions, n=6):
        # First map the predictions to each user.
        top_n = defaultdict(list)
        # uid: User ID
        # iid： item ID
        # true_r: Real score
        # est: Estimated score
        for uid, iid, true_r, est, _ in predictions:
            top_n[uid].append((iid, est))
        # Then sort the predictions for each user and retrieve the k highest ones.
        # Find the K highest scored items for each user
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]

        return top_n

    def recommend(self, user_id):
        svd = SVD()
        self.svd_trainset = self.svd_trainset.build_full_trainset()
        svd.fit(self.svd_trainset)
        testset = [(user_id, p, 0) for p in self.popular_links]
        predictions = svd.test(testset)
        return [pair[0] for pair in self.get_top_n(predictions)[user_id] if pair[0] != user_id]
