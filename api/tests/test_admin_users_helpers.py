import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import admin_users as au


def test_validate_invite_payload_ok_invite():
    result = au.validate_invite_payload({"email": "Nueva@CavaGourmet.com", "role": "admin", "mode": "invite"})
    assert result == {"email": "nueva@cavagourmet.com", "role": "admin", "mode": "invite", "password": None}


def test_validate_invite_payload_ok_create():
    result = au.validate_invite_payload({
        "email": "nueva@cavagourmet.com", "role": "admin", "mode": "create", "password": "unaClaveSegura1",
    })
    assert result["mode"] == "create"
    assert result["password"] == "unaClaveSegura1"


def test_validate_invite_payload_rejects_bad_email():
    try:
        au.validate_invite_payload({"email": "no-es-correo", "role": "admin", "mode": "invite"})
        assert False, "debió lanzar ValidationError"
    except au.ValidationError:
        pass


def test_validate_invite_payload_rejects_bad_role():
    try:
        au.validate_invite_payload({"email": "a@b.com", "role": "superadmin", "mode": "invite"})
        assert False, "debió lanzar ValidationError"
    except au.ValidationError:
        pass


def test_validate_invite_payload_rejects_bad_mode():
    try:
        au.validate_invite_payload({"email": "a@b.com", "role": "admin", "mode": "delete"})
        assert False, "debió lanzar ValidationError"
    except au.ValidationError:
        pass


def test_validate_invite_payload_create_requires_password_length():
    try:
        au.validate_invite_payload({"email": "a@b.com", "role": "admin", "mode": "create", "password": "corta"})
        assert False, "debió lanzar ValidationError"
    except au.ValidationError:
        pass


def test_validate_invite_payload_create_requires_password_present():
    try:
        au.validate_invite_payload({"email": "a@b.com", "role": "admin", "mode": "create"})
        assert False, "debió lanzar ValidationError"
    except au.ValidationError:
        pass


def test_guard_self_deactivate_blocks_self():
    try:
        au.guard_self_deactivate("u1", "u1")
        assert False, "debió lanzar ValidationError"
    except au.ValidationError:
        pass


def test_guard_self_deactivate_allows_others():
    au.guard_self_deactivate("u1", "u2")


def test_guard_last_owner_blocks_dropping_to_zero():
    admins = [
        {"user_id": "owner1", "role": "owner", "active": True},
        {"user_id": "admin1", "role": "admin", "active": True},
    ]
    try:
        au.guard_last_owner(admins, "owner1", False)
        assert False, "debió lanzar ValidationError"
    except au.ValidationError:
        pass


def test_guard_last_owner_allows_when_another_owner_remains():
    admins = [
        {"user_id": "owner1", "role": "owner", "active": True},
        {"user_id": "owner2", "role": "owner", "active": True},
    ]
    au.guard_last_owner(admins, "owner1", False)


def test_guard_last_owner_ignores_non_owner_targets():
    admins = [
        {"user_id": "owner1", "role": "owner", "active": True},
        {"user_id": "admin1", "role": "admin", "active": True},
    ]
    au.guard_last_owner(admins, "admin1", False)


def test_guard_last_owner_allows_reactivating():
    admins = [{"user_id": "owner1", "role": "owner", "active": False}]
    au.guard_last_owner(admins, "owner1", True)
