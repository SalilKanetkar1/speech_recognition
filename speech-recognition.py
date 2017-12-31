
# coding: utf-8

# In[1]:


import tensorflow as tf
import time,sys,os,math,random,itertools,glob,cv2
from datetime import timedelta
#from sklearn.utils import shuffle
import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.model_selection import train_test_split,ShuffleSplit
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
#Adding Seed so that random initialization is consistent
from numpy.random import seed
seed(1)
from tensorflow import set_random_seed
import matplotlib.pyplot as plt
#get_ipython().run_line_magic('matplotlib', 'inline')
set_random_seed(2)
final_project_path = r"C:\tmp\speech_dataset"
os.chdir(final_project_path)


# In[2]:


def drawProgressBar(percent, barLen = 50):
	sys.stdout.write("\r")
	progress = ""
	for i in range(barLen):
		if i<int(barLen * percent):
			progress += "="
		else:
			progress += " "
	sys.stdout.write("[ %s ] %.2f%%" % (progress, percent * 100))
	sys.stdout.flush()



imp_labels = ['yes', 'no', 'up', 'down', 'left', 'right', 'on', 'off', 'stop', 'go', 'silence', 'unknown']

def load_train(train_path):
	images = []
	classes = []
	path = train_path
	file_names = os.listdir(os.path.join(os.getcwd(),train_path))
	counter = 1
	print("Creating Classes, reading images and breaking things ...\n")
	for file in file_names:
		drawProgressBar(counter/len(file_names))
		#print(file)
		classes.append(file.split("_")[0])
		image = cv2.imread(os.path.join(os.getcwd(),train_path,file))
		image = image.astype(np.float32)
		image = np.multiply(image, 1.0/255.0) #normalizing the pixel intensities
		images.append(image)
		counter += 1
	print("\nDone!")
	images = np.array(images)
	#classes now has all the labels. order preserved
	#but we need the classes to be floats/ints so lets map the shit out of them
	for i in range(len(classes)):
		if classes[i] not in imp_labels:
			classes[i] = 'unkown'
	d = {ni:indi for indi, ni in enumerate(set(classes))}
	classes = [d[ni] for ni in classes]
	classes = np.array(classes)
	n_values = np.max(classes)+1
	classes = np.eye(n_values)[classes]
	#classes = np.eye(n_values)[classes.reshape(-1)]
	print("\nDone!")
	print("\n images shape: {}, labels shape: {}".format(images.shape,classes.shape))
	return (images,classes)#(train_x,train_y,test_x,test_y)
	
images,labels = load_train("im_train")

def split_data(images, labels,test_size = 0.2, random_state = 7, shuffle = False):
	return(train_test_split(images,labels,test_size = test_size,random_state = random_state,shuffle = shuffle))
train_x,test_x,train_y,test_y = split_data(images,labels, test_size = 0.2, shuffle = True)
print(train_x.shape,test_x.shape,train_y.shape,test_y.shape)
#plt.imshow(train_x[12])


# In[36]:

num_classes = 12

def random_mini_batches(X, Y, mini_batch_size = 64, seed = 0):
	"""
	Creates a list of random minibatches from (X, Y)
	
	Arguments:
	X -- input data, of shape (input size, number of examples) (m, Hi, Wi, Ci)
	Y -- true "label" vector (containing 0 if cat, 1 if non-cat), of shape (1, number of examples) (m, n_y)
	mini_batch_size - size of the mini-batches, integer
	seed -- this is only for the purpose of grading, so that you're "random minibatches are the same as ours.
	
	Returns:
	mini_batches -- list of synchronous (mini_batch_X, mini_batch_Y)
	"""
	
	m = X.shape[0]                  # number of training examples
	mini_batches = []
	np.random.seed(seed)
	
	# Step 1: Shuffle (X, Y)
	permutation = list(np.random.permutation(m))
	shuffled_X = X[permutation,:,:,:]
	shuffled_Y = Y[permutation,:]

	# Step 2: Partition (shuffled_X, shuffled_Y). Minus the end case.
	num_complete_minibatches = math.floor(m/mini_batch_size) # number of mini batches of size mini_batch_size in your partitionning
	for k in range(0, num_complete_minibatches):
		mini_batch_X = shuffled_X[k * mini_batch_size : k * mini_batch_size + mini_batch_size,:,:,:]
		mini_batch_Y = shuffled_Y[k * mini_batch_size : k * mini_batch_size + mini_batch_size,:]
		mini_batch = (mini_batch_X, mini_batch_Y)
		mini_batches.append(mini_batch)
	
	# Handling the end case (last mini-batch < mini_batch_size)
	if m % mini_batch_size != 0:
		mini_batch_X = shuffled_X[num_complete_minibatches * mini_batch_size : m,:,:,:]
		mini_batch_Y = shuffled_Y[num_complete_minibatches * mini_batch_size : m,:]
		mini_batch = (mini_batch_X, mini_batch_Y)
		mini_batches.append(mini_batch)
	
	return mini_batches



