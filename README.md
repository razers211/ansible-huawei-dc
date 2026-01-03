# Huawei CE6800 Spine-Leaf Fabric Manager

An interactive Ansible-based solution for deploying and managing spine-leaf architecture on Huawei CE6800 switches using `ansible.netcommon.network_cli`.

## 🏗️ Architecture Overview

This solution provides a complete fabric management system for:
- **Spine Switches**: Core routing and BGP route reflection
- **Leaf Switches**: Access layer with VXLAN/EVPN overlay
- **Tenant Networks**: Multi-tenant isolation with VRFs
- **Dynamic Scaling**: Add spines/leafs to existing fabric

## 📋 Features

### Core Capabilities
- ✅ Complete fabric deployment with OSPF underlay and BGP/EVPN overlay
- ✅ VXLAN/EVPN multi-tenant support
- ✅ Interactive configuration with validation
- ✅ Automated backup and rollback
- ✅ Fabric expansion (add spines/leafs)
- ✅ Tenant network provisioning
- ✅ Comprehensive verification and reporting

### Interactive Management
- 🎯 Menu-driven deployment wizard
- 🔍 Pre-deployment validation
- 📊 Real-time progress tracking
- 📋 Automated reporting
- 🛡️ Safety checks and confirmations

## 🚀 Quick Start

### Prerequisites
```bash
# Install Ansible
pip install ansible>=4.0

# Install Python dependencies
pip install paramiko jinja2
```

### Initial Setup
```bash
# 1. Clone or download the project
# 2. Install Ansible collections
ansible-galaxy collection install -r requirements.yml

# 3. Configure credentials
ansible-vault create inventory/group_vars/vault.yml
# Add your passwords:
# vault_admin_password: "your_admin_password"
# vault_enable_password: "your_enable_password"
# vault_bgp_password: "your_bgp_password"

# 4. Update inventory
vim inventory/hosts.yml
# Configure your switch IPs and interfaces
```

### Interactive Deployment
```bash
# Launch the interactive fabric manager
python interactive_fabric.py

# Or run playbooks directly
ansible-playbook deploy_fabric.yml -i inventory/hosts.yml --ask-vault-pass
```

## 📁 Project Structure

```
├── ansible.cfg                 # Ansible configuration
├── requirements.yml           # Collection dependencies
├── interactive_fabric.py      # Interactive management script
├── deploy_fabric.yml         # Main fabric deployment
├── deploy_tenants.yml         # Tenant network deployment
├── add_leaf.yml              # Add leaf switch
├── add_spine.yml             # Add spine switch
├── inventory/
│   ├── hosts.yml             # Switch inventory
│   └── group_vars/
│       ├── all.yml           # Global variables
│       └── vault.yml         # Encrypted credentials
├── tasks/
│   ├── basic_system.yml      # System configuration
│   ├── interfaces.yml        # Interface configuration
│   ├── underlay_routing.yml  # OSPF configuration
│   ├── bgp_overlay.yml       # BGP/EVPN configuration
│   ├── vxlan.yml            # VXLAN configuration
│   └── *_new_*.yml          # Device addition tasks
└── templates/
    ├── fabric_report.j2      # Fabric deployment report
    ├── tenant_report.j2      # Tenant deployment report
    ├── leaf_addition_report.j2
    └── spine_addition_report.j2
```

## 🎯 Usage Scenarios

### 1. Complete Fabric Deployment
```bash
python interactive_fabric.py
# Select option 1: Deploy Complete Fabric
```

### 2. Deploy Tenant Networks
```bash
python interactive_fabric.py
# Select option 2: Deploy Tenant Networks
```

### 3. Add New Leaf Switch
```bash
python interactive_fabric.py
# Select option 3: Add New Leaf Switch
# Provide: hostname, IP, leaf ID, loopback IPs, connected spines
```

### 4. Add New Spine Switch
```bash
python interactive_fabric.py
# Select option 4: Add New Spine Switch
# Provide: hostname, IP, spine ID, loopback IP, connected leaves
```

## 🔧 Configuration Details

### Network Design
- **Underlay**: OSPF Area 0 with point-to-point links
- **Overlay**: BGP EVPN with VXLAN
- **VXLAN**: VNI range 10000-19999
- **VLANs**: 1000-1999 for tenant networks
- **VRFs**: 10-99 for tenant isolation

