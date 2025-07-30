# import defusedxml.lxml
# Safe XML parsing with custom options (solution of the author)
# https://github.com/tiran/defusedxml/issues/102
# Nb: From issue #33, defusedxml.lxml should be depracted by the author.
# PARSER = etree.Parser(remove_blank_text=True, resolve_entities=False)
# LOOKUP = etree.ElementDefaultClassLookup(defusedxml.lxml.RestrictedElement)
# PARSER.set_element_class_lookup(LOOKUP)
# https://stackoverflow.com/questions/3310614/remove-whitespaces-in-xml-string
import time
from typing import List, Union

import xmltodict
from lxml import etree  # nosec B410
from typing_extensions import TypeAlias

# Element = NewType("Element", etree._Element)
_Element: TypeAlias = etree._Element  # noqa: SLF001
Element: TypeAlias = etree.Element


def _pprint(n: Element):
    print(etree_tostring(n, True).decode())


def pprint(n: Union[Element, List[Element]]):
    if isinstance(n, list):
        root = Element("pprint")
        root.extend(e.copy() for e in n)
        n = root
    _pprint(n)


def wait_attempts(attempts: int = 100, pool_delay: int = 20, start_index: int = 0):
    for i in range(start_index, start_index + attempts):
        yield i
        time.sleep(pool_delay)
    return


def wait_with_duration(duration: int = 1800, pool_delay: int = 20):
    start = time.perf_counter()
    while True:
        delta = time.perf_counter() - start
        yield delta
        if delta >= duration:
            return
        time.sleep(pool_delay)


wait = wait_with_duration


def etree_fromstring(
    string: Union[str, bytes], remove_blank_text: bool = True
) -> Element:
    parser = etree.XMLParser(remove_blank_text=remove_blank_text)
    return etree.XML(string, parser=parser)


def etree_tostring(element: Element, pretty_print: bool = False) -> bytes:
    return etree.tostring(element, pretty_print=pretty_print)


def parse_response(response: Union[str, bytes, Element]) -> List[Element]:
    if isinstance(response, (str, bytes)):
        # Nb: We should use defusedxml library but it doesn't support
        # Removing blank spaces
        response = etree_fromstring(response)
    data = response.xpath("/response/result/*")
    for d in data:
        detach(d)
    return data


def detach(e: Element) -> Element:
    parent = e.getparent()
    if parent is not None:
        parent.remove(e)
    return e


def delete_policy_membership(element):
    entry = element.entry
    # TODO: Check type
    element.remove()  # Remove element from tree
    print(element.dumps(True))
    with entry.as_dict() as d:
        d.target.negate = "no"
        d["destination-hip"].member = "any"
    print(element.dumps(True))

    # client.update(e.xpath, e.dumps())
    # client.create(e.xpath, e.dumps())


def map_dicts(a: dict, b: dict):
    """
    Combine values from b with the value in a having the same key.
    """
    for uuid, u in a.items():
        r = b.get(uuid)
        if r is None:
            continue
        yield u, r


def extend_element(dest, elements):
    """
    Only add element that are not already in the destination
    element.extend(...) is causing duplicates entries because
    the merge is not controlled
    """
    children = {c.tag for c in dest.getchildren()}
    for e in elements:
        if e.tag in children:
            continue
        dest.append(e)
    return dest


def el2dict(e: Union[str, Element]) -> dict:
    if isinstance(e, str):
        e = etree_fromstring(e)
    e.tail = None
    return xmltodict.parse(etree_tostring(e))


# =============================================
# Utility function to compare the changes between configurations
# Nb: native difflib is too slow

# Using xmldiff.main.diff_trees gives false positives (can be filtered) and is very slow
# also, deepdiff.DeepDiff(el2dict(xml1), el2dict(xml2)).to_json() xpath is not able to use attributes to identify entries
# eval(re.findall(".*entry'\]\[\d+\]", diff["dictionary_item_added"][0])[0], {"root": y})


# def _diff_patch(text1, text2):
#     dmp = diff_match_patch()
#     patches = dmp.patch_make(text1, text2)
#     return urllib.parse.unquote(dmp.patch_toText(patches))


# def diff_patch(xml1, xml2):
#     if not isinstance(xml1, str):
#         xml1 = etree_tostring(xml1).decode()
#     if not isinstance(xml2, str):
#         xml2 = etree_tostring(xml2).decode()
#     return _diff_patch(xml1, xml2)
