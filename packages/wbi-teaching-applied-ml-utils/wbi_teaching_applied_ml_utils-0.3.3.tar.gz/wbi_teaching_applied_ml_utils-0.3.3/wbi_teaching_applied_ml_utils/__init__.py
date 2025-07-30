import sys
import requests
import json 
import os

from PIL import Image
from io import BytesIO

import time 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import platform

from scipy.special import expit

from IPython.display import display, Markdown, Latex
from matplotlib.widgets import Slider
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Rectangle

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Lasso, Ridge, LinearRegression

__version__ = '0.3.3'

class LinearAlgebraUtils:
    @staticmethod
    def Plotvec(u):
        fig, ax = plt.subplots(1,1,figsize=(4,4))
        ax.arrow(0, 0, *u, head_width=0.05, color='r', head_length=0.1)
        plt.text(*(u + 0.1), 'u')    
        plt.ylim(0, 2)
        plt.xlim(0, 2)
        plt.show()
        
    @staticmethod
    def Plotvec1(u, z, v):
        fig, ax = plt.subplots(1,1,figsize=(4,4))
        ax.arrow(0, 0, *u, head_width=0.05, color='r', head_length=0.1)
        plt.text(*(u + 0.1), 'u')
        
        ax.arrow(0, 0, *v, head_width=0.05, color='b', head_length=0.1)
        plt.text(*(v + 0.1), 'v')
        
        ax.arrow(0, 0, *z, head_width=0.05, head_length=0.1)
        plt.text(*(z + 0.1), 'z')
        
        plt.ylim(-2, 2)
        plt.xlim(-2, 2)
        plt.show()

    @staticmethod
    def Plotvec2(a,b):
        fig, ax = plt.subplots(1,1,figsize=(4,4))
        ax.arrow(0, 0, *a, head_width=0.05, color ='r', head_length=0.1)
        plt.text(*(a + 0.1), 'a')
        ax.arrow(0, 0, *b, head_width=0.05, color ='b', head_length=0.1)
        plt.text(*(b + 0.1), 'b')
        plt.ylim(-2, 2)
        plt.xlim(-2, 2)
        plt.show()

    @staticmethod
    def plot_points(x, y):
        fig, ax = plt.subplots(1,1,figsize=(4,4))
        _ = plt.scatter(x,y,color='red')
        plt.ylabel("Salary (y)")
        plt.title("Salary Data")
        plt.xlabel("Experience (x)")
        plt.show()

    @staticmethod
    def plot_regression_line(x, y, w0, w1):
        fig, ax = plt.subplots(1,1,figsize=(4,4))
        plt.scatter(x,y,color='red')
        axes = plt.gca()
        x_vals = np.array(axes.get_xlim())
        y_vals = w0 + w1 * x_vals
        _ = plt.plot(x_vals, y_vals, '--')
        plt.ylabel("Salary (y)")
        plt.title("Salary Data")
        plt.xlabel("Experience (x)")
        plt.show()

    @staticmethod
    def plot_mean_squared_error(x, y, w1, w0, compute_l):
        fig, ax = plt.subplots(1,1,figsize=(4,4))
        axes = plt.gca()
        w1_vals = np.arange(0, 20000, 100)
        L_vals = [compute_l(x, y, w1, w0) for w1 in w1_vals]

        _ = plt.plot(w1_vals, L_vals, '--')

        plt.ylabel("MSE")
        plt.title("Mean Squared Loss")
        plt.xlabel("$w_1$")
        plt.show()
        
    @staticmethod
    def load_salary_data():
        data_path = os.path.join(os.path.dirname(__file__), 'datasets', 'linear_algebra', 'salary_data.csv')
        train_data = np.loadtxt(data_path, skiprows=1, delimiter=",")
        x = train_data[:, 0]
        y = train_data[:, 1]        
        return x, y
        

