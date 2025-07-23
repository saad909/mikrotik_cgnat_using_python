import ipaddress
import pandas as pd

def generate_cgnat_rules(private_pool, public_pool, base_port=1, ports_per_user=1000):
    private_network = ipaddress.ip_network(private_pool)
    public_network = ipaddress.ip_network(public_pool)

    private_subnets = list(private_network.subnets(new_prefix=26))
    public_ips = list(public_network.hosts())

    rules = []
    public_ip_index = 0

    for subnet in private_subnets:
        hosts = list(subnet.hosts())
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

            rules.append(f"add action=src-nat chain=srcnat protocol=tcp src-address={host} to-addresses={public_ip} to-ports={port_start}-{port_end}\n")
            rules.append(f"add action=src-nat chain=srcnat protocol=udp src-address={host} to-addresses={public_ip} to-ports={port_start}-{port_end}\n")
            rules.append(f"add action=src-nat chain=srcnat src-address={host} to-addresses={public_ip}\n")

            port_start += ports_per_user

        public_ip_index += 1

    return rules


def main():
    excel_file = "ip_pools.xlsx"  # Make sure this Excel file is formatted correctly
    df = pd.read_excel(excel_file)

    with open("natting_output.txt","w") as handler:
        for index, row in df.iterrows():
            private_pool = row[0]
            public_pool = row[1]

            message = f"\n# CGNAT Rules for {private_pool} -> {public_pool}\n"
            handler.write(message)
            print(message)
            rules = generate_cgnat_rules(private_pool, public_pool)
            for rule in rules:
                handler.write(rule)
                print("\n" + rule + "\n")


if __name__ == "__main__":
    main()

