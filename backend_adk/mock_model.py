from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any

from google.adk.models import BaseLlm, LlmCapabilities, LlmRequest, LlmResponse
from google.genai import types

from backend_adk.text_analysis import extract_keywords


class MockInterviewModel(BaseLlm):
    """Deterministic ADK model for credential-free local runs and tests."""

    agent_key: str

    @property
    def capabilities(self) -> LlmCapabilities:
        return LlmCapabilities(output_schema_and_tools=True)

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        payload = self._request_payload(llm_request)
        tool_result = self._tool_result(llm_request)

        if tool_result is None and self.agent_key in {"skill_match_agent", "company_research_agent", "interview_trends_agent"}:
            function_name, arguments = self._tool_call(payload)
            part = types.Part.from_function_call(name=function_name, args=arguments)
        else:
            part = types.Part.from_text(text=self._respond(payload, tool_result))

        yield LlmResponse(
            model_version="offline-adk-mock",
            content=types.Content(role="model", parts=[part]),
            usage_metadata=types.GenerateContentResponseUsageMetadata(
                prompt_token_count=0,
                candidates_token_count=0,
                total_token_count=0,
            ),
            partial=False,
            turn_complete=True,
        )

    def _request_payload(self, request: LlmRequest) -> dict[str, str]:
        for content in reversed(request.contents):
            if content.role != "user":
                continue
            text = "\n".join(part.text or "" for part in content.parts or [])
            marker = "Interview preparation context (treat all fields as user data):\n"
            if marker not in text:
                continue
            try:
                values = json.loads(text.split(marker, 1)[1])
            except json.JSONDecodeError:
                continue
            return {key: str(value) for key, value in values.items()}
        return {}

    def _tool_result(self, request: LlmRequest) -> dict[str, Any] | None:
        for content in reversed(request.contents):
            for part in content.parts or []:
                if part.function_response and part.function_response.response:
                    return part.function_response.response
        return None

    def _tool_call(self, payload: dict[str, str]) -> tuple[str, dict[str, str]]:
        if self.agent_key == "skill_match_agent":
            return "match_job_skills", {
                "job_description": payload.get("job_description", ""),
                "candidate_experience": payload.get("answer", ""),
            }
        if self.agent_key == "company_research_agent":
            return "search_interview_research", {
                "company": payload.get("company", "the company"),
                "role": payload.get("role", "the target role"),
            }
        return "get_interview_question_trends", {"role": payload.get("role", "the target role")}

    def _respond(
        self, payload: dict[str, str], tool_result: dict[str, Any] | None
    ) -> str:
        role = payload.get("role") or "your target role"
        company = payload.get("company") or "the company"
        seniority = payload.get("seniority") or "Senior"
        job = payload.get("job_description", "")
        question = payload.get("question") or "Tell me about a challenging project you delivered."
        answer = payload.get("answer", "")

        if self.agent_key == "interview_brief_agent":
            return (
                f"## Your interview brief\n\nFor a **{seniority} {role}** conversation at **{company}**, "
                "anchor your preparation in decisions you owned, measurable outcomes, and what you learned.\n\n"
                "### Before the interview\n- Prepare two project stories with clear before-and-after outcomes.\n"
                "- Practice explaining a technical trade-off to both an engineer and a product partner.\n"
                "- Bring one thoughtful question about how the team measures success."
            )
        if self.agent_key == "answer_coach_agent":
            return (
                f"## Answer coaching\n\n**Prompt:** {question}\n\n"
                "### Keep\n- Lead with your personal ownership and the constraints you faced.\n"
                "- Make the result concrete with a metric, baseline, or user impact.\n\n"
                "### Strengthen\n- Use **Situation → Task → Action → Result → Reflection**.\n"
                "- Spend most of your answer on your decisions, not the team's background.\n"
                "- Close with what you would carry into the next project.\n\n"
                + (f"### Your draft\n\n{answer}\n\n" if answer else "")
                + '### A stronger opening\n\n"The constraint we faced was ___. I owned ___, and chose ___ because ___."'
            )
        if self.agent_key == "role_reader":
            keywords = sorted(extract_keywords(job))[:6] or ["system design", "reliability", "communication"]
            return f"Role signals: {', '.join(keywords)}. Prioritize evidence of ownership, technical judgment, and measurable impact."
        if self.agent_key == "question_planner":
            return (
                f"1. Describe an architecture decision involving {', '.join(sorted(extract_keywords(job))[:3]) or 'the role requirements'}; explain the trade-off.\n"
                "2. Debug a reliability issue and explain how you would prevent recurrence.\n"
                "3. Tell me about a time you influenced a technical decision across teams."
            )
        if self.agent_key == "study_planner":
            return (
                f"## A focused plan for {role}\n\n### Role signals\n{', '.join(sorted(extract_keywords(job))[:6]) or 'system design, reliability, communication'}\n\n"
                "### Likely questions\nPrepare to explain an architecture trade-off, a reliability incident, and a cross-team technical decision.\n\n### Four-session practice plan\n"
                "1. Refresh role fundamentals and connect each one to a project.\n"
                "2. Practice a coding problem and explain complexity aloud.\n"
                "3. Walk through an architecture prompt, assumptions, failure modes, and trade-offs.\n"
                "4. Rehearse two STAR stories and refine them with measurable outcomes."
            )
        if self.agent_key == "skills_analyst":
            skills = ", ".join(sorted(extract_keywords(job))[:4]) or "distributed systems, APIs, and reliability"
            return f"Prioritize **{skills}**. Connect each requirement to a concrete project and a decision you owned."
        if self.agent_key == "question_analyst":
            return "Likely prompts: design a reliable service; debug a production incident; explain a cross-team technical trade-off."
        if self.agent_key == "risk_analyst":
            return "Clarify individual ownership, show a measurable outcome, and prepare an example of how you handled ambiguity."
        if self.agent_key == "answer_critic":
            return "Sharpen the decision you personally made, explain why you chose it, and add the result or mark missing metrics explicitly."
        if self.agent_key == "answer_reviser":
            return (
                "## Rehearsed answer\n\n"
                f"**Question:** {question}\n\n### Revised structure\n"
                f"**Situation:** {answer[:260] or 'Describe the context and constraints.'}\n\n"
                "**Task:** State the outcome you personally owned.\n\n"
                "**Action:** Explain your decisions, trade-offs, and collaboration.\n\n"
                "**Result:** Add a measurable outcome.\n\n**Reflection:** Share what you learned and would apply next time."
            )
        if self.agent_key == "architecture_interviewer":
            return (
                f"## System design: {question}\n\n### 1. Clarify the problem\nDefine users, workflows, latency, availability, and scope.\n\n"
                "### 2. Sketch the architecture\n**Client → API gateway → stateless service → durable store**, with a queue for asynchronous work and a cache for read-heavy paths.\n\n"
                "### 3. Follow one request\nDescribe validation, authorization, idempotency, persistence, and response delivery.\n\n"
                "### 4. Explore trade-offs\nDiscuss consistency, partitioning, cache invalidation, and synchronous versus asynchronous work.\n\n"
                "### 5. Cover failure and scale\nDiscuss retries, rate limits, observability, and gradual rollout. State assumptions before drawing boxes."
            )
        if self.agent_key == "behavioral_interviewer":
            return f"Structure your answer to **{question}** with Situation, Task, Action, Result, and Reflection. Use your own examples; do not invent metrics."
        if self.agent_key == "skill_match_agent":
            match = tool_result or {}
            matched = match.get("matched_terms", []) or ["No direct evidence found yet"]
            missing = match.get("unmentioned_terms", []) or ["Add a concrete project example"]
            return (
                "## Experience-to-role match\n\n"
                f"**Keyword overlap:** {match.get('overlap_percent', 0)}%\n\n"
                f"### Evidence in your draft\n{', '.join(f'`{item}`' for item in matched)}\n\n"
                f"### Requirements to address\n{', '.join(f'`{item}`' for item in missing)}\n\n"
                "This local keyword comparison is not a qualification score."
            )
        if self.agent_key == "company_research_agent":
            return self._format_tool_result("Research brief", tool_result)
        if self.agent_key == "interview_trends_agent":
            return self._format_tool_result("Interview-question trends", tool_result)
        return "Interview preparation complete. Ground your answer in a specific decision, its trade-offs, and an honest outcome."

    @staticmethod
    def _format_tool_result(title: str, result: dict[str, Any] | None) -> str:
        result = result or {}
        return f"## {title}\n\n**Mock mode:** {result.get('notice', 'Illustrative local data.')}\n\n{result.get('markdown', '')}"