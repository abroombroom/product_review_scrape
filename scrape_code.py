@author __author__ = "Alyse Kim"

import requests
from bs4 import BeautifulSoup
from BeautifulSoup import BeautifulSoup as BS
import pandas as pd

#specify list of the webpages in interest
pages = ['https://...']

review_heading = []
review_content = []
review_rating = []
review_date = []

for page in pages:
    html = requests.get(page)
    soup = BeautifulSoup(html.text, 'html.parser')
#     ws_title = soup.title.string
#     print soup.prettify()
    all_reviews = soup.find_all('div', class_ = 'review-content')

    for review in all_reviews:
        review_heading.append(review.find('h3').text.strip())
        review_content.append(review.find('div', attrs = {'class':'review-overall'}).text.strip())
        review_rating.append(review.find('span', attrs = {'itemprop':'ratingValue'}).text.strip())
        review_date.append(str(review.find('meta', attrs = {'itemprop':'datePublished'})).split('"')[1])


data = {'Review Title' : review_heading, 'Review Content': review_content,
        'Review Rating': review_rating, 'Review Date': review_date}

#create review dataframe
review_df = pd.DataFrame(data, columns = ['Review Date','Review Title', 'Review Content', 'Review Rating'])
review_df.sort_values('Review Date', ascending = False, inplace = True)


#export to a path as csv file
review_df.to_csv('path')
