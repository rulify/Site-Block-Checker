import csv
import requests
import random
import time
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

# ANSI colour codes
class Colour:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    WHITE = '\e[0;37m'
    RESET = '\033[0m'

# Load user agents from a text file
def load_user_agents(file_path: str) -> List[str]:
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# Load site list from CSV (assumes URLs are in first column)
def load_site_list(csv_path: str) -> List[str]:
    urls = []
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:
                urls.append(row[0].strip())
    return urls

# Send GET request to a site with a random user-agent and delay
def check_site(url: str, user_agents: List[str]) -> Dict:
    headers = {
        "User-Agent": random.choice(user_agents)
    }

    time.sleep(random.uniform(1.5, 4.0))

    result = {
        "url": url,
        "status_code": None,
        "error": None,
        "elapsed_time": None,
        "user_agent": headers["User-Agent"]
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        result["status_code"] = response.status_code
        result["elapsed_time"] = round(response.elapsed.total_seconds(), 3)
    except requests.RequestException as e:
        result["error"] = str(e)

    return result

# Write results to an output CSV
def write_results_to_csv(results: List[Dict], output_prefix: str):
    full_output = f"{output_prefix}_full.csv"
    summary_output = f"{output_prefix}_summary.csv"

    with open(full_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    summary_fields = ["url", "status_code", "elapsed_time"]
    with open(summary_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=summary_fields)
        writer.writeheader()
        for row in results:
            summary_row = {key: row[key] for key in summary_fields}
            writer.writerow(summary_row)

# Run the full scan
def run_checks(site_list_path: str, ua_list_path: str):
    sites = load_site_list(site_list_path)
    user_agents = load_user_agents(ua_list_path)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_prefix = f"site_results_{timestamp}"

    results = []
    total_sites = len(sites)
    completed = 0
    success_count = 0
    error_count = 0

    print(f"Starting checks on {total_sites} sites with multithreading...")

    with ThreadPoolExecutor(max_workers=25) as executor:
        future_to_url = {
            executor.submit(check_site, site, user_agents): site for site in sites
        }

        for future in as_completed(future_to_url):
            result = future.result()
            completed += 1

            # Count success or error
            if result["error"]:
                error_count += 1
                colour = Colour.RED
                status_display = "ERROR"
            elif result["status_code"] == 200:
                success_count += 1
                colour = Colour.GREEN
                status_display = str(result["status_code"])
            elif result["status_code"] and result["status_code"] < 400:
                colour = Colour.YELLOW
                status_display = str(result["status_code"])
            else:
                colour = Colour.RED
                status_display = str(result["status_code"])

            print(f"{colour}[{completed}/{total_sites}] Checked: {result['url']} "
                  f"(Status: {status_display}, Time: {result['elapsed_time']}s){Colour.RESET}")
            results.append(result)

    # Write results CSVs
    write_results_to_csv(results, output_prefix)

    # Print summary
    print(f"\nDone. Results written to:\n - {output_prefix}_full.csv\n - {output_prefix}_summary.csv")
    print(f"\nSummary:")
    print(f" - ✅ 200 OK responses: {success_count}")
    print(f" - ❌ Errors (timeouts, DNS fails, etc.): {error_count}")

    # Append summary to bottom of full CSV
    full_output = f"{output_prefix}_full.csv"
    with open(full_output, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([])
        writer.writerow(["SUMMARY"])
        writer.writerow(["Total Sites", total_sites])
        writer.writerow(["200 OK", success_count])
        writer.writerow(["Errors", error_count])


# Main entry point
if __name__ == "__main__":
    run_checks("site_list.csv", "user_agents.txt") #FOR LINUX: remove the ".txt" from the user_agents section
