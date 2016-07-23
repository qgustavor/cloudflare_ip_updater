import os, json
import requests
from subprocess import Popen, PIPE
import dns.resolver
import urllib2

with open('config.json') as data_file:
    config = json.load(data_file)
email, api_key, domains = [config.get(s) for s in ["email", "api_key", "domains"]]

def parse_api_result(url_extension, headers, data=None):
    base_api_url = "https://api.cloudflare.com/client/v4/zones"
    if data is not None:
        res = requests.put(base_api_url + url_extension, headers=headers, data=json.dumps(options)).json()
    else:
        res = requests.get(base_api_url + url_extension, headers=headers).json()
    if not res.get("success", False):
        print("Error occurred for %s:\n%s\n"%(url_extension, res))
    return res

def get_zone_id(domain):
    print("Getting zone id")
    return parse_api_result("?name=" + domain, headers={"X-Auth-Email": email, "X-Auth-Key": api_key})["result"][0]["id"]

def get_record_ids(zone_id, sub_domain_names):
    print("Getting record ids for %s"%sub_domain_names)
    res = parse_api_result("/%s/dns_records"%(zone_id), headers={"X-Auth-Email": email, "X-Auth-Key": api_key})      
    return {e["name"]:e["id"] for e in res["result"] if e["name"] in sub_domain_names}

def get_ip():
    # https://stackoverflow.com/a/22075729
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ["208.67.222.222", "208.67.220.220"]
    return resolver.query("myip.opendns.com")[0].to_text()

if __name__ == "__main__":
    ip = get_ip()
    for domain, sub_domain_names in domains.iteritems():
        zone_id = get_zone_id(domain)
        for name, rec_id in get_record_ids(zone_id, sub_domain_names).items():
            print("Updating ip for " + name)
            options = {'id': rec_id, 'type': "A", 'name': name, 'content': ip}
            url = "https://api.cloudflare.com/client/v4/zones/%s/dns_records/%s"%(zone_id, rec_id)
            headers={"X-Auth-Email":email, "X-Auth-Key":api_key}
            response = requests.put(url, headers=headers, data=json.dumps(options)).json()
            print("Success: %s \n%s"%(response["success"],("" if response["success"] else response["errors"])))

