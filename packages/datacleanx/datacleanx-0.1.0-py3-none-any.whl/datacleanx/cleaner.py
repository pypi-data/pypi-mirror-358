import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler, RobustScaler

class Cleaner:
    def __init__(
        self,
        impute_strategy="mean",
        encode_categoricals=None,
        remove_outliers=False,
        scale_numerics=None
    ):
        self.impute_strategy = impute_strategy
        self.encode_categoricals = encode_categoricals
        self.remove_outliers = remove_outliers
        self.scale_numerics = scale_numerics
        self._report = {}

    def clean(self, df):
        self._report = {}
        self._report["shape_before"] = df.shape
        df = df.copy()

        # Imputation
        if isinstance(self.impute_strategy, dict):
            for col, strategy in self.impute_strategy.items():
                if strategy == "mean":
                    value = df[col].mean()
                elif strategy == "median":
                    value = df[col].median()
                elif strategy == "mode":
                    value = df[col].mode().iloc[0]
                else:
                    raise ValueError(f"Unknown imputation strategy: {strategy}")
                df[col] = df[col].fillna(value)
                self._report[f"{col}_imputed_with"] = strategy
        else:
            for col in df.columns:
                if df[col].isnull().any():
                    strategy = self.impute_strategy
                    if df[col].dtype in [np.float64, np.int64]:
                        value = df[col].mean() if strategy == "mean" else df[col].median()
                    else:
                        value = df[col].mode().iloc[0]
                    df[col] = df[col].fillna(value)
                    self._report[f"{col}_imputed_with"] = strategy

        # Outlier Removal (IQR method)
        if self.remove_outliers:
            num_cols = df.select_dtypes(include=[np.number]).columns
            for col in num_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                before = df.shape[0]
                df = df[(df[col] >= lower) & (df[col] <= upper)]
                after = df.shape[0]
                self._report[f"{col}_outliers_removed"] = before - after

        # Encoding
        if self.encode_categoricals == "label":
            cat_cols = df.select_dtypes(include=['object']).columns
            for col in cat_cols:
                df[col] = LabelEncoder().fit_transform(df[col])
            self._report["categorical_encoding"] = "label"

        elif self.encode_categoricals == "onehot":
            cat_cols = df.select_dtypes(include=['object']).columns
            df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
            self._report["categorical_encoding"] = "onehot"

        # Feature Scaling
        if self.scale_numerics:
            num_cols = df.select_dtypes(include=[np.number]).columns
            scaler = {
                "standard": StandardScaler(),
                "minmax": MinMaxScaler(),
                "robust": RobustScaler()
            }.get(self.scale_numerics)

            if scaler is None:
                raise ValueError(f"Unknown scaling method: {self.scale_numerics}")

            df[num_cols] = scaler.fit_transform(df[num_cols])
            self._report["scaling"] = self.scale_numerics

        self._report["shape_after"] = df.shape
        return df

    def report(self):
        return self._report
