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
    """This class represents one row in the due_dates.csv file, and interprets the strings as dates.
    Provided with two probability dicts, it will calculate the probability of going into labor on a given date.
    """
    def __init__(self, due_date_string, scheduled_date_string):
        """This assumes two strings are passed in. The first must be the due date in mm/yy format, and
        the second is either an empty string (no scheduled date) or a scheduled c-section/induction date
        in mm/yy format. If no scheduled date is provided, the due date + MAX_DAYS_PAST_DUE days will be used.
        """
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
            self.scheduled_date = self.due_date + datetime.timedelta(days=MAX_DAYS_PAST_DUE)


    def prob_of_labor(self, date, prob_of_date: dict[int:float], prob_of_getting_to_date: dict[int:float]) -> float:
        """Returns the probability of going into labor on a given date, given the two probability dicts.

        The first probability dict is the probability of going into spontaneous labor on any specific day,
        relative to the due date (e.g. odds of labor 3 days before the due date (-3) is 2.7%).

        The second probability dict is the probability of getting to the date while still pregnant (i.e. without
        having gone into labor on any previous date). In this case, the odds of getting to 3 days before your due
        date and still being pregnant is 61.4%. This corresponds to 1 - (sum of prob_of_date for all previous dates),
        so could be derived from the previous probability dict, but I'm passing it in for simplicity/performance sake.

        This function begins by just calculating the probability of spontaneous labor on the given date. Then it compares
        the given date to the scheduled date. If the given date is exactly the scheduled date, than we assume that the odds
        of delivery that day are equal to the odds of getting to that date (this basically excludes the possibility that a
        scheduled induction or c-section is delayed, and in the case of inductions is the probability of labor beginning that
        day, not a baby actually arriving). For any date after the scheduled date, the probability is 0, because we assume
        the baby is already born.
        """
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


def load_probability_csv_as_dict(filename: str) -> tuple[dict[int:float], dict[int:float]]:
    """This loads a csv file with the following format:
    nicely formatted date (ignored), days relative to due date (pos or neg integer), prob_of_date, prob_of_getting_to_date.
    See the doc string of DueDateDataPoint.prob_of_labor for more info on the two probability lists.
    It returns two dictionaries which map the number of days relative to the due date to the corresponding probability.
    """
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
    """This loads a csv file with the following format:
    name (ignored), due_date (mm/dd), scheduled_date (mm/dd or empty), baby_born (TRUE or FALSE or empty (False)).
    At this point, baby_born excludes the data point becuase the odds of labor at anytime in the future is 0.

    It returns a list of DueDateDataPoints corresponding to each still-pregnant person.
    """
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
    """Generates a list of dates between start_date and end_date, inclusive."""
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
    """Calculates the net probability of a given date. This is the probability that ANYONE is in labor (or delivers,
    in the case of a c-section) on the given date.

    The P(anyone is in labor) can be rephrased as not P(no one in labor), which is how it is calculated. First the odds
    for each individual to be in labor on that day are calculated, and inversed to be the probability that each individual
    is NOT in labor. The product of that array is the probability that no one is in labor, and that's inverted to be the
    probability that someone is in labor.
    """

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
