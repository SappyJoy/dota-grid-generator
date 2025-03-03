def translate_rank_to_basic(rank: str) -> str:
    mapping = {
        "UNCALIBRATED": "UNCALIBRATED",
        "HERALD": "HERALD_GUARDIAN",
        "GUARDIAN": "HERALD_GUARDIAN",
        "CRUSADER": "CRUSADER_ARCHON",
        "ARCHON": "CRUSADER_ARCHON",
        "LEGEND": "LEGEND_ANCIENT",
        "ANCIENT": "LEGEND_ANCIENT",
        "DIVINE": "DIVINE_IMMORTAL",
        "IMMORTAL": "DIVINE_IMMORTAL",
    }
    return mapping.get(rank.upper(), rank)
