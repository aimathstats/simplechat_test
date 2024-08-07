import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import numpy as np
from pytrends.request import TrendReq

st.set_page_config(layout="wide")

# PDFからのテーブル取得と可視化：都道府県別コロナ定点観測の折れ線
import fitz
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 対象ページのURL
url = "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000121431_00461.html"
response = requests.get(url)
response.raise_for_status()  # エラーが発生した場合、例外を投げる

# BeautifulSoupでHTMLを解析
soup = BeautifulSoup(response.text, "html.parser")

# すべてのリンクを検索
links = soup.find_all("a")

# PDFファイルのURLを抽出
pdf_urls = [link.get("href") for link in links if link.get("href") and ".pdf" in link.get("href")]

# 相対URLを絶対URLに変換
absolute_pdf_urls = [urljoin(url, pdf_url) for pdf_url in pdf_urls]

# 最新のPDFのURLを取得
latest_pdf_url = absolute_pdf_urls[0] if absolute_pdf_urls else None
#latest_pdf_url = pdf_urls[0] if pdf_urls else None
st.write(f"最新のPDFのURL: {latest_pdf_url}")

# 取得したPDFアドレスからテーブル取得
#url = 'https://www.mhlw.go.jp/content/001282915.pdf'
url = latest_pdf_url
response = requests.get(url)
response.raise_for_status() # エラーになった時用

# ローカルにPDFファイルを保存
with open('covid.pdf', 'wb') as f:
    f.write(response.content) 

doc = fitz.open('covid.pdf', filetype="pdf")  
page_1 = doc[2]
pdf_text_1 = page_1.get_text("text")
tabs = page_1.find_tables()

table_data = tabs[0].extract()
columns0 = table_data[0] 
columns = table_data[1]
columns[0] = "都道府県" 
data_rows = table_data[2:]
df = pd.DataFrame(data_rows, columns=columns)
#st.table(df)
st.subheader('PDFからのデータフレーム')
st.write(df)

prefectures = df["都道府県"].unique().tolist()
selected_prefecture = st.selectbox("都道府県を選択してください:", prefectures, index=prefectures.index("京 都 府"))
prefecture_data = df[df["都道府県"] == selected_prefecture]
prefecture_data = prefecture_data.melt(id_vars=["都道府県"], var_name="週", value_name="値").drop(columns="都道府県")

fig29 = px.line(prefecture_data, x="週", y="値", title=f"{selected_prefecture}の週ごとのデータ")
st.subheader('2024年コロナ都道府県別定点観測:  ' + selected_prefecture)
st.plotly_chart(fig29)


# network graph
import networkx as nx
G = nx.random_geometric_graph(200, 0.125)
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = G.nodes[edge[0]]['pos']
    x1, y1 = G.nodes[edge[1]]['pos']
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

node_x = []
node_y = []
for node in G.nodes():
    x, y = G.nodes[node]['pos']
    node_x.append(x)
    node_y.append(y)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        # colorscale options
        #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
        colorscale='YlGnBu',
        reversescale=True,
        color=[],
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        ),
        line_width=2))

node_adjacencies = []
node_text = []
for node, adjacencies in enumerate(G.adjacency()):
    node_adjacencies.append(len(adjacencies[1]))
    node_text.append('# of connections: '+str(len(adjacencies[1])))

node_trace.marker.color = node_adjacencies
node_trace.text = node_text

fig28 = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='<br>Network graph made with Python',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="Python code: <a href='https://plotly.com/python/network-graphs/'> https://plotly.com/python/network-graphs/</a>",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
st.subheader('network graph')
st.plotly_chart(fig28)

# contour plot
fig27 = go.Figure(data=go.Contour(
            z=[[10, 10.625, 12.5, 15.625, 20],
            [5.625, 6.25, 8.125, 11.25, 15.625],
            [2.5, 3.125, 5., 8.125, 12.5],
            [0.625, 1.25, 3.125, 6.25, 10.625],
            [0, 0.625, 2.5, 5.625, 10]]
            ))
