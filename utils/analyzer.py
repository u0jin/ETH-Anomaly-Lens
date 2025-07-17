import os
import networkx as nx
import requests
import re
from typing import Tuple, List
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_API_URL = "https://api.etherscan.io/api"

DANGEROUS_FUNCTIONS = [
    "selfdestruct", "delegatecall", "tx.origin", "suicide", "callcode", "assembly", "low-level-call"
]

def get_contract_source(address: str) -> str:
    """Etherscan API를 통해 컨트랙트 소스코드를 가져옵니다."""
    if not ETHERSCAN_API_KEY:
        raise Exception("ETHERSCAN_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    
    try:
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": address,
            "apikey": ETHERSCAN_API_KEY
        }
        print(f"API 요청 파라미터: {params}")
        response = requests.get(ETHERSCAN_API_URL, params=params)
        data = response.json()
        print(f"Etherscan API 응답: {data}")
        
        if data['status'] == '1' and data['result']:
            contract_data = data['result'][0]
            if contract_data['SourceCode']:
                return contract_data['SourceCode']
            else:
                raise Exception("컨트랙트 소스코드가 공개되지 않았습니다.")
        else:
            raise Exception(f"API 오류: {data.get('message', 'Unknown error')}")
    except Exception as e:
        raise Exception(f"Etherscan API 오류: {e}")

def analyze_solidity_code(source_code: str) -> Tuple[nx.DiGraph, List[str]]:
    """Solidity 소스코드를 분석하여 함수 호출 그래프를 생성합니다."""
    G = nx.DiGraph()
    dangerous_functions = []
    
    # 함수 정의 찾기 (더 정확한 패턴)
    function_pattern = r"function\s+(\w+)\s*\([^)]*\)\s*(?:public|private|internal|external)?\s*(?:view|pure|payable)?\s*{"
    functions = re.findall(function_pattern, source_code)
    
    # 위험 함수 패턴
    dangerous_patterns = {
        "selfdestruct": r"selfdestruct\s*\(",
        "delegatecall": r"\.delegatecall\s*\(",
        "tx.origin": r"\.origin",
        "suicide": r"suicide\s*\(",
        "callcode": r"\.callcode\s*\(",
        "assembly": r"assembly\s*{",
        "low-level-call": r"\.call\s*\("
    }
    
    # 각 함수 분석
    for func_name in functions:
        G.add_node(func_name)
        
        # 함수 내부 코드 추출
        func_start = source_code.find(f'function {func_name}()')
        if func_start != -1:
            # 함수 본문 찾기
            brace_count = 0
            func_code = ""
            start_pos = source_code.find('{', func_start)
            
            if start_pos != -1:
                for i in range(start_pos, len(source_code)):
                    char = source_code[i]
                    func_code += char
                    
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            break
                
                # 위험 함수 호출 검사
                for danger_type, pattern in dangerous_patterns.items():
                    if re.search(pattern, func_code):
                        if func_name not in dangerous_functions:
                            dangerous_functions.append(func_name)
                        break
                
                # 함수 호출 관계 찾기
                for other_func in functions:
                    if other_func != func_name:
                        call_pattern = rf"\b{other_func}\s*\("
                        if re.search(call_pattern, func_code):
                            G.add_edge(func_name, other_func)
    
    return G, dangerous_functions

def analyze_contract(address: str) -> Tuple[nx.DiGraph, List[str]]:
    """컨트랙트를 분석하고 공격 흐름 다이어그램을 반환합니다."""
    try:
        # Etherscan에서 소스코드 가져오기
        source_code = get_contract_source(address)
        
        # Solidity 코드 분석
        graph, dangerous_functions = analyze_solidity_code(source_code)
        
        if not graph.nodes():
            raise Exception("분석할 함수를 찾을 수 없습니다.")
        
        return graph, dangerous_functions
        
    except Exception as e:
        raise Exception(f"컨트랙트 분석 실패: {str(e)}") 