import parsel
import json
import pandas as pd

def findTop500():
  with open('top500.html') as f:
    html = f.read()

  sel = parsel.Selector(text=html)
  
  # extract the table rows
  rows = sel.xpath('//table/tbody/tr')

  companies = {}
  company_list = []
  company_names = []

  for row in rows:
    rank = row.xpath('td[1]/text()').get()
    company = row.xpath('td[2]/text()').get()
    industry = row.xpath('td[3]/text()').get()
    city = row.xpath('td[4]/text()').get()
    state = row.xpath('td[5]/text()').get()
    zip = row.xpath('td[6]/text()').get()
    website = row.xpath('td[7]/text()').get()
    employees = row.xpath('td[8]/text()').get()
    revenue = row.xpath('td[9]/text()').get()
    valuation = row.xpath('td[10]/text()').get()
    profit = row.xpath('td[11]/text()').get()
    ticker = row.xpath('td[13]/text()').get()
    ceo = row.xpath('td[14]/text()').get()
    companies[company] = {
      'rank': rank,
      'industry': industry,
      'city': city,
      'state': state,
      'zip': zip,
      'website': website,
      'employees': employees,
      'revenue': revenue,
      'valuation': valuation,
      'profit': profit,
      'ticker': ticker,
      'ceo': ceo
    }
    company_list.append([rank, company, industry, city, state, zip, website, employees, revenue, valuation, profit, ticker, ceo])
    company_names.append(company)
  columns = ['rank', 'company', 'industry', 'city', 'state', 'zip', 'website', 'employees', 'revenue', 'valuation', 'profit', 'ticker', 'ceo']
  df = pd.DataFrame(company_list, columns=columns)
  df.to_csv('top500.csv', index=False)
  df.to_json('top500.json', orient='records', indent=2)
  with open('top500.txt', 'w') as f:
    for company in company_names:
      f.write(company + '\n')


if __name__ == '__main__':
  findTop500()