from enum import Enum
from typing import Any, Callable, Dict, Generic, List, Optional, TypedDict, Union, Literal, TypeVar, cast
from uuid import uuid4
from datetime import datetime

# Type variable for generic types
T = TypeVar('T')

# Environment type
Environment = Literal['TEST', 'LIVE', 'INTERNAL']

# ID Types
TaskId = str  # Format: tsk-{uuid}
SessionId = str  # Format: ses-{uuid}
RequestId = str  # Format: req-{uuid}

class PaymanConfig(TypedDict, total=False):
    """
    Configuration for the Payman client.

    Args:
        client_id: Your Payman client ID
        client_secret: Your Payman client secret
        environment: Optional environment to use ("TEST" or "LIVE"). Defaults to "LIVE"
        name: Optional name for the client instance
        session_id: Optional session ID to use instead of generating a new one
    """
    client_id: str
    client_secret: Optional[str]
    environment: Optional[Environment]
    name: Optional[str]
    session_id: Optional[SessionId]

class OAuthResponse(TypedDict):
    accessToken: str
    tokenType: str
    expiresIn: int
    scope: str
    refreshToken: Optional[str]

class MessagePart(TypedDict):
    type: Literal['text']
    text: str
    metadata: Optional[Dict[str, Any]]

class Message(TypedDict):
    role: Literal['user', 'assistant']
    parts: List[MessagePart]
    metadata: Optional[Dict[str, Any]]

class TaskState(str, Enum):
    SUBMITTED = 'submitted'
    WORKING = 'working'
    INPUT_REQUIRED = 'input-required'
    COMPLETED = 'completed'
    CANCELED = 'canceled'
    FAILED = 'failed'
    UNKNOWN = 'unknown'

class TaskStatus(TypedDict):
    state: TaskState
    message: Optional[Message]
    timestamp: str

class FormattedArtifact(TypedDict):
    name: str
    description: Optional[str]
    content: str
    type: str
    timestamp: str
    metadata: Optional[Dict[str, Any]]

class Artifact(TypedDict):
    name: Optional[str]
    description: Optional[str]
    parts: List[MessagePart]
    index: Optional[int]
    append: Optional[bool]
    metadata: Optional[Dict[str, Any]]
    last_chunk: Optional[bool]

class Task(TypedDict):
    id: TaskId
    session_id: Optional[SessionId]
    status: TaskStatus
    artifacts: List[Artifact]
    metadata: Dict[str, Any]

class AgentCapabilities(TypedDict):
    streaming: bool
    push_notifications: bool
    state_transition_history: bool

class AgentProvider(TypedDict):
    organization: str
    url: str

class AgentAuthentication(TypedDict):
    schemes: List[str]
    credentials: Optional[str]

class AgentSkill(TypedDict):
    id: str
    name: str
    description: Optional[str]
    tags: Optional[List[str]]
    examples: Optional[List[str]]
    input_modes: Optional[List[str]]
    output_modes: Optional[List[str]]

class AgentCard(TypedDict):
    name: str
    description: Optional[str]
    url: str
    provider: AgentProvider
    version: str
    documentation_url: Optional[str]
    capabilities: AgentCapabilities
    authentication: AgentAuthentication
    default_input_modes: List[str]
    default_output_modes: List[str]
    skills: List[AgentSkill]

# JSON-RPC Types
class JsonRPCRequest(TypedDict, Generic[T]):
    jsonrpc: Literal['2.0']
    id: RequestId
    method: str
    params: T

class TaskParams(TypedDict):
    id: TaskId
    message: Message
    sessionId: SessionId
    metadata: Optional[Dict[str, Any]]

class TaskGetParams(TypedDict):
    id: TaskId

class TaskCancelParams(TypedDict):
    id: TaskId

class AskOptions(TypedDict, total=False):
    """
    Options for the ask method.

    new_session: Whether to start a new session for this request
    output_format: Desired format of the response returned by ask.
        - 'markdown' (default) returns a simplified structure for the artifacts
        - 'json' returns the json rpc response for the artifacts
    metadata: Additional metadata to include with the request
    part_metadata: Metadata to include with the message parts
    message_metadata: Metadata to include with the message
    on_message: Callback function to handle incoming messages. If provided, the request will be streamed.
    """
    new_session: bool
    output_format: Literal['markdown', 'json']
    metadata: Dict[str, Any]
    part_metadata: Dict[str, Any]
    message_metadata: Dict[str, Any]
    on_message: Callable[[Any], None]

class TaskStatusUpdateEvent(TypedDict):
    id: TaskId
    status: TaskStatus
    is_final: bool
    metadata: Dict[str, Any]

class TaskArtifactUpdateEvent(TypedDict):
    id: TaskId
    artifact: Artifact

# Response Types
class A2AError(TypedDict):
    code: int
    message: str
    data: Optional[Any]

class JsonRPCResponse(TypedDict, Generic[T]):
    jsonrpc: Literal['2.0']
    id: RequestId
    result: Optional[T]
    error: Optional[A2AError]

class FormattedTaskResponse(TypedDict):
    task_id: TaskId
    request_id: RequestId
    session_id: Optional[SessionId]
    status: TaskState
    status_message: Optional[str]
    timestamp: str
    artifacts: List[FormattedArtifact]
    metadata: Dict[str, Any]
    error: Optional[A2AError]

# Type aliases
TaskResponse = JsonRPCResponse[Task]
AgentCardResponse = AgentCard
TaskStatusUpdateResponse = JsonRPCResponse[TaskStatusUpdateEvent]
TaskArtifactUpdateResponse = JsonRPCResponse[TaskArtifactUpdateEvent]

def format_response(response: TaskResponse) -> FormattedTaskResponse:
    """Formats a TaskResponse into a more developer-friendly structure."""
    if response.get('error'):
        return cast(FormattedTaskResponse, {
            'task_id': response['id'],
            'request_id': response['id'],
            'session_id': None,
            'status': TaskState.FAILED,
            'status_message': None,
            'timestamp': datetime.utcnow().isoformat(),
            'artifacts': [],
            'metadata': {},
            'error': response['error'],
        })

    if not response.get('result'):
        raise Exception('Response has no result and no error')

    result = response['result']
    if not result:
        raise Exception('Response result is None')

    formatted_artifacts: List[FormattedArtifact] = []
    for i, artifact in enumerate(result.get('artifacts', [])):
        content = '\n'.join(part['text'] for part in artifact.get('parts', []))
        formatted_artifacts.append({
            'name': artifact.get('name') or 'artifact',
            'description': artifact.get('description'),
            'content': content,
            'type': 'text',
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': artifact.get('metadata', {}),
        })

    formatted_response = {
        'task_id': result['id'],
        'request_id': response['id'],
        'session_id': result.get('session_id'),
        'status': result['status']['state'],
        'status_message': None,
        'timestamp': result['status']['timestamp'],
        'artifacts': formatted_artifacts,
        'metadata': result.get('metadata', {}),
        'error': None,
    }
    return cast(FormattedTaskResponse, formatted_response) 