class Exercise1Utils:
    ## Define a function that displays a dog
    images_URL = "http://vision.stanford.edu/aditya86/ImageNetDogs/images/"


    def load_npy(file_name):
        data_path = os.path.join(os.path.dirname(__file__), 'datasets', 'exercise1', file_name)
        return np.load(data_path)

    @staticmethod
    def load_data_exercise_1():
        train_data = Exercise1Utils.load_npy('train_data.npy')
        train_labels = Exercise1Utils.load_npy('train_labels.npy')
        test_data = Exercise1Utils.load_npy('test_data.npy')
        test_labels = Exercise1Utils.load_npy('test_labels.npy')
            
        return train_data, train_labels, test_data, test_labels

    def load_data_exercise_1_scaled():
        train_data, train_labels, test_data, test_labels = Exercise1Utils.load_data_exercise_1()

        scaler = StandardScaler()
        train_data_norm = scaler.fit_transform(train_data) 
        test_data_norm = scaler.transform(test_data)    
            
        return train_data, train_data_norm, train_labels, test_data, test_data_norm, test_labels

    @staticmethod
    def load_data_exercise_1_dog_embeddings(subset):
        file_name = 'vectors.csv.gz'
        embeddings_path = os.path.join(os.path.dirname(__file__), 'datasets', 'exercise1', file_name)

        df = pd.read_csv(embeddings_path, sep=';', compression='gzip', index_col=0)

        # Next, we will convert the embeddings String-column into a numpy-vector
        start_time = time.time()
        data = df["embedding"].apply(json.loads).values
        embeddings = np.zeros((data.shape[0], len(data[0])), dtype=np.float32)
        for i, d in enumerate(data):
            embeddings[i] = d
        
        # select a subset of the data
        df_sub = df[df["class"].isin(subset)]
        data_sub = embeddings[df["class"].isin(subset)]
        filenames = df_sub["dir"].values + "/" + df_sub["filename"].values

        x = data_sub
        y = df_sub["class"].values
        indices = np.arange(len(x), dtype=np.int32)

        (x_train, x_test, 
         y_train, y_test, 
         idx_train, idx_test, 
         filenames_train, filenames_test) = train_test_split(
                x, y, indices, filenames, train_size=1000, random_state=47)

        end_time = time.time()
        print(f"Time to load {np.round(end_time-start_time,3)}s")

        return (x_train, x_test, 
                y_train, y_test, 
                idx_train, idx_test, 
                filenames_train, filenames_test)

    @staticmethod
    def plot_dog(filename, label):

        plt.axis('off')
        url = f'{Exercise1Utils.images_URL}/{filename}.jpg'
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))        
            plt.imshow(img)
        plt.show()
        print("Label ", label)

    @staticmethod
    def plot_knn_results(query_file_name, query_label, filenames_train, labels, train=True):
        # Plot search results        
        k = len(filenames_train)
        fig, ax = plt.subplots(1, k+1, figsize=(3*(k+1),4))

        filename = query_file_name
        url = f'{Exercise1Utils.images_URL}/{filename}.jpg'

        response = requests.get(url, stream=True)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))            
            ax[0].imshow(img)
            ax[0].axis('off')
            ax[0].set_title(f"Query: {query_label}")

        for i, filename in enumerate(filenames_train):
            url = f'{Exercise1Utils.images_URL}/{filename}.jpg'        
            response = requests.get(url, stream=True)
            
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                ax[1+i].imshow(img)
                ax[1+i].axis('off')
                ax[1+i].set_title(f"{i+1}-NN: " + labels[i])

                #xy = (d_train["xmin"], d_train["ymin"])
                #width = d_train["xmax"]-d_train["xmin"]
                #height = d_train["ymax"]-d_train["ymin"]
                #rect = Rectangle(xy, width, height, edgecolor='white', fill=None)
                #ax[1+i].add_patch(rect)
                #ax[1+i].text(xy[0], xy[1], d_train["class"], fontsize=12, color='white', 
                #             verticalalignment='bottom', horizontalalignment='left')
                
            else:
                ax[i+1].remove()

        plt.tight_layout()
        plt.show()