### IP Addressing Scheme
- **Spine Loopbacks**: 10.255.1.0/24
- **Leaf Loopbacks**: 10.255.2.0/24
- **VTEP Loopbacks**: 10.255.3.0/24
- **Point-to-Point Links**: 10.1.x.x/30

### BGP Configuration
- **ASN**: 65000 (configurable)
- **Route Reflection**: Spines act as reflectors
- **EVPN**: L2VPN and IRB advertisement
- **Timers**: 60s keepalive, 180s hold

## 🛡️ Safety Features

### Pre-deployment Checks
- ✅ Ansible connectivity verification
- ✅ Credential validation
- ✅ Inventory syntax checking
- ✅ Required file presence

### Configuration Safety
- ✅ Automatic backup before changes
- ✅ Confirmation prompts for destructive actions
- ✅ Rollback capability
- ✅ Configuration validation

### Verification
- ✅ Interface status checking
- ✅ BGP peer validation
- ✅ OSPF adjacency verification
- ✅ VXLAN tunnel status

## 📊 Monitoring & Verification

### Key Commands
```bash
# Interface status
display ip interface brief

# BGP peers
display bgp peer
display bgp l2vpn evpn routing-table

# OSPF neighbors
display ospf peer

# VXLAN status
display vxlan tunnel
display bridge-domain

# VRF information
display vpn-instance <vrf-name>
```

### Automated Reports
- Fabric deployment reports
- Tenant configuration reports
- Device addition reports
- Backup configuration files

## 🔍 Troubleshooting

### Common Issues

#### 1. Connection Failures
```bash
# Check connectivity
ansible all -i inventory/hosts.yml -m ping

# Verify credentials
ansible-vault view inventory/group_vars/vault.yml
```

#### 2. BGP Session Issues
```bash
# Check BGP status
display bgp peer

# Verify loopback reachability
ping <loopback-ip>

# Check BGP configuration
display current-configuration section bgp
```

#### 3. VXLAN Problems
```bash
# Check VXLAN configuration
display vxlan tunnel
display bridge-domain

# Verify VTEP source
display current-configuration section nve
```

#### 4. OSPF Issues
```bash
# Check OSPF neighbors
display ospf peer

# Verify OSPF configuration
display current-configuration section ospf
```

## 📚 Advanced Configuration

### Custom IP Schemes
Edit `inventory/group_vars/all.yml` to modify:
- IP addressing ranges
- VLAN/VNI ranges
- BGP ASN
- OSPF area configuration

### Interface Customization
Update `inventory/hosts.yml` for:
- Interface naming
- Port speeds
- Link descriptions
- Access port configurations

### Tenant Templates
Modify `deploy_tenants.yml` for:
- Custom VRF naming
- VLAN assignment strategies
- Subnet allocation
- Gateway configurations

## 🔄 Workflow Examples

### New Fabric Deployment
1. Configure inventory with switch details
2. Set up encrypted credentials
3. Run interactive fabric manager
4. Select "Deploy Complete Fabric"
5. Verify deployment with reports

### Adding Capacity
1. Run interactive fabric manager
2. Select "Add New Leaf" or "Add New Spine"
3. Provide device details
4. Confirm connectivity
5. Update monitoring

### Tenant Onboarding
1. Run interactive fabric manager
2. Select "Deploy Tenant Networks"
3. Provide tenant details
4. Configure access ports
5. Verify tenant isolation

## 📞 Support

### Documentation
- Ansible Network Automation Guide
- Huawei CE6800 Configuration Guide
- VXLAN/EVPN Best Practices

### Community Resources
- Ansible Network Community
- Huawei Enterprise Support
- Network Automation Forums

## 📄 License

This project is provided as-is for educational and production use. Please review and test thoroughly before deployment in production environments.

## 🔄 Version History

- **v1.0**: Initial release with complete fabric management
- **v1.1**: Added interactive management script
- **v1.2**: Enhanced reporting and verification
- **v1.3**: Improved safety checks and rollback

---

**⚠️ Important**: Always test configurations in a lab environment before deploying to production. Ensure you have proper backups and rollback procedures in place.
