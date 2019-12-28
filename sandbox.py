import asyncio

from homebot.services.hass import HassApi

token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhMmY2ZmRjYzMyYzY0ODQ3OTk3NjMwYzIzOTBkYTExNSIsImlhdCI6MTU3NzQ0OTM3OCwiZXhwIjoxODkyODA5Mzc4fQ.SE2MXlmhjCmQKmV5JgK-YPQ5ZOAtcuZMLYWoE-UhoZU'
dut = HassApi(base_url='http://localhost:8123', token=token, timeout=1)



print(asyncio.run(dut.call(
    endpoint='services/homeassistant/turn_on',
    method=HassApi.METHOD_POST,
    data=dict(entity_id='light.light_dummy')
)))

