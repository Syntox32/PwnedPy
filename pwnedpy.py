import requests
import hashlib

class RateLimitException(Exception):
    """
    https://haveibeenpwned.com/API/v2#AcceptableUse
    """
    pass

class Pwned:
    """
    API Documentation can be found at:
        https://haveibeenpwned.com/API/v2
    """

    URL_RANGE = "https://api.pwnedpasswords.com/range/{hash_prefix}"

    def __init__(self):
        self.user_agent = "PwnedCheck-Python-Script"
        # The API is versioned as the creator would have wanted it, as kind of a tribute.
        #   https://www.troyhunt.com/your-api-versioning-is-wrong-which-is/
        self.api_version = "application/vnd.haveibeenpwned.v2+json"


    # Public functions

    def check_hash(self, pwdhash):
        return self._do_check(pwdhash)

    def check(self, pwd):
        return self._do_check(self._get_hash(pwd))


    # Private functions

    def _do_get(self, url, hash_prefix):
        """
        Do a GET request with custom headers.
        """
        headers = {
            "User-Agent": self.user_agent,
            "Accept": self.api_version
        }
        return requests.get(url.format(hash_prefix=hash_prefix), headers=headers)

    def _get_hash(self, pwd, prefix=False):
        """
        Return the first 5 chars of a SHA-1 hash, or the whole hash.
        """
        h = hashlib.sha1(pwd.encode("utf-8")).hexdigest()
        if prefix:
            return h[:5]
        return h

    def _check_hashes(self, full_hash, resp_str):
        hashes = resp_str.split("\n")
        # The hashes in the response are suffixes to the
        # hash we sent a response for, so we have to combine
        # them and check if any match.
        #   https://www.troyhunt.com/ive-just-launched-pwned-passwords-version-2/
        for suffix in hashes:
            hash_suffix = suffix.split(":")[0]
            count = suffix.split(":")[1]

            if full_hash.lower() == full_hash[:5].lower() + hash_suffix.lower():
                return full_hash.upper(), count

        return None, 0

    def _do_check(self, pwdhash):
        hash_prefix = pwdhash[:5]
        r = self._do_get(self.URL_RANGE, hash_prefix)

        if r.status_code == 200:
            return self._check_hashes(pwdhash, r.text)
        elif r.status_code == 429:
            raise RateLimitException("Rate limit exceeded, refer to acceptable use \
                of the API: https://haveibeenpwned.com/API/v2#AcceptableUse")
        else:
            # The API states that there should be no circumstance
            # where the `range` request does not find any hash.
            # Which means no `404` should occur.
            raise requests.exceptions.HTTPError("Status was {0}, expected 200"
                .format(r.status_code))
