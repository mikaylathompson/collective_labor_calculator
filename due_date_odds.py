import csv
import datetime
import math
from pprint import pprint

# Start and end dates for the generated data
START_DATE = datetime.date.today()
END_DATE = datetime.date(2024, 1, 15)

# Maximum number of days past due date to consider a possibility of labor.
# Basically this assumes that everyone is induced at due_date + MAX_DAYS_PAST_DUE.
MAX_DAYS_PAST_DUE = 14


class DueDateDataPoint:
    def __init__(self, due_date_string, scheduled_date_string):
        due_date = datetime.datetime.strptime(due_date_string, "%m/%d")
        due_date_with_year = due_date.replace(year=2023 if due_date.month != 1 else 2024).date()
        self.due_date = due_date_with_year
        self.scheduled_date_provided = bool(scheduled_date_string)

        if scheduled_date_string:
            scheduled_date = datetime.datetime.strptime(scheduled_date_string, "%m/%d")
            sched_date_with_year = scheduled_date.replace(year=2023 if scheduled_date.month != 1 else 2024).date()
            self.scheduled_date = sched_date_with_year
        else:
            # If no scheduled date provided, assume due date + 14 days
            self.scheduled_date = self.due_date + datetime.timedelta(days=14)

    def prob_of_labor(self, date, prob_of_date: dict[int:float], prob_of_getting_to_date: dict[int:float]):
        # Fully naive odds of going into labor on this date.
        prob = prob_of_date.get((date - self.due_date).days, 0)

        # Incorporates scheduled date
        if self.scheduled_date == date:
            # Use the odds of getting to this date
            prob = prob_of_getting_to_date.get((date - self.due_date).days, 0)
        elif self.scheduled_date < date:
            # Assume all scheduled dates actually stick.
            prob = 0

        return prob


def load_probability_csv_as_dict(filename):
    prob_of_date = {}
    prob_of_getting_to_date = {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader) # Skip header
        for row in reader:
            key = int(row[1].strip(' days'))
            prob_of_date[key] = float(row[2].strip('%')) / 100
            prob_of_getting_to_date[key] = float(row[3].strip('%')) / 100
    return prob_of_date, prob_of_getting_to_date


def load_due_dates_as_list(filename: str) -> list[DueDateDataPoint]:
    data_list = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader) # Skip header
        for row in reader:
            baby_born = row[3] == "TRUE"
            if not baby_born:
                data_list.append(DueDateDataPoint(row[1], row[2]))
    return data_list

def generate_dates(start_date, end_date) -> list[datetime.date]:
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += datetime.timedelta(days=1)
    return dates

def calculate_net_probability(prob_of_date: dict[int:float],
                              prob_of_getting_to_date: dict[int:float],
                              due_date_list: list[DueDateDataPoint],
                              date: datetime.date) -> float:

    per_person_prob_of_labor = [
        due_date.prob_of_labor(date, prob_of_date, prob_of_getting_to_date) for due_date in due_date_list
    ]
    per_person_prob_of_not_labor = [1 - prob for prob in per_person_prob_of_labor]
    prob_of_no_one_in_labor = math.prod(per_person_prob_of_not_labor)
    return 1 - prob_of_no_one_in_labor


def main(probabilities_file, dates_file, output_csv_file):
    prob_of_date, prob_of_getting_to_date = load_probability_csv_as_dict(probabilities_file)
    
    due_date_list = load_due_dates_as_list(dates_file)

    dates = generate_dates(START_DATE, END_DATE)
    
    with open(output_csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date","Net Probability"])
        for date in dates:
            net_prob = calculate_net_probability(prob_of_date, prob_of_getting_to_date, due_date_list, date)
            writer.writerow([date, net_prob])


if __name__ == "__main__":
    # Ideally these would be user provided inputs, but for now they're hard coded.
    probabilties_csv_file = 'probabilities.csv'
    dates_csv_file = 'due_dates.csv'
    output_csv_file = 'net_probabilities.csv'
    main(probabilties_csv_file, dates_csv_file, output_csv_file)
