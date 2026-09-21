import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    # 날짜 열을 문자열로 읽어오기 위해 dtype 설정
    df = pd.read_csv(url, dtype={'날짜': str})
    
    # '날짜' 열을 YYYY-MM-DD 형식의 datetime 객체로 변환
    df['날짜'] = pd.to_datetime(df['날짜'], format='%Y%m%d')
    return df

df = load_data()

with st.expander("원본 데이터 확인하기"):
    st.dataframe(df.head())

# --- 1. 영화별 일일 관객수 변화 ---
st.header("1. 영화별 일일 관객수 변화")

movie_list = df['영화명'].unique().tolist()
movie_list.sort()

selected_movie = st.selectbox("영화를 선택하세요:", movie_list)

movie_data = df[df['영화명'] == selected_movie]

if not movie_data.empty:
    fig1 = px.line(
        movie_data, 
        x='날짜', 
        y='일관객', 
        title=f"[{selected_movie}] 일일 관객수 변화",
        labels={'일관객': '관객수(명)', '날짜': '날짜'},
        markers=True
    )
    
    fig1.update_traces(hovertemplate='날짜: %{x}<br>관객수: %{y:,.0f}명')
    st.plotly_chart(fig1, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 한 문장 요약을 적어주세요.)")
else:
    st.warning("선택한 영화의 데이터가 없습니다.")

st.divider()

# --- 2. TOP 5 영화 일일 관객수 비교 ---
st.header("2. TOP 5 영화 일일 관객수 비교")

top5_movies = df.groupby('영화명')['일관객'].sum().nlargest(5).index.tolist()
top5_data = df[df['영화명'].isin(top5_movies)]

fig2 = px.line(
    top5_data, 
    x='날짜', 
    y='일관객', 
    color='영화명',
    title="총 관객수 TOP 5 영화의 일일 관객수 변화 추이",
    labels={'일관객': '관객수(명)', '날짜': '날짜', '영화명': '영화 제목'}
)

fig2.update_traces(hovertemplate='<b>%{fullData.name}</b><br>날짜: %{x}<br>관객수: %{y:,.0f}명')
st.plotly_chart(fig2, use_container_width=True)
st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 한 문장 요약을 적어주세요.)")

st.divider()

# --- 3. 날짜별 10위권 일관객 합계 (영역 그래프) ---
st.header("3. 날짜별 10위권 일관객 전체 합계")

daily_total = df.groupby('날짜')['일관객'].sum().reset_index()

fig3 = px.area(
    daily_total,
    x='날짜',
    y='일관객',
    title="일별 TOP 10 영화 관객수 전체 합계 추이",
    labels={'일관객': '총 관객수(명)', '날짜': '날짜'}
)

fig3.update_traces(hovertemplate='날짜: %{x}<br>총 관객수: %{y:,.0f}명')

top3_dates = daily_total.nlargest(3, '일관객')

for idx, row in top3_dates.iterrows():
    date_str = row['날짜'].strftime('%Y-%m-%d')
    audience_cnt = row['일관객']
    fig3.add_annotation(
        x=row['날짜'],
        y=audience_cnt,
        text=f"<b>{date_str}</b><br>({audience_cnt:,.0f}명)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="red",
        ax=0,
        ay=-40,
        bgcolor="white",
        bordercolor="red",
        borderwidth=1
    )

st.plotly_chart(fig3, use_container_width=True)
st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 한 문장 요약을 적어주세요.)")

st.divider()

# --- 4. 총 관객수 TOP 10 영화 (가로 막대그래프) ---
st.header("4. 총 관객수 TOP 10 영화")

movie_stats = df.groupby('영화명').agg(
    총관객=('일관객', 'sum'),
    TOP10일수=('날짜', 'nunique')
).reset_index()

top10_movies = movie_stats.nlargest(10, '총관객')

fig4 = px.bar(
    top10_movies,
    x='총관객',
    y='영화명',
    orientation='h',
    custom_data=['TOP10일수'],
    title="기간 내 총 관객수 TOP 10 영화",
    labels={'총관객': '총 관객수(명)', '영화명': '영화 제목'}
)

fig4.update_layout(yaxis={'categoryorder': 'total ascending'})
fig4.update_traces(
    hovertemplate='<b>%{y}</b><br>총 관객수: %{x:,.0f}명<br>10위권 진입 일수: %{customdata[0]}일<extra></extra>'
)

st.plotly_chart(fig4, use_container_width=True)
st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 한 문장 요약을 적어주세요.)")

st.divider()

# --- 5. 월 × 요일별 일관객 합계 (히트맵) ---
st.header("5. 월 × 요일별 일관객 합계 히트맵")

# 날짜 데이터에서 월과 요일 추출
day_map = {0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일', 5: '토요일', 6: '일요일'}
df_heatmap = df.copy()
df_heatmap['요일'] = df_heatmap['날짜'].dt.dayofweek.map(day_map)
df_heatmap['월'] = df_heatmap['날짜'].dt.month.astype(str) + '월'

# 순서 정렬 설정 (월요일~일요일, 1월~12월)
day_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
unique_months = sorted(df['날짜'].dt.month.unique())
month_order = [f"{m}월" for m in unique_months]

# 피벗 테이블 생성
pivot_df = df_heatmap.pivot_table(index='월', columns='요일', values='일관객', aggfunc='sum')
pivot_df = pivot_df.reindex(index=month_order, columns=day_order)

# 히트맵 생성
fig5 = px.imshow(
    pivot_df,
    labels=dict(x="요일", y="월", color="총 관객수(명)"),
    title="월 × 요일별 관객수 분포 히트맵",
    color_continuous_scale="Blues",
    text_auto=',.0f'
)

fig5.update_traces(
    hovertemplate='<b>%{y} %{x}</b><br>총 관객수: %{z:,.0f}명<extra></extra>'
)

st.plotly_chart(fig5, use_container_width=True)
st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 한 문장 요약을 적어주세요.)")
