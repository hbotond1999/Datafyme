from dateutil.parser import parse

def axis_date_str_converter(dates, date_format):
    try:
        labels = []
        for date in dates:
            date_object = parse(date)
            date = date_object.strftime(date_format)
            labels.append(date)
    except ValueError:
        labels = dates

    return labels