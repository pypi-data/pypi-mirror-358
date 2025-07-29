import mlflow
from autogluon.tabular import TabularPredictor
import tempfile
import os
from optuna import artifacts
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import json
from wedata_autogluon.autogluon_wrapper import AutoGluonTabularPyFuncWrapper

class WeDataH2oClassification:
    """
    H2O TabularPredictor 的 wedata 风格包装器，支持所有主流参数，并集成 MLflow 日志。

    参数说明见 fit 方法。
    """

    def __init__(
        self,
        label: str,
        problem_type: str = None,
        eval_metric=None,
        path=None,
        verbosity: int = 4,
        log_to_file: bool = True,
        log_file_path: str = "auto",
        sample_weight: str = None,
        weight_evaluation: bool = False,
        groups: str = None,
        positive_class=None,
        **kwargs
    ):
        """
        参数
        ----------
        label : str
            目标变量所在列的名称。
        problem_type : str, optional
            预测问题类型（'binary', 'multiclass', 'regression', 'quantile'），默认自动推断。
        eval_metric : str or Scorer, optional
            评估指标，默认根据 problem_type 自动选择。
        path : str or Path, optional
            模型保存路径，默认自动生成。
        verbosity : int, default=2
            日志详细程度，0-4。
        log_to_file : bool, default=False
            是否将日志保存到文件。
        log_file_path : str, default="auto"
            日志文件路径。
        sample_weight : str, optional
            样本权重列名。
        weight_evaluation : bool, default=False
            验证/测试时是否考虑样本权重。
        groups : str, optional
            分组列名（bagging 时用）。
        positive_class : str or int, optional
            二分类正类。
        kwargs : dict
            其他 TabularPredictor 支持的参数。
        """
        self.label = label
        self.problem_type = problem_type
        self.eval_metric = eval_metric
        self.path = path
        self.verbosity = verbosity
        self.log_to_file = log_to_file
        self.log_file_path = log_file_path
        self.sample_weight = sample_weight
        self.weight_evaluation = weight_evaluation
        self.groups = groups
        self.positive_class = positive_class
        self.kwargs = kwargs
        self.predictor = None
        self.tmpdir = None

        if self.path is None:
            self.tmpdir = tempfile.TemporaryDirectory()
            path = self.tmpdir.name
        else:
            path = self.path
        self.path = path
        self.predictor = TabularPredictor(
            label=self.label,
            problem_type=self.problem_type,
            eval_metric=self.eval_metric,
            path=path,
            verbosity=self.verbosity,
            log_to_file=self.log_to_file,
            log_file_path=self.log_file_path,
            sample_weight=self.sample_weight,
            weight_evaluation=self.weight_evaluation,
            groups=self.groups,
            positive_class=self.positive_class,
            **self.kwargs
        )

    def fit(self, train_data, tuning_data=None, hyperparameters=None, time_limit=None, presets=None, **fit_kwargs):
        """
        训练模型。

        参数
        ----------
        train_data : pd.DataFrame
            训练数据。
        tuning_data : pd.DataFrame, optional
            验证集。
        time_limit : int, optional
            训练时间限制（秒）。
        presets : str, optional
            训练预设（如 'best_quality'）。
        fit_kwargs : dict
            其他 fit 支持的参数。
        """


        self.predictor.fit(
            train_data=train_data,
            tuning_data=tuning_data,
            hyperparameters=hyperparameters,
            time_limit=time_limit,
            presets=presets,
            **fit_kwargs
        )

    def evaluate(self, test_data):
        if self.predictor is None:
            raise Exception("Model not fitted yet!")
        return self.predictor.evaluate(test_data)

    def log_to_mlflow(self, experiment_name = "default", run_name = "defalue", test_data = None):
        if self.predictor is None:
            raise Exception("Model not fitted yet!")

        mlflow.set_experiment(experiment_name)
        experiment = mlflow.get_experiment_by_name(experiment_name)
        experiment_id = experiment.experiment_id

        with mlflow.start_run(run_name=run_name, experiment_id=experiment_id) as parent_run:
            leaderboard = None
            # 记录整体 leaderboard
            if test_data is not None:
                leaderboard = self.predictor.leaderboard(test_data, silent=True)
            else:
                leaderboard = self.predictor.leaderboard()
            leaderboard_path = os.path.join(self.predictor.path, "leaderboard.csv")
            leaderboard.to_csv(leaderboard_path, index=False)
            mlflow.log_artifact(leaderboard_path)
            info = self.predictor.info()

            # 遍历所有子模型
            for model_name in self.predictor.model_names():

                models_info = info['model_info']
                params = models_info[model_name]['hyperparameters']
                score_val = models_info[model_name]['val_score']
                model_type = models_info[model_name]['model_type']
                fit_time = models_info[model_name]['fit_time']
                predict_time = models_info[model_name]['predict_time']
                memory_size = models_info[model_name]['memory_size']
                ag_args_fit = models_info[model_name]['ag_args_fit']


                with mlflow.start_run(run_name=model_name, experiment_id=experiment_id, nested=True):
                    mlflow.log_param("model_name", model_name)
                    mlflow.log_param("model_type", model_type)
                    for k, v in params.items():
                        mlflow.log_param(f"hyperparameters_{k}", v)
                    for k, v in ag_args_fit.items():
                        mlflow.log_param(f"autogluon_args_fig_{k}", v)
                    mlflow.log_metric("val_score", score_val)
                    mlflow.log_metric("fit_time", fit_time)
                    mlflow.log_metric("predict_time", predict_time)
                    mlflow.log_metric("memory_size", memory_size)

                    mlflow.pyfunc.log_model(
                        artifact_path="model",
                        python_model=AutoGluonTabularPyFuncWrapper(),
                        artifacts={"autogluon_model_dir": self.path},
                    )

            # 记录整体参数和最佳模型性能
            mlflow.log_param("label", self.label)
            mlflow.log_param("problem_type", self.problem_type)
            mlflow.log_param("eval_metric", self.eval_metric)
            mlflow.log_param("path", self.path)
            mlflow.log_param("verbosity", self.verbosity)
            mlflow.log_param("log_to_file", self.log_to_file)
            mlflow.log_param("log_file_path", self.log_file_path)
            mlflow.log_param("sample_weight", self.sample_weight)
            mlflow.log_param("weight_evaluation", self.weight_evaluation)
            mlflow.log_param("groups", self.groups)
            mlflow.log_param("positive_class", self.positive_class)
            for k, v in self.kwargs.items():
                mlflow.log_param(k, v)

            best_model = self.predictor.model_best

            mlflow.log_param("best_model", best_model)


    def __del__(self):
        if self.tmpdir is not None:
            self.tmpdir.cleanup()
