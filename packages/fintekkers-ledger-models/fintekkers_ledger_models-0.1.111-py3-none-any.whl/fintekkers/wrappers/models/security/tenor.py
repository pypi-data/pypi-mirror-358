from dateutil.relativedelta import relativedelta

from fintekkers.models.security.tenor_type_pb2 import TenorTypeProto
from fintekkers.models.security.tenor_pb2 import TenorProto
class Tenor:
    UNKNOWN_TENOR = None
    type:TenorTypeProto = None
    tenor:relativedelta = None
    
    def __init__(self, type:TenorTypeProto, term:str=None):
        self.type = type
        if term != None:
            self.tenor = Tenor.from_tenor_description(term)
    
    
    def __str__(self) -> str:
        result = []
        type_name = TenorTypeProto.Name(self.get_type())
        result.append(type_name)

        if self.get_type() == TenorTypeProto.TERM:
            result.append(": ")
            result.append(self.get_tenor_description())

        return "".join(result)

    @classmethod
    def from_tenor_description(cls, tenor_description) -> relativedelta:
        if not tenor_description and tenor_description != "":
            return None
        
        return Tenor.parse_period(tenor_description)
    
    def get_type(self) -> TenorTypeProto:
        return self.type


    def get_type_name(self) -> str:
        return TenorTypeProto.Name(self.type)
    
    def get_tenor(self) -> relativedelta:
        return self.tenor
    
    def get_tenor_description(self) -> str:
        if self.get_type() == TenorTypeProto.UNKNOWN_TENOR_TYPE:
            return TenorTypeProto.Name(self.get_type())
        if self.get_type() == TenorTypeProto.PERPETUAL:
            return TenorTypeProto.Name(self.get_type())
        
        return Tenor.period_to_string(self.tenor)
    
    def as_proto(self) -> TenorProto:
        return TenorProto(
            tenor_type=self.type,
            term_value=self.get_tenor_description()
        )

    @staticmethod
    def period_to_string(period:relativedelta) -> str:
        years = period.years
        months = period.months
        weeks = period.days // 7
        days = period.days % 7
        
        result = ""
        if years > 0:
            result += f"{years}Y"
        if months > 0:
            result += f"{months}M"
        if weeks > 0:
            result += f"{weeks}W"
        if days > 0:
            result += f"{days}D"
        
        return result.strip()
    
    @staticmethod
    def parse_period(period_string) -> relativedelta:
        years = 0
        months = 0
        weeks = 0
        days = 0
        
        number_string = ""
        for c in period_string:
            if c.isdigit():
                number_string += c
            else:
                number = int(number_string)
                if c == 'Y':
                    years = number
                elif c == 'M':
                    if period_string.index(c) < len(period_string) - 1 and period_string[period_string.index(c) + 1] == 'W':
                        weeks = number
                        number_string = ""
                        continue
                    else:
                        months = number
                elif c == 'W':
                    weeks = number
                elif c == 'D':
                    days = number
                else:
                    raise ValueError("Invalid character in period string: {}".format(c))
                number_string = ""
        
        return relativedelta(days=days, weeks=weeks, months=months, years=years)

