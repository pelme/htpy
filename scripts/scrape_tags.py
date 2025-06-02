# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "beautifulsoup4",
#     "httpx",
# ]
# ///
import asyncio
import json
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

ELEMENTS_URL = "https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements"
VOID_ELEMENTS_URL = "https://developer.mozilla.org/en-US/docs/Glossary/Void_element"
GLOBAL_ATTRS_URL = "https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes"


async def scrape_elements(client: httpx.AsyncClient) -> dict[str, dict]:
    elements = {}
    r = await client.get(ELEMENTS_URL)
    soup = BeautifulSoup(r.content, "html.parser")
    main = soup.find("article")
    current_tag_nodes = main.select("section:not(:has(div.warning)) td:first-child a code")
    for tag in current_tag_nodes:
        tag_name = tag.text.strip("<>")
        detail_url = urljoin(ELEMENTS_URL, tag.parent["href"])
        attrs = await scrape_attributes(client, detail_url)
        elements[tag_name] = {"attributes": attrs, "deprecated": False, "void": False}

    deprecated_tag_nodes = main.select("section:has(div.warning) td:first-child code")
    for deprecated_tag_node in deprecated_tag_nodes:
        tag_name = deprecated_tag_node.text.strip("<>")
        if tag_name in elements:
            elements[tag_name]["deprecated"] = True

    voids = await void_elements(client)
    for v in voids:
        if v in elements:
            elements[v]["void"] = True
    return elements


async def scrape_attributes(client: httpx.AsyncClient, url: str) -> list[str]:
    r = await client.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    attribute_nodes = soup.select(
        "section[aria-labelledby*=attributes] .section-content>dl>dt:not(:has(.icon-deprecated))"
    )
    attrs = []
    for node in attribute_nodes:
        attr = node.find("code").text
        # If the attribute has a star it's not a specific attribute i.e. data-*
        if "*" not in attr:
            attrs.append(attr)
    return attrs


async def void_elements(client: httpx.AsyncClient) -> list[str]:
    r = await client.get(VOID_ELEMENTS_URL)
    soup = BeautifulSoup(r.content, "html.parser")
    void_tags = soup.select("article ul a code")
    return [t.text.strip("<>") for t in void_tags]


async def global_attributes(client: httpx.AsyncClient) -> list[str]:
    return await scrape_attributes(client, GLOBAL_ATTRS_URL)


async def main():
    async with httpx.AsyncClient() as client:
        global_attrs = await global_attributes(client)
        els = await scrape_elements(client)
    output = {"global_attributes": global_attrs, "elements": els}
    with open("html_spec.json", "w") as f:
        json.dump(output, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
