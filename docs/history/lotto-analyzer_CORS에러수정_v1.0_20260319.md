# 히스토리 문서
- 프로젝트명: lotto-analyzer
- 문서명: CORS_에러수정_히스토리
- 버전: v1.0
- 변경일: 2026-03-19

## 변경 사항 및 의사결정 내역
1. **문제 상황**
   - 로또 분석기 웹페이지에서 "데이터 갱신" 시 최신 회차(1213회차 이후)가 정상적으로 로드되지 않는 현상 발생.
   - 원인: 기존 사용하던 `corsproxy.io`가 유료화 및 차단되면서 API 호출에 실패함.
2. **의사 결정**
   - 대체 퍼블릭 CORS 서비스인 `api.allorigins.win/get` 과 `api.codetabs.com/v1/proxy` 로 프록시 리스트 변경을 결정함.
3. **작업 내역**
   - `index.html` 파일의 `CORS_PROXIES` 배열을 수정함.
   - `fetchDraw` 함수 내에서 `api.allorigins.win/get` 호출 시 응답 결과가 직렬화된 JSON 텍스트(`data.contents`)로 감싸져서 전달되는 특성에 맞춰, 존재 시 `JSON.parse`하도록 로직을 개선함.
