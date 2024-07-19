# adapted from https://www.kaggle.com/code/anapedralpez/time-series-forecasting-with-xgbregressor
# see also for slices, loc, index

import pandas as pd

START: int = input()
END: int = input()

df: pd.DataFrame = pd.read_csv("...")
# STATE: END -> U; START -> U; df -> {_ -> U}; i -> W; j -> {_ -> W}; k -> {_ -> W}; metric -> {_ -> W}; performance -> {_ -> W}; res -> {_ -> W}; val_performance -> {_ -> W}; y -> {_ -> W}; y_fit -> {_ -> W}; y_pred -> {_ -> W}; y_train -> {_ -> W}; y_valid -> {_ -> W}
y: pd.DataFrame = df.loc[START:END]


print(y)
y_train: pd.DataFrame = y["2017-07-01"]
y_valid: pd.DataFrame = y["2017-07-02"]

# y_fit = pd.DataFrame(model_linear.predict(X1_train), index=X1_train.index, columns=y_train.columns)
y_fit: pd.DataFrame = pd.read_csv("...")
# y_pred = pd.DataFrame(model_linear.predict(X1_valid), index=X1_valid.index, columns=y_valid.columns)
y_pred: pd.DataFrame = pd.read_csv("...")

val_performance: pd.DataFrame = pd.read_csv()
performance: pd.DataFrame = pd.read_csv()

# Record performance:
# i: int = input()
# res: pd.DataFrame = pd.read_csv("...")
# if i == 0:
#     val_performance: pd.DataFrame = pd.concat([val_performance, res])
# else:
#     performance: pd.DataFrame = pd.concat([performance, res])
# 
# performance.head()


# STATE: END -> N; START -> N; df -> {_ -> N}; i -> W; j -> {_ -> W}; k -> {_ -> W}; metric -> {_ -> W}; performance -> {_ -> U}; res -> {_ -> W}; val_performance -> {_ -> U}; y -> {_ -> N}; y_fit -> {_ -> U}; y_pred -> {_ -> U}; y_train -> {_ -> U}; y_valid -> {_ -> U}
i: int = 0
j: pd.DataFrame = y_train
k: pd.DataFrame = y_fit
metric : pd.DataFrame = pd.read_csv()
metric['MAE'] : pd.Series = mean_absolute_error(j, k)
metric['MSE'] = mean_squared_error(j, k)
metric['RMSE'] = sqrt(mean_squared_error(j, k))
metric['R2'] = r2_score(j, k)
res: pd.DataFrame = metric
# STATE: END -> N; START -> N; df -> {_ -> N}; i -> U; j -> {_ -> W}; k -> {_ -> W}; metric -> {_ -> W}; performance -> {_ -> U}; res -> {(index) -> W, _ -> U}; val_performance -> {_ -> U}; y -> {_ -> N}; y_fit -> {_ -> N}; y_pred -> {_ -> U}; y_train -> {_ -> N}; y_valid -> {_ -> U}
res.index = ['Classic_Linear']
print(res)
if i == 0:
    val_performance = pd.concat([val_performance, res])
else:
    performance = pd.concat([performance, res])


i = 1
j = y_valid
k = y_pred
metric = pd.read_csv()
# STATE: END -> N; START -> N; df -> {_ -> N}; i -> U; j -> {_ -> U}; k -> {_ -> U}; metric -> {MAE -> W, MSE -> W, R2 -> W, RMSE -> W, _ -> U}; performance -> {_ -> U}; res -> {_ -> W}; val_performance -> {_ -> U}; y -> {_ -> N}; y_fit -> {_ -> N}; y_pred -> {_ -> N}; y_train -> {_ -> N}; y_valid -> {_ -> N}
metric['MAE'] : pd.Series = mean_absolute_error(j, k)
metric['MSE'] = mean_squared_error(j, k)
metric['RMSE'] = sqrt(mean_squared_error(j, k))
metric['R2'] = r2_score(j, k)
res: pd.DataFrame = metric
# STATE: END -> N; START -> N; df -> {_ -> N}; i -> U; j -> {_ -> N}; k -> {_ -> N}; metric -> {_ -> N}; performance -> {_ -> U}; res -> {(index) -> W, _ -> U}; val_performance -> {_ -> U}; y -> {_ -> N}; y_fit -> {_ -> N}; y_pred -> {_ -> N}; y_train -> {_ -> N}; y_valid -> {_ -> N}
res.index = ['Classic_Linear']
print(res)
if i == 0:
    val_performance = pd.concat([val_performance, res])
else:
    performance = pd.concat([performance, res])

# STATE: END -> N; START -> N; df -> {_ -> N}; i -> N; j -> {_ -> N}; k -> {_ -> N}; metric -> {_ -> N}; performance -> {_ -> U}; res -> {_ -> N}; val_performance -> {_ -> U}; y -> {_ -> N}; y_fit -> {_ -> N}; y_pred -> {_ -> N}; y_train -> {_ -> N}; y_valid -> {_ -> N}
performance.head()
print(val_performance.head())

# FINAL: END -> N; START -> N; df -> {_ -> N}; i -> N; j -> {_ -> N}; k -> {_ -> N}; metric -> {_ -> N}; performance -> {_ -> N}; res -> {_ -> N}; val_performance -> {_ -> N}; y -> {_ -> N}; y_fit -> {_ -> N}; y_pred -> {_ -> N}; y_train -> {_ -> N}; y_valid -> {_ -> N}
