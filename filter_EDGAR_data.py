import pandas as pd
from datetime import datetime

def filtered_transactions(path_to_data):
    
    # ACCESSION_NUMBER	RPTOWNERCIK	RPTOWNERNAME	RPTOWNER_RELATIONSHIP	RPTOWNER_TITLE	RPTOWNER_TXT	RPTOWNER_STREET1	RPTOWNER_STREET2	RPTOWNER_CITY	RPTOWNER_STATE	RPTOWNER_ZIPCODE	RPTOWNER_STATE_DESC	FILE_NUMBER
    owners = pd.read_table(path_to_data + "REPORTINGOWNER.tsv", index_col=0)
    owners = owners.drop(['RPTOWNERCIK', 'RPTOWNERNAME', 'RPTOWNER_TITLE', 'RPTOWNER_TXT', 'RPTOWNER_STREET1', 'RPTOWNER_STREET2', 'RPTOWNER_CITY', 'RPTOWNER_STATE', 'RPTOWNER_ZIPCODE','RPTOWNER_STATE_DESC','FILE_NUMBER'], axis=1)
    # print(owners.head())

    # ACCESSION_NUMBER	FILING_DATE	PERIOD_OF_REPORT	DATE_OF_ORIG_SUB	NO_SECURITIES_OWNED	NOT_SUBJECT_SEC16	FORM3_HOLDINGS_REPORTED	FORM4_TRANS_REPORTED	DOCUMENT_TYPE	ISSUERCIK	ISSUERNAME	ISSUERTRADINGSYMBOL	REMARKS
    submissions = pd.read_table(path_to_data + "SUBMISSION.tsv", index_col=0)
    submissions = submissions.drop(['PERIOD_OF_REPORT','DATE_OF_ORIG_SUB','NO_SECURITIES_OWNED','NOT_SUBJECT_SEC16','FORM3_HOLDINGS_REPORTED','FORM4_TRANS_REPORTED','DOCUMENT_TYPE','ISSUERCIK','ISSUERNAME', 'REMARKS'], axis=1)
    # print(submissions.head())

    # ACCESSION_NUMBER	NONDERIV_TRANS_SK	SECURITY_TITLE	SECURITY_TITLE_FN	TRANS_DATE	TRANS_DATE_FN	DEEMED_EXECUTION_DATE	DEEMED_EXECUTION_DATE_FN	TRANS_FORM_TYPE	TRANS_CODE	EQUITY_SWAP_INVOLVED	EQUITY_SWAP_TRANS_CD_FN	TRANS_TIMELINESS	TRANS_TIMELINESS_FN	TRANS_SHARES	TRANS_SHARES_FN	TRANS_PRICEPERSHARE	TRANS_PRICEPERSHARE_FN	TRANS_ACQUIRED_DISP_CD	TRANS_ACQUIRED_DISP_CD_FN	SHRS_OWND_FOLWNG_TRANS	SHRS_OWND_FOLWNG_TRANS_FN	VALU_OWND_FOLWNG_TRANS	VALU_OWND_FOLWNG_TRANS_FN	DIRECT_INDIRECT_OWNERSHIP	DIRECT_INDIRECT_OWNERSHIP_FN	NATURE_OF_OWNERSHIP	NATURE_OF_OWNERSHIP_FN
    transactions = pd.read_table(path_to_data + "NONDERIV_TRANS.tsv", index_col=0, dtype={'VALU_OWND_FOLWNG_TRANS': str, 'VALU_OWND_FOLWNG_TRANS_FN': str, 'SHRS_OWND_FOLWNG_TRANS_FN': str})
    transactions = transactions.drop(['NONDERIV_TRANS_SK','SECURITY_TITLE','SECURITY_TITLE_FN', 'TRANS_DATE_FN','DEEMED_EXECUTION_DATE','DEEMED_EXECUTION_DATE_FN','EQUITY_SWAP_INVOLVED','EQUITY_SWAP_TRANS_CD_FN','TRANS_TIMELINESS','TRANS_TIMELINESS_FN','TRANS_SHARES_FN','TRANS_PRICEPERSHARE_FN','TRANS_ACQUIRED_DISP_CD_FN','SHRS_OWND_FOLWNG_TRANS_FN','VALU_OWND_FOLWNG_TRANS','VALU_OWND_FOLWNG_TRANS_FN','DIRECT_INDIRECT_OWNERSHIP_FN','NATURE_OF_OWNERSHIP','NATURE_OF_OWNERSHIP_FN'], axis=1)
    print(f"Number transactions 1: {len(transactions)}")

    transactions = transactions[transactions["TRANS_FORM_TYPE"] == 4]
    transactions = transactions[transactions["TRANS_ACQUIRED_DISP_CD"] == "A"]
    transactions = transactions[transactions["DIRECT_INDIRECT_OWNERSHIP"] == "D"]
    transactions = transactions[transactions["TRANS_CODE"] == "A"]
    transactions = transactions.dropna(subset=['TRANS_PRICEPERSHARE', 'TRANS_SHARES'])
    transactions = transactions[transactions["TRANS_PRICEPERSHARE"] > 0]
    print(f"Number transactions 2: {len(transactions)}")


    transactions = transactions.merge(owners, how='inner', on='ACCESSION_NUMBER')
    transactions = transactions.merge(submissions, how='inner', on='ACCESSION_NUMBER')

    transactions = transactions.dropna(subset=['ISSUERTRADINGSYMBOL'])

    print(f"Number transactions 2.5: {len(transactions)}")

    def convert_date(date_string):
        return datetime.strptime(date_string, "%d-%b-%Y")

    transactions["datetime"] = transactions['FILING_DATE'].apply(convert_date)
    print(f"Number transactions 2.75: {len(transactions)}")

    def extract_month(datetime_obj):
        return datetime_obj.month
    transactions["month"] = transactions['datetime'].apply(extract_month)

    # transactions = transactions[transactions["month"] >= 9]
    # print(f"Number transactions 2.85: {len(transactions)}")

    def extract_day(datetime_obj):
        return datetime_obj.day
    transactions["day"] = transactions['datetime'].apply(extract_day)

    transactions = transactions[transactions["RPTOWNER_RELATIONSHIP"] == "Officer"]
    print(f"Number transactions 3: {len(transactions)}")

    # print(transactions.head())
    # print(f"Number of form 4 transactions: {len(transactions)}")
    return transactions

