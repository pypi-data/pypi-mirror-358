from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Pipeline(BaseModel):
    id: str
    name: str


class ProjectItem(BaseModel):
    tenant_id: str = Field(alias="tenantId")
    created_at: datetime = Field(alias="createdAt")
    require_classification: bool = Field(alias="requireClassification")
    budget_amount: Optional[Any] = Field(None, alias="budgetAmount")
    budget_period: Optional[Any] = Field(None, alias="budgetPeriod")
    budget_alert: Optional[Any] = Field(None, alias="budgetAlert")
    budget_stop: bool = Field(alias="budgetStop")
    used_budget_amount: Optional[Any] = Field(None, alias="usedBudgetAmount")
    resume_ends_at: Optional[datetime] = Field(None, alias="resumeEndsAt")
    updated_at: datetime = Field(alias="updatedAt")
    pipelines: List[Pipeline]
    models: Optional[Any] = None
    data_sources: List[Any] = Field(alias="dataSources")
    prompts: Optional[Any] = None
    api_keys: Optional[Any] = Field(alias="apiKeys")
    memories: Optional[Any] = None
    project_icon: Optional[str] = Field(None, alias="projectIcon")
    project_icon_id: Optional[str] = Field(None, alias="projectIconId")
    description: Optional[str] = None
    project_type: str = Field(alias="projectType")
    classifications: Optional[Any] = None
    id: str
    name: str
