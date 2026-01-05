#!/usr/bin/python3
import pandas as pd

df = pd.read_csv("data/interim/farmers_synthetic.csv")

df.columns.tolist()
df.isna().sum().sort_values(ascending=False).head()
df[['region','zone','woreda','kebele']].nunique()
print(df.shape)
print(df.head())
# print(df['ai_crop_advisory_adoption'].value_counts())
print("Tomas kitaba")