class Exercise2Utils:
    @staticmethod
    def load_data_exercise_2():
        data_path = os.path.join(os.path.dirname(__file__), 'datasets', 'exercise2', 'ex1data2.txt')
        data = np.loadtxt(data_path, delimiter=',', dtype=np.float64)
        x = data[:, :1] / 100 # We will only use the size as a feature
        y = data[:, 2] / 1000 # convert to 1000$
        m = y.size
        return x, y, m

    @staticmethod
    def load_data_exercise_2_scaled():        
        x, y, m = Exercise2Utils.load_data_exercise_2()

        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.5, random_state=0)        
        scaler = StandardScaler()
        X_train_normalized = scaler.fit_transform(X_train)
        X_test_normalized = scaler.transform(X_test)

        return X_train, X_train_normalized, X_test, X_test_normalized, y_train, y_test, scaler

    @staticmethod
    def plotData(x_train, y_train, x_test, y_test):
        plt.figure(figsize=(10,5))
        plt.scatter(x_train, y_train, label='train data')
        plt.scatter(x_test, y_test, label='test data')
        plt.ylabel('Price in 1000$')
        plt.xlabel('Size in 100 sq-feet')
        plt.legend(loc=4)

    @staticmethod
    def plotDataModel(X_train, y_train, X_test, y_test, model, scaler):
        Exercise2Utils.plotData(X_train, y_train, X_test, y_test)
        axes = plt.gca()
        axes.set_xlim([0, 60])
        x_vals = np.array(axes.get_xlim())
        X_new = np.arange(-2, 6, 0.1).reshape(-1,1)
        y_new = model.predict(X_new)
        plt.plot(scaler.inverse_transform(X_new), y_new, '-')
        plt.show()

    @staticmethod
    def plotLine(x_train, y_train, x_test, y_test, w):
        Exercise2Utils.plotData(x_train, y_train, x_test, y_test)

        # Regression Line
        axes = plt.gca()
        x_vals = np.array(axes.get_xlim())
        y_vals = w[0] + w[1] * x_vals
        plt.plot(x_vals, y_vals, '-')


    @staticmethod
    def plotPolyLines(
            x_train, y_train, x_test, y_test, w, degree, 
            mapPolynomialFeatures, normalEqn, predictPrice
        ):
        Exercise2Utils.plotData(x_train, y_train, x_test, y_test)
            
        # Regression Polynom
        for degree in np.arange(2, degree+1) :
            X_poly = mapPolynomialFeatures(x_train[:,0], degree)    
            w_poly = normalEqn(X_poly, y_train);
            x1 = np.float32(np.linspace(5, 45, 100))
            x2 = np.float32(np.linspace(1, 1, 100))
            polys = mapPolynomialFeatures(x1, degree)
            y_vals = [predictPrice(poly, w_poly) for poly in polys]
            latex = "$\\dots+size^"+str(degree)+"$"
            plt.plot(x1, y_vals, alpha=0.8, lw=2, label=latex)
        
        plt.legend()        

    @staticmethod
    def plotLossFunction(X, y, w0_vals, w1_vals, L_vals, w):
        # surface plot
        fig = plt.figure(figsize=(12, 5))
        ax = fig.add_subplot(121, projection='3d')
        ax.plot_surface(w0_vals, w1_vals, L_vals, cmap='viridis')
        plt.xlabel('w0')
        plt.ylabel('w1')
        plt.title('Surface')

        # contour plot
        ax = plt.subplot(122)
        plt.contour(w0_vals, w1_vals, L_vals, linewidths=2, levels=20)
        plt.xlabel('w0')
        plt.ylabel('w1')
        plt.plot(w[0], w[1], 'ro', ms=10, lw=2)
        plt.title('Contour, showing minimum')

    @staticmethod
    def plot_one(X_train, y_train, X_test, y_test, degree_predictions, x_interval, degree):
        plt.figure(figsize=(10,5))
        plt.plot(X_train, y_train, 'o', label='training data', markersize=10)
        plt.plot(X_test, y_test, 'o', label='test data', markersize=10)
        for i,degree in enumerate(degree):
            plt.plot(x_interval, degree_predictions[i],
                     alpha=0.8, lw=2, label='degree={}'.format(degree))
        plt.legend(loc=4)
        plt.ylim(0,1000)
        plt.xlim(0,60)

    @staticmethod
    def plot_validation_curve(mse_train, mse_test, degrees):
        plt.figure(figsize=(14,5))
        plt.title('RMSE for varying polynomial degrees')
        plt.xlabel('polynomial Degree')
        plt.ylabel('RMSE')
        # plt.ylim(0, 100)
        plt.xticks(np.arange(min(degrees), max(degrees)+1, 1.0))

        plt.plot(degrees, np.sqrt(mse_train / 2), label='Training MSE')
        plt.plot(degrees, np.sqrt(mse_test  / 2), label='Test MSE')
        plt.legend(loc='best')
        plt.show()

    @staticmethod
    def plot_polynomial_rmse(polys, Ls_poly_train, Ls_poly_test=None, logscale=False):
        plt.figure(figsize=(14,5))
        plt.title('RMSE for varying polynomial degrees')
        plt.xlabel('polynomial Degree')
        plt.ylabel('RMSE')

        plt.plot(polys, Ls_poly_train, '-', label="RMSE train")
        plt.xticks(np.arange(min(polys), max(polys)+1, 1.0))

        if Ls_poly_test:
            plt.plot(polys, Ls_poly_test, '-', label="RMSE test")
        
        if logscale:
            plt.yscale('log')  # Set y-axis to log scale        
        
        plt.legend(loc='best')
        plt.show()

    @staticmethod
    def get_pipelines(alpha, random_state, max_iter, degree):
        result = (make_pipeline(
                StandardScaler(), 
                PolynomialFeatures(degree=degree), 
                LinearRegression()), "Linear Regression")
        result2 = (make_pipeline(
                StandardScaler(), 
                PolynomialFeatures(degree=degree), 
                Lasso(alpha=alpha, max_iter = max_iter, random_state=random_state)), "Lasso Regression")
        result3 = (make_pipeline(
                StandardScaler(), 
                PolynomialFeatures(degree=degree), 
                Ridge(alpha=alpha, max_iter = max_iter, random_state=random_state)), "Ridge Regression")
        return (result, result2, result3)


