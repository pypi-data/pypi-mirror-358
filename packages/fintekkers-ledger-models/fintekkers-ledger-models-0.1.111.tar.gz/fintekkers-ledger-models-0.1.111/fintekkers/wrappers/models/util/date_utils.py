from datetime import datetime
from fintekkers.models.util.local_date_pb2 import LocalDateProto

def today_proto():
    return get_date_proto(datetime.now())

def get_date_proto(input_date:str):
    if input_date is None:
        return None

    date = datetime.strptime(input_date, '%Y-%m-%d')
    return get_date_proto(date)

def get_date_proto(date:datetime):
    return LocalDateProto(year=date.year, month=date.month, day=date.day)

def get_date_from_proto(local_date_proto:LocalDateProto) -> datetime:
    return datetime(local_date_proto.year, local_date_proto.month, local_date_proto.day, 1, 1, 1, 1)

def get_date(input_date:str) -> datetime:
    if input_date is None:
        return None

    try:
        return datetime.strptime(input_date, '%Y-%m-%d')
    except:
        try:
            return datetime.strptime(input_date, '%m/%d/%y')
        except:
            return datetime.strptime(input_date, '%m/%d/%Y')

def get_date_as_dict(input_date:str) -> dict:
    date = get_date(input_date)
    return { 'year': date.year, 'month': date.month, 'day': date.day}