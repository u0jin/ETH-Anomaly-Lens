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
    
    # 주소 형식 검증
    if not address.startswith('0x') or len(address) != 42:
        raise Exception("올바른 이더리움 주소 형식이 아닙니다. (0x로 시작하는 42자리 주소)")
    
    try:
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": address,
            "apikey": ETHERSCAN_API_KEY
        }
        print(f"API 요청 파라미터: {params}")
        response = requests.get(ETHERSCAN_API_URL, params=params, timeout=10)
        data = response.json()
        print(f"Etherscan API 응답: {data}")
        
        if data.get('status') == '1' and data.get('result'):
            contract_data = data['result'][0]
            if contract_data.get('SourceCode'):
                return contract_data['SourceCode']
            else:
                raise Exception("컨트랙트 소스코드가 공개되지 않았습니다. (Verified 컨트랙트만 분석 가능)")
        elif data.get('status') == '0':
            error_msg = data.get('message', 'Unknown error')
            if 'NOTOK' in error_msg:
                raise Exception("API 키가 유효하지 않거나 사용량 제한에 도달했습니다.")
            elif 'No records found' in error_msg:
                raise Exception("해당 주소의 컨트랙트를 찾을 수 없습니다.")
            else:
                raise Exception(f"API 오류: {error_msg}")
        else:
            raise Exception(f"API 응답 오류: {data}")
    except requests.exceptions.Timeout:
        raise Exception("API 요청 시간 초과. 잠시 후 다시 시도해주세요.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"네트워크 오류: {e}")
    except Exception as e:
        raise Exception(f"Etherscan API 오류: {e}")

def analyze_solidity_code(source_code: str) -> Tuple[nx.DiGraph, List[str]]:
    """Solidity 소스코드를 분석하여 함수 호출 그래프를 생성합니다."""
    G = nx.DiGraph()
    dangerous_functions = []

    # 함수 시그니처 패턴 (이름 없는 fallback/receive 포함)
    function_sig_pattern = r"((?:function\s+\w+|constructor|fallback|receive)\s*\([^)]*\)[^{]*{)"
    matches = list(re.finditer(function_sig_pattern, source_code, re.IGNORECASE))

    func_infos = []
    for i, match in enumerate(matches):
        sig_start = match.start()
        brace_start = source_code.find('{', sig_start)
        if brace_start == -1:
            continue
        # 중괄호 개수 세며 함수 본문 추출
        brace_count = 1
        func_body = '{'
        for j in range(brace_start + 1, len(source_code)):
            func_body += source_code[j]
            if source_code[j] == '{':
                brace_count += 1
            elif source_code[j] == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
        # 함수명 추출
        sig = match.group(1)
        name_match = re.search(r'function\s+(\w+)', sig)
        if name_match:
            func_name = name_match.group(1)
        elif sig.strip().startswith('constructor'):
            func_name = 'constructor'
        elif sig.strip().startswith('fallback'):
            func_name = 'fallback'
        elif sig.strip().startswith('receive'):
            func_name = 'receive'
        else:
            func_name = f'unknown_{i}'
        func_infos.append((func_name, func_body))

    all_functions = [name for name, _ in func_infos]

    # 위험 함수 패턴
    dangerous_patterns = {
        "selfdestruct": r"selfdestruct",
        "delegatecall": r"delegatecall",
        "tx.origin": r"tx\.origin",
        "suicide": r"suicide",
        "callcode": r"callcode",
        "assembly": r"assembly",
        "low-level-call": r"\.call\s*\(",
        "staticcall": r"staticcall",
        "block.timestamp": r"block\.timestamp",
        "block.number": r"block\.number"
    }

    print(f"발견된 함수들: {all_functions}")

    for func_name, func_code in func_infos:
        G.add_node(func_name)
        # 위험 함수 탐지
        for danger_type, pattern in dangerous_patterns.items():
            if re.search(pattern, func_code, re.IGNORECASE):
                print(f"위험 함수 발견: {func_name}에서 {danger_type}")
                if func_name not in dangerous_functions:
                    dangerous_functions.append(func_name)
                break
        # 함수 호출 관계
        for other_func, _ in func_infos:
            if other_func != func_name:
                call_patterns = [
                    rf"\b{re.escape(other_func)}\s*\(",
                    rf"this\.{re.escape(other_func)}\s*\(",
                    rf"super\.{re.escape(other_func)}\s*\("
                ]
                for call_pattern in call_patterns:
                    if re.search(call_pattern, func_code, re.IGNORECASE):
                        G.add_edge(func_name, other_func)
                        print(f"함수 호출 발견: {func_name} → {other_func}")
                        break
    print(f"위험 함수 목록: {dangerous_functions}")
    return G, dangerous_functions

def create_test_contract() -> str:
    """테스트용 위험 함수가 포함된 Solidity 코드를 생성합니다."""
    return '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DangerousTestContract {
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    // 위험 함수: selfdestruct
    function destroy() public {
        require(msg.sender == owner, "Not owner");
        selfdestruct(payable(owner));
    }
    
    // 위험 함수: delegatecall
    function executeDelegateCall(address target, bytes memory data) public {
        (bool success, ) = target.delegatecall(data);
        require(success, "Delegate call failed");
    }
    
    // 위험 함수: tx.origin
    function checkOrigin() public view returns (bool) {
        return tx.origin == owner;
    }
    
    // 위험 함수: assembly
    function assemblyTest() public pure returns (uint256) {
        assembly {
            let result := 42
            return(result, 32)
        }
    }
    
    // 위험 함수: low-level call
    function lowLevelCall(address target, bytes memory data) public {
        (bool success, ) = target.call(data);
        require(success, "Call failed");
    }
    
    // 일반 함수
    function normalFunction() public pure returns (string memory) {
        return "This is a normal function";
    }
    
    // 위험 함수를 호출하는 함수
    function callDangerous() public {
        normalFunction();
        checkOrigin();
    }
    
    // fallback 함수
    fallback() external payable {
        // 위험 함수 호출
        lowLevelCall(msg.sender, "");
    }
    
    // receive 함수
    receive() external payable {
        // 위험 함수 호출
        assemblyTest();
    }
}
'''

def analyze_contract(address: str) -> Tuple[nx.DiGraph, List[str]]:
    """컨트랙트를 분석하고 공격 흐름 다이어그램을 반환합니다."""
    try:
        # 테스트용 주소인 경우 더미 데이터 사용
        if address.lower() == "0x0000000000000000000000000000000000000000":
            source_code = create_test_contract()
            print("테스트용 더미 컨트랙트 사용")
        else:
            # Etherscan에서 소스코드 가져오기
            source_code = get_contract_source(address)
        
        # Solidity 코드 분석
        graph, dangerous_functions = analyze_solidity_code(source_code)
        
        if not graph.nodes():
            raise Exception("분석할 함수를 찾을 수 없습니다.")
        
        return graph, dangerous_functions
        
    except Exception as e:
        raise Exception(f"컨트랙트 분석 실패: {str(e)}") 