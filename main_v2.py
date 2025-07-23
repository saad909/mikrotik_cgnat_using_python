import ipaddress
import pandas as pd
import os

def generate_cgnat_rules(private_pool, public_pool, base_port=1, ports_per_user=1000):
    private_network = ipaddress.ip_network(private_pool)
    public_network = ipaddress.ip_network(public_pool)

    private_subnets = list(private_network.subnets(new_prefix=26))
    public_ips = list(public_network)  # includes network & broadcast addresses

    rules = []
    mappings = []
    public_ip_index = 0

    for subnet in private_subnets:
        hosts = list(subnet)
        if public_ip_index >= len(public_ips):
            print("Warning: Not enough public IPs for all /26 subnets.")
            break

        public_ip = public_ips[public_ip_index]
        port_start = base_port

        for host in hosts:
            port_end = port_start + ports_per_user - 1

            if port_end > 65535:
                print(f"Warning: Port range exceeded for {public_ip}. Skipping further hosts.")
                break

            # Generate NAT rules
            rules.append(f"add action=src-nat chain=srcnat protocol=tcp src-address={host} to-addresses={public_ip} to-ports={port_start}-{port_end}\n")
            rules.append(f"add action=src-nat chain=srcnat protocol=udp src-address={host} to-addresses={public_ip} to-ports={port_start}-{port_end}\n")
            rules.append(f"add action=src-nat chain=srcnat src-address={host} to-addresses={public_ip}\n")

            # Add to mapping
            mappings.append({
                "Private IP": str(host),
                "Public IP": str(public_ip),
                "Port Start": port_start,
                "Port End": port_end
            })

            port_start += ports_per_user

        public_ip_index += 1

    return rules, mappings


def main():
    excel_file = "ip_pools.xlsx"  # Excel input file
    df = pd.read_excel(excel_file)

    all_mappings = []

    # output file path
    output_dir = "Outputs"
    output_filename = input("Please enter the project name with no spaces in name: ")
    output_path = os.path.join(output_dir, output_filename)

    with open(f"{output_path}.rsc", "w") as handler:
        for index, row in df.iterrows():
            # private_pool = row[0]
            # public_pool = row[1]
            private_pool = row.iloc[0]
            public_pool = row.iloc[1]
            print(f"{public_pool} -> {private_pool}")

            handler.write("/ip firewall nat" + "\n")
            header = f"\n# CGNAT Rules for {private_pool} -> {public_pool}\n"
            handler.write(header)
            # print(header)

            rules, mappings = generate_cgnat_rules(private_pool, public_pool)

            # Write NAT rules to script file
            for rule in rules:
                handler.write(rule)

            # Collect all mappings
            all_mappings.extend(mappings)

        # Optional: write all mappings at the end of the script file for reference
        handler.write("\n\n# Mapping of Private IPs to Public IP and Port Ranges\n")
        for m in all_mappings:
            handler.write(f"# {m['Private IP']} => {m['Public IP']}:{m['Port Start']}-{m['Port End']}\n")

    # Save the mapping to Excel
    mapping_df = pd.DataFrame(all_mappings)
    mapping_df.to_excel(f"{output_path}" + ".xlsx", index=False)
    print(f"\n✅ Mapping saved to '{output_path}.xlsx'")


if __name__ == "__main__":
    main()
