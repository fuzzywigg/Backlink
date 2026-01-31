"""
Security Bee
------------
Responsible for Defensive OSINT, Code Auditing, and "Immunity" against malware/tracking.
Specialized in scanning proprietary IoT dumps (Watch OS) and Android APKs.
"""

import os

from hive.bees.base_bee import BaseBee


class SecurityBee(BaseBee):
    """
    The Security Bee - Hive Immunity System.
    """

    def __init__(self, hive_path, gateway=None):
        super().__init__(hive_path, gateway)

        # Signatures based on 'Reverse Engineering Cookbook'
        self.signatures = {
            "unidbg": [b"unidbg", b"com.github.unidbg"],
            "frida": [b"frida-agent", b"frida-gadget"],
            "tracking_hosts": [b"ad.xiaomi.com", b"tracking", b"analytics"],
            "suspicious_permissions": ["READ_SMS", "RECORD_AUDIO", "ACCESS_FINE_LOCATION"]
        }

    def work(self, task):
        instruction = task.get("instruction", "").lower()
        args = task.get("args", {})
        target_path = args.get("path")

        self.log(f"Security Bee scanning: {target_path} | Instruction: {instruction}")

        if not target_path or not os.path.exists(target_path):
            return {"success": False, "reason": "Invalid or missing target path"}

        if "manifest" in instruction:
            return self.scan_android_manifest(target_path)
        elif "unidbg" in instruction:
            return self.detect_unidbg_signatures(target_path)

        if os.path.isdir(target_path):
            return self.scan_directory(target_path)
        else:
            return self.scan_file(target_path)

    def scan_directory(self, directory):
        """
        Recursively scan a directory for signatures.
        """
        results = {
            "files_scanned": 0,
            "threats_found": [],
            "suspicious_files": []
        }

        for root, _dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                results["files_scanned"] += 1

                # Heuristic checks
                if file.endswith(".so") or file.endswith(".dll") or file.endswith(".apk") or file.endswith(".xml"):
                    scan_res = self.scan_file(filepath)
                    if scan_res["threats"]:
                        results["threats_found"].extend(scan_res["threats"])
                        results["suspicious_files"].append(filepath)

        return {"success": True, "report": results}

    def scan_file(self, filepath):
        """
        Scan a binary file for string signatures.
        """
        threats = []
        try:
            with open(filepath, "rb") as f:
                content = f.read()

                # Check General Signatures
                for sig_name, patterns in self.signatures.items():
                    # Skip permission checks here, those are for manifest
                    if sig_name == "suspicious_permissions":
                         continue

                    for pattern in patterns:
                        if pattern in content:
                            threats.append(f"{sig_name}_detected")

                # Check for Permissions (Binary String Search)
                # Many AXML files keep permission strings intact
                for perm in self.signatures["suspicious_permissions"]:
                    if perm.encode() in content:
                        threats.append(f"permission_{perm}")

        except Exception as e:
            self.log(f"Error scanning {filepath}: {e}", level="error")

        return {"success": True, "threats": list(set(threats))}

    def scan_android_manifest(self, filepath):
        """
        Specifically scans AndroidManifest.xml for permissions and entry poins.
        """
        self.log(f"Scanning Manifest: {filepath}")
        results = {"permissions": [], "risks": []}

        try:
            with open(filepath, "rb") as f:
                content = f.read()

            for perm in self.signatures["suspicious_permissions"]:
                if perm.encode() in content:
                    results["permissions"].append(perm)
                    results["risks"].append(f"High risk permission: {perm}")

            return {"success": True, "manifest_analysis": results}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def detect_unidbg_signatures(self, filepath):
        """
        Deep scan for UniDBG emulation artifacts.
        """
        unidbg_sigs = [
            b"com.github.unidbg",
            b"unidbg-android",
            b"libc.so", # Often hooked/emulated
            b"/data/local/tmp"
        ]

        detected = []
        try:
            with open(filepath, "rb") as f:
                content = f.read()

            for sig in unidbg_sigs:
                if sig in content:
                    detected.append(sig.decode('utf-8', errors='ignore'))

            if detected:
                return {"success": True, "unidbg_detected": True, "signatures": detected}
            return {"success": True, "unidbg_detected": False}

        except Exception as e:
            return {"success": False, "error": str(e)}
