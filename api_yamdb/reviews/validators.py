import datetime as dt


def year_validator(year):
    now_date = dt.date.today()
    if year > now_date.year:
        raise ValueError(f'Некорректный год {year}')
