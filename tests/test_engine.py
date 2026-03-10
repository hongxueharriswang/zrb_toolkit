from zrb.core.models import User, Zone, Role, Operation
from zrb.engine.access import AccessEngine
from zrb.storage.memory import MemoryStore
from zrb.core.types import AccessMode

def test_direct_mode_allows_when_permission_present():
    store = MemoryStore()
    user = User(id="u1", username="alice", email="a@b.com")
    zone = Zone(id="z1", name="Zone1")
    op = Operation(id="op1", app_name="app", name="view")
    role = Role(id="r1", zone_id="z1", name="Role1", base_permissions={"op1"})
    store.add_user(user)
    store.add_zone(zone)
    store.add_operation(op)
    store.add_role(role)
    store.assign_user_to_role(user.id, zone.id, role.id)

    engine = AccessEngine(store)
    assert engine.decide(user, op, zone, mode=AccessMode.DIRECT) is True


def test_direct_mode_denies_when_not_present():
    store = MemoryStore()
    user = User(id="u1", username="alice", email="a@b.com")
    zone = Zone(id="z1", name="Zone1")
    op = Operation(id="op2", app_name="app", name="delete")
    role = Role(id="r1", zone_id="z1", name="Role1", base_permissions={"op1"})
    store.add_user(user)
    store.add_zone(zone)
    store.add_operation(op)
    store.add_role(role)
    store.assign_user_to_role(user.id, zone.id, role.id)

    engine = AccessEngine(store)
    assert engine.decide(user, op, zone, mode=AccessMode.DIRECT) is False
