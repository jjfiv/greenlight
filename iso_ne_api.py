import attr
import ujson as json
import requests
from requests.auth import HTTPBasicAuth
from typing import List
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


if __name__ == "__main__":
    distribution = Counter()
    fuel_mix = get_current_fuel_mix()
    total_mw = sum(md.GenMw for md in fuel_mix)
    for mix_data in fuel_mix:
        distribution[mix_data.FuelCategoryRollup] += mix_data.GenMw
    print("Current Fuel Mix")
    print("Timestamp:", fuel_mix[0].BeginDate.humanize())
    print("Mw Distribution", dict(distribution))
    print("Renewables: %1.2f%%" % (distribution["Renewables"] / total_mw))
