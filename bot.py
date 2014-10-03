
import sys, datetime, requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Fetch website HTML and parse jobs data out of it
def fetch(keyword):

	SEARCH_URL = 'https://weworkremotely.com/jobs/search?term=%s'
	CSS_QUERY = '#category-2 > article > ul > li a'

	response = requests.get(SEARCH_URL % (keyword), timeout=10)

	if response.status_code != requests.codes.ok:
		return False

	html = BeautifulSoup(response.text)
	jobs = html.select(CSS_QUERY)

	# If there's only one item in the list, then it's just a category
	if len(jobs) <= 1:
		return False

	# We don't need the category...
	del jobs[-1]

	months = {
		'Jan': '01',
		'Feb': '02',
		'Mar': '03',
		'Apr': '04',
		'May': '05',
		'Jun': '06',
		'Jul': '07',
		'Aug': '08',
		'Sep': '09',
		'Oct': '10',
		'Nov': '11',
		'Dec': '12'
	};
	current_date = datetime.datetime.now()

	result = []

	for job in jobs:
		job_id = job['href'].strip('/').split('/')[1].strip()
		if job_id == '':
			continue
		job_details = job.find_all('span')
		# We should have exactly 3 "span" tags
		if len(job_details) != 3:
			continue
		date_parts = ' '.join(job_details[2].string.split()).split(' ')
		# Ugly hack, I know... but works perfectly
		if len(date_parts[1]) == 1:
			date_parts[1] = str('0' + date_parts[1])
		result.append({
			'job_id': job_id,
			'title': job_details[1].string.strip(),
			'company': job_details[0].string.strip(),
			'date': '%s-%s-%s' % (current_date.year, months[date_parts[0]], date_parts[1])
		})

	return result

# Insert jobs in the database
def insert(jobs):
	db = MongoClient()
	for job in jobs:
		db.we_work_remotely.jobs.update(
			{
				'job_id': job['job_id']
			},
			{
				'$setOnInsert': job
			},
			True
		)


# Helper function to terminate program execution gracefully
def exit_program(message='You shall not pass!'):
	print(message)
	sys.exit(0)

# Handle search keyword argument
SEARCH_TERM = 'php'
if len(sys.argv) == 2:
	SEARCH_TERM = sys.argv[1].strip()

# Main script controller
def main():
	try:
		jobs = fetch(SEARCH_TERM)
		if jobs == False:
			exit_program()
		insert(jobs)
	except:
		exit_program('Blame it on a boogie!..')

# Gimme some lovin'
if __name__ == '__main__':
	main()
