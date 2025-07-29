import mlflow
import pandas as pd
from autogluon.tabular import TabularPredictor


# PyFunc Wrapper for AutoGluon
class AutoGluonTabularPyFuncWrapper(mlflow.pyfunc.PythonModel):

    def __init__(self):
        self.predictor = None
        self.model_name = None

    def load_context(self, context):
        self.predictor = TabularPredictor.load(context.artifacts["autogluon_model_dir"])

    def predict(self, context, model_input):
        if isinstance(model_input, pd.DataFrame):
            return self.predictor.predict(model_input)
        else:
            return self.predictor.predict(pd.DataFrame(model_input))
