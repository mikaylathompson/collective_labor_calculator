import csv
import datetime
import math
from pprint import pprint

def load_csv_as_dict(filename):
    data_dict = {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader) # Skip header
        for row in reader:
            key = int(row[1].strip(' days'))
            value = float(row[2].strip('%')) / 100
            data_dict[key] = value
    return data_dict

def load_due_dates_as_list(filename, override_with_scheduled_date=False):
    data_list = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader) # Skip header
        for row in reader:
            day = datetime.datetime.strptime(row[1], "%m/%d")
            if override_with_scheduled_date:
                scheduled_date = row[2]
                if scheduled_date:
                    day = datetime.datetime.strptime(scheduled_date, "%m/%d")
            baby_born = row[3] == "TRUE"
            if not baby_born:
                date_with_year = day.replace(year=2023 if day.month != 1 else 2024).date()
                data_list.append(date_with_year)
    return data_list

def generate_dates(start_date, end_date) -> list[datetime.date]:
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += datetime.timedelta(days=1)
    return dates

def calculate_net_probability(prob_by_date: dict[int:float],
                              due_date_list: list[datetime.date],
                              date: datetime.date) -> float:

    per_person_prob_of_labor = [
        prob_by_date.get((date - due_date).days, 0) for due_date in due_date_list
    ]
    per_person_prob_of_not_labor = [1 - prob for prob in per_person_prob_of_labor]
    prob_of_no_one_in_labor = math.prod(per_person_prob_of_not_labor)
    return 1 - prob_of_no_one_in_labor


def main(probabilities_file, dates_file, output_csv_file):
    # Load first CSV as a dictionary
    prob_by_date = load_csv_as_dict(probabilities_file)
    
    # Load second CSV as a list
    due_date_list = load_due_dates_as_list(dates_file)

    # Get today's date
    today = datetime.date.today()
    
    # Get the end of December date
    end_of_december = datetime.date(today.year, 12, 31)
    
    # Generate the list of dates between today and the end of December
    dates = generate_dates(today, end_of_december)
    
    # Write the output CSV file
    with open(output_csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        for date in dates:
            net_prob = calculate_net_probability(prob_by_date, due_date_list, date)
            writer.writerow([date, net_prob])

# Example usage
probabilties_csv_file = 'probabilities.csv'
dates_csv_file = 'due_dates.csv'
output_csv_file = 'net_probabilities.csv'
main(probabilties_csv_file, dates_csv_file, output_csv_file)
