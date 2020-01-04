from unittest import mock
from unittest.mock import MagicMock

import pytest

from homebot.services.traffic import DeutscheBahn, TrafficInfo, TrafficConnection


@pytest.mark.asyncio
async def test_pull():
    with mock.patch('homebot.services.traffic.Schiene') as mck:
        mSchiene =MagicMock()
        mck.return_value = mSchiene
        mSchiene.connections.return_value = [{
            'arrival': '12:00',
            'canceled': False,
            'departure': '11:00',
            'products': ['RE', 'NBE'],
            'transfers': 1,
            'time': '1:00',
            'ontime': False,
            'delay': {'delay_departure': 2, 'delay_arrival': 1}
        }]

        dut = DeutscheBahn()
        res = await dut.pull(origin='Leckerland', destination='CandyTown')

        assert res == TrafficInfo(
            origin='Leckerland',
            destination='CandyTown',
            connections=[
                TrafficConnection(
                    arrival='12:00',
                    canceled=False,
                    departure='11:00',
                    products=['RE', 'NBE'],
                    transfers=1,
                    travel_time='1:00',
                    delayed=True,
                    delay_departure=2,
                    delay_arrival=1
                )
            ]
        )
