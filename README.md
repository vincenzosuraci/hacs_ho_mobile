
[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)


This custom component allows you to retrieve the following information related to the SIM card of the `ho-mobile` operator:

# HACS version (suggested)

## Installation
- add `ho-mobile` as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/)
- in HACS, search for `ho-mobile` and install the latest release
- in Home Assistant, add the `ho-mobile` integration, insert the `username`, `password` and the sim `number` and follow the instructions  


# Stand-alone version

# Introduction
- This custom component allows you to retrieve the following information related to the SIM card of the `ho-mobile` operator:
  - remaining GB (internet/data);
  - total GB provided by the plan;
  - next renewal date.
- The case of 2 or more SIM cards (phone numbers) associated with the same account (password) is supported.
- The case of 2 or more accounts is not supported.

## Installation

- Copy the `ho_mobile_account` folder into your [custom_components folder](https://developers.home-assistant.io/docs/en/creating_component_loading.html).
- Restart Home Assistant.
- After restarting Home Assistant, add the following lines to the <code>configuration.yaml</code> file (and save):


```yaml
ho_mobile_account:
  phone_numbers: !secret ho_mobile_account_phone_numbers
  password: !secret ho_mobile_account_password
  ```

- Go to the `secrets.yaml` file and add the following lines (and save):

```yaml
ho_mobile_account_password: "inserire-qui-la-password"
ho_mobile_account_phone_numbers: 
  - "inserire-qui-il-numero-di-telefono-#1"
  - "inserire-qui-il-numero-di-telefono-#2"  
```

- Restart Home Assistant.
- The following entity triples should appear (one triple for each phone number):
  - `ho_mobile_account.<phone-number>_internet` > Remaining GB
  - `ho_mobile_account.<phone-number>_internet_renewal` > Next renewal date
  - `ho_mobile_account.<phone-number>_internet_threshold` > Total GB of the plan

## Configuration
- By default, data is updated every 15 minutes.
- You can customize the data update interval by configuring the scan_interval parameter, expressed in seconds:

```yaml
ho_mobile_account:
  phone_numbers: !secret ho_mobile_account_phone_numbers
  password: !secret ho_mobile_account_password
  scan_interval: 900
  ```

