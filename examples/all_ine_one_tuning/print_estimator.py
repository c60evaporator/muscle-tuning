# %% AllInOneTuning, binary, no argument, print_estimator
import parent_import
from tune_easy import AllInOneTuning
import seaborn as sns
# Load dataset
iris = sns.load_dataset("iris")
iris = iris[iris['species'] != 'setosa']  # Only 2 class
TARGET_VARIALBLE = 'species'  # Target variable name
USE_EXPLANATORY = ['petal_width', 'petal_length', 'sepal_width', 'sepal_length']  # Selected explanatory variables
y = iris[TARGET_VARIALBLE].values
X = iris[USE_EXPLANATORY].values
# Run parameter tuning
all_tuner = AllInOneTuning()
all_tuner.all_in_one_tuning(X, y, x_colnames=USE_EXPLANATORY)
# Print estimator
all_tuner.print_estimator('randomforest', 'randomforest estimator')

# %% AllInOneTuning, multiclass, no argument, print_estimator
import parent_import
from tune_easy import AllInOneTuning
import seaborn as sns
# Load dataset
iris = sns.load_dataset("iris")
TARGET_VARIALBLE = 'species'  # Target variable name
USE_EXPLANATORY = ['petal_width', 'petal_length', 'sepal_width', 'sepal_length']  # Selected explanatory variables
y = iris[TARGET_VARIALBLE].values
X = iris[USE_EXPLANATORY].values
# Run parameter tuning
all_tuner = AllInOneTuning()
all_tuner.all_in_one_tuning(X, y, x_colnames=USE_EXPLANATORY)
# Print estimator
all_tuner.print_estimator('randomforest', 'randomforest estimator')

# %% AllInOneTuning, regression, no argument, print_estimator
import parent_import
from tune_easy import AllInOneTuning
from sklearn.datasets import fetch_california_housing
import pandas as pd
import numpy as np
# Load dataset
TARGET_VARIALBLE = 'price'  # Objective variable name
USE_EXPLANATORY = ['MedInc', 'AveOccup', 'Latitude', 'HouseAge']  # Selected explanatory variables
california_housing = pd.DataFrame(np.column_stack((fetch_california_housing().data, fetch_california_housing().target)),
        columns = np.append(fetch_california_housing().feature_names, TARGET_VARIALBLE))
california_housing = california_housing.sample(n=1000, random_state=42)  # sampling from 20640 to 1000
y = california_housing[TARGET_VARIALBLE].values  # Explanatory variables
X = california_housing[USE_EXPLANATORY].values  # Objective variable
# Run parameter tuning
all_tuner = AllInOneTuning()
all_tuner.all_in_one_tuning(X, y, x_colnames=USE_EXPLANATORY)
# Print estimator
all_tuner.print_estimator('svr', 'svr estimator')