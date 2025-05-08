def parse_api_response(data: dict) -> dict:
    # my future self will be mad, but present me is happy
    data = data["data"]

    player_hero_data = {}

    for segment in data:
        if segment.get("type") == "hero":

            hero_name = segment["metadata"]["name"]
            hero_data = {}

            hero_data["hero_class"] = segment["metadata"]["roleName"]
            play_time_hours = segment["stats"]["timePlayed"]["value"] / 3600
            hero_data["playtime_formatted"] = f"{round(play_time_hours, 2)} hours"
            hero_data["playtime_raw"] = play_time_hours
            hero_data["kda"] = segment["stats"]["kdaRatio"]["value"]

            # calculate winrate
            matches_played = segment["stats"]["matchesPlayed"]["value"]
            matches_won = segment["stats"]["matchesWon"]["value"]
            winrate = (matches_won / matches_played) * 100
            hero_data["winrate"] = winrate

            player_hero_data[hero_name] = hero_data

    return player_hero_data
