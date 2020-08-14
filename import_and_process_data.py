#%%
import pandas as pd
import quandl
from datetime import datetime,  timedelta

import plotly
import plotly.offline as py
import plotly.graph_objs as go
import bs4 as BeautifulSoup

def getprice(x):
    try:
        return btc_price_data.loc[x][indication]
    except KeyError:
        return 
btc_price_data["Date"] = btc_price_data.index
btc_price_data["theory_date"] = btc_price_data.Date.apply(lambda x: x - timedelta(days=365*4))
btc_price_data["theory"] = btc_price_data["theory_date"].apply(getprice)


def generer_html():

    #Load data form coinmarketcap or kraken
    source = "cmc"
    indication = "Close"

    if source == "kraken":
        btc_price_data = quandl.get("BCHARTS/KRAKENEUR") #KRAKENUSD
        btc_price_data = btc_price_data[btc_price_data["Open"] != 0]
        btc_price_data = btc_price_data[['Open', 'High', 'Low', 'Close']]
    elif source == "cmc":
        url = f"https://coinmarketcap.com/currencies/bitcoin/historical-data/?start=20130429&end={datetime.now().year}{datetime.now().month:02d}{datetime.now().day:02d}"
        btc_price_data = pd.read_html(url)[2]
        btc_price_data["Date"] = pd.to_datetime(btc_price_data.Date)
        btc_price_data = btc_price_data.set_index("Date")
        btc_price_data = btc_price_data[['Open*', 'High', 'Low', 'Close**']]
        btc_price_data.columns = ['Open', 'High', 'Low', 'Close']


    btc_price_data["Date"] = btc_price_data.index

    # Generate historical graph 
    fig = go.Figure([
        go.Scatter(x=btc_price_data['Date'], y=btc_price_data['Close'], name="price", hovertemplate = 'Price: %{y:$.2f}<extra></extra>',),
        go.Scatter(x=btc_price_data['Date'], y=btc_price_data['theory'], name ="Price 4years before", hovertemplate = 'Price 4 years before: %{y:$.2f}<extra></extra>',)])
    fig.update_layout(xaxis=dict(range=["2018-01-01",datetime.today()]))
    fig.update_layout(hovermode='x unified')
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white", 
            font_size=16, 
            font_family="Rockwell"
        )
    )

    # Generate indicator graph
    btc_price_data.sort_index().iloc[-1].Close
    figind = go.Figure()

    #current price
    figind.add_trace(go.Indicator(
        mode = "number+delta",
        value = btc_price_data.sort_index().iloc[-1].Close,
        number = {'prefix': "$"},
        title = {"text": "Price today<br><span style='font-size:0.8em;color:gray'>Increase in % compared to 4 years ago</span>"},
        delta = {'position': "bottom", 'reference': btc_price_data.sort_index().iloc[-1].theory, 'relative': True},
        domain = {'x': [0, 0.5], 'y': [0, 1]}))

    #price 4 year ago
    btc_price_data.sort_index().iloc[-1].Close
    figind.add_trace( go.Indicator(
        mode = "number",
        value = btc_price_data.sort_index().iloc[-1].theory,
        title = {"text": "Price 4 years ago"},
        number = {'prefix': "$"},
        delta = {'position': "bottom", 'reference': btc_price_data.sort_index().iloc[-1].theory, 'relative': True},
        domain = {'x': [0.6, 1], 'y': [0, 1]})
    )


    # Generate HTML page
    soup = BeautifulSoup.BeautifulSoup(figind.to_html()) 
    math_js = soup.find("body").find("div").find_all("script")[0] #math_js extraction
    plotly_js = soup.find("body").find("div").find_all("script")[1] # plotly.js extraction

    #extraction of the indicator
    divindicator = soup.find("body").find("div").find("div")
    scriptindicator = soup.find("body").find("div").find_all("script")[2]

    #extraction of the chart
    soup = BeautifulSoup.BeautifulSoup(fig.to_html())
    divChart = soup.find("body").find("div").find("div")
    scriptChart = soup.find("body").find("div").find_all("script")[2]

    #Creation of the final page 

    with open("index.html", "w") as f:
        f.write("<!DOCTYPE html>\n")
        f.write("<html>\n")
        f.write('<head>\n')
        f.write('<title>210 000 blocks theory</title>\n')
        f.write(str(math_js)+"\n")
        f.write(str(plotly_js)+"\n")
        f.write('</head>\n')
        f.write('<body>\n')
        f.write('<div>\n')
        f.write(str(divindicator)+"\n")
        f.write(str(scriptindicator)+"\n")
        f.write("</div>\n")
        f.write('<div>\n')
        f.write(str(divChart)+"\n")
        f.write(str(scriptChart)+"\n")
        f.write("</div>\n")
        f.write('<iframe width="1" scrolling="no" height="1" seamless="seamless" frameborder="0" src="https://analytics.redoules.synology.me/ip">')
        f.write('</body>\n')
        f.write("</html>")
