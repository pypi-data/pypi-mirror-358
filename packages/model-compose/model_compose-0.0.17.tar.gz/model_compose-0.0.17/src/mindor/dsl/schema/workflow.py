from typing import Type, Union, Literal, Optional, Dict, List, Tuple, Set, Annotated, Any
from pydantic import BaseModel, Field
from pydantic import model_validator
from .component import ComponentConfig

class JobConfig(BaseModel):
    component: Optional[Union[ str, ComponentConfig ]] = "__default__"
    action: Optional[str] = "__default__"
    input: Optional[Any] = None
    output: Optional[Any] = None
    depends_on: Optional[List[str]] = Field(default_factory=list)

class WorkflowVariableConfig(BaseModel):
    name: Optional[str] = Field(default=None, description="The name of the variable")
    type: Literal[ "string", "base64", "integer", "number", "json", "boolean", "image", "file", "select" ] = Field(..., description="Type of the variable")
    format: Optional[Literal[ "base64" ]] = Field(default=None, description="Format of the variable")
    required: bool = Field(default=False, description="Whether this variable is required")
    default: Optional[Any] = Field(default=None, description="Default value if not provided")
    description: Optional[str] = Field(default=None, description="Description of the variable")
    options: Optional[List[Any]] = Field(default=None, description="List of valid options for select type")

class WorkflowConfig(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    jobs: Optional[Dict[str, JobConfig]] = Field(default_factory=dict)
    default: bool = False

    @model_validator(mode="before")
    def inflate_single_job(cls, values: Dict[str, Any]):
        if "jobs" not in values:
            job_keys = set(JobConfig.model_fields.keys())
            if any(k in values for k in job_keys):
                values["jobs"] = { "__default__": { k: values.pop(k) for k in job_keys if k in values } }
        return values
