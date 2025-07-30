from nintendo.nex import rmc, matchmaking, common
from pymongo.collection import Collection

from nex_protocols_common_py import matchmaking_utils
from nex_protocols_common_py.matchmaking_utils import GatheringFlags


class CommonMatchMakingServer(matchmaking.MatchMakingServer):

    def __init__(self,
                 settings,
                 gatherings_db: Collection,
                 sessions_db: Collection,
                 sequence_db: Collection):
        super().__init__()
        self.settings = settings

        self.gatherings_db = gatherings_db
        self.sessions_db = sessions_db
        self.sequence_db = sequence_db

    # ============= Utility functions  =============

    # ============= Method implementations  =============

    async def unregister_gathering(self, client, gid):
        gathering = self.gatherings_db.find_one({"id": gid})
        if not gathering:
            raise common.RMCError("RendezVous::SessionVoid")

        if gathering["owner"] != client.pid():
            raise common.RMCError("RendezVous::PermissionDenied")

        self.gatherings_db.delete_one({"id": gid})
        return True

    async def get_session_urls(self, client, gid):
        gathering = self.gatherings_db.find_one({"id": gid})
        if not gathering:
            raise common.RMCError("RendezVous::SessionVoid")

        if client.pid() not in gathering["players"]:
            raise common.RMCError("RendezVous::PermissionDenied")

        host_session = self.sessions_db.find_one({"pid": gathering["host"]})

        res = []
        for url in host_session["urls"]:
            res.append(common.StationURL.parse(url))

        return res

    async def find_by_single_id(self, client, gid):
        gathering = self.gatherings_db.find_one({"id": gid})
        if not gathering:
            raise common.RMCError("RendezVous::SessionVoid")

        response = rmc.RMCResponse()
        response.result = True
        response.gathering = matchmaking_utils.gathering_type_from_document(gathering)
        return response

    async def update_session_host_v1(self, client, gid: int):
        gathering = self.gatherings_db.find_one({"id": gid})
        if not gathering:
            raise common.RMCError("RendezVous::SessionVoid")

        if client.pid() not in gathering["players"]:
            raise common.RMCError("RendezVous::PermissionDenied")

        updates = {"host": client.pid()}
        if gathering["flags"] & GatheringFlags.CAN_OWNERSHIP_BE_TAKEN_BY_PARTICIPANTS:
            updates.update({"owner": client.pid()})

        self.gatherings_db.update_one({"id": gid}, {"$set": updates})

        if gathering["flags"] & GatheringFlags.CAN_OWNERSHIP_BE_TAKEN_BY_PARTICIPANTS:
            for pid in gathering["players"]:
                pass  # TODO: Send notification 4000
