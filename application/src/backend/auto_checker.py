import socket
import requests

def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def sync_points(email, points):
    if not is_connected():
        print("No internet connection. Will sync later.")
        return False

    try:
        response = requests.post(
            "http://127.0.0.1:5000/update_points",
            json={"email": email, "points": points},
            timeout=5
        )
        if response.status_code == 200:
            print("Points synced successfully.")
            return True
        else:
            print("Failed to sync points:", response.json())
            return False
    except Exception as e:
        print("Error syncing points:", e)
        return False


def fetch_leaderboard():
    if not is_connected():
        print("No internet connection. Can't fetch leaderboard.")
        return None
    try:
        response = requests.get("http://127.0.0.1:5000/leaderboard", timeout=5)
        if response.status_code == 200:
            return response.json()['leaderboard']
        else:
            print("Failed to fetch leaderboard:", response.json())
            return None
    except Exception as e:
        print("Error fetching leaderboard:", e)
        return None
