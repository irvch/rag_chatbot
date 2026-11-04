import pdfkit
import os
# pdfkit.from_file('test_10k.htm', 'test_10k.pdf')
# pdfkit.from_file('test_10k.htm', 'test_10k.pdf', options={'page-size': 'Letter'})

# pdfkit.from_url('https://www.sec.gov/ix?doc=/Archives/edgar/data/0001318605/000162828024002390/tsla-20231231.htm', 'test_10k2.pdf')


directory = "./8k_filings"
count = 0
for filename in os.listdir(directory):
    count += 1
    print(count)
    f = os.path.join(directory, filename)
    # print(f)
    # checking if it is a file
    if os.path.isfile(f):
        # print(f)
        name = filename[:-4]
        # print(name)
        try:
          pdfkit.from_file(f'{f}', f'./8k_filings_pdf/{name}.pdf')
        except:
          print("error")

print(len(os.listdir("./8k_filings_pdf")))
print(len(os.listdir("./8k_filings")))

# print(len(os.listdir("./10k_filings_pdf")))
# print(len(os.listdir("./10k_filings")))
        