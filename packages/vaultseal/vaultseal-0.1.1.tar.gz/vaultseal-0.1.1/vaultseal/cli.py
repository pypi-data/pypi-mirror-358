import argparse
import getpass
from vaultseal.vault import (
    add_secret,
    get_secret,
    delete_secret,
    list_secrets,
    load_vault,
    save_vault
)

try:
    import pyperclip
except ImportError:
    pyperclip = None

def main():
    parser = argparse.ArgumentParser(
        description="VaultSeal: Encrypted local secret storage",
        epilog="Commands:\n"
               "  add <name> <value>       Add a new secret\n"
               "  get <name> [--copy]      Retrieve a secret\n"
               "  list                     List stored secret names\n"
               "  delete <name>            Delete a secret\n"
               "  change-password          Change your master password\n",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_cmd = subparsers.add_parser("add", help="Add a new secret")
    add_cmd.add_argument("name")
    add_cmd.add_argument("value")

    get_cmd = subparsers.add_parser("get", help="Retrieve a secret")
    get_cmd.add_argument("name")
    get_cmd.add_argument("--copy", action="store_true")

    subparsers.add_parser("list", help="List stored secret names")

    del_cmd = subparsers.add_parser("delete", help="Delete a secret")
    del_cmd.add_argument("name")

    subparsers.add_parser("change-password", help="Change your master password")

    args = parser.parse_args()
    command = args.command

    if command == "add":
        password = getpass.getpass("🔑 Enter master password: ")
        add_secret(args.name, args.value, password)
        print(f"✅ Secret '{args.name}' added.")

    elif command == "get":
        password = getpass.getpass("🔑 Enter master password: ")
        value = get_secret(args.name, password)
        if value:
            if args.copy and pyperclip:
                pyperclip.copy(value)
                print("📋 Secret copied to clipboard.")
            else:
                print(f"🔓 {args.name}: {value}")
        else:
            print("❌ Secret not found or wrong password.")

    elif command == "list":
        password = getpass.getpass("🔑 Enter master password: ")
        secrets = list_secrets(password)
        if not secrets:
            print("📭 Vault is empty or wrong password.")
        else:
            print("🗂️ Stored secrets:")
            for key in secrets:
                print(" -", key)

    elif command == "delete":
        password = getpass.getpass("🔑 Enter master password: ")
        if delete_secret(args.name, password):
            print(f"🗑️ Secret '{args.name}' deleted.")
        else:
            print("❌ Secret not found or wrong password.")

    elif command == "change-password":
        old_pwd = getpass.getpass("🔑 Current password: ")
        vault = load_vault(old_pwd)
        if not vault:
            print("❌ Wrong password or empty vault.")
            return
        new_pwd = getpass.getpass("🔐 New password: ")
        confirm = getpass.getpass("🔐 Confirm new password: ")
        if new_pwd != confirm:
            print("❌ Passwords do not match.")
            return
        save_vault(vault, new_pwd)
        print("✅ Master password updated.")
