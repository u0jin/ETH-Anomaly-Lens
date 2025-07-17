import networkx as nx

DANGEROUS_FUNCTIONS = [
    "selfdestruct", "delegatecall", "tx.origin", "suicide", "callcode", "assembly", "low-level-call"
]

def analyze_contract(address: str):
    # 실제 구현에서는 Slither 분석 및 Etherscan 연동 필요
    # 여기서는 샘플 함수 호출 그래프를 반환
    G = nx.DiGraph()
    G.add_node("safeFunction")
    G.add_node("dangerousFunction")
    G.add_node("delegateCallFunction")
    G.add_edge("safeFunction", "dangerousFunction")
    G.add_edge("dangerousFunction", "delegateCallFunction")
    dangerous = ["dangerousFunction", "delegateCallFunction"]
    return G, dangerous 