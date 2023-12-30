import os
from dotenv import load_dotenv
from nba import NBA


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

    nba = NBA(consumer_key=consumer_key, consumer_secret=consumer_secret)
    nba.main()
