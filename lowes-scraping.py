# Author : Ben Rodrawangpai
# Date 8/30/2017
# Fix - some comments don't show up - Bug from Lowes.com
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd


def lowes_search(query):
    with requests.session() as c:
        url = 'https://www.lowes.com/search'
        query = {'searchTerm': query}
        url_link = requests.get(url, params=query)
        print(url_link.url)

        return url_link


def product_list(r):
    soup = BeautifulSoup(r.text, "html.parser")
    products_tag = soup.find_all('div', attrs={'class': 'grid-100 grid-parent v-spacing-large'})

    titles = []
    urls = []

    for product in products_tag:
        links = product.find_all("a", {"class": "display-block"})

        for link in links:
            titles.append(str(link.text).strip())
            urls.append(str('https://www.lowes.com'+link['href']))

    print("Number of Products:", len(titles))

    return titles, urls


def reviews_scraping(url):
    def product_review_request(url):
        with requests.session() as c:
            url = url
            url_link = requests.get(url)
            print(url_link.url)

            return url_link

    def product_review_extract(soup):
        # extract part
        review_titles = soup.find_all('h4', class_='reviews-list-quote grid-60 clearfix v-spacing-medium')
        reviews = soup.find_all('p', class_='reviews-helpful-text secondary-text v-spacing-medium')
        ratings = soup.find_all('meta', {'itemprop': 'ratingValue'})
        dates = soup.find_all('small', class_="darkMidGrey")

        ext_review_titles = []
        ext_reviews = []
        ext_ratings = []
        ext_dates = []

        for item in zip(review_titles, ratings, reviews,dates):
            ext_review_titles.append(str(item[0].text).strip())
            ext_ratings.append(str(item[1]['content']).strip())
            ext_reviews.append(re.sub(r'\r', '',str(item[2].text).strip()))
            ext_dates.append(str(item[3].text).strip()[12:])

        return ext_review_titles, ext_ratings, ext_reviews, ext_dates

    def product_review_number(soup):
        try:
            reviews_number = soup.find("span", class_='reviews-number h3')
            reviews_number = re.findall(r'\d+', str(reviews_number.text))
            reviews_number = int(reviews_number[0])
        except:
            print("No data")
            return 0

        print('Number of reviews: ', reviews_number)

        return reviews_number

    # Review collection
    pp = product_review_request(url + '/reviews')
    soup = BeautifulSoup(pp.text, "html.parser")

    # extract part
    reviews_number = product_review_number(soup)

    ext_review_titles = []
    ext_reviews = []
    ext_ratings = []
    ext_dates = []

    if reviews_number == 0:
        return ext_review_titles, ext_ratings, ext_reviews, ext_dates
    else:

        pp = product_review_request(url + '/reviews?sortMethod=SubmissionTime&sortDirection=desc')
        soup = BeautifulSoup(pp.text, "html.parser")
        ext_review_titles, ext_ratings, ext_reviews, ext_dates  = product_review_extract(soup)

        if reviews_number > 10:
            nloop = int(reviews_number / 10)

            for i in range(nloop):
                urll = (url + '/reviews?sortMethod=SubmissionTime&sortDirection=desc&offset=' + str((i + 1) * 10))
                pp = product_review_request(urll)
                soup = BeautifulSoup(pp.text, "html.parser")

                x, y, z, j = product_review_extract(soup)

                ext_review_titles += x
                ext_ratings += y
                ext_reviews += z
                ext_dates += j

        return ext_review_titles, ext_ratings, ext_reviews, ext_dates

### Main function ###

r = lowes_search('samsung+washer')
titles, urls = product_list(r)

for product_item in zip(titles, urls):
    review_titles, ratings, reviews, dates = reviews_scraping(product_item[1])

    product_reviews = pd.DataFrame(
        {'review_title': review_titles,
         'rating': ratings,
         'review': reviews,
         'date': dates,
         })

    product_reviews.to_csv('reviews_data/'+product_item[0]+'.csv', index=False)


