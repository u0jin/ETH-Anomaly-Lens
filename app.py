import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import os
from datetime import datetime
from utils.analyzer import analyze_contract
from utils.report_generator import SecurityReportGenerator
from utils.file_manager import FileManager

# 파일 관리자 초기화
file_manager = FileManager()

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

# 세션 상태 초기화
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'pdf_generated' not in st.session_state:
    st.session_state.pdf_generated = False
if 'pdf_bytes' not in st.session_state:
    st.session_state.pdf_bytes = None
if 'pdf_filename' not in st.session_state:
    st.session_state.pdf_filename = None

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
                        
                        # 분석 결과를 세션에 저장
                        st.session_state.analysis_complete = True
                        st.session_state.contract_address = contract_address
                        st.session_state.graph = graph
                        st.session_state.dangerous_functions = dangerous_functions
                        
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
                        
                        # 그래프 생성 전에 matplotlib 백엔드 설정
                        plt.switch_backend('Agg')
                        fig, ax = plt.subplots(figsize=(16, 12))  # 그래프 크기 증가
                        
                        # 더 나은 레이아웃 알고리즘 사용
                        pos = nx.spring_layout(graph, k=3, iterations=100) if len(graph.nodes()) > 1 else nx.spring_layout(graph)
                        
                        # 노드 색상 및 크기 설정
                        node_colors = ['red' if node in dangerous_functions else 'lightblue' for node in graph.nodes()]
                        node_sizes = [4000 if node in dangerous_functions else 3000 for node in graph.nodes()]  # 노드 크기 증가
                        
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
                            font_size=10,  # 폰트 크기 증가
                            font_weight='bold',
                            arrows=True,
                            edge_color=edge_colors,
                            width=2.5,  # 엣지 두께 증가
                            with_labels=True,
                            ax=ax,
                            arrowstyle='->',
                            arrowsize=25  # 화살표 크기 증가
                        )
                        
                        # 범례 위치 조정
                        legend_elements = [
                            mpatches.Patch(color='red', label='Dangerous Functions'),
                            mpatches.Patch(color='lightblue', label='Normal Functions')
                        ]
                        ax.legend(handles=legend_elements, loc='upper right', fontsize=14, bbox_to_anchor=(1.15, 1))
                        ax.set_title("Function Call Structure", fontsize=18, fontweight='bold', pad=30)
                        
                        # 그래프 여백 조정
                        plt.tight_layout()
                        plt.subplots_adjust(right=0.85)  # 범례를 위한 여백
                        
                        # 그래프 표시
                        st.pyplot(fig, clear_figure=True)
                        plt.close(fig)  # 메모리 정리
                        
                        st.header("📋 함수 호출 관계")
                        if graph.edges():
                            # 함수 호출 관계를 더 깔끔하게 표시
                            st.markdown("**함수 호출 관계:**")
                            for caller, callee in graph.edges():
                                if callee in dangerous_functions:
                                    st.markdown(f"🔴 **{caller}** → **{callee}** (위험)")
                                else:
                                    st.markdown(f"🔵 **{caller}** → **{callee}**")
                        else:
                            st.info("함수 간 호출 관계가 없습니다.")
                        
                    else:
                        st.warning("분석할 함수를 찾을 수 없습니다.")
                except Exception as e:
                    st.error(f"분석 중 오류가 발생했습니다: {str(e)}")
        else:
            st.warning("컨트랙트 주소를 입력해주세요.")

# PDF 보고서 생성 섹션 (분석이 완료된 경우에만 표시)
if st.session_state.analysis_complete:
    st.header("📋 PDF 보고서 생성")
    
    # PDF 생성 버튼
    if st.button("📋 PDF 보고서 생성 및 저장", key="save_pdf"):
        try:
            with st.spinner("PDF 보고서를 생성하고 있습니다..."):
                # 이전 분석 결과 사용
                contract_address = st.session_state.contract_address
                graph = st.session_state.graph
                dangerous_functions = st.session_state.dangerous_functions
                
                # PDF 보고서 생성
                report_generator = SecurityReportGenerator()
                pdf_bytes = report_generator.generate_report(
                    contract_address=contract_address,
                    graph=graph,
                    dangerous_functions=dangerous_functions
                )
                
                # 파일 저장
                pdf_filename = file_manager.save_pdf_report(contract_address, pdf_bytes)
                
                # 세션 상태 업데이트
                st.session_state.pdf_generated = True
                st.session_state.pdf_bytes = pdf_bytes
                st.session_state.pdf_filename = pdf_filename
                
                st.success(f"✅ PDF 보고서가 생성되었습니다!")
                
                # 보고서 미리보기 정보
                st.info("📋 보고서 내용:")
                st.write("• 제목 페이지")
                st.write("• 실행 요약")
                if dangerous_functions:
                    st.write("• 위험 함수 상세 분석")
                st.write("• 함수 호출 관계 (그래프 이미지 포함)")
                st.write("• 보안 권장사항")
                
                st.rerun()
                
        except Exception as e:
            st.error(f"PDF 보고서 생성 중 오류가 발생했습니다: {str(e)}")
            st.write(f"오류 상세: {e}")
    
    # PDF 다운로드 버튼 (생성된 경우에만 표시)
    if st.session_state.pdf_generated and st.session_state.pdf_bytes:
        st.success("📋 PDF 보고서가 준비되었습니다!")
        
        # 다운로드 버튼
        st.download_button(
            label="📥 PDF 보고서 다운로드",
            data=st.session_state.pdf_bytes,
            file_name=st.session_state.pdf_filename,
            mime="application/pdf",
            key="download_pdf"
        )
        
        # 저장된 파일 정보
        st.info(f"💾 파일명: {st.session_state.pdf_filename}")
        
        # 새로고침 버튼
        if st.button("🔄 새로고침", key="refresh"):
            st.session_state.pdf_generated = False
            st.session_state.pdf_bytes = None
            st.session_state.pdf_filename = None
            st.rerun()

st.markdown("---")
st.markdown("""
### 📝 사용법
1. 이더리움 스마트 컨트랙트 주소를 입력하세요
2. 컨트랙트 분석하기 버튼을 클릭하세요
3. 위험 함수는 빨간색으로 표시됩니다
4. 함수 호출 관계를 확인하세요
5. PDF 보고서 생성 및 저장 버튼을 클릭하세요

### ⚠️ 주의사항
- 이 도구는 교육 및 연구 목적으로 제작되었습니다
- 실제 보안 감사에는 전문 도구를 사용하세요
- 분석 결과는 참고용이며, 실제 보안 상태를 보장하지 않습니다
""") 