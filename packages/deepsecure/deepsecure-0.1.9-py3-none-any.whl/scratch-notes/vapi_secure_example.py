import asyncio
from vapi import Vapi
from deepsecure import issue_credential_ext_async, register_agent_if_not_exists
from deepsecure.core.types import CredentialRequestContext, CredentialRequestExt

# --- DeepSecure Configuration ---
# This name uniquely identifies your Vapi application/agent.
AGENT_NAME = "vapi-call-creator-agent"

# This defines the "scope" or resource the agent is requesting.
# It must match what's configured in your credservice policy.
VAPI_RESOURCE_ID = "vapi_production_credentials"
VAPI_ACTION = "get_api_key"

async def get_vapi_key(agent_id: str) -> str:
    """
    Issues a credential from DeepSecure to securely fetch the Vapi API key.
    The access_token in the credential response will contain the Vapi key.
    """
    print("Requesting Vapi API key from DeepSecure...")
    try:
        context = CredentialRequestContext(
            resource_id=VAPI_RESOURCE_ID,
            action=VAPI_ACTION,
        )
        request_ext = CredentialRequestExt(context=context)

        # Issue an ephemeral credential for the agent by its registered ID
        cred_response = await issue_credential_ext_async(
            agent_id=agent_id,
            request=request_ext,
            ttl=300  # Requesting the key for 5 minutes
        )

        print("Successfully fetched Vapi API key.")
        # The backend is configured to put the Vapi API key in the 'access_token' field.
        return cred_response.access_token

    except Exception as e:
        print(f"\nError fetching credential from DeepSecure: {e}")
        print("Ensure credservice is running, configured with the Vapi policy, and the CLI is configured (URL, token).")
        raise

async def create_call(vapi_client: Vapi):
    """Uses the initialized Vapi client to create a call."""
    print("Creating call with Vapi...")
    response = await vapi_client.calls.create(
        phone_number_id="YOUR_PHONE_NUMBER_ID",  # Replace with your Vapi Phone Number ID
        customer={"number": "+1234567890"},  # Replace with your customer's phone number
        assistant={
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Keep your responses concise and friendly."
                    }
                ]
            }
        }
    )
    print("Call creation response received.")
    return response

async def main():
    """
    Main function to set up the agent, get the key, and create the call.
    """
    # 1. Register the agent if it doesn't exist. This stores the agent's private
    #    key in the local OS keyring for secure, passwordless authentication.
    print(f"Ensuring agent '{AGENT_NAME}' is registered...")
    agent_identity = await register_agent_if_not_exists(name=AGENT_NAME, auto_generate_keys=True)
    print(f"Agent '{agent_identity.name}' is ready with ID: {agent_identity.id}")

    # 2. Securely fetch the Vapi API key using the agent's identity.
    vapi_api_key = await get_vapi_key(agent_id=agent_identity.id)

    # 3. Initialize the Vapi client with the fetched key.
    vapi_client = Vapi(vapi_api_key)

    # 4. Make the call.
    call_response = await create_call(vapi_client)
    print("\n--- Vapi Call Response ---")
    print(call_response)
    print("--------------------------")


if __name__ == "__main__":
    # Ensure your deepsecure CLI is configured first!
    # `deepsecure configure set-url http://localhost:8001`
    # `deepsecure configure set-token`
    asyncio.run(main()) 