from __future__ import annotations

from pydantic import BaseModel, Field

import opportunity_agent.prompts.prompts as prompts
from opportunity_agent.llm.client import LLMClient
from opportunity_agent.matcher.base import BaseMatcher
from opportunity_agent.models.candidate import CandidateProfile
from opportunity_agent.models.job import JobPosting
from opportunity_agent.models.match import MatchResult


class MatchEvaluationSchema(BaseModel):
    """
    Intermediate Pydantic schema for LLM structured output matching MatchResult.
    """

    overall_score: float = Field(description="Overall match score from 0.0 to 100.0.")
    skill_score: float = Field(
        description="Technical and skill score from 0.0 to 100.0."
    )
    education_score: float = Field(
        description="Education alignment score from 0.0 to 100.0."
    )
    experience_score: float = Field(
        description="Work experience relevance score from 0.0 to 100.0."
    )
    research_score: float = Field(
        description="Research domain fit score from 0.0 to 100.0."
    )
    publication_score: float = Field(
        description="Publication and academic record score from 0.0 to 100.0."
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="Key candidate strengths relevant to this job.",
    )
    missing_requirements: list[str] = Field(
        default_factory=list,
        description="Explicit gaps or missing skills required by the job.",
    )
    reasoning: str = Field(
        description="Detailed evaluation reasoning explaining if"
        "and why the user should apply."
    )


class LLMMatcher(BaseMatcher):
    """
    Matches candidate profile to job posting using an LLMClient.
    """

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def match(self, candidate, job):
        """
        Evaluates match fit by feeding combined Candidate and Job JSON to the LLM.
        """
        combined_payload = self._build_evaluation_text(candidate, job)

        try:
            raw_dict = self.llm.generate_json(
                prompt=prompts.MATCH_EVALUATION_PROMPT,
                text=combined_payload,
                response_schema=MatchEvaluationSchema,
            )

            eval_res = MatchEvaluationSchema(**raw_dict)

            return MatchResult(
                job=job,
                overall_score=eval_res.overall_score,
                skill_score=eval_res.skill_score,
                education_score=eval_res.education_score,
                experience_score=eval_res.experience_score,
                research_score=eval_res.research_score,
                publication_score=eval_res.publication_score,
                strengths=eval_res.strengths,
                missing_requirements=eval_res.missing_requirements,
                reasoning=eval_res.reasoning,
            )
        except Exception as e:
            return MatchResult(
                job=job,
                overall_score=0.0,
                skill_score=0.0,
                education_score=0.0,
                experience_score=0.0,
                research_score=0.0,
                publication_score=0.0,
                strengths=[],
                missing_requirements=["Unable to complete automated evaluation"],
                reasoning=f"Evaluation failed due to error: {e}",
            )

    def _build_evaluation_text(
        self, candidate: CandidateProfile, job: JobPosting
    ) -> str:
        """
        Helper to format candidate profile and job posting into structured input text.
        """
        candidate_json = candidate.model_dump_json(indent=2, exclude_none=True)
        job_json = job.model_dump_json(indent=2, exclude_none=True)

        return (
            f"=== CANDIDATE PROFILE ===\n"
            f"{candidate_json}\n\n"
            f"=== JOB POSTING ===\n"
            f"{job_json}"
        )
