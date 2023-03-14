# SimpleTwitterBot
Collection of customizable Twitter Bots.

## Usage
Single Service Bot
```python
from translate_tweets import TranslateTweetsBot

# Bot that translates Tweets it's tagged under
bot = TranslateTweetsBot(src="th", dst="en")
bot.start()
```
Multiple Service Bot:
```python
import threading
from translate_tweets import TranslateTweetsBot
from translate_tiktoks import TranslateTikToksBot

# Bot that translates Tweets it's tagged under and reposts Instagram updates to Twitter
bot1 = TranslateTweetsBot(src="th", dst="en")
t_bot1 = threading.Thread(target=bot1.start)
t_bot1.start()

api = ttw.getapi()
bot2 = TranslateTikToksBot(src="th", dst="th", api=api)
t_bot2 = threading.Thread(target=bot2.start)
t_bot2.start()
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
-e API_FLASH_KEY="{1st api flash key}" \
-e API_FLASH_KEY2="{2nd api flash key}" \
-e API_FLASH_KEY3="{3rd api flash key}" \ main
```