def create_placeholders(n_H0, n_W0, n_C0, n_y):
	"""
	Creates the placeholders for the tensorflow session.
	
	Arguments:
	n_H0 -- scalar, height of an input image
	n_W0 -- scalar, width of an input image
	n_C0 -- scalar, number of channels of the input
	n_y -- scalar, number of classes
		
	Returns:
	X -- placeholder for the data input, of shape [None, n_H0, n_W0, n_C0] and dtype "float"
	Y -- placeholder for the input labels, of shape [None, n_y] and dtype "float"
	"""
	X = tf.placeholder(shape = [None, n_H0, n_W0, n_C0],dtype = tf.float32)
	Y = tf.placeholder(shape = [None, n_y],dtype = tf.float32)

	return X, Y


# In[40]:


def initialize_parameters():
	"""
	Initializes weight parameters to build a neural network with tensorflow. The shapes are:
						W1 : [4, 4, 3, 8]
						W2 : [2, 2, 8, 16]
	Returns:
	parameters -- a dictionary of tensors containing W1, W2
	"""
	
	tf.set_random_seed(1)                              # so that your "random" numbers match ours
		

	W1 = tf.get_variable("W1",[4, 4, 3, 8], initializer = tf.contrib.layers.xavier_initializer(seed = 0))
	W2 = tf.get_variable("W2",[2, 2, 16,16], initializer = tf.contrib.layers.xavier_initializer(seed = 0))


	parameters = {"W1": W1,
				  "W2": W2}
	
	return parameters


# In[ ]:


def forward_propagation(X, parameters):

	W1 = parameters['W1']
	W2 = parameters['W2']
	with tf.device('/device:CPU:0'):

		Z1 = tf.nn.conv2d(X,W1,strides = [1,2,2,1], padding = 'SAME')
		A1 = tf.nn.dropout(tf.nn.relu(Z1),keep_prob = 0.9)		
		P1 = tf.nn.max_pool(A1,ksize = [1,8,8,1], strides = [1,8,8,1],padding = 'SAME')
		

		Z2 = tf.nn.conv2d(P1, W2, strides=[1, 1, 1, 1], padding='SAME')
		A2 = tf.nn.dropout(tf.nn.relu(Z2),keep_prob = 0.8)#relu(Z2)
		P2 = tf.nn.max_pool(A2, ksize = [1, 4,4, 1], strides = [1, 2,2, 1], padding='SAME')
		
		Z3 = tf.nn.conv2d(P2, W2, strides=[1, 1, 1, 1], padding='SAME')
		A3 = tf.nn.dropout(tf.nn.relu(Z3),keep_prob = 0.8)
		P3 = tf.nn.max_pool(A3, ksize = [1, 4,4, 1], strides = [1, 2,2, 1], padding='SAME')
		# FLATTEN
		P = tf.contrib.layers.flatten(P3)
		Z4 = tf.contrib.layers.fully_connected(P, 12, activation_fn=None)
		Z5 = tf.nn.dropout(tf.contrib.layers.fully_connected(Z3, 12, activation_fn=None),keep_prob = 0.8)

	return Z5,Z3


def compute_cost(Z5, Y):

	cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits = Z5, labels = Y))
	
	return cost


# In[57]:


