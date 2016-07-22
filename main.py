import os, json
import requests
from subprocess import Popen, PIPE
import ConfigParser


config = ConfigParser.RawConfigParser()

config.readfp(open('options.cfg'))
email, api_key, domain, sub_domain_names = [config.get("Options", s) for s in
                            ["email", "api_key", "domain", "sub_domain_names"]]


def get_system_command_result(command):
    return Popen(command, shell=True, stdout=PIPE).stdout.read()

def parse_api_result(url_extension, headers, data=None):
    base_api_url = "https://api.cloudflare.com/client/v4/zones"
    if data is not None:
        return requests.put(base_api_url+url_extension, headers=headers, data=json.dumps(options)).json()
    else:
        return requests.get(base_api_url+url_extension, headers=headers).json()

def get_zone_id():
    res = parse_api_result("?name="+domain, headers={"X-Auth-Email":email, "X-Auth-Key":api_key})
    print res
    return res["result"][0]["id"]

def get_record_ids(zone_id, sub_domain_names):
    res = parse_api_result("/%s/dns_records"%(zone_id), headers={"X-Auth-Email":email, "X-Auth-Key":api_key})
    ids = {e["name"]: e["id"] for e in res["result"] if e["name"] in sub_domain_names}
    return ids

def get_record_id_data(zone_id, sub_domain_names):
    res = parse_api_result("/%s/dns_records"%(zone_id), headers={"X-Auth-Email":email, "X-Auth-Key":api_key})
    return {e["name"]:e for e in res["result"] if e["name"] in sub_domain_names}

def get_ip():
    from json import load
    from urllib2 import urlopen
    return load(urlopen('https://api.ipify.org/?format=json'))['ip']

def get_ip6():
    # CAUTION! DIRTY INSUFFICIENTLY TESTED HACK INCOMING
    def get_res(command):
        return os.popen(command).read().split("\n")
    ips = get_res("/sbin/ifconfig eth0 |  awk '/inet6/{print $3}'")
    scopes = get_res("/sbin/ifconfig eth0 |  awk '/inet6/{print $4}'")
    if len(sys.argv)>1 and sys.argv[1]=="debug":
        print "ips, scopes:", ips, scopes
    ip = [ip for ip,scope in zip(ips,scopes) if "Global" in scope][0]
    return ip.split("/")[0]


if __name__ == "__main__":
    ip = get_ip()
    zone_id = get_zone_id()
    for name, rec_id in get_record_ids(zone_id, sub_domain_names).items():
        print("ID: " + rec_id + " Name: " + name)
        options = {'id': rec_id, 'type': "A", 'name': name, 'content': ip}
        url = "https://api.cloudflare.com/client/v4/zones/%s/dns_records/%s"%(zone_id, rec_id)
        headers={"X-Auth-Email":email, "X-Auth-Key":api_key}
        response = requests.put(url, headers=headers, data=json.dumps(options)).json()
        print response

