# %% LGBMClassifier, GridSearch, no argument
import parent_import
from muscle_tuning import LGBMClassifierTuning
import seaborn as sns
iris = sns.load_dataset("iris")
TARGET_VARIALBLE = 'species'  # 目的変数
USE_EXPLANATORY = ['petal_width', 'petal_length', 'sepal_width', 'sepal_length']  # 説明変数
y = iris[TARGET_VARIALBLE].values
X = iris[USE_EXPLANATORY].values
tuning = LGBMClassifierTuning(X, y, USE_EXPLANATORY, y_colname=TARGET_VARIALBLE)
tuning.plot_first_validation_curve()
tuning.grid_search_tuning()
tuning.plot_search_history()
tuning.plot_search_map()
tuning.plot_best_learning_curve()
tuning.plot_best_validation_curve()
tuning.plot_param_importances()

# %% LGBMClassifier, RandomSearch, no argument
import parent_import
from muscle_tuning import LGBMClassifierTuning
import seaborn as sns
iris = sns.load_dataset("iris")
TARGET_VARIALBLE = 'species'  # 目的変数
USE_EXPLANATORY = ['petal_width', 'petal_length', 'sepal_width', 'sepal_length']  # 説明変数
y = iris[TARGET_VARIALBLE].values
X = iris[USE_EXPLANATORY].values
tuning = LGBMClassifierTuning(X, y, USE_EXPLANATORY, y_colname=TARGET_VARIALBLE)
tuning.random_search_tuning()
tuning.plot_search_history()
tuning.plot_search_map()
tuning.plot_best_learning_curve()
tuning.plot_best_validation_curve()
tuning.plot_param_importances()

# %% LGBMClassifier, BayesianOptimization, no argument
import parent_import
from muscle_tuning import LGBMClassifierTuning
import seaborn as sns
iris = sns.load_dataset("iris")
TARGET_VARIALBLE = 'species'  # 目的変数
USE_EXPLANATORY = ['petal_width', 'petal_length', 'sepal_width', 'sepal_length']  # 説明変数
y = iris[TARGET_VARIALBLE].values
X = iris[USE_EXPLANATORY].values
tuning = LGBMClassifierTuning(X, y, USE_EXPLANATORY, y_colname=TARGET_VARIALBLE)
tuning.bayes_opt_tuning()
tuning.plot_search_history()
tuning.plot_search_map()
tuning.plot_best_learning_curve()
tuning.plot_best_validation_curve()
tuning.plot_param_importances()

# %% LGBMClassifier, Optuna, no argument
import parent_import
from muscle_tuning import LGBMClassifierTuning
import seaborn as sns
iris = sns.load_dataset("iris")
TARGET_VARIALBLE = 'species'  # 目的変数
USE_EXPLANATORY = ['petal_width', 'petal_length', 'sepal_width', 'sepal_length']  # 説明変数
y = iris[TARGET_VARIALBLE].values
X = iris[USE_EXPLANATORY].values
tuning = LGBMClassifierTuning(X, y, USE_EXPLANATORY, y_colname=TARGET_VARIALBLE)
tuning.optuna_tuning()
tuning.plot_search_history()
tuning.plot_search_map()
tuning.plot_best_learning_curve()
tuning.plot_best_validation_curve()
tuning.plot_param_importances()