# download-all-videos-from-youtube-channel

```sh
export YOUTUBE_API_KEY=

poetry run python main.py <channel_id> -d

# or

poetry run python main.py <channel_id>
poetry run cat outputs/videos.txt | xargs -n1 -P5 yt-dlp -f "bv+ba/b" -o "outputs/%(title)s.f%(format_id)s.%(ext)s"
```
