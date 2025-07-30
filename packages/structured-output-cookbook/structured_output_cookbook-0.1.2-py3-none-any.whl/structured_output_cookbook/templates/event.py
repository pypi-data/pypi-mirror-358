"""Event extraction schema."""

from pydantic import Field

from ..schemas.base import BaseSchema


class EventSchema(BaseSchema):
    """Extract structured information from event descriptions."""

    # Basic event information
    title: str = Field(description="Event title or name")
    description: str | None = Field(description="Event description or summary")
    event_type: str | None = Field(
        description="Type of event: conference, workshop, party, meeting, etc.",
    )
    category: str | None = Field(
        description="Category: business, social, educational, cultural, etc.",
    )

    # Date and time
    start_date: str | None = Field(description="Start date of the event")
    end_date: str | None = Field(description="End date of the event")
    start_time: str | None = Field(description="Start time")
    end_time: str | None = Field(description="End time")
    duration: str | None = Field(description="Duration of the event")
    timezone: str | None = Field(description="Timezone if specified")

    # Location information
    venue_name: str | None = Field(description="Name of the venue")
    address: str | None = Field(description="Full address of the event")
    city: str | None = Field(description="City where event takes place")
    state_province: str | None = Field(description="State or province")
    country: str | None = Field(description="Country")
    is_virtual: bool | None = Field(
        description="Whether the event is virtual/online",
    )
    virtual_platform: str | None = Field(
        description="Platform for virtual events",
    )

    # Organizer information
    organizer_name: str | None = Field(
        description="Name of the organizing person or entity",
    )
    organizer_contact: str | None = Field(
        description="Contact information for organizer",
    )
    organizing_company: str | None = Field(
        description="Company organizing the event",
    )

    # Attendance information
    capacity: int | None = Field(description="Maximum number of attendees")
    expected_attendance: int | None = Field(
        description="Expected number of attendees",
    )
    target_audience: list[str] = Field(description="Target audience or demographics")

    # Registration and costs
    registration_required: bool | None = Field(
        description="Whether registration is required",
    )
    registration_deadline: str | None = Field(description="Registration deadline")
    registration_link: str | None = Field(description="URL for registration")
    cost: str | None = Field(description="Cost or price to attend")
    is_free: bool | None = Field(description="Whether the event is free")

    # Content and speakers
    agenda_topics: list[str] = Field(description="Main topics or agenda items")
    speakers: list[str] = Field(description="Names of speakers or presenters")
    keynote_speakers: list[str] = Field(description="Keynote speakers if specified")

    # Additional details
    dress_code: str | None = Field(description="Dress code if specified")
    language: str | None = Field(description="Primary language of the event")
    accessibility_info: str | None = Field(
        description="Accessibility information",
    )
    parking_info: str | None = Field(description="Parking information")
    food_provided: bool | None = Field(
        description="Whether food/refreshments are provided",
    )

    # Contact and links
    website: str | None = Field(description="Event website")
    social_media: list[str] = Field(description="Social media links or hashtags")
    contact_email: str | None = Field(description="Contact email for inquiries")
    contact_phone: str | None = Field(description="Contact phone number")

    # Tags and categorization
    tags: list[str] = Field(description="Tags or keywords associated with the event")
    industries: list[str] = Field(
        description="Industries or sectors relevant to the event",
    )

    @classmethod
    def get_extraction_prompt(cls) -> str:
        return """
        Extract structured information from the following event description or announcement.
        Focus on identifying:
        - Event title, type, and description
        - Date, time, and location details (including virtual platform if applicable)
        - Organizer and contact information
        - Registration requirements and costs
        - Speakers, agenda topics, and target audience
        - Additional logistics like dress code, parking, accessibility
        - Websites, social media, and contact details
        
        If information is not explicitly mentioned, leave the field empty or null.
        For date/time fields, preserve the original format when possible.
        Extract all relevant items for list fields.
        """.strip()
