
import sys, requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Fetch website HTML and parse jobs data out of it
def fetch():

	SEARCH_TERM = 'php'
	SEARCH_URL = 'https://weworkremotely.com/jobs/search?term=%s'
	CSS_QUERY = '#category-2 > article > ul > li a'

	response = requests.get(SEARCH_URL % (SEARCH_TERM), timeout=10)

	if response.status_code != requests.codes.ok:
		return False

	html = BeautifulSoup(response.text)
	jobs = html.select(CSS_QUERY)

	# If there's only one item in the list, then it's just a category
	if len(jobs) <= 1:
		return False

	# We don't need the category...
	del jobs[-1]

	result = []

	for job in jobs:
		result.append({
			'job_id': job['href'].strip('/').split('/')[1],
			'title': job.find('span.title'),
			'company': job.find('span.company'),
			'date': job.find('span.date')
		})

	return result

def insert():
	pass

# Main script controller
def main():
	jobs = fetch()
	if jobs == False:
		print('You shall not pass!')
		sys.exit(0)
	print(jobs)

# Blame it on a boogie!
if __name__ == '__main__':
	main()
