from typing import Literal, Optional, Sequence

from pydantic import BaseModel, Field


class Position(BaseModel):
    x: float
    y: float


class Measured(BaseModel):
    width: float
    height: float


class NodeData(BaseModel):
    label: str
    description: Optional[str] = None
    type: Optional[str] = None


class StartNodeRequestBody(BaseModel):
    name: str
    type: Literal["string", "integer", "float", "boolean"]
    sub_type: Optional[str] = None
    required: bool = True


class StartNodeData(NodeData):
    request_body: Sequence[StartNodeRequestBody] = Field(default_factory=list)
    type: str = "start"
    label: str = "Start"


class CodeNodeData(NodeData):
    code: str
    inputs: Sequence[dict | str] = Field(default_factory=list)
    outputs: Sequence[dict | str] = Field(default_factory=list)
    type: str = "code"
    language: str = "python"


class Node(BaseModel):
    id: str
    data: NodeData | CodeNodeData | StartNodeData
    position: Position = Field(default_factory=lambda: Position(x=0, y=0))
    measured: Measured = Field(default_factory=lambda: Measured(width=176, height=60))
    type: str = "custom"
    deletable: bool = True
    selected: bool = False
    dragging: bool = False


class Edge(BaseModel):
    id: str
    source: str
    target: str
    type: str = "custom"
    marker_end: dict = Field(
        default_factory=lambda: {"type": "arrowclosed", "width": 24, "height": 24}
    )
