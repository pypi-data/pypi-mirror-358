# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import datetime
from typing import List, Union, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["NoteCreateParams", "NoteType", "PatientInfo"]


class NoteCreateParams(TypedDict, total=False):
    date: Required[Annotated[Union[str, datetime.date], PropertyInfo(format="iso8601")]]
    """Date of the patient encounter"""

    transcript: Required[str]
    """The raw medical transcript text to be processed into a clinical note"""

    context: Optional[str]
    """Additional context for note generation. This field is optional."""

    instructions: Optional[List[str]]
    """Special instructions for note generation. This field is optional."""

    language: Literal["en", "es", "fr", "de", "it", "pt", "ru", "zh"]
    """Language code for the transcript content.

    While multiple languages are supported, English ('en') is recommended for
    optimal output quality and accuracy.
    """

    medication_list: Annotated[str, PropertyInfo(alias="medicationList")]
    """
    List of up to 50 medications (comma separated) to use as reference for fixing
    spelling errors. This field is optional.
    """

    note_type: Annotated[NoteType, PropertyInfo(alias="noteType")]
    """Configuration object specifying the style and format of the generated note"""

    patient_info: Annotated[PatientInfo, PropertyInfo(alias="patientInfo")]
    """Optional patient information"""

    previous_note: Annotated[str, PropertyInfo(alias="previousNote")]
    """Reference to a previous note if this is a follow-up. This field is optional."""


class NoteType(TypedDict, total=False):
    description: str
    """A brief overview of the note."""

    include_json: Annotated[bool, PropertyInfo(alias="includeJson")]
    """Determines whether to include a JSON payload in the custom note output.

    This option is applicable only for custom notes and defaults to `false`.
    Enabling this will increase latency and payload size.
    """

    template: Union[str, object]
    """Custom template to generate the note.

    This is applicable only when `type` is set to `note_style` or `note_template`.

    - When `type` is `note_style`, this is a note style string
    - When `type` is `note_template`, this is a
      [Note Template](/api-reference/schemas/note-template) payload
    """

    type: Literal["soap", "note_style", "note_template"]
    """Determines the type of note to generate.

    - Use `note_style` to provide a note style string
    - Use `note_template` to provide a
      [Note Template](/api-reference/schemas/note-template) payload
    - Use `soap` for the default SOAP template
    """


class PatientInfo(TypedDict, total=False):
    date_of_birth: Annotated[Union[str, datetime.date], PropertyInfo(alias="dateOfBirth", format="iso8601")]
    """Patient's date of birth in ISO-8601 format (YYYY-MM-DD)"""

    gender: Literal["male", "female", "other", "prefer not to say", "unspecified"]
    """Patient's gender identity"""

    name: str
    """Patient's full name"""
