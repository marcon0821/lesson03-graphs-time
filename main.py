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

st.header("1. 영화별 일일 관객수 변화")

# 영화 목록 추출 (고유값)
movie_list = df['영화명'].unique().tolist()
movie_list.sort()

# 드롭다운으로 영화 선택
selected_movie = st.selectbox("영화를 선택하세요:", movie_list)

# 선택된 영화 데이터 필터링
movie_data = df[df['영화명'] == selected_movie]

# 데이터가 있는 경우에만 그래프 그리기
if not movie_data.empty:
    # Plotly 선 그래프 생성
    fig = px.line(
        movie_data, 
        x='날짜', 
        y='일관객', 
        title=f"[{selected_movie}] 일일 관객수 변화",
        labels={'일관객': '관객수(명)', '날짜': '날짜'},
        markers=True # 데이터 포인트에 마커 표시
    )
    
    # 툴팁(마우스 오버) 설정: 날짜와 관객수 명시적 표시
    fig.update_traces(hovertemplate='날짜: %{x}<br>관객수: %{y:,.0f}명')
    
    # 스트림릿에 그래프 표시
    st.plotly_chart(fig, use_container_width=True)
    
    # 알 수 있는 점 입력 칸 (사용자가 직접 입력하거나 나중에 채울 수 있도록 빈 문자열로 둠)
    st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 한 문장 요약을 적어주세요.)")
else:
    st.warning("선택한 영화의 데이터가 없습니다.")

st.divider()

st.header("2. TOP 5 영화 일일 관객수 비교")

# 1. 일관객 합계가 가장 큰 상위 5개 영화 이름 추출
top5_movies = df.groupby('영화명')['일관객'].sum().nlargest(5).index.tolist()

# 2. 상위 5개 영화의 데이터만 필터링
top5_data = df[df['영화명'].isin(top5_movies)]

# 3. Plotly 다중 선 그래프 생성 (color='영화명'으로 색상 구분)
fig2 = px.line(
    top5_data, 
    x='날짜', 
    y='일관객', 
    color='영화명',
    title="총 관객수 TOP 5 영화의 일일 관객수 변화 추이",
    labels={'일관객': '관객수(명)', '날짜': '날짜', '영화명': '영화 제목'}
)

# 툴팁(마우스 오버) 설정: 영화 이름, 날짜, 관객수 표시
fig2.update_traces(hovertemplate='<b>%{fullData.name}</b><br>날짜: %{x}<br>관객수: %{y:,.0f}명')

# 4. 스트림릿에 그래프 표시 (범례 클릭 시 영화 켜고 끄기는 Plotly 기본 동작으로 지원됨)
st.plotly_chart(fig2, use_container_width=True)

# 알 수 있는 점 입력 칸
st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 한 문장 요약을 적어주세요.)")

st.divider()

st.header("3. (그래프 추가 예정)")
st.write("이곳에 다음 그래프가 추가될 예정입니다.")
