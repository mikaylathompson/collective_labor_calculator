# Description

This is a tiny little project based on the wonderful [Datayze Labor Probability Calculator](https://datayze.com/labor-probability-calculator). That calculator accepts a due date and calculates the odds of going into spontaneous labor on each day between now and the the latest possible end of pregnancy (it uses 44 weeks).

This answers the same question, but applied to a group instead of an individual. So instead of answering what the odds that an individual goes into labor on a given day, it answers what the odds that *anyone* in the group goes into labor on a given day are.

It also extends the functionality to include scheduled c-section or induction dates. In these cases, the spontaneous labor probabilities are used up until the scheduled date, at which point delivery is assumed (unless spontaneous labor began earlier).

# Usage
I have included the probabilities csv, but you're responsible for providing your own list of due dates. Mine is formatted as:
`name (currently ignored by the code), due_date (mm/dd), scheduled_date (mm/dd or empty), baby_born (TRUE or FALSE or empty (False))`

I'm using Python 3.11 locally, but I assume this should work with most recent versions of python (probably >3.6 or so). I recommend setting up a virtualenv before installing pip requirements.

To use:
```
# Assumes there is an added file called `due_dates.csv` in the directory
pip install -r requirements.txt

# If you want to generate matplotlib histograbs of due dates.
# It actually generates two plots--the first is due dates, and the second is due dates, but replaced by scheduled dates if applicable.
python due_date_histogram.py

# To generate net probabilities (probability that anyone is in labor on the given day).
# This outputs a file called `net_probabilities.csv`, which is a list of dates (YYYY-MM-DD) and probabilities (as floats).
python due_date_odds.py
```

I've been opening that csv in a spreadsheet and graphing it there, but I hope to do an update that incorporates matplotlib generating the graph.

# Future Work

A few thoughts:
1. As mentioned above, include generating a plot in the net odds script.
2. Incorporate the current date to update the probabilities used. Right now, the probabilities of labor on a given date for each user don't incorporate any information about the current date/state of the user. If today is the user's due date, the sum of all calculated probabilities will be only about 50%, but it should be 100% because we know (assert) that the user hasn't given birth yet. Basically, this requires renormalizing all remaining days to sum to 1 before using the probability dictionary. To do this more easily, I suspect I'll switch to making the probability dicts into numpy arrays.
3. Output the name of the person most likely to go into labor/deliver on each day (and their odds).
4. Generate a list of days where there's more than an X% chance that someone goes into labor/delivers.
5. General clean up/improvements (like command line args for file names, etc.)