class Exercise3Utils:
    @staticmethod
    def load_exam_data():
        # The first two columns contains the exam scores and the third column
        # contains the label.
        data_path = os.path.join(os.path.dirname(__file__), 'datasets', 'exercise3', 'ex2data1.txt')
        data = np.loadtxt(data_path, delimiter=',', dtype=np.float64)
        X, y = data[:, 0:2], data[:, 2]
        
        # we norm the data
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        
        return X, y, scaler

    @staticmethod
    def load_microchip_data():
        data_path = os.path.join(os.path.dirname(__file__), 'datasets', 'exercise3', 'ex2data2.txt')
        data = np.loadtxt(data_path, delimiter=',', dtype=np.float64)
        X = data[:, :2]
        y = data[:, 2]
        
        # we norm the data
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        
        return X, y, scaler


    @staticmethod
    def load_sentiment_data():
        data_path = os.path.join(os.path.dirname(__file__), 'datasets', 'exercise3', 'full_set.txt')
        content = np.loadtxt(data_path, dtype=object, delimiter="\t")
        
        ## Separate the sentences from the labels
        sentences = np.array([x[0].strip() for x in content])
        labels = np.array([x[1].strip() for x in content])

        ## Transform the labels from '0 v.s. 1' to '-1 v.s. 1'
        y = np.array(labels, dtype='int8')
        y = 2*y - 1
        
        return sentences, labels, y


    @staticmethod
    def plot_learning_rate(L_history, alpha):
        fig, ax = plt.subplots(figsize=(12,6))
        ax.set_ylabel('$L(w)$')
        ax.set_xlabel('Iterations')
        plt.title('Alpha:' + str(alpha))
        _=ax.plot(range(len(L_history)), L_history, 'b')


    @staticmethod
    def plotData(X, y):
        fig = plt.figure(figsize=(8,6))

        # Find Indices of Positive and Negative Examples
        pos = y == 1
        neg = y == 0

        # Plot Examples
        plt.plot(X[pos, 0], X[pos, 1], 'x', lw=2, ms=10)
        plt.plot(X[neg, 0], X[neg, 1], 'o', ms=10)

        plt.xlabel('Normalized Exam 1 score')
        plt.ylabel('Normalized Exam 2 score')
        plt.legend(['Admitted', 'Not admitted'])

    @staticmethod
    def plotMicrofabDecisionBoundary(X_poly, y, w, cost, degree, lambda_):
        Exercise3Utils.plotDecisionBoundary(X_poly, y, w, degree)
        plt.xlabel('Microchip Test 1')
        plt.ylabel('Microchip Test 2')
        plt.legend(['y = 1', 'y = 0'])
        plt.grid(False)
        plt.title('lambda = %0.2f, loss = %0.2f, ' % (lambda_, cost))
        plt.xlabel('Microchip Test 1')
        plt.ylabel('Microchip Test 2')
        plt.legend(['y = 1', 'y = 0'], loc='upper right')

    @staticmethod
    def sigmoid(z):
        return expit(z)

    @staticmethod
    def plotDecisionBoundary3d(X, y, w, elev=5, azim=-45):
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot data points
        ax.scatter(X[y == 1][:, 0], X[y == 1][:, 1], 1, label='Admitted', s=100)
        ax.scatter(X[y == 0][:, 0], X[y == 0][:, 1], 0, label='Not admitted', s=100)
        ax.view_init(elev=elev, azim=azim)

        # Create grid to plot decision boundary plane
        x1 = np.linspace(np.min(X[:, 0]), np.max(X[:, 0]), 10)
        x2 = np.linspace(np.min(X[:, 1]), np.max(X[:, 1]), 10)
        xx1, xx2 = np.meshgrid(x1, x2)
        
        zz = Exercise3Utils.sigmoid((w[0] + w[1]*xx1 + w[2]*xx2))
        # zz = zz.T

        # Plot the decision boundary plane
        ax.plot_surface(xx1, xx2, zz, color='orange', alpha=0.2)
        plt.xlabel('Normalized Exam 1 score')
        plt.ylabel('Normalized Exam 2 score')
        
        ax.set_zlabel('$h_w(x)$')
        ax.set_zlim([-1,2])
        
        ax.legend()
        plt.tight_layout()


    @staticmethod
    def plotPolyDecisionBoundary3d(X, y, w, degree=6, elev=5, azim=-45):
        print("Theta", w.shape)

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot data points
        pred = Exercise3Utils.sigmoid(
                np.dot(Exercise3Utils.mapFeature(X[:, 0], X[:, 1], degree), w)
            )
        X_pred = pred >= 0.5
        
        ax.scatter(
            X[y == 1][:, 0], X[y == 1][:, 1], 
            # 1, 
            pred[y == 1],
            label='Admitted', s=100)
        ax.scatter(
            X[y == 0][:, 0], X[y == 0][:, 1], 
            # 0, 
            pred[y == 0],
            label='Not admitted', s=100)

        # Create grid to plot decision boundary plane
        # x1 = np.linspace(np.min(X[:, 0]), np.max(X[:, 0]), 20)
        # x2 = np.linspace(np.min(X[:, 1]), np.max(X[:, 1]), 20)
        # Define grid range
        x1 = np.linspace(-2, 2, 50)
        x2 = np.linspace(-2, 2, 50)
        xx1, xx2 = np.meshgrid(x1, x2)
        
        z = np.zeros((x1.size, x2.size))
        for i, ui in enumerate(x1):
            for j, vj in enumerate(x2):
                z[i, j] = Exercise3Utils.sigmoid(np.dot(Exercise3Utils.mapFeature(ui, vj, degree), w))
        z = z.T

        # Plot the decision boundary plane
        ax.plot_surface(xx1, xx2, z, color='blue', alpha=0.2)
        plt.xlabel('Microchip Test 1')
        plt.ylabel('Microchip Test 2')
        
        ax.set_zlabel('$h_w(x)$')
        ax.set_zlim([-1,2])
        ax.view_init(elev=elev, azim=azim)

        # ax.legend()
        # plt.tight_layout()
        # plt.show()


    @staticmethod   
    def mapFeature(X1, X2, degree):
        """
        poly = PolynomialFeatures(degree=degree, include_bias=True)                
        if X1.ndim > 0:
            # print("2d", np.stack([X1, X2], axis=1).shape)
            return poly.fit_transform(np.stack([X1, X2], axis=1))
        else: 
            # print("1d", np.array([X1, X2]).reshape(1,-1).shape)
            return poly.fit_transform(np.array([X1, X2]).reshape(1,-1))

        """

        if X1.ndim > 0:
            out = [np.ones(X1.shape[0], dtype=np.float64)]
        else:
            out = [1]

        for i in range(1, degree + 1):
            for j in range(i + 1):
                out.append((X1 ** (i - j)) * (X2 ** j))

        if X1.ndim > 0:
            return np.stack(out, axis=1, dtype=np.float64)
        else:
            return np.array(out, dtype=np.float64)

    @staticmethod
    def plotDecisionBoundary(X, y, theta, degree=None):
        # make sure theta is a numpy array
        theta = np.array(theta)

        # Plot Data
        Exercise3Utils.plotData(X[:, 1:3], y)

        if X.shape[1] <= 3:
            # Only need 2 points to define a line, so choose two endpoints
            plot_x = np.array([np.min(X[:, 1]), np.max(X[:, 1])])

            # Calculate the decision boundary line
            plot_y = (-1. / theta[2]) * (theta[1] * plot_x + theta[0])

            # Plot, and adjust axes for better viewing
            plt.plot(plot_x, plot_y)

            # Legend, specific for the exercise
            plt.legend(['Admitted', 'Not admitted', 'Decision Boundary'])
            #plt.xlim([1, 100])
            #plt.ylim([1, 100])

        else:
            # Define grid range
            u = np.linspace(-2, 2, 50)
            v = np.linspace(-2, 2, 50)

            z = np.zeros((u.size, v.size))

            # Evaluate z = theta*x over the grid
            for i, ui in enumerate(u):
                for j, vj in enumerate(v):
                    z[i, j] = np.dot(Exercise3Utils.mapFeature(ui, vj, degree), theta)

            # important to transpose z before calling contour
            z = z.T  
            plt.contour(u, v, z, levels=[0], linewidths=2, colors='g')

        plt.tight_layout()


    @staticmethod
    def vis_coef(estimator, feature_names, topn = 10):
        """
        Visualize the top-n most influential coefficients
        for linear models.
        """
        fig = plt.figure(figsize=(8,8))
        feature_names = np.array(feature_names)

        coefs  = estimator.coef_[0]
        sorted_coefs = np.argsort(coefs)
        positive_coefs = sorted_coefs[-topn:]
        negative_coefs = sorted_coefs[:topn]

        top_coefs = np.hstack([negative_coefs, positive_coefs])
        colors = ['r' if c < 0 else 'b' for c in coefs[top_coefs]]
        y_pos = np.arange(2 * topn)
        plt.barh(y_pos, coefs[top_coefs], color = colors, align = 'center')
        plt.yticks(y_pos, feature_names[top_coefs])
        plt.title('top {} positive/negative words'.format(topn))

        plt.tight_layout()


