import attr
import ujson as json
import requests
from requests.auth import HTTPBasicAuth
from typing import List, Dict
from functools import lru_cache
import arrow
from collections import Counter

ISO_NE_API_BASE = "https://webservices.iso-ne.com/api/v1.1/"


@lru_cache(maxsize=2)
def get_config():
    with open(".config.json") as fp:
        return json.load(fp)


def get_auth() -> HTTPBasicAuth:
    CONFIG = get_config()
    return HTTPBasicAuth(CONFIG["user"], CONFIG["password"])


def smart_time(input: str) -> arrow.Arrow:
    return arrow.get(input)


@attr.s
class GenFuelMixData(object):
    BeginDate = attr.ib(converter=smart_time, type=arrow.Arrow)
    GenMw = attr.ib(type=int)
    # "Renewables, Other, Oil, Nuclear, Natural Gas, Coal"
    FuelCategoryRollup = attr.ib(type=str)
    # "Refuse, Solar, Wind, etc."
    FuelCategory = attr.ib(type=str)
    MarginalFlag = attr.ib(type=str)


def get_current_fuel_mix() -> List[GenFuelMixData]:
    response = requests.get(
        ISO_NE_API_BASE + "genfuelmix/current.json", auth=get_auth()
    )
    mix_list = response.json()["GenFuelMixes"]["GenFuelMix"]
    return [GenFuelMixData(**it) for it in mix_list]


@attr.s
class LocationInfo(object):
    LocId = attr.ib(type=str)
    LocType = attr.ib(type=str)
    LocName = attr.ib(type=str)


def make_location(data: Dict[str, str]) -> LocationInfo:
    # weird field names:
    return LocationInfo(data["@LocId"], data["@LocType"], LocName=data["$"])


@attr.s
class FiveMinutePriceData(object):
    BeginDate = attr.ib(converter=smart_time, type=arrow.Arrow)
    Location = attr.ib(converter=make_location, type=LocationInfo)
    LmpTotal = attr.ib(type=float)
    EnergyComponent = attr.ib(type=float)
    CongestionComponent = attr.ib(type=float)
    LossComponent = attr.ib(type=float)


def get_five_minute_pricing() -> List[FiveMinutePriceData]:
    response = requests.get(
        ISO_NE_API_BASE + "fiveminutelmp/current.json", auth=get_auth()
    )
    data_list = response.json()["FiveMinLmps"]["FiveMinLmp"]
    return [FiveMinutePriceData(**it) for it in data_list]


def get_pricing_by_zone() -> Dict[str, FiveMinutePriceData]:
    pricing_info = get_five_minute_pricing()
    output = {}
    for p in pricing_info:
        output[p.Location.LocName] = p
    return output


WESTERN_MA_LOCATION_NAME = ".Z.WCMASS"

if __name__ == "__main__":
    pricing_info = get_pricing_by_zone()[WESTERN_MA_LOCATION_NAME]
    print("# Pricing Info")
    print("  Timestamp:", pricing_info.BeginDate.humanize())
    print(
        "  Energy, Congestion, Loss:",
        pricing_info.EnergyComponent,
        pricing_info.CongestionComponent,
        pricing_info.LossComponent,
    )
    print("  Total Price:", pricing_info.LmpTotal)
    print()

    distribution = Counter()
    fuel_mix = get_current_fuel_mix()
    total_mw = sum(md.GenMw for md in fuel_mix)
    for mix_data in fuel_mix:
        distribution[mix_data.FuelCategoryRollup] += mix_data.GenMw
    print("# Current Fuel Mix")
    print("  Timestamp:", fuel_mix[0].BeginDate.humanize())
    print("  Mw Distribution", dict(distribution))
    print("  Renewables: %1.2f%%" % (distribution["Renewables"] / total_mw))
