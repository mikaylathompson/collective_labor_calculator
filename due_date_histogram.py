import csv
import datetime
from matplotlib import pyplot as plt
import numpy as np
from due_date_odds import generate_dates, load_due_dates_as_list

def generate_histogram(due_date_list, filename):
    bins = generate_dates(min(due_date_list)-datetime.timedelta(days=2), max(due_date_list)+datetime.timedelta(days=2))
    counts, bins = np.histogram(due_date_list, bins=bins)
    plt.hist(bins[:-1], bins, weights=counts)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout(pad=1.3)
    plt.savefig(filename)
    plt.show()

if __name__ == "__main__":
    data_points = load_due_dates_as_list("due_dates.csv")
    due_dates = [data_point.due_date for data_point in data_points]
    generate_histogram(due_dates, "due_date_histogram.png")
    due_dates_with_scheduled = [data_point.scheduled_date if data_point.scheduled_date_provided else data_point.due_date for data_point in data_points]
    generate_histogram(due_dates_with_scheduled, "scheduled_or_due_date_histogram.png")