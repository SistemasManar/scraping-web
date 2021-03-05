from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq

my_url = "https://www.flipkart.com/search?q=iphone&otracker=start&as-show=on&as-off=&p%5B%5D=facets.brand%255B%255D%3DApple&p%5B%5D=facets.price_range.from%3D10000&p%5B%5D=facets.price_range.to%3DMax"

uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")

containers = page_soup.findAll("div", {"class": "_3liAhj"})
#print(len(containers))
#print(soup.prettify(containers[0]))

container = containers[0]
#print(container.div.img["alt"])

price = container.findAll("div", {"class": "_1vC4OE"})

ratings = container.findAll("div", {"class": "hGSR34"})

filename = "prueba.csv"
f = open(filename, "w")

headers = "Product_name,Pricing,Ratings\n"
f.write(headers)

for container in containers:
    #Aqui se saca el val (probar)
    product_name = container.div.img["alt"]

    price_container = container.findAll("div", {"class": "_1vC4OE"})
    price = price_container[0].text.strip()

    rating_container = container.findAll("div", {"class": "hGSR34"})
    rating = rating_container[0].text

    print("product_name: "+product_name)
    print("price: " + price)
    print("rating: " + rating)

    #string parsing
    trim_price = ''.join(price.split(','))
    rm_rupee = trim_price.split("₹")
    add_rs_price = "Rs."+rm_rupee[1]
    split_price = add_rs_price.split('E')
    final_price = split_price[0]

    split_rating = rating.split(" ")
    final_rating = split_rating[0]

    print(product_name.replace(", ", "|") + ", "+final_price+", "+final_rating+"\n")
    f.write(product_name.replace(", ", "|") + ", "+final_price+", "+final_rating+"\n")

f.close()