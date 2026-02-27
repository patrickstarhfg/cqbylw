import pandas as pd
import numpy as np
import os
from statsmodels.formula.api import ols
import statsmodels.api as sm

# 1. 读取数据
file_path = r"D:\SHLT\cqgs\cqbylw\data\final_data.csv"
print(f"Reading data from {file_path}...")
df = pd.read_csv(file_path)

# 2. 数据筛选 (2016-2024)
print("Filtering data (Year >= 2016)...")
df = df[df['Year'] >= 2016]

# 3. 填补缺失值 (简单的均值填补，仅供参考)
# 注意：严谨的研究应该用插值法或直接剔除
print("Handling missing values...")
cols_to_fill = ['GDP', 'ROA']
for col in cols_to_fill:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].mean())

# 4. 定义模型公式
# 被解释变量：TFP_OLS, ROA
# 解释变量：Treat_time (数字化转型虚拟变量)
# 控制变量：Size, Lev, TobinQ, Board, Indb, Top1, Age, GDP, SOE
controls = "Size + Lev + TobinQ + Board + Indb + Top1 + Age + GDP + C(SOE) + C(Year)"

# 模型 1: TFP 回归
formula_tfp = f"TFP_OLS ~ Treat_time + {controls}"
print(f"\n=== Regression 1: TFP ~ Digitalization ===")
print(f"Formula: {formula_tfp}")

try:
    model_tfp = ols(formula_tfp, data=df).fit(cov_type='HC1') # 使用稳健标准误
    print(model_tfp.summary())
except Exception as e:
    print(f"Error in TFP regression: {e}")

# 模型 2: ROA 回归
formula_roa = f"ROA ~ Treat_time + {controls}"
print(f"\n=== Regression 2: ROA ~ Digitalization ===")
print(f"Formula: {formula_roa}")

try:
    model_roa = ols(formula_roa, data=df).fit(cov_type='HC1')
    print(model_roa.summary())
except Exception as e:
    print(f"Error in ROA regression: {e}")

print("\nRegression analysis completed.")
