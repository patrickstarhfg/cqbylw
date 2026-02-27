import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings('ignore')

# 1. 设置路径
base_path = r"D:\SHLT\cqgs\cqbylw"
# 所有的控制变量文件都在 control_data_new 文件夹中
control_path = os.path.join(base_path, "control_data_new")
output_path = os.path.join(base_path, "data", "final_data.csv")

# 辅助函数：统一证券代码为6位字符串
def standardize_stkcd(stkcd):
    try:
        # 先转为字符串
        s = str(stkcd).strip()
        # 如果是数字形式的字符串（如 '2'），补零到6位（如 '000002'）
        if s.isdigit():
            return s.zfill(6)
        return s
    except:
        return str(stkcd)

# 2. 读取各个数据文件
print("Reading data files...")

# (1) 财务报表 (资产负债表 - Lev, TotalAssets)
# 文件名：PT_LCMAINFIN.xlsx (从 226实际指标文件160900502 等文件夹里找，或者上市公司主要财务指标)
# 根据 check_new_controls.py，TotalAssets 在 PT_LCMAINFIN.xlsx 中
pt_file = None
for root, dirs, files in os.walk(control_path):
    if "PT_LCMAINFIN.xlsx" in files:
        pt_file = os.path.join(root, "PT_LCMAINFIN.xlsx")
        break

if pt_file:
    balance_sheet = pd.read_excel(pt_file)
    balance_sheet = balance_sheet[pd.to_numeric(balance_sheet['Symbol'], errors='coerce').notna()]
    balance_sheet = balance_sheet.rename(columns={
        'Symbol': 'Stkcd', 
        'EndDate': 'Year', 
        'TotalAssets': 'TotalAssets'
    })
    # 需要找 Lev (资产负债率)，在 check_new_controls.py 中看到 FI_T1.xlsx 有 F011201A (资产负债率)
else:
    print("Warning: PT_LCMAINFIN.xlsx not found!")
    balance_sheet = pd.DataFrame()

# 偿债能力 (Lev)
fi_t1_file = None
for root, dirs, files in os.walk(control_path):
    if "FI_T1.xlsx" in files:
        fi_t1_file = os.path.join(root, "FI_T1.xlsx")
        break

if fi_t1_file:
    debt = pd.read_excel(fi_t1_file)
    debt = debt[pd.to_numeric(debt['Stkcd'], errors='coerce').notna()]
    debt = debt.rename(columns={
        'Stkcd': 'Stkcd', 
        'Accper': 'Year', 
        'F011201A': 'Lev' # 资产负债率
    })
    # 合并 Lev
    balance_sheet['Year'] = pd.to_datetime(balance_sheet['Year']).dt.year.astype('int64')
    debt['Year'] = pd.to_datetime(debt['Year']).dt.year.astype('int64')
    
    balance_sheet['Stkcd'] = balance_sheet['Stkcd'].apply(standardize_stkcd)
    debt['Stkcd'] = debt['Stkcd'].apply(standardize_stkcd)
    
    balance_sheet = pd.merge(balance_sheet, debt[['Stkcd', 'Year', 'Lev']], on=['Stkcd', 'Year'], how='outer')
    balance_sheet = balance_sheet.sort_values(['Stkcd', 'Year']).drop_duplicates(['Stkcd', 'Year'], keep='last')

# (2) 利润表 (ROA, NetProfit)
# check_new_controls.py 显示 AF_Actual.xlsx 有 ROA
af_file = None
for root, dirs, files in os.walk(control_path):
    if "AF_Actual.xlsx" in files:
        af_file = os.path.join(root, "AF_Actual.xlsx")
        break

if af_file:
    income_statement = pd.read_excel(af_file)
    income_statement = income_statement[pd.to_numeric(income_statement['Stkcd'], errors='coerce').notna()]
    income_statement = income_statement.rename(columns={
        'Stkcd': 'Stkcd', 
        'Ddate': 'Year', 
        'ROA': 'ROA'
    })
    income_statement['Year'] = pd.to_datetime(income_statement['Year']).dt.year.astype('int64')
    income_statement['Stkcd'] = income_statement['Stkcd'].apply(standardize_stkcd)
    income_statement = income_statement.sort_values(['Stkcd', 'Year']).drop_duplicates(['Stkcd', 'Year'], keep='last')