st.subheader('contour plot')
st.plotly_chart(fig27)

# ridgeline plot
from plotly.colors import n_colors
# 12 sets of normal distributed random data, with increasing mean and standard deviation
np.random.seed(1)
data = (np.linspace(1, 2, 12)[:, np.newaxis] * np.random.randn(12, 200) +
            (np.arange(12) + 2 * np.random.random(12))[:, np.newaxis])
colors = n_colors('rgb(5, 200, 200)', 'rgb(200, 10, 10)', 12, colortype='rgb')

fig26 = go.Figure()
for data_line, color in zip(data, colors):
    fig26.add_trace(go.Violin(x=data_line, line_color=color))

fig26.update_traces(orientation='h', side='positive', width=3, points=False)
fig26.update_layout(xaxis_showgrid=False, xaxis_zeroline=False)
st.subheader('ridgeline plot')
st.plotly_chart(fig26)


# violin plot
df = px.data.tips()
fig23 = px.violin(df, y="total_bill")
fig24 = px.violin(df, y="total_bill", box=True, # draw box plot inside the violin
                points='all', # can be 'outliers', or False
               )

st.subheader('violin plot')
st.plotly_chart(fig23)
st.plotly_chart(fig24)

# another violin plot
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/violin_data.csv")
pointpos_male = [-0.9,-1.1,-0.6,-0.3]
pointpos_female = [0.45,0.55,1,0.4]
show_legend = [True,False,False,False]

fig25 = go.Figure()
for i in range(0,len(pd.unique(df['day']))):
    fig25.add_trace(go.Violin(x=df['day'][(df['sex'] == 'Male') &
                                        (df['day'] == pd.unique(df['day'])[i])],
                            y=df['total_bill'][(df['sex'] == 'Male')&
                                               (df['day'] == pd.unique(df['day'])[i])],
                            legendgroup='M', scalegroup='M', name='M',
                            side='negative',
                            pointpos=pointpos_male[i], # where to position points
                            line_color='lightseagreen',
                            showlegend=show_legend[i])
             )
    fig25.add_trace(go.Violin(x=df['day'][(df['sex'] == 'Female') &
                                        (df['day'] == pd.unique(df['day'])[i])],
                            y=df['total_bill'][(df['sex'] == 'Female')&
                                               (df['day'] == pd.unique(df['day'])[i])],
                            legendgroup='F', scalegroup='F', name='F',
                            side='positive',
                            pointpos=pointpos_female[i],
                            line_color='mediumpurple',
                            showlegend=show_legend[i])
             )

# update characteristics shared by all traces
fig25.update_traces(meanline_visible=True,
                  points='all', # show all points
                  jitter=0.05,  # add some jitter on points for better visibility
                  scalemode='count') #scale violin plot area with total count
fig25.update_layout(
    title_text="Total bill distribution<br><i>scaled by number of bills per gender",
    violingap=0, violingroupgap=0, violinmode='overlay')

st.subheader('Another violin plot')
st.plotly_chart(fig25)

# funnel plot
fig22 = go.Figure(go.Funnel(
    y = ["Website visit", "Downloads", "Potential customers", "Requested price", "invoice sent"],
    x = [39, 27.4, 20.6, 11, 2]))

st.subheader('funnel plot')
st.plotly_chart(fig22)

# histogram animation
import time
bins = [0, 1, 2, 3]
hist_values = [5, 8, 4]
max_height = max(hist_values)

# Streamlitのセットアップ
st.subheader("Falling Blocks Histogram")
start_button = st.button("Start Animation")

# 初期のプロットの設定
fig = go.Figure()
fig.update_xaxes(range=[0, 3], tickvals=[0.5, 1.5, 2.5], ticktext=["0-1", "1-2", "2-3"])
fig.update_yaxes(range=[0, max_height])

