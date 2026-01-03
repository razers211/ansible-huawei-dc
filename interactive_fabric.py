#!/usr/bin/env python3
"""
Interactive Ansible Fabric Deployment Script
For Huawei CE6800 Spine-Leaf Architecture
"""

import os
import sys
import subprocess
import json
from typing import Dict, List, Optional

class FabricManager:
    def __init__(self):
        self.ansible_cmd = "ansible-playbook"
        self.inventory_file = "inventory/hosts.yml"
        self.vault_file = "inventory/group_vars/vault.yml"
        
    def run_command(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result"""
        try:
            result = subprocess.run(cmd, check=check, capture_output=True, text=True)
            return result
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {' '.join(cmd)}")
            print(f"Error: {e.stderr}")
            raise
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check if Ansible is installed
        try:
            self.run_command(["ansible", "--version"])
            print("✅ Ansible is installed")
        except subprocess.CalledProcessError:
            print("❌ Ansible is not installed. Please install Ansible first.")
            return False
        
        # Check if required files exist
        required_files = [
            "ansible.cfg",
            "requirements.yml",
            self.inventory_file,
            "deploy_fabric.yml",
            "deploy_tenants.yml",
            "add_leaf.yml",
            "add_spine.yml"
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                print(f"❌ Required file missing: {file}")
                return False
        
        print("✅ All required files present")
        
        # Check if vault is encrypted
        if os.path.exists(self.vault_file):
            try:
                result = self.run_command(["ansible-vault", "view", self.vault_file], check=False)
                if result.returncode != 0:
                    print("⚠️  Vault file exists but may not be properly encrypted")
                    print("   Run: ansible-vault encrypt inventory/group_vars/vault.yml")
                else:
                    print("✅ Vault file is accessible")
            except:
                print("⚠️  Could not verify vault file status")
        
        return True
    
    def generate_inventory(self) -> bool:
        """Generate inventory interactively"""
        print("📋 Generating inventory...")
        try:
            result = self.run_command(["python3", "generate_inventory.py"])
            print("✅ Inventory generation completed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to generate inventory")
            return False
    
    def install_collections(self) -> bool:
        """Install required Ansible collections"""
        print("📦 Installing Ansible collections...")
        try:
            self.run_command(["ansible-galaxy", "collection", "install", "-r", "requirements.yml"])
            print("✅ Collections installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install collections")
            return False
    
    def deploy_fabric(self) -> bool:
        """Deploy the complete spine-leaf fabric"""
        print("🚀 Deploying spine-leaf fabric...")
        try:
            cmd = [self.ansible_cmd, "deploy_fabric.yml", "-i", self.inventory_file]
            if self.ask_yes_no("Use vault for credentials?"):
                cmd.extend(["--ask-vault-pass"])
            
            result = self.run_command(cmd)
            print("✅ Fabric deployment completed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Fabric deployment failed")
            return False
    
    def deploy_tenants(self) -> bool:
        """Deploy tenant networks"""
        print("🏢 Deploying tenant networks...")
        try:
            cmd = [self.ansible_cmd, "deploy_tenants.yml", "-i", self.inventory_file]
            if self.ask_yes_no("Use vault for credentials?"):
                cmd.extend(["--ask-vault-pass"])
            
            result = self.run_command(cmd)
            print("✅ Tenant deployment completed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Tenant deployment failed")
            return False
    
    def add_leaf(self) -> bool:
        """Add a new leaf switch"""
        print("🍃 Adding new leaf switch...")
        try:
            cmd = [self.ansible_cmd, "add_leaf.yml", "-i", self.inventory_file]
            if self.ask_yes_no("Use vault for credentials?"):
                cmd.extend(["--ask-vault-pass"])
            
            result = self.run_command(cmd)
            print("✅ Leaf switch added successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to add leaf switch")
            return False
    
    def add_spine(self) -> bool:
        """Add a new spine switch"""
        print("🦴 Adding new spine switch...")
        try:
            cmd = [self.ansible_cmd, "add_spine.yml", "-i", self.inventory_file]
            if self.ask_yes_no("Use vault for credentials?"):
                cmd.extend(["--ask-vault-pass"])
            
            result = self.run_command(cmd)
            print("✅ Spine switch added successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to add spine switch")
            return False
    
    def verify_fabric(self) -> bool:
        """Verify fabric connectivity and configuration"""
        print("🔍 Verifying fabric...")
        try:
            cmd = [self.ansible_cmd, "-i", self.inventory_file, "all", "-m", "huawei_vrp_command", 
                   "-a", "commands='display ip interface brief'"]
            if self.ask_yes_no("Use vault for credentials?"):
                cmd.extend(["--ask-vault-pass"])
            
            result = self.run_command(cmd)
            print("✅ Fabric verification completed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Fabric verification failed")
            return False
    
    def show_inventory(self) -> None:
        """Display current inventory"""
        print("📋 Current Inventory:")
        try:
            with open(self.inventory_file, 'r') as f:
                print(f.read())
        except FileNotFoundError:
            print("❌ Inventory file not found")
    
    def ask_yes_no(self, question: str) -> bool:
        """Ask a yes/no question"""
        while True:
            response = input(f"{question} (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    def show_menu(self) -> None:
        """Display the main menu"""
        print("\n" + "="*60)
        print("🌐 HUAWEI CE6800 SPINE-LEAF FABRIC MANAGER")
        print("="*60)
        print("1. 📋 Generate Inventory")
        print("2. 🚀 Deploy Complete Fabric")
        print("3. 🏢 Deploy Tenant Networks")
        print("4. 🍃 Add New Leaf Switch")
        print("5. 🦴 Add New Spine Switch")
        print("6. 🔍 Verify Fabric")
        print("7. 📋 Show Inventory")
        print("8. 📦 Install Collections")
        print("9. ❌ Exit")
        print("-"*60)
    
    def run(self) -> None:
        """Main execution loop"""
        print("🌐 Welcome to Huawei CE6800 Spine-Leaf Fabric Manager")
        
        if not self.check_prerequisites():
            print("\n❌ Prerequisites not met. Please resolve issues and try again.")
            return
        
        while True:
            self.show_menu()
            choice = input("Select an option (1-9): ").strip()
            
            if choice == "1":
                self.generate_inventory()
            elif choice == "2":
                if self.ask_yes_no("This will deploy a complete fabric. Continue?"):
                    self.deploy_fabric()
            elif choice == "3":
                self.deploy_tenants()
            elif choice == "4":
                self.add_leaf()
            elif choice == "5":
                self.add_spine()
            elif choice == "6":
                self.verify_fabric()
            elif choice == "7":
                self.show_inventory()
            elif choice == "8":
                self.install_collections()
            elif choice == "9":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-9.")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        manager = FabricManager()
        manager.run()
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
