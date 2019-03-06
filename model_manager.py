from sklearn import tree
import numpy as np
class Model(object):
	"""docstring for Model"""
	def __init__(self,i,j):
		super(Model, self).__init__()
		self.row = i
		self.col = j
		self.model = tree.DecisionTreeClassifier()

	def train(self,X_train,Y_train):
		self.model.fit(X_train,Y_train)

	def predict(self,X):
		res = self.model.predict(X)
		return np.bincount(res).argmax()
		