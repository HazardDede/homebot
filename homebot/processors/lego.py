"""Lego related processors."""
import re
from typing import Tuple

import httpx
import pandas as pd  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

from homebot.models import HelpEntry, Message, LegoPricing
from homebot.processors.base import RegexProcessor


class Pricing(RegexProcessor):
    """Processes a !traffic command and delegates the work to a traffic service."""
    DEFAULT_COMMAND = 'lego pricing'
    MESSAGE_REGEX = r'^\s*{command}\s+(?P<set_id>\d+)\s*$'

    CURRENT_PRICE_LABEL = 'Aktueller Preis'
    LEGO_RECOMMENDATION_LABEL = 'Lego Preisempfehlung'
    HIGHEST_EVER_LABEL = 'Höchsten Preis je'
    LOWEST_EVER_LABEL = 'Besten Preis je'
    NAME_ID_REGEX = r"(?P<name>.+?)\s*\((?P<id>\d+)\)\s*"
    BASE_URL = "https://www.brickwatch.net/de-DE/set"
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 " \
                 "(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"

    async def help(self) -> HelpEntry:
        return HelpEntry(
            command=str(self.command),
            usage="{} <set id>".format(self.command),
            description="Queries brickwatch.net for pricing information about the given set id"
        )

    async def _fetch_set_ident(self, soup: BeautifulSoup, set_id: int) -> Tuple[str, int]:
        name_tag = soup.find('h2', attrs={'itemprop': 'name'})
        if not name_tag:
            raise RuntimeError(
                f"Name tag for lego set '{set_id}' was not found in the html content.")
        set_name_id = name_tag['content']
        match = re.match(self.NAME_ID_REGEX, set_name_id)
        if not match:
            raise RuntimeError(f"Could not extract name and set id from html content")

        return str(match.group('name')).strip(), int(str(match.group('id')).strip())

    async def _fetch_prices(self, soup: BeautifulSoup) -> Tuple[float, float, float, float]:
        def _fetch_price(label: str) -> float:
            subset = df[df.label == label]
            if len(subset) == 0:
                raise IndexError(f"Could not fetch price with label '{label}'")
            price_as_str = str(subset.iloc[0]['price'])  # First price
            price_as_str = price_as_str.strip().strip('€').strip().replace(',', '.')
            return float(price_as_str)

        tables = soup.find('table', class_='table-condensed')
        df = pd.read_html(str(tables))[0]
        df.columns = ['label', 'price', 'info']

        return (
            _fetch_price(self.CURRENT_PRICE_LABEL),
            _fetch_price(self.LEGO_RECOMMENDATION_LABEL),
            _fetch_price(self.HIGHEST_EVER_LABEL),
            _fetch_price(self.LOWEST_EVER_LABEL)
        )

    async def _fetch_image(self, soup: BeautifulSoup, set_id: int) -> str:
        image_tag = soup.find('img', attrs={'id': 'setimage_xs'})
        if not image_tag:
            raise RuntimeError(
                f"Image tag for lego set '{set_id}' was not found in the html content.")
        return str(image_tag['src'])

    async def __call__(self, message: Message) -> LegoPricing:
        match = await super().__call__(message)
        set_id = int(match.group('set_id').strip())

        resp = await httpx.get(
            url=f"{self.BASE_URL}/{str(set_id)}",
            headers={'User-Agent': self.USER_AGENT}
        )
        soup = BeautifulSoup(resp.content, 'html.parser')

        set_name, p_set_id = await self._fetch_set_ident(soup, set_id)
        current, recommended, highest, lowest = await self._fetch_prices(soup)
        image_url = await self._fetch_image(soup, set_id)

        return LegoPricing(
            set_name=set_name,
            set_id=p_set_id,
            set_image_url=image_url,
            current=current,
            recommended=recommended,
            highest=highest,
            lowest=lowest
        )
