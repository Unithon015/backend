from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyCatalogSeed:
    policy_code: str
    title: str
    review_category: str
    source_url: str


META_COMMUNITY_STANDARDS: tuple[PolicyCatalogSeed, ...] = (
    PolicyCatalogSeed("META_COORDINATING_HARM", "가해 행위 도모 및 범죄 조장", "COORDINATING_HARM_CRIME", "https://transparency.meta.com/policies/community-standards/coordinating-harm-publicizing-crime/"),
    PolicyCatalogSeed("META_DANGEROUS_ORGANIZATIONS", "위험한 단체 및 개인", "DANGEROUS_INDIVIDUALS_ORGANIZATIONS", "https://transparency.meta.com/policies/community-standards/dangerous-individuals-organizations/"),
    PolicyCatalogSeed("META_FRAUD_SCAMS", "사기, 스캠 및 기만적 행위", "FRAUD_SCAMS_DECEPTION", "https://transparency.meta.com/policies/community-standards/fraud-scams/"),
    PolicyCatalogSeed("META_REGULATED_GOODS", "규제 상품 및 서비스", "REGULATED_GOODS", "https://transparency.meta.com/policies/community-standards/regulated-goods/"),
    PolicyCatalogSeed("META_VIOLENCE_INCITEMENT", "폭력 및 선동", "VIOLENCE_INCITEMENT", "https://transparency.meta.com/policies/community-standards/violence-incitement/"),
    PolicyCatalogSeed("META_ADULT_SEXUAL_EXPLOITATION", "성인 대상 성적 학대", "ADULT_SEXUAL_EXPLOITATION", "https://transparency.meta.com/policies/community-standards/sexual-exploitation-adults/"),
    PolicyCatalogSeed("META_BULLYING_HARASSMENT", "따돌림 및 괴롭힘", "BULLYING_HARASSMENT", "https://transparency.meta.com/policies/community-standards/bullying-harassment/"),
    PolicyCatalogSeed("META_CHILD_SAFETY", "아동 대상 성적 학대, 학대 및 나체 이미지", "CHILD_SAFETY", "https://transparency.meta.com/policies/community-standards/child-sexual-exploitation-abuse-nudity/"),
    PolicyCatalogSeed("META_HUMAN_EXPLOITATION", "인신 착취", "HUMAN_EXPLOITATION", "https://transparency.meta.com/policies/community-standards/human-exploitation/"),
    PolicyCatalogSeed("META_SUICIDE_SELF_INJURY", "자살, 자해, 섭식 장애", "SUICIDE_SELF_INJURY", "https://transparency.meta.com/policies/community-standards/suicide-self-injury/"),
    PolicyCatalogSeed("META_ADULT_NUDITY", "성인 나체 이미지 및 성적 행위", "ADULT_NUDITY_SEXUAL_ACTIVITY", "https://transparency.meta.com/policies/community-standards/adult-nudity-sexual-activity/"),
    PolicyCatalogSeed("META_SEXUAL_SOLICITATION", "성인 성매매 알선 및 성적으로 노골적인 표현", "SEXUAL_SOLICITATION", "https://transparency.meta.com/policies/community-standards/sexual-solicitation/"),
    PolicyCatalogSeed("META_HATE_SPEECH", "혐오 행동", "HATE_DISCRIMINATION_CULTURE", "https://transparency.meta.com/policies/community-standards/hate-speech/"),
    PolicyCatalogSeed("META_PRIVACY", "개인정보처리방침 위반", "PERSONAL_DATA", "https://transparency.meta.com/policies/community-standards/privacy-violations-image-privacy-rights/"),
    PolicyCatalogSeed("META_VIOLENT_GRAPHIC_CONTENT", "폭력적이고 자극적인 내용", "VIOLENT_GRAPHIC_CONTENT", "https://transparency.meta.com/policies/community-standards/violent-graphic-content/"),
    PolicyCatalogSeed("META_ACCOUNT_INTEGRITY", "계정 무결성", "ACCOUNT_INTEGRITY", "https://transparency.meta.com/policies/community-standards/account-integrity/"),
    PolicyCatalogSeed("META_AUTHENTIC_IDENTITY", "실제 신원 표현", "AUTHENTIC_IDENTITY", "https://transparency.meta.com/policies/community-standards/authentic-identity-representation/"),
    PolicyCatalogSeed("META_CYBERSECURITY", "사이버 보안", "CYBERSECURITY", "https://transparency.meta.com/policies/community-standards/cybersecurity/"),
    PolicyCatalogSeed("META_INAUTHENTIC_BEHAVIOR", "허위 행동", "INAUTHENTIC_BEHAVIOR", "https://transparency.meta.com/policies/community-standards/inauthentic-behavior/"),
    PolicyCatalogSeed("META_MEMORIALIZATION", "기념 계정", "MEMORIALIZATION", "https://transparency.meta.com/policies/community-standards/memorialization/"),
    PolicyCatalogSeed("META_MISINFORMATION", "허위 정보", "MISINFORMATION", "https://transparency.meta.com/policies/community-standards/misinformation/"),
    PolicyCatalogSeed("META_SPAM", "스팸", "SPAM", "https://transparency.meta.com/policies/community-standards/spam/"),
    PolicyCatalogSeed("META_THIRD_PARTY_IP", "제3자 지식재산권 침해", "THIRD_PARTY_INTELLECTUAL_PROPERTY", "https://transparency.meta.com/policies/community-standards/intellectual-property/"),
    PolicyCatalogSeed("META_IP_LICENSE", "Meta 지식재산권 및 라이선스 사용", "META_INTELLECTUAL_PROPERTY", "https://transparency.meta.com/policies/community-standards/meta-intellectual-property/"),
    PolicyCatalogSeed("META_MINORS", "미성년자 추가 보호", "MINOR_PROTECTION", "https://transparency.meta.com/policies/community-standards/additional-protection-minors/"),
    PolicyCatalogSeed("META_LOCAL_ILLEGAL_CONTENT", "특정 지역 내 불법 콘텐츠, 제품 또는 서비스", "LOCALLY_ILLEGAL_PRODUCTS_SERVICES", "https://transparency.meta.com/policies/community-standards/locally-illegal-products-services/"),
    PolicyCatalogSeed("META_USER_REQUESTS", "사용자 요청", "USER_REQUESTS", "https://transparency.meta.com/policies/community-standards/user-requests/"),
)
