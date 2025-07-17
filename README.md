# 🚨 ETH Anomaly Lens: Attack Flow Diagram

이더리움 스마트 컨트랙트의 위험 함수 호출 구조를 시각화하는 Streamlit 앱입니다.

## 🎯 주요 기능

- **스마트 컨트랙트 주소 입력**: 이더리움 컨트랙트 주소를 입력하여 분석
- **위험 함수 감지**: `selfdestruct`, `delegatecall`, `tx.origin` 등 위험 함수 자동 감지
- **함수 호출 구조 시각화**: NetworkX와 Matplotlib을 사용한 인터랙티브 다이어그램
- **위험 함수 강조**: 위험 함수는 빨간색으로 표시하여 시각적 구분

## 🛠️ 사용 기술

- **Streamlit**: 웹 UI 프레임워크
- **Slither**: 스마트 컨트랙트 정적 분석 도구
- **NetworkX**: 그래프 분석 및 시각화
- **Matplotlib**: 그래프 렌더링
- **Web3**: 이더리움 블록체인 연동

## 📦 설치 및 실행

### 1패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 앱 실행
```bash
streamlit run app.py
```

###3브라우저에서 접속
```
http://localhost:8501
```

## 📋 사용법

1**컨트랙트 주소 입력**: 분석할 이더리움 스마트 컨트랙트 주소를 입력
2 **분석 버튼 클릭**:🔍 컨트랙트 분석하기 버튼 클릭3. **결과 확인**: 
   - 위험 함수 개수 및 목록 확인
   - 함수 호출 구조 다이어그램 확인
   - 함수 간 호출 관계 확인

## 🔍 감지하는 위험 함수

- `selfdestruct`: 컨트랙트 자체 파괴
- `delegatecall`: 위임 호출 (위험한 컨텍스트 변경)
- `tx.origin`: 트랜잭션 원본 주소 (피싱 공격 위험)
- `suicide`: selfdestruct의 이전 이름
- `callcode`: delegatecall의 이전 이름
- `assembly`: 인라인 어셈블리
- `low-level-call`: 저수준 호출

## 📁 프로젝트 구조

```
eth-anomaly-lens/
├── app.py              # Streamlit 메인 파일
├── requirements.txt    # 필요한 패키지 명시
├── README.md          # 프로젝트 설명
└── utils/
    └── analyzer.py    # 컨트랙트 분석 모듈
```

## ⚠️ 주의사항

- 이 도구는 **교육 및 연구 목적**으로 제작되었습니다
- 실제 보안 감사에는 전문 도구를 사용하세요
- 분석 결과는 참고용이며, 실제 보안 상태를 보장하지 않습니다

## 🚀 향후 개선 계획

- ] Etherscan API 연동으로 실제 컨트랙트 소스코드 가져오기
-  더 정교한 위험 함수 감지 알고리즘
-  ] 다중 컨트랙트 분석 지원
-  ] PDF 리포트 생성 기능
- ] 실시간 블록체인 모니터링

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.

---

**ETH Anomaly Lens** - 이더리움 스마트 컨트랙트 보안 분석 도구