# cloudflare_ip_updater

Updates the IPs for several DNS records on CloudFlare using their native API

# Howto:
* `pip install -r requirements.txt`
* copy options.json.template to options.json
* change options.json
* run ``python main.py`` to see if it works

## Use crontab (or similar) to run the updater every 5 minutes:
* ``crontab -e``
* add the following line: ``*/5 * * * * python /path_to_cloudflare_ip_updater/main.py``

