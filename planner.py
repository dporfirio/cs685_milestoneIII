import sys

import unified_planning as up
from unified_planning.io import PDDLReader
from unified_planning.shortcuts import OneshotPlanner


def solve_pddl(domain_file: str, problem_file: str):
    # Read the PDDL domain + problem.
    reader = PDDLReader()
    problem = reader.parse_problem(domain_file, problem_file)

    print(f"Loaded problem: {problem.name}")
    print(f"Problem kind: {problem.kind}")

    with OneshotPlanner(name="fast-downward-opt", problem_kind=problem.kind) as planner:
        print(f"Using planner: {planner.name}")

        result = planner.solve(problem)

        if result.plan is None:
            print(f"No plan found. Planner status: {result.status}")
            return None

        print(f"Planner status: {result.status}")
        print("\nPlan:")

        for i, action in enumerate(result.plan.actions):
            print(f"{i}: {action}")

        return result.plan


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} DOMAIN.pddl PROBLEM.pddl")
        sys.exit(1)

    domain_file = sys.argv[1]
    problem_file = sys.argv[2]

    solve_pddl(domain_file, problem_file)