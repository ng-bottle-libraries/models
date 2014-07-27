from uuid import uuid4
from itertools import izip
from hashlib import sha512

generate_random_salt = lambda size=64: uuid4().hex[:size]
generate_password_hash = lambda passwd, salt: sha512(salt + passwd).hexdigest()
check_password_hash = lambda password, password_hash, salt: \
    safe_str_cmp(password_hash, generate_password_hash(password, salt))


def safe_str_cmp(a, b):
    """This function compares strings in somewhat constant time. This
    requires that the length of at least one string is known in advance.

    Returns `True` if the two strings are equal, or `False` if they are not.

    From: https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/security.py
    """
    if len(a) != len(b):
        return False
    rv = 0
    for x, y in izip(a, b):
        rv |= ord(x) ^ ord(y)
    return rv == 0
