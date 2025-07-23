import socket
import requests
import json
import os

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
            "http://127.0.0.1:5000/points",  # Make sure this matches your server route
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
            leaderboard = response.json().get('leaderboard')
            if leaderboard is not None:

                save_leaderboard_to_file(leaderboard)
                return leaderboard
            else:
                print("Leaderboard key missing in response.")
                return None
        else:
            print("Failed to fetch leaderboard:", response.json())
            return None
    except Exception as e:
        print("Error fetching leaderboard:", e)
        return None

def save_leaderboard_to_file(data, filename="leaderboard.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Leaderboard saved to {os.path.abspath(filename)}")
    except Exception as e:
        print("Error saving leaderboard to file:", e)


if __name__ == "__main__":

    leaderboard = fetch_leaderboard()
    if leaderboard:
        print("Leaderboard fetched and saved.")
    else:
        print("Could not fetch leaderboard.")
