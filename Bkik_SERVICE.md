# 나락각 측정기 — 서비스 정의서 v1.0

> UNWORK 콘텐츠 사전 모니터링 서비스 | 해커톤 MVP

---

## 핵심 원칙

**"AI가 논란을 판단하는 것이 아니다. AI가 보고, 찾고, 조사하고, 정리한다. 사람은 판단한다."**

이 서비스는 AI가 게시 직전 콘텐츠를 전체적으로 관찰하고, 사람이 직접 하던 검색·사례 조사·정책 확인·현재 맥락 조회·위험 요소 정리를 대신 수행하여, 사람이 확인할 필요가 있는 항목만 Human Review Queue로 전달한다.

---

## UNWORK 정의

**Level 3 — 업무 대행**

| | |
|---|---|
| **사라지는 일** | 전체 재시청, 수동 검색, 과거 사례 조사, 정책 검색, 현재 이슈 확인, 자료 정리, 문제 구간 탐색 |
| **사람에게 남는 일** | 업로드 → 후보 확인 → 근거 확인 → 최종 판단 |

---

## 파이프라인

```
완성 콘텐츠
  ↓
콘텐츠 + Caption 업로드
  ↓
[1] Media Preprocessor
  ↓
[2] Signal Extractor
  ↓
[3] Candidate Generator
  ↓
[4] Query Builder
  ↓
[5] Evidence Retriever
  ├─ Rule  : Platform Policy DB
  ├─ Memory: Historical Controversy Case DB
  └─ Now   : Context Event DB + Current News Search
  ↓
[6] Evidence Synthesizer / Review Prioritizer
  ↓
[7] Human Review Queue
  ↓
[8] Human Judgment
```

**핵심 질문:** "이 구간/요소를 사람이 다시 확인할 충분한 이유가 있는가?"  
**핵심 질문이 아닌 것:** "이 콘텐츠가 논란이 날 것인가?" / "게시해도 되는가?"

---

## 상태 표현 원칙

| 허용 | 금지 |
|---|---|
| `REVIEW_REQUIRED` | "출고 가능" / "PASS" |
| `NO_CANDIDATE_FOUND` | "안전합니다" / "게시해도 됩니다" |
| Review Priority: `HIGH / MEDIUM / LOW` | 숫자 risk_score (e.g. "82%") |

> `NO_CANDIDATE_FOUND`는 안전 보증이 아님을 사용자에게 명시한다.

---

## Evidence Layer

| Layer | Source | 질문 |
|---|---|---|
| **Rule** | Platform Policy DB | 정책상 사람이 다시 확인해야 할 근거가 있는가? |
| **Memory** | Historical Controversy Case DB | 과거 유사 논란 사례가 있었는가? |
| **Now** | Context Event DB + Current News | 분석 시점에 결합되는 민감한 사회적 맥락이 있는가? |

**Evidence 노출 규칙:** 내부 Retrieval Top 3~5 → 사용자에게 최대 1~3개만 노출  
(많이 보여주면 검색 업무가 사용자에게 역귀환)

---

## Risk Category

| ID | 분류 | 우선순위 |
|---|---|---|
| R-01 | 정치·선거 맥락 | P0 |
| R-02 | 역사·국가·기념일 맥락 | P0 |
| R-03 | 혐오·차별·젠더·문화 | P0 |
| R-04 | 민감 발언·욕설·성적·공격 표현 | P0 |
| R-05 | 평판·사실관계 확인 필요 주장 | P0 |
| R-06 | 사건·재난·애도 시의성 | P1 |
| R-07 | 제3자 개인정보·노출 | P1 |
| R-08 | 광고·협찬 컴플라이언스 | P1 |

---

## 영상 분석 원칙

- **프레임 추출:** 0.5~1초 간격 또는 장면 변화 기반 (시각 Signal 수집용)
- **의미 판단:** 5~10초 또는 문장 단위 Context Window (1초 프레임 독립 판정 금지)
- **인접 Candidate 병합:** 겹치는 구간은 하나의 Finding으로 통합

> "초 단위 위치 추적, 문맥 단위 판단"

---

## MVP 범위

### P0 (반드시 엔드투엔드 동작)
- 30초 이하 MP4 + Caption 업로드
- 영상 전처리 / STT + timestamp / 화면 텍스트 추출 / 프레임 Signal 추출
- Context Window 기반 Candidate 탐지
- Query 자동 생성 → Policy / Historical / Context / News 조회
- Evidence Synthesis → Human Review Queue
- Timestamp Seek (Candidate 클릭 → 해당 구간 재생)
- Evidence Card (이유·사례·출처 한 화면)
- Error / Fallback

### P1 (P0 안정 후)
- 정적 이미지(JPG/PNG) 입력
- Candidate 자동 병합 고도화
- Review Status 저장 / 분석 이력
- 수정본 Re-scan

### CUT (이번 명세에서 구현하지 않음)
- 게시 후 자동 모니터링 / 댓글·SNS 지속 추적
- 캡션·이미지·영상 자동 수정 / 컷·블러 / 생성형 장면 교체
- 자동 게시
- 단일 risk_score 대시보드
- 법적 확정 판정
- 전 커뮤니티 실시간 크롤링

---

## Data Source 원칙

- **나무위키:** 사례 발견용 Retrieval Index 후보로만 활용. 최종 Evidence는 뉴스/공식 출처 우선
- **Historical Case DB:** 최근 5년 기준 30~50개 검증 사례. 핵심 대표 사례는 예외적으로 포함 가능 (수동 검증 후)
- **Current News:** 외부 API 실패 시 Policy + Historical + Context Event만으로 Core Demo 완주
- **근거 없으면:** AI가 근거를 생성하지 않고 "관련 근거 확인되지 않음" 반환

---

## UNWORK가 무너지는 조건

1. AI 결과가 불안해서 사람이 결국 영상을 처음부터 끝까지 다시 봐야 함
2. Finding마다 너무 많은 Evidence를 읽어야 함
3. 오탐이 많아 Review Queue가 사실상 전체 콘텐츠
4. 근거가 불분명해 사용자가 다시 직접 검색해야 함
5. 자동 수정 등 부가 기능 때문에 새로운 검증 업무가 더 생김

> 따라서 제품 성공의 중심은 **"Human Review Queue를 얼마나 작고 근거 있게 만드는가"**

---

## 개발 의사결정 체크리스트

새 기능 추가 전:
1. 사람이 게시 전에 하던 모니터링 업무를 실제로 줄이는가?
2. 새로운 입력·검증·오류 처리 업무가 더 많이 생기지 않는가?
3. Human Review Queue를 더 작고 정확하게 만드는가?
4. 3일 MVP 핵심 플로우를 깨지 않는가?

**YES가 명확하지 않으면 구현하지 않는다.**
