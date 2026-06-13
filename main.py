"""Entry point for the Aircon Automation CLI app."""

import inquirer
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table

from calculator import compute_total_btu
from materials import CEILING_MATERIALS, FLOOR_MATERIALS, WALL_MATERIALS

console = Console()
WINDOW_AREA_PER_UNIT_M2 = 1.5
MIN_DIMENSION_M = 1.0
MAX_DIMENSION_M = 50.0
MIN_HEIGHT_M = 2.0
MAX_HEIGHT_M = 6.0
HIGH_LOAD_WARNING_BTU = 30000
SMALL_ROOM_MAX_AREA_M2 = 10.0
APPLIANCE_LOAD_OPTIONS = {
    "none": 0.0,
    "light": 250.0,  # TV + lights
    "heavy": 700.0,  # PC + TV + lights
}
WINDOW_U_VALUE = 5.8


def _positive_float(_answers: dict, value: str) -> bool | str:
    try:
        number = float(value)
        if MIN_DIMENSION_M <= number <= MAX_DIMENSION_M:
            return True
        return (
            f"Value must be between {MIN_DIMENSION_M:.0f} m and "
            f"{MAX_DIMENSION_M:.0f} m."
        )
    except ValueError:
        return "Please enter a valid number."


def _non_negative_int(_answers: dict, value: str) -> bool | str:
    try:
        return int(value) >= 0
    except ValueError:
        return "Please enter a whole number."


def _material_choices(materials: dict[str, dict]) -> list[tuple[str, str]]:
    choices: list[tuple[str, str]] = []
    for index, (key, meta) in enumerate(materials.items(), start=1):
        label = (
            f"{index}. {meta['display_name']} "
            f"(U={meta['u_value']} W/m²·K) - {meta['description']}"
        )
        choices.append((label, key))
    return choices


def _temperature(_answers: dict, value: str) -> bool | str:
    try:
        temp = float(value)
        if 16 <= temp <= 30:
            return True
        return "Please enter a temperature between 16 and 30 °C."
    except ValueError:
        return "Please enter a valid number."


def _height(_answers: dict, value: str) -> bool | str:
    try:
        number = float(value)
        if MIN_HEIGHT_M <= number <= MAX_HEIGHT_M:
            return True
        return (
            f"Height must be between {MIN_HEIGHT_M:.0f} m and "
            f"{MAX_HEIGHT_M:.0f} m."
        )
    except ValueError:
        return "Please enter a valid number."


def _recommendation_note(
    recommended_hp: float, next_size_up_hp: float, top_floor: bool, west_facing: bool
) -> str:
    if top_floor or west_facing:
        return (
            f"Exposure is higher, so consider [bold]{next_size_up_hp:.2f} HP[/bold] "
            "inverter for better headroom and lower afternoon energy spikes."
        )
    if recommended_hp >= 1.5:
        return (
            "For longer daily usage, an inverter model is usually more efficient "
            "than non-inverter units at this capacity."
        )
    return (
        "For short and occasional use, non-inverter can be cost-effective; "
        "for all-day use, inverter is typically the better choice."
    )


