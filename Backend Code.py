import psycopg2
from tabulate import tabulate
import smtplib
import requests 
from tabulate import tabulate #library to create tables for formatting output
from bs4 import BeautifulSoup 
from csv import writer 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

url = "https://newyork.craigslist.org/search/wri?"
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
			host = '127.0.0.1', #the server name or IP address on which PostgreSQL is running
			database = '', #name of the database
			user = '', #The username you use to work with PostgreSQL. The default username for the PostgreSQL database is postgres.
			password = '')

		#create a cursor object to use queries
		cursor = connect.cursor()

		#execute queries
		# cursor.execute('drop table jobs;') #IF YOU UNCOMMENT THIS, IT WILL ONLY SHOW THE SECOND PAGE ON THE DATABASE
		cursor.execute("select * from information_schema.tables where table_name=%s", ('jobs',))
		table_present = bool(cursor.rowcount)
		if not table_present:
			cursor.execute('create table jobs(title varchar(500), date varchar(500), location varchar(500), attributes varchar(500), link varchar(500));')

		with open('jobs.csv', 'a') as csv_file: 
			csv_writer = writer(csv_file)
			headers = ['number','title','date','location','attributes','link'] 
			csv_writer.writerow(headers)
			for job in jobs:
				link = job.find('a')['href'] 
				postgreSQL_select_Query = "select count(*) > 0 from jobs where link = %s"
				cursor.execute(postgreSQL_select_Query, (link,))
				records = cursor.fetchone()
				string = str(records)
				if string == "(False,)": #if the link is not already in the database
					title = job.find(class_="result-title").getText() 
					date = job.find(class_="result-date").getText()
					location_tag = job.find(class_="result-hood") 
					location = location_tag.getText() if location_tag else "N/A"

					# NAVIGATE TO THE JOB DESCRIPTION PAGE INSIDE EACH JOB
					job_response = requests.get(link) 
					job_soup = BeautifulSoup(job_response.content,'html.parser') 
					job_attributes_tag = job_soup.find(class_="attrgroup") 
					job_attributes = job_attributes_tag.getText() if job_attributes_tag else "N/A"
					job_counter += 1
					csv_writer.writerow([job_counter,title,date,location,job_attributes,link])	

					cursor.execute('Insert into jobs(title,date,location,attributes,link) values (%s, %s,%s, %s,%s);', (title,date,location,job_attributes,link))
					cursor.execute('Select * from jobs;')
					# records = cursor.fetchall()
					# print(tabulate(records, headers=['title', 'date', 'location', 'attributes', 'link'], tablefmt='psql')) #print in a pqsl tabl format (there are other formats: you can reger to the tabulate webpage)


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

def sendMail():
	#cannot be a gmail account. Unsure what other email types dont work, but outlook works for sure.
	sender_email = ''
	password = ''
	with open('mailinglist.txt') as f:
		for i in f:	
			try:
				email_receiver = i.lower().rstrip()
				msg = MIMEMultipart()
				msg['From'] = sender_email
				msg['To'] = email_receiver
				msg['Subject'] = "This Week's Job Listing!"

				body = "Dont forget to check out this week's job listing. If you do not see any listings in this week's attatchment, no new jobs have been posted. See attatchment for more details!"
				msg.attach(MIMEText(body,'plain'))

				filename = 'jobs.csv'
				attachment = open(filename,'rb')

				part = MIMEBase('application','octet-stream')
				part.set_payload((attachment).read())
				encoders.encode_base64(part)
				part.add_header('Content-Disposition',"attachment; filename= " + filename)

				msg.attach(part)
				text = msg.as_string()
				server = smtplib.SMTP('smtp-mail.outlook.com', 587)
				server.starttls()
				server.login(sender_email,password)
				server.sendmail(sender_email,email_receiver,text)
				server.quit()

			except:
				print("Mailing went south...")	

printData(url,job_counter,page_number)
sendMail()
# finally:
# 	connect.commit() 
# 	cursor.close()
# 	connect.close()