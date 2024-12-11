import base64
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import statsmodels.api as sm
import numpy as np
st.set_page_config(page_title="Olympic Medal Analysis", page_icon="🏅", layout="wide")

def main_bg(main_bg):
    main_bg_ext = "gif" 
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
            background-size: cover;
            background-attachment: fixed;
            height: 100vh;  /* Full height of the screen */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def sidebar_bg():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] > div:first-child {
            background-color: rgba(190,44,37, 0.8);  /* 设置左侧侧边栏背景色为半透明的暗红色 */
            color: white;  /* 确保文字为白色，以便清晰可见 */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

main_bg('./static/bac.gif') 
sidebar_bg()
st.markdown("""
    <style>
    /* 引入黑体字体 */
    @import url('https://fonts.googleapis.com/css2?family=SimHei&display=swap');

    /* 设置左侧侧边栏字体为黑体、白色 */
    .css-1v3fvcr, .css-1c0zwtb, .css-1k5m0a1 {
        font-family: 'SimHei', sans-serif;
        color: white;
    }

    /* 侧边栏背景和按钮的样式 */
    .stButton > button {
        background-color: #008CBA;
        color: white;
        border-radius: 8px;
        font-size: 14px;
    }
            
    .dataframe-container {
        width: 95%;
        max-height: 550px;  /* 设置表格最大高度 */
        overflow-y: scroll;  /* 竖向滚动条 */
        border: 1px solid #ccc;  /* 表格外边框 */
    }
    </style>
""", unsafe_allow_html=True)

hosts_df = pd.read_csv('input/olympic_hosts.csv')  
medals_df = pd.read_csv('input/Country_Medals.csv', delimiter=';')  
gdp_data = pd.read_csv('input/China_GDP.csv') 

# 筛选夏季奥运会
hosts_df = hosts_df[hosts_df['game_season'] == 'Summer']

medals_df['Year'] = medals_df['Year'].astype(int)

# 计算总奖牌数
medals_df['Total'] = medals_df['Gold'] + medals_df['Silver'] + medals_df['Bronze']

# 计算奖牌的平均值
average_medals_df = medals_df.groupby('Country_Name')[['Gold', 'Silver', 'Bronze', 'Total']].mean()

st.markdown("# The Olympic Games")
# 左侧选择框
with st.sidebar:
    st.header("Analysis of Olympic Games Over the Years")
    analysis_type = st.radio("Choose the Type of Analysis", ['Overall Overview', 'Host Advantage', 'Impact on Economic Strength','Bonus for Strong Events'])

    if analysis_type == 'Overall Overview':
        analysis_subtype = st.radio("Choose Display Content", ['Data', 'Map'])
    elif analysis_type == 'Host Advantage':
        selected_country = st.selectbox('Choose a Country', medals_df['Country_Name'].unique())
        medal_type = st.selectbox('Choose a Medal Type', ['Gold', 'Silver', 'Bronze', 'Total'])
        chart_type = st.selectbox('Choose a Chart Type', ['Line Chart', 'Box Plot', 'Regression Analysis'])
    elif analysis_type == 'Impact on Economic Strength':
        chart_type = st.selectbox('Choose a Chart Type', ['Line Chart', 'Heatmap'])
    elif analysis_type == 'Bonus for Strong Events':
        chart_type = st.selectbox('Choose a Chart Type',['Bar Chart','Sankey Diagram'])

if analysis_type == 'Overall Overview':
    st.markdown("## Overall Overview")
    if analysis_subtype == 'Data':
        st.markdown("## Medal Statistics")

        years = medals_df['Year'].unique()
        years = sorted(years)  
        selected_year = st.selectbox('Choose a year', years)

        df_year = medals_df[medals_df['Year'] == selected_year]

        # 汇总每个国家的金、银、铜奖牌数量，并计算总数
        medal_counts = df_year.groupby('Country_Name')[['Country_Name', 'Gold', 'Silver', 'Bronze']].sum()
        medal_counts['Total'] = medal_counts['Gold'] + medal_counts['Silver'] + medal_counts['Bronze']

        sort_by = st.selectbox('Choose the sorting criterion', ['Gold', 'Silver', 'Bronze', 'Total'])

        medal_counts = medal_counts.sort_values(by=sort_by, ascending=False)

        styled_df = medal_counts[['Country_Name', 'Gold', 'Silver', 'Bronze', 'Total']].style.set_caption(f'Medals by Country: Summer Olympic Games {selected_year}')\
            .bar(subset=['Gold'], color='#f0c05a', width=100)\
            .bar(subset=['Silver'], color='#c0c0c0', width=100)\
            .bar(subset=['Bronze'], color='#a97142', width=100)\
            .set_table_styles([
                {'selector': 'thead th', 'props': [('background-color', '#f1f1f1'), ('color', '#000')]},  # 头部背景
                {'selector': 'tbody td', 'props': [('background-color', 'white'), ('color', '#000')]},  # 数据背景
                {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]},  # 隔行背景
            ])\
            .hide(axis='index')  

        html_table = styled_df.to_html()

        col1, col2 = st.columns([2, 1.15]) 

        with col1:
            st.markdown(f'<div class="dataframe-container">{html_table}</div>', unsafe_allow_html=True)

        with col2:
            selected_country = st.selectbox('Choose to view the gold, silver, and copper ratio of this country', medal_counts.index)

            country_medals = medal_counts.loc[selected_country][['Gold', 'Silver', 'Bronze']]

            # 计算奖牌比例
            total_medals = country_medals.sum()
            medal_ratios = country_medals / total_medals

            fig = px.pie(
                values=medal_ratios,
                names=['Gold', 'Silver', 'Bronze'],
                title=f"{selected_country} Medal Proportions",
                hole=0.4,  
                color=['Gold', 'Silver', 'Bronze'],
                color_discrete_map={'Gold': '#f0c05a', 'Silver': '#c0c0c0', 'Bronze': '#a97142'},
                labels={'Gold': 'Gold', 'Silver': 'Silver', 'Bronze': 'Bronze'}
            )

            fig.update_layout(
                template="plotly_dark",
                showlegend=True,
                title_x=0.28, 
            )

            fig.update_traces(
                hovertemplate="Medal = %{label} <br> Proportion = %{percent:.2f}<extra></extra>",
                hoverlabel=dict(
                    font=dict(
                        family="Arial Black", 
                        size=16, 
                        color="black"  
                    )
                )
            )

            st.plotly_chart(fig)

    elif analysis_subtype == 'Map':
        st.markdown("## Medal Distribution Map")

        # 用户选择年份和奖牌类型
        years = sorted(medals_df['Year'].unique())
        selected_year = st.selectbox('Choose a year', years, index=len(years)-1)  # 默认选最后一年
        medal_type = st.selectbox('Choose a Medal Type', ['Gold', 'Silver', 'Bronze', 'Total'])
        df_year = medals_df[medals_df['Year'] == selected_year]

        # 汇总每个国家的奖牌数
        medal_counts_map = df_year.groupby('Country_Name')[['Gold', 'Silver', 'Bronze', 'Total']].sum().reset_index()

        color_column = medal_type  

        fig_map = px.choropleth(
            medal_counts_map,
            locations='Country_Name',
            locationmode='country names',
            color=color_column,
            hover_data={medal_type: True},
            color_continuous_scale='Blues', 
            title=f'{medal_type} Medals by Country in {selected_year}',
            labels={color_column: f'{medal_type} Medals'}
        )

        fig_map.update_geos(
            visible=True,
            showcoastlines=True,
            coastlinecolor="Black",
            projection_type="mercator",  
            showland=True,
            landcolor="rgb(255, 255, 255)",
            showlakes=True,
            lakecolor="rgb(255, 255, 255)"
        )

        fig_map.update_layout(
            geo=dict(
                visible=True,
                projection_type="natural earth",
                scope="world",  
                center={"lat": 0, "lon": 0},
                showframe=False,
                showcoastlines=True
            ),
            autosize=True,  
            width=1200,  
            height=800,  
            hoverlabel=dict(
                font=dict(
                    family="Arial Black",  
                    size=16,  
                    color="black" 
                )
            )
        )

        st.plotly_chart(fig_map)

