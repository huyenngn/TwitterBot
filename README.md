# Translation Twitter Bot
A bot that translates tweets.

## Usage
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