else:
    income_statement = pd.DataFrame()

# (3) 发展能力 (Grow - 营业利润增长率B)
# check_new_controls.py 显示 FI_T8.xlsx 有 F081202B
fi_t8_file = None
for root, dirs, files in os.walk(control_path):
    if "FI_T8.xlsx" in files:
        fi_t8_file = os.path.join(root, "FI_T8.xlsx")
        break

if fi_t8_file:
    growth = pd.read_excel(fi_t8_file)
    growth = growth[pd.to_numeric(growth['Stkcd'], errors='coerce').notna()]
    growth = growth.rename(columns={
        'Stkcd': 'Stkcd', 
        'Accper': 'Year', 
        'F081202B': 'Grow' # 营业利润增长率
    })
    growth['Year'] = pd.to_datetime(growth['Year']).dt.year.astype('int64')
    growth['Stkcd'] = growth['Stkcd'].apply(standardize_stkcd)
    growth = growth.sort_values(['Stkcd', 'Year']).drop_duplicates(['Stkcd', 'Year'], keep='last')
else:
    growth = pd.DataFrame()

# (4) 现金流 (CashFlow - 暂时作为占位，如果TFP计算需要)
# FI_T6.xlsx
cash_file = None
for root, dirs, files in os.walk(control_path):
    if "FI_T6.xlsx" in files:
        cash_file = os.path.join(root, "FI_T6.xlsx")
        break
    
# (5) 股权性质 (SOE, Top1) - 仍然使用旧数据 (EN_EquityNatureAll.xlsx)
# 假设旧数据还在 base_path 下，或者在 control_data_new 里
equity_file = None
for root, dirs, files in os.walk(base_path): # Search entire base_path including old folders
    if "EN_EquityNatureAll.xlsx" in files:
        equity_file = os.path.join(root, "EN_EquityNatureAll.xlsx")
        break

if equity_file:
    equity = pd.read_excel(equity_file)
    equity = equity[pd.to_numeric(equity['Symbol'], errors='coerce').notna()]
    equity = equity.rename(columns={
        'Symbol': 'Stkcd', 
        'EndDate': 'Year', 
        'LargestHolderRate': 'Top1', 
        'EquityNatureID': 'SOE_ID'
    })
    equity['Year'] = pd.to_datetime(equity['Year']).dt.year.astype('int64')
    def is_soe(code):
        try:
            if str(code).startswith('1'): return 1
            return 0
        except:
            return 0
    equity['SOE'] = equity['SOE_ID'].apply(is_soe)
    equity['Stkcd'] = equity['Stkcd'].apply(standardize_stkcd)
    equity = equity.sort_values(['Stkcd', 'Year']).drop_duplicates(['Stkcd', 'Year'], keep='last')
    equity = equity[['Stkcd', 'Year', 'Top1', 'SOE']]
else:
    equity = pd.DataFrame()

# (6) 治理结构 (Board, Indb, Duality, Staff) - 旧数据 BDT_ManaGovAbil.xlsx
gov_file = None
for root, dirs, files in os.walk(base_path):
    if "BDT_ManaGovAbil.xlsx" in files:
        gov_file = os.path.join(root, "BDT_ManaGovAbil.xlsx")
        break

if gov_file:
    governance = pd.read_excel(gov_file)
    governance = governance[pd.to_numeric(governance['Symbol'], errors='coerce').notna()]
    governance = governance.rename(columns={
        'Symbol': 'Stkcd', 
        'Enddate': 'Year', 
        'Boardsize': 'Board', 
        'IndDirectorRatio': 'Indb', 
        'IsCocurP': 'Duality', 
        'StaffNumber': 'Staff'
    })
    governance['Year'] = pd.to_datetime(governance['Year']).dt.year.astype('int64')
    governance['Stkcd'] = governance['Stkcd'].apply(standardize_stkcd)
    governance = governance.sort_values(['Stkcd', 'Year']).drop_duplicates(['Stkcd', 'Year'], keep='last')
    governance = governance[['Stkcd', 'Year', 'Board', 'Indb', 'Duality', 'Staff']]
else:
    governance = pd.DataFrame()

