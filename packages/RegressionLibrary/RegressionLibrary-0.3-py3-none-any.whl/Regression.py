import numpy as np 
from tqdm import tqdm
class LinearRegression ():
    def __init__ (self):
        self.parameters = {}
    
    def forward_pass(self,train_input):
        # y = m * x + b
        m = self.parameters.get('m')
        b = self.parameters.get('b')
        predictions = (m* train_input) + b
        return predictions
    
    def backward_pass(self,train_input,train_output,predictions):
        # calculate the derivatives 
        derivatives = {}
        # m = slope , b  = intercept
        # df/dm = 2 * mean((y - y_hat) * x)
        df = predictions - train_output 
        dm = 2 * np.mean(df * train_input)
        dc = 2 * np.mean(df)
        derivatives['m'] = dm
        derivatives['b'] = dc
        return derivatives
    
    def update_parameters(self,derivatives,learning_rate):
        # update the parameters 
        self.parameters['m'] = self.parameters['m'] - learning_rate * derivatives['m']
        self.parameters['b'] = self.parameters['b'] - learning_rate * derivatives['b']
    def fit(self,train_input,train_output,learning_rate ,epochs):
        #initialize the parameters 
        self.parameters['m'] = np.random.uniform(0,1)*-1
        self.parameters['b'] = np.random.uniform(0,1)*-1

        self.loss = []
        self.accuracy = []
        for epoch in tqdm(range(epochs)):
            predictions = self.forward_pass(train_input)
            derivatives = self.backward_pass(train_input,train_output,predictions)
            self.update_parameters(derivatives , learning_rate)
            loss = np.mean(predictions - train_output)**2
            accuracy = np.mean(np.abs(predictions - train_output) < 0.1) * 100
            self.loss.append(loss)
            self.accuracy.append(accuracy)
            print(f'Epoch {epoch+1}/{epochs}, Loss: {loss:.4f}', 'Accuracy: {:.2f}%'.format(accuracy))
        return self.parameters , np.mean(self.loss) , np.mean(self.accuracy)
    def predict(self, test_input):
        return self.forward_pass(test_input)
    def evaluate(self, test_input, test_output):
        predictions = self.forward_pass(test_input)
        mse = np.mean((test_output - predictions) ** 2)
        # r2 optional
        r2 = 1 - np.sum((test_output - predictions) ** 2) / np.sum((test_output - np.mean(test_output)) ** 2)
        accuracy = np.mean(np.abs(predictions - test_output) < 0.1) * 100
        return mse, r2 , accuracy 



class LassoRegression:
    def __init__(self, learning_rate=0.01, iterations=1000, l1_penalty=0.1):
        self.learning_rate = learning_rate
        self.iterations = iterations
        self.l1_penalty = l1_penalty

    def fit(self, X, Y):
        self.m, self.n = X.shape
        self.W = np.zeros(self.n)
        self.b = 0
        self.X = X
        self.Y = Y
        
        for i in tqdm(range(self.iterations)):
            self.update_weights()
            
            Y_pred = self.predict(self.X)
            loss = np.mean((self.Y - Y_pred) ** 2)
            accuracy = np.mean(np.abs(Y_pred - self.Y) < 0.1) * 100
            print(f'Iteration {i+1}/{self.iterations}, Loss: {loss:.4f}, Accuracy: {accuracy:.2f}%')
            
        return self

    def update_weights(self):
        Y_pred = self.predict(self.X)
        dW = np.zeros(self.n)

        for j in range(self.n):
            gradient = -2 * (self.X[:, j]).dot(self.Y - Y_pred) / self.m
            if self.W[j] > 0:
                dW[j] = gradient + self.l1_penalty
            else:
                dW[j] = gradient - self.l1_penalty

        db = -2 * np.sum(self.Y - Y_pred) / self.m

        self.W -= self.learning_rate * dW
        self.b -= self.learning_rate * db

    def predict(self, X):
        return X.dot(self.W) + self.b

    def evaluate(self, X, Y):
        Y_pred = self.predict(X)
        mse = np.mean((Y - Y_pred) ** 2)
        r2 = 1 - np.sum((Y - Y_pred) ** 2) / np.sum((Y - np.mean(Y)) ** 2)
        accuracy = np.mean(np.abs(Y_pred - Y) < 0.1) * 100
        return mse, r2, accuracy


class RidgeRegression():
    def __init__ (self , learning_rate ,  epochs , l2_penalty ):
        self.learning_rate = learning_rate 
        self.epochs = epochs 
        self.l2_penalty = l2_penalty 

    def fit(self, X,Y):
        self.m , self.n = X.shape 
        self.W = np.zeros(self.n)
        self.b=0
        self.X = X
        self.Y = Y
        
        for i in tqdm(range(self.epochs)):
            self.update_weights()
            Y_pred = self.predict(self.X)
            loss = np.mean(self.Y - Y_pred)**2 + self.l2_penalty * np.sum(self.W ** 2)
            accuracy = np.mean(np.abs(Y_pred - self.Y)<0.1) *100
            print(f'Epoch {i+1}/{self.epochs}, Loss: {loss:.4f}, Accuracy: {accuracy:.2f}%')
        return self
    def update_weights(self):
        Y_pred = self.predict(self.X)
        dW = ( - ( 2 * ( self.X.T ).dot( self.Y - Y_pred ) ) +               
               ( 2 * self.l2_penalty * self.W ) ) / self.m     
        db = - 2 * np.sum( self.Y - Y_pred ) / self.m
        self.W -= self.learning_rate * dW
        self.b -= self.learning_rate * db
    def predict(self,X):
        return X.dot(self.W) + self.b
    def evaluate(self, X, Y):
        Y_pred = self.predict(X)
        mse = np.mean((Y - Y_pred) ** 2)
        r2 = 1 - np.sum((Y - Y_pred) ** 2) / np.sum((Y - np.mean(Y)) ** 2)
        accuracy = np.mean(np.abs(Y_pred - Y) < 0.1) * 100
        return mse, r2, accuracy

class PolynomialRegression:
    def __init__(self, degree=2, learning_rate=0.01, epochs=1000):
        self.degree = degree
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.parameters = None

    def fit(self, X, Y):
        X_poly = np.vander(X.flatten(), self.degree + 1, increasing=True)
        self.parameters = np.zeros(X_poly.shape[1])
        
        for epoch in tqdm(range(self.epochs)):
            predictions = X_poly.dot(self.parameters)
            errors = predictions - Y
            
            gradients = (2 / len(Y)) * X_poly.T.dot(errors)
            self.parameters -= self.learning_rate * gradients
            
            loss = np.mean(errors ** 2)
            accuracy = np.mean(np.abs(predictions - Y) < 0.1) * 100
            print(f'Epoch {epoch + 1}/{self.epochs}, Loss: {loss:.4f}, Accuracy: {accuracy:.2f}%')
        
        return self

    def predict(self, X):
        X_poly = np.vander(X.flatten(), self.degree + 1, increasing=True)
        return X_poly.dot(self.parameters)

    def evaluate(self, X, Y):
        predictions = self.predict(X)
        mse = np.mean((Y - predictions) ** 2)
        r2 = 1 - np.sum((Y - predictions) ** 2) / np.sum((Y - np.mean(Y)) ** 2)
        accuracy = np.mean(np.abs(predictions - Y) < 0.1) * 100
        return mse, r2, accuracy