def run() -> None:
    console.print(Panel.fit("Aircon Automation", style="bold cyan"))
    console.print("Answer the prompts to estimate BTU/h and recommended HP.\n")
    while True:
        questions = [
            inquirer.Text(
                "length_m",
                message="1) Room length (m)",
                validate=_positive_float,
                default="4.0",
            ),
            inquirer.Text(
                "width_m",
                message="1) Room width (m)",
                validate=_positive_float,
                default="3.0",
            ),
            inquirer.Text(
                "height_m", message="1) Room height (m)", validate=_height, default="2.8"
            ),
            inquirer.List(
                "wall_material",
                message="2) Wall material",
                choices=_material_choices(WALL_MATERIALS),
            ),
            inquirer.List(
                "ceiling_material",
                message="3) Ceiling material",
                choices=_material_choices(CEILING_MATERIALS),
            ),
            inquirer.List(
                "floor_material",
                message="4) Floor material",
                choices=_material_choices(FLOOR_MATERIALS),
            ),
            inquirer.Text(
                "occupants",
                message="5) Number of occupants",
                validate=_non_negative_int,
                default="2",
            ),
            inquirer.Text(
                "windows",
                message="6) Number of windows",
                validate=_non_negative_int,
                default="1",
            ),
            inquirer.List(
                "appliance_load",
                message="7) Estimated appliance load",
                choices=[
                    ("None", "none"),
                    ("Light (TV + lights)", "light"),
                    ("Heavy (PC + TV + lights)", "heavy"),
                ],
                default="light",
            ),
            inquirer.Confirm(
                "top_floor",
                message="8) Is this a top floor / directly under the roof?",
                default=False,
            ),
            inquirer.Confirm(
                "west_facing",
                message="9) Is the room west-facing or gets afternoon sun?",
                default=False,
            ),
            inquirer.Text(
                "desired_temp",
                message="10) Desired indoor temperature (°C)",
                validate=_temperature,
                default="24",
            ),
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            console.print("\n[bold yellow]Cancelled by user.[/bold yellow]")
            return

        windows_count = int(answers["windows"])
        windows_area_m2 = windows_count * WINDOW_AREA_PER_UNIT_M2
        appliance_watts = APPLIANCE_LOAD_OPTIONS[answers["appliance_load"]]

        result = compute_total_btu(
            length=float(answers["length_m"]),
            width=float(answers["width_m"]),
            height=float(answers["height_m"]),
            wall_material=answers["wall_material"],
            ceiling_material=answers["ceiling_material"],
            floor_material=answers["floor_material"],
            occupants=int(answers["occupants"]),
            windows=windows_area_m2,
            appliances_watts=appliance_watts,
            top_floor=bool(answers["top_floor"]),
            west_facing=bool(answers["west_facing"]),
            desired_temp=float(answers["desired_temp"]),
            outdoor_temp=35.0,
        )

        room_volume = (
            float(answers["length_m"]) * float(answers["width_m"]) * float(answers["height_m"])
        )
        floor_area = result["areas"]["floor_area_m2"]

        summary = Table(show_header=False, box=None, pad_edge=False)
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", justify="right")
        summary.add_row("Room Volume", f"{room_volume:.2f} m3")
        summary.add_row("Total BTU/h", f"{result['total_btu_per_hour']:,.0f}")
        summary.add_row(
            "Recommended HP",
            f"[bold green]{result['hp']['recommended_hp']:.2f} HP[/bold green]",
        )
        summary.add_row("Next Size Up HP", f"{result['hp']['next_size_up_hp']:.2f} HP")

        breakdown = Table(title="Heat Gain Breakdown", header_style="bold blue")
        breakdown.add_column("Surface/Load", style="cyan")
        breakdown.add_column("Area/Count", justify="right")
        breakdown.add_column("U-Value (W/m²·K)", justify="right")
        breakdown.add_column("BTU/h", justify="right", style="magenta")

        wall_meta = WALL_MATERIALS[answers["wall_material"]]
        ceiling_meta = CEILING_MATERIALS[answers["ceiling_material"]]
        floor_meta = FLOOR_MATERIALS[answers["floor_material"]]

        breakdown.add_row(
            "Wall",
            f"{result['areas']['wall_area_m2']:.2f} m2",
            f"{wall_meta['u_value']:.2f}",
            f"{result['breakdown_btu_per_hour']['wall_heat_gain']:,.0f}",
        )
        breakdown.add_row(
            "Ceiling",
            f"{result['areas']['ceiling_area_m2']:.2f} m2",
            f"{ceiling_meta['u_value']:.2f}",
            f"{result['breakdown_btu_per_hour']['ceiling_heat_gain']:,.0f}",
        )
        breakdown.add_row(
            "Floor",
            f"{result['areas']['floor_area_m2']:.2f} m2",
            f"{floor_meta['u_value']:.2f}",
            f"{result['breakdown_btu_per_hour']['floor_heat_gain']:,.0f}",
        )
        breakdown.add_row(
            "Occupants",
            f"{int(answers['occupants'])} person(s)",
            "-",
            f"{result['breakdown_btu_per_hour']['occupants']:,.0f}",
        )
        breakdown.add_row(
            "Windows",
            f"{windows_count} window(s) / {windows_area_m2:.2f} m2",
            f"{WINDOW_U_VALUE:.2f}",
            f"{result['breakdown_btu_per_hour']['window_heat_gain']:,.0f}",
        )
        breakdown.add_row(
            "Appliances",
            f"{answers['appliance_load'].title()} ({appliance_watts:.0f} W)",
            "-",
            f"{result['breakdown_btu_per_hour']['appliances']:,.0f}",
        )

        note = _recommendation_note(
            recommended_hp=result["hp"]["recommended_hp"],
            next_size_up_hp=result["hp"]["next_size_up_hp"],
            top_floor=bool(answers["top_floor"]),
            west_facing=bool(answers["west_facing"]),
        )

        alerts: list[str] = []
        if result["total_btu_per_hour"] > HIGH_LOAD_WARNING_BTU:
            alerts.append(
                "[bold yellow]High load warning:[/bold yellow] Total exceeds 30,000 BTU/h. "
                "Consider multiple AC units and split the room into zones."
            )
        if floor_area < SMALL_ROOM_MAX_AREA_M2:
            alerts.append(
                "[bold green]Small room tip:[/bold green] Area is under 10 m2; "
                "a 0.5 HP window-type unit may be enough."
            )

        group_items: list[object] = [
            summary,
            "",
            breakdown,
            "",
            f"[yellow]Recommendation:[/yellow] {note}",
            f"[dim]Window count converted using {WINDOW_AREA_PER_UNIT_M2:.1f} m2/window.[/dim]",
        ]
        if alerts:
            group_items.extend(["", *alerts])

        result_panel = Panel(
            Group(*group_items),
            title="[bold cyan]Aircon Sizing Result[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )

        console.print()
        console.print(result_panel)

        recalculate = inquirer.prompt(
            [
                inquirer.Confirm(
                    "recalculate",
                    message="Recalculate with different inputs?",
                    default=True,
                )
            ]
        )
        if not recalculate or not recalculate["recalculate"]:
            break


if __name__ == "__main__":
    run()

