#!/usr/bin/env python3
"""Script to login to CDWiFi captive portal."""
import sys
import requests
from bs4 import BeautifulSoup


def main():
    """Main function."""
    test_req = requests.get("http://www.example.com",
                            timeout=5, allow_redirects=False)
    if test_req.status_code == 302 and "Location" in test_req.headers:
        # Extract the URL of the captive portal from the Location header
        captive_portal_url = test_req.headers["Location"]
    else:
        internet = requests.get("http://www.example.com", timeout=5)
        if internet.status_code == 200:
            print("Already connected to the internet", file=sys.stderr)
            sys.exit(0)

        print("Couldn't get CAPNET address", file=sys.stderr)
        sys.exit(1)
    capnet = requests.get(captive_portal_url, timeout=5)

    soup = BeautifulSoup(capnet.text, "html.parser")
    # Get input[name=secret]
    secret = soup.find("input", {"name": "secret"})
    # If secret is None, exit
    if secret is None:
        print("Failed to get secret", file=sys.stderr)
        sys.exit(1)

    value = secret["value"]

    if value is None:
        print("Unknown secret format", file=sys.stderr)
        sys.exit(1)

    # Create x-www-urlencoded payload
    payload = {"secret": value, "eula": "on"}
    # Send POST request
    capnet = requests.post(
        captive_portal_url + "/accept",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=payload,
        timeout=5,
    )

    if capnet.status_code != 200:
        print("Failed to login to CAPNET", file=sys.stderr)
        sys.exit(1)

    print("Logged in to CAPNET")


if __name__ == "__main__":
    main()
