import argparse
import csv
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import date
from collections import defaultdict


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Plot Fail2Ban bans per day from a CSV produced by the summary script.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input-file",
        default="bans_summary.csv",
        help="Path to the input CSV file",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        default="bans_summary.png",
        help="Path to the output image file (e.g., .png, .svg, .pdf)",
    )
    parser.add_argument(
        "-d",
        "--csv-delimiter",
        default=",",
        help="CSV delimiter of the input file",
    )
    parser.add_argument(
        "--title",
        default="Fail2Ban Bans per Day",
        help="Plot title",
    )
    parser.add_argument(
        "--width",
        type=float,
        default=12.0,
        help="Figure width in inches",
    )
    parser.add_argument(
        "--height",
        type=float,
        default=6.0,
        help="Figure height in inches",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=mpl.rcParams["figure.dpi"],  # Usually 100
        help="Figure DPI",
    )
    args = parser.parse_args()
    return args


def get_plot_data_from_csv(filename, csv_delimiter):
    """Retrieve data to be plotted from the CSV file: dates and series"""
    dates = []
    series = defaultdict(list)
    with open(filename, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=csv_delimiter)
        serie_labels = {column for column in reader.fieldnames if column != "date"}

        # Read rows
        for row in reader:
            dates.append(date.fromisoformat(row["date"]))
            for label in serie_labels:
                series[label].append(int(row.get(label) or 0))

    return dates, series


def plot_series(filename, dates, series, title, width, height, dpi):
    plt.figure(figsize=(width, height), dpi=dpi)
    for label, values in series.items():
        plt.plot(dates, values, marker="o", label=label)

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Bans")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"Image file generated: {filename}")


def main():
    args = parse_arguments()
    dates, series = get_plot_data_from_csv(
        filename=args.input_file, csv_delimiter=args.csv_delimiter
    )
    plot_series(
        filename=args.output_file,
        dates=dates,
        series=series,
        title=args.title,
        width=args.width,
        height=args.height,
        dpi=args.dpi,
    )


if __name__ == "__main__":
    main()
