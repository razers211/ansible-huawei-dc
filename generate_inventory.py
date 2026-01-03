#!/usr/bin/env python3
"""
Interactive Inventory Generator for Huawei CE6800 Spine-Leaf Fabric
"""

import yaml
import ipaddress
from typing import Dict, List, Tuple

class InventoryGenerator:
    def __init__(self):
        self.inventory = {
            'all': {
                'children': {
                    'spine': {'hosts': {}},
                    'leaf': {'hosts': {}}
                }
            }
        }
        self.ip_scheme = {}
        
    def get_user_input(self) -> Dict:
        """Get interactive user input for fabric configuration"""
        print("🌐 Huawei CE6800 Spine-Leaf Inventory Generator")
        print("=" * 50)
        
        config = {}
        
        # Basic fabric info
        config['fabric_name'] = input("Enter fabric name [spine_leaf_fabric]: ").strip() or "spine_leaf_fabric"
        config['asn'] = input("Enter BGP ASN [65000]: ").strip() or "65000"
        
        # IP addressing
        print("\n📡 IP Addressing Configuration")
        config['spine_loopback_subnet'] = input("Spine loopback subnet [10.255.1.0/24]: ").strip() or "10.255.1.0/24"
        config['leaf_loopback_subnet'] = input("Leaf loopback subnet [10.255.2.0/24]: ").strip() or "10.255.2.0/24"
        config['vtep_loopback_subnet'] = input("VTEP loopback subnet [10.255.3.0/24]: ").strip() or "10.255.3.0/24"
        config['interconnect_subnet_base'] = input("Interconnect subnet base [10.1.0.0/16]: ").strip() or "10.1.0.0/16"
        
        # Device counts
        print("\n🔧 Device Configuration")
        config['spine_count'] = int(input("Number of spine switches [2]: ").strip() or "2")
        config['leaf_count'] = int(input("Number of leaf switches [2]: ").strip() or "2")
        
        # Interface configuration
        print("\n🔌 Interface Configuration")
        config['spine_interface_start'] = int(input("Spine interface start number [1]: ").strip() or "1")
        config['leaf_interface_start'] = int(input("Leaf interface start number [1]: ").strip() or "1")
        config['leaf_access_interface'] = input("Leaf access interface [48]: ").strip() or "48"
        
        # Interface mapping mode
        print("\n🔌 Interface Mapping Mode:")
        print("1. Sequential (auto-generate interfaces)")
        print("2. Exact Match (specify exact interfaces)")
        mapping_mode = input("Select interface mapping mode [1]: ").strip() or "1"
        config['interface_mapping_mode'] = mapping_mode
        
        if mapping_mode == "2":
            config['spine_interfaces'] = {}
            config['leaf_interfaces'] = {}
            
            print("\n🔌 Spine Interface Configuration:")
            for spine_idx in range(config['spine_count']):
                hostname = f"spine{spine_idx+1:02d}"
                interfaces = []
                for leaf_idx in range(config['leaf_count']):
                    interface = input(f"  {hostname} -> leaf{leaf_idx+1:02d} interface [10GE1/0/{spine_idx + leaf_idx + 1}]: ").strip()
                    if not interface:
                        interface = f"10GE1/0/{spine_idx + leaf_idx + 1}"
                    interfaces.append(interface)
                config['spine_interfaces'][hostname] = interfaces
            
            print("\n🔌 Leaf Interface Configuration:")
            for leaf_idx in range(config['leaf_count']):
                hostname = f"leaf{leaf_idx+1:02d}"
                interfaces = []
                for spine_idx in range(config['spine_count']):
                    interface = input(f"  {hostname} -> spine{spine_idx+1:02d} interface [10GE1/0/{spine_idx + leaf_idx + 1}]: ").strip()
                    if not interface:
                        interface = f"10GE1/0/{spine_idx + leaf_idx + 1}"
                    interfaces.append(interface)
                
                access_interface = input(f"  {hostname} access interface [10GE1/0/{config['leaf_access_interface']}]: ").strip()
                if not access_interface:
                    access_interface = f"10GE1/0/{config['leaf_access_interface']}"
                interfaces.append(access_interface)
                config['leaf_interfaces'][hostname] = interfaces
        
        # Management IPs
        print("\n💻 Management IP Configuration")
        mgmt_mode = input("Management IP mode (auto/manual) [auto]: ").strip() or "auto"
        config['mgmt_mode'] = mgmt_mode
        
        if mgmt_mode == "manual":
            config['spine_mgmt_ips'] = {}
            config['leaf_mgmt_ips'] = {}
            
            print("\n🔧 Spine Management IPs:")
            for i in range(config['spine_count']):
                hostname = f"spine{i+1:02d}"
                mgmt_ip = input(f"  {hostname} management IP: ").strip()
                while not mgmt_ip:
                    mgmt_ip = input(f"  {hostname} management IP (required): ").strip()
                config['spine_mgmt_ips'][hostname] = mgmt_ip
            
            print("\n🔧 Leaf Management IPs:")
            for i in range(config['leaf_count']):
                hostname = f"leaf{i+1:02d}"
                mgmt_ip = input(f"  {hostname} management IP: ").strip()
                while not mgmt_ip:
                    mgmt_ip = input(f"  {hostname} management IP (required): ").strip()
                config['leaf_mgmt_ips'][hostname] = mgmt_ip
        else:
            config['mgmt_base_ip'] = input("Management IP base [192.168.1]: ").strip() or "192.168.1"
            config['mgmt_start'] = int(input("Management IP start [10]: ").strip() or "10")
        
        return config
    
    def generate_ip_addresses(self, config: Dict) -> Dict:
        """Generate IP addresses based on configuration"""
        ip_scheme = {}
        
        # Parse subnets
        spine_loopback_net = ipaddress.IPv4Network(config['spine_loopback_subnet'])
        leaf_loopback_net = ipaddress.IPv4Network(config['leaf_loopback_subnet'])
        vtep_loopback_net = ipaddress.IPv4Network(config['vtep_loopback_subnet'])
        interconnect_net = ipaddress.IPv4Network(config['interconnect_subnet_base'])
        
        # Generate spine loopbacks
        spine_loopbacks = []
        for i in range(config['spine_count']):
            ip = list(spine_loopback_net.hosts())[i]
            spine_loopbacks.append(f"{ip}/32")
        
        # Generate leaf loopbacks
        leaf_loopbacks = []
        for i in range(config['leaf_count']):
            ip = list(leaf_loopback_net.hosts())[i]
            leaf_loopbacks.append(f"{ip}/32")
        
        # Generate VTEP loopbacks
        vtep_loopbacks = []
        for i in range(config['leaf_count']):
            ip = list(vtep_loopback_net.hosts())[i]
            vtep_loopbacks.append(f"{ip}/32")
        
        # Generate interconnect IPs
        interconnect_ips = {}
        ip_iter = iter(interconnect_net.hosts())
        
        for spine_idx in range(config['spine_count']):
            for leaf_idx in range(config['leaf_count']):
                pair_key = f"spine{spine_idx+1}_leaf{leaf_idx+1}"
                spine_ip = next(ip_iter)
                leaf_ip = next(ip_iter)
                interconnect_ips[pair_key] = {
                    'spine_ip': f"{spine_ip}/30",
                    'leaf_ip': f"{leaf_ip}/30"
                }
        
        # Generate management IPs
        if config.get('mgmt_mode') == "manual":
            mgmt_ips = []
            # Use manually specified IPs
            for i in range(config['spine_count']):
                hostname = f"spine{i+1:02d}"
                mgmt_ips.append(config['spine_mgmt_ips'][hostname])
            for i in range(config['leaf_count']):
                hostname = f"leaf{i+1:02d}"
                mgmt_ips.append(config['leaf_mgmt_ips'][hostname])
        else:
            # Auto-generate management IPs
            mgmt_ips = []
            for i in range(config['spine_count'] + config['leaf_count']):
                mgmt_ip = f"{config['mgmt_base_ip']}.{config['mgmt_start'] + i}"
                mgmt_ips.append(mgmt_ip)
        
        ip_scheme = {
            'spine_loopbacks': spine_loopbacks,
            'leaf_loopbacks': leaf_loopbacks,
            'vtep_loopbacks': vtep_loopbacks,
            'interconnect_ips': interconnect_ips,
            'mgmt_ips': mgmt_ips
        }
        
        return ip_scheme
    
    def generate_spine_config(self, spine_idx: int, config: Dict, ip_scheme: Dict) -> Dict:
        """Generate configuration for a spine switch"""
        hostname = f"spine{spine_idx+1:02d}"
        
        # Get management IP based on mode
        if config.get('mgmt_mode') == "manual":
            mgmt_ip = config['spine_mgmt_ips'][hostname]
        else:
            mgmt_ip = ip_scheme['mgmt_ips'][spine_idx]
        
        loopback0 = ip_scheme['spine_loopbacks'][spine_idx]
        
        spine_interfaces = []
        
        if config.get('interface_mapping_mode') == "2":
            # Use exact interface mapping
            interfaces = config['spine_interfaces'].get(hostname, [])
            for leaf_idx, interface_name in enumerate(interfaces):
                if leaf_idx < config['leaf_count']:
                    pair_key = f"spine{spine_idx+1}_leaf{leaf_idx+1}"
                    interconnect = ip_scheme['interconnect_ips'][pair_key]
                    
                    spine_interfaces.append({
                        'interface': interface_name,
                        'description': f'Link to leaf{leaf_idx+1:02d}',
                        'ip': interconnect['spine_ip']
                    })
        else:
            # Use sequential interface numbering
            interface_num = config['spine_interface_start']
            for leaf_idx in range(config['leaf_count']):
                pair_key = f"spine{spine_idx+1}_leaf{leaf_idx+1}"
                interconnect = ip_scheme['interconnect_ips'][pair_key]
                
                spine_interfaces.append({
                    'interface': f'10GE1/0/{interface_num}',
                    'description': f'Link to leaf{leaf_idx+1:02d}',
                    'ip': interconnect['spine_ip']
                })
                interface_num += 1
        
        return {
            'ansible_host': mgmt_ip,
            'spine_id': spine_idx + 1,
            'loopback0': loopback0,
            'spine_interfaces': spine_interfaces
        }
    
    def generate_leaf_config(self, leaf_idx: int, config: Dict, ip_scheme: Dict) -> Dict:
        hostname = f"leaf{leaf_idx+1:02d}"
        
        # Get management IP based on mode
        if config.get('mgmt_mode') == "manual":
            mgmt_ip = config['leaf_mgmt_ips'][hostname]
        else:
            mgmt_ip = ip_scheme['mgmt_ips'][config['spine_count'] + leaf_idx]
        
        loopback0 = ip_scheme['leaf_loopbacks'][leaf_idx]
        vtep_loopback = ip_scheme['vtep_loopbacks'][leaf_idx]
        
        leaf_interfaces = []
        
        if config.get('interface_mapping_mode') == "2":
            interfaces = config['leaf_interfaces'].get(hostname, [])
            for spine_idx, interface_name in enumerate(interfaces):
                if spine_idx < config['spine_count']:
                    pair_key = f"spine{spine_idx+1}_leaf{leaf_idx+1}"
                    interconnect = ip_scheme['interconnect_ips'][pair_key]
                    
                    leaf_interfaces.append({
                        'interface': interface_name,
                        'description': f'Link to spine{spine_idx+1:02d}',
                        'ip': interconnect['leaf_ip']
                    })
            
            # Add access interface (last one in the list)
            if len(interfaces) > config['spine_count']:
                access_interface = interfaces[config['spine_count']]
                leaf_interfaces.append({
                    'interface': access_interface,
                    'description': 'Server Access',
                    'mode': 'access',
                    'vlan': str(100 + leaf_idx)
                })
        else:
            interface_num = config['leaf_interface_start']
            for spine_idx in range(config['spine_count']):
                pair_key = f"spine{spine_idx+1}_leaf{leaf_idx+1}"
                interconnect = ip_scheme['interconnect_ips'][pair_key]
                
                leaf_interfaces.append({
                    'interface': f'10GE1/0/{interface_num}',
                    'description': f'Link to spine{spine_idx+1:02d}',
                    'ip': interconnect['leaf_ip']
                })
                interface_num += 1
            
            leaf_interfaces.append({
                'interface': f'10GE1/0/{config["leaf_access_interface"]}',
                'description': 'Server Access',
                'mode': 'access',
                'vlan': str(100 + leaf_idx)
            })
        
        return {
            'ansible_host': mgmt_ip,
            'leaf_id': leaf_idx + 1,
            'loopback0': loopback0,
            'vtep_loopback': vtep_loopback,
            'leaf_interfaces': leaf_interfaces
        }
    
    def generate_inventory(self, config: Dict, ip_scheme: Dict) -> Dict:
        """Generate complete inventory"""
        inventory = {
            'all': {
                'vars': {
                    'fabric_name': config['fabric_name'],
                    'asn': config['asn'],
                    'spine_loopback_subnet': config['spine_loopback_subnet'],
                    'leaf_loopback_subnet': config['leaf_loopback_subnet'],
                    'vtep_loopback_subnet': config['vtep_loopback_subnet'],
                    'interconnect_subnet_base': config['interconnect_subnet_base']
                },
                'children': {
                    'spine': {'hosts': {}},
                    'leaf': {'hosts': {}}
                }
            }
        }
        
        # Generate spine configurations
        for i in range(config['spine_count']):
            spine_config = self.generate_spine_config(i, config, ip_scheme)
            hostname = f"spine{i+1:02d}"
            inventory['all']['children']['spine']['hosts'][hostname] = spine_config
        
        # Generate leaf configurations
        for i in range(config['leaf_count']):
            leaf_config = self.generate_leaf_config(i, config, ip_scheme)
            hostname = f"leaf{i+1:02d}"
            inventory['all']['children']['leaf']['hosts'][hostname] = leaf_config
        
        return inventory
    
    def save_inventory(self, inventory: Dict, filename: str = "inventory/hosts.yml"):
        """Save inventory to file"""
        try:
            with open(filename, 'w') as f:
                yaml.dump(inventory, f, default_flow_style=False, indent=2)
            print(f"✅ Inventory saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving inventory: {e}")
    
    def display_summary(self, config: Dict, ip_scheme: Dict):
        """Display configuration summary"""
        print("\n" + "=" * 60)
        print("📊 CONFIGURATION SUMMARY")
        print("=" * 60)
        print(f"Fabric Name: {config['fabric_name']}")
        print(f"BGP ASN: {config['asn']}")
        print(f"Spine Switches: {config['spine_count']}")
        print(f"Leaf Switches: {config['leaf_count']}")
        print()
        print("📡 IP Addressing:")
        print(f"Spine Loopbacks: {config['spine_loopback_subnet']}")
        print(f"Leaf Loopbacks: {config['leaf_loopback_subnet']}")
        print(f"VTEP Loopbacks: {config['vtep_loopback_subnet']}")
        print(f"Interconnect Base: {config['interconnect_subnet_base']}")
        print()
        print("🔌 Interface Mapping:")
        if config.get('interface_mapping_mode') == "2":
            print("  Mode: Exact Match (user-specified interfaces)")
            for hostname, interfaces in config.get('spine_interfaces', {}).items():
                print(f"  {hostname}: {interfaces}")
            for hostname, interfaces in config.get('leaf_interfaces', {}).items():
                print(f"  {hostname}: {interfaces}")
        else:
            print(f"  Mode: Sequential")
            print(f"  Spine Interface Start: 10GE1/0/{config['spine_interface_start']}")
            print(f"  Leaf Interface Start: 10GE1/0/{config['leaf_interface_start']}")
            print(f"  Leaf Access Interface: 10GE1/0/{config['leaf_access_interface']}")
        print()
        print("💻 Management IPs:")
        if config.get('mgmt_mode') == "manual":
            print("  Mode: Manual (user-specified)")
            for hostname, ip in config.get('spine_mgmt_ips', {}).items():
                print(f"  {hostname}: {ip}")
            for hostname, ip in config.get('leaf_mgmt_ips', {}).items():
                print(f"  {hostname}: {ip}")
        else:
            print("  Mode: Auto-generated")
            for i, ip in enumerate(ip_scheme['mgmt_ips']):
                device_type = "Spine" if i < config['spine_count'] else "Leaf"
                device_num = (i if i < config['spine_count'] else i - config['spine_count']) + 1
                hostname = f"{device_type.lower()}{device_num:02d}"
                print(f"  {hostname}: {ip}")
        
        print("\n" + "=" * 60)
    
    def run(self):
        """Main execution"""
        try:
            # Get user configuration
            config = self.get_user_input()
            
            # Generate IP addresses
            print("\n🔧 Generating IP addresses...")
            ip_scheme = self.generate_ip_addresses(config)
            
            # Generate inventory
            print("📋 Generating inventory...")
            inventory = self.generate_inventory(config, ip_scheme)
            
            # Display summary
            self.display_summary(config, ip_scheme)
            
            # Confirm and save
            confirm = input("\n💾 Save inventory to inventory/hosts.yml? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                self.save_inventory(inventory)
                print("\n🎉 Inventory generation completed!")
                print("Next steps:")
                print("1. Review the generated inventory file")
                print("2. Configure credentials: ansible-vault edit inventory/group_vars/vault.yml")
                print("3. Run fabric deployment: python3 interactive_fabric.py")
            else:
                print("❌ Inventory not saved.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    generator = InventoryGenerator()
    generator.run()
