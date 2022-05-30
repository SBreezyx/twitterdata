import time

import requests
import tqdm

import csv
import json


def get_keys(pth="app.json"):
    with open(pth) as f:
        return json.load(f)


def main():
    keys = get_keys()

    with open("congress.csv") as csvfp:
        reader = csv.DictReader(csvfp, delimiter="|")
        congress = [r for r in reader]

    for congressman in tqdm.tqdm(congress):
        username = congressman["username"]
        id = congressman["id"]
        # this can happen for when a congressman isn't on twitter, but we want to record his existence
        if not id:
            time.sleep(1)
            res = requests.get(
                url=f"https://api.twitter.com/2/users/by/username/{username}",
                headers={"Authorization": f"Bearer {keys['bearer']}"},
            )
            if res.status_code == 200:
                data = res.json()
                if "data" in data:
                    data = data["data"]
                    congressman["id"] = data["id"]
                    print(f"Added {username} with id {data['id']}")
                else:
                    # supplied username does not match what is on twitter. skip
                    pass
            else:
                # error with the API. log it?
                pass
        else:
            # ID already gotten
            pass

    with open("congress.csv", "w") as csvfp:
        writer = csv.DictWriter(csvfp, fieldnames=("name", "username", "id"), delimiter="|")
        writer.writeheader()
        for congressman in congress:
            writer.writerow(congressman)


if __name__ == "__main__":
    main()

