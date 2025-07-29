# datacleanx/imputer.py

import pandas as pd
import numpy as np

class MissingValueHandler:
    """
    Handles missing values using common strategies.
    """

    def __init__(self, strategy: str = "mean"):
        """
        Initialize the handler with a given strategy.
        Options: 'mean', 'median', 'mode'
        """
        self.strategy = strategy
        self.fill_values = {}

    def handle_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Impute missing values in numerical and categorical columns.

        Parameters:
            df (pd.DataFrame): DataFrame with NaNs

        Returns:
            pd.DataFrame: DataFrame with missing values imputed
        """
        df = df.copy()

        for col in df.columns:
            if df[col].isnull().sum() == 0:
                continue  # Skip if no missing

            if pd.api.types.is_numeric_dtype(df[col]):
                if self.strategy == "mean":
                    fill = df[col].mean()
                elif self.strategy == "median":
                    fill = df[col].median()
                else:
                    fill = df[col].mode().dropna().iloc[0]
            else:
                fill = df[col].mode().dropna().iloc[0]

            df[col] = df[col].fillna(fill)
            self.fill_values[col] = fill

        return df
