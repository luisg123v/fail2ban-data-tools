import argparse
import csv
import subprocess
from collections import defaultdict


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate a CSV with Fail2Ban ban counts per date and per jail.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-o",
        "--output-file",
        default="bans_summary.csv",
        help="Path to the output CSV file",
    )
    parser.add_argument(
        "-d",
        "--csv-delimiter",
        default=",",
        help="Delimiter used in the CSV output file",
    )
    args = parser.parse_args()
    return args


def get_bans_info_from_logs():
    """Retrieve bans info from log files and return fails per day and per jail"""
    # Bans by date and jail: {date: {jail: count}}
    bans_by_date = defaultdict(lambda: defaultdict(int))
    bans_by_jail = defaultdict(int)

    # Using shell to retrieve banned from logs because it's much simpler
    cmd_readlogs = "zgrep -h '] Ban ' /var/log/fail2ban.log* 2>/dev/null"
    proc = subprocess.Popen(cmd_readlogs, shell=True, stdout=subprocess.PIPE, text=True)
    for logline in proc.stdout:
        # Example log line: 2025-01-02 01:02:03,456 fail2ban.actions [PID]: [sshd] Ban 192.168.0.1
        line_parts = logline.split()
        date_ban = line_parts[0]
        jail = line_parts[5].strip("[]")
        bans_by_date[date_ban][jail] += 1
        bans_by_jail[jail] += 1

    # Ensure results are sorted: dates ascending, jails by total count desc
    bans_by_date = dict(sorted(bans_by_date.items()))
    bans_by_jail = dict(
        sorted(bans_by_jail.items(), key=lambda item: item[1], reverse=True)
    )
    return bans_by_date, bans_by_jail


def write_to_file(filename, csv_delimiter, bans_by_date, bans_by_jail):
    if not bans_by_jail:
        print("No bans found in logs, exiting.")
        return
    all_jails = list(bans_by_jail)
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["date", "All jails"] + all_jails,
            delimiter=csv_delimiter,
        )
        writer.writeheader()

        # Data rows
        for date_ban, bans_this_date in bans_by_date.items():
            row = {
                "date": date_ban,
                "All jails": sum(bans_this_date.values()),
                # Ensure all jails are filled even if there are no cases on this date
                **dict.fromkeys(all_jails, 0),
                **bans_this_date,
            }
            writer.writerow(row)

    print(f"CSV file generated: {filename}")


def main():
    args = parse_arguments()
    bans_by_date, bans_by_jail = get_bans_info_from_logs()
    write_to_file(
        filename=args.output_file,
        csv_delimiter=args.csv_delimiter,
        bans_by_date=bans_by_date,
        bans_by_jail=bans_by_jail,
    )


if __name__ == "__main__":
    main()
