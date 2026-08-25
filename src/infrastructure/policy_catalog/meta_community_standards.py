from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class PolicyCatalogSeed:
    """Concise, review-oriented reference to a public platform policy."""

    policy_code: str
    title: str
    review_category: str
    source_url: str
    policy_summary: str
    detection_hints: tuple[str, ...]
    applicable_media_types: tuple[str, ...] = ("text", "image", "video")
    is_active: bool = True
    match_keywords: tuple[str, ...] = ()


_ALL = ("text", "image", "video")
_VISUAL = ("image", "video")


_META_COMMUNITY_STANDARDS: tuple[PolicyCatalogSeed, ...] = (
    PolicyCatalogSeed("META_COORDINATING_HARM", "가해 행위 도모 및 범죄 조장", "COORDINATING_HARM_CRIME", "https://transparency.meta.com/policies/community-standards/coordinating-harm-publicizing-crime/", "타인에게 위해를 가하거나 범죄를 실행·조장하기 위한 계획, 협력, 공개를 검토합니다.", ("범죄 실행 방법·역할·장소를 구체적으로 조율하는지", "폭력·절도·사기 등 위해 행위를 함께 하자고 권유하는지"), _ALL),
    PolicyCatalogSeed("META_DANGEROUS_ORGANIZATIONS", "위험한 단체 및 개인", "DANGEROUS_INDIVIDUALS_ORGANIZATIONS", "https://transparency.meta.com/policies/community-standards/dangerous-individuals-organizations/", "폭력적·범죄적 단체 또는 개인에 대한 지지, 찬양, 모집·지원 신호를 검토합니다.", ("위험 단체·인물의 폭력 행위를 찬양하거나 정당화하는지", "가입·모금·지원·선전을 유도하는지", "상징·구호가 지지 맥락으로 사용되는지"), _ALL),
    PolicyCatalogSeed("META_FRAUD_SCAMS", "사기, 스캠 및 기만적 행위", "FRAUD_SCAMS_DECEPTION", "https://transparency.meta.com/policies/community-standards/fraud-scams/", "금전·개인정보를 얻기 위한 허위 제안, 사칭, 비정상적 결제 유도를 검토합니다.", ("확인하기 어려운 수익·경품·투자 약속으로 결제를 유도하는지", "기관·타인·브랜드를 사칭하는지", "계좌·인증정보를 급하게 요구하는지"), _ALL),
    PolicyCatalogSeed("META_REGULATED_GOODS", "규제 상품 및 서비스", "REGULATED_GOODS", "https://transparency.meta.com/policies/community-standards/regulated-goods/", "무기, 약물, 주류·담배 등 규제 대상 상품·서비스의 판매·거래·홍보 맥락을 검토합니다.", ("규제 물품의 구매·판매·배송·교환을 직접 제안하는지", "연령·지역 제한이 있는 상품을 홍보하는지"), _ALL),
    PolicyCatalogSeed("META_VIOLENCE_INCITEMENT", "폭력 및 선동", "VIOLENCE_INCITEMENT", "https://transparency.meta.com/policies/community-standards/violence-incitement/", "특정 대상에 대한 위협, 폭력의 촉구·정당화, 폭력적 행동 유도를 검토합니다.", ("사람·집단을 향한 신체적 위해를 위협하는지", "폭력을 실행하자고 부추기거나 보상을 약속하는지", "폭력 행위를 정당화하는 표현이 있는지"), _ALL),
    PolicyCatalogSeed("META_ADULT_SEXUAL_EXPLOITATION", "성인 대상 성적 학대", "ADULT_SEXUAL_EXPLOITATION", "https://transparency.meta.com/policies/community-standards/sexual-exploitation-adults/", "동의 없는 성적 이미지·정보의 공유, 성적 협박·착취 정황을 검토합니다.", ("사적인 성적 이미지·정보를 공개하거나 유포하겠다고 위협하는지", "동의 여부가 불명확한 성적 콘텐츠를 거래·공유하는지"), _ALL),
    PolicyCatalogSeed("META_BULLYING_HARASSMENT", "따돌림 및 괴롭힘", "BULLYING_HARASSMENT", "https://transparency.meta.com/policies/community-standards/bullying-harassment/", "특정 개인을 겨냥한 모욕, 망신 주기, 반복적 공격·괴롭힘 신호를 검토합니다.", ("식별 가능한 개인을 조롱·비하·모욕하는지", "공격이나 집단 괴롭힘을 유도하는지", "신체·외모·사생활을 망신 주는 맥락인지"), _ALL),
    PolicyCatalogSeed("META_CHILD_SAFETY", "아동 대상 성적 학대, 학대 및 나체 이미지", "CHILD_SAFETY", "https://transparency.meta.com/policies/community-standards/child-sexual-exploitation-abuse-nudity/", "미성년자 대상 성적 대상화, 학대, 착취 또는 나체 이미지 가능성을 최우선 검토합니다.", ("미성년자로 보이는 인물이 성적 맥락·노출과 결합되는지", "아동 학대·착취를 묘사·조장·거래하는지", "연령 확인이 필요한 취약한 상황인지"), _ALL),
    PolicyCatalogSeed("META_HUMAN_EXPLOITATION", "인신 착취", "HUMAN_EXPLOITATION", "https://transparency.meta.com/policies/community-standards/human-exploitation/", "인신매매, 강제 노동·성착취, 사람의 이동·거래를 조장하는 신호를 검토합니다.", ("사람을 모집·이동·통제·거래하는 제안이 있는지", "강요·감금·착취가 암시되는지"), _ALL),
    PolicyCatalogSeed("META_SUICIDE_SELF_INJURY", "자살, 자해, 섭식 장애", "SUICIDE_SELF_INJURY", "https://transparency.meta.com/policies/community-standards/suicide-self-injury/", "자살·자해·섭식장애의 조장, 방법 공유, 위험 신호를 민감하게 검토합니다.", ("자해·자살을 권유·미화·경쟁처럼 표현하는지", "실행 방법이나 수단을 안내하는지", "섭식장애 행동을 조장하거나 찬양하는지"), _ALL),
    PolicyCatalogSeed("META_ADULT_NUDITY", "성인 나체 이미지 및 성적 행위", "ADULT_NUDITY_SEXUAL_ACTIVITY", "https://transparency.meta.com/policies/community-standards/adult-nudity-sexual-activity/", "성인 나체 또는 노골적 성적 행위의 시각적·설명적 노출 가능성을 검토합니다.", ("성인 신체의 민감 부위 노출이 핵심 장면인지", "노골적 성적 행위·연출이 포함되는지"), _VISUAL),
    PolicyCatalogSeed("META_SEXUAL_SOLICITATION", "성인 성매매 알선 및 성적으로 노골적인 표현", "SEXUAL_SOLICITATION", "https://transparency.meta.com/policies/community-standards/sexual-solicitation/", "성적 서비스의 구매·판매·알선 또는 노골적 성적 제안·요청을 검토합니다.", ("대가를 전제로 성적 만남·서비스를 제안하는지", "노골적 성적 행위·접촉을 요청하거나 협상하는지"), _ALL),
    PolicyCatalogSeed("META_HATE_SPEECH", "혐오 행동", "HATE_DISCRIMINATION_CULTURE", "https://transparency.meta.com/policies/community-standards/hate-speech/", "보호 특성을 이유로 개인·집단을 공격, 배제, 비인간화하는 표현을 검토합니다.", ("인종·국적·종교·성별 등 정체성을 근거로 비하하는지", "특정 집단에 대한 배제·폭력·차별을 촉구하는지", "고정관념을 공격적으로 일반화하는지"), _ALL),
    PolicyCatalogSeed("META_PRIVACY", "개인정보처리방침 위반", "PERSONAL_DATA", "https://transparency.meta.com/policies/community-standards/privacy-violations-image-privacy-rights/", "개인 식별·연락·위치 정보와 사적 이미지의 무단 노출 가능성을 검토합니다.", ("전화번호·주소·계좌·신분증 등 식별정보가 보이는지", "타인의 사적 이미지·대화·위치를 동의 없이 공개하는지", "번호판·얼굴·문서가 식별 가능한지"), _ALL),
    PolicyCatalogSeed("META_VIOLENT_GRAPHIC_CONTENT", "폭력적이고 자극적인 내용", "VIOLENT_GRAPHIC_CONTENT", "https://transparency.meta.com/policies/community-standards/violent-graphic-content/", "심각한 부상, 사망, 신체 훼손 등 충격적 시각 묘사 가능성을 검토합니다.", ("피·상처·사체·신체 훼손이 선명하게 노출되는지", "충격을 주기 위해 잔혹한 장면을 강조하는지"), _VISUAL),
    PolicyCatalogSeed("META_ACCOUNT_INTEGRITY", "계정 무결성", "ACCOUNT_INTEGRITY", "https://transparency.meta.com/policies/community-standards/account-integrity/", "계정의 매매·대여·탈취 또는 플랫폼 보호장치 우회 제안을 검토합니다.", ("계정·인증수단의 구매·판매·대여를 제안하는지", "정지·인증·보안 절차 우회를 안내하는지"), _ALL),
    PolicyCatalogSeed("META_AUTHENTIC_IDENTITY", "실제 신원 표현", "AUTHENTIC_IDENTITY", "https://transparency.meta.com/policies/community-standards/authentic-identity-representation/", "타인을 사칭하거나 실제 신원을 오인시키는 표현·이미지·프로필 맥락을 검토합니다.", ("타인·기관·브랜드인 것처럼 자신을 표현하는지", "합성·편집된 신원 표현이 실제인 것처럼 제시되는지"), _ALL),
    PolicyCatalogSeed("META_CYBERSECURITY", "사이버 보안", "CYBERSECURITY", "https://transparency.meta.com/policies/community-standards/cybersecurity/", "무단 접근, 계정 탈취, 악성 도구·코드, 개인정보 탈취를 돕는 내용을 검토합니다.", ("타인의 계정·시스템에 무단 접근하도록 안내하는지", "인증정보 탈취·악성코드·피싱을 조장하는지"), _ALL),
    PolicyCatalogSeed("META_INAUTHENTIC_BEHAVIOR", "허위 행동", "INAUTHENTIC_BEHAVIOR", "https://transparency.meta.com/policies/community-standards/inauthentic-behavior/", "가짜 계정·조작된 참여·조직적 기만으로 여론이나 지표를 왜곡하는 신호를 검토합니다.", ("가짜 계정·리뷰·팔로워를 만들거나 구매하도록 제안하는지", "조직적으로 반응·투표·도달을 조작하는지"), _ALL),
    PolicyCatalogSeed("META_MEMORIALIZATION", "기념 계정", "MEMORIALIZATION", "https://transparency.meta.com/policies/community-standards/memorialization/", "사망자의 계정·기억을 사칭, 악용 또는 부적절하게 상업화하는 맥락을 검토합니다.", ("사망자·추모 계정을 실제 운영자인 것처럼 사칭하는지", "애도 맥락을 조롱하거나 부당하게 이용하는지"), _ALL),
    PolicyCatalogSeed("META_MISINFORMATION", "허위 정보", "MISINFORMATION", "https://transparency.meta.com/policies/community-standards/misinformation/", "검증이 필요한 사실 주장, 특히 건강·안전·공적 사안의 오해 소지를 검토합니다.", ("출처 없는 사실·통계·의학·안전 주장을 단정하는지", "오해가 큰 공적 사건·선거·재난 정보를 확정적으로 전달하는지"), _ALL),
    PolicyCatalogSeed("META_SPAM", "스팸", "SPAM", "https://transparency.meta.com/policies/community-standards/spam/", "반복·대량 게시, 무관한 링크 유도, 비정상적 참여 유도 등 스팸 신호를 검토합니다.", ("반복 문구·링크·태그로 클릭을 유도하는지", "내용과 무관한 홍보·대량 게시를 제안하는지"), ("text", "image")),
    PolicyCatalogSeed("META_THIRD_PARTY_IP", "제3자 지식재산권 침해", "THIRD_PARTY_INTELLECTUAL_PROPERTY", "https://transparency.meta.com/policies/community-standards/intellectual-property/", "타인의 저작물·상표·콘텐츠를 권한 없이 복제·배포·판매하는 정황을 검토합니다.", ("제3자 콘텐츠를 무단 복제·재게시·판매한다고 명시하는지", "상표·저작권 귀속을 오인시키는지"), _ALL),
    PolicyCatalogSeed("META_IP_LICENSE", "Meta 지식재산권 및 라이선스 사용", "META_INTELLECTUAL_PROPERTY", "https://transparency.meta.com/policies/community-standards/meta-intellectual-property/", "Meta 상표·브랜드 자산·라이선스를 공식 관계처럼 오인시키는 사용을 검토합니다.", ("Meta 공식 승인·제휴를 근거 없이 주장하는지", "Meta 브랜드 자산을 오인 가능하게 사용하는지"), _ALL),
    PolicyCatalogSeed("META_MINORS", "미성년자 추가 보호", "MINOR_PROTECTION", "https://transparency.meta.com/policies/community-standards/additional-protection-minors/", "미성년자를 대상으로 한 부적절한 접촉·모집·상업적 이용 및 연령 보호 필요성을 검토합니다.", ("미성년자에게 사적 연락·만남·거래를 유도하는지", "미성년자의 신원·사생활·취약성을 이용하는지"), _ALL),
    PolicyCatalogSeed("META_LOCAL_ILLEGAL_CONTENT", "특정 지역 내 불법 콘텐츠, 제품 또는 서비스", "LOCALLY_ILLEGAL_PRODUCTS_SERVICES", "https://transparency.meta.com/policies/community-standards/locally-illegal-products-services/", "지역 법령에 따라 제한될 수 있는 제품·서비스·행위의 판매·홍보·제공 맥락을 검토합니다.", ("특정 국가·지역에서 불법·제한될 수 있는 거래를 권유하는지", "지역별 허가·연령·신고 요건을 무시하도록 유도하는지"), _ALL),
    PolicyCatalogSeed("META_USER_REQUESTS", "사용자 요청", "USER_REQUESTS", "https://transparency.meta.com/policies/community-standards/user-requests/", "사용자 신고·삭제 요청을 다루는 운영 정책으로, 일반 콘텐츠 자동 검수 근거로는 사용하지 않습니다.", ("일반 콘텐츠 분석에서는 자동 후보를 생성하지 않음",), (), False),
)


