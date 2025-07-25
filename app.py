import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import os
import requests
import numpy as np
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

# 이더스캔 API 설정
ETHERSCAN_API_KEY = "YourApiKeyToken"  # 실제 사용시 API 키 필요
ETHERSCAN_BASE_URL = "https://api.etherscan.io/api"

def get_contract_info(address):
    """이더스캔 API를 통해 컨트랙트 정보 가져오기"""
    try:
        params = {
            'module': 'contract',
            'action': 'getsourcecode',
            'address': address,
            'apikey': ETHERSCAN_API_KEY
        }
        response = requests.get(ETHERSCAN_BASE_URL, params=params)
        data = response.json()
        
        if data['status'] == '1' and data['result']:
            contract_info = data['result'][0]
            return {
                'contract_name': contract_info.get('ContractName', 'Unknown'),
                'compiler_version': contract_info.get('CompilerVersion', 'Unknown'),
                'optimization_used': contract_info.get('OptimizationUsed', 'Unknown'),
                'source_code': contract_info.get('SourceCode', ''),
                'abi': contract_info.get('ABI', ''),
                'verified': contract_info.get('SourceCode', '') != ''
            }
    except Exception as e:
        st.error(f"이더스캔 API 오류: {str(e)}")
    return None

def get_historical_incidents():
    """2020~2025년 7월까지 실제 기사/보고서가 열리는 사건만 incidents에 반영."""
    return [
        {
            "date": "2021-08-10",
            "platform": "🔵 이더리움 (Ethereum)",
            "incident": "Poly Network 해킹",
            "description": "크로스체인 브리지 취약점으로 $600M 탈취",
            "loss": "$600M",
            "cause": "브리지 취약점",
            "source": "https://www.coindesk.com/markets/2021/08/10/cross-chain-defi-site-poly-network-hacked-hundreds-of-millions-potentially-lost?utm_source=chatgpt.com"
        },
        {
            "date": "2022-03-23",
            "platform": "🔵 이더리움 (Ethereum)",
            "incident": "Ronin Network 해킹",
            "description": "Axie Infinity 게임 브리지 해킹, $625M 탈취",
            "loss": "$625M",
            "cause": "브리지 취약점",
            "source": "https://www.coindesk.com/tech/2022/03/29/axie-infinitys-ronin-network-suffers-625m-exploit?utm_source=chatgpt.com"
        },
        {
            "date": "2022-11-11",
            "platform": "🟣 거래소 (Exchange)",
            "incident": "FTX 붕괴",
            "description": "FTX 거래소 파산, 고객 자산 $8B 손실",
            "loss": "$8B",
            "cause": "거래소 운영 부실",
            "source": "https://apnews.com/article/ftx-sam-bankmanfried-crypto-gary-wang-09f59a3575d8a8b9fb0b444679f9c109"
        },
        {
            "date": "2023-03-13",
            "platform": "🔵 이더리움 (Ethereum)",
            "incident": "Euler Finance 해킹",
            "description": "플래시론 공격으로 $197M 탈취",
            "loss": "$197M",
            "cause": "플래시론 공격",
            "source": "https://www.chainalysis.com/blog/euler-finance-flash-loan-attack/?utm_source=chatgpt.com"
        },
        {
            "date": "2022-08-01",
            "platform": "🔵 이더리움 (Ethereum)",
            "incident": "Nomad Bridge 해킹",
            "description": "브리지 취약점으로 $45M 탈취",
            "loss": "$45M",
            "cause": "브리지 취약점",
            "source": "https://thedefiant.io/nomad-bridge-exploit"
        },
        {
            "date": "2023-06-03",
            "platform": "🔵 이더리움 (Ethereum)",
            "incident": "Atomic Wallet 해킹",
            "description": "지갑 보안 취약점으로 $100M 탈취",
            "loss": "$100M",
            "cause": "지갑 보안 취약점",
            "source": "https://www.elliptic.co/blog/analysis/north-korea-linked-atomic-wallet-heist-tops-100-million?utm_source=chatgpt.com"
        },
        {
            "date": "2022-06-24",
            "platform": "🔵 이더리움 (Ethereum)",
            "incident": "Harmony Bridge 해킹",
            "description": "브리지 취약점으로 $100M 탈취",
            "loss": "$100M",
            "cause": "브리지 취약점",
            "source": "https://www.elliptic.co/hubfs/Harmony%20Horizon%20Bridge%20Hack%20P1%20briefing%20note%20final.pdf?utm_source=chatgpt.com"
        },
        {
            "date": "2023-09-20",
            "platform": "🔵 이더리움 (Ethereum)",
            "incident": "Mixin Network 해킹",
            "description": "클라우드 서비스 공격으로 $200M 탈취",
            "loss": "$200M",
            "cause": "클라우드 서비스 취약점",
            "source": "https://www.elliptic.co/blog/mixin-network-hacked-for-200-million?utm_source=chatgpt.com"
        },
        {
            "date": "2025-03-15",
            "platform": "🟣 거래소 (Exchange)",
            "incident": "Bybit 해킹",
            "description": "중앙화 거래소 해킹, $1.5B 탈취",
            "loss": "$1.5B",
            "cause": "거래소 보안 취약점",
            "source": "https://www.chainalysis.com/blog/2025-crypto-crime-mid-year-update/"
        }
    ]

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

