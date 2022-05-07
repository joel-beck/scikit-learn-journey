#%%
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.experimental import enable_halving_search_cv
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from sklearn.model_selection import HalvingRandomSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

from sklearn_helpers import ClassificationMetrics, MetricsComparison

#%%
# SUBSECTION: Configuration Parameters
DATA_PATH = "https://raw.githubusercontent.com/mrdbourke/zero-to-mastery-ml/master/data/heart-disease.csv"
TARGET_COL = "target"

#%%

# SUBSECTION: Setup Data
data = pd.read_csv(DATA_PATH)
data.head()

#%%
X = data.drop(columns=[TARGET_COL])
y = data[TARGET_COL]

X_train, X_test, y_train, y_test = train_test_split(X, y)
X_train.shape, X_test.shape

#%%
# SUBSECTION: Preprocessing
scaler = StandardScaler()
encoder = OneHotEncoder(handle_unknown="ignore")

column_transformer = ColumnTransformer(
    [
        ("scaler", scaler, make_column_selector(dtype_include="number")),
        ("encoder", encoder, make_column_selector(dtype_include="object")),
    ],
)

#%%
# SUBSECTION: Modeling
# BOOKMARK: Random Forest
random_forest = RandomForestClassifier()
pipe_rf = Pipeline([("preprocessor", column_transformer), ("clf", random_forest)])
param_grid_rf = {"clf__n_estimators": range(10, 110, 10)}
cv_rf = HalvingRandomSearchCV(pipe_rf, param_distributions=param_grid_rf)
cv_rf.fit(X_train, y_train)

#%%
print(cv_rf.best_params_)

#%%
print(cv_rf.best_score_)

#%%
print(cv_rf.best_estimator_)

#%%
pd.DataFrame(cv_rf.cv_results_)

#%%
# BOOKMARK: HistGradientBoosting
gradient_boosting = HistGradientBoostingClassifier()
pipe_gb = Pipeline([("preprocessor", column_transformer), ("clf", gradient_boosting)])
param_grid_gb = {"clf__max_depth": range(1, 6)}
cv_gb = HalvingRandomSearchCV(pipe_gb, param_distributions=param_grid_gb)
cv_gb.fit(X_train, y_train)

#%%
# BOOKMARK: XGBoost
xgboost = XGBClassifier()
pipe_xgb = Pipeline([("preprocessor", column_transformer), ("clf", xgboost)])
param_grid_xgb = {"clf__max_depth": range(1, 6)}
cv_xgb = HalvingRandomSearchCV(pipe_xgb, param_distributions=param_grid_xgb)
cv_xgb.fit(X_train, y_train)

#%%
# BOOKMARK: LightGBM
lightgbm = LGBMClassifier()
pipe_lgbm = Pipeline([("preprocessor", column_transformer), ("clf", lightgbm)])
param_grid_lgbm = {"clf__max_depth": range(1, 6)}
cv_lgbm = HalvingRandomSearchCV(pipe_lgbm, param_distributions=param_grid_lgbm)
cv_lgbm.fit(X_train, y_train)

#%%
# SUBSECTION: Evaluation
# two ways to compute accuracy on test set:
# 1. cv.score(X_test, y_test)
# 2. accuracy_score(y_test, y_pred) with y_pred = cv.best_estimator_.predict(X_test)
for cv in [cv_rf, cv_gb, cv_xgb, cv_lgbm]:
    print(
        f"Accuracy {cv.best_estimator_['clf'].__class__.__name__}: {cv.score(X_test, y_test):.2f}"
    )

#%%
y_pred_rf = cv_rf.best_estimator_.predict(X_test)
rf_metrics = ClassificationMetrics(y_test, y_pred_rf)
rf_metrics

y_pred_gb = cv_gb.best_estimator_.predict(X_test)
gb_metrics = ClassificationMetrics(y_test, y_pred_gb)
gb_metrics

y_pred_xgb = cv_xgb.best_estimator_.predict(X_test)
xgb_metrics = ClassificationMetrics(y_test, y_pred_xgb)
xgb_metrics

y_pred_lgbm = cv_lgbm.best_estimator_.predict(X_test)
lgbm_metrics = ClassificationMetrics(y_test, y_pred_lgbm)
lgbm_metrics

#%%
sns.set_theme(style="white")
print(confusion_matrix(y_test, y_pred_rf))

ConfusionMatrixDisplay.from_predictions(y_test, y_pred_rf)
plt.show()

sns.set_theme(style="whitegrid")

#%%
metrics_comparison = MetricsComparison(
    [rf_metrics, gb_metrics, xgb_metrics, lgbm_metrics],
    ["Random Forest", "HistGradientBoosting", "XGBoost", "LightGBM"],
    lower_bound=0.7,
    marker_size=10,
)
metrics_comparison.to_df()

#%%
metrics_comparison.barplot()

#%%
metrics_comparison.stripplot()

#%%
