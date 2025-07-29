import base64
from datetime import datetime
from typing import Dict, Optional, Union, Callable, Any, cast, List
import requests
import threading

from .types import (
    AskOptions,
    Environment,
    FormattedTaskResponse,
    OAuthResponse,
    PaymanConfig,
    SessionId,
    TaskResponse,
    format_response,
)
from .utils import (
    API_ENDPOINTS,
    BASE_URLS,
    create_message,
    create_task_request,
    generate_session_id,
)

class PaymanClient:
    """
    Client for interacting with the Payman AI Platform

    Example:
        ```python
        # Initialize with client credentials
        payman = PaymanClient.with_credentials({
            'client_id': 'your-client-id',
            'client_secret': 'your-client-secret',
            'session_id': 'ses-existing-session-id'  # optional, if not provided, a new session will be created
        })

        # Initialize with authorization code
        payman = PaymanClient.with_auth_code({
            'client_id': 'your-client-id',
            'client_secret': 'your-client-secret',
            'session_id': 'ses-existing-session-id'  # optional, if not provided, a new session will be created
        }, 'your-auth-code')

        # Initialize with pre-existing access token
        payman = PaymanClient.with_token(
            {
                'client_id': 'your-client-id',
                'environment': 'LIVE',  # optional, defaults to 'LIVE'
                'name': 'my-client',  # optional
                'session_id': 'ses-existing-session-id'  # optional
            },
            {
                'accessToken': 'your-access-token',
                'expiresIn': 3600  # token expiry in seconds
            },
        )

        # Initialize with refresh token
        payman = PaymanClient.with_token(
            {
                'client_id': 'your-client-id',
                'environment': 'LIVE',  # optional, defaults to 'LIVE'
                'name': 'my-client',  # optional
                'session_id': 'ses-existing-session-id'  # optional
            },
            {
                'refreshToken': 'your-refresh-token'
            },
        )

        # Get a formatted response (recommended for most use cases)
        formatted_response = await payman.ask("What's the weather?")

        # Get a raw response
        raw_response = await payman.ask("What's the weather?", {'output_format': 'json'})

        # Start a new session with metadata
        response = await payman.ask("Hello!", {
            'new_session': True,
            'metadata': {'source': 'web-app'}
        })

        # Resume a conversation using session ID from previous response
        response1 = await payman.ask("Hello!")
        session_id = response1['session_id']  # Save this for later

        # Later, resume the conversation
        payman2 = PaymanClient.with_credentials({
            'client_id': 'your-client-id',
            'client_secret': 'your-client-secret',
            'session_id': session_id
        })
        response2 = await payman2.ask("What did we talk about earlier?")

        # Get the current session ID from a client instance
        current_session_id = payman.get_session_id()

        # Get the current refresh token from a client instance
        current_refresh_token = payman.get_refresh_token()
        ```
    """

    def __init__(
        self,
        config: PaymanConfig,
        auth_code: Optional[str] = None,
        token_info: Optional[Dict[str, Any]] = None,
    ):
        """
        Creates a new PaymanClient instance with full configuration

        Args:
            config: Configuration for the client
            auth_code: Optional authorization code obtained via OAuth
            token_info: Optional object containing pre-existing access token information or refresh token
                - accessToken: Pre-existing access token (optional if refreshToken is provided)
                - expiresIn: Token expiry time in seconds (optional if refreshToken is provided)
                - refreshToken: Optional refresh token to use for obtaining a new access token
        """
        self.config = config
        self.session_id = config.get('session_id') or generate_session_id()
        env = config.get('environment', 'LIVE')
        self.base_url = BASE_URLS[cast(Environment, env)]
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

        # Initialize synchronization primitives
        self.initialization_lock = threading.Lock()
        self.initialization_complete = threading.Event()
        self.initialization_complete.set()  # Initially set since we're not initializing
        self.is_initializing = False

        # Initialize token-related attributes
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[float] = None
        self.refresh_token: Optional[str] = None

        if token_info:
            # Handle both camelCase (API format) and snake_case formats
            self.access_token = token_info.get('accessToken') or token_info.get('access_token')
            expires_in = token_info.get('expiresIn')
            if expires_in is None:
                expires_in = token_info.get('expires_in')
            self.refresh_token = token_info.get('refreshToken') or token_info.get('refresh_token')
            
            if self.access_token and expires_in is not None:
                self.token_expiry = datetime.now().timestamp() + expires_in
            elif self.refresh_token:
                # If only refresh token is provided, we'll initialize it later
                self._initialize_access_token(refresh_token=self.refresh_token)
            else:
                raise ValueError('Either accessToken and expiresIn must be provided, or refreshToken must be provided')
        else:
            if auth_code:
                self._initialize_access_token(auth_code=auth_code)

    @classmethod
    def with_credentials(cls, config: PaymanConfig) -> 'PaymanClient':
        """Creates a new PaymanClient instance with client credentials."""
        if not config.get('client_id') or not isinstance(config['client_id'], str):
            raise ValueError('client_id is required')
        if not config.get('client_secret') or not isinstance(config['client_secret'], str):
            raise ValueError('client_secret is required for client credentials flow')
        return cls(config)

    @classmethod
    def with_auth_code(cls, config: PaymanConfig, auth_code: str) -> 'PaymanClient':
        """Creates a new PaymanClient instance with an authorization code."""
        if not config.get('client_id') or not isinstance(config['client_id'], str):
            raise ValueError('client_id is required')
        if not config.get('client_secret') or not isinstance(config['client_secret'], str):
            raise ValueError('client_secret is required for authorization code flow')
        if not auth_code or not isinstance(auth_code, str) or not auth_code.strip():
            raise ValueError('auth_code is required')
        return cls(config, auth_code=auth_code)

    @classmethod
    def with_token(
        cls,
        config: PaymanConfig,
        token_info: Dict[str, Any],
    ) -> 'PaymanClient':
        """Creates a new PaymanClient instance with just client ID and access token."""
        if not config.get('client_id') or not isinstance(config['client_id'], str):
            raise ValueError('client_id is required')
        
        # Validate that either accessToken + expiresIn are provided, or refreshToken is provided
        has_access_token = token_info.get('accessToken') is not None and token_info.get('expiresIn') is not None
        has_refresh_token = token_info.get('refreshToken') is not None
        
        if not has_access_token and not has_refresh_token:
            raise ValueError('Either accessToken and expiresIn must be provided, or refreshToken must be provided')
        
        return cls(config, token_info=token_info)

    def _initialize_access_token(self, auth_code: Optional[str] = None, refresh_token: Optional[str] = None) -> None:
        """
        Initializes or refreshes the OAuth access token

        Args:
            auth_code: Optional authorization code. If provided, uses authorization_code grant type,
                      otherwise uses client_credentials
            refresh_token: Optional refresh token. If provided, uses refresh_token grant type
        """
        with self.initialization_lock:
            if self.is_initializing:
                return

            self.is_initializing = True
            self.initialization_complete.clear()  # Signal that initialization has started
            try:
                params = {}
                
                if refresh_token:
                    params['grant_type'] = 'refresh_token'
                    params['refresh_token'] = refresh_token
                elif auth_code:
                    params['grant_type'] = 'authorization_code'
                    params['code'] = auth_code
                else:
                    params['grant_type'] = 'client_credentials'

                auth = base64.b64encode(
                    f"{self.config['client_id']}:{self.config['client_secret']}".encode()
                ).decode()

                response = self.session.post(
                    f"{self.base_url}{API_ENDPOINTS['OAUTH_TOKEN']}",
                    params=params,
                    headers={'Authorization': f'Basic {auth}'},
                )
                response.raise_for_status()
                data: OAuthResponse = response.json()

                self.access_token = data['accessToken']
                self.token_expiry = datetime.now().timestamp() + data['expiresIn']
                self.refresh_token = data.get('refreshToken')
            except Exception as e:
                print(f'Failed to initialize access token: {e}')
                if hasattr(e, 'response'):
                    print(f'Response data: {e.response.json()}')
                    print(f'Response status: {e.response.status_code}')
                raise
            finally:
                self.is_initializing = False
                self.initialization_complete.set()  # Signal that initialization is complete

    def _ensure_valid_access_token(self) -> str:
        """
        Ensures the access token is valid and refreshes it if necessary

        Returns:
            A valid access token

        Raises:
            Error: If token cannot be obtained
        """
        now = datetime.now().timestamp()
        if not self.access_token or not self.token_expiry or now >= self.token_expiry - 60:
            # Try to refresh using stored refresh token first, fallback to client credentials
            if self.refresh_token:
                self._initialize_access_token(refresh_token=self.refresh_token)
            else:
                self._initialize_access_token()

        if not self.access_token:
            raise Exception('Failed to obtain access token')

        return self.access_token

    def ask(
        self,
        text: str,
        options: Optional[AskOptions] = None,
    ) -> Union[FormattedTaskResponse, TaskResponse]:
        """
        Ask a question or send a message to the Payman AI Agent

        Args:
            text: The message or question to send to the agent
            options: Optional parameters for the request
                - on_message: Callback function to handle incoming messages
                - new_session: Whether to start a new session
                - metadata: Additional metadata to include
                - part_metadata: Metadata for message parts
                - message_metadata: Metadata for the message
                - output_format: Desired format ('markdown' or 'json')

        Returns:
            The task response (formatted or raw)
        """
        token = self._ensure_valid_access_token()

        if options and options.get('new_session'):
            self.session_id = generate_session_id()

        message = create_message(text, options)
        request = create_task_request(message, self.session_id, options)

        response = self.session.post(
            f"{self.base_url}{API_ENDPOINTS['TASKS_SEND']}",
            json=request,
            headers={'x-payman-access-token': token},
        )
        response.raise_for_status()
        data: TaskResponse = response.json()

        if data.get('error'):
            raise Exception(f"Failed to get response from agent: {data['error']}")

        if not data.get('result'):
            raise Exception('No response received from agent')

        if options and options.get('output_format') == 'json':
            return data

        return format_response(data)

    def get_access_token(self) -> Optional[Dict[str, Any]]:
        """Gets the current access token information."""
        try:
            # Wait for any ongoing initialization to complete
            self.initialization_complete.wait()
            
            # Now we can safely access the token
            token = self._ensure_valid_access_token()
            if not self.token_expiry:
                return None
            expires_in = max(0, int(self.token_expiry - datetime.now().timestamp()))
            return {
                'accessToken': token,
                'expiresIn': expires_in,
            }
        except Exception as e:
            print(f'Failed to get access token: {e}')
            return None

    def is_access_token_expired(self) -> bool:
        """Checks if the current access token has expired."""
        if not self.access_token or not self.token_expiry:
            return True
        return bool(datetime.now().timestamp() >= self.token_expiry - 60)

    def get_client_name(self) -> Optional[str]:
        """Gets the name of the Payman client from the configuration."""
        return self.config.get('name')

    def get_session_id(self) -> SessionId:
        """Gets the current session ID."""
        return self.session_id

    def get_refresh_token(self) -> Optional[str]:
        """Gets the current refresh token if available."""
        return self.refresh_token 