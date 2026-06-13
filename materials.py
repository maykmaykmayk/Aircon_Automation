"""Material reference tables used by the aircon sizing calculator.

Each material entry contains:
- display_name
- u_value (W/m²·K)
- description
"""

WALL_MATERIALS = {
    "chb": {
        "display_name": "CHB",
        "u_value": 2.3,
        "description": "Concrete hollow block wall; durable but moderate insulation.",
    },
    "brick": {
        "display_name": "Brick",
        "u_value": 1.6,
        "description": "Clay brick masonry wall with decent thermal mass.",
    },
    "wood": {
        "display_name": "Wood",
        "u_value": 0.8,
        "description": "Timber wall assembly with better insulation than masonry.",
    },
    "glass": {
        "display_name": "Glass",
        "u_value": 5.8,
        "description": "Single-glazed glass surface with high heat transfer.",
    },
    "insulated_drywall": {
        "display_name": "Insulated Drywall",
        "u_value": 0.55,
        "description": "Drywall partition with insulation layer for improved performance.",
    },
}

CEILING_MATERIALS = {
    "concrete_slab": {
        "display_name": "Concrete Slab",
        "u_value": 1.8,
        "description": "Standard reinforced concrete slab without extra insulation.",
    },
    "insulated_concrete": {
        "display_name": "Insulated Concrete",
        "u_value": 0.75,
        "description": "Concrete ceiling with added insulation to reduce heat gain.",
    },
    "wood_plywood": {
        "display_name": "Wood/Plywood",
        "u_value": 1.2,
        "description": "Wood or plywood ceiling construction with moderate insulation.",
    },
    "pvc_false_ceiling": {
        "display_name": "PVC False Ceiling",
        "u_value": 1.0,
        "description": "PVC ceiling assembly, often creating an insulating air gap.",
    },
}

FLOOR_MATERIALS = {
    "concrete_slab_on_ground": {
        "display_name": "Concrete Slab on Ground",
        "u_value": 1.5,
        "description": "Ground-contact concrete slab with typical thermal behavior.",
    },
    "elevated_wood": {
        "display_name": "Elevated Wood",
        "u_value": 1.2,
        "description": "Raised timber floor with lower thermal conductivity than concrete.",
    },
    "tiled_concrete": {
        "display_name": "Tiled Concrete",
        "u_value": 1.7,
        "description": "Concrete floor finished with tile; slightly higher heat transfer.",
    },
}

# Backward-compatible U-value maps for calculator/main imports.
WALL_U_VALUES = {key: item["u_value"] for key, item in WALL_MATERIALS.items()}
CEILING_U_VALUES = {key: item["u_value"] for key, item in CEILING_MATERIALS.items()}
FLOOR_U_VALUES = {key: item["u_value"] for key, item in FLOOR_MATERIALS.items()}

