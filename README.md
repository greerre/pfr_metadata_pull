# pfr_metadata_pull

This repo contains the set of scripts used to create the dataset referenced here:

https://twitter.com/greerreNFL/status/1146519422527389696

The dataset takes metadata from pro-football-reference and merges it with the game files from the nflscrapR pbp data package.
This matches pfr's game id to the NFL API's game id, allowing for more interesting analysis. For instance, passing EPA by depth of target (nflscrapR data) can be viewed against windspeed or stadium (from p-f-r).

This repo has three scipts with the following purposes:
- pfr_game_link_scraper.py // creates a csv with all p-f-r boxscores dating to 1960
- pfr_meta_data_pull.py    // uses the box score links to pull metadata for each game
- pfr_meta_data_format.py  // formats the metadata to make it 1) more structured and 2) joinable to nflscrapR

These scripts are pretty hacky, but the hope is to turn it into a package that can be update the dataset on an ongoing basis