# (7) 基本信息 (Age, Province, City, IndustryCode)
# STK_LISTEDCOINFOANL.xlsx (新文件)
info_file = None
for root, dirs, files in os.walk(control_path):
    if "STK_LISTEDCOINFOANL.xlsx" in files:
        info_file = os.path.join(root, "STK_LISTEDCOINFOANL.xlsx")
        break

if info_file:
    base_info = pd.read_excel(info_file)
    base_info = base_info[pd.to_numeric(base_info['Symbol'], errors='coerce').notna()]
    base_info = base_info.rename(columns={
        'Symbol': 'Stkcd', 
        'EndDate': 'Year', 
        'EstablishDate': 'EstablishDate', # 用成立日期算 Age 更准
        'IndustryCode': 'IndustryCode' # 行业代码
    })
    # 注意：STK_LISTEDCOINFOANL 好像没有 Province/City，需要从旧的 DM_ListedCoInfoAnlY.xlsx 找
    # 或者如果不重要就先略过
    
    base_info['Year'] = pd.to_datetime(base_info['Year']).dt.year.astype('int64')
    base_info['EstablishDate'] = pd.to_datetime(base_info['EstablishDate'])
    base_info['EstablishYear'] = base_info['EstablishDate'].dt.year
    base_info['Age'] = base_info['Year'] - base_info['EstablishYear']
    base_info['Age'] = base_info['Age'].apply(lambda x: x if x >= 0 else np.nan)
    # 使用 np.log1p 处理 float 类型，避免 float.log 错误
    base_info['Age'] = np.log1p(base_info['Age'])
    
    base_info['Stkcd'] = base_info['Stkcd'].apply(standardize_stkcd)
    base_info = base_info.sort_values(['Stkcd', 'Year']).drop_duplicates(['Stkcd', 'Year'], keep='last')
    
    # 检查 IndustryCode 是否存在，如果不存在则不包含在列列表中
    cols_to_keep = ['Stkcd', 'Year', 'Age']
    if 'IndustryCode' in base_info.columns:
        cols_to_keep.append('IndustryCode')
    else:
        print("Warning: 'IndustryCode' not found in base_info. Trying to merge from old file later if possible.")
        
    base_info = base_info[cols_to_keep]
else:
    base_info = pd.DataFrame()

# (8) 数字化转型 (Digital) - 旧数据
digital_file = None
for root, dirs, files in os.walk(base_path):
    if "DM_ListedCoDigTrsDegreeY.xlsx" in files:
        digital_file = os.path.join(root, "DM_ListedCoDigTrsDegreeY.xlsx")
        break

if digital_file:
    digital = pd.read_excel(digital_file)
    digital = digital[pd.to_numeric(digital['Symbol'], errors='coerce').notna()]
    digital = digital.rename(columns={
        'Symbol': 'Stkcd', 
        'SgnYear': 'Year', 
        'DigitalTechApplication': 'DigitalScore'
    })
    digital['Treat_time'] = np.where(digital['DigitalScore'] > 0, 1, 0)
    digital['Stkcd'] = digital['Stkcd'].apply(standardize_stkcd)
    digital['Year'] = digital['Year'].astype('int64')
    digital = digital[['Stkcd', 'Year', 'Treat_time', 'DigitalScore']]
else:
    digital = pd.DataFrame()

# (9) 托宾Q (TobinQ) - 旧数据 FI_T10.xlsx
tobin_file = None
for root, dirs, files in os.walk(base_path):
    if "FI_T10.xlsx" in files:
        tobin_file = os.path.join(root, "FI_T10.xlsx")
        break

if tobin_file:
    tobin_q = pd.read_excel(tobin_file)
    tobin_q = tobin_q[pd.to_numeric(tobin_q['Stkcd'], errors='coerce').notna()]
    tobin_q = tobin_q.rename(columns={
        'Stkcd': 'Stkcd', 
        'Accper': 'Year', 
        'F100901A': 'TobinQ'
    })
    tobin_q['Year'] = pd.to_datetime(tobin_q['Year']).dt.year.astype('int64')
    tobin_q['Stkcd'] = tobin_q['Stkcd'].apply(standardize_stkcd)
    tobin_q = tobin_q.sort_values(['Stkcd', 'Year']).drop_duplicates(['Stkcd', 'Year'], keep='last')
