import warnings
warnings.filterwarnings("ignore")

import mesa, os, mesa_geo as mg, geopandas as gpd, math, random
from shapely.geometry import Point

from agent import *

# Set to current directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load Stadtteile
stadtteile = gpd.read_file('data/bevoelkerung_stadtteile.json')
stadtraeder = gpd.read_file('data/stadtrad_stationen.json')


def generate_random_point_in_polygon(polygon):
    min_x, min_y, max_x, max_y = polygon.bounds
    while True:
        pnt = Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
        if polygon.contains(pnt):
            return pnt


class GeoModel(mesa.Model):
    def __init__(self, agents_per_10000_inhabitants):
        self.space = mg.GeoSpace(crs="epsg:4326")
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True

        ac = mg.AgentCreator(agent_class=Stadtteil, model=self)
        agents = ac.from_GeoDataFrame(gdf=stadtteile, unique_id="stadtteil")
        self.space.add_agents(agents)

        ac = mg.AgentCreator(agent_class=StadtradStation, model=self)
        agents = ac.from_GeoDataFrame(gdf=stadtraeder, unique_id="name")
        self.space.add_agents(agents)

        ac = mg.AgentCreator(agent_class=Radfahrerin, model=self,crs="epsg:4326")

        for stadtteil in stadtteile["stadtteil"]:

            # Create Radfahrer based on the population of the Stadtteil
            population = stadtteile[stadtteile["stadtteil"] == stadtteil]["bev"].values[0]

            for i in range(math.floor(population / 10000) * agents_per_10000_inhabitants):
                location = generate_random_point_in_polygon(stadtteile[stadtteile["stadtteil"] == stadtteil]["geometry"].values[0])
                agent = ac.create_agent(location, stadtteil + "-" + str(i))
                self.space.add_agents([agent])
                self.schedule.add(agent)

        self.datacollector = mesa.DataCollector(
            model_reporters={}, agent_reporters={"geometry": "geometry", "Geschwindigkeit": "speed", "Info": "info"}
        )
    
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

        

