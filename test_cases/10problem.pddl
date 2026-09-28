(define (problem portal)
	(:domain portal)
	(:objects Start Chamber1 Chamber2 Chamber3 - location
              EndPortal - portal
              cake - item
              cube - container)
	(:init (robot_at Start)
		   ;(item_at cake EndPortal)
           (item_at cube EndPortal)
           (robot_holding cake))
	(:goal (or (and (is_portaled cake) (is_portaled cube))
               (and (is_portaled cube) (item_contains cube cake))))
)