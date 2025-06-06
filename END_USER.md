# End User Usage

## Types of Users

- [ ] Badge Barry
  - Programs badge at registration, never touches
  - Cares about a badge that runs all day/low power detection mode
- [ ] Tinkerer Tina
  - Wants to play around with their badge to try apps or change settings
  - Might connect their badge to WiFi
  - Need better on-board configuration and app selections
- [x] Script Kiddie Sam
  - Wants to modify existing apps and write basic code
  - May be overwhelemed by project setup but can use WiFi landing page to modify or upload new single-file apps
- [x] Hacker Hanna
  - Wants to set up the dev environment on their computer to play with the badge, largely by playing with the exiting micropython code base, but wants to do it in their editor for full deployment control
  - Need access to the GitHub repo for the source code (to be released post conference because of CTF things on the badge)
- [x] Embedded Eddie
  - Will set up the `esp-idf` himself and load his own custom images
  - Would benefit most from schematics

## Adding custom apps

- Start up badge
- Put into AP mode
- Open page to add app /apps
  - Text editor to paste code
  - Download examples

## Modify app configurations

- Start up badge
- Put into AP mode
- Open page to change config (/config.html)
- Edit configs in recursive menu
  - Make HTML tables based on
  - `bool`, `str`, `int`, and `float` properties can be editable fields in table
  - `dict` objects in config can be sub-tables (should be avoided)
