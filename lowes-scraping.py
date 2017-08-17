import requests
import re
from bs4 import BeautifulSoup


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

    return titles,urls


def review_extract(urls):

    def product_review(url):
        with requests.session() as c:
            url = url
            url_link = requests.get(url + '/reviews')
            print(url_link.url)

            return url_link

    pp = product_review(urls[0])
    soup = BeautifulSoup(pp.text, "html.parser")

    reviews_number = soup.find("span", class_='reviews-number h3')
    reviews_number = re.findall(r'\d+', str(reviews_number.text))
    reviews_number = int(reviews_number[0])

    reviews = soup.find_all('p', class_='reviews-helpful-text secondary-text v-spacing-medium')

    for review in reviews:
        print(str(review.text).strip())

### Main ###

r = lowes_search('samsung+washer')
titles, urls = product_list(r)

review_extract(urls)
