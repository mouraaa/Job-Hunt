import psycopg2
from tabulate import tabulate
import requests 
from tabulate import tabulate #library to create tables for formatting output
from bs4 import BeautifulSoup 
from csv import writer 

url = "https://newyork.craigslist.org/search/bus?"
job_counter = 0
page_number = 0

#print data to CSV file
def printData(url,job_counter,page_number):
	response = requests.get(url) 
	soup = BeautifulSoup(response.content, 'html.parser')
	jobs = soup.findAll(class_="result-info") 


	try:
		#connect to the database
		connect = psycopg2.connect(
			host = '', #the server name or IP address on which PostgreSQL is running
			database = '', #name of the database
			user = '', #The username you use to work with PostgreSQL. The default username for the PostgreSQL database is postgres.
			password = '')

		#create a cursor object to use queries
		cursor = connect.cursor()

		#execute queries
		# cursor.execute('drop table jobs;')
		cursor.execute("select * from information_schema.tables where table_name=%s", ('jobs',))
		table_present = bool(cursor.rowcount)
		if not table_present:
			cursor.execute('create table jobs(title varchar(500), date varchar(500), location varchar(500), attributes varchar(500), link varchar(500));')

		with open('jobs.csv', 'a') as csv_file: 
			csv_writer = writer(csv_file)
			headers = ['number','title','date','location','attributes','link'] 
			csv_writer.writerow(headers)
			for job in jobs:
				title = job.find(class_="result-title").getText() 
				date = job.find(class_="result-date").getText()
				location_tag = job.find(class_="result-hood") 
				location = location_tag.getText() if location_tag else "N/A"
				link = job.find('a')['href'] 
																			 

				#NAVIGATE TO THE JOB DESCRIPTION PAGE INSIDE EACH JOB
				job_response = requests.get(link) 
				job_soup = BeautifulSoup(job_response.content,'html.parser') 
				job_attributes_tag = job_soup.find(class_="attrgroup") 
				job_attributes = job_attributes_tag.getText() if job_attributes_tag else "N/A"
				job_counter += 1
				csv_writer.writerow([job_counter,title,date,location,job_attributes,link])	

				cursor.execute('Insert into jobs(title,date,location,attributes,link) values (%s, %s,%s, %s,%s);', (title,date,location,job_attributes,link))
				cursor.execute('Select * from jobs;')
				records = cursor.fetchall()
				print(tabulate(records, headers=['title', 'date', 'location', 'attributes', 'link'], tablefmt='psql')) #print in a pqsl tabl format (there are other formats: you can reger to the tabulate webpage)


			connect.commit() 
			cursor.close()
			connect.close()

		page_number += 1
		print("Page " + str(page_number) + " completed")	

		#NAVIGATE TO THE NEXT PAGE
		nextPage = soup.find(class_='button next') 
		if nextPage.get('href'):
			url = 'https://newyork.craigslist.org' + nextPage.get('href')
			printData(url,job_counter,page_number)

	except:
		print("Something went wrong while connecting or querying the database")

printData(url,job_counter,page_number)
# finally:
# 	connect.commit() 
# 	cursor.close()
# 	connect.close()
