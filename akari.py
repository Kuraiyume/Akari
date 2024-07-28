import argparse
import configparser
import dns.resolver
import concurrent.futures
import json
import csv
from termcolor import colored
from retrying import retry

def perform_dns_lookup(domain, record_type, timeout):
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = timeout
    result = []
    try:
        answers = resolver.resolve(domain, record_type)
        result.append(f"{colored(record_type, 'blue')} records for {colored(domain, 'green')}:")
        for rdata in answers:
            result.append(f"  {rdata}")
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

def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    domains = config.get('settings', 'domains').split(',')
    record_types = config.get('settings', 'record_types').split(',')
    timeout = config.getfloat('settings', 'timeout')
    return domains, record_types, timeout

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
def perform_dns_lookup_with_retry(domain, record_type, timeout):
    return perform_dns_lookup(domain, record_type, timeout)

def main():
    parser = argparse.ArgumentParser(description="Akari: Advanced DNS Enumerator")
    parser.add_argument("-d", "--domain", type=str, help="The target domain to lookup.")
    parser.add_argument("-t", "--types", type=str, nargs='+', default=["A", "AAAA", "CNAME", "MX", "NS", "SOA", "TXT", "CAA", "PTR", "SRV", "NAPTR", "DS", "DNSKEY", "TLSA", "LOC"],
                        help="The DNS record types to lookup. Default is a comprehensive set of common types.")
    parser.add_argument("-to", "--timeout", type=float, default=5.0, help="Timeout for DNS queries in seconds. Default is 5 seconds.")
    parser.add_argument("-c", "--config", type=str, help="Path to configuration file.")
    parser.add_argument("-o", "--output", type=str, help="Output file to save the results.")
    parser.add_argument("-f", "--format", type=str, choices=['txt', 'json', 'csv'], default='txt', help="Output format for the results.")
    args = parser.parse_args()

    if args.config:
        domains, record_types, timeout = load_config(args.config)
    else:
        if not args.domain:
            parser.error("The target domain must be specified if no config file is provided.")
        domains = [args.domain]
        record_types = args.types
        timeout = args.timeout

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_domain_record = {executor.submit(perform_dns_lookup_with_retry, domain, record_type, timeout): (domain, record_type) for domain in domains for record_type in record_types}
        for future in concurrent.futures.as_completed(future_to_domain_record):
            domain, record_type = future_to_domain_record[future]
            try:
                result = future.result()
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