# 初期のブロックの表示
for i in range(len(bins) - 1):
    fig.add_trace(go.Scatter(
        x=[bins[i] + 0.5] * hist_values[i],
        y=[0] * hist_values[i],
        mode='markers',
        marker=dict(size=20, color='blue')
    ))

plot = st.plotly_chart(fig)

# ボタンが押されたか確認
if start_button:
    # ブロックを上から落とすアニメーション
    for step in range(max_height):
        new_fig = go.Figure()
        for i in range(len(bins) - 1):
            y_vals = [j for j in range(hist_values[i]) if j <= step]
            new_fig.add_trace(go.Scatter(
                x=[bins[i] + 0.5] * len(y_vals),
                y=y_vals,
                mode='markers',
                marker=dict(size=20, color='blue')
            ))
        new_fig.update_xaxes(range=[0, 3], tickvals=[0.5, 1.5, 2.5], ticktext=["0-1", "1-2", "2-3"])
        new_fig.update_yaxes(range=[0, max_height])
        plot.plotly_chart(new_fig)
        time.sleep(0.5)    
    st.write("Histogram completed!")


# histogram animation (from bottom)
data = np.random.normal(loc=0, scale=1, size=100)
num_bins = 10
bin_counts = np.zeros(num_bins)

# ヒストグラムの範囲を設定
bin_edges = np.linspace(-4, 4, num_bins + 1)
x = (bin_edges[:-1] + bin_edges[1:]) / 2

# 初期設定
frames = []
for i in range(len(data)):
    new_value = data[i]
    bin_index = np.digitize(new_value, bin_edges) - 1
    bin_counts[bin_index] += 1
    
    frame = go.Frame(
        data=[go.Bar(x=x, y=bin_counts, width=0.7, marker_color='blue')],
        name=str(i)
    )
    frames.append(frame)

# 初期フレーム
initial_frame = frames[0]

# プロットの設定
fig = go.Figure(
    data=initial_frame.data,
    layout=go.Layout(
        xaxis=dict(range=[-4, 4]),
        yaxis=dict(range=[0, max(bin_counts) + 1]),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[dict(label="Play",
                          method="animate",
                          args=[None, dict(frame=dict(duration=100, redraw=True), fromcurrent=True)])]
        )]
    ),
    frames=frames
)

st.subheader("テトリス風ヒストグラムアニメーション")
st.plotly_chart(fig)




# 2D Brownian motion
n_points = 3
n_steps = 100
delta_t = 0.1

np.random.seed(42)  # For reproducibility
x = np.zeros((n_points, n_steps))
y = np.zeros((n_points, n_steps))

for i in range(1, n_steps):
    x[:, i] = x[:, i-1] + np.sqrt(delta_t) * np.random.randn(n_points)
    y[:, i] = y[:, i-1] + np.sqrt(delta_t) * np.random.randn(n_points)

colors = [f'rgba({r}, {g}, {b}, 0.8)' for r, g, b in np.random.randint(0, 255, size=(n_points, 3))]

fig0 = go.Figure()
for i in range(n_points):
    fig0.add_trace(go.Scatter(
        x=[x[i, 0]],
        y=[y[i, 0]],
        mode='lines',
        line=dict(color=colors[i], width=1),
        showlegend=False
    ))

fig0.update_layout(
    xaxis=dict(range=[-10, 10], autorange=False),
    yaxis=dict(range=[-10, 10], autorange=False),
    title="2D Brownian Motion",
    updatemenus=[dict(
        type="buttons",
        buttons=[dict(label="Play",
                      method="animate",
                      args=[None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True, "mode": "immediate"}])]
    )]
)
fig0.frames = [go.Frame(data=[go.Scatter(x=x[i, :k+1], y=y[i, :k+1]) for i in range(n_points)]) for k in range(n_steps)]

