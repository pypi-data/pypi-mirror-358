import argparse
import asyncio
import csv
import json
import os
import shutil
import sys
import textwrap

from euvdmapper.euvd_alert import run_alert_mode
from euvdmapper.fetch_api import (
    fetch_euvd_entries,
    lookup_cve,
    lookup_euvd,
    fetch_exploited_vulnerabilities,
    fetch_latest_vulnerabilities,
    fetch_critical_vulnerabilities,
    fetch_advisory
)


def fit_ascii_to_terminal(art_text):
    term_width = shutil.get_terminal_size((80, 20)).columns
    fitted_lines = []
    for line in art_text.splitlines():
        if len(line) > term_width:
            fitted_lines.append(line[:term_width])
        else:
            fitted_lines.append(line)
    return "\n".join(fitted_lines)


def flatten_entry(entry):
    return {
        "EUVD_ID": entry.get("id", ""),
        "Alt_IDs": entry.get("aliases", "").replace("\n", ", "),
        "Exploitation": entry.get("exploitation", "Not available"),
        "CVSS": f'v{entry.get("baseScoreVersion", "")}: {entry.get("baseScore", "")}'
                if entry.get("baseScore") else "",
        "EPSS": entry.get("epss", ""),
        "Product": ", ".join(
            p["product"]["name"]
            for p in entry.get("enisaIdProduct", [])
            if "product" in p
        ),
        "Vendor": ", ".join(
            v["vendor"]["name"]
            for v in entry.get("enisaIdVendor", [])
            if "vendor" in v
        ),
        "Changed": entry.get("dateUpdated", ""),
        "Summary": entry.get("description", ""),
        "Version": ", ".join(
            p.get("product_version", "")
            for p in entry.get("enisaIdProduct", [])
            if "product_version" in p
        ),
        "Published": entry.get("datePublished", ""),
        "Updated": entry.get("dateUpdated", ""),
        "References": entry.get("references", "").replace("\n", ", ")
    }


