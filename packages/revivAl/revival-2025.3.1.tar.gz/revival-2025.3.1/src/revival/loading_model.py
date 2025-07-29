# Copyright MewsLabs 2025
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


import json
import os

import h5py
import pandas as pd

from revival import LiteModel
from utils.utils import deserialize_model
from sklearn.multioutput import MultiOutputClassifier, MultiOutputRegressor


def load_model(path: str, file_name: str) -> LiteModel:
    """Function that loads a trained model and its data from a hdf5 file.
    Parameters:
    ----------
    path: str
        the path where the file is saved
    file_name: str
        the name of the file where the model is saved
    """
    file_path = os.path.join(path, f"{file_name}.h5")
    with h5py.File(file_path, "r") as f:
        if "X_train" in f:
            X_data = f["X_train"][()]
            if "X_train_columns" in f and "X_train_index" in f:
                columns = [col.decode("utf-8") for col in f["X_train_columns"][()]]
                index = [idx.decode("utf-8") for idx in f["X_train_index"][()]]
                _X_train = pd.DataFrame(X_data, columns=columns, index=index)
            else:
                _X_train = X_data
        if "y_train" in f:
            y_data = f["y_train"][()]
            if "y_train_columns" in f and "y_train_index" in f:
                columns = [col.decode("utf-8") for col in f["y_train_columns"][()]]
                index = [idx.decode("utf-8") for idx in f["y_train_index"][()]]
                _y_train = pd.DataFrame(y_data, columns=columns, index=index)
            else:
                _y_train = y_data

        prediction = f["y_predict"][()] if "y_predict" in f else None
        score = f.attrs.get("score")
        # Load model bytes and metadata
        model_data = bytes(f["model_data"][()])
        model_meta = f["model_meta"]
        multi = model_meta.attrs["is_multi"]
        library = json.loads(model_meta.attrs["library"])
        lib_name = next(iter(library.keys()))
        model_class = (
            model_meta.attrs["estimator_class"]
            if model_meta.attrs.get("is_multi", False)
            else model_meta.attrs["model_class"]
        )
        lib_name = next(iter(json.loads(model_meta.attrs["library"]).keys()))
        lib_name_classe = next(
            iter(json.loads(model_meta.attrs["lib_name_class"]).keys())
        )
        wrapp = None
        cls_name = model_class.split(".")[-1]
        if multi:
            if "wrapper_class" in model_meta.attrs:
                wrapp = model_meta.attrs['wrapper_class']

            if "estimator_params" in model_meta.attrs:
                est_params = json.loads(model_meta.attrs["estimator_params"])
            if "wrapper_params" in model_meta.attrs:
                wrapp_params = json.loads(model_meta.attrs["wrapper_params"])
        else:
            if "params" in model_meta.attrs:
                est_params = model_meta.attrs["params"]
        try:
            _model = deserialize_model(model_data, lib_name, cls_name)
        except:
            _model = create_model_refit(lib_name_classe, cls_name, est_params , multi, wrapp)
            _model.train()

    print(f"Full model loaded from {file_path}")
    litemodel = LiteModel(X_train=_X_train, y_train=_y_train, model=_model)
    litemodel.score = score
    litemodel.est_params = est_params
    litemodel.wrapp_params = wrapp_params if multi else None
    litemodel.lib_name = lib_name
    litemodel.lib_name_classe = lib_name_classe
    litemodel.cls_name = cls_name
    litemodel._is_multi = multi
    litemodel.prediction = prediction
    return litemodel

def create_model_refit(lib_name_classe, cls_name, est_params , multi, wrapp = None):
    import importlib
    est_params = json.loads(est_params)
    module = importlib.import_module(lib_name_classe)
    ModelClass = getattr(module, cls_name)
    if multi and isinstance(wrapp, MultiOutputClassifier):
        _model = MultiOutputClassifier(ModelClass(**est_params))
    elif multi and not isinstance(wrapp, MultiOutputRegressor):
        _model = MultiOutputRegressor(ModelClass(**est_params))
    else:
        print(type(est_params))
        print("creating model")
        _model = ModelClass(**est_params)
    return _model