else:
    tobin_q = pd.DataFrame()

# (10) GDP - 旧数据
city_gdp_file = None
prov_gdp_file = None
for root, dirs, files in os.walk(base_path):
    if "CRE_Gdpct.xlsx" in files: city_gdp_file = os.path.join(root, "CRE_Gdpct.xlsx")
    if "CRE_Gdp01.xlsx" in files: prov_gdp_file = os.path.join(root, "CRE_Gdp01.xlsx")

# 3. 合并数据
print("Merging datasets...")
# 以 balance_sheet (资产负债表) 为主表，因为它通常最全
df_final = balance_sheet.copy()

# 依次左连接
dfs_to_merge = [income_statement, growth, equity, governance, base_info, digital, tobin_q]

for i, df in enumerate(dfs_to_merge):
    if not df.empty:
        print(f"Merging dataframe {i+1}...")
        df_final = pd.merge(df_final, df, on=['Stkcd', 'Year'], how='left')

# 优先使用城市 GDP，如果缺失则使用省份 GDP
if 'GDP_City' in df_final.columns and 'GDP_Prov' in df_final.columns:
    df_final['GDP'] = df_final['GDP_City'].fillna(df_final['GDP_Prov'])
else:
    # 尝试从旧逻辑中恢复 GDP 列，或者如果都缺失则设为 NaN
    print("Warning: GDP_City or GDP_Prov not found in merged data.")
    if 'GDP_City' in df_final.columns:
        df_final['GDP'] = df_final['GDP_City']
    elif 'GDP_Prov' in df_final.columns:
        df_final['GDP'] = df_final['GDP_Prov']
    else:
        df_final['GDP'] = np.nan

# 4. 变量计算与清洗
print("Calculating variables...")
# (0) GDP: ln(GDP)
# 注意单位：通常 GDP 是亿元，取对数前确认是否有 0 或负数
# 如果 GDP 缺失严重，可能是因为 City/Province 名称不匹配（比如多了“市”字或者空格）
df_final['GDP'] = np.log1p(df_final['GDP'])


# (1) Size: ln(TotalAssets)
# 确保 TotalAssets 是浮点数类型
df_final['TotalAssets'] = pd.to_numeric(df_final['TotalAssets'], errors='coerce')
df_final['Size'] = np.log1p(df_final['TotalAssets'])

# (2) Lev: TotalLiabilities / TotalAssets
# 检查列是否存在
if 'TotalLiabilities' in df_final.columns and 'TotalAssets' in df_final.columns:
    df_final['TotalLiabilities'] = pd.to_numeric(df_final['TotalLiabilities'], errors='coerce')
    df_final['Lev'] = df_final['TotalLiabilities'] / df_final['TotalAssets']
else:
    print("Warning: TotalLiabilities or TotalAssets not found. Lev will be NaN.")
    df_final['Lev'] = np.nan

# (3) ROA: NetProfit / TotalAssets
# 如果 ROA 缺失，可能是 NetProfit 缺失或者 TotalAssets 缺失
if 'NetProfit' in df_final.columns and 'TotalAssets' in df_final.columns:
    df_final['NetProfit'] = pd.to_numeric(df_final['NetProfit'], errors='coerce')
    df_final['ROA'] = df_final['NetProfit'] / df_final['TotalAssets']
else:
    # 尝试使用直接的 ROA 列
    if 'ROA' not in df_final.columns:
        print("Warning: NetProfit or TotalAssets not found, and ROA column missing. ROA will be NaN.")
        df_final['ROA'] = np.nan

# (4) Board: ln(Board)
if 'Board' in df_final.columns:
    df_final['Board'] = pd.to_numeric(df_final['Board'], errors='coerce')
    df_final['Board'] = np.log1p(df_final['Board'])
else:
    print("Warning: Board column not found.")

# 5. 保存结果
print(f"Saving final dataset to {output_path}...")
try:
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print("Done! Final dataset shape:", df_final.shape)
    print(df_final.head())
except PermissionError:
    print(f"Permission denied: {output_path}")
    print("Please close the file if it is open in Excel or another program.")
