"""
PromptBuilder 서비스

다양한 목적의 LLM 프롬프트를 동적으로 생성하는 메인 서비스입니다.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from .models import (
    PromptInput, PromptResult, PromptType, PromptMetadata,
    CustomizationOptions
)
from .exceptions import (
    PromptBuilderException, InvalidPromptTypeException,
    TemplateNotFoundException
)

logger = logging.getLogger(__name__)


class PromptBuilderService:
    """프롬프트 빌더 서비스"""
    
    def __init__(self):
        self.templates = self._load_templates()
        logger.info("PromptBuilderService initialized")
    
    def _load_templates(self) -> Dict[str, str]:
        """프롬프트 템플릿 로드"""
        return {
            "daily_summary": """
🔍 {developer_name}님의 {date} 개발 활동 요약

📊 전체 통계:
- 커밋 수: {commit_count}개
- 변경 파일: {files_changed}개
- 추가된 라인: {lines_added}줄
- 삭제된 라인: {lines_deleted}줄

🚀 주요 작업 내용:
{main_activities}

📈 코드 품질:
- 평균 복잡도: {avg_complexity}
- 사용 언어: {languages_used}

⏰ 작업 패턴:
- 피크 시간: {peak_hours}
            """.strip(),
            
            "code_review": """
📋 {developer_name}님의 코드 리뷰 요약

🔍 변경사항 분석:
{code_changes}

✅ 개선사항:
{improvements}
            """.strip()
        }
    
    async def build_prompt(self, input_data: PromptInput) -> PromptResult:
        """프롬프트 생성 메인 메서드"""
        try:
            template = self._select_template(input_data.prompt_type)
            context_data = self._build_context(input_data)
            rendered_prompt = self._render_template(template, context_data)
            optimized_prompt = self._optimize_token_usage(rendered_prompt)
            
            metadata = PromptMetadata(
                template_version="1.0",
                token_count=self._estimate_token_count(optimized_prompt),
                language="korean"
            )
            
            return PromptResult(
                prompt=optimized_prompt,
                metadata=metadata,
                context_data=context_data,
                template_used=input_data.prompt_type.value
            )
            
        except Exception as e:
            raise PromptBuilderException(f"Failed to build prompt: {str(e)}")
    
    def build_daily_summary_prompt(self, aggregated_data: Dict[str, Any], 
                                  target_developer: str) -> PromptResult:
        """일일 요약용 프롬프트 생성 (동기 버전)"""
        try:
            template = self._select_template(PromptType.DAILY_SUMMARY)
            
            # 컨텍스트 구성
            dev_stats = aggregated_data.get("developer_stats", {})
            target_stats = None
            
            # 대상 개발자 찾기
            for dev_email, stats in dev_stats.items():
                if stats.get("developer") == target_developer:
                    target_stats = stats
                    break
            
            if not target_stats:
                target_stats = {
                    "developer": target_developer,
                    "commit_count": 0,
                    "lines_added": 0,
                    "lines_deleted": 0,
                    "files_changed": 0,
                    "languages_used": [],
                    "avg_complexity": 0.0
                }
            
            context_data = {
                "developer_name": target_stats.get("developer", target_developer),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "commit_count": target_stats.get("commit_count", 0),
                "files_changed": target_stats.get("files_changed", 0),
                "lines_added": target_stats.get("lines_added", 0),
                "lines_deleted": target_stats.get("lines_deleted", 0),
                "avg_complexity": target_stats.get("avg_complexity", 0.0),
                "languages_used": ", ".join(target_stats.get("languages_used", [])),
                "main_activities": "주요 활동 내용이 여기에 표시됩니다.",
                "peak_hours": "오후 시간대"
            }
            
            rendered_prompt = self._render_template(template, context_data)
            optimized_prompt = self._optimize_token_usage(rendered_prompt)
            
            metadata = PromptMetadata(
                template_version="1.0",
                token_count=self._estimate_token_count(optimized_prompt),
                language="korean"
            )
            
            return PromptResult(
                prompt=optimized_prompt,
                metadata=metadata,
                context_data=context_data,
                template_used="daily_summary"
            )
            
        except Exception as e:
            raise PromptBuilderException(f"Failed to build daily summary prompt: {str(e)}")
    
    def _select_template(self, prompt_type: PromptType) -> str:
        """템플릿 선택"""
        template_name = prompt_type.value
        if template_name not in self.templates:
            raise TemplateNotFoundException(template_name)
        return self.templates[template_name]
    
    def _build_context(self, input_data: PromptInput) -> Dict[str, Any]:
        """컨텍스트 구성"""
        dev_stats = input_data.aggregated_data.get("developer_stats", {})
        target_stats = None
        
        # 대상 개발자 찾기
        for dev_email, stats in dev_stats.items():
            if stats.get("developer") == input_data.target_developer:
                target_stats = stats
                break
        
        if not target_stats:
            target_stats = {
                "developer": input_data.target_developer,
                "commit_count": 0,
                "lines_added": 0,
                "lines_deleted": 0,
                "files_changed": 0,
                "languages_used": [],
                "avg_complexity": 0.0
            }
        
        return {
            "developer_name": target_stats.get("developer", input_data.target_developer),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "commit_count": target_stats.get("commit_count", 0),
            "files_changed": target_stats.get("files_changed", 0),
            "lines_added": target_stats.get("lines_added", 0),
            "lines_deleted": target_stats.get("lines_deleted", 0),
            "avg_complexity": target_stats.get("avg_complexity", 0.0),
            "languages_used": ", ".join(target_stats.get("languages_used", [])),
            "main_activities": "주요 활동 내용이 여기에 표시됩니다.",
            "peak_hours": "오후 시간대",
            "code_changes": "코드 변경사항 분석",
            "improvements": "개선사항 목록"
        }
    
    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        """템플릿 렌더링"""
        try:
            return template.format(**context)
        except KeyError as e:
            raise PromptBuilderException(f"Missing template variable: {e}")
    
    def _optimize_token_usage(self, prompt: str) -> str:
        """토큰 최적화"""
        if len(prompt) > 2000:  # 간단한 길이 제한
            return prompt[:2000] + "\n\n(내용이 축약되었습니다)"
        return prompt
    
    def _estimate_token_count(self, text: str) -> int:
        """토큰 수 추정"""
        return int(len(text.split()) * 1.3) 