from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RunSummary(BaseModel):
    data_groups: Optional[List[str]] = Field(None, title="Team that collected the run. e.g. PI name, safety form, proposal number")
    experimenter_name: Optional[str] = Field(None, title="name of user or entity that performed collection")
    experiment_title: Optional[str]
    proposal: Optional[str] = Field(None, title="Team that collected the run. e.g. PI name, safety form, proposal number")
    collection_date: str = Field(None, title="run colleciton date")
    instrument_name: Optional[str] = Field(
        None, title="name of the instrument (beamline, etc) where data collection was performed")
    num_data_images: Optional[int] = Field(None, title="number of data collection images")
    sample_name: Optional[str] = Field(None, title="sample name")
    uid: str

    class Config:
        title = "Summary information for a run, intended to be used by "\
              "applications when a brief view is needed, as in a list of runs"
