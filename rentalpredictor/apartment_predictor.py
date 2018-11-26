# -*- coding: utf-8 -*-
"""
apartment_predictor.py

Creates model to predict appropriate rental price for an apartment property in
Vancouver, Canada

"""

import numpy as np
import pandas as pd
import math
import pickle
import glob
import os
from sklearn.preprocessing import Imputer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Create export directory if not already created
EXPORT_DIR='./models/'
if not os.path.exists(EXPORT_DIR):
    os.mkdir(EXPORT_DIR)
     
# Iterate through each csv file with raw data
for filepath in glob.glob('../data/export_processed/*.csv'):
    print(filepath)


    """ 
    Import the dataset
    """
    dataset = pd.read_csv(filepath)
    # Matrix of features: 
    #   sqft, furnished, laundry, bedrooms, bathrooms, stop_distance
    X = dataset.iloc[:, [5,6,7,8,9,12]].values
    # Dependent variable: 
    #   price
    y = dataset.iloc[:, 0].values
    
    
    """
    Handle missing data
    """
    # sqft - fill with mean of all property's sqft
    imputer_mean = Imputer(missing_values = 'NaN', strategy = 'mean', axis = 0)
    imputer_mean = imputer_mean.fit(X[:, [0]])
    X[:, [0]] = imputer_mean.transform(X[:, [0]])
    # bedroom/bathroom:
    # Fill NaN with 1 because we deduce that missing BR/Ba data most likely means
    # the property has 1 bedroom and 1 bathroom
    X[:, 3] = [1 if math.isnan(x) else x for x in X[:, 3]]
    X[:, 4] = [1 if math.isnan(x) else x for x in X[:, 4]]
    # stop_distance:
    # Fill NaN with 2000 because 2000 is the max radius of stop distance
    # retrieved from TransLink API.
    X[:, 5] = [2000 if math.isnan(x) else x for x in X[:, 5]]
    
    
    """
    Split dataset into training and test set
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25)
    
    
    """
    Fit Multiple Linear Regression to the training set
    """
    regressor = LinearRegression()
    regressor.fit(X_train, y_train)
    
    # Get file name
    filename = filepath.rsplit("/", 1)[1]
    filename = os.path.splitext(filename)[0]

    # Serialize model to a export directory with file name
    pickle.dump(regressor, open(EXPORT_DIR + filename + ".pkl", "wb"))
    
    
    """
    Predicting test set resultsz
    """
    y_pred = regressor.predict(X_test)
    
    
    """
    Applying k-Fold Cross Validation
    """
    from sklearn.model_selection import cross_val_score
    accuracies = cross_val_score(estimator = regressor,
                                 X = X_train,
                                 y = y_train,
                                 cv = 10)
    
    import statsmodels.formula.api as sm
    X = np.append(arr = np.ones((X[:, [0]].size, 1)).astype(int),
                  values = X,
                  axis = 1)
    X_opt = X[:, [0,1,2,3,4,5]]
    regressor_OLS = sm.OLS(endog = y, exog = X_opt).fit()
    regressor_OLS.summary()
