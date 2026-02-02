from pydantic import BaseModel, Field
from typing import List, Literal

class CounselingResponse(BaseModel):
    """상담 응답 구조"""
    
    답변: str = Field(
        description="학생에게 전달할 공감적이고 따뜻한 답변"
    )
    
    정서적_고통: Literal["낮음", "중간", "높음"] = Field(
        description="학생의 현재 정서적 고통 수준"
    )
    
    자살_신호: Literal["낮음", "중간", "높음"] = Field(
        description="자살 위기 신호 수준"
    )
    
    감지된_위험요인: List[str] = Field(
        default_factory=list,
        description="대화에서 감지된 위험 요인 목록"
    )
    
    권장_대응: str = Field(
        description="교사/상담자가 취해야 할 다음 행동"
    )
    
    종료_판단: bool = Field(
        default=False,
        description="대화 종료 조건 충족 여부"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "답변": "많이 힘들었겠구나. 네 이야기를 듣고 싶어.",
                "정서적_고통": "높음",
                "자살_신호": "높음",
                "감지된_위험요인": ["구체적 자살 계획", "수단 준비"],
                "권장_대응": "즉시 개입 필요. 보호자 연락 및 전문기관 연계",
                "종료_판단": False
            }
        }