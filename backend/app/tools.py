from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal


USERS: dict[str, dict[str, Any]] = {
    "alex.chen": {
        "name": "Alex Chen",
        "department": "Marketing",
        "recovery_email": "alex.chen.recovery@example.com",
        "licensed_software": {"Slack", "Microsoft 365", "Figma"},
        "vpn": {
            "status": "degraded",
            "last_seen": "2026-05-21T09:16:00+05:30",
            "gateway": "blr-vpn-02",
            "server_load_percent": 87,
            "recent_errors": ["TLS renegotiation timeout", "Packet loss above 4%"],
        },
    }
}

TICKETS: dict[str, dict[str, Any]] = {
    "IT-2417": {
        "user": "alex.chen",
        "issue": "Laptop display flickers on external monitor",
        "priority": "medium",
        "status": "In progress",
        "owner": "Workspace Support",
        "created_at": "2026-05-20T15:32:00+05:30",
    }
}

_ticket_counter = 4182


def normalize_user(user: str | None) -> str:
    if not user:
        return "alex.chen"
    user = user.strip().lower().replace(" ", ".")
    return user if user in USERS else "alex.chen"


def check_entitlements(user: str, software: str) -> dict[str, Any]:
    user_id = normalize_user(user)
    software_name = software.strip()
    licensed = USERS[user_id]["licensed_software"]
    entitled = software_name.lower() in {item.lower() for item in licensed}
    return {
        "user": user_id,
        "employee_name": USERS[user_id]["name"],
        "software": software_name,
        "entitled": entitled,
        "licensed_software": sorted(licensed),
        "message": (
            f"{USERS[user_id]['name']} is licensed for {software_name}."
            if entitled
            else f"{USERS[user_id]['name']} is not currently licensed for {software_name}."
        ),
    }


def reset_password(user: str) -> dict[str, Any]:
    user_id = normalize_user(user)
    return {
        "user": user_id,
        "employee_name": USERS[user_id]["name"],
        "temporary_password_expires_minutes": 15,
        "recovery_email": USERS[user_id]["recovery_email"],
        "message": (
            f"Password reset started for {USERS[user_id]['name']}. "
            f"Recovery instructions were sent to {USERS[user_id]['recovery_email']}."
        ),
    }


def check_vpn_status(user: str) -> dict[str, Any]:
    user_id = normalize_user(user)
    vpn = USERS[user_id]["vpn"]
    return {
        "user": user_id,
        "employee_name": USERS[user_id]["name"],
        **vpn,
        "message": (
            f"{vpn['gateway']} is {vpn['status']} with server load at "
            f"{vpn['server_load_percent']}%."
        ),
    }


def create_ticket(
    user: str,
    issue: str,
    priority: Literal["low", "medium", "high", "urgent"] = "medium",
) -> dict[str, Any]:
    global _ticket_counter
    user_id = normalize_user(user)
    _ticket_counter += 1
    ticket_id = f"IT-{_ticket_counter}"
    ticket = {
        "user": user_id,
        "employee_name": USERS[user_id]["name"],
        "issue": issue.strip(),
        "priority": priority,
        "status": "Open",
        "owner": "Service Desk",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    TICKETS[ticket_id] = ticket
    return {
        "ticket_id": ticket_id,
        **ticket,
        "message": (
            f"Ticket {ticket_id} was created for {USERS[user_id]['name']} "
            f"with {priority} priority."
        ),
    }


def get_ticket_status(ticket_id: str) -> dict[str, Any]:
    normalized = ticket_id.strip().upper()
    ticket = TICKETS.get(normalized)
    if not ticket:
        return {
            "ticket_id": normalized,
            "found": False,
            "message": f"No ticket was found for {normalized}.",
        }
    return {
        "ticket_id": normalized,
        "found": True,
        **ticket,
        "message": (
            f"{normalized} is {ticket['status']} with {ticket['owner']}."
        ),
    }


TOOL_FUNCTIONS = {
    "check_entitlements": check_entitlements,
    "reset_password": reset_password,
    "check_vpn_status": check_vpn_status,
    "create_ticket": create_ticket,
    "get_ticket_status": get_ticket_status,
}

OPENAI_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "check_entitlements",
        "description": "Check whether a user is already licensed for a software product.",
        "parameters": {
            "type": "object",
            "properties": {
                "user": {"type": "string", "description": "Employee username. Use alex.chen if unspecified."},
                "software": {"type": "string", "description": "Software name requested by the employee."},
            },
            "required": ["user", "software"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "reset_password",
        "description": "Reset an employee password and return the recovery email used.",
        "parameters": {
            "type": "object",
            "properties": {
                "user": {"type": "string", "description": "Employee username. Use alex.chen if unspecified."},
            },
            "required": ["user"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "check_vpn_status",
        "description": "Check recent VPN logs, connection state, gateway, and server load for a user.",
        "parameters": {
            "type": "object",
            "properties": {
                "user": {"type": "string", "description": "Employee username. Use alex.chen if unspecified."},
            },
            "required": ["user"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "create_ticket",
        "description": "Create an IT support ticket for an employee issue.",
        "parameters": {
            "type": "object",
            "properties": {
                "user": {"type": "string", "description": "Employee username. Use alex.chen if unspecified."},
                "issue": {"type": "string", "description": "Concrete issue summary."},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
            },
            "required": ["user", "issue", "priority"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_ticket_status",
        "description": "Look up the current status of an IT ticket.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string", "description": "Ticket identifier, for example IT-2417."},
            },
            "required": ["ticket_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]
