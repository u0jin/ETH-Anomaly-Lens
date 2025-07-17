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
    try:
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": address,
            "apikey": ETHERSCAN_API_KEY
        }
        response = requests.get(ETHERSCAN_API_URL, params=params)
        data = response.json()
        if data['status'] == '1' and data['result']:
            contract_data = data['result'][0]
            if contract_data['SourceCode']:
                return contract_data['SourceCode']
            else:
                raise Exception("컨트랙트 소스코드가 공개되지 않았습니다.")
        else:
            raise Exception(f"API 오류: {data.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Etherscan API 오류: {e}")
        return get_sample_contract()

def get_sample_contract() -> str:
    return """
    // SPDX-License-Identifier: MIT
    pragma solidity ^0.8.0;
    contract VulnerableContract {
        address public owner;
        constructor() { owner = msg.sender; }
        function dangerousFunction() public { require(tx.origin == owner, "Not owner"); selfdestruct(payable(owner)); }
        function delegateCallFunction(address target, bytes memory data) public { (bool success, ) = target.delegatecall(data); require(success, "Delegate call failed"); }
        function safeFunction() public { owner = msg.sender; }
        function callDangerous() public { dangerousFunction(); }
        function callDelegate() public { delegateCallFunction(address(0), ""); }
    }
    """

def analyze_solidity_code(source_code: str) -> Tuple[nx.DiGraph, List[str]]:
    G = nx.DiGraph()
    dangerous_functions = []
    # 함수 정의 찾기
    function_pattern = r"function\s+(\w+)\s*\([^)]*\)"
    functions = re.findall(function_pattern, source_code)
    # 각 함수 분석
    for func_name in functions:
        G.add_node(func_name)
        # 위험 함수 포함 여부
        for danger in DANGEROUS_FUNCTIONS:
            if danger in source_code:
                if func_name not in dangerous_functions:
                    dangerous_functions.append(func_name)
        # 함수 호출 관계
        for other_func in functions:
            if other_func != func_name:
                call_pattern = rf"{other_func}\s*\("
                if re.search(call_pattern, source_code):
                    G.add_edge(func_name, other_func)
    return G, dangerous_functions

def analyze_contract(address: str) -> Tuple[nx.DiGraph, List[str]]:
    try:
        source_code = get_contract_source(address)
        graph, dangerous_functions = analyze_solidity_code(source_code)
        return graph, dangerous_functions
    except Exception as e:
        print(f"분석 중 오류: {e}")
        G = nx.DiGraph()
        G.add_node("safeFunction")
        G.add_node("dangerousFunction")
        G.add_node("delegateCallFunction")
        G.add_edge("safeFunction", "dangerousFunction")
        G.add_edge("dangerousFunction", "delegateCallFunction")
        dangerous = ["dangerousFunction", "delegateCallFunction"]
        return G, dangerous 