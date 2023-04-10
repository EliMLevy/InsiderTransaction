import pandas as pd

df = pd.read_table("./data/2022Q1/NONDERIV_TRANS.tsv")
df = df.drop(['NONDERIV_TRANS_SK','SECURITY_TITLE','SECURITY_TITLE_FN', 'TRANS_DATE_FN','DEEMED_EXECUTION_DATE','DEEMED_EXECUTION_DATE_FN','EQUITY_SWAP_INVOLVED','EQUITY_SWAP_TRANS_CD_FN','TRANS_TIMELINESS','TRANS_TIMELINESS_FN','TRANS_SHARES_FN','TRANS_PRICEPERSHARE_FN','TRANS_ACQUIRED_DISP_CD_FN','SHRS_OWND_FOLWNG_TRANS_FN','VALU_OWND_FOLWNG_TRANS','VALU_OWND_FOLWNG_TRANS_FN','DIRECT_INDIRECT_OWNERSHIP_FN','NATURE_OF_OWNERSHIP','NATURE_OF_OWNERSHIP_FN'], axis=1)
print(len(df))
df = df[df["TRANS_FORM_TYPE"] == 4]
print(len(df))

df = df[df["TRANS_ACQUIRED_DISP_CD"] == "A"]
print(len(df))

df = df[df["DIRECT_INDIRECT_OWNERSHIP"] == "D"]
print(len(df))

df = df[df["TRANS_CODE"] == "A"]
print(len(df))


df = df.dropna(subset=['TRANS_PRICEPERSHARE', 'TRANS_SHARES'])
print(len(df))

df = df[df["TRANS_PRICEPERSHARE"] > 0]
print(len(df))



print(df.head())