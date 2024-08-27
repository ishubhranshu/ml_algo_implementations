import operator
from collections import Counter

class KNN:
    def __init__(self, k):
        self.k = k

    def fit(self, xtrain, ytrain):
        self.xtrain = xtrain
        self.ytrain = ytrain
        print("Training Done..")

    def predict(self, xtest):

        distances = {}
        counter = 1

        for i, point in enumerate(self.xtrain):
            distances[i] = ((xtest[0][0] - point[0])**2 + (xtest[0][1] - point[1])**2)**0.5

        distances = sorted(distances.items(), key=operator.itemgetter(1))
        classification = self.classify(distances[:self.k])

        return classification

    def classify(self, distances):
        labels=[]

        for distance in distances:
            labels.append(self.ytrain[distance[0]])
            
        return (Counter(labels).most_common()[0][0]) 