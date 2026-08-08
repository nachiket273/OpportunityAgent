from __future__ import annotations

import asyncio
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from opportunity_agent.config.settings import EmailConfig
from opportunity_agent.models.report import OpportunityReport


class EmailNotifier:
    """Handles sending email notifications with attached Excel opportunity reports."""

    def __init__(self, config: EmailConfig) -> None:
        self.config = config

    def send_report(
        self,
        report: OpportunityReport,
        excel_path: Path | str,
        top_n: int = 5,
    ) -> bool:
        """
        Builds and sends an email report with the Excel file attached.

        Args:
            report: The OpportunityReport instance.
            excel_path: Path to the generated Excel file.
            top_n: Number of top matches to highlight in the email body.

        Returns:
            bool: True if sent successfully, False otherwise.
        """
        if not self.config.enabled:
            return False

        path = Path(excel_path)
        if not path.exists():
            return False

        try:
            msg = self._build_email_message(report, path, top_n)
            self._send_via_smtp(msg)
            return True

        except Exception:
            return False

    def _build_email_message(
        self,
        report: OpportunityReport,
        excel_path: Path,
        top_n: int,
    ) -> MIMEMultipart:
        """Constructs the MIME email message with HTML body and Excel attachment."""
        msg = MIMEMultipart()
        msg["From"] = self.config.sender_email or self.config.username
        msg["To"] = self.config.recipient_email
        msg["Subject"] = (
            f"Opportunity Agent Report - {len(report.results)} Matches Found"
        )

        # Build email body summary
        total_found = len(report.results)
        top_matches = report.results[:top_n]

        body_lines = [
            f"Hello {report.candidate.name or 'there'},\n",
            f"Found {total_found} opportunity "
            f"{'match' if total_found == 1 else 'matches'} for your profile.\n",
        ]

        if top_matches:
            body_lines.append(f"Top {len(top_matches)} Opportunities:")
            for idx, match in enumerate(top_matches, start=1):
                org = match.job.organization or "Unknown Org"
                title = match.job.title or "Unknown Role"
                score = round(match.overall_score)
                body_lines.append(f"{idx}. {org} - {title} ({score}%)")

        body_lines.append(
            "\nSee attached spreadsheet for complete details and application links."
        )
        body_lines.append("\nBest regards,\nOpportunity Agent")

        body_text = "\n".join(body_lines)
        msg.attach(MIMEText(body_text, "plain", "utf-8"))

        # Attach Excel File
        with excel_path.open("rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="xlsx")
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=excel_path.name,
            )
            msg.attach(attachment)

        return msg

    def _send_via_smtp(self, msg: MIMEMultipart) -> None:
        """Sends MIME message using configured SMTP server and TLS authentication."""
        with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
            server.starttls()
            if self.config.username and self.config.password:
                server.login(self.config.username, self.config.password)
            server.send_message(msg)

    async def send_report_async(
        self,
        report: OpportunityReport,
        excel_path: Path | str,
        top_n: int = 5,
    ) -> bool:
        """Asynchronously executes send_report in a thread pool executor."""
        return await asyncio.to_thread(self.send_report, report, excel_path, top_n)
