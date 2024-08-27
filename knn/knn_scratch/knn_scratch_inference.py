"""
This code performs the following tasks:
1. Loads a dataset from a CSV file and preprocesses the data.
2. Splits the data into training and testing sets.
3. Scales the numerical features in the data.
4. Trains a k-nearest neighbors (KNN) classifier on the training data.
5. Defines a function to predict whether a customer will purchase a product based on their age and estimated salary.

The code uses the pandas, numpy, and scikit-learn libraries to load and preprocess the data, and the KNN classifier from a custom module called `knn_scratch`. It also includes code to visualize the data using matplotlib.
"""
import pandas as pd
import numpy as np
from knn_scratch import KNN
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Load the dataset from a CSV file and preprocess the data.
df = pd.read_csv("../Social_Network_Ads.csv")
# Sample 3 rows from the dataframe for inspection
df.sample(3)

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111)

# Define marker styles for different genders
markers = {'Male': 'o', 'Female': '*'}  # 'o' for circles, 's' for squares

# Initialize a list to store scatter plots
scatter_plots = []

# Plot each gender separately
for gender, marker in markers.items():
    subset = df[df['Gender'] == gender]
    scatter = ax.scatter(subset['Age'], subset['EstimatedSalary'], c=subset['Purchased'], cmap='viridis', 
                        marker=marker, label=gender, s=70)  # s parameter adjusts the point size
    scatter_plots.append(scatter)  # Add scatter plot to the list

# Add color bar based on the last scatter plot
cbar = plt.colorbar(scatter_plots[-1], ax=ax, label='Purchased')

# Labels
ax.set_xlabel('Age')
ax.set_ylabel('EstimatedSalary')

# Add legend
ax.legend(title='Gender')
plt.show()



X = df.iloc[:, 2:4].values
# print(type(X), X.shape)

y = df.iloc[:, -1].values
# print(type(y), y.shape)

xtrain, xtest, ytrain, ytest = train_test_split(X, y, test_size = .2, random_state=0)
# print(xtrain.shape)
# print(xtest.shape)
# print(ytrain.shape)
# print(ytest.shape)


scaler = StandardScaler()
columns_to_scale = [1, 2]

xtrain = scaler.fit_transform(xtrain)
xtest = scaler.fit_transform(xtest)

# Initialize a Custom KNN Object
knn = KNN(5)
knn.fit(xtrain, ytrain)

def predict(age, salary):
    # Predicts whether a customer will purchase a product based on their age and estimated salary.
    
    # Args:
    #     age (int): The age of the customer.
    #     salary (float): The estimated salary of the customer.
    
    # Returns:
    #     str: A string indicating whether the customer will purchase the product ("Will Purchase") or not ("will Not Purchase").
    
    input = np.array([[age], [salary]]).reshape(1, 2)
    input_scaled = scaler.transform(input)
    result = knn.predict(input_scaled)

    return "Will Purchase" if result else "Will Not Purchase"

print(predict(25, 5000))
print(predict(40, 500001))
