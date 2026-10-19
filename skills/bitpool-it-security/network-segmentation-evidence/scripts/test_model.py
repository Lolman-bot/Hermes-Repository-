#!/usr/bin/env python3
"""Guards the two rules this tool exists to enforce.

Run from this directory:   python3 test_model.py

1. A subnet's tier comes from its ROUTE TABLE, never its Name tag. This is the
   rule that caught `public-bp-zone-a-db-subnet` — named public, routed private.
2. Only rules genuinely open to 0.0.0.0/0 are reported. A rule restricted to an
   internal CIDR must never be flagged, or the findings lose credibility.

Plus a guard on the Mermaid emitter: GitBook renders `block-beta` as raw code and
fails silently, so the emitter must only ever produce `flowchart`.
"""
import sys

import model
import render

FAILURES = []


def check(label, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {label:<46} got={got!r}")
    if not ok:
        FAILURES.append(f"{label}: wanted {want!r}, got {got!r}")


def test_subnet_tier():
    print("subnet_tier — derived from routing, not naming")
    check("igw default route -> public",
          model.subnet_tier({"Routes": [{"DestinationCidrBlock": "0.0.0.0/0",
                                         "GatewayId": "igw-1"}]}), "public")
    check("nat default route -> private",
          model.subnet_tier({"Routes": [{"DestinationCidrBlock": "0.0.0.0/0",
                                         "NatGatewayId": "nat-1"}]}), "private")
    check("no default route -> isolated",
          model.subnet_tier({"Routes": [{"DestinationCidrBlock": "10.0.0.0/16",
                                         "GatewayId": "local"}]}), "isolated")
    check("no route table -> unrouted", model.subnet_tier(None), "unrouted")
    check("named public but NAT-routed -> private",
          model.subnet_tier({"Routes": [{"DestinationCidrBlock": "0.0.0.0/0",
                                         "GatewayId": "", "NatGatewayId": "nat-9"}]}), "private")


def test_open_rules():
    print("\n_open_rules — only genuinely world-open rules are reported")
    sg = {"IpPermissions": [
        {"IpProtocol": "tcp", "FromPort": 5432, "ToPort": 5433,
         "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
        {"IpProtocol": "tcp", "FromPort": 443, "ToPort": 443,
         "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
        {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22,
         "IpRanges": [{"CidrIp": "10.0.0.0/8"}]},
        {"IpProtocol": "-1", "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}],
        "IpPermissionsEgress": [{"IpProtocol": "-1", "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}]}
    ing = model._open_rules(sg, "ingress")
    services = [s for r in ing for s in r["services"]]
    check("PostgreSQL on 5432-5433 is flagged", "PostgreSQL" in services, True)
    check("SSH restricted to 10/8 is NOT flagged", "SSH" in services, False)
    check("all-protocols rule is flagged", any(r["all"] for r in ing), True)
    eg = model._open_rules(sg, "egress")
    check("unrestricted egress is flagged", bool(eg) and eg[0]["all"], True)


def test_mermaid_guard():
    print("\nMermaid emitter — flowchart only, never block-beta")
    mm = render.mermaid_adjacency({"accounts": [], "peerings": []})
    check("starts with flowchart", mm.startswith("flowchart"), True)
    check("contains no block-beta", "block-beta" in mm, False)


if __name__ == "__main__":
    test_subnet_tier()
    test_open_rules()
    test_mermaid_guard()
    if FAILURES:
        print("\nFAILED:")
        for x in FAILURES:
            print("  - " + x)
        sys.exit(1)
    print("\nAll checks passed.")
