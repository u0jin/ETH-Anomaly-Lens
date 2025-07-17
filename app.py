import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
from datetime import datetime
from utils.analyzer import analyze_contract

# 한글 폰트 설정
import matplotlib.font_manager as fm
import platform

# 시스템에 설치된 한글 폰트 찾기
def get_korean_font():
    if platform.system() == 'Darwin':  # macOS
        # macOS에서 사용 가능한 한글 폰트들
        korean_fonts = ['AppleGothic', 'Apple SD Gothic Neo', 'NanumGothic', 'Malgun Gothic']
        for font in korean_fonts:
            try:
                fm.findfont(font)
                return font
            except:
                continue
    elif platform.system() == 'Windows':
        return 'Malgun Gothic'
    else:  # Linux
        return 'DejaVu Sans'
    
    # 기본값
    return 'DejaVu Sans'

# 폰트 설정
plt.rcParams['font.family'] = get_korean_font()
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

st.set_page_config(
    page_title="ETH Anomaly Lens",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 ETH Anomaly Lens: Attack Flow Diagram")
st.markdown("이더리움 스마트 컨트랙트의 위험 함수 호출 구조를 시각화합니다.")

st.sidebar.header("설정")
st.sidebar.markdown("""
### 위험 함수 목록
- `selfdestruct`: 컨트랙트 자체 파괴
- `delegatecall`: 위임 호출 (위험한 컨텍스트 변경)
- `tx.origin`: 트랜잭션 원본 주소 (피싱 공격 위험)
- `suicide`: selfdestruct의 이전 이름
- `callcode`: delegatecall의 이전 이름
- `assembly`: 인라인 어셈블리
- `low-level-call`: 저수준 호출
""")

col1, col2 = st.columns([2, 1])

with col1:
    st.header("📋 컨트랙트 분석")
    contract_address = st.text_input(
        "이더리움 스마트 컨트랙트 주소",
        placeholder="0x...",
        help="분석할 스마트 컨트랙트의 주소를 입력하세요"
    )
    st.info("⚠️ 반드시 0x로 시작하는 스마트 컨트랙트 주소만 입력하세요! (트랜잭션 해시, 지갑 주소 X)")
    if st.button("🔍 컨트랙트 분석하기"):
        if contract_address:
            with st.spinner("컨트랙트를 분석하고 있습니다..."):
                try:
                    graph, dangerous_functions = analyze_contract(contract_address)
                    if graph.nodes():
                        st.success("분석이 완료되었습니다!")
                        with col2:
                            st.header("📊 분석 결과")
                            st.metric("발견된 위험 함수", len(dangerous_functions))
                            st.metric("전체 함수", len(graph.nodes()))
                            if dangerous_functions:
                                st.warning("🚨 발견된 위험 함수:")
                                for func in dangerous_functions:
                                    st.write(f"• `{func}`")
                            else:
                                st.success("✅ 위험 함수가 발견되지 않았습니다.")
                        st.header("🔄 함수 호출 구조")
                        fig, ax = plt.subplots(figsize=(14, 10))
                        
                        # 더 나은 레이아웃 알고리즘 사용
                        pos = nx.spring_layout(graph, k=2, iterations=50) if len(graph.nodes()) > 1 else nx.spring_layout(graph)
                        
                        # 노드 색상 및 크기 설정
                        node_colors = ['red' if node in dangerous_functions else 'lightblue' for node in graph.nodes()]
                        node_sizes = [3000 if node in dangerous_functions else 2000 for node in graph.nodes()]
                        
                        # 엣지 색상 설정 (위험 함수로 가는 엣지는 빨간색)
                        edge_colors = []
                        for u, v in graph.edges():
                            if v in dangerous_functions:
                                edge_colors.append('red')
                            else:
                                edge_colors.append('gray')
                        
                        # 그래프 그리기
                        nx.draw(
                            graph, pos,
                            node_color=node_colors,
                            node_size=node_sizes,
                            font_size=9,
                            font_weight='bold',
                            arrows=True,
                            edge_color=edge_colors,
                            width=2,
                            with_labels=True,
                            ax=ax,
                            arrowstyle='->',
                            arrowsize=20
                        )
                        
                        # 범례
                        legend_elements = [
                            mpatches.Patch(color='red', label='Dangerous Functions'),
                            mpatches.Patch(color='lightblue', label='Normal Functions')
                        ]
                        ax.legend(handles=legend_elements, loc='upper left', fontsize=12)
                        ax.set_title("Function Call Structure", fontsize=16, fontweight='bold', pad=20)
                        
                        st.pyplot(fig)
                        st.header("📋 함수 호출 관계")
                        if graph.edges():
                            for caller, callee in graph.edges():
                                if callee in dangerous_functions:
                                    st.write(f"🔴 `{caller}` → `{callee}` (위험)")
                                else:
                                    st.write(f"🔵 `{caller}` → `{callee}`")
                        else:
                            st.info("함수 간 호출 관계가 없습니다.")
                        
                        # 분석 결과 저장
                        if st.button("💾 분석 결과 저장"):
                            analysis_result = {
                                "contract_address": contract_address,
                                "analysis_date": datetime.now().isoformat(),
                                "total_functions": len(graph.nodes()),
                                "dangerous_functions": dangerous_functions,
                                "function_calls": list(graph.edges()),
                                "graph_data": {
                                    "nodes": list(graph.nodes()),
                                    "edges": list(graph.edges())
                                }
                            }
                            
                            filename = f"analysis_{contract_address}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                            with open(filename, 'w', encoding='utf-8') as f:
                                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
                            
                            st.success(f"분석 결과가 {filename}에 저장되었습니다!")
                            st.download_button(
                                label="📥 결과 파일 다운로드",
                                data=json.dumps(analysis_result, ensure_ascii=False, indent=2),
                                file_name=filename,
                                mime="application/json"
                            )
                    else:
                        st.warning("분석할 함수를 찾을 수 없습니다.")
                except Exception as e:
                    st.error(f"분석 중 오류가 발생했습니다: {str(e)}")
        else:
            st.warning("컨트랙트 주소를 입력해주세요.")

st.markdown("---")
st.markdown("""
### 📝 사용법
1. 이더리움 스마트 컨트랙트 주소를 입력하세요
2. 컨트랙트 분석하기 버튼을 클릭하세요
3. 위험 함수는 빨간색으로 표시됩니다
4. 함수 호출 관계를 확인하세요

### ⚠️ 주의사항
- 이 도구는 교육 및 연구 목적으로 제작되었습니다
- 실제 보안 감사에는 전문 도구를 사용하세요
- 분석 결과는 참고용이며, 실제 보안 상태를 보장하지 않습니다
""") 