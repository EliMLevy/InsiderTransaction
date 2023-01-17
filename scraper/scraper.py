import requests
import os
import csv
from bs4 import BeautifulSoup

# Create the "data" directory if it doesn't already exist
if not os.path.exists("data"):
    os.mkdir("data")

# Set the URL for the Form 4 filings page
url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&dateb=&owner=exclude&count=80"
headers = {"User-Agent": "testing.test@gmail.com"}
# Send a request to the URL and retrieve the HTML
html = requests.get(url, headers=headers).text

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html, "html.parser")

# print(html)

# Find all of the rows in the table of Form 4 filings
# body > div > table:nth-child(6)
# /html/body/div/table[2]
# table = soup.find("table", {"class": "tableFile2"})
body = soup.select("body")[0]
bodydiv = body.select("div")[0]
table = bodydiv.select("table")[3]
rows = table.find_all("tr")

# For each row, find the company name, insider name, and link to the filing
titleRow = True
currentRow = {}


for row in rows[1:]:
    print("******")
    # print(row)
    cells = row.find_all("td")

    if len(cells) > 0:
        if titleRow:
            currentRow["company_name"] = cells[0].text
            currentRow["company_link"] = cells[0].a["href"]
            titleRow = False
        else:
            currentRow["form"] = cells[0].text
            links = cells[1].find_all("a")
            if len(links) > 1:
                currentRow["filing_link"] = cells[1].find_all("a")[1]["href"]
            elif len(links) == 1:
                currentRow["filing_link"] = cells[1].find_all("a")[0]["href"]
            else:
                currentRow["filing_link"] = "NOT FOUND"

            currentRow["description"] = cells[2].text
            currentRow["accepted"] = cells[3].text
            currentRow["filing_date"] = cells[4].text
            print(currentRow)
            titleRow = True


            # for index, cell in enumerate(cells):
            #     links = cell.find_all("a")

            #     if links is not None and len(links) > 0:
            #         print(f"[{index}] {cell.text}")
            #         for link in links:
            #             print(f"{link['href']}")
            #     else:
            #         print(f"[{index}] {cell.text}")

#     if len(cells) > 3:
#         print(f"link: {cells}")
#         company_name = cells[1].text
#         insider_name = cells[2].text
#         filing_link = cells[3].a["href"]

        # Retrieve the filing HTML
        # filing_html = requests.get(filing_link).text

        # # Parse the filing HTML
        # filing_soup = BeautifulSoup(filing_html, "html.parser")

        # # Find the table of insider transactions
        # filing_table = filing_soup.find("table", {"class": "tableFile"})

        # # Create a list of dictionaries representing each row in the table
        # data = []
        # rows = filing_table.tbody.find_all("tr")
        # for row in rows:
        #     cells = row.find_all("td")
        #     if len(cells) > 0:
        #         transaction_dict = {}
        #         transaction_dict["Date"] = cells[0].text
        #         transaction_dict["Title"] = cells[1].text
        #         transaction_dict["Number of Shares"] = cells[2].text
        #         transaction_dict["Price"] = cells[3].text
        #         transaction_dict["Transaction"] = cells[4].text
        #         transaction_dict["Direct/Indirect"] = cells[5].text
        #         transaction_dict["Form Type"] = cells[6].text
        #         data.append(transaction_dict)

        # # Write the data to a CSV file in the "data" directory
        # filename = f"{company_name}_{insider_name}.csv"
        # filepath = os.path.join("data", filename)
        # with open(filepath, "w") as f:
        #     writer = csv.DictWriter(f, fieldnames=data[0].keys())
        #     writer.writeheader()
        #     writer.writerows(data)
