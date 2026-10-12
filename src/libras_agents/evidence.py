"""Citation filtering adapted from C:\\cw\\Libras\\src\\formatting.py.

Original: _is_private_blob_url, reference commit 2591bdc5e272b26453c6ac30b0c987530c0d5e69
with dirty working-tree changes. Keep hostname parsing inside the malformed-URL guard.
"""

from urllib.parse import urlparse


def is_private_blob_url(url: str) -> bool:
    """Reject Azure Blob object URLs even when source labels are unreliable.

    This preserves the reference policy: even anonymously readable Azure Blob
    objects are suppressed as citations. False does not establish public access.
    """
    try:
        parsed = urlparse(str(url or ""))
        host = (parsed.hostname or "").casefold().rstrip(".")
    except (TypeError, ValueError):
        return False
    return (
        parsed.scheme.casefold() == "blob"
        or host.endswith(".blob.core.windows.net")
        or host.endswith(".blob.core.usgovcloudapi.net")
        or host.endswith(".blob.core.chinacloudapi.cn")
    )
