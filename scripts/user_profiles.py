"""Canonical user profile and persona context service for POL MVP."""

from __future__ import annotations

from typing import Any
from zoneinfo import ZoneInfo


class UserProfileAccessError(PermissionError):
    pass


class UserProfileService:
    USER_ALLOWED_PROFILE_FIELDS = {
        "display_name", "email", "preferred_language", "timezone", "bio", "avatar_media_asset_id"
    }

    # RBAC-bearing fields are deliberately excluded. They are admin/system managed.
    MEMBERSHIP_ALLOWED_FIELDS = {
        "display_name_override", "title", "default_contact_channel", "locale_override", "preferences"
    }

    @staticmethod
    def _active_membership(cur, user_id: str, organization_id: str) -> dict:
        cur.execute(
            """
            SELECT m.*, o.org_type, o.name AS organization_name, o.status AS organization_status
            FROM organization_memberships m
            JOIN organizations o ON o.id = m.organization_id
            WHERE m.user_id = %s
              AND m.organization_id = %s
              AND m.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
            LIMIT 1;
            """,
            (user_id, organization_id),
        )
        row = cur.fetchone()
        if not row:
            raise UserProfileAccessError("User has no active membership in this organization.")
        return row

    @classmethod
    def get_my_profile(cls, cur, user_id: str, organization_id: str | None = None) -> dict:
        cur.execute(
            """
            SELECT p.*, u.phone_number, u.is_active, u.last_login_at
            FROM user_profiles p
            JOIN users u ON u.id = p.user_id
            WHERE p.user_id = %s;
            """,
            (user_id,),
        )
        profile = cur.fetchone()
        if not profile:
            raise UserProfileAccessError("Canonical user profile does not exist.")

        result = {"user_profile": profile, "membership_profile": None, "persona_profile": None}
        if organization_id is None:
            return result

        membership = cls._active_membership(cur, user_id, organization_id)
        cur.execute("SELECT * FROM membership_profiles WHERE membership_id = %s", (membership["id"],))
        result["membership"] = membership
        result["membership_profile"] = cur.fetchone()

        role = membership["role"]
        if role in ("RETAILER_OWNER", "RETAILER_STAFF"):
            table = "retailer_membership_profiles"
        elif role in ("VENDOR_OWNER", "VENDOR_STAFF"):
            table = "vendor_membership_profiles"
        elif role == "FIELD_ACTIVATOR":
            table = "field_activator_profiles"
        else:
            table = "operator_membership_profiles"

        cur.execute(f"SELECT * FROM {table} WHERE membership_id = %s", (membership["id"],))
        result["persona_profile"] = cur.fetchone()
        return result

    @classmethod
    def update_my_profile(cls, cur, user_id: str, fields: dict[str, Any]) -> dict:
        unknown = set(fields) - cls.USER_ALLOWED_PROFILE_FIELDS
        if unknown:
            raise ValueError(f"Unsupported user profile fields: {sorted(unknown)}")
        fields = dict(fields)
        if not fields:
            return cls.get_my_profile(cur, user_id)
        if "display_name" in fields and not str(fields["display_name"]).strip():
            raise ValueError("display_name cannot be empty")

        if "email" in fields and fields["email"] is not None:
            email = str(fields["email"]).strip().lower()
            if "@" not in email or len(email) > 254:
                raise ValueError("Invalid email address")
            fields["email"] = email

        if "timezone" in fields:
            try:
                ZoneInfo(str(fields["timezone"]))
            except Exception as exc:
                raise ValueError("Invalid IANA timezone") from exc

        if "avatar_media_asset_id" in fields and fields["avatar_media_asset_id"] is not None:
            cur.execute(
                """
                SELECT 1
                FROM media_assets
                WHERE id = %s
                  AND status = 'READY'
                  AND mime_type LIKE 'image/%'
                  AND uploaded_by_user_id = %s;
                """,
                (fields["avatar_media_asset_id"], user_id),
            )
            if not cur.fetchone():
                raise UserProfileAccessError("Avatar must reference a READY image uploaded by the same user.")

        columns = []
        values = []
        for key in cls.USER_ALLOWED_PROFILE_FIELDS:
            if key in fields:
                columns.append(f"{key} = %s")
                values.append(fields[key])
        values.append(user_id)
        cur.execute(
            f"UPDATE user_profiles SET {', '.join(columns)}, updated_at = now() WHERE user_id = %s RETURNING *",
            tuple(values),
        )
        profile = cur.fetchone()
        if not profile:
            raise UserProfileAccessError("Canonical user profile does not exist.")

        if "display_name" in fields:
            cur.execute("UPDATE users SET full_name = %s, updated_at = now() WHERE id = %s", (fields["display_name"], user_id))
        return profile

    @classmethod
    def update_membership_profile(cls, cur, user_id: str, organization_id: str, fields: dict[str, Any]) -> dict:
        unknown = set(fields) - cls.MEMBERSHIP_ALLOWED_FIELDS
        if unknown:
            raise ValueError(f"Unsupported membership profile fields: {sorted(unknown)}")
        membership = cls._active_membership(cur, user_id, organization_id)
        if not fields:
            cur.execute("SELECT * FROM membership_profiles WHERE membership_id = %s", (membership["id"],))
            return cur.fetchone()

        fields = dict(fields)
        if fields.get("default_contact_channel") not in {None, "IN_APP", "PUSH", "SMS"}:
            raise ValueError("Invalid default_contact_channel")
        if fields.get("locale_override") not in {None, "fa-IR", "en-US"}:
            raise ValueError("Invalid locale_override")

        columns = []
        values = []
        for key in cls.MEMBERSHIP_ALLOWED_FIELDS:
            if key in fields:
                columns.append(f"{key} = %s")
                values.append(fields[key])
        values.append(membership["id"])
        cur.execute(
            f"UPDATE membership_profiles SET {', '.join(columns)}, updated_at = now() WHERE membership_id = %s RETURNING *",
            tuple(values),
        )
        row = cur.fetchone()
        if not row:
            raise UserProfileAccessError("Membership profile does not exist.")
        return row

    @classmethod
    def profile_completion(cls, cur, user_id: str, organization_id: str | None = None) -> dict:
        data = cls.get_my_profile(cur, user_id, organization_id)
        p = data["user_profile"]
        checks = {
            "display_name": bool(p["display_name"]),
            "phone_number": bool(p["phone_number"]),
            "language": bool(p["preferred_language"]),
            "timezone": bool(p["timezone"]),
            "contact_channel": True,
        }
        if organization_id:
            mp = data["membership_profile"] or {}
            checks["title_or_job_function"] = bool(mp.get("title") or mp.get("job_function"))
            checks["dashboard"] = bool(mp.get("preferred_dashboard"))
            checks["onboarding_ready"] = mp.get("onboarding_status") == "READY"

        completed = sum(bool(v) for v in checks.values())
        return {
            "completed": completed,
            "total": len(checks),
            "percentage": round(completed * 100 / len(checks)),
            "checks": checks,
        }
