#!/bin/bash

# Huawei CE6800 Spine-Leaf Fabric Setup Script
# This script prepares the environment for fabric deployment

set -e

echo "🌐 Huawei CE6800 Spine-Leaf Fabric Setup"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

# Install Ansible
echo "📦 Installing Ansible..."
pip3 install ansible>=4.0

# Install required Python packages
echo "📦 Installing Python dependencies..."
pip3 install paramiko jinja2 netaddr

# Install Ansible collections
echo "📦 Installing Ansible collections..."
ansible-galaxy collection install -r requirements.yml

# Create backup directory
echo "📁 Creating backup directory..."
mkdir -p backups

# Set up vault
echo "🔐 Setting up Ansible Vault..."
if [ ! -f "inventory/group_vars/vault.yml" ]; then
    echo "Creating vault file with default template..."
    cp inventory/group_vars/vault.yml inventory/group_vars/vault.yml.bak
fi

echo "🔐 Please configure your credentials:"
echo "   Run: ansible-vault edit inventory/group_vars/vault.yml"
echo "   Add your admin, enable, and BGP passwords"

# Make interactive script executable
echo "🔧 Making interactive script executable..."
chmod +x interactive_fabric.py

# Verify installation
echo "🔍 Verifying installation..."
if command -v ansible &> /dev/null; then
    echo "✅ Ansible installed: $(ansible --version | head -1)"
else
    echo "❌ Ansible installation failed"
    exit 1
fi

# Check if required files exist
required_files=(
    "ansible.cfg"
    "requirements.yml"
    "inventory/hosts.yml"
    "deploy_fabric.yml"
    "deploy_tenants.yml"
    "add_leaf.yml"
    "add_spine.yml"
    "interactive_fabric.py"
)

echo "📋 Checking required files..."
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure your inventory: vim inventory/hosts.yml"
echo "2. Set up credentials: ansible-vault edit inventory/group_vars/vault.yml"
echo "3. Run the interactive manager: python3 interactive_fabric.py"
echo ""
echo "For detailed instructions, see README.md"
