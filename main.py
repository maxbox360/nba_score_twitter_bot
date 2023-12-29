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
    consumer_key = get_env('CONSUMER_KEY')
    consumer_secret = get_env('CONSUMER_SECRET')
    access_token = get_env('ACCESS_TOKEN')
    access_token_secret = get_env('TOKEN_SECRET')

    nba = NBA(consumer_key=consumer_key, consumer_secret=consumer_secret,
              access_token=access_token, token_secret=access_token_secret)
    nba.main()
