## Financial News Chatbot -- Big Data Science Final Project
by Irvin Chadraa, Chris Xu, and Jerry Yao

The "source_code" folder contains code written entirely in Python for acquiring the data in our model's knowledge base as well as the code to run the chatbot itself. All code can be separately run within individual Jupyter Notebooks on Google Colab. For recreating results, begin by running the Glassdoor scraping code since the SEC scraper needs the list of companies made by findTop500.py. Any necessary libraries and dependencies should be ideally be accounted for within the notebooks for each file. If not, a simple "pip install {insert_name}" should suffice in the command line interface for .py files or run "!pip install {insert_name}" in a code block for .ipynb files.

Ensure that you are connected to the GPU in Colab for the chatbot code since the language model will not run properly without it. 

## Files

### For Glassdoor:
- findTop500.py -- find list of company names
- findId.ipynb -- find all Glassdoor Ids
- findReview.ipynb -- find all reviews
- cleanUp.py -- clean up data

### For SEC reports:
- sec_scraping.ipynb -- collect 10-K and 8-K reports using SEC API
- html_to_pdf.py -- convert HTML reports to PDF form

### For Chatbot:
- final_chatbot.ipynb -- the pipeline for creating the chatbot using retrievalQA on our dataset
- auto_gptq-0.4.0+cu118-cp310-cp310-linux_x86_64.whl -- Python package in a WHL file for AutoGPTQ
- db -- folder containing indices for our FAISS database


All data on Glassdoor reviews and SEC reports in our knowledge base is contained within the "data" folder. Out of concern for space limitations, we use only the "test_pdfs" and "test_txts" subfolders which contain only the information set for the two companies we compared: NVIDIA and AMD.

The "reports" folder contains our final write ups. "final_report.pdf" is our writeup describing the process of developing our chatbot. Meanwhile, "report_2_appendix.pdf" contains the same initial writeup but includes an appendix with the full responses of both our chatbot and the customized ChatGPT4 model we used as a baseline.


# CODE
## 1. collect and clean Glassdoor reviews

### i. collect top 500 company list
1. found a table of top500 company at https://www.50pros.com/fortune500 (unable to download the html table)
2. used developer tool to collect the source code snippet for the table, saved in top500.html
3. used findTop500.py extracted all information to top500.csv and top500.json

### ii. scrape Glassdoor ID for each company
1. all Glassdoor lives in following url, so we need to extract IDs first: https://www.glassdoor.com/Reviews/{company}-Reviews-E{id}.htm
2. found the seach autocomplete always returns Glassdoor name and id as search suggestion, sent a GET request to the following url will return its ID: https://www.glassdoor.com/searchsuggest/typeahead?numSuggestions=8&source=GD_V2&version=NEW&rf=full&fallback=token&input={companyName}
3. Pure python GET request will be detected and blocked
4. Used Scrapfly API service to bypass Glassdoor anti-scraping system.
5. 18 out of 500 IDs were not found, manually added these ID
    - most are because name mismatch or API quota cost exceed the max budget I set
    - more are found missing in later steps, because search suggestion bugs (like many company containing the keyword "banks" will be suggested to one id)

### iii. scrape Glassdoor reviews (20 reviews per company)
1. used following url as target: https://www.glassdoor.com/Reviews/{company}-Reviews-E{id}.htm
2. Extracted hidden web cache from Glassdoor HTML (Apollo GraphQL)
3. Unpacked and extracted reviews section
4. Repeat step 2 and 3 for page 2
5. Divided 500 companies to 10 batchs. After 50 companies every time, save and concat the data to top500_reviews.json
    - On average, each company(2 pages) took 30 seconds
6. after every batch, display companies that has errors. And fixed all name-id mismatch errors.
    - There are issues with Glassdoor unique urls format. For Alphabet Inc. Glassdoor uses Google as company name.
7. Redo all the error companies in next batch
8. In total, running this step took 5 hours 

### iv. Clean up scraped data
1. data from last step has 1.5 millions lines, still too much trivial information after clean up. And it is hard to get a good result from this in a complicated Json-strucutured data after testing. so the data is required to be cleaned and reorganized again.
2. extract useful data and store them in top500_reviews_clean.json
    - cleaned up trivial key names like "_typename"
    - modified key names to human readable format. Like "ratingBusinessOutlook" to "Business Outlook Rating"; "_5" to "5"
3. convert all the json information to to English text with the same format. This is much more readable to both human and LLM. And it is easier to perform sentiment analysis if needed.


## 2. collect SEC reports

### i. collect URLs for reports
1. create list of company tickers from top500.json file
2. acquire URLs with SEC Filings Query API
    - query most recent 10-K reports based on tickers
    - query five most recent 8-K reports based on tickers
3. save URLs into text files
    - save 10-K URLs into "10k_filings_url.txt"
    - save 8-K URLs into "8k_filings_url.txt"

### ii. save HTML files of reports
1. use SEC Filings Extract and Render API to download filings
    - save 10-K HTMLs into "10k_filings" folder
    - save 8-K HTMLs into "8k_filings" folder

### iii. save PDF files of reports
1. use pdfkit and wkhtmltopdf to save info into PDF form

## 3. create and run chatbot
### i. setup
1. install dependencies
2. Make sure you are using Colab GPU (T4 works fine)
3. log into HuggingFace for access to models
4. mount onto Google Drive for access to data
5. install autogptq library if not present
### ii. embeddings
1. load text splitter and embeddings model
2. get FAISS knowledge vector store database
    - if knowledge base exists already, run "load_knowledgeBase()"
    - if knowledge base is empty or new data is added, run "load_text()" and "train_knowledgeBase()"
### iii. create text generation pipeline
1. load quantized LLaMA-2 language model for running on GPU
2. load tokenizer that uses same quantized language model
3. load streamer which uses above tokenizer
4. set up HuggingFace pipeline with model, tokenizer, streamer, and parameters

### iv. set up retrievalQA chain for response
1. write default system prompt
2. write prompt template taking in context and question
3. write function for getting responses
    - conduct similarity search on FAISS database
    - convert subset of documents into FAISS index 
    - use index as retriever for QA chain
    - write retrievalQA chain with LLM, above retriever, and prompt as argument

### v. ask the model a question