# 탭 생성
tab1, tab2 = st.tabs(["🔍 컨트랙트 분석", "📊 보안 사건사고"])

with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📋 컨트랙트 분석")
        contract_address = st.text_input(
            "이더리움 스마트 컨트랙트 주소",
            placeholder="0x...",
            help="분석할 스마트 컨트랙트의 주소를 입력하세요"
        )
        st.info("⚠️ 반드시 0x로 시작하는 스마트 컨트랙트 주소만 입력하세요! (트랜잭션 해시, 지갑 주소 X)")
        
        if contract_address:
            # 이더스캔 정보 가져오기
            with st.spinner("이더스캔에서 컨트랙트 정보를 가져오는 중..."):
                contract_info = get_contract_info(contract_address)
                
            if contract_info:
                st.success("✅ 이더스캔에서 컨트랙트 정보를 찾았습니다!")
                
                # 컨트랙트 기본 정보 표시
                info_col1, info_col2, info_col3 = st.columns(3)
                with info_col1:
                    st.metric("컨트랙트명", contract_info['contract_name'])
                with info_col2:
                    st.metric("컴파일러 버전", contract_info['compiler_version'])
                with info_col3:
                    st.metric("검증 상태", "✅ 검증됨" if contract_info['verified'] else "❌ 미검증")
        
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
                            fig, ax = plt.subplots(figsize=(12, 8))  # 보기 편한 크기로 조절
                            
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