elif analysis_type == 'Host Advantage':
    st.markdown("## Analysis of Host Advantage")
    host_data = hosts_df[hosts_df['game_location'] == selected_country]
    country_medals = medals_df[medals_df['Country_Name'] == selected_country]
    country_medals = country_medals.groupby('Year')[['Gold', 'Silver', 'Bronze', 'Total']].sum().reset_index()

    # 计算东道主年份
    host_years = host_data['game_year'].unique()
    valid_host_years = [year for year in host_years if year in country_medals['Year'].values]

    if chart_type == 'Line Chart':
        st.markdown("### Line Chart")
        fig = go.Figure()

        # 奖牌类型的折线
        fig.add_trace(go.Scatter(x=country_medals['Year'], y=country_medals[medal_type], mode='lines+markers',
                                name=medal_type, line=dict(width=2, color='blue'), marker=dict(size=8, color='blue')))

        # 高亮显示东道主年份
        highlight_marker_color = 'rgba(255, 99, 71, 0.6)'  
        for year in valid_host_years:
            fig.add_trace(go.Scatter(
                x=[year],
                y=[country_medals[country_medals['Year'] == year][medal_type].values[0]],
                mode='markers',
                marker=dict(size=12, color=highlight_marker_color, symbol='circle'),
                name=f"Host Year: {year}", 
                hoverinfo='text',  
                hovertext=f"Host Year: {year}"  
            ))

        # 计算该国家奖牌的平均值
        average_medal_value = country_medals[medal_type].mean()

        # 平均值的虚线
        fig.add_shape(
            type="line",
            x0=country_medals['Year'].min(), x1=country_medals['Year'].max(), 
            y0=average_medal_value, y1=average_medal_value,  
            line=dict(
                color="red", 
                width=2,  
                dash="dash"  
            ),
            name="Average",  
            legendgroup="average",  
            showlegend=True  
        )

        fig.update_layout(
            title=f"{selected_country} {medal_type} Medal History",
            xaxis_title="Year",
            yaxis_title="Medals Count",
            hovermode="x unified",  
            template="plotly_dark",  
            hoverlabel=dict(
                font=dict(
                    family="Arial Black",  
                    size=16,  
                    color="black"  
                ),
                bgcolor="rgba(255, 255, 255, 0.8)",  
                bordercolor="gray"  
            )
        )

        st.plotly_chart(fig)

    elif chart_type == 'Box Plot':
        st.markdown("### Box Plot")
        fig2 = px.box(country_medals,
                    y=['Gold', 'Silver', 'Bronze', 'Total'],
                    title=f"{selected_country} Medal Distribution Boxplot",
                    color='variable',
                    color_discrete_map={
                        'Gold': '#1f77b4',
                        'Silver': '#4682b4',
                        'Bronze': '#5f9ea0',
                        'Total': '#87cefa'
                    })
        
        fig2.update_traces(marker=dict(color='black', size=6),
                        line=dict(width=3, color='darkblue'),
                        boxmean='sd',
                        boxpoints=False,
                        jitter=0)
        
        fig2.update_layout(
            yaxis_title='Medals Count',
            showlegend=False,
            template="plotly_dark",
            plot_bgcolor='rgba(0, 0, 0, 0)',  
            hoverlabel=dict(
                font=dict(
                    family="Arial Black",  
                    size=16, 
                    color="black"  
                ),
                bgcolor="rgba(255, 255, 255, 0.8)",  
                bordercolor="gray"  
            )
        )

        st.plotly_chart(fig2)

    elif chart_type == 'Regression Analysis':
        st.markdown("### Regression Analysis")
        country_medals['Is_Host'] = country_medals['Year'].apply(lambda x: 1 if x in valid_host_years else 0)

        # OLS 回归分析
        X = country_medals[['Is_Host']]  
        Y = country_medals[medal_type]  

        X = sm.add_constant(X)

        # OLS 回归分析
        model = sm.OLS(Y, X).fit()

        intercept = model.params['const']
        slope = model.params['Is_Host']
        r_value = model.rsquared

        fig3 = go.Figure()

        fig3.add_trace(go.Scatter(
            x=country_medals['Is_Host'],
            y=country_medals[medal_type],
            mode='markers',
            name=f'{medal_type} Medals',
            marker=dict(color='blue', size=10, opacity=0.7)
        ))

        x_vals = np.array([0, 1])  
        y_vals = intercept + slope * x_vals  

        fig3.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='lines',
            name=f'Regression Line',
            line=dict(color='red', width=2)
        ))

        fig3.update_layout(
            title=f"Regression Analysis: {medal_type} Medals vs Host Year",
            xaxis_title="Host Year (0=Non-Host, 1=Host)",
            yaxis_title=f'{medal_type} Medals',
            hovermode="closest",  
            template="plotly_dark",  
            hoverlabel=dict(
                font=dict(
                    family="Arial Black",  
                    size=16,  
                    color="black"  
                ),
                bgcolor="rgba(255, 255, 255, 0.8)",  
                bordercolor="gray" 
            )
        )

        fig3.add_annotation(
            x=0.5,
            y=0.95,
            text=f"R-squared: {r_value:.2f}",
            showarrow=False,
            font=dict(size=14, color='white'),
            align="center",
            bgcolor="rgba(0, 0, 0, 0.7)",
            borderpad=4,
        )

        st.plotly_chart(fig3)