fig00 = go.Figure()
for i in range(n_points):
    fig00.add_trace(go.Scatter(
        x=[x[i, 0]],
        y=[y[i, 0]],
        mode='markers',
        marker=dict(color=colors[i], size=5),
        showlegend=False
    ))

fig00.update_layout(
    xaxis=dict(range=[-10, 10], autorange=False),
    yaxis=dict(range=[-10, 10], autorange=False),
    title="2D Brownian Motion",
    updatemenus=[dict(
        type="buttons",
        buttons=[dict(label="Play",
                      method="animate",
                      args=[None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True, "mode": "immediate"}])]
    )]
)
fig00.frames = [go.Frame(data=[go.Scatter(x=[x[i, k]], y=[y[i, k]], mode='markers', marker=dict(color=colors[i], size=5)) for i in range(n_points)]) for k in range(n_steps)]

left_column3, right_column3 = st.columns(2)
left_column3.subheader('2D Brownian Motion Animation')
left_column3.plotly_chart(fig0)
right_column3.subheader('2D Brownian Motion Animation (w/o trace)')
right_column3.plotly_chart(fig00)


# data
df2 = pd.read_csv('data/koukouseiseki.csv')
df3 = pd.read_csv('data/nikkei225.csv')
vars2 = [var for var in df2.columns]
vars3 = [var for var in df3.columns]


# Layout (Sidebar)
st.sidebar.markdown("## サイドバーの使い方")
vars2_selected = st.sidebar.selectbox('散布図：高校科目', vars2)
vars2_multi_selected = st.sidebar.multiselect('相関行列：高校科目', vars2, default=vars2) # デフォルトは全部
vars3_selected = st.sidebar.selectbox('日経225の折れ線グラフ', vars3[1:])
vars3_multi_selected = st.sidebar.multiselect('日経225の折れ線グラフ（複数）', vars3, default=vars3[1:])


# map graph
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

import pandas as pd
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})
import plotly.express as px
fig11 = px.choropleth(df, geojson=counties, locations='fips', color='unemp',
                           color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           scope="usa",
                           labels={'unemp':'unemployment rate'}
                          )
fig11.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


