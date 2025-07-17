# 🚨 ETH Anomaly Lens: Attack Flow Diagram

이더리움 스마트 컨트랙트의 위험 함수 호출 구조를 시각화하는 Streamlit 애플리케이션입니다.

## ✨ 주요 기능

- **스마트 컨트랙트 분석**: Etherscan API를 통해 공개된 컨트랙트 소스코드 분석
- **위험 함수 탐지**: `selfdestruct`, `delegatecall`, `tx.origin` 등 위험한 함수 자동 탐지
- **시각적 다이어그램**: NetworkX와 Matplotlib을 사용한 함수 호출 구조 시각화
- **결과 저장**: 분석 결과를 JSON 형식으로 저장 및 다운로드
- **실시간 분석**: Streamlit을 통한 실시간 웹 인터페이스

## 🎯 탐지하는 위험 함수

- `selfdestruct`: 컨트랙트 자체 파괴
- `delegatecall`: 위임 호출 (위험한 컨텍스트 변경)
- `tx.origin`: 트랜잭션 원본 주소 (피싱 공격 위험)
- `suicide`: selfdestruct의 이전 이름
- `callcode`: delegatecall의 이전 이름
- `assembly`: 인라인 어셈블리
- `low-level-call`: 저수준 호출
- `staticcall`: 정적 호출

## 🚀 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 Etherscan API 키를 설정하세요:
```
ETHERSCAN_API_KEY=your_etherscan_api_key_here
```

### 3. 애플리케이션 실행
```bash
streamlit run app.py
```

## 📖 사용법

1. **컨트랙트 주소 입력**: 분석할 스마트 컨트랙트 주소를 입력하세요
2. **분석 실행**: "컨트랙트 분석하기" 버튼을 클릭하세요
3. **결과 확인**: 위험 함수는 빨간색으로 표시됩니다
4. **결과 저장**: 분석 결과를 JSON 파일로 저장할 수 있습니다

## ⚠️ 주의사항

- **Verified 컨트랙트만 분석 가능**: 소스코드가 공개된 컨트랙트만 분석할 수 있습니다
- **교육 목적**: 이 도구는 교육 및 연구 목적으로 제작되었습니다
- **전문 감사 대체 불가**: 실제 보안 감사에는 전문 도구를 사용하세요
- **API 제한**: Etherscan API 사용량 제한에 주의하세요

## 🔧 기술 스택

- **Frontend**: Streamlit
- **그래프 시각화**: NetworkX, Matplotlib
- **API**: Etherscan API
- **언어**: Python 3.8+

## 📁 프로젝트 구조

```
ETH-Anomaly-Lens/
├── app.py              # Streamlit 메인 애플리케이션
├── utils/
│   └── analyzer.py     # 컨트랙트 분석 로직
├── requirements.txt    # Python 의존성
├── .env               # 환경 변수 (사용자 생성)
└── README.md         # 프로젝트 문서
```

## 🐛 알려진 문제

- 복잡한 Solidity 문법의 경우 정확도가 떨어질 수 있습니다
- 대용량 컨트랙트의 경우 분석 시간이 오래 걸릴 수 있습니다
- API 키 문제나 네트워크 오류 시 적절한 오류 메시지가 표시됩니다

## 🔄 최근 업데이트

- ✅ Etherscan API 연동 완료
- ✅ 위험 함수 탐지 로직 개선
- ✅ 시각화 개선 (더 나은 레이아웃, 색상 구분)
- ✅ 에러 처리 강화
- ✅ 분석 결과 저장 기능 추가

## 📞 지원

문제가 발생하거나 개선 사항이 있으시면 이슈를 등록해주세요.