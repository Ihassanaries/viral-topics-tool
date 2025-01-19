import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyBrWecWtZjfdzTQCStr5Hw8iDUu_HrS13c"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# List of broader keywords
keywords = [
    "HFY", "Humanity F Yeah", "HFY Humanity F*** Yeah", "hfy sci fi stories", "hfy stories",
    "hfy battle", "hfy scifi", "sci fi hfy", "hfy reddit stories", "hfy war stories",
    "sci fi hfy stories", "best hfy stories", "hfy revelation", "scifi hfy stories",
    "hfy battel", "hfy galactic stories", "hfy human", "hfy deathworlder", "hfy human pet",
    "best hfy story", "hfy war", "hfy human pets"
]

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        # Iterate over the list of keywords
        for keyword in keywords:
            st.write(f"Searching for keyword")
            
            # Define search parameters
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            # Fetch video data
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            if response.status_code != 200:
                st.error(f"Failed to fetch data for keyword: {keyword}")
                continue

            videos = response.json()["items"]
            video_ids = [video["id"]["videoId"] for video in videos]
            channel_ids = [video["snippet"]["channelId"] for video in videos]

            # Fetch video and channel statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)

            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)

            if stats_response.status_code == 200 and channel_response.status_code == 200:
                stats = stats_response.json()["items"]
                channels = channel_response.json()["items"]

                # Collect results
                for video, stat, channel in zip(videos, stats, channels):
                    title = video["snippet"]["title"]
                    description = video["snippet"]["description"][:200]
                    video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                    views = int(stat["statistics"]["viewCount"])
                    subs = int(channel["statistics"].get("subscriberCount", 0))

                    if subs < 3000:  # Only include channels with fewer than 3,000 subscribers
                        all_results.append({
                            "Title": title,
                            "Description": description,
                            "URL": video_url,  # Store the raw URL
                            "Views": views,
                            "Subscribers": subs
                        })
            else:
                st.error(f"Failed to fetch statistics for keyword: {keyword}")

        # Display all results in a clickable format
        if all_results:
            st.success(f"Found {len(all_results)} results across all keywords!")
            for result in all_results:
                st.markdown(
                    f"**Title:** {result['Title']}  \n"
                    f"**Description:** {result['Description']}  \n"
                    f"**URL:** [Watch Video]({result['URL']})  \n"
                    f"**Views:** {result['Views']}  \n"
                    f"**Subscribers:** {result['Subscribers']}"
                )
                st.write("---")
        else:
            st.warning("No results found for channels with fewer than 3,000 subscribers.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
