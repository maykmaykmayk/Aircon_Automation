"""Core BTU and HP calculation logic for aircon sizing."""

from dataclasses import dataclass

from materials import CEILING_MATERIALS, FLOOR_MATERIALS, WALL_MATERIALS

WATTS_TO_BTU_PER_HOUR = 3.412
BTU_PER_HP = 9000
MIN_DIMENSION_M = 1.0
MAX_DIMENSION_M = 50.0
MIN_HEIGHT_M = 2.0
MAX_HEIGHT_M = 6.0

# PH shortcut baseline for residential spaces.
PH_BASE_BTU_PER_M2 = 600

# Practical adjustment multipliers.
TOP_FLOOR_MULTIPLIER = 1.08
WEST_FACING_MULTIPLIER = 1.10
STANDARD_HP_SIZES = [0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]


@dataclass
class CalculationInput:
    """Container for room and usage details."""

    length_m: float
    width_m: float
    height_m: float
    people_count: int
    electronics_watts: float
    wall_material: str
    ceiling_material: str
    floor_material: str
    climate_zone: str = "hot"
    sun_exposure: str = "normal"


@dataclass
class CalculationResult:
    """Computed cooling values."""

    area_m2: float
    volume_m3: float
    btu_per_hour: float
    hp_required: float


def compute_heat_gain(surface: str, u_value: float, area: float, delta_t: float) -> float:
    """Compute sensible heat gain through a surface in BTU/h."""
    if area < 0:
        raise ValueError(f"{surface} area cannot be negative.")
    if delta_t < 0:
        raise ValueError("Temperature difference cannot be negative.")

    watts = u_value * area * delta_t
    return watts * WATTS_TO_BTU_PER_HOUR


def _height_multiplier(height: float) -> float:
    """Scale BTU for ceiling heights above a typical 2.7 m baseline."""
    if height <= 0:
        raise ValueError("Room height must be greater than zero.")
    return max(1.0, height / 2.7)