with tab2:
    st.header("📊 주요 암호화폐 보안 사건사고 분석 보고서")
    st.markdown("비트코인과 이더리움의 주요 보안 사건사고를 종합적으로 분석한 보고서입니다.")
    
    incidents = get_historical_incidents()
    
    # 대시보드 스타일 개선
    st.markdown("---")
    
    # 상단 통계 카드
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Total Incidents",
            value=len(incidents),
            delta=f"{len(incidents)} major incidents"
        )
    with col2:
        ethereum_incidents = len([inc for inc in incidents if inc["platform"] == "🔵 이더리움 (Ethereum)"])
        st.metric(
            label="Ethereum Incidents",
            value=ethereum_incidents,
            delta="Smart contract/bridge-centered"
        )
    with col3:
        exchange_incidents = len([inc for inc in incidents if inc["platform"] == "🟣 거래소 (Exchange)"])
        st.metric(
            label="Exchange Incidents",
            value=exchange_incidents,
            delta="Centralized exchange-centered"
        )
    
    st.markdown("---")
    
    # 플랫폼별 필터링 및 검색
    col1, col2 = st.columns([1, 2])
    with col1:
        platform_filter = st.selectbox(
            "Select Platform",
            ["All", "🔵 이더리움 (Ethereum)", "🟣 거래소 (Exchange)"],
            help="Select a platform for analysis"
        )
    with col2:
        search_term = st.text_input(
            "Search Incident",
            placeholder="Poly, Ronin, FTX, Bybit etc.",
            help="Search incident names"
        )
    
    filtered_incidents = incidents
    if platform_filter != "All":
        filtered_incidents = [inc for inc in incidents if inc["platform"] == platform_filter]
    
    if search_term:
        filtered_incidents = [inc for inc in filtered_incidents if search_term.lower() in inc["incident"].lower()]
    
    # 시각화 섹션
    st.subheader("📈 Visual Analysis")
    
    # 탭으로 시각화 분리
    viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs(["📊 Yearly Analysis", "💰 Loss Analysis", "🎯 Attack Type", "📅 Timeline"])
    
    # 연도별 분석
    with viz_tab1:
        years = {}
        for incident in filtered_incidents:
            year = incident['date'][:4]
            years[year] = years.get(year, 0) + 1
        if years:
            fig, ax = plt.subplots(figsize=(12, 6))
            years_list = sorted(years.keys())
            counts = [years[year] for year in years_list]
            colors = plt.cm.viridis(np.linspace(0, 1, len(years_list)))
            bars = ax.bar(years_list, counts, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
            ax.set_xlabel('Year', fontsize=14, fontweight='bold')
            ax.set_ylabel('Number of Incidents', fontsize=14, fontweight='bold')
            ax.set_title('Incidents per Year', fontsize=16, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3, axis='y')
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                       f'{count}', ha='center', va='bottom', fontweight='bold', fontsize=13)
            plt.tight_layout()
            st.pyplot(fig, clear_figure=True)
            plt.close(fig)
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Year with Most Incidents**: {max(years, key=years.get)} ({max(years.values())})")
            with col2:
                st.info(f"**Period**: {min(years.keys())} ~ {max(years.keys())}")

    # 손실액 분석
    with viz_tab2:
        # 플랫폼 영어 변환 맵
        platform_map = {
            "🔵 이더리움 (Ethereum)": "Ethereum",
            "🟣 거래소 (Exchange)": "Exchange"
        }
        platform_losses = {}
        for incident in filtered_incidents:
            platform = incident["platform"]
            platform_en = platform_map.get(platform, platform)
            loss_str = incident["loss"]
            loss_str = loss_str.replace("$", "")
            if "B" in loss_str:
                loss = float(loss_str.replace("B", "")) * 1000000000
            elif "M" in loss_str:
                loss = float(loss_str.replace("M", "")) * 1000000
            elif "K" in loss_str:
                loss = float(loss_str.replace("K", "")) * 1000
            else:
                loss = float(loss_str)
            platform_losses[platform_en] = platform_losses.get(platform_en, 0) + loss
        if platform_losses:
            fig, ax = plt.subplots(figsize=(10, 6))
            platforms = list(platform_losses.keys())
            losses = list(platform_losses.values())
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
            wedges, texts, autotexts = ax.pie(losses, labels=platforms, autopct='%1.1f%%', 
                                             colors=colors[:len(platforms)], startangle=90, textprops={'fontsize': 13})
            ax.set_title('Loss Distribution by Platform', fontsize=16, fontweight='bold', pad=20)
            ax.legend(wedges, [f'{p}: ${l/1000000:.1f}M' for p, l in zip(platforms, losses)],
                     title="Loss by Platform", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=13)
            plt.tight_layout()
            st.pyplot(fig, clear_figure=True)
            plt.close(fig)

    # 공격 유형 분석
    with viz_tab3:
        import re
        import unicodedata
        # cause 영어 변환 맵 (상세)
        cause_map = {
            "재진입 공격": "Reentrancy",
            "정수 오버플로우": "Integer Overflow",
            "플래시론 공격": "Flash Loan",
            "크로스체인 브리지 취약점": "Cross-Chain Bridge",
            "거래소 보안": "Exchange Security",
            "오라클 조작": "Oracle Manipulation",
            "내부자 공격": "Insider Attack",
            "API 키 유출": "API Key Leak",
            "클라우드 서비스 취약점": "Cloud Service Vulnerability",
            "거래소 운영 실수": "Exchange Operational Error",
            "블록 타임스탬프 조작": "Block Timestamp Manipulation",
            "블록 넘버 조작": "Block Number Manipulation",
            "플래시론": "Flash Loan",
            "오버플로우": "Overflow",
            "언더플로우": "Underflow",
            "자체파괴": "Selfdestruct",
            "위험 함수": "Dangerous Function",
            "오라클 취약점": "Oracle Vulnerability",
            "브리지 해킹": "Bridge Hack",
            "사기": "Fraud",
            "피싱": "Phishing",
            "기타": "Miscellaneous",
            # 필요시 추가
        }
        def romanize_korean(text):
            try:
                from unidecode import unidecode
                return unidecode(text)
            except ImportError:
                return text
        attack_types = {}
        for incident in filtered_incidents:
            cause = incident["cause"]
            cause_no_emoji = ''.join(c for c in cause if c.isalnum() or c.isspace())
            cause_en = cause_map.get(cause_no_emoji.strip(), None)
            if not cause_en:
                if re.search(r'[가-힣]', cause_no_emoji):
                    cause_en = romanize_korean(cause_no_emoji.strip())
                else:
                    cause_en = cause_no_emoji.strip()
            # 알파벳/숫자/공백만 남기고 모두 제거
            cause_en_clean = re.sub(r'[^a-zA-Z0-9 ]', '', cause_en)
            cause_en_clean = cause_en_clean.strip()
            if not cause_en_clean:
                continue  # 완전히 빈 값은 그래프에서 제외
            attack_types[cause_en_clean] = attack_types.get(cause_en_clean, 0) + 1
        if attack_types:
            fig, ax = plt.subplots(figsize=(12, 6))
            causes = list(attack_types.keys())
            counts = list(attack_types.values())
            y_pos = np.arange(len(causes))
            bars = ax.barh(y_pos, counts, color='lightcoral', alpha=0.8, edgecolor='darkred')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(causes, fontsize=13)
            ax.set_xlabel('Number of Incidents', fontsize=14, fontweight='bold')
            ax.set_title('Incident Count by Attack Type', fontsize=16, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3, axis='x')
            for bar, count in zip(bars, counts):
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                       f'{count}', ha='left', va='center', fontweight='bold', fontsize=13)
            plt.tight_layout()
            st.pyplot(fig, clear_figure=True)
            plt.close(fig)

    # 타임라인(꺾은선)
    with viz_tab4:
        if filtered_incidents:
            year_count = {}
            year_loss = {}
            for inc in filtered_incidents:
                year = inc['date'][:4]
                year_count[year] = year_count.get(year, 0) + 1
                loss_str = inc['loss'].replace('$', '')
                if 'B' in loss_str:
                    loss = float(loss_str.replace('B', '')) * 1_000_000_000
                elif 'M' in loss_str:
                    loss = float(loss_str.replace('M', '')) * 1_000_000
                elif 'K' in loss_str:
                    loss = float(loss_str.replace('K', '')) * 1_000
                else:
                    loss = float(loss_str)
                year_loss[year] = year_loss.get(year, 0) + loss
            years = sorted(year_count.keys())
            counts = [year_count[y] for y in years]
            losses = [year_loss[y] for y in years]
            fig, ax1 = plt.subplots(figsize=(12, 6))
            ax1.plot(years, counts, marker='o', color='#4e79a7', label='Incidents', linewidth=2)
            ax1.set_xlabel('Year', fontsize=14)
            ax1.set_ylabel('Number of Incidents', fontsize=14, color='#4e79a7')
            ax1.tick_params(axis='y', labelcolor='#4e79a7', labelsize=13)
            ax1.set_title('Incident Trend by Year', fontsize=16, fontweight='bold', pad=10)
            ax1.grid(True, axis='y', alpha=0.2, linestyle='--')
            ax2 = ax1.twinx()
            ax2.plot(years, [l/1_000_000 for l in losses], marker='s', color='#e15759', label='Loss (M USD)', linewidth=2, linestyle='dashed')
            ax2.set_ylabel('Loss (Million USD)', fontsize=14, color='#e15759')
            ax2.tick_params(axis='y', labelcolor='#e15759', labelsize=13)
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=13, framealpha=0.9)
            plt.tight_layout()
            st.pyplot(fig, clear_figure=True)
            plt.close(fig)
        else:
            st.info('No incidents found for the selected condition.')
    
    st.markdown("---")
    
    # 상세 사건사고 목록 (개선된 UI)
    st.subheader("📋 Detailed Incident Analysis")
    
    # 정렬 옵션 UI 개선
    col1, col2 = st.columns([1, 1])
    with col1:
        sort_by = st.selectbox(
            "Sort by",
            ["Date", "Loss", "Platform"],
            help="Select a sorting criterion for incidents"
        )
    with col2:
        show_details = st.checkbox("Show Details", value=True)

    # 정렬 로직
    if sort_by == "Date":
        sorted_incidents = sorted(filtered_incidents, key=lambda x: x['date'])
    elif sort_by == "Loss":
        def parse_loss(incident):
            loss_str = incident["loss"].replace("$", "").replace("B", "000000000").replace("M", "000000").replace("K", "000")
            return float(loss_str)
        sorted_incidents = sorted(filtered_incidents, key=parse_loss, reverse=True)
    else:  # 플랫폼별
        sorted_incidents = sorted(filtered_incidents, key=lambda x: x['platform'])

    # 카드형 UI로 사건사고 표시
    for i, incident in enumerate(sorted_incidents, 1):
        st.markdown(f"""
<div style='border:1px solid #e0e0e0; border-radius:12px; padding:18px 20px; margin-bottom:18px; background:#fafbfc;'>
  <div style='font-size:1.2rem; font-weight:700; color:#222; margin-bottom:6px;'>{i}. {incident['incident']}</div>
  <div style='font-size:0.95rem; color:#888; margin-bottom:8px;'>
    📅 {incident['date']} | {incident['platform']}
  </div>
  <div style='font-size:1.05rem; margin-bottom:8px;'>💡 {incident['description']}</div>
  <div style='font-size:1.05rem; margin-bottom:8px;'><b>🎯 Cause:</b> <span style='color:#e15759; font-weight:600'>{incident['cause']}</span></div>
  <div style='font-size:1.05rem; margin-bottom:8px;'><b>💸 Loss:</b> <span style='color:#1976d2; font-weight:600'>{incident['loss']}</span></div>
  <a href='{incident['source']}' target='_blank' style='display:inline-block; margin-top:6px; padding:6px 14px; background:#1976d2; color:#fff; border-radius:6px; text-decoration:none; font-size:0.98rem; font-weight:500;'>🔗 Official Source</a>
</div>
""", unsafe_allow_html=True)
    
    # 보안 교훈 및 권장사항 (개선된 섹션)
    st.subheader("💡 Security Lessons and Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🛡️ Security Recommendations
        
        **Smart Contract Development**
        - ✅ Mandatory verification and auditing
        - ✅ Adherence to security best practices
        - ✅ Regular updates
        
        **Asset Storage**
        - ✅ Use multi-signature wallets
        - ✅ Decentralized asset storage
        - ✅ Cold storage utilization
        
        **Exchange Usage**
        - ✅ Select trusted exchanges
        - ✅ Enable 2FA
        - ✅ Regular security checks
        
        **Personal Security**
        - ✅ Strong password usage
        - ✅ Phishing site awareness
        - ✅ Develop and implement backup plans
        """)
    
    # 추가 통계 및 인사이트
    st.markdown("---")
    st.subheader("📊 Additional Statistics and Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **🔍 Analysis Results**
        - Ethereum incidents: Smart contract vulnerabilities centered
        - Bitcoin incidents: Centralized exchange security issues centered
        - Recent trend: Increased cross-chain bridge attacks
        """)
    
    with col2:
        st.warning("""
        **⚠️ Caution**
        - This data is for educational purposes only
        - Professional tools are required for actual security audits
        - Mandatory regular security updates
        """)
    
    with col3:
        st.success("""
        **💪 Prevention Methods**
        - Learning security best practices
        - Regular security checks
        - Consult with experts
        """) 