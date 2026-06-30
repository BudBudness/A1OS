#!/usr/bin/env python3
import sys
import argparse
from control_plane.control_plane import ControlPlane
from system.plugin_manager import PluginLifecycleManager

def main():
    parser = argparse.ArgumentParser(description="A1OS Kernel Orchestration Terminal Engine (v1.0)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # a1os new-plugin <id>
    new_parser = subparsers.add_parser("new-plugin", help="Scaffold an isolated plugin package layout")
    new_parser.add_argument("name", type=str, help="Unique string identifier for the target package")

    # a1os install <id>
    install_parser = subparsers.add_parser("install", help="Admit, cryptographically sign, and mount a plugin")
    install_parser.add_argument("name", type=str, help="Target package directory string name")

    # a1os upgrade <id>
    upgrade_parser = subparsers.add_parser("upgrade", help="Re-sign, validate, and bump an existing plugin package")
    upgrade_parser.add_argument("name", type=str, help="Target package directory string name")

    # a1os uninstall <id>
    uninstall_parser = subparsers.add_parser("uninstall", help="Revoke trust keys and wipe plugin directory safely")
    uninstall_parser.add_argument("name", type=str, help="Target package directory string name")

    args = parser.parse_args()
    
    cp = ControlPlane(secret_key="FORT_KNOX_KEY")
    mgr = PluginLifecycleManager(control_plane=cp)

    if args.command == "new-plugin":
        mgr.scaffold_plugin(args.name)
    elif args.command == "install":
        mgr.formal_install(args.name)
    elif args.command == "upgrade":
        mgr.upgrade_plugin(args.name)
    elif args.command == "uninstall":
        mgr.uninstall_plugin(args.name)

if __name__ == "__main__":
    main()
