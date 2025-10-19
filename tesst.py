from deepgram import DeepgramClient

DEEPGRAM_API_KEY = "ac67d33899c481316bd6fbde62a87f1003aa123b"

def generate_access_token():
    try:
        client = DeepgramClient(api_key=DEEPGRAM_API_KEY)

        # Use grant_token(), not grant()
        token_response = client.auth.v1.grant_token()

        print("Access token:", token_response.access_token)
        print("Expires in (seconds):", token_response.expires_in)

    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    generate_access_token()
"""
curl --location --request POST 'https://api.deepgram.com/v1/auth/grant' \
--header 'Authorization: Token 52cfca21cf50b4127497b622122c6fa8f93f8aca'
"""
