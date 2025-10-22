import uuid
import boto3
from boto3.session import Session
from bedrock_agentcore_starter_toolkit import Runtime
from typing import Optional, Any
import json
import requests
import urllib

def setup_cognito_user_pool():

    print("Setting up Amazon Cognito user pool...")
    boto_session = Session()
    region = boto_session.region_name
    # Initialize Cognito client
    cognito_client = boto3.client("cognito-idp", region_name=region)
    try:
        # Create User Pool
        user_pool_response = cognito_client.create_user_pool(
            PoolName="agentpool", Policies={"PasswordPolicy": {"MinimumLength": 8}}
        )
        pool_id = user_pool_response["UserPool"]["Id"]
        # Create App Client
        app_client_response = cognito_client.create_user_pool_client(
            UserPoolId=pool_id,
            ClientName="MCPServerPoolClient",
            GenerateSecret=False,
            ExplicitAuthFlows=["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"],
        )
        client_id = app_client_response["UserPoolClient"]["ClientId"]
        # Create User
        cognito_client.admin_create_user(
            UserPoolId=pool_id,
            Username="testuser",
            TemporaryPassword="Temp123!",
            MessageAction="SUPPRESS",
        )
        # Set Permanent Password
        cognito_client.admin_set_user_password(
            UserPoolId=pool_id,
            Username="testuser",
            Password="MyPassword123!",
            Permanent=True,
        )
        # Authenticate User and get Access Token
        auth_response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": "testuser", "PASSWORD": "MyPassword123!"},
        )
        bearer_token = auth_response["AuthenticationResult"]["AccessToken"]
        # Output the required values
        print(f"Pool id: {pool_id}")
        print(
            f"Discovery URL: https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/openid-configuration"
        )
        print(f"Client ID: {client_id}")
        print(f"Bearer Token: {bearer_token}")

        # Return values if needed for further processing
        return {
            "pool_id": pool_id,
            "client_id": client_id,
            "bearer_token": bearer_token,
            "discovery_url": f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/openid-configuration",
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def reauthenticate_user(client_id):
    boto_session = Session()
    region = boto_session.region_name
    # Initialize Cognito client
    cognito_client = boto3.client("cognito-idp", region_name=region)
    # Authenticate User and get Access Token
    auth_response = cognito_client.initiate_auth(
        ClientId=client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": "testuser", "PASSWORD": "MyPassword123!"},
    )
    bearer_token = auth_response["AuthenticationResult"]["AccessToken"]
    return bearer_token

def invoke_endpoint(
    agent_arn: str,
    payload,
    session_id: str,
    bearer_token: Optional[str],
    region: str = "us-west-2",
    endpoint_name: str = "DEFAULT",
) -> Any:
    """Invoke agent endpoint using HTTP request with bearer token."""
    escaped_arn = urllib.parse.quote(agent_arn, safe="")
    url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{escaped_arn}/invocations"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id,
    }

    try:
        body = json.loads(payload) if isinstance(payload, str) else payload
    except json.JSONDecodeError:
        body = {"payload": payload}

    try:
        response = requests.post(
            url,
            params={"qualifier": endpoint_name},
            headers=headers,
            json=body,
            timeout=100,
            stream=True,
        )
        print("Response: ", response.json())
        return response.json()

    except requests.exceptions.RequestException as e:
        print("Failed to invoke agent endpoint: %s", str(e))
        raise

def configure_runtime(runtime: Runtime, agent_name: str, auth_config: dict = None):
    print("Configuring AgentCore Runtime...")

    config_params = {
        "entrypoint": "backend/app/agents/bedrock_agent/bedrock_agent.py",
        "auto_create_execution_role": True,
        "auto_create_ecr": True,
        "requirements_file": "backend/app/agents/bedrock_agent/requirements.txt",
        "region": "us-west-2",
    }

    # Add auth config if provided
    if auth_config:
        config_params["authorizer_configuration"] = auth_config

    runtime.configure(**config_params)

    print("Configuration completed ✓")

def launch_runtime(runtime: Runtime):
    print("Launching Agent server to AgentCore Runtime...")
    print("This may take several minutes...")
    launch_result = runtime.launch(
        env_vars={"OTEL_PYTHON_EXCLUDED_URLS": "/ping,/invocations"}
    )
    print("Launch completed ✓")
    return launch_result

def invoke_agent(prompt: str, setup_runtime=False, agent_arn=None, agent_id=None, client_id=None):
    if setup_runtime:

        cognito_config = setup_cognito_user_pool()
        client_id = cognito_config["client_id"]

        auth_config = {
            "customJWTAuthorizer": {
                "allowedClients": [client_id],
                "discoveryUrl": cognito_config["discovery_url"],
            }
        }

        print("Auth config: ", auth_config)

        agentcore_runtime = Runtime()
        configure_runtime(runtime=agentcore_runtime, agent_name="main_agent", auth_config=auth_config)
        launch_result = launch_runtime(runtime=agentcore_runtime)
        agent_arn = launch_result.agent_arn
        agent_id = launch_result.agent_id

    else:
        assert agent_arn is not None, "Agent ARN is required"
        assert agent_id is not None, "Agent ID is required"
        assert client_id is not None, "Client ID is required"
        print("Runtime already setup")

    print("Agent ARN: %s", agent_arn)
    print("Agent ID: %s", agent_id)

    bearer_token = reauthenticate_user(client_id=client_id)

    print("Bearer Token: %s", bearer_token)

    response = invoke_endpoint(
        agent_arn=agent_arn,
        payload={"prompt": prompt},
        session_id=str(uuid.uuid4()),
        bearer_token=bearer_token,
    )

    return response["response"]



if __name__ == "__main__":
    # invoke_agent(setup_runtime=True)
    response = invoke_agent(prompt="Find me real 3 job openings for software engineer intern with apply urls", setup_runtime=False,
        agent_arn="arn:aws:bedrock-agentcore:us-west-2:488234668762:runtime/bedrock_agent-TO4pEH7Avm",
        agent_id="bedrock_agent-TO4pEH7Avm",
        client_id="6riuf44c9oa1vf7ut7t2jukf37")
    print("Response: ", response)
