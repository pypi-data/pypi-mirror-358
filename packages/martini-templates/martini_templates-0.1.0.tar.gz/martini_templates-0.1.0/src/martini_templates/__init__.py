import argparse
import importlib.resources

import jinja2


def generate_mdp(template_path, output_path, **kwargs):
    with importlib.resources.open_text(
        "martini_templates", template_path
    ) as template_file:
        template = jinja2.Template(template_file.read())
        rendered = template.render(**kwargs)
    with open(output_path, "w") as output_file:
        output_file.write(rendered)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Martini MDP files.")
    parser.add_argument(
        "--nvt",
        action="store_true",
        help="Generate NVT file (20 ns, no pressure coupling).",
    )
    parser.add_argument(
        "--npt",
        action="store_true",
        help="Generate NPT file (50 ns, pressure coupling).",
    )
    parser.add_argument(
        "--em", action="store_true", help="Generate energy minimisation file."
    )
    parser.add_argument(
        "--all", action="store_true", help="Generate all files (NVT, NPT, EM)."
    )
    parser.add_argument(
        "--ref_t",
        type=float,
        default=298,
        help="Reference temperature (default: 298 K).",
    )
    parser.add_argument(
        "--ref_p", type=float, default=1, help="Reference pressure (default: 1 bar)."
    )
    parser.add_argument(
        "--output", type=str, help="Custom output filename (overrides default naming)."
    )

    args = parser.parse_args()

    if args.all or args.nvt:
        output_name = args.output or "martini_nvt.mdp"
        generate_mdp(
            "template.mdp.jinja",
            output_name,
            ref_t=args.ref_t,
            ref_p=None,
            time=20,
            energy_minimisation=False,
        )

    if args.all or args.npt:
        output_name = args.output or "martini_npt.mdp"
        generate_mdp(
            "template.mdp.jinja",
            output_name,
            ref_t=args.ref_t,
            ref_p=args.ref_p,
            time=50,
            energy_minimisation=False,
        )

    if args.all or args.em:
        output_name = args.output or "martini_em.mdp"
        generate_mdp(
            "template.mdp.jinja",
            output_name,
            ref_t=None,
            ref_p=None,
            time=0,
            energy_minimisation=True,
        )
