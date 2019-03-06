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
	temp = []
	for f in features:
		if len(f) == 7 and None not in f:
			temp.append(f)
	temp = np.asarray(temp)
	temp = temp / np.max(temp)
	return temp


def train_matrix(matrix,user1,user2):
	user_1_id = user1['login_id']
	user_2_id = user2['login_id']
	print(user_1_id,user_2_id)
	user_1_features = pre_process_features(demjson.decode(user1['features']))
	user_2_features = pre_process_features(demjson.decode(user2['features']))
	user_1_op = np.asarray([user_1_id] * user_1_features.shape[0])
	user_2_op = np.asarray([user_2_id] * user_2_features.shape[0])
	X_train = np.append(user_1_features,user_2_features,axis=0)
	Y_train = np.concatenate((user_1_op,user_2_op),axis=0)
	matrix[user_1_id][user_2_id].train(X_train,Y_train)


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
	print(array)
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


# features = "[[105,108,96,635,611,707,539],[108,111,72,170,155,227,98],[111,118,57,271,298,355,214],[118,101,84,339,330,414,255],[101,32,75,654,662,737,579],[32,121,83,393,389,472,310],[121,111,79,209,211,290,130],[111,117,81,219,221,302,138],[117,32,83,138,147,230,55],[32,97,92,829,800,892,737],[97,110,63,544,557,620,481],[110,105,76,189,181,257,113],[105,108,68,166,182,250,98],[108,97,84,470,469,553,386],[97,32,83,367,332,415,284],[32,46,48,2046,2050,2098,1998],[46,97,52,428,440,492,376],[97,110,64,642,603,667,578],[110,105,25,179,213,238,154],[105,108,59,170,197,256,111],[108,97,86,566,550,636,480],[97,32,70,414,394,464,344],[32,105,50,399,416,466,349],[105,115,67,347,337,404,280],[115,32,57,329,339,396,272],[32,109,67,476,487,554,409],[109,121,78,309,299,377,231],[121,32,68,217,202,270,149],[32,108,53,402,422,475,349],[108,105,73,229,208,281,156],[105,102,52,401,406,458,349],[102,101,57,335,331,388,278]]"
# id = get_login_id(features)

# print(id)