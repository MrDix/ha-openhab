# 2021: Work by [kubawolanin](https://github.com/kubawolanin/ha-openhab)
Original Plugin development

# 2023: Work by [hauserbauten](https://github.com/hauserbauten/ha-openhab)
Fix GitHub issue link [#23](https://github.com/kubawolanin/ha-openhab/issues/23)

# 2024: Work by [bob-tm](https://github.com/bob-tm/ha-openhab)
* Fix for Home Assistant Version 2024.6 internal API change.   
  This covers the following tickets: [#22](https://github.com/kubawolanin/ha-openhab/issues/22),[#29](https://github.com/kubawolanin/ha-openhab/issues/29),[#29](https://github.com/kubawolanin/ha-openhab/issues/29),[#30](https://github.com/kubawolanin/ha-openhab/issues/30)
* Adding devireg thermostat support
For DeviReg climate there is a [new Home Assistant Addon](https://github.com/bob-tm/ha-devireg-mqtt-addon).  
For these devices no external openHAB setup is needed anymore.

# 2025: Work by [MrDix](https://github.com/MrDix/ha-openhab)
* Fix NotImplementedError when comparing DateTimeItem objects  
  This covers the ticket [#31](https://github.com/kubawolanin/ha-openhab/issues/31)
* Add SSE support for real-time updates from openHAB  
  This covers the ticket [#28](https://github.com/kubawolanin/ha-openhab/issues/28)

# openHAB custom integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]
![][maintenance-shield]
[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Component to integrate with [openHAB][openHAB]._

**This is a Work in Progress repo!**

**This component will set up the following platforms.**

| Platform         | Item types                     |
| ---------------- | ------------------------------ |
| `climate`        | `Devireg thermostat`           |
| `binary_sensor`  | `Contact`                      |
| `sensor`         | `String`, `Number`, `DateTime` |
| `switch`         | `Switch`                       |
| `cover`          | `Rollershutter`                |
| `device_tracker` | `Location`                     |


## HACS Installation

1. Go to http://homeassistant.local:8123/hacs/integrations
1. Add `https://github.com/MrDix/ha-openhab` custom integration repository
1. Download the openHAB repository
1. Go to http://homeassistant.local:8123/config/integrations and add new integration
1. Choose "openHAB" from the list and follow the config flow steps
1. Use oauth2 for Devireg (more properties and correct floor / air temperature display)

## Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `openhab`.
4. Download _all_ the files from the `custom_components/openhab/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "openHAB"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/openhab/translations/en.json
custom_components/openhab/translations/nb.json
custom_components/openhab/translations/sensor.nb.json
custom_components/openhab/__init__.py
custom_components/openhab/api.py
custom_components/openhab/binary_sensor.py
custom_components/openhab/config_flow.py
custom_components/openhab/const.py
custom_components/openhab/manifest.json
custom_components/openhab/sensor.py
custom_components/openhab/switch.py
```

## Configuration is done in the UI

<!---->

## Icons

To show the icons, we are taking openHAB Items "category" field and then matching its value with predefined map (based on classic iconset and Material Design Icons). If none is returned, we proceed with checking the Item's type (Switch, String, Number, Contact and so on) - all of these have their own icon as well.

## Device classes

Device class of each Entity is assigned dynamically based on Items name or label.

## Changes in openHAB Items

When you add/remove Items in openHAB, simply reload the integration in Home Assistant. New entities will appear automatically after reloading the custom component.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

---

[openhab]: https://openhab.org
[buymecoffee]: https://www.buymeacoffee.com/kubawolanin
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/kubawolanin/ha-openhab.svg?style=for-the-badge
[commits]: https://github.com/bob-tm/ha-openhab/commits/master
[hacs]: https://github.com/ludeeus/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/kubawolanin/ha-openhab.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Kuba%20Wolanin%20%40kubawolanin-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/bob-tm/ha-openhab.svg?style=for-the-badge
[releases]: https://github.com/bob-tm/ha-openhab/releases
