
from model_utils import train_model
from database import load_ohlcv_months
import pandas as pd

df_train = load_ohlcv_months()
# print("==")
df_train.to_csv("train.csv")
# train_model(df_train)