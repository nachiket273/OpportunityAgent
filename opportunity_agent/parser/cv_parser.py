from __future__ import annotations

import json

from pydantic import ValidationError

from opportunity_agent.llm.client import LLMClient
from opportunity_agent.models.candidate import CandidateProfile, ParsedResult
from opportunity_agent.prompts import prompts


class CVParser:

    def __init__(self, llm: LLMClient, max_retries: int = 3) -> None:
        self.llm = llm
        self.max_retries = max_retries

    def parse(self, cv_text: str) -> ParsedResult:
        """
        Parse the CV text using the LLM client.

        Args:
            cv_text (str): The text of the CV to be parsed.

        Returns:
            ParsedCV: The parsed CV data.
        """
        attempts = 0
        last_error = None
        raw_dict = None

        # Extraction loop with self correction and retries
        while attempts <= self.max_retries:
            try:
                if attempts == 0:
                    current_prompt = prompts.CV_PARSE_PROMPT
                else:
                    # If there was an error, we can modify the prompt to ask for
                    # clarification or correction
                    current_prompt = (
                        f"{prompts.CV_PARSE_PROMPT}"
                        f"\n\nCRITICAL: Your previous output failed validation"
                        f" with error:\n{last_error}\n"
                        f"Please fix the schema issues and re-extract accurately."
                    )

                # Use the LLM client to parse the CV text
                raw_dict = self.llm.generate_json(
                    prompt=current_prompt,
                    text=cv_text,
                    response_schema=CandidateProfile,
                )

                # Convert the JSON response to a CandidateProfile object
                candidate_profile = CandidateProfile(**raw_dict)

                break

            except (ValidationError, json.JSONDecodeError, ValueError) as e:
                last_error = str(e)
                attempts += 1

                if attempts > self.max_retries:
                    print(
                        f"CRITICAL: Failed to parse CV after {self.max_retries}"
                        f" attempts. Last error: {last_error}"
                    )
                    return ParsedResult(
                        profile=CandidateProfile(name="Unknown / Extraction Failed"),
                        warnings=[
                            f"CRITICAL: Failed to parse CV after {self.max_retries}"
                            f" attempts. Last error: {last_error}"
                        ],
                        is_successful=False,
                    )

        # Warning generation based on missing critical fields
        warnings = self._generate_warnings(candidate_profile, cv_text)

        # Return the parsed result
        return ParsedResult(
            profile=candidate_profile,
            warnings=warnings,
            is_successful=True,
        )

    def _generate_warnings(self, profile: CandidateProfile, raw_text: str) -> list[str]:
        """
        Combines deterministic business rules and semantic checks
        to populate warnings in ParseResult.
        """
        warnings: list[str] = []

        # --- Rule 1: Missing Contact Details ---
        if not profile.email:
            warnings.append("MISSING_DATA: No candidate email address detected.")
        if not profile.phone:
            warnings.append("MISSING_DATA: No candidate phone number detected.")

        # --- Rule 2: Incomplete Work History ---
        if not profile.experience:
            warnings.append("INCOMPLETE_PROFILE: No work experience entries extracted.")
        else:
            for idx, exp in enumerate(profile.experience):
                if not exp.start_date:
                    warnings.append(
                        f"DATA_QUALITY: Experience block"
                        f"'{exp.title} at {exp.organization}'"
                        f"is missing a start date."
                    )

        # --- Rule 3: Missing Education ---
        if not profile.education:
            warnings.append("INCOMPLETE_PROFILE: No education history found.")

        # --- Rule 4: LLM Semantic Verification (Optional Agent Call) ---
        # The agent checks if high-level text context conflicts with extracted data
        if len(raw_text) > 500 and len(profile.technical_skills) == 0:
            warnings.append(
                "POTENTIAL_PARSING_GAP: Resume text contains substantial content, "
                "but 0 technical skills were extracted."
            )

        return warnings