elif analysis_type == 'Impact on Economic Strength':
    st.markdown("## Impact on Economic Strength")
    # 选中国的奖牌数据
    china_medals = medals_df[medals_df['Country_Name'] == 'China']
    china_medals_yearly = china_medals.groupby('Year')[['Gold', 'Silver', 'Bronze']].sum().reset_index()
    china_medals_yearly['Total_Medals'] = china_medals_yearly['Gold'] + china_medals_yearly['Silver'] + china_medals_yearly['Bronze']

    merged_data = pd.merge(gdp_data, china_medals_yearly[['Year', 'Gold', 'Total_Medals']], on='Year', how='left')
    
    if chart_type == 'Heatmap':
        st.markdown("### Heatmap")
        heatmap_data = merged_data[['GDP', 'GDP_WorldPercent', 'Gold', 'Total_Medals']].corr()  

        col1, col2 = st.columns([3, 2])  #
        
        with col2:
            start_year = st.selectbox("Choose the Starting Year", options=range(int(gdp_data['Year'].min()), int(gdp_data['Year'].max()) + 1), index=0)
            end_year = st.selectbox("Choose the Ending Year", options=range(int(gdp_data['Year'].min()), int(gdp_data['Year'].max()) + 1), index=int(gdp_data['Year'].max()) - int(gdp_data['Year'].min()))
        
        if start_year > end_year:
            st.warning("The starting year must be earlier than the ending year. Please choose again")

        with col2:
            st.subheader("Choose the indicators you want to view")
            metrics = []
            if st.checkbox("GDP"):
                metrics.append("GDP")
            if st.checkbox("GDP_WorldPercent"):
                metrics.append("GDP_WorldPercent")
            if st.checkbox("Gold"):
                metrics.append("Gold")
            if st.checkbox("Total_Medals"):
                metrics.append("Total_Medals")
            if not metrics:
                metrics = ["GDP", "GDP_WorldPercent", "Gold", "Total_Medals"]

        filtered_data = merged_data[(merged_data['Year'] >= start_year) & (merged_data['Year'] <= end_year)]
        
        if len(metrics) > 1:  
            # 计算相关性矩阵
            heatmap_data_filtered = filtered_data[metrics].corr()

            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data_filtered.values, 
                x=heatmap_data_filtered.columns, 
                y=heatmap_data_filtered.index,    
                colorscale='Blues',  
                colorbar=dict(title='Correlation'),  
                zmin=-1, zmax=1, 
                text=heatmap_data_filtered.round(2).values,  
                hoverinfo='text',  
                showscale=True,  
            ))

            fig.update_layout(
                title=f'Correlation between selected metrics from {start_year} to {end_year}',
                xaxis_title='Metrics',
                yaxis_title='Metrics',
                template='plotly',  
                hoverlabel=dict(
                    font=dict(
                        family="Arial Black",  
                        size=18,  
                        color="black"  
                    )
                )
            )

            with col1:
                st.plotly_chart(fig)
        else:
            st.warning("Please select at least two indicators to calculate the correlation")


    elif chart_type == 'Line Chart':
        st.markdown("### Line Chart")
        gdp_data = pd.read_csv('input/China_GDP.csv')  
        medals_data = pd.read_csv('input/Country_Medals.csv', delimiter=';')  
        # 选出中国的数据
        china_medals = medals_data[medals_data['Country_Name'] == 'China']

        # 计算中国每年的奖牌总数（包括金牌、银牌和铜牌的数量之和）和金牌数量
        china_medals_yearly = china_medals.groupby('Year').agg(
            Gold_Medals=('Gold', 'sum'),  
            Silver_Medals=('Silver', 'sum'),  
            Bronze_Medals=('Bronze', 'sum')  
        ).reset_index()

        # 计算奖牌总数
        china_medals_yearly['Total_Medals'] = china_medals_yearly['Gold_Medals'] + china_medals_yearly['Silver_Medals'] + china_medals_yearly['Bronze_Medals']
        data = pd.merge(gdp_data, china_medals_yearly, on='Year', how='inner')
        data = data[data['Year'] >= 1984]
        fig = go.Figure()

        # 中国GDP的折线图（左轴）
        fig.add_trace(go.Scatter(
            x=data['Year'], 
            y=data['GDP'], 
            mode='lines+markers',
            name='China GDP',
            line=dict(color='#1f77b4'),  
            yaxis='y1'
        ))

        # 中国奖牌总数的折线图（右轴）
        fig.add_trace(go.Scatter(
            x=data['Year'], 
            y=data['Total_Medals'], 
            mode='lines+markers',
            name='Total Medals',
            line=dict(color='#9b59b6'),  
            yaxis='y2'
        ))

        # 中国金牌数量的折线图（右轴）
        fig.add_trace(go.Scatter(
            x=data['Year'], 
            y=data['Gold_Medals'], 
            mode='lines+markers',
            name='Gold Medals',
            line=dict(color='#f39c12'),  
            yaxis='y2'
        ))

        # 高亮2008年的奖牌总数和金牌总数
        highlight_2008 = data[data['Year'] == 2008]

        # 高亮2008年奖牌总数的标记
        fig.add_trace(go.Scatter(
            x=highlight_2008['Year'], 
            y=highlight_2008['Total_Medals'], 
            mode='markers',
            name='2008 Total Medals (Highlight)',
            marker=dict(color='#9b59b6', size=10, symbol='circle'),
            showlegend=False,  
            yaxis='y2'
        ))

        # 高亮2008年金牌数量的标记
        fig.add_trace(go.Scatter(
            x=highlight_2008['Year'], 
            y=highlight_2008['Gold_Medals'], 
            mode='markers',
            name='2008 Gold Medals (Highlight)',
            marker=dict(color='#f39c12', size=10, symbol='circle'),
            showlegend=False, 
            yaxis='y2'
        ))

        # 设置x轴的时间间隔为4年
        fig.update_layout(
            title='China GDP and Medal Counts Over the Years',
            xaxis=dict(
                title='Year',
                tickmode='array',  
                tickvals=list(range(1984, data['Year'].max()+1, 4)),  
                ticktext=[str(year) for year in range(1984, data['Year'].max()+1, 4)]  
            ),
            yaxis=dict(
                title='China GDP (Trillions Dollars)',
                titlefont=dict(color='#1f77b4'),  
                tickfont=dict(color='#1f77b4'), 
                side='left'
            ),
            yaxis2=dict(
                title='Medals Count',
                titlefont=dict(color='#9b59b6'),  
                tickfont=dict(color='#9b59b6'),  
                overlaying='y',  
                side='right'
            ),
            legend=dict(x=0.1, y=0.9),
            template='plotly_white',  
            hoverlabel=dict(
                font=dict(
                    family="Arial Black",  
                    size=18, 
                    color="black"  
                )
            )
        )

        st.plotly_chart(fig)

