# Random Forest Regression

# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Importing the dataset
dataset = pd.read_csv('apartments.csv')
lat_X = dataset.iloc[:, 5:6].values
lng_X = dataset.iloc[:, 6:7].values

plt.scatter(lat_X, lng_X, color='red')
plt.title("Location of Apartment Listings")
plt.xlabel("Latitude")
plt.ylabel("Longitude")
plt.gca().invert_yaxis()
plt.show()