"""
This is a generic trigger function that can be used
to trigger all specifications belonging to an app
"""

import os

from servc.svc.client.poll import pollMessage
from servc.svc.client.send import sendMessage
from servc.svc.com.bus.rabbitmq import BusRabbitMQ
from servc.svc.com.cache.redis import CacheRedis
from servc.svc.config import Config
from servc.svc.idgen.simple import simple
from servc.svc.io.input import InputPayload, InputType

ORCHESTRATOR_QUEUE = os.getenv("ORCHESTRATOR_QUEUE", "orchestrator")
PROVISIONER_QUEUE = os.getenv("PROVISIONER_QUEUE", "provisioner")
config = Config()
bus = BusRabbitMQ(config.get(f"conf.{BusRabbitMQ.name}"))
cache = CacheRedis(config.get(f"conf.{CacheRedis.name}"))


profile = {
    "profile_id": os.getenv("PROFILE_ID", ""),
    "app_id": os.getenv("APP_ID", ""),
}

# send a message to the provisioner to get all the tenants
tenantMessageId = sendMessage(
    {
        "id": "",
        "type": InputType.INPUT.value,
        "route": PROVISIONER_QUEUE,
        "force": True,
        "argumentId": "",
        "instanceId": "",
        "argument": {
            "method": "getspec",
            "inputs": profile,
        },
    },
    bus,
    cache,
    simple,
    force=True,
)
tenantSpecs = pollMessage(tenantMessageId, cache, timeout=5 * 60)
if tenantSpecs["isError"]:
    print("Error retrieving tenant specs:", tenantSpecs["responseBody"])
    exit(1)

for row in tenantSpecs["responseBody"]:
    tenant = row["auth_expression"]
    payload: InputPayload = {
        "id": "",
        "type": InputType.INPUT.value,
        "route": ORCHESTRATOR_QUEUE,
        "force": True,
        "argumentId": "",
        "instanceId": "",
        "argument": {
            "method": "trigger",
            "inputs": {
                **profile,
                "dag_version": None,
                "tenant_name": tenant,
                "payload": {},
            },
        },
    }

    id = sendMessage(payload, bus, cache, simple, force=True)
    trigger_response = pollMessage(id, cache, timeout=5 * 60)
    if trigger_response["isError"]:
        print(f"Error triggering tenant {tenant}:", trigger_response["responseBody"])
        exit(1)
    else:
        print(
            f"Successfully triggered tenant {tenant}:", trigger_response["responseBody"]
        )
