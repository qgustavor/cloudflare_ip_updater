import os, json
import requests
from subprocess import Popen, PIPE
import ConfigParser
import urllib2

#TODO replace config parser with json
config = ConfigParser.RawConfigParser()
config.readfp(open('options.cfg'))
email, api_key, domain, sub_domain_names = [config.get("Options", s) for s in
                            ["email", "api_key", "domain", "sub_domain_names"]]

sub_domain_names = [e for e in sub_domain_names.split("'") if "." in e]


def parse_api_result(url_extension, headers, data=None):
    base_api_url = "https://api.cloudflare.com/client/v4/zones"
    if data is not None:
        res = requests.put(base_api_url+url_extension, headers=headers, data=json.dumps(options)).json()
    else:
        res = requests.get(base_api_url+url_extension, headers=headers).json()
    if not res.get("success", False):
	print("error occurred for %s:\n%s\n"%(url_extension, res))
    return res

def get_zone_id():
    print("getting zone id")
    return parse_api_result("?name="+domain, headers={"X-Auth-Email":email, "X-Auth-Key":api_key})["result"][0]["id"]

def get_record_ids(zone_id, sub_domain_names):
    print("getting record ids for %s"%sub_domain_names)
    res = parse_api_result("/%s/dns_records"%(zone_id), headers={"X-Auth-Email":email, "X-Auth-Key":api_key})      
    return {e["name"]:e["id"] for e in res["result"] if e["name"] in sub_domain_names}

def get_ip():
    return json.load(urllib2.urlopen('https://api.ipify.org/?format=json'))['ip']


if __name__ == "__main__":
    ip = get_ip()
    zone_id = get_zone_id()
    for name, rec_id in get_record_ids(zone_id, sub_domain_names).items():
        print("updating ip for " + name)
        options = {'id': rec_id, 'type': "A", 'name': name, 'content': ip}
        url = "https://api.cloudflare.com/client/v4/zones/%s/dns_records/%s"%(zone_id, rec_id)
        headers={"X-Auth-Email":email, "X-Auth-Key":api_key}
        response = requests.put(url, headers=headers, data=json.dumps(options)).json()
        print("success: %s \n%s"%(response["success"],("" if response["success"] else response["errors"])))

