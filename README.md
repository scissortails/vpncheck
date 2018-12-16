# vpncheck
A proof-of-concept tool written to gather forensic information from VPN clients (ProtonVPN and OVPN). After executing, output is provided which will generate a timeline of VPN connection/disconnection events using the [Timeline](https://github.com/scissortails/Timeline) tool.

## Getting started
vpncheck has one prerequisite.

* [Colorama](https://github.com/tartley/colorama) - For pretty colors

## Configuration
The tool currently does not allow for any configuration during runtime (with the exception of functionality during said runtime).
Hoever, manual alteration can be performed such as altering the width of the generated timeline.

## Using vpncheck
Start the script using the following line.
```python main.py```
During runtime there are few options, some depending on the VPN client analyzed.
* `Client version scan type`. Set to Deep (find all used client versions) or Shallow (find only the latest client version).
* `Username scan type`. Set to Deep (find all used usernames) or Shallow (find only the latest username).
Once complete, a JSON string is generated, looking like this (non-beautified).

```
{
    "width": 2000,
    "start": "12 Dec 2018",
    "end": "16 Dec 2018",
    "callouts": [
        ["Log start: 12 Dec 2018", "12 Dec 2018"],
        ["Log stop: 16 Dec 2018", "16 Dec 2018"],
        ["Username: ['USERNAME']", "12 Dec 2018"],
        ["Version: ['X.X.X.X']", "12 Dec 2018"],
        ["IPv4\nIPv6", "00:00:00 13 Dec, 2018"],
        ...
    ],
    "eras": [
        [" ", "00:00:00 13 Dec, 2018", "01:00:00 13 Dec, 2018"],
        ...
    ]
}
```
 Write this to a file (non-beautified is fine) and run the [Timeline](https://github.com/scissortails/Timeline) tool as follows.
 `python make_timeline.py file.json > out.svg`
 Please see the above link for more information on the Timeline tool.


## Disclaimer
This is a proof-of-concept and should be treated as such.
