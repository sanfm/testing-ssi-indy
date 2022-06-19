import asyncio
import json
import logging
import os
import sys
import time
import datetime

from aiohttp import ClientError
from qrcode import QRCode

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from runners.agent_container import (  # noqa:E402
    arg_parser,
    create_agent_with_args,
    AriesAgent,
)
from runners.support.agent import (  # noqa:E402
    CRED_FORMAT_INDY,
    CRED_FORMAT_JSON_LD,
    SIG_TYPE_BLS,
)
from runners.support.utils import (  # noqa:E402
    log_msg,
    log_status,
    prompt,
    prompt_loop,
)


CRED_PREVIEW_TYPE = "https://didcomm.org/issue-credential/2.0/credential-preview"
SELF_ATTESTED = os.getenv("SELF_ATTESTED")
TAILS_FILE_COUNT = int(os.getenv("TAILS_FILE_COUNT", 100))

logging.basicConfig(level=logging.WARNING)
LOGGER = logging.getLogger(__name__)





class UGRAgent(AriesAgent):
    def __init__(
        self,
        ident: str,
        http_port: int,
        admin_port: int,
        no_auto: bool = False,
        endorser_role: str = None,
        revocation: bool = False,
        **kwargs,
    ):
        super().__init__(
            ident,
            http_port,
            admin_port,
            prefix="UGR",
            no_auto=no_auto,
            endorser_role=endorser_role,
            revocation=revocation,
            **kwargs,
        )
        self.connection_id = None
        self._connection_ready = None
        self.cred_state = {}
        self.cred_attrs = {}


    async def detect_connection(self):
        await self._connection_ready
        self._connection_ready = None

    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()











async def main(args):

    ugr_agent = await create_agent_with_args(args, ident="ugr")





    try:
        log_status(
            "#1 Provision an agent and wallet, get back configuration details"
            + (
                f" (Wallet type: {ugr_agent.wallet_type})"
                if ugr_agent.wallet_type
                else ""
            )
        )


        agent = UGRAgent(
            "ugr.agent",
            ugr_agent.start_port,
            ugr_agent.start_port + 1,
            genesis_data=ugr_agent.genesis_txns,
            genesis_txn_list=ugr_agent.genesis_txn_list,
            no_auto=ugr_agent.no_auto,
            tails_server_base_url=ugr_agent.tails_server_base_url,
            revocation=ugr_agent.revocation,
            timing=ugr_agent.show_timing,
            multitenant=ugr_agent.multitenant,
            mediation=ugr_agent.mediation,
            wallet_type=ugr_agent.wallet_type,
            seed=ugr_agent.seed,
            aip=ugr_agent.aip,
            endorser_role=ugr_agent.endorser_role,
        )



        ugr_schema_name = "degree schema"
        ugr_schema_attrs = [
            "name",
            "date",
            "degree",
            "birthdate_dateint",
            "timestamp",
        ]



        if ugr_agent.cred_type == CRED_FORMAT_INDY:
            ugr_agent.public_did = True
            await ugr_agent.initialize(
                the_agent=agent,
                schema_name=ugr_schema_name,
                schema_attrs=ugr_schema_attrs,
                create_endorser_agent=(ugr_agent.endorser_role == "author")
                if ugr_agent.endorser_role
                else False,
            )
        elif ugr_agent.cred_type == CRED_FORMAT_JSON_LD:
            ugr_agent.public_did = True
            await ugr_agent.initialize(the_agent=agent)
        else:
            raise Exception("Invalid credential type:" + ugr_agent.cred_type)

        # generate an invitation for Fede
        await ugr_agent.generate_invitation(
            display_qr=True, reuse_connections=ugr_agent.reuse_connections, wait=True
        )

        exchange_tracing = False









# Fin del try
    finally:
        terminated = await ugr_agent.terminate()

    await asyncio.sleep(0.1)

    if not terminated:
        os._exit(1)









if __name__ == "__main__":
    parser = arg_parser(ident="ugr", port=8020)
    args = parser.parse_args()


    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        os._exit(1)
