from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from pythonik.models.base import UserInfo, PaginatedResponse


class Point(BaseModel):
    x: Optional[int] = None
    y: Optional[int] = None


class Primitive(BaseModel):
    color: Optional[str] = ""
    points: List[Point] = []
    text: Optional[str] = ""
    type: Optional[str] = ""


class Drawing(BaseModel):
    primitives: List[Primitive] = []


class Word(BaseModel):
    end_ms: Optional[int] = None
    score: Optional[int] = None
    start_ms: Optional[int] = None
    value: Optional[str] = ""


class Transcription(BaseModel):
    speaker: Optional[int] = None
    words: List[Word] = []


class SegmentBody(BaseModel):
    drawing: Optional[Drawing] = None
    external_id: Optional[str] = ""
    keyframe_id: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = None
    metadata_view_id: Optional[str] = ""
    parent_id: Optional[str] = ""
    path: Optional[str] = ""
    segment_checked: Optional[bool] = None
    segment_color: Optional[str] = ""
    segment_text: Optional[str] = ""
    segment_track: Optional[str] = ""
    segment_type: Optional[str] = ""
    share_user_email: Optional[str] = ""
    status: Optional[str] = ""
    time_end_milliseconds: Optional[int] = None
    time_start_milliseconds: Optional[int] = None
    top_level: Optional[bool] = None
    transcription: Optional[Transcription] = None
    transcription_id: Optional[str] = ""
    user_id: Optional[str] = ""
    user_info: Optional[UserInfo] = None
    version_id: Optional[str] = ""


class FaceBoundingBox(BaseModel):
    bounding_box: Optional[List[int]] = []
    face_id: Optional[str] = ""
    timestamp_ms: Optional[int] = None


class SegmentResponse(SegmentBody):
    id: Optional[str] = ""


class SegmentDetailResponse(SegmentBody):
    """Detailed segment response with additional fields returned by get_segments endpoint."""

    id: Optional[str] = ""
    asset_id: Optional[str] = ""
    date_created: Optional[str] = ""
    date_modified: Optional[str] = ""
    external_id: Optional[str] = ""
    face_bounding_boxes: Optional[List[FaceBoundingBox]] = []
    has_drawing: Optional[bool] = None
    is_internal: Optional[bool] = None
    person_id: Optional[str] = ""
    project_id: Optional[str] = ""
    segment_checked: Optional[bool] = None
    segment_color: Optional[str] = ""
    segment_text: Optional[str] = ""
    segment_track: Optional[str] = ""
    segment_type: Optional[str] = ""
    share_id: Optional[str] = ""
    share_user_email: Optional[str] = ""
    status: Optional[str] = ""
    subclip_id: Optional[str] = ""
    time_end_milliseconds: Optional[int] = None
    time_start_milliseconds: Optional[int] = None
    top_level: Optional[bool] = None
    transcription: Optional[Transcription] = None
    transcription_id: Optional[str] = ""
    user_first_name: Optional[str] = ""
    user_id: Optional[str] = ""
    user_info: Optional[UserInfo] = None
    user_last_name: Optional[str] = ""
    user_photo: Optional[str] = ""
    version_id: Optional[str] = ""


class SegmentListResponse(PaginatedResponse):
    """Response model for paginated list of segments."""

    facets: Optional[Dict[str, Any]] = {}
    objects: Optional[List[SegmentDetailResponse]] = []


class BulkDeleteSegmentsBody(BaseModel):
    """Request body for bulk deleting segments."""

    segment_ids: Optional[List[str]] = None
    segment_type: Optional[str] = None
    version_id: Optional[str] = None
