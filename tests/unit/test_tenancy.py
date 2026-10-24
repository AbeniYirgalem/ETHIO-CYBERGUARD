"""Tenancy building blocks: organization ids, record scoping, per-organization telemetry, stream routing."""

import pytest

from services.security.tenancy import (
    DEFAULT_ORG_ID, can_access, is_global, normalize_org_id, org_id_from_name, org_of, record_org, scope,
)
from services.telemetry.stats import TelemetryRegistry, TelemetryStats
from services.websocket.manager import ChannelSubscriptionManager


# ---------- organization ids ----------

def test_org_id_from_name():
    assert org_id_from_name("Awash Bank") == "org_awash_bank"
    assert org_id_from_name("  Commercial   Bank of Ethiopia ") == DEFAULT_ORG_ID
    assert org_id_from_name("CBE") == DEFAULT_ORG_ID
    assert org_id_from_name("") == DEFAULT_ORG_ID
    assert org_id_from_name(None) == DEFAULT_ORG_ID
    assert org_id_from_name("!!!") == DEFAULT_ORG_ID


def test_normalize_accepts_ids_and_names():
    assert normalize_org_id("org_awash_bank") == "org_awash_bank"
    assert normalize_org_id("ORG_AWASH_BANK") == "org_awash_bank"
    assert normalize_org_id("Awash Bank") == "org_awash_bank"
    assert normalize_org_id("../../etc/passwd").startswith("org_")


def test_user_and_record_organization():
    assert org_of({"organization": "Awash Bank"}) == "org_awash_bank"
    assert org_of({"org_id": "org_a", "organization": "Other"}) == "org_a"
    assert org_of({"id": "usr_guest"}) == DEFAULT_ORG_ID   # demo guest and the built-in demo accounts
    assert org_of(None) == DEFAULT_ORG_ID
    assert record_org({}) == DEFAULT_ORG_ID                # records saved before tenancy existed
    assert record_org({"org_id": "org_awash_bank"}) == "org_awash_bank"


def test_scope_and_can_access():
    cbe = {"id": 1}                                         # legacy record -> default org
    awash = {"id": 2, "org_id": "org_awash_bank"}
    cbe_user = {"role": "SECURITY_ANALYST", "organization": "Commercial Bank of Ethiopia"}
    awash_user = {"role": "SECURITY_ANALYST", "organization": "Awash Bank"}
    national = {"role": "SUPER_ADMIN", "organization": "Awash Bank"}

    assert scope(cbe_user, [cbe, awash]) == [cbe]
    assert scope(awash_user, [cbe, awash]) == [awash]
    assert scope(national, [cbe, awash]) == [cbe, awash]
    assert can_access(awash_user, awash) and not can_access(awash_user, cbe)
    assert is_global(national) and not is_global(awash_user) and not is_global(None)


# ---------- per-organization telemetry ----------

def _registry(**kwargs):
    now = [1_800_000_000.0]
    national = TelemetryStats(clock=lambda: now[0])
    return TelemetryRegistry(national, clock=lambda: now[0], **kwargs), now


def test_registry_keeps_organizations_apart_and_sums_the_national_view():
    registry, _ = _registry()
    registry.record_event("org_a", "HIGH", [{"title": "Brute force", "severity": "HIGH"}])
    registry.record_event("org_a", "INFO")
    registry.record_event("org_b", "CRITICAL")

    a = registry.for_org("org_a").snapshot()
    b = registry.for_org("org_b").snapshot()
    assert a["events_processed_today"] == 2 and a["by_severity"]["HIGH"] == 1
    assert [t["name"] for t in a["top_alerts"]] == ["Brute force"]
    assert b["events_processed_today"] == 1 and b["top_alerts"] == []
    assert registry.national.snapshot()["events_processed_today"] == 3
    assert registry.org_ids() == ["org_a", "org_b"]


def test_registry_persists_and_restores_every_organization():
    saved = []
    registry, now = _registry(persist_docs=lambda docs: saved.append(docs), persist_interval=0)
    registry.record_event("org_a", "HIGH")
    registry.record_event("org_b", "LOW")
    registry.flush_all()
    docs = saved[-1]
    assert {d["org_id"] for d in docs} == {"org_a", "org_b"}

    fresh, _ = _registry()
    fresh.national._clock = lambda: now[0]
    assert fresh.load_all(docs) == 2
    assert fresh.for_org("org_a").snapshot()["events_processed_today"] == 1
    assert fresh.for_org("org_b").snapshot()["by_severity"]["LOW"] == 1


def test_registry_ignores_malformed_saved_documents():
    registry, _ = _registry()
    assert registry.load_all("nope") == 0
    assert registry.load_all([1, {"org_id": ""}, {"no": "org"}, {"org_id": 5}]) == 0
    assert registry.org_ids() == []


def test_registry_cap_keeps_memory_bounded():
    registry, _ = _registry(max_orgs=2)
    registry.record_event("org_a", "INFO")
    registry.record_event("org_b", "INFO")
    registry.record_event("org_c", "INFO")      # over the cap: counted nationally, not stored per org
    assert registry.org_ids() == ["org_a", "org_b"]
    assert registry.national.snapshot()["events_processed_today"] == 3


def test_registry_reset_clears_organizations():
    registry, _ = _registry()
    registry.record_event("org_a", "INFO")
    registry.reset()
    assert registry.org_ids() == []


# ---------- stream routing ----------

class _Socket:
    def __init__(self):
        self.messages = []

    async def accept(self):
        pass

    async def close(self, code=1000, reason=""):
        pass

    async def send_json(self, msg):
        self.messages.append(msg)


@pytest.mark.anyio
async def test_tenant_broadcast_reaches_only_that_organization_and_national_admins():
    mgr = ChannelSubscriptionManager()
    cbe, awash, national = _Socket(), _Socket(), _Socket()
    await mgr.connect(cbe, {"org_id": "org_cbe_01", "global": False})
    await mgr.connect(awash, {"org_id": "org_awash_bank", "global": False})
    await mgr.connect(national, {"org_id": "org_cbe_01", "global": True})

    await mgr.broadcast_to_tenant("org_awash_bank", {"type": "EVENT_INGESTED"})
    assert len(awash.messages) == 1
    assert cbe.messages == []
    assert len(national.messages) == 1

    # A national admin who also belongs to the organization is not sent the message twice.
    await mgr.broadcast_to_tenant("org_cbe_01", {"type": "EVENT_INGESTED"})
    assert len(cbe.messages) == 1
    assert len(national.messages) == 2
    assert len(awash.messages) == 1

    assert mgr.get_tenant_count("org_cbe_01") == 2
    assert mgr.get_tenant_count("org_awash_bank") == 1
    assert mgr.get_tenant_count("org_unknown") == 0

    mgr.disconnect(national)
    assert mgr.get_tenant_count("org_cbe_01") == 1
