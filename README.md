# 삐빅 백엔드

FastAPI 기반 콘텐츠 사전 모니터링 API입니다. AI가 게시 가능 여부를 판정하지 않고,
사람이 다시 확인할 후보와 근거를 Human Review Queue로 정리합니다.

## 콘텐츠 검수 API

`POST /contents`는 `multipart/form-data`를 받습니다. `text`, `files`는 함께 또는 각각
보낼 수 있으며, 파일은 MP4, JPG/JPEG, PNG, WEBP만 지원합니다.

```bash
curl -X POST http://localhost:8000/contents \
  -F "title=여름 캠페인 숏폼 영상" \
  -F "text=게시할 캡션 문구" \
  -F "files=@campaign.mp4;type=video/mp4"
```

응답의 `status`는 처음에 `QUEUED`입니다. 실제 분석 워커가 작업을 시작·완료하면
`ANALYZING`, `COMPLETED`, `FAILED`로 갱신합니다. `COMPLETED` 전에는 결과를 만들어
반환하지 않습니다.

| Endpoint | 설명 |
| --- | --- |
| `POST /contents` | 텍스트·이미지·영상 검수 요청 생성 |
| `GET /contents` | 최근 검수 요청 목록 |
| `GET /contents/{submission_id}` | 검수 요청과 원본 자산 메타데이터 |
| `GET /contents/{submission_id}/analysis` | 분석 상태와 검수 후보·근거 |
| `GET /contents/{submission_id}/assets/{asset_id}` | 원본 자산 조회 |

로컬/단일 EC2 MVP에서는 `UPLOAD_DIRECTORY`에 원본을 저장합니다. 다중 인스턴스나
운영 배포 전에는 같은 `ContentStorage` 포트에 S3 어댑터를 연결해야 합니다.
