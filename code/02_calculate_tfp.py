import pandas as pd
import numpy as np
import os
from statsmodels.formula.api import ols

# 1. 设置路径
base_path = r"D:\SHLT\cqgs\cqbylw\tfp_data"
output_path = os.path.join(r"D:\SHLT\cqgs\cqbylw\data", "tfp_result.csv")

# 辅助函数：统一证券代码
def standardize_stkcd(stkcd):
    try:
        s = str(stkcd).strip()
        if s.isdigit():
            return s.zfill(6)
        return s
    except:
        return str(stkcd)

print("Reading TFP source files...")

# (1) 产出 Y: 营业收入 (B001101000)
# 注意：FS_Comins.xlsx 中 B001101000 是营业收入
income = pd.read_excel(os.path.join(base_path, "226利润表133904769", "FS_Comins.xlsx"))
income = income[pd.to_numeric(income['Stkcd'], errors='coerce').notna()] # 去表头
income = income.rename(columns={'Stkcd': 'Stkcd', 'Accper': 'Year', 'B001101000': 'Y_Revenue'})
income['Year'] = pd.to_datetime(income['Year']).dt.year.astype('int64')
income['Stkcd'] = income['Stkcd'].apply(standardize_stkcd)
income = income.sort_values(['Stkcd', 'Year']).drop_duplicates(['Stkcd', 'Year'], keep='last')

# (2) 中间投入 M: 购买商品支付现金 (C001014000)
cash = pd.read_excel(os.path.join(base_path, "226现金流量表(直接法)134129681", "FS_Comscfd.xlsx"))
cash = cash[pd.to_numeric(cash['Stkcd'], errors='coerce').notna()]
cash = cash.rename(columns={'Stkcd': 'Stkcd', 'Accper': 'Year', 'C001014000': 'M_Input'})
cash['Year'] = pd.to_datetime(cash['Year']).dt.year.astype('int64')
cash['Stkcd'] = cash['Stkcd'].apply(standardize_stkcd)
cash = cash.sort_values(['Stkcd', 'Year']).drop_duplicates(['Stkcd', 'Year'], keep='last')

# (3) 资本 K: 固定资产净额 (A001212000)
balance = pd.read_excel(os.path.join(base_path, "226资产负债表133659536", "FS_Combas.xlsx"))
balance = balance[pd.to_numeric(balance['Stkcd'], errors='coerce').notna()]
balance = balance.rename(columns={'Stkcd': 'Stkcd', 'Accper': 'Year', 'A001212000': 'K_Capital'})
balance['Year'] = pd.to_datetime(balance['Year']).dt.year.astype('int64')
balance['Stkcd'] = balance['Stkcd'].apply(standardize_stkcd)
balance = balance.sort_values(['Stkcd', 'Year']).drop_duplicates(['Stkcd', 'Year'], keep='last')

# (4) 劳动 L: 员工人数 (Y0601b)
# 来源：治理综合信息文件 (CG_Ybasic.xlsx)
staff = pd.read_excel(os.path.join(base_path, "226治理综合信息文件142353163", "CG_Ybasic.xlsx"))
staff = staff[pd.to_numeric(staff['Stkcd'], errors='coerce').notna()]

staff = staff.rename(columns={'Stkcd': 'Stkcd', 'Reptdt': 'Year', 'Y0601b': 'L_Labor'})
staff['Year'] = pd.to_datetime(staff['Year']).dt.year.astype('int64')
staff['Stkcd'] = staff['Stkcd'].apply(standardize_stkcd)
staff = staff.sort_values(['Stkcd', 'Year']).drop_duplicates(['Stkcd', 'Year'], keep='last')

# 2. 合并数据
print("Merging data...")
# 使用外连接并打印每一步的数据量，以便排查问题
df = pd.merge(income[['Stkcd', 'Year', 'Y_Revenue']], 
              cash[['Stkcd', 'Year', 'M_Input']], on=['Stkcd', 'Year'], how='inner')
print(f"After Income-Cash merge: {df.shape}")

df = pd.merge(df, balance[['Stkcd', 'Year', 'K_Capital']], on=['Stkcd', 'Year'], how='inner')
print(f"After Balance merge: {df.shape}")

df = pd.merge(df, staff[['Stkcd', 'Year', 'L_Labor']], on=['Stkcd', 'Year'], how='inner')
print(f"After Staff merge: {df.shape}")

# 3. 预处理
print("Preprocessing...")
# 转换为数值型
cols = ['Y_Revenue', 'M_Input', 'K_Capital', 'L_Labor']
for col in cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 去除缺失值和负值/零值 (取对数要求 > 0)
df = df.dropna()
df = df[(df['Y_Revenue'] > 0) & (df['M_Input'] > 0) & (df['K_Capital'] > 0) & (df['L_Labor'] > 0)]

# 取对数
df['lnY'] = np.log(df['Y_Revenue'])
df['lnM'] = np.log(df['M_Input'])
df['lnK'] = np.log(df['K_Capital'])
df['lnL'] = np.log(df['L_Labor'])

# 4. 计算 TFP (简化版 LP 法 / OLS 替代)
# 真正的 LP 法需要 GMM 估计，比较复杂。
# 这里我们先用 OLS 估计残差作为 TFP 的近似 (TFP_OLS)，这也是一种常见的基础做法。
# 如果需要严格的 LP 法，可以后续引入 pyprods 库或 semipy。

print("Estimating TFP (OLS)...")
# 模型：lnY = alpha * lnL + beta * lnK + gamma * lnM + epsilon
# TFP = lnY - (alpha * lnL + beta * lnK + gamma * lnM)
# 注意：有些文献把 M 放在左边 (Value Added)，这里我们用 Gross Output 模型

# 分行业回归 (如果没有行业数据，先做全样本回归)
model = ols('lnY ~ lnL + lnK + lnM', data=df).fit()
print(model.summary())

# 计算 TFP
df['TFP_OLS'] = model.resid + model.params['Intercept'] 
# 或者直接用残差代表 TFP 的波动部分
# 这里保留截距项代表平均技术水平

# 5. 保存结果
print(f"Saving TFP results to {output_path}...")
df[['Stkcd', 'Year', 'TFP_OLS', 'lnY', 'lnL', 'lnK', 'lnM']].to_csv(output_path, index=False, encoding='utf-8-sig')
print("Done! Shape:", df.shape)
