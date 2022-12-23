import mesa, mesa_geo as mg, math
from shapely.geometry import Point, LineString

class Stadtteil(mg.GeoAgent):
    def __init__(self, unique_id, model, geometry, crs):
        super().__init__(unique_id, model, geometry, crs)

class StadtradStation(mg.GeoAgent):
    def __init__(self, unique_id, model, geometry, crs):
        super().__init__(unique_id, model, geometry, crs)

class Radfahrerin(mg.GeoAgent):
    def __init__(self, unique_id, model, geometry, crs, speed=0.002, destination=None): 
        super().__init__(unique_id, model, geometry, crs)
        self.speed = speed
        self.destination = destination
        self.info = ""

    def step(self):

        # Vary speed randomly
        self.speed = max(0, self.speed + self.random.uniform(-0.0005, 0.0005))


        # See if we are at the destination
        if self.destination is not None:
            self.info = "I have a destination"
            # If we are, stop moving
            if self.geometry.distance(self.destination.geometry) < self.speed:
                self.destination = None
            # If not, move towards it
            else:
                self.move_towards_destination()
        
        # If there is no destination, pick one
        if self.destination is None:
            self.info = "Looking for a destination"
            allStations = [
                agent for agent in self.model.space.agents if isinstance(agent, StadtradStation)
            ]
            randomStation = self.random.randint(0, len(allStations) - 1)
            self.destination = allStations[randomStation]

    def move_towards_destination(self):
        self.geometry = LineString([self.geometry, self.destination.geometry]).interpolate(self.speed)