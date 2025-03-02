import os

from dotenv import load_dotenv

from nba.nba_main import NBA


def get_env(name):
    try:
        load_dotenv()
        secret = os.getenv(name)

        return secret

    except Exception as e:
        print(f"Error loading secrets: {e}")


if __name__ == "__main__":
    username = get_env('BLUESKY_USERNAME')
    password = get_env('BLUESKY_PASSWORD')

    nba = NBA(username=username, password=password)
    nba.main()
