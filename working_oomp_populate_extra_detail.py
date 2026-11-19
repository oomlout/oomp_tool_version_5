"""Optional project-specific additions, applied after resolving tool identities."""


def main(**kwargs):
    extras = kwargs.get("extras", [])
    for part in extras:
        if part["key"] == "quarter_inch":
            part["note"] = (
                "The drive size is 6.35 mm. The holder uses a round 8 × 100 mm "
                "clearance profile for bits with unspecified length and head."
            )

