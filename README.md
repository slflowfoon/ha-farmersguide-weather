# Farmers Guide Weather

A Home Assistant custom integration that scrapes soil data from [farmersguide.co.uk](https://www.farmersguide.co.uk/weather/) for a given UK postcode. Updates every hour.

## Sensors

| Entity | Description |
|--------|-------------|
| `sensor.farmers_guide_soil_temperature` | Current soil temperature (°C) from the 72-hour forecast |
| `sensor.farmers_guide_soil_moisture` | Current soil moisture (%) from the 72-hour forecast |

## Installation via HACS

1. In HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/slflowfoon/ha-farmersguide-weather` as an **Integration**
3. Install **Farmers Guide Weather**
4. Restart Home Assistant
5. Go to **Settings → Devices & Services → Add Integration**
6. Search for **Farmers Guide Weather** and enter your postcode when prompted
