"""
Main API class

the way I want it to work :

app = LeCrapaud()

kwargs = {

}

experiment = app.create_experiment(**kwargs) # return a class Experiment()
ou
experiment = app.get_experiment(exp_id)

best_features, artifacts, best_model = experiment.train(get_data, get_data_params)

new_data + target_pred + target_proba (if classif) = experiment.predict(**new_data)

On veut aussi pouvoir juste faire :

experiment.feature_engineering(data) : feat eng, return data

experiment.preprocess_feature(data) : split, encoding, pcas, return train, val, test df

experiment.feature_selection(train) : return features

experiment.preprocess_model(train, val, test) : return data = dict of df

experiment.model_selection(data) : return best_model
"""

import joblib
import pandas as pd
import logging
from lecrapaud.utils import logger
from lecrapaud.db.session import init_db
from lecrapaud.feature_selection import FeatureSelectionEngine, PreprocessModel
from lecrapaud.model_selection import ModelSelectionEngine, ModelEngine, evaluate
from lecrapaud.feature_engineering import FeatureEngineeringEngine, PreprocessFeature
from lecrapaud.experiment import create_experiment
from lecrapaud.db import Experiment
from lecrapaud.search_space import normalize_models_idx


class LeCrapaud:
    def __init__(self, uri: str = None):
        init_db(uri=uri)

    def create_experiment(self, data: pd.DataFrame, **kwargs):
        return ExperimentEngine(data=data, **kwargs)

    def get_experiment(self, id: int, **kwargs):
        return ExperimentEngine(id=id, **kwargs)