from tensorflow.python.framework import ops
def model(X_train, Y_train, X_test, Y_test, learning_rate=0.009,
		  num_epochs=100, minibatch_size=64, print_cost=True):
	"""
	Implements a three-layer ConvNet in Tensorflow:
	CONV2D -> RELU -> MAXPOOL -> CONV2D -> RELU -> MAXPOOL -> FLATTEN -> FULLYCONNECTED
	
	Arguments:
	X_train -- training set, of shape (None, 64, 64, 3)
	Y_train -- test set, of shape (None, n_y = 6)
	X_test -- training set, of shape (None, 64, 64, 3)
	Y_test -- test set, of shape (None, n_y = 6)
	learning_rate -- learning rate of the optimization
	num_epochs -- number of epochs of the optimization loop
	minibatch_size -- size of a minibatch
	print_cost -- True to print the cost every 100 epochs
	
	Returns:
	train_accuracy -- real number, accuracy on the train set (X_train)
	test_accuracy -- real number, testing accuracy on the test set (X_test)
	parameters -- parameters learnt by the model. They can then be used to predict.
	"""
	
	ops.reset_default_graph()                         # to be able to rerun the model without overwriting tf variables
	tf.set_random_seed(1)                             # to keep results consistent (tensorflow seed)
	seed = 3                                          # to keep results consistent (numpy seed)
	(m, n_H0, n_W0, n_C0) = X_train.shape             
	n_y = Y_train.shape[1]                            
	costs = []                                        # To keep track of the cost
	
	# Create Placeholders of the correct shape
	X, Y = create_placeholders(n_H0, n_W0, n_C0, n_y)

	# Initialize parameters
	parameters = initialize_parameters()
	
	# Forward propagation: Build the forward propagation in the tensorflow graph
	Z5,Z3 = forward_propagation(X, parameters)
	
	# Cost function: Add cost function to tensorflow graph
	#cost = compute_cost(Z3, Y)
	cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits = Z3, labels = Y))
	with tf.name_scope('Optimizer'):
	# Backpropagation: Define the tensorflow optimizer. Use an AdamOptimizer that minimizes the cost.
		optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)
	
	
	#summary_op = tf.summary.merge_all()
	config = tf.ConfigProto(log_device_placement=True)
	config.gpu_options.allow_growth = True
	sess = tf.Session(config = config)
	init = tf.global_variables_initializer()
	merged = tf.summary.merge([tf.summary.scalar('cross_entropy', cost)])
	writer = tf.summary.FileWriter(os.path.join(os.getcwd(),"logs"), graph=sess.graph)
	with sess.as_default():
		sess.run(init)
		# Do the training loop
		
		for epoch in range(num_epochs):
			start = time.time()
			minibatch_cost = 0.
			num_minibatches = int(m / minibatch_size) # number of minibatches of size minibatch_size in the train set
			batch_count = int(m/minibatch_size)
			seed = seed + 1
			minibatches = random_mini_batches(X_train, Y_train, minibatch_size, seed)
			#c = 0
			for minibatch in minibatches:
				(minibatch_X, minibatch_Y) = minibatch
				_ , temp_cost,summary= sess.run([optimizer, cost,merged], feed_dict={X:minibatch_X, Y:minibatch_Y})
				
				#c += 1
				minibatch_cost += temp_cost / num_minibatches
			#print(type(summary))
			if minibatch_cost <= 0.4 and costs[-1] - minibatch_cost <= 0.001:
				break;
			writer.add_summary(summary, epoch)
			if print_cost == False:
				drawProgressBar(epoch/num_epochs,barLen = 50)
			# Print the cost every epoch
			if print_cost == True and num_epochs<100 and epoch % 2 == 0:
				end = time.time()
				print ("Cost after epoch {}: {}\t time taken:{}".format(epoch, minibatch_cost,(end-start)))
			if print_cost == True and num_epochs>=100:
				if epoch % 10 == 0:
					end = time.time()
					print ("Cost after epoch {}: {}\t time taken:{}".format(epoch, minibatch_cost,(end-start)))
			if print_cost == True and epoch % 1 == 0:
				costs.append(minibatch_cost)
		
		
		# plot the cost
		plt.figure(figsize = (5,5))
		plt.plot(np.squeeze(costs))
		plt.ylabel('cost')
		plt.xlabel('iterations (per tens)')
		plt.title("Learning rate =" + str(learning_rate))
		#plt.savefig("asd.png")
		plt.show()
		with tf.device('/device:CPU:0'):
			# Calculate the correct predictions
			predict_op = tf.argmax(Z3, 1)
			correct_prediction = tf.equal(predict_op, tf.argmax(Y, 1))

			# Calculate accuracy on the test set
			accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
			print(accuracy)
			train_accuracy = accuracy.eval({X: X_train, Y: Y_train})
			test_accuracy = accuracy.eval({X: X_test, Y: Y_test})
		print("Train Accuracy:", train_accuracy)
		print("Test Accuracy:", test_accuracy)
				
		return train_accuracy, test_accuracy, parameters




print("\ndropout in non linear transformation layers, 3000 epochs, 1024 batch size\n")
start = time.time()
_, _, parameters = model(train_x, train_y, test_x, test_y,learning_rate=0.009,
		  num_epochs=3000, minibatch_size = 1024, print_cost=True)
end = time.time()
ttl = end-start
seconds = ttl%60
ttl//=60
if ttl > 60:
	minutes = ttl//60
ttl//=60
hrs = ttl
print("Time take: {} hours, {} minutes and {} seconds".format(hrs,minutes,seconds))

