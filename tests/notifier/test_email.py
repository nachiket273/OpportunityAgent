from __future__ import annotations

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from opportunity_agent.config.settings import EmailConfig
from opportunity_agent.models.candidate import CandidateProfile
from opportunity_agent.models.job import JobPosting
from opportunity_agent.models.match import MatchResult
from opportunity_agent.models.report import OpportunityReport
from opportunity_agent.notifier.email import EmailNotifier


@pytest.fixture
def sample_report() -> OpportunityReport:
    candidate = CandidateProfile(name="Alice Scientist")
    matches = [
        MatchResult(
            job=JobPosting(
                id="1", title="Postdoc", organization="ETH Zurich", url="http://a.com"
            ),
            overall_score=97.0,
            skill_score=97.0,
            education_score=97.0,
            experience_score=97.0,
            research_score=97.0,
            publication_score=97.0,
        ),
        MatchResult(
            job=JobPosting(
                id="2",
                title="Research Scientist",
                organization="EPFL",
                url="http://b.com",
            ),
            overall_score=95.0,
            skill_score=95.0,
            education_score=95.0,
            experience_score=95.0,
            research_score=95.0,
            publication_score=95.0,
        ),
    ]
    return OpportunityReport(
        candidate=candidate,
        results=matches,
        generated_at=datetime.now(),
    )


@pytest.fixture
def email_config() -> EmailConfig:
    return EmailConfig(
        enabled=True,
        smtp_server="smtp.test.com",
        smtp_port=587,
        username="user@test.com",
        password="password123",
        sender_email="user@test.com",
        recipient_email="candidate@test.com",
    )


def test_send_report_disabled(
    sample_report: OpportunityReport, email_config: EmailConfig, tmp_path: Path
) -> None:
    """Verify that email sending is skipped if enabled=False."""
    email_config.enabled = False
    notifier = EmailNotifier(config=email_config)

    fake_excel = tmp_path / "jobs.xlsx"
    fake_excel.write_text("dummy")

    result = notifier.send_report(sample_report, fake_excel)
    assert result is False


@patch("opportunity_agent.notifier.email.smtplib.SMTP")
def test_send_report_success(
    mock_smtp_class: MagicMock,
    sample_report: OpportunityReport,
    email_config: EmailConfig,
    tmp_path: Path,
) -> None:
    """Verify successful SMTP message construction and delivery."""
    mock_smtp_instance = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp_instance

    fake_excel = tmp_path / "jobs_2026_08_09.xlsx"
    fake_excel.write_bytes(b"PK\x03\x04 fake excel content")

    notifier = EmailNotifier(config=email_config)
    success = notifier.send_report(sample_report, fake_excel, top_n=2)

    assert success is True
    assert mock_smtp_instance.starttls.called
    assert mock_smtp_instance.login.called
    assert mock_smtp_instance.send_message.called

    # Inspect sent MIME message
    sent_msg = mock_smtp_instance.send_message.call_args[0][0]
    assert sent_msg["To"] == "candidate@test.com"
    assert "2 Matches Found" in sent_msg["Subject"]


@pytest.mark.asyncio
@patch("opportunity_agent.notifier.email.smtplib.SMTP")
async def test_send_report_async(
    mock_smtp_class: MagicMock,
    sample_report: OpportunityReport,
    email_config: EmailConfig,
    tmp_path: Path,
) -> None:
    """Verify asynchronous wrapper execution."""
    mock_smtp_instance = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp_instance

    fake_excel = tmp_path / "jobs.xlsx"
    fake_excel.write_bytes(b"fake data")

    notifier = EmailNotifier(config=email_config)
    success = await notifier.send_report_async(sample_report, fake_excel)

    assert success is True