elif analysis_type == 'Bonus for Strong Events':
    st.markdown("## Bonus for Strong Events")
    if chart_type == 'Bar Chart':
        st.markdown("### Bar Chart")
        file_path = "input/athlete_events.csv" 
        df = pd.read_csv(file_path)
        summer_olympics = df[df['Season'] == 'Summer']

        sports = summer_olympics['Sport'].unique()

        selected_sport = st.selectbox("Select Sport", sports)

        sport_gold = summer_olympics[(summer_olympics['Sport'] == selected_sport) & (summer_olympics['Medal'] == 'Gold')]

        # 去重
        sport_gold_unique = sport_gold.drop_duplicates(subset=['Year', 'Event', 'Team'])

        # 按年份排序
        sorted_years = sorted(summer_olympics['Year'].unique())
        year = st.selectbox("Select Year", sorted_years)

        sport_gold_year = sport_gold_unique[sport_gold_unique['Year'] == year]
        gold_medals_by_country = sport_gold_year.groupby('Team').size().reset_index(name='Gold Medals')

        gold_medals_by_country = gold_medals_by_country.sort_values('Gold Medals', ascending=False)

        # 获取前8名国家
        top_8_countries = gold_medals_by_country.head(8)

        # 获取没有获得金牌的国家
        all_countries = summer_olympics['Team'].unique()
        countries_with_gold = gold_medals_by_country['Team'].unique()
        countries_without_gold = sorted(set(all_countries) - set(countries_with_gold))

        # 补齐到8个国家
        if len(top_8_countries) < 8:
            remaining_countries = countries_without_gold[:8 - len(top_8_countries)]
            additional_countries = pd.DataFrame(remaining_countries, columns=['Team'])
            additional_countries['Gold Medals'] = 0  # 没有金牌的国家，金牌数设为0
            top_8_countries = pd.concat([top_8_countries, additional_countries], ignore_index=True)

        # 重新排序
        top_8_countries = top_8_countries.sort_values(by=['Gold Medals', 'Team'], ascending=[False, True])

        fig = px.bar(top_8_countries,
                    x='Team',
                    y='Gold Medals',
                    title=f'Top 8 Gold Medals in {selected_sport} by Country in {year} (Summer Olympics)',
                    labels={'Team': 'Country', 'Gold Medals': 'Number of Gold Medals'},
                    color='Gold Medals',  
                    color_continuous_scale='blues') 

        fig.update_layout(
            xaxis_tickangle=90,  
            bargap=0.15,  
            bargroupgap=0.1, 
            height=600, 
            hoverlabel=dict(
                font=dict(
                    family="Arial Black",  
                    size=20,  
                    color="black" 
                )
            )
        )

        st.plotly_chart(fig)
    elif chart_type == 'Sankey Diagram':
        st.markdown("### Sankey Diagram")
        file_path = "input/athlete_events.csv"  

        df = pd.read_csv(file_path)

        summer_olympics = df[df['Season'] == 'Summer']

        gold_medals = summer_olympics[summer_olympics['Medal'] == 'Gold']

        # 去重
        gold_medals_unique = gold_medals.drop_duplicates(subset=['Year', 'Event', 'Team'])

        # 获取所有年份的唯一列表，并倒序排列
        years = sorted(gold_medals_unique['Year'].unique(), reverse=True)

        selected_year = st.selectbox("Select Year", years)

        gold_medals_by_year = gold_medals_unique[gold_medals_unique['Year'] == selected_year]
        gold_medals_by_country = gold_medals_by_year.groupby('Team').size().reset_index(name='Gold Medals')

        # 排序并选择金牌数最多的前20个国家
        top_countries = gold_medals_by_country.sort_values(by='Gold Medals', ascending=False).head(20)

        countries = top_countries['Team'].unique()
        selected_country = st.selectbox("Select Country", countries)

        country_gold_medals = gold_medals_unique[
            (gold_medals_unique['Team'] == selected_country) & (gold_medals_unique['Year'] == selected_year)]

        gold_medals_by_country_sport = country_gold_medals.groupby(['Team', 'Sport']).size().reset_index(name='Gold Medals')

        gold_medals_by_country_sport = gold_medals_by_country_sport[gold_medals_by_country_sport['Gold Medals'] > 0].dropna()

        sports = gold_medals_by_country_sport['Sport'].unique()

        colorscale = 'Blues'  

        nodes = [selected_country] + list(sports)  
        node_indices = {node: idx for idx, node in enumerate(nodes)}

        sources = []
        targets = []
        values = []
        link_colors = []

        max_gold = gold_medals_by_country_sport['Gold Medals'].max()
        min_gold = gold_medals_by_country_sport['Gold Medals'].min()

        for _, row in gold_medals_by_country_sport.iterrows():
            source_country = node_indices[row['Team']]
            target_sport = node_indices[row['Sport']]
            flow_width = row['Gold Medals'] 
            if max_gold != min_gold:
                color_value = (row['Gold Medals'] - min_gold) / (max_gold - min_gold)
                color_value = 0.3 + 0.5 * color_value  
            else:
                color_value = 0.5  

            color = px.colors.sample_colorscale(colorscale, color_value)[0]  

            values.append(flow_width)
            sources.append(source_country)
            targets.append(target_sport)
            link_colors.append(color)  

        fig = go.Figure(go.Sankey(
            node=dict(
                pad=15,  
                thickness=20, 
                line=dict(color="black", width=0.5),
                label=nodes,  
                color='lightyellow', 
                x=[0.03] * 1 + [0.6] * len(sports),  
                y=[0.52] * 1, 
                hoverlabel=dict(
                    font=dict(
                        family="Arial Black",  
                        size=12, 
                        color="black"  
                    )
                ),
            ),
            link=dict(
                source=sources,  
                target=targets, 
                value=values,  
                color=link_colors,  
                hoverlabel=dict(
                    font=dict(
                        family="Arial Black",  
                        size=20,  
                        color="black"  
                    )
                )
            )
        ))

        fig.update_layout(
            title=f"Gold Medals Flow by {selected_country} in Sport ({selected_year} Summer Olympics)",
            font_size=12,
            width=600,  
            height=500, 
            margin=dict(
                l=50,  
                r=50,  
                t=50,  
                b=50   
            ),
            autosize=True  
        )

        st.plotly_chart(fig, use_container_width=True)

    


