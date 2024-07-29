# Akari: Advanced DNS Enumerator

Akari is a robust and versatile DNS enumeration tool designed to cater to the needs of security professionals, network administrators, and IT enthusiasts. It provides a comprehensive set of features to perform detailed DNS lookups, making it an invaluable tool for both reconnaissance and troubleshooting.

## Features

- **Comprehensive DNS Lookups:** Supports a wide range of DNS record types including A, AAAA, CNAME, MX, NS, SOA, TXT, CAA, PTR, SRV, NAPTR, DS, DNSKEY, TLSA, and LOC.
- **Multi-Domain Support:** Easily configure and perform lookups on multiple domains simultaneously using a configuration file.
- **Configurable Timeouts:** Set custom timeouts for DNS queries to ensure timely responses even in slow network conditions.
- **Automatic Retries:** Built-in retry mechanism for handling transient errors, ensuring reliable and consistent results.
- **Flexible Output Formats:** Save results in plain text, JSON, or CSV formats for easy integration with other tools and workflows.
- **IP Geolocation Data (Optional):** Retrieve and display geolocation information for IP addresses found in DNS A records using the IPinfo API (to obtain the API token, users need to sign up [here](https://ipinfo.io)). The information includes city, region, country, organization, postal code, timezone, and location coordinates.
- **Customizable Nameservers:** Optionally specify custom nameservers for DNS resolution to use different DNS servers than the system defaults, allowing for more control over the DNS lookup process.

## Installation

1. Clone the repository

```bash
git clone https://github.com/veilwr4ith/Akari
```

2. Install the specified requirements for Akari

```bash
pip3 install -r requirements.txt
```

3. Run the tool in help mode to show all the parameters

```bash
python3 akari.py -h
```

## Available Parameters

**-d, --domain:** The target domain to lookup. (Required if no config file is provided)

**-t, --types:** The DNS record types to lookup. Default is a comprehensive set of common types.

**-to, --timeout:** Timeout for DNS queries in seconds. Default is 5 seconds.

**-c, --config:** Path to configuration file.

**-o, --output:** Output file to save the results.

**-f, --format:** Output format for the results. Choices are txt, json, csv. Default is txt.

**-n, --nameserver:** Custom nameserver for DNS resolution.

**--ipinfo-token:** IPinfo API token for IP geolocation.

## Usage

1. Perform DNS lookups for a single domain with default settings:

```bash
python3 akari.py -d example.com
```

2. Specify custom DNS record types to lookup:

```bash
python3 akari.py -d example.com -t A MX TXT
```

3. Use a configuration file to specify domains, record types, and timeout:

```bash
python3 akari.py -c config.ini
```

4. Save the results to a JSON file for further analysis:

```bash
python3 akari.py -d example.com -o results.json -f json
```

5. Specify a custom name server for DNS resolution:

```bash
python3 akari.py -d example.com -n 8.8.8.8
```

6. Use ipinfo token for IP Geolocation (If the token is not provided it will skip the geolocation process):

```bash
python3 akari.py -d example.com --ipinfo-token <your_ip_info_token>
```

## Configuration File Format

The configuration file should be in INI format with the following structure:

```bash
[settings]
domains = example.com,example.org
record_types = A,MX,TXT
timeout = 5.0
nameserver = 8.8.8.8 (optional)
ipinfo_token = <your_ip_info_token> (optional)
```

## License

- Akari is licensed under the GNU General Public License.





