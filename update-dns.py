#!/usr/bin/env python3

# Python 3 required.
# Script to update Dynamic DNS. Ties in with a crontab if you want to update your dynamic DNS everyso often like other dynamic dns providers do.
# Requires you to use a "sticky" domain.

import urllib.request
import json
import logging

# Setup logging
logging.basicConfig(filename="dns-history.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S", level=logging.INFO)

# What the name says
def fetch_personal_access_token():
	try:
		with open("secrets.json", "r") as f:
			logging.info("Found token!")
			return json.load(f)['token']
	except FileNotFoundError:
		logging.error("File not found! Please add in your token and name it secrets.yml for this to work.")

# Finds record based on domain name
def find_record_by_name(domain, sticky_domain_key):
	# Record the Domain
	DOMAIN_RECORDS_URL="{0}/{1}/records".format(API_URL, domain)
	logging.info("Fetched Domain: {0}".format(DOMAIN_RECORDS_URL))
	# Fetch and parse API Request
	req = urllib.request.Request(url=DOMAIN_RECORDS_URL)
	req.add_header("Authorization", "Bearer {}".format(TOKEN))
	# Setup the request
	try:
		with urllib.request.urlopen(req) as f:
			logging.info("Fetched API Request for Domain Records")
			req_json = json.loads(f.read().decode("UTF-8"))
			domain_records = req_json['domain_records']
			return next(domain_record['id'] for domain_record in domain_records if domain_record['name'] == sticky_domain_key)
	except Exception as e:
		logging.error(str(e))

def get_wan_ip():
	return urllib.request.urlopen("https://checkip.amazonaws.com").read().decode("UTF-8")

def get_current_wan_ip():
	with open("ip.json", "r+") as f:
		content = f.read()
		if content == "":
			new_wan_ip = get_wan_ip().strip()
			json_params = json.dumps({"ip": new_wan_ip})
			f.write(json_params)
		else:
			json_wan_ip = json.loads(content)
			return json_wan_ip['ip']

# Finally to update the DNS records
def update_dns_record(wan_ip, record_id):
	UPDATE_DOMAIN_URL="{0}/{1}/records/{2}".format(API_URL, DOMAIN, record_id)
	logging.info("Fetched Domain: {0}".format(UPDATE_DOMAIN_URL))
	# Fetch and parse API Request
	params = {"data": str(wan_ip)}
	json_params = json.dumps(params).encode("UTF-8")
	req = urllib.request.Request(url=UPDATE_DOMAIN_URL, method='PUT', data=json_params)
	req.add_header("Authorization", "Bearer {}".format(TOKEN))
	req.add_header("Content-Type", "application/json")
	try:
		with urllib.request.urlopen(req) as response:
			json_response = json.loads(response.read().decode("UTF-8"))
			logging.info(json_response)
	except Exception as e:
		logging.error(str(e))

# CONSTANTS (globals but whatever)
DOMAIN="maindomain.com"
STICKY_DOMAIN_KEY="home"
API_URL="https://api.digitalocean.com/v2/domains"
TOKEN=fetch_personal_access_token()

# Check the WAN-IP
new_wan_ip = get_wan_ip().strip()
current_wan_ip = get_current_wan_ip()

# Check for WAN ip and only update if they changed
if new_wan_ip == current_wan_ip:
	logging.info("Same WAN IP. Exiting...")
else:
	# Write to the file to update the WAN IP.
	with open("ip.json", "w") as f:
		json_params = json.dumps({"ip": new_wan_ip})
		f.write(json_params)
	logging.info("Updated WAN IP")
	
	# Find the domain record
	domain_record = find_record_by_name(DOMAIN, STICKY_DOMAIN_KEY)

	# Check for Domain record
	if domain_record:
		logging.info("Domain record found: {0}. Updating record...".format(domain_record))
		update_dns_record(new_wan_ip, domain_record)
	else:
		logging.error("Could not find domain record. Please add your domain to DigitalOcean, and setup the constant variables.")