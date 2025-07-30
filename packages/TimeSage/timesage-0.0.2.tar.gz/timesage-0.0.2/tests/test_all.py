from importlib.metadata import version
import re

from timesage import Period, Time


def test_():
    print("")


def test_package():

    print("")
    print("Start testing the package.")

    try:
        _version = version("timesage")
        print("Version:", _version)
    except Exception as e:
        print(e)


def test_Period():

    print("")
    print("Start testing class `Period`.")


def test_Time():

    print("")
    print("Start testing class `Time`.")

    assert re.match(r"^\d{9,11}\.\d{6}$", str(Time()))
    assert re.match(r"^\d{9,11}\.\d{6}$", str(Time("now")))
    assert re.match(r"^0.000000$", str(Time("zero")))
