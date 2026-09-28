(define (problem portal)
	(:domain portal)
	(:objects Start Chamber1 Chamber2 Chamber3 - location
              EndPortal - portal
              cake - item
              cube - container)
	(:init (robot_at Start)
		   (item_at cake Chamber1)
           (item_at cube Chamber2)
           (gripper_free))
	(:goal (or (and (is_portaled cake) (is_portaled cube))
               (and (is_portaled cube) (item_contains cube cake))))
)