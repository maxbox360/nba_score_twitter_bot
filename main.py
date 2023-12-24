from nba import NBA
from dotenv import load_dotenv
import os

def get_env(name):
    try:
        load_dotenv()
        secret = os.getenv(name)

        return secret
    except Exception as e:
        print(f"Error loading secrets: {e}")


if __name__ == "__main__":
    api_key = get_env('TWITTER_API_KEY')
    api_secret_key = get_env('TWITTER_API_SECRET')
    access_token = get_env('TWITTER_ACCESS_TOKEN')
    access_token_secret = get_env('TWITTER_TOKEN_SECRET')

    nba = NBA(api_key=api_key, api_secret_key=api_secret_key, access_token=access_token, access_token_secret=access_token_secret)
    nba.main()
