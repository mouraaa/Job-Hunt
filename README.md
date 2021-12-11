# About
The pandemic sure did take a lot of our jobs and as college students, me and my friends need to pay for our tuition. Lets face it, the relief the government is providing is not enough and it will run out soon so its time to search for jobs, and quick.

The script webscrappes a craigslist link for current job offers in the area and creates a file retaining all the information relevant to each offer. It places all job listings in a database and using the mailchimp service, it automatically sends emails every week with the csv file attatchment.

You can change the link to any craigslist link as long as it is in the jobs filter. Feel free to change the location and job type then use the new link in the code. You can also modify the code by adding if statements to only output certain results from the page based on your preferences. 


![](email.png)


# Prerequisites
` pip install requests `

` pip install beaitifulsoup4 `


## Notice
Please allow for a couple of moments for the email to be received. If a few minutes have passed and you still haven't received the email, please check your spam folder as it may have found it's way over there instead.