def generate_html_report(data, output_file):
    """
    Generates an HTML report.

    Args:
        data (list): list of vulnerability entries.
        output_file (str): The path to the output HTML file.
    """
    html = """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>EUVD Vulnerability Report</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            h1 { font-size: 24px; }
            input, select, button {
                margin: 5px;
                padding: 8px;
                font-size: 14px;
            }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; vertical-align: top; }
            th { background-color: #f2f2f2; }
            td { font-size: 12px; }
            .low-risk { background-color: #d4edda; }
            .medium-risk { background-color: #fff3cd; }
            .high-risk { background-color: #ffe5b4; }
            .critical-risk { background-color: #f8d7da; }
        </style>
        <script>
            function filterTable(filterText = "") {
                let vendor = document.getElementById("vendorFilter").value.toLowerCase();
                let product = document.getElementById("productFilter").value.toLowerCase();
                let cvssRange = document.getElementById("cvssFilter").value;
                let rows = document.querySelectorAll("table tbody tr");
                rows.forEach(function(row) {
                    let text = row.textContent.toLowerCase();
                    let vendorText = row.cells[6].textContent.toLowerCase();
                    let productText = row.cells[5].textContent.toLowerCase();
                    let cvssScore = parseFloat(row.cells[3].textContent.split(":").pop()) || 0;
                    let cvssMatch = (
                        (cvssRange === "all") ||
                        (cvssRange === "critical" && cvssScore >= 9.0) ||
                        (cvssRange === "high" && cvssScore >= 8.0 && cvssScore < 9.0) ||
                        (cvssRange === "medium" && cvssScore >= 5.0 && cvssScore < 8.0) ||
                        (cvssRange === "low" && cvssScore < 5.0)
                    );
                    let match = text.includes(filterText.toLowerCase()) &&
                                vendorText.includes(vendor) &&
                                productText.includes(product) &&
                                cvssMatch;
                    row.style.display = match ? "" : "none";
                });
            }
            function exportPDF() { window.print(); }
        </script>
    </head>
    <body>
        <h1>EUVD Vulnerability Report</h1>
        <input type="text" id="searchInput" onkeyup="filterTable(this.value)" placeholder="Search in report...">
        <select id="vendorFilter" onchange="filterTable()">
            <option value="">Filter by Vendor</option>
        </select>
        <select id="productFilter" onchange="filterTable()">
            <option value="">Filter by Product</option>
        </select>
        <select id="cvssFilter" onchange="filterTable()">
            <option value="all">All CVSS</option>
            <option value="critical">Critical (9.0+)</option>
            <option value="high">High (8.0 - 8.9)</option>
            <option value="medium">Medium (5.0 - 7.9)</option>
            <option value="low">Low (&lt; 5.0)</option>
        </select>
        <button onclick="exportPDF()">Export PDF</button>
        <table>
            <thead>
                <tr>
                    <th>EUVD_ID</th><th>Alt_IDs</th><th>Exploitation</th><th>CVSS</th><th>EPSS</th><th>Product</th>
                    <th>Vendor</th><th>Changed</th><th>Summary</th><th>Version</th>
                    <th>Published</th><th>Updated</th><th>References</th>
                </tr>
            </thead>
            <tbody>
    """
    vendor_set = set()
    product_set = set()
    for entry in data:
        euvd_id = entry.get("id", "")
        alt_ids = entry.get("aliases", "").replace("\n", ", ")
        exploitation = entry.get("exploitation", "Not available")
        cvss_score = entry.get("baseScore")
        epss = entry.get("epss", "")
        cvss = f'v{entry.get("baseScoreVersion", "")}: {cvss_score}' if cvss_score else ""
        summary = entry.get("description", "")
        published = entry.get("datePublished", "")
        updated = entry.get("dateUpdated", "")
        references = entry.get("references", "").replace("\n", ", ")
        products = ", ".join(
            p["product"]["name"] for p in entry.get("enisaIdProduct", []) if "product" in p
        )
        versions = ", ".join(
            p.get("product_version", "") for p in entry.get("enisaIdProduct", []) if "product_version" in p
        )
        vendors = ", ".join(
            v["vendor"]["name"] for v in entry.get("enisaIdVendor", []) if "vendor" in v
        )
        vendor_set.update(vendors.split(", "))
        product_set.update(products.split(", "))
        row_class = ""
        if cvss_score is not None:
            try:
                score = float(cvss_score)
                if score <= 3.9:
                    row_class = "low-risk"
                elif score <= 6.9:
                    row_class = "medium-risk"
                elif score <= 8.9:
                    row_class = "high-risk"
                else:
                    row_class = "critical-risk"
            except ValueError:
                pass
        html += f"""
        <tr class="{row_class}">
            <td>{euvd_id}</td><td>{alt_ids}</td><td>{exploitation}</td><td>{cvss}</td>
            <td>{epss}</td><td>{products}</td><td>{vendors}</td><td>{updated}</td>
            <td>{summary}</td><td>{versions}</td><td>{published}</td>
            <td>{updated}</td><td>{references}</td>
        </tr>
        """
    html += """
            </tbody>
        </table>
        <script>
            let vendorFilter = document.getElementById("vendorFilter");
            let productFilter = document.getElementById("productFilter");
    """
    for vendor in sorted(vendor_set):
        html += f'vendorFilter.innerHTML += `<option value="{vendor}">{vendor}</option>`;\n'
    for product in sorted(product_set):
        html += f'productFilter.innerHTML += `<option value="{product}">{product}</option>`;\n'
    html += """
        </script>
    </body>
    </html>
    """
    # ensure the output directory exists (or use cwd if none specified)
    out_dir = os.path.dirname(output_file) or "."
    os.makedirs(out_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    epilog_text = textwrap.dedent("""
        Examples:
          euvdmapper --keyword fortinet
              Searches for vulnerabilities by keyword and prints the results.

          euvdmapper --keyword fortinet --no-banner | jq .
              Searches without banner and pipes raw JSON to jq.

          euvdmapper --keyword fortinet --output fortinet.csv
              Exports results to CSV in the current directory.

          euvdmapper --keyword fortinet --output reports/fortinet.html
              Generates an HTML report under 'reports/'.

          euvdmapper --lookup-cve CVE-2024-1234
              Looks up details by CVE ID.

          euvdmapper --lookup-euvd EUVD-2024-5678
              Looks up by EUVD ID.

          euvdmapper --show-exploited --output exploited.csv
              Displays the latest exploited vulnerabilities and generates an CSV report [.json or .csv] (API cap: max 8 records).

          euvdmapper --last --output last.json
              Fetches the latest 8 vulnerabilities to last.json [.json or .csv] (API cap: max 8 records).

          euvdmapper --critical --output critical.csv
              Fetches the latest 8 critical vulnerabilities to critical.csv [.json or .csv] (API cap: max 8 records).

          euvdmapper --enisa-id EUVD-2025-XXXX
              Fetches details for the given ENISA ID.

          euvdmapper --advisory-id cisco-sa-example-XXXX
              Fetches advisory details by ID.

          euvdmapper --advisory-id cisco-sa-example-XXXX | jq '.description'
              Prints only the advisory’s main description.

          euvdmapper --advisory-id cisco-sa-example-XXXX | jq '.enisaIdAdvisories'
              Lists all EUVD entries linked to this advisory.

          euvdmapper --advisory-id cisco-sa-example-XXXX | jq '.vulnerabilityAdvisory'
              Lists all CVE details linked to this advisory.

          euvdmapper --input watchlist.yaml --alerts
              Uses a YAML watchlist to generate alert reports (CSV + HTML).
    """)


    parser = argparse.ArgumentParser(
        prog="euvdmapper",
        description="EUVD Mapper - ENISA EUVD Data Retriever and Formatter",
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--keyword", help="Search keyword (text param)")
    parser.add_argument("--vendor", help="Filter by vendor (exact match)")
    parser.add_argument("--product", help="Filter by product (exact match)")
    parser.add_argument("--output", help="Output file: .json / .csv / .html")
    parser.add_argument("--lookup-cve", help="Get details by CVE ID")
    parser.add_argument("--lookup-euvd", help="Get details by EUVD ID")
    parser.add_argument("--max-entries", type=int, help="Max number of entries to fetch")
    parser.add_argument("--show-exploited", action="store_true", help="Fetch latest exploited vulnerabilities")
    parser.add_argument("--input", type=str, help="YAML watchlist file (each entry must include vendor and product)")
    parser.add_argument("--alerts", action="store_true", help="Trigger alert mode using the YAML watchlist")
    parser.add_argument("--no-banner", action="store_true", help="Suppress ASCII banner even on terminal")
    parser.add_argument("--last", action="store_true", help="Show latest 8 vulnerabilities")
    parser.add_argument("--critical", action="store_true", help="Show latest 8 critical vulnerabilities")
    parser.add_argument("--enisa-id", type=str, help="Get vulnerability details by ENISA ID")
    parser.add_argument("--advisory-id", type=str, help="Get advisory by ID")

    args = parser.parse_args()

    # Print banner only if output is a terminal and user did not request --no-banner
    if sys.stdout.isatty() and not args.no_banner:
        MIN_WIDTH_FOR_ASCII = 72
        term_width = shutil.get_terminal_size((80, 20)).columns
        ascii_description = "\t@Developed by Ferdi Gül | @Github: /FerdiGul\n"
        ascii_art = r"""
╔────────────────────────────────────────────────────────────────╗
│ _____ _   ___     ______    __  __                             │
│| ____| | | \ \   / /  _ \  |  \/  | __ _ _ __  _ __   ___ _ __ │
│|  _| | | | |\ \ / /| | | | | |\/| |/ _` | '_ \| '_ \ / _ \ '__|│
│| |___| |_| | \ V / | |_| | | |  | | (_| | |_) | |_) |  __/ |   │
│|_____|\___/   \_/  |____/  |_|  |_|\__,_| .__/| .__/ \___|_|   │
│                                         |_|   |_|              │   
│                         Version: v1.5                          │
╚────────────────────────────────────────────────────────────────╝
"""
        if term_width >= MIN_WIDTH_FOR_ASCII:
            print(ascii_art)
        else:
            print("EUVD Mapper - ENISA EUVD Data Retriever and Formatter")
        print(ascii_description)

    # Alert mode must have both flags
    if bool(args.input) ^ bool(args.alerts):
        parser.error("Both --input and --alerts must be used together.")
    if args.input and args.alerts:
        asyncio.run(run_alert_mode(args.input))
        return

    # Lookups
    if args.lookup_cve:
        result = asyncio.run(lookup_cve(args.lookup_cve))
        print(json.dumps(result, indent=2))
        return
    if args.lookup_euvd:
        result = asyncio.run(lookup_euvd(args.lookup_euvd))
        print(json.dumps(result, indent=2))
        return
    if args.enisa_id:
        result = asyncio.run(lookup_euvd(args.enisa_id))
        print(json.dumps(result, indent=2))
        return
    if args.advisory_id:
        result = asyncio.run(fetch_advisory(args.advisory_id))
        print(json.dumps(result, indent=2))
        return

    # Fetch lists
    if args.show_exploited:
        entries = asyncio.run(fetch_exploited_vulnerabilities())
    elif args.last:
        entries = asyncio.run(fetch_latest_vulnerabilities())
    elif args.critical:
        entries = asyncio.run(fetch_critical_vulnerabilities())
    else:
        if not (args.keyword or args.vendor or args.product):
            print("Please provide at least one of --keyword, --vendor, or --product")
            return
        entries = asyncio.run(fetch_euvd_entries(
            keyword=args.keyword,
            vendor=args.vendor,
            product=args.product,
            max_entries=args.max_entries
        ))

    if not entries:
        print("[!] No results found.")
        return

    # Handle output
    if args.output:
        output_file = args.output
        out_dir = os.path.dirname(output_file) or "."
        os.makedirs(out_dir, exist_ok=True)

        if output_file.endswith(".json"):
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2)
            print(f"[✓] JSON report saved as: {output_file}")

        elif output_file.endswith(".csv"):
            flattened = [flatten_entry(e) for e in entries]
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=flattened[0].keys())
                writer.writeheader()
                writer.writerows(flattened)
            print(f"[✓] CSV report saved as: {output_file}")

        elif output_file.endswith(".html"):
            generate_html_report(entries, output_file)
            print(f"[✓] HTML report saved as: {output_file}")

    else:
        print(json.dumps(entries, indent=2))


if __name__ == "__main__":
    main()
