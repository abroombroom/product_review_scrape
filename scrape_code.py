# @author __author__ = "Alyse Kim"

import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict
import re
import json
import os
import arrow


class SnoozeReviews:

	def __init__(self, base_url='https://www.productreview.com.au/p/snooze.html'):

		self.today = arrow.utcnow().to('Australia/Sydney').format('YYYYMMDD')
		self.base_url = base_url
		self.total_reviews = None
		self.review_counts = defaultdict()
		self.reviews = []
		self.authors = []

		if not os.path.exists('data'):
			os.mkdir('data')

		self.data_dir = 'data'

	def get_reviews(self):

		pages_ = int(re.search(r'\d+\)', BeautifulSoup(requests.get('https://www.productreview.com.au/p/snooze/2.html').text, 'html.parser').find('div', class_='item-header-summary-title').text.lower().strip()).group(0).split(')')[0])
		
		for p in range(1, pages_ + 1):

			sp = BeautifulSoup(requests.get(f'https://www.productreview.com.au/p/snooze/{p}.html').text, 'html.parser')

			if p == 1:

				for _ in sp.find_all('span', itemprop='ratingCount'):
	
					try:
						self.total_reviews = int(_.text.strip())
					except:
						continue
	
				print(f'found {self.total_reviews} snooze reviews...')

				for _ in sp.find_all('li', class_='rating-overview-row'):
			
					for r_, d_ in zip(_.find_all('div', class_='rate'), _.find_all('div', class_='count')):

						self.review_counts[r_.text.lower()] = int(d_.text.lower())

				self.reviews.append(self.review_counts)

			for review in sp.find_all('div', class_='review'):

				this_review = defaultdict()

				auth = review.find('a', itemprop='author')

				if not auth:
					continue

				lnk = auth['href']

				this_review['id'] = re.search(r'\d+', lnk).group(0)
				this_review['author'] = auth.text.lower().strip()
				this_review['author_link'] = 'https://www.productreview.com.au' + lnk

				shop = defaultdict()

				shop_line = review.find('p', class_='review-labels')

				if shop_line and ('verified' in shop_line.text.lower()):
					this_review['verified'] = 'yes'
				else:
					this_review['verified'] = 'no'

				try:
					shop['state'], shop['suburb'] = [_.split(':')[-1].strip() 
								for _ in shop_line.text.strip().lower().split(',')]
				except:
					pass

				this_review['shop'] = shop

				this_review['title'] = review.find('h3', itemprop='name').text.lower().strip()

				try:
					rating_ = int(review.find('span', itemprop='ratingValue').text.strip())
				except:
					rating_ = None

				this_review['rating'] = rating_

				this_review['date'] = review.find('meta', itemprop='datePublished')['content']

				this_review['text'] = review.find('div', itemprop='description').text.lower().strip()

				self.reviews.append(this_review)

			print(f'pages: {p:02d}, reviews: {len(self.reviews):03d}...')


		json.dump(self.reviews, open(os.path.join(self.data_dir, f'reviews_{self.today}.json'), 'w'))

		return self

	def get_reviewers(self):

		print('collecting reviewer information...')

		for review in self.reviews:

			this_reviewer = defaultdict()

			try:
				sp = BeautifulSoup(requests.get(review['author_link']).text, 'html.parser')

				for b in sp.find_all('a'):
					try:
						this_reviewer['id'] = b['rel'].pop()
						break
					except:
						continue 

				this_reviewer['name'] = sp.find('div', class_='profile-summary').find('img')['alt'].lower().strip()

				# dates are like August 27, 2018

				for l in sp.find('div', class_='user-info-content').find_all('dd'):

					if re.match(r'\d{4}', l.text):
						this_reviewer['joined'] = arrow.get(''.join([_ for _ in l.text.title() 
													if _ not in '.,']), 'MMMM D YYYY')
					elif {'act', 'nsw', 'vic', 'qld', 'sa', 'nt', 'tas'} & set(l.text.lower().split()):
						this_reviewer['location'] = l.text.lower()

				for _ in sp.find_all('a', class_='btn'):

					if 'review' in _.text.lower():
						this_reviewer['number_reviews'] = re.search(r'\d+', _.text).group(0)
						break

				self.authors.append(this_reviewer)

			except:
				continue

		json.dump(self.authors, open(os.path.join(self.data_dir, f'authors_{self.today}.json'), 'w'))

		return self

if __name__ == '__main__':

	sr = SnoozeReviews() \
		.get_reviews().get_reviewers()
