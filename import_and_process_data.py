#%%
import pandas as pd
import quandl
from datetime import datetime,  timedelta

import plotly
import plotly.offline as py
import plotly.graph_objs as go

#%%

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


# %%
btc_price_data


# %%
def getprice(x):
    try:
        return btc_price_data.loc[x][indication]
    except KeyError:
        return 
btc_price_data["Date"] = btc_price_data.index
btc_price_data["theory_date"] = btc_price_data.Date.apply(lambda x: x - timedelta(days=365*4))
btc_price_data["theory"] = btc_price_data["theory_date"].apply(getprice)



# %%
btc_price_data["Date"] = btc_price_data.index


fig = go.Figure([
    go.Scatter(x=btc_price_data['Date'], y=btc_price_data['Close'], name="price", hovertemplate = 'Price: %{y:$.2f}<extra></extra>',),
    go.Scatter(x=btc_price_data['Date'], y=btc_price_data['theory'], name ="Price 4years before", hovertemplate = 'Price 4 years before: %{y:$.2f}<extra></extra>',),
    ])
    
#fig.update_layout(yaxis_type="log")
fig.update_layout(xaxis=dict(range=["2018-01-01",datetime.today()]))
fig.update_layout(hovermode='x unified')
fig.update_layout(
    hoverlabel=dict(
        bgcolor="white", 
        font_size=16, 
        font_family="Rockwell"
    )
)

#%%

btc_price_data.sort_index().iloc[-1].Close
figind = go.Figure()


figind.add_trace(go.Indicator(
    mode = "number+delta",
    value = btc_price_data.sort_index().iloc[-1].Close,
    number = {'prefix': "$"},
    title = {"text": "Price today<br><span style='font-size:0.8em;color:gray'>Increase in % compared to 4 years ago</span>"},
    delta = {'position': "bottom", 'reference': btc_price_data.sort_index().iloc[-1].theory, 'relative': True},
    domain = {'x': [0, 0.5], 'y': [0, 1]}))



btc_price_data.sort_index().iloc[-1].Close
figind.add_trace( go.Indicator(
    mode = "number",
    value = btc_price_data.sort_index().iloc[-1].theory,
    title = {"text": "Price 4 years ago"},
    number = {'prefix': "$"},
    delta = {'position': "bottom", 'reference': btc_price_data.sort_index().iloc[-1].theory, 'relative': True},
    domain = {'x': [0.6, 1], 'y': [0, 1]})
)

#figind.update_layout(paper_bgcolor = "lightgray")
figind.show()


# %%
import bs4 as BeautifulSoup


soup = BeautifulSoup.BeautifulSoup(figind.to_html())
math_js = soup.find("body").find("div").find_all("script")[0]
plotly_js = soup.find("body").find("div").find_all("script")[1]

divindicator = soup.find("body").find("div").find("div")
scriptindicator = soup.find("body").find("div").find_all("script")[2]


soup = BeautifulSoup.BeautifulSoup(fig.to_html())
divChart = soup.find("body").find("div").find("div")
scriptChart = soup.find("body").find("div").find_all("script")[2]

# %%

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
    f.write('</body>\n')
    f.write("</html>")
# %%

# %%

# %%
