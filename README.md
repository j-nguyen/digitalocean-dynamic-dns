# DigitalOcean Dynamic DNS Script

A script to help update your domain match with the WAN IP you have at home. Uses the "sticky" method by updating 1 record only, and having CNAMEs to update accordingly.


## Configuration

You will need an empty `ip.json` file, and a `secrets.json` file. Your `secrets.json` should look something like this:


```json
{
  "token": "my digitalocean personal token"
}
```

## Usage

Run the script, or use a scheduler like cron to check and update your records every so often. This script also checks if your wan IP actually changed so you don't have to make another call to potentially avoid any rate limiting calls.


## Logging

Feel free to look at the logs in `dns-history.log`. You should see if your stuff updated or not. Also, feel free to edit the script to your liking.