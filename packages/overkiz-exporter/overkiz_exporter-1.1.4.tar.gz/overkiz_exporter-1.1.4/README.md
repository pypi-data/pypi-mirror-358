[![PyPI - Version](https://img.shields.io/pypi/v/overkiz-exporter)](https://pypi.org/project/overkiz-exporter/) [![Docker Image Version](https://img.shields.io/docker/v/jaesivsm/overkiz-exporter)](https://hub.docker.com/r/jaesivsm/overkiz-exporter/tags)

# Overkiz Exporter

A simple open metrics exporter for metrics yielded from overkiz api.

## Metrics served

* `daemon`: Will serve various metrics about the exporter itself.
* `overkiz_measurable`: Will export any float or integer value returned by the overkiz API and tag it with the device specifics.
* `overkiz_label`: Will export any string values returned by the overkiz API. The string value will be placed in the `label` label and the value set to `1`.

Note:
- the `daemon` metric name is configurable through by editing `daemon.metricname`
- the `daemon` name label is configurable by editing `daemon.namelabel`

## Used labels

| Label              | Available on                          | Comment                                                                                  |
|--------------------|---------------------------------------|------------------------------------------------------------------------------------------|
| `status`           | `daemon`                              | Any value, describe the runtime status of the exporter                                   |
| `name`             | `daemon`                              | The value set in the configuration under the `daemon.namelabel` key                      |
| `device_id`        | `overkiz_measurable`, `overkiz_label` | The device id of the current metric                                                      |
| `device_label`     | `overkiz_measurable`, `overkiz_label` | The device name, may be customized                                                       |
| `metric_namespace` | `overkiz_measurable`, `overkiz_label` | The metric namespace, extracted from the API name (example: `core`, `modbuslink`)        |
| `metric_name`      | `overkiz_measurable`, `overkiz_label` | The metric name, extracted from the API name (example: `NameState`, `NumberOfTankState`) |
| `label`            | `overkiz_measurable`                  | The value outputed by the API (example: `Heating`, `off)                                 |

## Example configuration

```json
{
    "credentials": [
        {
            "username": "<login to your atlantic account>",
            "password": "<password to your atlantic account>",
            "servertype": "ATLANTIC_COZYTOUCH"
        }
    ]
}
```

## Running it

For the next few bits of code, we'll suppose you have a working configuration above in `~/.config/overkiz.json`.

### ... with python:

```shell
pip install overkiz-exporter
python -m overkiz_exporter
```

### ... with docker:

```shell
 docker run -v ~/.config/:/etc/overkiz/:ro -p 9100:9100 overkiz-exporter:main
```

You'll then be able retrieve some values:

```shell
curl localhost:9100/metrics

# HELP daemon
# TYPE daemon gauge
daemon{name="overkiz-exporter",section="config",status="loop_interval"} 60.0
daemon{name="overkiz-exporter",section="config",status="items-count"} 1.0
daemon{name="overkiz-exporter",section="exec",status="items-ok"} 1.0
daemon{name="overkiz-exporter",section="exec",status="items-ko"} 0.0
[...]
```