_MATCH_KEYWORDS: dict[str, tuple[str, ...]] = {
    "META_COORDINATING_HARM": ("범죄", "테러", "공격 계획", "범행", "공모", "위해"),
    "META_DANGEROUS_ORGANIZATIONS": ("테러 단체", "범죄 조직", "극단주의", "가입", "모금", "찬양"),
    "META_FRAUD_SCAMS": ("사기", "스캠", "피싱", "투자 수익", "경품", "송금", "사칭"),
    "META_REGULATED_GOODS": ("무기", "마약", "약물", "담배", "전자담배", "주류", "총기", "도박"),
    "META_VIOLENCE_INCITEMENT": ("폭력", "살해", "공격", "위협", "선동", "해치다", "죽이다"),
    "META_ADULT_SEXUAL_EXPLOITATION": ("성착취", "성적 협박", "불법 촬영", "리벤지 포르노", "동의 없는 유포"),
    "META_BULLYING_HARASSMENT": ("괴롭힘", "따돌림", "조롱", "모욕", "망신", "집단 공격"),
    "META_CHILD_SAFETY": ("아동 성착취", "미성년자 나체", "아동 학대", "그루밍", "아동 성적 대상화"),
    "META_HUMAN_EXPLOITATION": ("인신매매", "강제 노동", "감금", "착취", "노예", "사람 거래"),
    "META_SUICIDE_SELF_INJURY": ("자살", "자해", "극단적 선택", "섭식 장애", "거식", "폭식"),
    "META_ADULT_NUDITY": ("나체", "누드", "성행위", "민감 부위", "노골적 성적 장면"),
    "META_SEXUAL_SOLICITATION": ("성매매", "조건 만남", "성적 서비스", "성적 제안", "성적 알선"),
    "META_HATE_SPEECH": ("혐오", "차별", "비하", "인종", "국적", "종교", "성별", "장애", "성적 지향"),
    "META_PRIVACY": ("개인정보", "전화번호", "주소", "계좌", "신분증", "번호판", "사생활", "위치 정보"),
    "META_VIOLENT_GRAPHIC_CONTENT": ("유혈", "사체", "시신", "신체 훼손", "잔혹", "심각한 부상"),
    "META_ACCOUNT_INTEGRITY": ("계정 판매", "계정 대여", "계정 탈취", "인증 우회", "정지 우회"),
    "META_AUTHENTIC_IDENTITY": ("사칭", "가짜 신원", "신분 도용", "공식 계정", "딥페이크"),
    "META_CYBERSECURITY": ("해킹", "악성코드", "피싱", "계정 탈취", "디도스", "무단 접근"),
    "META_INAUTHENTIC_BEHAVIOR": ("가짜 계정", "가짜 리뷰", "팔로워 구매", "좋아요 조작", "여론 조작"),
    "META_MEMORIALIZATION": ("추모 계정", "기념 계정", "사망자 계정", "고인 사칭"),
    "META_MISINFORMATION": ("허위 정보", "가짜 뉴스", "오보", "조작 정보", "사실 확인", "미확인 주장"),
    "META_SPAM": ("스팸", "도배", "대량 게시", "반복 링크", "클릭 유도"),
    "META_THIRD_PARTY_IP": ("저작권", "상표권", "무단 복제", "불법 공유", "재업로드"),
    "META_IP_LICENSE": ("Meta 공식", "메타 공식", "Facebook 공식", "Instagram 공식", "브랜드 사칭"),
    "META_MINORS": ("미성년자", "아동", "청소년", "그루밍", "미성년자 만남", "미성년자 개인정보"),
    "META_LOCAL_ILLEGAL_CONTENT": ("불법 상품", "불법 서비스", "무허가", "연령 제한", "지역 제한"),
    "META_USER_REQUESTS": (),
}


META_COMMUNITY_STANDARDS: tuple[PolicyCatalogSeed, ...] = tuple(
    replace(entry, match_keywords=_MATCH_KEYWORDS[entry.policy_code])
    for entry in _META_COMMUNITY_STANDARDS
)
