import argparse
import configparser
import dns.resolver
import json
import csv
from termcolor import colored
from retrying import retry
import ipinfo

banner = r"""
           _              _ 
     /\   | |            (_)
    /  \  | | ____ _ _ __ _ 
   / /\ \ | |/ / _` | '__| |
  / ____ \|   < (_| | |  | |
 /_/    \_\_|\_\__,_|_|  |_|v0.12
                Veilwr4ith
"""

def perform_dns_lookup(domain, record_type, timeout, nameserver=None, ipinfo_token=None):
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = timeout
    if nameserver:
        resolver.nameservers = [nameserver]
    
    result = []
    try:
        answers = resolver.resolve(domain, record_type)
        result.append(f"{colored(record_type, 'blue')} records for {colored(domain, 'green')}:")
        ips = []
        for rdata in answers:
            ip_str = str(rdata)
            result.append(ip_str)
            if record_type == "A" and ipinfo_token:
                ips.append(ip_str)
        
        if ips and ipinfo_token:
            ip_geolocations = get_ipinfo_data(ips, ipinfo_token)
            for ip, geo_data in ip_geolocations.items():
                result.append(f"IP Geolocation for {ip}:")
                for key, value in geo_data.items():
                    result.append(f"    {key}: {value}")
    except dns.resolver.NoAnswer:
        result.append(colored(f"No {record_type} records found for {domain}.", 'yellow'))
    except dns.resolver.NXDOMAIN:
        result.append(colored(f"The domain {domain} does not exist.", 'red'))
    except dns.resolver.Timeout:
        result.append(colored(f"Timeout while resolving {domain} for {record_type} records.", 'red'))
    except dns.resolver.YXDOMAIN:
        result.append(colored(f"Too many questions in the DNS query for {domain}.", 'red'))
    except dns.resolver.NoNameservers:
        result.append(colored(f"No nameservers available to resolve {domain}.", 'red'))
    except Exception as e:
        result.append(colored(f"An error occurred: {e}", 'red'))
    return result

def get_ipinfo_data(ips, token):
    handler = ipinfo.getHandler(token)
    geolocations = {}
    for ip in ips:
        try:
            details = handler.getDetails(ip)
            geolocations[ip] = {
                "City": details.city,
                "Region": details.region,
                "Country": details.country,
                "Org": details.org,
                "Postal": details.postal,
                "Timezone": details.timezone,
                "Location": details.loc
            }
        except Exception as e:
            geolocations[ip] = {
                "Error": f"Could not retrieve geolocation data: {e}"
            }
    return geolocations

def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    domains = config.get('settings', 'domains').split(',')
    record_types = config.get('settings', 'record_types').split(',')
    timeout = config.getfloat('settings', 'timeout')
    nameserver = config.get('settings', 'nameserver', fallback=None)
    ipinfo_token = config.get('settings', 'ipinfo_token', fallback=None)
    return domains, record_types, timeout, nameserver, ipinfo_token

def save_results(results, output_file, output_format):
    if output_format == 'json':
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)
    elif output_format == 'csv':
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for result in results:
                writer.writerow([result])
    else:
        with open(output_file, 'w') as f:
            for line in results:
                f.write(line + '\n')

@retry(wait_fixed=2000, stop_max_attempt_number=3)
def perform_dns_lookup_with_retry(domain, record_type, timeout, nameserver=None, ipinfo_token=None):
    return perform_dns_lookup(domain, record_type, timeout, nameserver, ipinfo_token)

def main():
    print(banner)
    parser = argparse.ArgumentParser(description="Akari: Advanced DNS Enumerator")
    parser.add_argument("-d", "--domain", type=str, help="The target domain to lookup.")
    parser.add_argument("-t", "--types", type=str, nargs='+', default=["A", "AAAA", "CNAME", "MX", "NS", "SOA", "TXT", "CAA", "PTR", "SRV", "NAPTR", "DS", "DNSKEY", "TLSA", "LOC"],
                        help="The DNS record types to lookup. Default is a comprehensive set of common types.")
    parser.add_argument("-to", "--timeout", type=float, default=5.0, help="Timeout for DNS queries in seconds. Default is 5 seconds.")
    parser.add_argument("-c", "--config", type=str, help="Path to configuration file.")
    parser.add_argument("-o", "--output", type=str, help="Output file to save the results.")
    parser.add_argument("-f", "--format", type=str, choices=['txt', 'json', 'csv'], default='txt', help="Output format for the results.")
    parser.add_argument("-n", "--nameserver", type=str, help="Custom nameserver for DNS resolution.")
    parser.add_argument("--ipinfo-token", type=str, help="IPinfo API token for IP geolocation.")
    args = parser.parse_args()

    if args.config:
        domains, record_types, timeout, nameserver, ipinfo_token = load_config(args.config)
    else:
        if not args.domain:
            parser.error("The target domain must be specified if no config file is provided.")
        domains = [args.domain]
        record_types = args.types
        timeout = args.timeout
        nameserver = args.nameserver
        ipinfo_token = args.ipinfo_token

    results = []
    
    for domain in domains:
        for record_type in record_types:
            try:
                result = perform_dns_lookup_with_retry(domain, record_type, timeout, nameserver, ipinfo_token)
                results.extend(result)
            except Exception as exc:
                results.append(colored(f"{record_type} generated an exception: {exc}", 'red'))

    if args.output:
        save_results(results, args.output, args.format)
    else:
        for line in results:
            print(line)

if __name__ == "__main__":
    main()