# 
import plotly.graph_objects as go
df4 = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv')
fig12 = go.Figure(data=go.Choropleth(
    locations=df4['code'], # Spatial coordinates
    z = df4['total exports'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "Millions USD",))
fig12.update_layout(
    title_text = '2011 US Agriculture Exports by State',
    geo_scope='usa', # limite map scope to USA
)

#
import json
from io import StringIO
with open("data/N03-23_25_230101.geojson", encoding = 'utf-8') as f:
    geojson = json.load(f)
#geojson["features"][1]["properties"]

shiga_pop_text = """市区町村名,男,女,計,世帯数
大津市,160170,169871,330041,130143
彦根市,53908,55368,109276,41257
長浜市,39575,41263,80838,27937
近江八幡市,33530,34786,68316,25445
草津市,59131,58415,117546,46997
守山市,37379,38152,75531,26689
栗東市,31775,31670,63445,23091
甲賀市,45782,46877,92659,30640
野洲市,24889,24960,49849,17639
湖南市,27278,25621,52899,20037
高島市,26260,27599,53859,19205
東近江市,56384,57781,114165,38143
米原市,20140,20932,41072,13147
日野町,11158,11644,22802,7552
竜王町,7068,6256,13324,4412
愛荘町,9623,9833,19456,6256
豊郷町,3524,3681,7205,2574
甲良町,3792,4162,7954,2425
多賀町,3882,4251,8133,2640"""
shiga_pop = pd.read_csv(StringIO(shiga_pop_text))
shiga_pop.head()

fig13 = px.choropleth_mapbox(
    shiga_pop,
    geojson=geojson,
    locations="市区町村名",
    color="計",
    hover_name="市区町村名",
    hover_data=["男", "女", "世帯数"],
    featureidkey="properties.N03_004",
    mapbox_style="carto-positron",
    zoom=8,
    center={"lat": 35.09, "lon": 136.18},
    opacity=0.5,
    width=800,
    height=800,
)

# treemap
df5 = px.data.tips()
fig14 = px.treemap(df5, path=[px.Constant("all"), 'day', 'time', 'sex'], values='total_bill')
fig14.update_traces(root_color="lightgrey")
#fig14.update_layout(margin = dict(t=50, l=25, r=25, b=25))

# area map
df6 = px.data.iris()
fig15 = px.area(df6, x="sepal_width", y="sepal_length",
            color="species",
            hover_data=['petal_width'],)


# 散布図
#fig2 = px.scatter(x=df2['国語'],y=df2['数学'])
fig2 = px.scatter(x=df2['国語'],y=df2[vars2_selected])
fig2.update_layout(height=300,
                   width=500,
                   margin={'l': 20, 'r': 20, 't': 0, 'b': 0})


# contribution graph
df8 = pd.read_csv('data/kisho_data.csv')


#（単一）折れ線グラフ
#fig3 = px.line(x=df3['日付'], y=df3['終値'])
df3['日付'] = pd.to_datetime(df3['日付'], format='%Y年%m月%d日')
fig3 = px.line(x=df3['日付'], y=df3[vars3_selected])
fig3.update_layout(height=300,
                   width=500,
                   margin={'l': 20, 'r': 20, 't': 0, 'b': 0})

#fig4 = px.line(df3[vars3_multi_selected])
#fig4.update_layout(height=300,
#                   width=1000,
#                   margin={'l': 20, 'r': 20, 't': 0, 'b': 0})

#（複数）折れ線グラフ
df3['日付'] = pd.to_datetime(df3['日付'], format='%Y年%m月%d日')
fig5 = px.line(df3, x='日付', y=vars3_multi_selected, 
              labels={'value': '株価（円）', 'variable': '株価の種類'},
              #title="日経225株価の推移"
              )
fig5.update_layout(height=300,
                   width=1000,
                   margin={'l': 20, 'r': 20, 't': 0, 'b': 0})

# 折れ線
df = px.data.stocks()
fig31 = px.line(df, x='date', y="GOOG")
st.subheader('折れ線')
st.plotly_chart(fig31)
st.write(df.head())

df = px.data.gapminder().query("continent=='Oceania'")
fig32 = px.line(df, x="year", y="lifeExp", color='country')
st.plotly_chart(fig32)
st.write(df.head())

#ウォーターフォール図
df3['終値'] = pd.to_numeric(df3['終値'].str.replace(',', ''))
df3['変化'] = df3['終値'].diff()
df3.at[0, '変化'] = df3.at[0, '終値']
fig6 = go.Figure(go.Waterfall(
    name="株価の変化",
    orientation="v",
    x=df3['日付'],
    y=df3['変化'],
    connector={"line":{"color":"rgb(63, 63, 63)"}},
    decreasing={"marker":{"color":"red"}},
    increasing={"marker":{"color":"green"}},
    totals={"marker":{"color":"blue"}},))
fig6.update_layout(
    title="日経225株価のウォーターフォール図",
    xaxis_title="日付",
    yaxis_title="株価の変化（円）",
    showlegend=True)


# Correlation Matrix of kamoku in Content
df2_corr = df2[vars2_multi_selected].corr()
fig_corr2 = go.Figure([go.Heatmap(z=df2_corr.values,
                                  x=df2_corr.index.values,
                                  y=df2_corr.columns.values)])
fig_corr2.update_layout(height=300,
                        width=1000,
                        margin={'l': 20, 'r': 20, 't': 0, 'b': 0})

# 箱ひげ図
df2_ = df2[vars2_multi_selected]
df2_melted = df2_.melt(var_name='科目', value_name='得点')
fig7 = px.box(df2_melted, x='科目', y='得点', color='科目', title='各科目の得点分布')
#fig7 = px.box(df2_melted, x=vars2_multi_selected, y='得点', color='科目', title='各科目の得点分布')
fig7.update_layout(
    xaxis_title='科目',
    yaxis_title='得点',
    showlegend=False)

# ヒストグラム
fig8 = px.histogram(df2, x='国語', nbins=10, title='国語の得点分布')
fig8 = px.histogram(df2, x=vars2_selected, nbins=10)
fig8.update_layout(
    xaxis_title='得点',
    yaxis_title='頻度')


# 円グラフを作成
data = pd.read_csv('data/nikkei225.csv')
#final_values = df3[vars3[1:]][:1]
#final_values = df3.iloc[-1][['始値', '高値', '安値', '終値']].values
final_values = [33193.05, 33299.39, 32693.18, 33288.29]
fig9 = px.pie(values=final_values, names=['始値', '高値', '安値', '終値'], title='最終時点の株価')

# 棒グラフで作成
data['始値'] = pd.to_numeric(data['始値'].str.replace(',', ''))
data['高値'] = pd.to_numeric(data['高値'].str.replace(',', ''))
data['安値'] = pd.to_numeric(data['安値'].str.replace(',', ''))
data['終値'] = pd.to_numeric(data['終値'].str.replace(',', ''))
final_row = data.iloc[-1]
final_values = [final_row['始値'], final_row['高値'], final_row['安値'], final_row['終値']]
fig10 = go.Figure(data=[
    go.Bar(name='始値', x=['始値'], y=[final_values[0]]),
    go.Bar(name='高値', x=['高値'], y=[final_values[1]]),
    go.Bar(name='安値', x=['安値'], y=[final_values[2]]),
    go.Bar(name='終値', x=['終値'], y=[final_values[3]])])
fig10.update_layout(
    title='最終時点の株価',
    xaxis_title='種類',
    yaxis_title='株価（円）',
    barmode='group')

# bar chart
import numpy as np
np.random.seed(42) 
random_x= np.random.randint(1,101,100) 
random_y= np.random.randint(1,101,100) 
fig16 = px.bar(random_x, random_y)

df7 = px.data.iris()
fig17 = px.bar(df7, x="sepal_width", y="sepal_length")
fig18 = px.bar(df7, x="sepal_width", y="sepal_length", color="species",
            hover_data=['petal_width'], barmode = 'stack')


# (green) contribution graph
# 日付を基に週番号と曜日を計算
data3 = pd.read_csv('data/kisho_data.csv')
vars3_2 = [var for var in data3.columns]
vars3_2_selected = st.sidebar.selectbox('気象データの貢献グラフ', vars3_2[2:])

data3['年月日'] = pd.to_datetime(data3['年月日'])
data3['week'] = data3['年月日'].apply(lambda x: x.isocalendar()[1])
data3['day_of_week'] = data3['年月日'].dt.dayofweek

# ピボットテーブルを作成して行列を転置
temperature_matrix = data3.pivot_table(values=vars3_2_selected, index='week', columns='day_of_week', aggfunc='mean').fillna(0)
temperature_matrix = temperature_matrix.T
custom_colorscale = [[0, 'black'],[1, 'green']]

# Plotlyでヒートマップを作成（色を反転）
fig19 = go.Figure(data=go.Heatmap(
    z=temperature_matrix.values,
    x=temperature_matrix.columns,
    #y=['Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon', 'Sun'],
    #y=list(range(7)),
    y=list(range(6,-1,-1)),
    colorscale=custom_colorscale,
    #colorscale='Greens_r'
    showscale=True
))

# グラフのレイアウトを設定して、セルを正方形にする
fig19.update_layout(
    title='Weekly Temperature Heatmap',
    xaxis_nticks=52,
    yaxis_nticks=7,
    yaxis_title='Day of the Week',
    xaxis_title='Week',
    xaxis=dict(
        tickmode='array',
        tickvals=list(range(1, 53)),
        ticktext=[str(i) for i in range(1, 53)]
    ),
    yaxis=dict(
        tickmode='array',
        #tickvals=list(range(7)),
        tickvals=list(range(6,-1,-1)),
        #ticktext=['Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon', 'Sun'],
        #ticktext=['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        scaleanchor='x',  # Make y-axis scale anchor to x-axis to make cells square
        scaleratio=1     # Ensure the ratio is 1 to make cells square
    ),
    autosize=False,
    width=1400,
    height=300
)


# contribution graph (with gap)
# ピボットテーブルを作成して行列を転置
rainfall_matrix = data3.pivot_table(values=vars3_2_selected, index='week', columns='day_of_week', aggfunc='mean').fillna(0)
rainfall_matrix_transposed = rainfall_matrix.T

# 元の行列を拡張し、値が入る場所に元のデータを配置し、それ以外の場所はNaNで埋める
expanded_matrix = np.full((rainfall_matrix_transposed.shape[0] * 2, rainfall_matrix_transposed.shape[1] * 2), np.nan)
expanded_matrix[::2, ::2] = rainfall_matrix_transposed.values

# Plotlyでヒートマップを作成（カスタムカラースケール）
fig20 = go.Figure(data=go.Heatmap(
    z=expanded_matrix,
    x=np.arange(0.5, len(rainfall_matrix.columns) + 0.5, 1),
    #y=np.arange(0.5, 7 + 0.5, 0.5),
    #y=np.arange(7, 0, -0.5),
    y=np.arange(6.5, 0, -1),
    colorscale=custom_colorscale,
    zmin=rainfall_matrix_transposed.values.min(),
    zmax=rainfall_matrix_transposed.values.max(),
    showscale=True
))

fig20.update_layout(
    title='Weekly Rainfall Heatmap',
    xaxis_nticks=52,
    yaxis_nticks=7,
    yaxis_title='Day of the Week',
    xaxis_title='Week',
    xaxis=dict(
        tickmode='array',
        tickvals=np.arange(0.5, len(rainfall_matrix.columns) + 0.5, 1),
        ticktext=[str(i) for i in range(1, 53)]
    ),
    yaxis=dict(
        tickmode='array',
        #tickvals=np.arange(0.5, 7 + 0.5, 1),
        #ticktext=['Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon', 'Sun'],
        #tickvals=np.arange(7.5, 0.5, -1),
        tickvals=np.arange(6.5, 0, -1),
        ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        scaleanchor='x',  # Make y-axis scale anchor to x-axis to make cells square
        scaleratio=1     # Ensure the ratio is 1 to make cells square
    ),
    autosize=False,
    width=1400,
    height=400
)


# another contribution graph
# 元の行列を拡張し、値が入る場所に元のデータを配置し、それ以外の場所はNaNで埋める
gap = 0.05  # 隙間のサイズを調整
expanded_matrix = np.full((rainfall_matrix_transposed.shape[0] * 2 - 1, rainfall_matrix_transposed.shape[1] * 2 - 1), np.nan)
expanded_matrix[::2, ::2] = rainfall_matrix_transposed.values

# Plotlyでヒートマップを作成（カスタムカラースケール）
fig21 = go.Figure(data=go.Heatmap(
    z=expanded_matrix,
    x=np.arange(0.5, len(rainfall_matrix.columns), 0.5) * (1 + gap),
    y=np.arange(0.5, 7, 0.5) * (1 + gap),
    colorscale=custom_colorscale,
    zmin=rainfall_matrix_transposed.values.min(),
    zmax=rainfall_matrix_transposed.values.max(),
    showscale=True
))

fig21.update_layout(
    title='Weekly Rainfall Heatmap (Transposed and Color Reversed)',
    xaxis_nticks=52,
    yaxis_nticks=7,
    yaxis_title='Day of the Week',
    xaxis_title='Week',
    xaxis=dict(
        tickmode='array',
        tickvals=np.arange(0.5, len(rainfall_matrix.columns) * (1 + gap), 1 + gap),
        ticktext=[str(i) for i in range(1, 53)]
    ),
    yaxis=dict(
        tickmode='array',
        tickvals=np.arange(0.5, 7 * (1 + gap), 1 + gap),
        ticktext=['Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon', 'Sun'],
        scaleanchor='x',  # Make y-axis scale anchor to x-axis to make cells square
        scaleratio=1     # Ensure the ratio is 1 to make cells square
    ),
    autosize=False,
    width=1400,
    height=400
)


# Layout (Content)
left_column, right_column = st.columns(2)
left_column.subheader('日経225: ' + vars3_selected)
left_column.plotly_chart(fig3)
right_column.subheader('散布図：国語と' + vars2_selected)
right_column.plotly_chart(fig2)

left, center, right = st.columns(3)
left.subheader('ウォーターフォール')
left.plotly_chart(fig6)
center.subheader('箱ひげ図')
center.plotly_chart(fig7)
right.subheader('ヒストグラム' + vars2_selected)
right.plotly_chart(fig8)

st.subheader('日経225すべて')
st.plotly_chart(fig5)
st.subheader('高校科目の相関行列')
st.plotly_chart(fig_corr2)

left_column2, right_column2 = st.columns(2)
left_column2.subheader('円グラフ')
left_column2.plotly_chart(fig9)
right_column2.subheader('棒グラフ')
right_column2.plotly_chart(fig10)


st.subheader('Choropleth map using GeoJSON')
st.plotly_chart(fig11)
st.subheader('Choropleth Maps with goChoropleth')
st.plotly_chart(fig12)
st.subheader('Choropleth Maps with goChoropleth')
st.plotly_chart(fig13)

st.subheader('treemap')
st.plotly_chart(fig14)
st.subheader('filled area chart')
st.plotly_chart(fig15)
st.subheader('bar chart')
st.plotly_chart(fig16)
st.subheader('bar chart with dataframe')
st.plotly_chart(fig17)
st.subheader('stack bar chart with dataframe')
st.plotly_chart(fig18)

st.subheader('Weekly Temperature Heatmap: ' + vars3_2_selected)
st.plotly_chart(fig19)
st.subheader('Weekly Temperature Heatmap')
st.plotly_chart(fig20)



#### google trend visualization

#from datetime import datetime
#now = datetime.now()
#date_str = now.strftime('%Y-%m-%d')

from datetime import datetime, timedelta
now = datetime.now()
yesterday = now - timedelta(days=1)
date_str = yesterday.strftime('%Y-%m-%d')

pytrends = TrendReq(hl='ja-JP', tz=360)
kw_list = ["AI","ChatGPT"]
#kw_list = ["データサイエンス"]
pytrends.build_payload(kw_list, timeframe='2020-01-01 2024-08-05', geo='JP')
df = pytrends.interest_over_time().drop(columns=['isPartial'])
df.reset_index(inplace=True)
st.dataframe(df)

fig33 = px.line(df, x='date', y=kw_list)
st.subheader('google trend')
st.plotly_chart(fig33)

pytrends = TrendReq(hl='ja-JP', tz=360)
kw_list = ["コロナ"]
start_date = '2024-06-01'
date_range = f'{start_date} {date_str}'
#pytrends.build_payload(kw_list, timeframe=date_range, geo='JP')
pytrends.build_payload(kw_list, timeframe='2024-06-01 2024-08-05', geo='JP')

df = pytrends.interest_over_time()
df.drop(columns=['isPartial'], inplace=True)
df.reset_index(inplace=True)
#st.dataframe(df)

fig34 = px.line(df, x='date', y=kw_list)
st.subheader('google trend')
st.plotly_chart(fig34)

