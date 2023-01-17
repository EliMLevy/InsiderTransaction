import csv
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


transactions = pd.read_table("NONDERIV_TRANS.tsv", dtype={'VALU_OWND_FOLWNG_TRANS': str, 'VALU_OWND_FOLWNG_TRANS_FN': str, 'SHRS_OWND_FOLWNG_TRANS_FN': str})

def convert_date(date_string):
    return datetime.strptime(date_string, "%d-%b-%Y").month


transactions["month"] = transactions['TRANS_DATE'].apply(convert_date)

# Initialize a dictionary to store the data
data = defaultdict(int)

# Iterate over the rows of the dataframe
for _, row in transactions.iterrows():
  # Extract the month from the 'Datetime' column
  month = row['month']
  # Increment the count for this month
  data[month] += 1


# Sort the data by month
sorted_data = sorted(data.items(), key=lambda x: x[0])

# Extract the month names and values from the sorted data
months, values = zip(*sorted_data)

# Set the position of the bars on the x-axis
x_pos = [i for i, _ in enumerate(months)]

# Create the bar plot
plt.bar(x_pos, values, width=0.4)

# Set the labels for the x-axis
plt.xticks(x_pos, months)

# Set the title and labels for the y-axis
plt.ylabel("Number of transactions")
plt.title("Transactions per month")

# Display the plot
plt.savefig('my_plot.png')

# # Extract the month names and values from the dictionary
# months = list(data.keys())
# values = list(data.values())


# # Set the position of the bars on the x-axis
# x_pos = [i for i, _ in enumerate(months)]

# # Create the bar plot
# plt.bar(x_pos, values, width=0.4)

# # Set the labels for the x-axis
# plt.xticks(x_pos, months)

# # Set the title and labels for the y-axis
# plt.ylabel("Number of transactions")
# plt.title("Transactions per month")

# # Display the plot
# plt.savefig('my_plot.png')