def compute_total_btu(
    length: float,
    width: float,
    height: float,
    wall_material: str,
    ceiling_material: str,
    floor_material: str,
    occupants: int,
    windows: float,
    appliances_watts: float,
    top_floor: bool,
    west_facing: bool,
    desired_temp: float = 24,
    outdoor_temp: float = 35,
) -> dict:
    """Compute total BTU/h with PH base formula + envelope and load adjustments."""
    if not MIN_DIMENSION_M <= length <= MAX_DIMENSION_M:
        raise ValueError(
            f"Room length must be between {MIN_DIMENSION_M:.0f} m and {MAX_DIMENSION_M:.0f} m."
        )
    if not MIN_DIMENSION_M <= width <= MAX_DIMENSION_M:
        raise ValueError(
            f"Room width must be between {MIN_DIMENSION_M:.0f} m and {MAX_DIMENSION_M:.0f} m."
        )
    if not MIN_HEIGHT_M <= height <= MAX_HEIGHT_M:
        raise ValueError(
            f"Room height must be between {MIN_HEIGHT_M:.0f} m and {MAX_HEIGHT_M:.0f} m."
        )
    if occupants < 0:
        raise ValueError("Occupants cannot be negative.")
    if windows < 0:
        raise ValueError("Window area cannot be negative.")
    if appliances_watts < 0:
        raise ValueError("Appliance watts cannot be negative.")

    floor_area = length * width
    perimeter = 2 * (length + width)
    wall_area = perimeter * height
    ceiling_area = floor_area
    delta_t = max(0.0, outdoor_temp - desired_temp)

    wall_u = WALL_MATERIALS[wall_material]["u_value"]
    ceiling_u = CEILING_MATERIALS[ceiling_material]["u_value"]
    floor_u = FLOOR_MATERIALS[floor_material]["u_value"]

    base_btu = floor_area * PH_BASE_BTU_PER_M2
    wall_btu = compute_heat_gain("wall", wall_u, wall_area, delta_t)
    ceiling_btu = compute_heat_gain("ceiling", ceiling_u, ceiling_area, delta_t)
    floor_btu = compute_heat_gain("floor", floor_u, floor_area, delta_t)

    # Window gain uses a fixed representative U-value for simple estimates.
    window_btu = compute_heat_gain("windows", 5.8, windows, delta_t)

    # Internal sensible loads.
    occupant_btu = occupants * 600
    appliance_btu = appliances_watts * WATTS_TO_BTU_PER_HOUR

    subtotal = (
        base_btu + wall_btu + ceiling_btu + floor_btu + window_btu + occupant_btu + appliance_btu
    )

    height_mult = _height_multiplier(height)
    top_floor_mult = TOP_FLOOR_MULTIPLIER if top_floor else 1.0
    west_mult = WEST_FACING_MULTIPLIER if west_facing else 1.0
    combined_multiplier = height_mult * top_floor_mult * west_mult

    total_btu = subtotal * combined_multiplier
    hp_data = btu_to_hp(total_btu)

    return {
        "inputs": {
            "length": length,
            "width": width,
            "height": height,
            "desired_temp": desired_temp,
            "outdoor_temp": outdoor_temp,
            "delta_t": delta_t,
            "wall_material": wall_material,
            "ceiling_material": ceiling_material,
            "floor_material": floor_material,
            "occupants": occupants,
            "windows_area_m2": windows,
            "appliances_watts": appliances_watts,
            "top_floor": top_floor,
            "west_facing": west_facing,
        },
        "areas": {
            "floor_area_m2": floor_area,
            "wall_area_m2": wall_area,
            "ceiling_area_m2": ceiling_area,
            "window_area_m2": windows,
        },
        "breakdown_btu_per_hour": {
            "base_ph_formula": base_btu,
            "wall_heat_gain": wall_btu,
            "ceiling_heat_gain": ceiling_btu,
            "floor_heat_gain": floor_btu,
            "window_heat_gain": window_btu,
            "occupants": occupant_btu,
            "appliances": appliance_btu,
        },
        "multipliers": {
            "height_multiplier": height_mult,
            "top_floor_multiplier": top_floor_mult,
            "west_facing_multiplier": west_mult,
            "combined_multiplier": combined_multiplier,
        },
        "subtotal_btu_per_hour": subtotal,
        "total_btu_per_hour": total_btu,
        "hp": hp_data,
    }


def btu_to_hp(total_btu: float) -> dict:
    """Return raw HP, recommended standard HP, and next size up."""
    if total_btu < 0:
        raise ValueError("Total BTU cannot be negative.")

    raw_hp = total_btu / BTU_PER_HP
    recommended_hp = min((hp for hp in STANDARD_HP_SIZES if hp >= raw_hp), default=STANDARD_HP_SIZES[-1])

    higher_sizes = [hp for hp in STANDARD_HP_SIZES if hp > recommended_hp]
    next_size_up = higher_sizes[0] if higher_sizes else recommended_hp

    return {
        "raw_hp": raw_hp,
        "recommended_hp": recommended_hp,
        "next_size_up_hp": next_size_up,
    }


def calculate_cooling_load(data: CalculationInput) -> CalculationResult:
    """Backward-compatible wrapper used by main CLI entry point."""
    result = compute_total_btu(
        length=data.length_m,
        width=data.width_m,
        height=data.height_m,
        wall_material=data.wall_material,
        ceiling_material=data.ceiling_material,
        floor_material=data.floor_material,
        occupants=data.people_count,
        windows=0.0,
        appliances_watts=data.electronics_watts,
        top_floor=False,
        west_facing=False,
        desired_temp=24,
        outdoor_temp=35,
    )
    floor_area = data.length_m * data.width_m
    volume_m3 = floor_area * data.height_m

    return CalculationResult(
        area_m2=floor_area,
        volume_m3=volume_m3,
        btu_per_hour=result["total_btu_per_hour"],
        hp_required=result["hp"]["raw_hp"],
    )

