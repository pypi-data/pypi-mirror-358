#!/usr/bin/env python3

import asyncio
import logging
import time
from datetime import datetime

from prometheus_client import Gauge, start_http_server
from pyoverkiz.client import OverkizClient
from pyoverkiz.const import SUPPORTED_SERVERS
from pyoverkiz.enums import DataType, Server
from the_conf import TheConf

logger = logging.getLogger(__name__)
conf = TheConf(
    {
        "source_order": ["env", "files"],
        "config_files": [
            "/etc/overkiz/overkiz.json",
            "~/.config/overkiz.json",
        ],
        "parameters": [
            {
                "daemon": [
                    {
                        "metricname": {
                            "default": "daemon",
                            "help": "the metric through which the state "
                            "of the exporter will be exporter",
                        }
                    },
                    {
                        "namelabel": {
                            "default": "overkiz-exporter",
                            "help": "the name label of the metric",
                        }
                    },
                ]
            },
            {
                "type": "list",
                "credentials": [
                    {"username": {"type": str}},
                    {"password": {"type": str}},
                    {"servertype": {"type": str}},
                ],
            },
            {"loop": [{"interval": {"default": 240}}]},
            {"prometheus": [{"port": {"type": "int", "default": 9100}}]},
        ],
    }
)
_BASE_LABELS = ["device_id", "device_label", "metric_namespace", "metric_name"]
DAEMON = Gauge(conf.daemon.metricname, "", ["name", "section", "status"])
OVERKIZ_MEASURABLE = Gauge("measurable", "", _BASE_LABELS, namespace="overkiz")
OVERKIZ_LABELS = Gauge(
    "labels", "", _BASE_LABELS + ["label"], namespace="overkiz"
)


async def update_metrics(username, password, server_type):
    server = SUPPORTED_SERVERS[Server[server_type]]
    async with OverkizClient(username, password, server=server) as client:
        try:
            await client.login()
        except Exception:  # pylint: disable=broad-except
            logger.error("%r/%r => couldn't connect", server, username)
            return

        devices = await client.get_devices()

        metric_count = metric_ignored = 0
        for device in devices:
            for state in device.states:
                if state.value and not isinstance(state.value, dict):
                    namespace, name = state.name.split(":")
                    lbl = [device.id, device.label, namespace, name]
                    if state.type in {DataType.FLOAT, DataType.INTEGER}:
                        OVERKIZ_MEASURABLE.labels(*lbl).set(state.value)
                    else:
                        OVERKIZ_LABELS.labels(*lbl, state.value).set(1)
                    metric_count += 1
                else:
                    metric_ignored += 1
        logger.debug(
            "%r/%r wrote %d metric, ignored %d",
            server,
            username,
            metric_count,
            metric_ignored,
        )


async def main() -> None:
    start_http_server(conf.prometheus.port)
    labels = {"name": conf.daemon.namelabel, "section": "config"}
    DAEMON.labels(status="loop-period", **labels).set(conf.loop.interval)
    DAEMON.labels(status="item-count", **labels).set(len(conf.credentials))

    labels["section"] = "exec"
    while True:
        start = datetime.now()
        OVERKIZ_LABELS.clear()  # removing existing labels
        DAEMON.labels(status="items-ok", **labels).set(0)
        DAEMON.labels(status="items-ko", **labels).set(0)
        for credential in conf.credentials:
            try:
                await update_metrics(
                    credential.username,
                    credential.password,
                    credential.servertype,
                )
            except Exception:
                DAEMON.labels(status="items-ko", **labels).inc()
                raise
            DAEMON.labels(status="items-ok", **labels).inc()

        exec_interval = (datetime.now() - start).total_seconds()
        DAEMON.labels(status="exec-time", **labels).set(exec_interval)
        DAEMON.labels(status="loop-count", **labels).inc()
        interval = conf.loop.interval - exec_interval
        if interval > 0:
            time.sleep(interval)


if __name__ == "__main__":
    asyncio.run(main())
