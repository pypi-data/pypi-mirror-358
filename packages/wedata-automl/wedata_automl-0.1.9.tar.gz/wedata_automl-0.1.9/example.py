import numpy as np
from wedata.ts_automl.flaml import WeDataTimeSeriesAutoML
import mlflow
import flaml
from flaml import AutoML
mlflow.set_tracking_uri("http://9.134.212.179:5000")
# 构造时序数据
X_train = np.arange("2014-01", "2022-01", dtype="datetime64[M]")
y_train = np.random.random(size=84)
# WeDataTimeSeriesAutoML 训练设置：最大训练时间为 60s，评价指标为 acc，每个 Executor 的并行度为 2，开启强制取消（开启后，超过最大训练时间后将立即停止）
automl_settings = {
    "time_budget": 10,
    "metric": 'accuracy',
    "n_concurrent_trials": 1,
    "use_spark": True,
    "force_cancel": False,  # Activating the force_cancel option can immediately halt Spark jobs once they exceed the allocated time_budget.
}
automl = WeDataTimeSeriesAutoML(settings=automl_settings)
mlflow.set_experiment("wedata_demo")

# 开始训练，请设置 mlflow 实验名和任务名，训练中将同步记录模型参数到实验管理，同时记录最优模型制品
automl.fit(
    X_train=X_train[:84],  # a single column of timestamp
    y_train=y_train,  # value for each timestamp
    period=12,  # time horizon to forecast, e.g., 12 months
    task="ts_forecast",
    log_file_name="ts_forecast.log",
    eval_method="holdout",
    use_spark=True
)
