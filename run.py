import argparse
import random
from pathlib import Path
from unified_planning.plans import SequentialPlan
from planner import solve_pddl
from vis import Map
from exec import Exec

RUNS = 10


def run_n_times(map, growth_factor: int = 5, step: float = 10.0,
                rrt_n: int = 5000, rrt_star: bool = False) -> None:
    output_dir = Path(__file__).resolve().parent / "generated_problems"
    output_dir.mkdir(exist_ok=True)
    for run in range(RUNS):
        map.randomly_generate_obstacles(growth_factor=growth_factor)

        '''
        Randomly generate the problem.
        '''
        pixels = map.get_pixels()
        width = len(pixels[0])
        available = [
            row * width + column
            for row, values in enumerate(pixels)
            for column, value in enumerate(values)
            if value != 0
        ]
        names = ("Start", "Chamber1", "Chamber2", "Chamber3", "EndPortal")
        selected = random.sample(available, len(names))
        map.locations = {
            name: (pixel % width, pixel // width)
            for name, pixel in zip(names, selected)
        }
        map.cake = random.choice(names)
        map.cube = random.choice(names)
        problem = (
            '(define (problem portal)\n'
            '\t(:domain portal)\n'
            '\t(:objects Start Chamber1 Chamber2 Chamber3 - location\n'
            '              EndPortal - portal\n'
            '              cake - item\n'
            '              cube - container)\n'
            '\t(:init (robot_at Start)\n'
            f'\t\t   (item_at cake {map.cake})\n'
            f'           (item_at cube {map.cube})\n'
            '           (gripper_free))\n'
            '\t(:goal (or (and (is_portaled cake) (is_portaled cube))\n'
            '               (and (is_portaled cube) (item_contains cube cake))))\n'
            ')'
        )
        (output_dir / f"{run + 1}problem.pddl").write_text(problem, encoding="utf-8")

        '''
        draw the problem
        '''
        map.executor = None
        map.canvas.delete("robot")
        map.draw_locations()
        map.window.update_idletasks()

        '''
        solve the problem
        '''
        domain_file = output_dir.parent / "domain.pddl"
        result = (
            solve_pddl(
                str(domain_file),
                str(output_dir / f"{run + 1}problem.pddl"),
            )
            if domain_file.is_file() else SequentialPlan([])
        )
        plan = (
            "\n".join(
                f"{step}. {' '.join(str(action).split())}"
                for step, action in enumerate(result.actions, start=1)
            )
            if result is not None else "No plan found."
        )
        plan_output = map.plan_output
        plan_output.configure(state="normal")
        plan_output.delete("1.0", "end")
        plan_output.insert("end", f"Run {run + 1}\n\n{plan}")
        plan_output.configure(state="disabled")
        Exec(result, map, step=step, rrt_n=rrt_n, rrt_star=rrt_star).run()
        map.window.update_idletasks()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    def dimension(value: str) -> int:
        value = int(value)
        if value < 5:
            raise argparse.ArgumentTypeError("dimensions must be at least 5")
        return value
    parser.add_argument("--step", type=float, default=10.0,
                        help="RRT step size (default: 10.0)")
    parser.add_argument("--rrt_n", "--rrt-n", type=int, default=5000,
                        help="Number of random points sampled in RRT (default: 5000)")
    parser.add_argument("--rrt_star", action="store_true", default=False,
                        help="Use RRT* instead of RRT")
    parser.add_argument("--growth-factor", type=int, choices=range(6), default=5,
                        help="Maximum obstacle growth factor (0 to 5; default: 5)")
    parser.add_argument("--dim", nargs=2, type=dimension, metavar=("X", "Y"),
                        help="X and Y dimensions (each at least 5)")
    parser.add_argument("--runs", type=int, default=RUNS, help="Number of runs")
    args = parser.parse_args()
    if any(dimension < 5 for dimension in args.dim):
        parser.error("both dimensions must be at least 5")
    RUNS = args.runs

    map = Map()
    print("map initialized", flush=True)
    map.set_grid(*args.dim)
    run_n_times(map, growth_factor=args.growth_factor,
                step=args.step, rrt_n=args.rrt_n, rrt_star=args.rrt_star)
    map.show()