class ExperimentEngine:
    def __init__(self, id=None, data=None, **kwargs):
        if id:
            self.experiment = Experiment.get(id)
            kwargs.update(self.experiment.context)
        else:
            self.experiment = create_experiment(data=data, **kwargs)

        for key, value in kwargs.items():
            if key == "models_idx":
                value = normalize_models_idx(value)
            setattr(self, key, value)

    def train(self, data):
        logger.info("Running training...")

        data_eng = self.feature_engineering(data)
        logger.info("Feature engineering done.")

        train, val, test = self.preprocess_feature(data_eng)
        logger.info("Feature preprocessing done.")

        self.feature_selection(train)
        logger.info("Feature selection done.")

        std_data, reshaped_data = self.preprocess_model(train, val, test)
        logger.info("Model preprocessing done.")

        self.model_selection(std_data, reshaped_data)
        logger.info("Model selection done.")

    def predict(self, new_data, verbose: int = 0):
        # for scores if TARGET is in columns
        scores_reg = []
        scores_clf = []

        if verbose == 0:
            logger.setLevel(logging.WARNING)

        logger.warning("Running prediction...")

        # feature engineering + preprocessing
        data = self.feature_engineering(
            data=new_data,
            for_training=False,
        )
        data = self.preprocess_feature(data, for_training=False)
        data, scaled_data, reshaped_data = self.preprocess_model(
            data, for_training=False
        )

        for target_number in self.target_numbers:

            # loading model
            target_dir = f"{self.experiment.path}/TARGET_{target_number}"
            all_features = self.experiment.get_all_features(
                date_column=self.date_column, group_column=self.group_column
            )
            features = self.experiment.get_features(target_number)

            model = ModelEngine(path=target_dir)

            # getting data
            if model.recurrent:
                features_idx = [
                    i for i, e in enumerate(all_features) if e in set(features)
                ]
                x_pred = reshaped_data[:, :, features_idx]
            else:
                x_pred = scaled_data[features] if model.need_scaling else data[features]

            # predicting
            y_pred = model.predict(x_pred)

            # fix for recurrent model because x_val has no index as it is a 3D np array
            if model.recurrent:
                y_pred.index = (
                    new_data.index
                )  # TODO: not sure this will work for old experiment not aligned with data_for_training for test use case (done, this is why we decode the test set)

            # unscaling prediction
            if (
                model.need_scaling
                and model.target_type == "regression"
                and model.scaler_y is not None
            ):
                y_pred = pd.Series(
                    model.scaler_y.inverse_transform(
                        y_pred.values.reshape(-1, 1)
                    ).flatten(),
                    index=new_data.index,
                )
                y_pred.name = "PRED"

            # evaluate if TARGET is in columns
            new_data.columns = new_data.columns.str.upper()
            if f"TARGET_{target_number}" in new_data.columns:
                y_true = new_data[f"TARGET_{target_number}"]
                prediction = pd.concat([y_true, y_pred], axis=1)
                prediction.rename(
                    columns={f"TARGET_{target_number}": "TARGET"}, inplace=True
                )
                score = evaluate(
                    prediction,
                    target_type=model.target_type,
                )
                score["TARGET"] = f"TARGET_{target_number}"

                if model.target_type == "classification":
                    scores_clf.append(score)
                else:
                    scores_reg.append(score)

            # renaming and concatenating with initial data
            if isinstance(y_pred, pd.DataFrame):
                y_pred = y_pred.add_prefix(f"TARGET_{target_number}_")
                new_data = pd.concat([new_data, y_pred], axis=1)

            else:
                y_pred.name = f"TARGET_{target_number}_PRED"
                new_data = pd.concat([new_data, y_pred], axis=1)

        if len(scores_reg) > 0:
            scores_reg = pd.DataFrame(scores_reg).set_index("TARGET")
        if len(scores_clf) > 0:
            scores_clf = pd.DataFrame(scores_clf).set_index("TARGET")
        return new_data, scores_reg, scores_clf

    def feature_engineering(self, data, for_training=True):
        app = FeatureEngineeringEngine(
            data=data,
            columns_drop=self.columns_drop,
            columns_boolean=self.columns_boolean,
            columns_date=self.columns_date,
            columns_te_groupby=self.columns_te_groupby,
            columns_te_target=self.columns_te_target,
            for_training=for_training,
        )
        data = app.run()
        return data

    def preprocess_feature(self, data, for_training=True):
        app = PreprocessFeature(
            data=data,
            experiment=self.experiment,
            time_series=self.time_series,
            date_column=self.date_column,
            group_column=self.group_column,
            val_size=self.val_size,
            test_size=self.test_size,
            columns_pca=self.columns_pca,
            columns_onehot=self.columns_onehot,
            columns_binary=self.columns_binary,
            columns_frequency=self.columns_frequency,
            columns_ordinal=self.columns_ordinal,
            target_numbers=self.target_numbers,
            target_clf=self.target_clf,
        )
        if for_training:
            train, val, test = app.run()
            return train, val, test
        else:
            data = app.inference()
            return data

    def feature_selection(self, train):
        for target_number in self.target_numbers:
            app = FeatureSelectionEngine(
                train=train,
                target_number=target_number,
                experiment=self.experiment,
                target_clf=self.target_clf,
            )
            app.run()
        self.experiment = Experiment.get(self.experiment.id)
        all_features = self.experiment.get_all_features(
            date_column=self.date_column, group_column=self.group_column
        )
        return all_features

    def preprocess_model(self, train, val=None, test=None, for_training=True):
        app = PreprocessModel(
            train=train,
            val=val,
            test=test,
            experiment=self.experiment,
            target_numbers=self.target_numbers,
            target_clf=self.target_clf,
            models_idx=self.models_idx,
            time_series=self.time_series,
            max_timesteps=self.max_timesteps,
            date_column=self.date_column,
            group_column=self.group_column,
        )
        if for_training:
            data, reshaped_data = app.run()
            return data, reshaped_data
        else:
            data, scaled_data, reshaped_data = app.inference()
            return data, scaled_data, reshaped_data

    def model_selection(self, data, reshaped_data):
        for target_number in self.target_numbers:
            app = ModelSelectionEngine(
                data=data,
                reshaped_data=reshaped_data,
                target_number=target_number,
                experiment=self.experiment,
                target_clf=self.target_clf,
                models_idx=self.models_idx,
                time_series=self.time_series,
                date_column=self.date_column,
                group_column=self.group_column,
                target_clf_thresholds=self.target_clf_thresholds,
            )
            app.run(
                self.experiment_name,
                perform_hyperopt=self.perform_hyperopt,
                number_of_trials=self.number_of_trials,
                perform_crossval=self.perform_crossval,
                plot=self.plot,
                preserve_model=self.preserve_model,
            )

    def get_scores(self, target_number: int):
        return pd.read_csv(
            f"{self.experiment.path}/TARGET_{target_number}/scores_tracking.csv"
        )

    def get_prediction(self, target_number: int, model_name: str):
        return pd.read_csv(
            f"{self.experiment.path}/TARGET_{target_number}/{model_name}/prediction.csv"
        )

    def get_feature_summary(self):
        return pd.read_csv(f"{self.experiment.path}/feature_summary.csv")

    def get_threshold(self, target_number: int):
        return joblib.load(
            f"{self.experiment.path}/TARGET_{target_number}/thresholds.pkl"
        )
