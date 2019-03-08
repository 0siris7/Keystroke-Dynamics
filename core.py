from database import *
import demjson
import numpy as np
from model_manager import Model
import pickle


def get_max_login_id():
	q = "select max(login_id) as  max from user_login"
	res = select(q)
	if res:
		return res[0]['max']
	else:
		return 0

def create_matrix():
	max_id = get_max_login_id()
	matrix = []
	for i in range(0,max_id+1):
		row = []
		for j in range(0,max_id+1):
			m = Model(i,j)
			row.append(m)
		matrix.append(row)
	for i in range(0,max_id+1):
		for j in range(0,max_id+1):
			matrix[j][i] = matrix[i][j]
	return matrix

def pre_process_features(features):
	# print(features)
	temp = []
	for f in features:
		if len(f) == 16 and None not in f:
			temp.append(f)

	if temp:
		temp = temp / np.max(temp)
		temp = np.asarray(temp)
	return temp


def train_matrix(matrix,user1,user2):
	user_1_id = user1['login_id']
	user_2_id = user2['login_id']

	user_1_features = pre_process_features(demjson.decode(user1['features']))
	user_2_features = pre_process_features(demjson.decode(user2['features']))

	user_1_op = np.asarray([user_1_id] * user_1_features.shape[0])
	user_2_op = np.asarray([user_2_id] * user_2_features.shape[0])
	X_train = np.append(user_1_features,user_2_features,axis=0)
	Y_train = np.concatenate((user_1_op,user_2_op),axis=0)
	matrix[user_1_id][user_2_id].train(X_train,Y_train)
	matrix[user_2_id][user_1_id].train(X_train,Y_train)


def train():
	matrix = create_matrix()
	q = "select * from user_login"
	res = select(q)
	for i in range((len(res))):
		for j in range((len(res))):
			user1 = res[i]
			user2 = res[j]
			train_matrix(matrix,user1,user2)
	file = open("model.pickle","wb")
	pickle.dump(matrix,file)
	file.close()


def predict(matrix,id1,id2,features):

	res = matrix[id2][id1].predict(features)

	return res

def predict_from_array(matrix,array,features):

	new_layer = []
	for i in range((len(array) - 1)):
		user1 = array[i]
		user2 = array[i+1]
		new_layer.append(predict(matrix,user1,user2,features))
	if len(new_layer) == 1:
		return new_layer[0]
	return predict_from_array(matrix,new_layer,features)




def get_login_id(features):
	file = open("model.pickle","rb")
	matrix = pickle.load(file)
	file.close()
	features = pre_process_features(demjson.decode(features))
	q = "select * from user_login"
	res = select(q)
	layer = []
	for row in res:
		layer.append(row['login_id'])
	id = predict_from_array(matrix,layer,features)
	return id


# features = "[[null,null,null,null,null],[65,349,346,411,284],[62,215,232,294,153],[79,347,336,415,268],[68,367,383,451,299],[84,347,350,434,263],[87,271,275,362,184],[91,407,397,488,316],[81,325,317,398,244],[73,862,884,957,789],[95,475,458,553,380],[78,219,213,291,141],[72,183,192,264,111],[81,242,234,315,161],[73,438,437,510,365],[72,370,362,434,298],[64,187,184,248,123]]"
# id = get_login_id(features)

# print(id)
# train()
