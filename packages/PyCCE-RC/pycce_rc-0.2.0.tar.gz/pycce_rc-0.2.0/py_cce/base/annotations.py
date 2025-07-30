import numpy as np
import pandas as pd

PandasObject = pd.DataFrame | pd.Series
ArrayLikeType = np.ndarray | list
PanelDataLikeType = ArrayLikeType | PandasObject
