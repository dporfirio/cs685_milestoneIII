import math
import random


class Exec:
    """Replay planner actions. Ground z=0, carried z=1, portaled positions=None."""

    def __init__(self, plan, map, step: float = 10.0, rrt_n: int = 5000,
                 rrt_star: bool = False):
        self.plan, self.map = plan, map
        self.step, self.rrt_n = step, rrt_n
        self.rrt_star = rrt_star
        self.locations = {name.lower(): name for name in map.locations}
        columns, rows = map.grid_size
        if columns <= 0 or rows <= 0:
            raise ValueError("Set the grid before planning a path")
        cell_width, cell_height = 511 / columns, 383 / rows
        self.obstacle_pixels = {
            (x, y)
            for column, row in map.obstacles
            for x in range(math.floor(column * cell_width),
                           math.floor((column + 1) * cell_width) + 1)
            for y in range(math.floor(row * cell_height),
                           math.floor((row + 1) * cell_height) + 1)
        }
        self.robot_location = "Start"
        self.held = None
        self.contained = {}
        self.portaled = set()
        self.active_portals = set()
        self.item_locations = {item: getattr(map, item) for item in ("cake", "cube")}
        self.item_positions = {}
        map.executor = self
        self._sync()

    def _position(self, location):
        """
        Helper function for sync
        """
        point = tuple(self.map.locations[location])
        return point if len(point) == 3 else (*point, 0)

    def _sync(self):
        """
        Store each position in the visualizer for later GUI updates
        """
        self.robot_position = self._position(self.robot_location)

        def position(item):
            if item in self.portaled:
                return None
            if item in self.contained:
                return position(self.contained[item])
            if item == self.held:
                x, y, z = self.robot_position
                return (x, y, z + 1)
            return self._position(self.item_locations[item])

        for item in self.item_locations:
            self.item_positions[item] = position(item)
            setattr(self.map, item, self.item_locations[item]
                    if item != self.held and item not in self.contained
                    and item not in self.portaled else None)

    def run(self):
        """
        This is the main task plan execution loop.

        Given a task plan (self.plan), run through and execute each action in the plan.
        """
        self.map.draw_locations()
        self.map.process_events(force=True)
        actions = self.plan.actions if self.plan is not None else ()
        if not actions:
            return
        self.map.start_execution()
        for index, action in enumerate(actions):
            self.map.begin_action(index)
            name = action.action.name.lower()
            args = [str(parameter).lower() for parameter in action.actual_parameters]
            if name == "move_to":
                self.robot_location = self.locations[args[1]]
            elif name == "grab":
                self.held = args[0]
            elif name == "put_at_location":
                self.item_locations[args[0]] = self.locations[args[1]]
                self.held = None
            elif name == "put_in_container":
                self.contained[args[0]] = args[1]
                self.held = None
            elif name == "put_in_portal":
                self.portaled.add(args[0])
                self.item_locations[args[0]] = self.locations[args[1]]
                self.held = None
            elif name == "activate":
                self.active_portals.add(self.locations[args[0]])
            else:
                raise ValueError(f"Unsupported action: {name}")
            self._sync()
            self.map.draw_locations()
            if name == "move_to":
                path = self.rrt(self.map.locations[self.locations[args[0]]],
                                self.map.locations[self.locations[args[1]]],
                                self.obstacle_pixels,
                                511, 383, step=self.step, n=self.rrt_n,
                                star=self.rrt_star)
                if path:
                    self.map.draw_path(path)
                else:
                    self.map.show_message("No path found!")
            self.map.wait_for_next_action()
        self.map.finish_execution()

    """
    CS 685: FILL THIS IN
    You can do whatever you need to do here to satisfy the rubric.
    Feel free to add any helper functionality (e.g., visualization functionality), and
    you can even create a new RRT file if you would prefer.
    """
    def rrt(self,
            i: tuple[float, float],
            g: tuple[float, float],
            obstacles: set[tuple[int, int]],
            xdim: int,
            ydim: int,
            step: float,
            n: int,
            star: bool = False) -> list[tuple[float, float]] | None:
        """
        Return a collision-free RRT path (RRT* if star is True), or None.
        i: start coordinate
        g: end coordinate
        obstacles: a set of pixels that represent obstacles
        xdim: x pixel dimensions
        ydim: y pixel dimensions
        step: number of pixels that the tree is allowed to step forward
        n: number of iterations in RRT/RRT*
        star: boolean, whether or not to use RRT*
        """
        return []
