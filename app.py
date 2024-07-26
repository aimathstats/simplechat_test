import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(layout="wide")

# additional codes
df2 = pd.read_csv('data/koukouseiseki.csv')
df3 = pd.read_csv('data/nikkei225.csv')
vars2 = [var for var in df2.columns]
vars3 = [var for var in df3.columns]

# Data
df = pd.read_csv('data/data_sample.csv')
vars_cat = [var for var in df.columns if var.startswith('cat')]
vars_cont = [var for var in df.columns if var.startswith('cont')]

'''
# Graph (Pie Chart in Sidebar)
df_target = df[['id', 'target']].groupby('target').count() / len(df)
fig_target = go.Figure(data=[go.Pie(labels=df_target.index,
                                    values=df_target['id'],
                                    hole=.3)])
fig_target.update_layout(showlegend=False,
                         height=200,
                         margin={'l': 20, 'r': 60, 't': 0, 'b': 0})
fig_target.update_traces(textposition='inside', textinfo='label+percent')
'''


# Layout (Sidebar)
st.sidebar.markdown("## Selection in Sidebar")
vars2_selected = st.sidebar.selectbox('高校科目', vars2)
vars2_multi_selected = st.sidebar.multiselect('高校科目', vars2, default=vars2) # デフォルトは全部
vars3_selected = st.sidebar.selectbox('日経225系列', vars3)

cat_selected = st.sidebar.selectbox('Categorical Variables', vars_cat)
cont_selected = st.sidebar.selectbox('Continuous Variables', vars_cont)
cont_multi_selected = st.sidebar.multiselect('Correlation Matrix', vars_cont, default=vars_cont)

st.sidebar.markdown("## Target Variables")
st.sidebar.plotly_chart(fig_target, use_container_width=True)


# Categorical Variable Bar Chart in Content
df_cat = df.groupby([cat_selected, 'target']).count()[['id']].reset_index()

cat0 = df_cat[df_cat['target'] == 0]
cat1 = df_cat[df_cat['target'] == 1]

fig_cat = go.Figure(data=[
    go.Bar(name='target=0', x=cat0[cat_selected], y=cat0['id']),
    go.Bar(name='target=1', x=cat1[cat_selected], y=cat1['id'])
])
fig_cat.update_layout(height=300,
                      width=500,
                      margin={'l': 20, 'r': 20, 't': 0, 'b': 0},
                      legend=dict(
                          yanchor="top",
                          y=0.99,
                          xanchor="right",
                          x=0.99),
                      barmode='stack')
fig_cat.update_xaxes(title_text=None)
fig_cat.update_yaxes(title_text='# of samples')


# Continuous Variable Distribution in Content
li_cont0 = df[df['target'] == 0][cont_selected].values.tolist()
li_cont1 = df[df['target'] == 1][cont_selected].values.tolist()

cont_data = [li_cont0, li_cont1]
group_labels = ['target=0', 'target=1']

fig_cont = ff.create_distplot(cont_data, group_labels,
                              show_hist=False,
                              show_rug=False)
fig_cont.update_layout(height=300,
                       width=500,
                       margin={'l': 20, 'r': 20, 't': 0, 'b': 0},
                       legend=dict(
                           yanchor="top",
                           y=0.99,
                           xanchor="right",
                           x=0.99)
                       )

import plotly.express as px
fig2 = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
fig2.update_layout(height=300,
                   width=500,
                   margin={'l': 20, 'r': 20, 't': 0, 'b': 0})

# Correlation Matrix of kamoku in Content
df2_corr = df2[vars2_multi_selected].corr()
fig_corr2 = go.Figure([go.Heatmap(z=df2_corr.values,
                                  x=df2_corr.index.values,
                                  y=df2_corr.columns.values)])
fig_corr2.update_layout(height=300,
                        width=1000,
                        margin={'l': 20, 'r': 20, 't': 0, 'b': 0})
'''
# Correlation Matrix in Content
df_corr = df[cont_multi_selected].corr()
fig_corr = go.Figure([go.Heatmap(z=df_corr.values,
                                 x=df_corr.index.values,
                                 y=df_corr.columns.values)])
fig_corr.update_layout(height=300,
                       width=1000,
                       margin={'l': 20, 'r': 20, 't': 0, 'b': 0})
'''

# Layout (Content)
left_column, right_column = st.columns(2)

left_column.subheader('Categorical Variable Distribution: ' + cat_selected)
left_column.plotly_chart(fig_cat)

right_column.subheader('Continuous Variable Distribution: ' + cont_selected)
#right_column.plotly_chart(fig_cont)
right_column.plotly_chart(fig2)

st.subheader('高校科目の相関行列')
st.plotly_chart(fig_corr2)

#st.subheader('Correlation Matrix')
#st.plotly_chart(fig_corr)