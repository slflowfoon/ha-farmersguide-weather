# Farmers Guide Weather

A Home Assistant custom integration that scrapes soil temperature data from [farmersguide.co.uk](https://www.farmersguide.co.uk/weather/).

## Sensor

| Entity | Description |
|--------|-------------|
| `sensor.farmers_guide_soil_temperature` | Current soil temperature (°C) from the 72-hour forecast for RH19 3QG |

Updates every hour.

## Installation via HACS

1. In HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/slflowfoon/ha-farmersguide-weather` as an **Integration**
3. Install **Farmers Guide Weather**
4. Restart Home Assistant

## Configuration

Add to `configuration.yaml`:

```yaml
sensor:
  - platform: farmersguide_weather
```

Then restart Home Assistant.