class Exercise4Utils:

    @staticmethod
    def load_data(name):
        # Load data
        data_path = os.path.join(os.path.dirname(__file__), 'datasets', 'exercise4', name)
        return np.loadtxt(data_path, dtype=np.float64)

    @staticmethod
    def load_data_X_y(name, bias = True):
        # Load data
        data_path = os.path.join(os.path.dirname(__file__), 'datasets', 'exercise4', name)
        data = np.loadtxt(data_path, dtype=np.float64)
        
        m,n = data.shape    

        # Create training set x and labels y
        X = data[:, 0:2]
        y = data[:, 2]

        if bias:
            X = np.concatenate([np.ones((m, 1)), X], axis=1)    

        return X, y

    @staticmethod
    def plotData(X, y, grid=False):
        # Find Indices of Positive and Negative Examples
        pos = y == 1
        neg = (y < 1)

        # Plot Examples
        plt.scatter(X[pos][:, 0], X[pos][:, 1], zorder=100, label="1", s=100, edgecolors='black')
        plt.scatter(X[neg][:, 0], X[neg][:, 1], zorder=100, label="0", s=100, edgecolors='black')
  
        plt.grid(grid)


    @staticmethod
    def plotMargin(x, y, w, file, seed, converged, predict) :        
        # Determine the x1- and x2- limits of the plot
        x1min = min(x[:,0]) - 0.5
        x1max = max(x[:,0]) + 0.5
        x2min = min(x[:,1]) - 0.5
        x2max = max(x[:,1]) + 0.5
        
        fig = plt.figure(figsize=(8,6))
        plt.title("Dataset: "+file+", seed="+str(seed)+ ", converged="+str(converged))

        plt.xlim(x1min,x1max)
        plt.ylim(x2min,x2max)
        
        # Plot the data points
        plt.plot(x[(y==1),0], x[(y==1),1], 'ro')
        plt.plot(x[(y==-1),0], x[(y==-1),1], 'k^')
        
        # Construct a grid of points at which to evaluate the classifier
        if converged:
            grid_spacing = 0.02
            xx1, xx2 = np.meshgrid(np.arange(x1min, x1max, grid_spacing), np.arange(x2min, x2max, grid_spacing))
            grid = np.c_[xx1.ravel(), xx2.ravel()]

            Grid = np.concatenate([np.ones((grid.shape[0], 1)), grid], axis=1)        
            Z = np.array([predict(w, pt) for pt in Grid])
            
            # Show the classifier's boundary using a color plot
            Z = Z.reshape(xx1.shape)
            plt.pcolormesh(xx1, xx2, Z, shading='auto', 
                            cmap=plt.cm.PRGn, vmin=-3, vmax=3)
        
        plt.show()

    @staticmethod 
    def display_data_and_boundary(x, y, w, predictMultiClass):
                
        # Determine the x1- and x2- limits of the plot
        x1min = min(x[:,0]) - 1
        x1max = max(x[:,0]) + 1
        x2min = min(x[:,1]) - 1
        x2max = max(x[:,1]) + 1
        plt.xlim(x1min,x1max)
        plt.ylim(x2min,x2max)

        # Plot the data points
        k = int(max(y)) + 1
        cols = ['ro', 'k^', 'b*','gx']
        for label in range(k):
            plt.plot(x[(y==label),0], x[(y==label),1], cols[label%4], markersize=8)
        
        # Construct a grid of points at which to evaluate the classifier
        grid_spacing = 0.05
        xx1, xx2 = np.meshgrid(np.arange(x1min, x1max, grid_spacing), np.arange(x2min, x2max, grid_spacing))
        grid = np.c_[xx1.ravel(), xx2.ravel()]
        
        Grid = np.concatenate([np.ones((grid.shape[0], 1)), grid], axis=1)        
        Z = np.array([predictMultiClass(w,pt) for pt in Grid])    
        #Z = np.array([predictMultiClass(w, pt) for pt in grid])
        
        # Show the classifier's boundary using a color plot
        Z = Z.reshape(xx1.shape)
        plt.pcolormesh(xx1, xx2, Z, shading='auto', cmap=plt.cm.Pastel1, vmin=0, vmax=k)
        # plt.show()


    @staticmethod
    def plot_boundary(X, y, clf):
        # Plot training data
        fig = plt.figure(figsize=(12, 6))
        ax1 = plt.subplot(1, 2, 1)
        ax1.set_title("Raw Data")
        Exercise4Utils.plotData(X, y)

        ax2 = plt.subplot(1, 2, 2)    
        ax2.set_title("RBF Decision Boundary")
        Exercise4Utils.visualizeBoundary(X, y, clf)

        plt.show()


    @staticmethod
    def visualizeBoundary(X, y, clf):
        #fig = plt.figure(figsize=(6,6))
        Exercise4Utils.plotData(X, y)

        h = .025  # step size in the mesh

        # create a mesh to plot in
        x_min, x_max = X[:, 0].min()-h, X[:, 0].max()+h
        y_min, y_max = X[:, 1].min()-h, X[:, 1].max()+h
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

        Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

        # Put the result into a color plot
        Z = Z.reshape(xx.shape)
        plt.contourf(xx, yy, Z, cmap=plt.cm.coolwarm, alpha=0.8)

        plt.xlim(xx.min(), xx.max())
        plt.ylim(yy.min(), yy.max())

        plt.xticks(())
        plt.yticks(())
        plt.grid(True, linestyle='--', alpha=0.5)


    @staticmethod
    def visualizeBoundary3D(X, y, clf, elev=45, azim=-45):
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='3d')
        
        pos = y == 1
        neg = (y < 1)

        # Plot Examples
        ax.scatter(X[pos][:, 0], X[pos][:, 1], 1, zorder=100, s=50, edgecolors='black')
        ax.scatter(X[neg][:, 0], X[neg][:, 1], -1, zorder=100, s=50, edgecolors='black')
        ax.view_init(elev=elev, azim=azim)

        # Create grid to plot decision boundary plane
        x1 = np.linspace(np.min(X[:, 0]), np.max(X[:, 0]), 50)
        x2 = np.linspace(np.min(X[:, 1]), np.max(X[:, 1]), 50)

        # Define grid range        
        xx1, xx2 = np.meshgrid(x1, x2)
        
        zz = np.zeros((x1.size, x2.size))
        for i, ui in enumerate(x1):
            for j, vj in enumerate(x2):
                zz[i, j] = clf.predict(np.c_[ui.ravel(), vj.ravel()])
        zz = zz.T
        

        # Plot the decision boundary plane
        ax.plot_surface(xx1, xx2, zz, color='blue', alpha=0.2)
                
        ax.set_zlabel('$h_w(x)$')
        ax.set_zlim([-1, 1])

        plt.tight_layout()
        # plt.show()  

    @staticmethod
    def plot_train_test(X_train, y_train, X_test, y_test):
        fig = plt.figure(figsize=(10, 5))

        # Plot training data
        ax1=plt.subplot(1, 2, 1)
        ax1.set_title("Train data")
        Exercise4Utils.plotData(X_train, y_train)

        ax1=plt.subplot(1, 2, 2)
        ax1.set_title("Test data")
        Exercise4Utils.plotData(X_test, y_test)
        
        plt.tight_layout()
        plt.show()


    class RBFKernelPerceptron:
        def __init__(self, train_dual_perceptron, sigma=0.1, n_epochs=1000):
            self.sigma = sigma  # RBF kernel parameter        
            self.n_epochs = n_epochs        
            self.train_dual_perceptron = train_dual_perceptron

        def precompute_kernel(self, X1, X2):
            # Compute squared Euclidean distance matrix
            dists = np.sum(X1**2, axis=1)[:, np.newaxis] + np.sum(X2**2, axis=1) - 2 * np.dot(X1, X2.T)
            K_train = np.exp(-dists / (2 * self.sigma ** 2))
            return K_train    
        
        def fit(self, X, y):
            self.X_train = X
            self.y_train = y
            self.y_train[self.y_train == 0] = -1        
            self.K_train = self.precompute_kernel(X, X)

            # Use dual training routine
            self.alpha, converged = self.train_dual_perceptron(self.K_train, self.y_train, seed=1, n_epochs=self.n_epochs)        
            return self
                    
        def predict(self, X):
            K_test = self.precompute_kernel(X, self.X_train)
            return np.sign(K_test @ (self.alpha * self.y_train))



