import time
import requests
import logging
from snscrape.base import ScraperException, logger

"""
This file is used for monkey patching to change the way the
snscrape handles its request.
"""


def scraping_request(
    self,
    method,
    url,
    params=None,
    data=None,
    headers=None,
    timeout=10,
    responseOkCallback=None,
    allowRedirects=True,
):
    for attempt in range(self._retries + 1):
        # The request is newly prepared on each retry because of potential cookie updates.
        req = self._session.prepare_request(
            requests.Request(method, url, params=params, data=data, headers=headers)
        )
        logger.info(f"Retrieving {req.url}")
        logger.debug(f"... with headers: {headers!r}")
        if data:
            logger.debug(f"... with data: {data!r}")
        try:
            r = self._session.send(
                req, allow_redirects=allowRedirects, timeout=timeout, verify=False
            )
        except requests.exceptions.RequestException as exc:
            if attempt < self._retries:
                retrying = ", retrying"
                level = logging.INFO
            else:
                retrying = ""
                level = logging.ERROR
            logger.log(level, f"Error retrieving {req.url}: {exc!r}{retrying}")
        else:
            redirected = f" (redirected to {r.url})" if r.history else ""
            logger.info(f"Retrieved {req.url}{redirected}: {r.status_code}")
            if r.history:
                for i, redirect in enumerate(r.history):
                    logger.debug(
                        f'... request {i}: {redirect.request.url}: {r.status_code} (Location: {r.headers.get("Location")})'
                    )
            if responseOkCallback is not None:
                success, msg = responseOkCallback(r)
            else:
                success, msg = (True, None)
            msg = f": {msg}" if msg else ""

            if success:
                logger.debug(f"{req.url} retrieved successfully{msg}")
                return r
            else:
                if attempt < self._retries:
                    retrying = ", retrying"
                    level = logging.INFO
                else:
                    retrying = ""
                    level = logging.ERROR
                logger.log(level, f"Error retrieving {req.url}{msg}{retrying}")
        if attempt < self._retries:
            sleepTime = (
                1.0 * 2**attempt
            )  # exponential backoff: sleep 1 second after first attempt, 2 after second, 4 after third, etc.
            logger.info(f"Waiting {sleepTime:.0f} seconds")
            time.sleep(sleepTime)
    else:
        msg = f"{self._retries + 1} requests to {req.url} failed, giving up."
        logger.fatal(msg)
        raise ScraperException(msg)
    raise RuntimeError("Reached unreachable code")
