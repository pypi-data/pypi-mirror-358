import re

import pydantic


@pydantic.validate_call(validate_return=True)
def sanitize_scopus_url(url: pydantic.HttpUrl) -> pydantic.HttpUrl:
    pattern = (
        r"^http:\/\/www\.scopus\.com\/inward\/record\.url\?eid=2-s2\.0-\d+&partnerID=[A-Z0-9]+$"
    )
    if not re.fullmatch(pattern, str(url)):
        msg_err = f"Unaccaptable Scoppus URL format: '{url}'"
        raise ValueError(msg_err)
    return url
