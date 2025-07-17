import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from utils.analyzer import analyze_contract

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
                        fig, ax = plt.subplots(figsize=(12, 8))
                        pos = nx.spring_layout(graph, k=1)
                        node_colors = [
                            'red' if node in dangerous_functions else 'lightblue'
                            for node in graph.nodes()
                        ]
                        nx.draw(
                            graph, pos,
                            node_color=node_colors,
                            node_size=2000,
                            font_size=10,
                            font_weight='bold',
                            arrows=True,
                            edge_color='gray',
                            with_labels=True,
                            ax=ax
                        )
                        legend_elements = [
                            mpatches.Patch(color='red', label='위험 함수'),
                            mpatches.Patch(color='lightblue', label='일반 함수')
                        ]
                        ax.legend(handles=legend_elements, loc='upper left')
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