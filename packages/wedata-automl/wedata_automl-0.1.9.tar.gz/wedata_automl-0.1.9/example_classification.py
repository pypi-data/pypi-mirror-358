import mlflow
import mlflow.pyfunc
from autogluon.tabular import TabularPredictor
from sklearn.datasets import fetch_california_housing
import pandas as pd
import tempfile
import os

from wedata_autogluon.classification import WeDataAutoGluonClassification
from  wedata_autogluon.regressor import WeDataAutoGluonRegressor
from wedata_autogluon.autogluon_wrapper import AutoGluonTabularPyFuncWrapper
import mlflow
import pandas as pd
from autogluon.tabular import TabularPredictor
from sklearn import datasets

# 1. 加载数据
iris = datasets.load_iris()
X = pd.DataFrame(iris.data, columns=iris.feature_names)
y = pd.Series(iris.target, name='target')
data = pd.concat([X, y], axis=1)


mlflow.set_tracking_uri("http://9.134.212.179:5000")

label = 'target'
with tempfile.TemporaryDirectory() as tmpdir:
    wedata_autogluon = WeDataAutoGluonClassification(label=label, path=tmpdir)
    wedata_autogluon.fit(train_data=data,
                         test_data=None,
    presets='medium_quality',
    verbosity=4,
    num_cpus=4)
    wedata_autogluon.log_to_mlflow(experiment_name="test_wedata_autogluon_3", test_data=None)
    wedata_autogluon.__del__()

# # 2. 指定 run_id
# run_id = "e6c1c2083df24a7ca279e6d4211b2393"  # 替换为实际的 run_id
# logged_model = f"runs:/{run_id}/model"
#
# # 3. 加载模型
# model = mlflow.pyfunc.load_model(logged_model)
#
# # 4. 准备测试数据
# data = fetch_california_housing(as_frame=True)
# df = data.frame
# X = df.drop(columns=["MedHouseVal"])
# X_sample = X.iloc[:5]  # 取前5行做预测
#
# # 5. 预测
# preds = model.predict(X_sample)
# print("预测结果：")
# print(preds)