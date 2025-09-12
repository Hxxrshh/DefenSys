# src/core/scanner.py

import importlib
import pkgutil
import os
from core.reporter import Reporter

class VulnScanner:
    """
    Core scanning engine that loads vulnerability detection plugins dynamically
    and runs them against the given target.
    """

    def __init__(self, target_url, plugins_path="src/core/plugins"):
        self.target = target_url
        self.plugins_path = plugins_path
        self.reporter = Reporter()
        self.plugins = self.load_plugins()

    def load_plugins(self):
        plugins = {}
        package = "core.plugins"
        package_path = os.path.join(os.path.dirname(__file__), "plugins")
        for _, module_name, _ in pkgutil.iter_modules([package_path]):
            module = importlib.import_module(f"{package}.{module_name}")
            if hasattr(module, "Plugin"):
                plugins[module_name] = module.Plugin()
        return plugins

    def run(self):
        findings = []
        for name, plugin in self.plugins.items():
            try:
                result = plugin.run(self.target)
                if result:
                    findings.append(result)
                    # Log finding into reporter (alerts + DB)
                    self.reporter.log_finding(
                        self.target,
                        result["vulnerability"],
                        result["severity"],
                        result["evidence"],
                        result["remediation"]
                    )
            except Exception as e:
                print(f"[!] Error running plugin {name}: {e}")
        return findings


# Example usage
if __name__ == "__main__":
    scanner = VulnScanner("http://localhost:3000")
    results = scanner.run()
    if not results:
        print("[✔] No vulnerabilities detected.")
    else:
        for r in results:
            print(f"[!] {r['vulnerability']} - {r['severity']}")
            print(f"    Evidence: {r['evidence']}")
            print(f"    Remediation: {r['remediation']}\n")
