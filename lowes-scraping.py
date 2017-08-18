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

        ext_review_titles = []
        ext_reviews = []
        ext_ratings = []

        for item in zip(review_titles, ratings, reviews):
            ext_review_titles.append(str(item[0].text).strip())
            ext_ratings.append(str(item[1]['content']).strip())
            ext_reviews.append(re.sub(r'\r', '',str(item[2].text).strip()))
            # Matches Unicode whitespace characters (which includes [ \t\n\r\f\v],
            # https://stackoverflow.com/questions/41896322/how-to-remove-all-kind-of-linebreaks-or-formattings-from-strings-in-python

        return ext_review_titles, ext_ratings, ext_reviews

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

    if reviews_number == 0:
        return ext_review_titles, ext_ratings, ext_reviews
    else:
        ext_review_titles, ext_ratings, ext_reviews = product_review_extract(soup)

        if reviews_number > 10:
            nloop = int(reviews_number / 10)

            for i in range(nloop):
                urll = (url + '/reviews?offset=' + str((i + 1) * 10))
                pp = product_review_request(urll)
                soup = BeautifulSoup(pp.text, "html.parser")

                x, y, z = product_review_extract(soup)

                ext_review_titles += x
                ext_ratings += y
                ext_reviews += z

        return ext_review_titles, ext_ratings, ext_reviews

### Main function ###

r = lowes_search('samsung+washer')
titles, urls = product_list(r)

for product_item in zip(titles, urls):
    review_titles, ratings, reviews = reviews_scraping(product_item[1])

    product_reviews = pd.DataFrame(
        {'review_titles': review_titles,
         'ratings': ratings,
         'reviews': reviews
         })

    product_reviews.to_csv('review_data/'+product_item[0]+'.csv', index=False)
