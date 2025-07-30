#!/usr/bin/env python3

import asyncio
import logging
import time

import daemon_metrics
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
            {"name": {"default": "overkiz-exporter"}},
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
    info = {
        "loop-perid": conf.loop.interval,
        "item-count": len(conf.credentials),
    }
    daemon_metrics.init(conf.name, info)

    while True:
        loop_context = daemon_metrics.LoopContext(conf.name)
        with loop_context:
            OVERKIZ_LABELS.clear()  # removing existing labels
            for cred in conf.credentials:
                try:
                    await update_metrics(
                        cred.username,
                        cred.password,
                        cred.servertype,
                    )
                except Exception:
                    daemon_metrics.item_result(conf.name, False, cred.username)
                    raise
                daemon_metrics.item_result(conf.name, True, cred.username)

        if (interval := conf.loop.interval - loop_context.exec_interval) > 0:
            time.sleep(interval)


if __name__ == "__main__":
    asyncio.run(main())
