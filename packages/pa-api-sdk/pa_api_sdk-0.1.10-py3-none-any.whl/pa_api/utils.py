import os
import re

URL_REG = re.compile("(http://|https://)?([^:/]*)(?::(\d+))?(/.*)?")


def first(iterable, default=None):
    return next(iter(iterable), default)


def clean_url_host(url):
    """
    Clean the url:
    * Add scheme if missing
    * Remove trailing slash and path
    * Extract the host
    """
    scheme, host, port, _ = URL_REG.match(url).groups()
    scheme = scheme or "https://"
    url = scheme + host + (f":{port}" if port else "")
    return url, host, port


# =============================================
def getenv(*varnames, raise_exception=True, default=None):
    for var in varnames:
        val = os.environ.get(var)
        if val is not None:
            return val.strip()
    if raise_exception:
        raise Exception(
            f"None of the following environment variables are defined: {', '.join(varnames)}"
        )
    return default


# =======================================================================================================


def get_credentials_from_env(raise_exception=False):
    host = getenv(
        "PA_HOST", "PANO_HOST", "PANORAMA_HOST", raise_exception=raise_exception
    )
    apikey = getenv(
        "PA_APIKEY", "PANO_APIKEY", "PANORAMA_APIKEY", raise_exception=raise_exception
    )
    return host, apikey
