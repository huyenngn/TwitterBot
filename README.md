# SimpleTwitterBot
Collection of customizable Twitter Bots.

## Usage
Single Service Bot
```python
from translate_tweets import TranslateTweetsBot

# Bot that translates Tweets it's tagged under
ttb = TranslateTweetBot()
ttb.start()
```
Multiple Service Bot:
```python
import threading
from translate_tweets import TranslateTweetsBot
from instagram_updates import InstagramUpdatesBot

# Bot that translates Tweets it's tagged under and reposts Instagram updates to Twitter
ttb = TranslateTweetBot()
t_ttb = threading.Thread(target=ttb.start)
t_ttb.start()

api = ttb.getapi()
iub = InstagramUpdatesBot(api=api)
t_iub = threading.Thread(target=iub.start)
t_iub.start()
```

## Example
Try out TranslateTweetsBot:
```bash
sudo docker build . -t main
```

```bash
docker run -d --restart always \
-e ACCESS_TOKEN="{twitter access token}" \
-e ACCESS_TOKEN_SECRET="{twitter access token secret}" \
-e BEARER_TOKEN="{twitter bearer token}" \
-e CONSUMER_KEY="{twitter consumer key}" \
-e CONSUMER_SECRET="{twitter consumer secret}" \
-e GCLOUD_ID="{google cloud id}" \
-e GOOGLE_APPLICATION_CREDENTIALS="{path/to/gcloud/app/creds.json}" \
-e API_FLASH_KEY="{api flash key}" main
```
