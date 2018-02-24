#!/usr/bin/python3
import getpass
import argparse
from pwnedpy import Pwned, RateLimitException

def main():
    parser = argparse.ArgumentParser(description="Check if a password has been pwned using the haveibeenpwned APIv2.")
    parser.add_argument("--password", "-p", dest="pwd", type=str, help="Password to check, in cleartext.")
    parser.add_argument("--hash", dest="pwdhash", type=str, help="Password to check, as a SHA-1 hash.")
    args = parser.parse_args()

    p = Pwned()
    try:
        if not args.pwd and not args.pwdhash:
            pwd = getpass.getpass("Password: ")
            h, count = p.check(pwd)
        elif args.pwd:
            h, count = p.check(args.pwd)
        elif args.pwdhash:
            h, count = p.check_hash(args.pwdhash)

        if h:
            print("There was a match, go change your password!")
            print("Seen # times in the database: {}".format(count))
        else:
            print("No match.")
    except RateLimitException as e:
        print("You're being rate-limited.")
    except Exception as e:
        print("Error: {}".format(e))

if __name__ == "__main__":
    main()
