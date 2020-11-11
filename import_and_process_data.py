#%%
import pandas as pd
import quandl
from datetime import datetime,  timedelta

import plotly
import plotly.offline as py
import plotly.graph_objs as go
import bs4 as BeautifulSoup




def generer_html():
    #Load data form coinmarketcap or kraken
    source = "yahoo"
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
    elif source == "yahoo":
        url = f'https://query1.finance.yahoo.com/v7/finance/download/BTC-USD?period1=1410912000&period2={int(datetime.now().timestamp())}&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true'
        btc_price_data = pd.read_csv(url)
        btc_price_data["Date"] = pd.to_datetime(btc_price_data.Date)
        btc_price_data = btc_price_data.set_index("Date")
        btc_price_data = btc_price_data[['Open', 'High', 'Low', 'Close']]
        btc_price_data.columns = ['Open', 'High', 'Low', 'Close']


    def getprice(x):
        try:
            return btc_price_data.loc[x][indication]
        except KeyError:
            return 
    btc_price_data["Date"] = btc_price_data.index
    btc_price_data["theory_date"] = btc_price_data.Date.apply(lambda x: x - timedelta(days=365*4))
    btc_price_data["theory"] = btc_price_data["theory_date"].apply(getprice)

    # Generate historical graph 
    fig = go.Figure([
        go.Scatter(x=btc_price_data['Date'], y=btc_price_data['Close'], name="price", hovertemplate = 'Price: %{y:$.2f}<extra></extra>',),
        go.Scatter(x=btc_price_data['Date'], y=btc_price_data['theory'], name ="Price 4years before", hovertemplate = 'Price 4 years before: %{y:$.2f}<extra></extra>',)])
    fig.update_layout(xaxis=dict(range=["2017-04-28",datetime.today()]))
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
        title = {"text": f"Price today<br><span style='font-size:0.8em;color:gray'>Increase in % compared to 4 years ago</span>"},
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
    soup = BeautifulSoup.BeautifulSoup(figind.to_html(), "lxml") 
    math_js = soup.find("body").find("div").find_all("script")[0] #math_js extraction
    plotly_js = soup.find("body").find("div").find_all("script")[1] # plotly.js extraction

    #extraction of the indicator
    divindicator = soup.find("body").find("div").find("div")
    scriptindicator = soup.find("body").find("div").find_all("script")[2]

    #extraction of the chart
    soup = BeautifulSoup.BeautifulSoup(fig.to_html(), "lxml")
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
        f.write('<section class="banner" style="width: 100%;padding:00px 0;text-align: center;background: #FFFFFF;color: black;"><div><h1 style="font-size: 2.8em;">210000 blocks theory dashboard</h1><p>The <a href="https://www.whatisbitcoin.com/what-is/210000-block-hodl-theory">210,000 blocks HOLD theory</a> is the idea that you should hold any given bitcoin for at least 210,000 blocks from when it was transacted because as of today\'s date, there are no transactions with a lower fiat valuation 210,000 blocks after that transaction is sent.</p><p>Dashboard updated daily.</p></div><hr style ="display: block;    height: 1px;    border: 0;    border-top: 1px solid #ccc;    margin: 1em 0;    padding: 0;"/></section>\n')
        f.write('<div>\n')
        f.write(str(divindicator)+"\n")
        f.write(str(scriptindicator)+"\n")
        f.write(f"<span style='font-size:0.8em;color:gray'>Updated on {datetime.now().day}-{datetime.now().month}-{datetime.now().year} at {datetime.now().hour}:{datetime.now().minute} (UTC+1)</span><br>")
        f.write("</div>\n")
        f.write('<div><p>The 210000 blocks HOLD theory is valid if the red line is below the blue line !</p></div>\n')
        f.write('<div>\n')
        f.write(str(divChart)+"\n")
        f.write(str(scriptChart)+"\n")
        f.write("</div>\n")
        f.write('<iframe width="1" scrolling="no" height="1" seamless="seamless" frameborder="0" src="https://analytics.redoules.synology.me/ip">')
        f.write('</body>\n')
        f.write("</html>")

if __name__ == '__main__':
    generer_html()

# %%
