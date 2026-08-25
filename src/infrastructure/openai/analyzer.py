import base64
import json

from openai import AsyncOpenAI

from src.domain.content.entity import EvidenceLayer, FindingEvidence, ReviewFinding, ReviewPriority

_SYSTEM_PROMPT = """당신은 한국 콘텐츠 크리에이터를 위한 콘텐츠 사전 검수 보조 AI입니다.

입력된 텍스트, 이미지, 또는 둘 다를 분석하여 사람이 검토해야 할 항목만 추출하세요.

중요 원칙:
- 게시 가능/불가를 판단하지 마세요.
- 숫자 위험 점수(예: 82%)를 부여하지 마세요.
- 실제로 검토가 필요한 항목만 후보화하세요. 문제가 없으면 findings를 빈 배열로 반환하세요.

Risk 분류 (category_code):
R-01: 정치·선거 맥락
R-02: 역사·국가·기념일 맥락
R-03: 혐오·차별·젠더·문화
R-04: 민감 발언·욕설·성적·공격 표현
R-05: 평판·사실관계 확인 필요 주장
R-06: 사건·재난·애도 시의성
R-07: 제3자 개인정보·노출
R-08: 광고·협찬 컴플라이언스

우선순위:
HIGH: 즉각 검토 필요
MEDIUM: 검토 권장
LOW: 참고 사항

다음 JSON 형식으로만 응답하세요:
{
  "findings": [
    {
      "type": ["text"],
      "category_code": "R-03",
      "priority": "HIGH",
      "signal_type": "혐오 표현",
      "reason": "검토가 필요한 이유를 1-2문장으로 설명",
      "excerpt": "문제가 되는 텍스트 원문 인용 (이미지면 묘사)",
      "evidences": [
        {
          "layer": "RULE",
          "title": "관련 정책 또는 근거 명칭",
          "source_url": "https://...",
          "excerpt": "정책 핵심 내용 요약"
        }
      ]
    }
  ]
}

type 필드 규칙:
- 텍스트에서 발견: ["text"]
- 이미지에서 발견: ["image"]
- 영상에서 발견: ["video"]
- 텍스트+이미지 조합에서 발견: ["text", "image"]"""


async def analyze(
    *,
    text: str | None = None,
    images: list[tuple[bytes, str]] | None = None,  # (content, mime_type)
    api_key: str,
) -> list[ReviewFinding]:
    client = AsyncOpenAI(api_key=api_key)
    user_content: list[dict] = _build_user_content(text, images or [])
    response = await client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
    )
    content = response.choices[0].message.content
    if not content:
        return []
    raw = json.loads(content)
    return _parse(raw.get("findings", []))


def _build_user_content(text: str | None, images: list[tuple[bytes, str]]) -> list[dict]:
    parts: list[dict] = []

    if text and images:
        parts.append({"type": "text", "text": f"다음 텍스트와 이미지를 함께 검수해주세요.\n\n텍스트:\n{text[:8000]}"})
    elif text:
        parts.append({"type": "text", "text": f"다음 텍스트를 검수해주세요:\n\n{text[:8000]}"})
    elif images:
        parts.append({"type": "text", "text": "다음 이미지를 검수해주세요:"})

    for content, mime_type in images[:4]:  # GPT-4o 최대 이미지 수 제한
        b64 = base64.b64encode(content).decode()
        parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type};base64,{b64}", "detail": "high"},
        })

    return parts


def _parse(items: list[dict]) -> list[ReviewFinding]:
    findings = []
    for item in items:
        try:
            priority = ReviewPriority(item.get("priority", "LOW"))
        except ValueError:
            priority = ReviewPriority.LOW

        evidences = []
        for ev in item.get("evidences", [])[:3]:
            try:
                layer = EvidenceLayer(ev.get("layer", "RULE"))
            except ValueError:
                layer = EvidenceLayer.RULE
            evidences.append(FindingEvidence(
                layer=layer,
                title=ev.get("title", ""),
                source_url=ev.get("source_url", ""),
                excerpt=ev.get("excerpt"),
            ))

        findings.append(ReviewFinding(
            category_code=item.get("category_code", "R-00"),
            priority=priority,
            signal_type=item.get("signal_type", ""),
            reason=item.get("reason", ""),
            excerpt=item.get("excerpt"),
            evidences=evidences,
            media_types=item.get("type", []),
        ))
    return findings
