import requests

import csv
import json
import os
import time


def get_keys(pth="app.json"):
    with open(pth) as f:
        return json.load(f)


def get_congress(pth="congress.csv"):
    congress = []
    with open(pth) as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        for r in reader:
            if r["id"]:
                congress.append(r)
            else:
                # no user ID, cannot use this congressman
                pass
    return congress


def main():
    keys = get_keys()
    congress = get_congress()

    db = {}
    for congressman in congress:
        print(f"Fetching timeline for {congressman['username']}...", end='')
        res = requests.get(
            url=f"https://api.twitter.com/2/users/{congressman['id']}/tweets",
            headers={"Authorization": f"Bearer {keys['bearer']}"},
            params={
                "expansions": "author_id,in_reply_to_user_id,referenced_tweets.id",
                "max_results": 5,
                "tweet.fields": "conversation_id,created_at,public_metrics,referenced_tweets,text",
                "user.fields": "location",
                "start_time": "2022-05-24T12:00:00Z",
                "end_time": "2022-05-26T12:00:00Z",  # TODO: remove later
            }
        )

        if res.status_code == 200:
            data = res.json()
            if "data" in data:
                users = {user["id"]: user for user in data.get("includes", {}).get("users", [])}
                for tweet in data["data"]:
                    referenced_tweet = tweet.get("referenced_tweets", [{"type": '', "id": ''}])[0]
                    pub_met = tweet["public_metrics"]
                    record = {
                        "tweet_id": tweet["id"],
                        "created_at": tweet["created_at"],
                        "author_id": tweet["author_id"],
                        "author_username": congressman["username"],
                        "author_geo": users[tweet["author_id"]].get("location", ''),
                        "conversation_id": tweet["conversation_id"],
                        "referenced_id": referenced_tweet["id"],
                        "reference_type": referenced_tweet["type"],
                        "pub_rt_cnt": pub_met["retweet_count"],
                        "pub_like_cnt": pub_met["like_count"],
                        "pub_rep_cnt": pub_met["reply_count"],
                        "pub_qt_cnt": pub_met["quote_count"],
                        "depth": 0 if tweet["id"] == tweet["conversation_id"] else ''
                    }
                    db[tweet["id"]] = record

                print("done.")
            else:
                # some kind of error. don't care
                print(f"failed.")

        else:
            print(f"failed (status code: {res.status_code})")

        time.sleep(1)

    with open("tweets.csv", "w") as csvfile:
        fields = ("tweet_id",
                  "created_at",
                  "author_id",
                  "author_username",
                  "author_geo",
                  "conversation_id",
                  "referenced_id",
                  "reference_type",
                  "pub_rt_cnt",
                  "pub_like_cnt",
                  "pub_rep_cnt",
                  "pub_qt_cnt",
                  "depth",)
        writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter="|")
        writer.writeheader()
        for record in db.values():
            writer.writerow(record)


if __name__ == "__main__":
    main()