class Exercise5Utils:

    @staticmethod
    def plot_images(X, y):
        fig, axes = plt.subplots(8, 8, figsize=(5,5))
        fig.tight_layout(pad=0.13,rect=[0, 0.03, 1, 0.91]) #[left, bottom, right, top]
        m, n = X.shape

        for i,ax in enumerate(axes.flat):
            # Select random indices
            random_index = np.random.randint(m)
            
            # Select rows corresponding to the random indices and
            # reshape the image
            X_random_reshaped = X[random_index].reshape((28,28))
            
            # Display the image
            ax.imshow(X_random_reshaped, cmap='gray')
            
            # Display the label above the image
            ax.set_title(np.int32(y[random_index]))
            ax.set_axis_off()
            fig.suptitle("Label", fontsize=14)


    @staticmethod    
    def plot_non_linear_decision_boundary(X, y, model, title="Decision Boundary"):
        Exercise3Utils.plotData(X, y)
        
        h = .02  # Step size in the mesh
        x_min, x_max = X[:, 0].min() - 0.1, X[:, 0].max() + 0.1
        y_min, y_max = X[:, 1].min() - 0.1, X[:, 1].max() + 0.1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
        
        # Make predictions on the meshgrid points
        Z = model.predict(np.c_[xx.ravel(), yy.ravel()], verbose=0)
        Z = Z.reshape(xx.shape)
        
        # Plot the contour plot
        plt.contourf(xx, yy, Z, cmap=plt.cm.RdBu, alpha=0.5)
                
        plt.show()      


    @staticmethod    
    def plt_softmax(my_softmax):
        fig, ax = plt.subplots(1,2,figsize=(8,4))
        plt.subplots_adjust(bottom=0.35)

        axz0 = fig.add_axes([0.15, 0.10, 0.30, 0.03]) # [left, bottom, width, height]
        axz1 = fig.add_axes([0.15, 0.15, 0.30, 0.03])
        axz2 = fig.add_axes([0.15, 0.20, 0.30, 0.03])
        axz3 = fig.add_axes([0.15, 0.25, 0.30, 0.03])

        z3 = Slider(axz3, 'z3', 0.1, 10.0, valinit=4, valstep=0.1)
        z2 = Slider(axz2, 'z2', 0.1, 10.0, valinit=3, valstep=0.1)
        z1 = Slider(axz1, 'z1', 0.1, 10.0, valinit=2, valstep=0.1)
        z0 = Slider(axz0, 'z0', 0.1, 10.0, valinit=1, valstep=0.1)

        z = np.array(['z0','z1','z2','z3'])
        bar = ax[0].barh(z, height=0.6, width=[z0.val,z1.val,z2.val,z3.val], left=None, align='center')
        bars = bar.get_children()
        ax[0].set_xlim([0,10])
        ax[0].set_title("z input to softmax")

        a = my_softmax(np.array([z0.val,z1.val,z2.val,z3.val]))
        anames = np.array(['a0','a1','a2','a3'])
        sbar = ax[1].barh(anames, height=0.6, width=a, left=None, align='center',color="#C00000")
        sbars = sbar.get_children()
        ax[1].set_xlim([0,1])
        ax[1].set_title("softmax(z)")

        def update(val):
            bars[0].set_width(z0.val)
            bars[1].set_width(z1.val)
            bars[2].set_width(z2.val)
            bars[3].set_width(z3.val)
            a = my_softmax(np.array([z0.val,z1.val,z2.val,z3.val]))
            sbars[0].set_width(a[0])
            sbars[1].set_width(a[1])
            sbars[2].set_width(a[2])
            sbars[3].set_width(a[3])

            fig.canvas.draw_idle()

        z0.on_changed(update)
        z1.on_changed(update)
        z2.on_changed(update)
        z3.on_changed(update)

    @staticmethod
    def display_images(X_all):
        """
        Displays 2D data stored in X in a nice grid.
        """
        # Randomly select 100 data points to display
        rand_indices = np.random.choice(X_all.shape[0], 100, replace=False)
        X = X_all[rand_indices, :]
        
        # Compute rows, cols
        if X.ndim == 2:
            m, n = X.shape
        elif X.ndim == 1:
            n = X.size
            m = 1
            X = X[None]  # Promote to a 2 dimensional array
        else:
            raise IndexError('Input X should be 1 or 2 dimensional.')

        example_width = int(np.round(np.sqrt(n)))
        example_height = n / example_width

        # Compute number of items to display
        display_rows = int(np.floor(np.sqrt(m)))
        display_cols = int(np.ceil(m / display_rows))

        fig, ax_array = plt.subplots(display_rows, display_cols, figsize=(6, 6))
        # fig.subplots_adjust(wspace=0.025, hspace=0.025)

        ax_array = [ax_array] if m == 1 else ax_array.ravel()

        for i, ax in enumerate(ax_array):
            ax.imshow(X[i].reshape(
                example_width, 
                example_width),
                cmap='Greys', extent=[0, 1, 0, 1])
            ax.axis('off') 


    def load_weights_task1():
        data_path = os.path.join(os.path.dirname(__file__), 'datasets', 'exercise5', 'weights.npz')
        weights = np.load(data_path, allow_pickle = True)
        W1 = weights["W1"]
        b1 = weights["b1"]
        W2 = weights["W2"]
        b2 = weights["b2"]   
        return W1, b1, W2, b2