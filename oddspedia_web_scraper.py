import datetime
import json
import requests
import time
import pandas as pd

start_date = datetime.date(2023, 3, 22)
end_date = datetime.date(2024, 1, 17)

headers = {
    "cookie": "first_visit=no; varnish_wettsteuer_enabled=0; HAOSSID=4d0694eaf9378; AMCVS_9CE579FD5DCD8B590A495E09%40AdobeOrg=1; user_metro_code=all; user_odds_format=decimal; accept-cookies=true; varnish_odds_format=decimal; user_country=all; SSID=CQBdjx0AAAAAAABEdqRlXFeAAER2pGUIAAAAAAAAAAAAMkSoZQATkw; SSSC=2.G7324108928449533788.8|0.0; SSRT=MkSoZQQBAA; varnish_timezone=America/New_York; cf_clearance=ugkFbI9_JpRSh0YlYdjUQ12PPZQbzNuEs_I3Ag35waY-1705526324-1-AcSXmmEmT6uh7pXwdMwYArrPDs8A5YVsN8yqM07w+1UBObP/IpHKfwk4ZxzmNwcPVGvSfqTQPn58cAtFCU3gGnQ=; AMCV_9CE579FD5DCD8B590A495E09%40AdobeOrg=179643557%7CMCIDTS%7C19740%7CMCMID%7C05879917495810038856964198409433384818%7CMCOPTOUT-1705533524s%7CNONE%7CvVersion%7C5.5.0; __cf_bm=c33Mn7a8XvuJ_zK4W5xxoia_3JVVoEB9gINeU9XDeGg-1705532397-1-AUzZGjkXkeBuDHg08q+ZCJdVTiZtjxwz/bbz1xHfSiC9FBEASqVEs9tLHX9Tkk/CXB9+0ZCvQX76a8a1c9BOLfc=",
    "authority": "oddspedia.com",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "baggage": "sentry-environment=production,sentry-release=1.214.0,sentry-public_key=5ee11cd5558a468388340fbac8cfe782,sentry-trace_id=bc88b9462ad5426ead425e25830e8495,sentry-sample_rate=0.01,sentry-sampled=false",
    "referer": "https://oddspedia.com/counter-strike-global-offensive/odds",
    "sec-ch-ua": """Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120""",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": """macOS""",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sentry-trace": "bc88b9462ad5426ead425e25830e8495-b4954334f4642e36-0",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

date_collection = []
for n in range(int((end_date - start_date).days)):
  date_collection.append((str(start_date + datetime.timedelta(n)), str(start_date + datetime.timedelta(n+1))))

def get_match_list(start_date, end_date):
    url = "https://oddspedia.com/api/v1/getMatchList"
    match_ids = []

    querystring = {
        "excludeSpecialStatus": "0",
        "sortBy": "default",
        "perPageDefault": "50",
        "startDate": f"{start_date}T05:00:00Z",
        "endDate": f"{end_date}T04:59:59Z",
        "geoCode": "US",
        "status": "all",
        "sport": "counter-strike-global-offensive",
        "popularLeaguesOnly": "0",
        "page": "1",
        "perPage": "50",
        "language": "en",
    }

    try:
        response = requests.request(
            "GET", url, data="", headers=headers, params=querystring
        )

        match_list = json.loads(response.text)

        for match in match_list['data']['matchList']:
            match_ids.append(match['id'])
    except:
        match_ids = []

    return match_ids

def get_odds_movement(match_id):
    url = "https://oddspedia.com/api/v1/getOddsMovements"

    querystring = {
        "ot": "201",
        "matchId": f"{match_id}",
        "inplay": "0",
        "wettsteuer": "0",
        "geoCode": "",
        "geoState": "",
        "language": "en",
    }

    try:
        response = requests.request(
            "GET", url, data="", headers=headers, params=querystring
        )

        odds_movement = json.loads(response.text)

        odds_movement_dict = {
            "Lowest": odds_movement['data']['1']['average']['lowest']['y'],
            "Highest": odds_movement['data']['1']['average']['highest']['y'],
            "Open": odds_movement['data']['1']['average']['open']['y']
        }
    except:
        odds_movement_dict = {}

    return odds_movement_dict

def get_match_info(match_id):
    url = "https://oddspedia.com/api/v1/getMatchInfo"

    querystring = {
        "geoCode": "",
        "wettsteuer": "0",
        "matchId": f"{match_id}",
        "language": "en",
    }

    response = requests.request(
        "GET", url, data="", headers=headers, params=querystring
    )

    match_info = json.loads(response.text)
    date, time = match_info['data']['md'].split(" ")

    match_info_dict = {
        'Start Date': date,
        'Start Time': time,
        'Event Name': match_info['data']['league_name'],
        "Team 1": match_info['data']['at'],
        "Team 2": match_info['data']['ht']
    }

    return match_info_dict

def get_match_odds(match_id):
    url = "https://oddspedia.com/api/v1/getMatchOdds"

    querystring = {
        "wettsteuer": "0",
        "geoCode": "US",
        "bookmakerGeoCode": "",
        "bookmakerGeoState": "",
        "matchId": f"{match_id}",
        "language": "en",
    }

    try:
        response = requests.request(
            "GET", url, data="", headers=headers, params=querystring
        )

        match_odds = json.loads(response.text)
        match_odds_dict = dict(match_odds['data']['prematch'][0])
        processed_odds_dict = {}

        for period in match_odds_dict['periods']:
            period_dict = dict(period)
            
            for odd in period_dict['odds']:
                odd_dict = dict(odd)
                processed_odds_dict.update({f"{odd_dict['bookie_name']} - {period_dict['name']} Team 2 Odds": odd_dict['o1']})
                processed_odds_dict.update({f"{odd_dict['bookie_name']} - {period_dict['name']} Team 1 Odds":odd_dict['o2']})
    except:
        processed_odds_dict = {}

    return processed_odds_dict

def get_match_handicap_odds(match_id):
    url = "https://oddspedia.com/api/v1/getMatchOdds"

    querystring = {
        "wettsteuer": "0",
        "geoCode": "US",
        "bookmakerGeoCode": "",
        "bookmakerGeoState": "",
        "matchId": f"{match_id}",
        "oddGroupId": "3",
        "inplay": "0",
        "language": "en",
    }

    try:
        response = requests.request(
            "GET", url, data="", headers=headers, params=querystring
        )

        match_odds = json.loads(response.text)
        handicap_odds_list = match_odds['data']['prematch'][2]['periods']
        processed_handicap_odds_dict = {}

        for index, period in enumerate(handicap_odds_list):
            period_dict = dict(period)
            processed_handicap_odds_dict.update({f"{period_dict['name']} Main Handicap Odds": period_dict['odds']['main'][0]['name']})
            processed_handicap_odds_dict.update({f"{period_dict['name']} Alt. Handicap Odds": period_dict['odds']['alternative'][index]['name']})
    except:
        processed_handicap_odds_dict = {}

    return processed_handicap_odds_dict

master_list = []
for date in date_collection:
    start_date, end_date = date[0], date[1]

    match_ids = get_match_list(start_date, end_date)
    
    for match_id in match_ids:
        odds_movement_dict = get_odds_movement(match_id)
        match_info_dict = get_match_info(match_id)
        processed_odds_dict = get_match_odds(match_id)
        processed_handicap_odds_dict = get_match_handicap_odds(match_id)

        merged_dict = {**match_info_dict, 
                    **processed_odds_dict,
                    **processed_handicap_odds_dict,
                    **odds_movement_dict
                    }
        
        master_list.append(merged_dict)

    time.sleep(5)

df = pd.DataFrame(master_list)
df.to_csv("oddspedia_csgo_scrape_combined.csv", index=False)