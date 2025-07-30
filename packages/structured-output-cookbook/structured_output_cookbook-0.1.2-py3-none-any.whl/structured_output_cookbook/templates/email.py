"""Email extraction schema."""

from pydantic import Field

from ..schemas.base import BaseSchema


class EmailSchema(BaseSchema):
    """Extract structured information from emails."""

    # Email metadata
    subject: str | None = Field(description="Email subject line")
    sender_name: str | None = Field(description="Name of the sender")
    sender_email: str | None = Field(description="Email address of the sender")
    recipient_names: list[str] = Field(description="Names of recipients")
    recipient_emails: list[str] = Field(description="Email addresses of recipients")
    cc_emails: list[str] = Field(description="CC email addresses")
    bcc_emails: list[str] = Field(description="BCC email addresses if visible")

    # Email classification
    email_type: str | None = Field(
        description="Type of email: business, personal, marketing, support, etc.",
    )
    priority: str | None = Field(description="Priority level: high, medium, low")
    category: str | None = Field(
        description="Category: inquiry, complaint, order, meeting, etc.",
    )

    # Content analysis
    main_topic: str | None = Field(description="Main topic or subject matter")
    summary: str | None = Field(description="Brief summary of the email content")
    key_points: list[str] = Field(description="Key points or important information")
    action_items: list[str] = Field(description="Action items or tasks mentioned")

    # Requests and responses
    questions_asked: list[str] = Field(description="Questions asked in the email")
    requests_made: list[str] = Field(description="Specific requests made")
    deadlines_mentioned: list[str] = Field(description="Deadlines or dates mentioned")

    # Contact information
    phone_numbers: list[str] = Field(description="Phone numbers mentioned")
    addresses: list[str] = Field(description="Physical addresses mentioned")
    websites_urls: list[str] = Field(description="Websites or URLs mentioned")

    # Business context
    company_names: list[str] = Field(description="Company names mentioned")
    product_services: list[str] = Field(description="Products or services mentioned")
    amounts_prices: list[str] = Field(
        description="Monetary amounts or prices mentioned",
    )

    # Sentiment and tone
    sentiment: str | None = Field(
        description="Overall sentiment: positive, negative, neutral",
    )
    tone: str | None = Field(
        description="Tone: formal, informal, urgent, friendly, etc.",
    )

    # Response requirements
    requires_response: bool | None = Field(
        description="Whether the email requires a response",
    )
    response_urgency: str | None = Field(description="Urgency of response needed")
    suggested_response_points: list[str] = Field(
        description="Key points to address in response",
    )

    @classmethod
    def get_extraction_prompt(cls) -> str:
        return """
        Extract structured information from the following email.
        Focus on identifying:
        - Email metadata (sender, recipients, subject)
        - Email classification and priority
        - Main content, key points, and action items
        - Questions, requests, and deadlines
        - Contact information and business context
        - Sentiment, tone, and response requirements
        
        If information is not present, leave fields empty or null.
        Extract all relevant items for list fields.
        Be careful to distinguish between actual content and email signatures.
        """.strip()
