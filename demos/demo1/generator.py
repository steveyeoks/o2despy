from o2despy.sandbox import Sandbox
from o2despy.action import Action
from o2despy.entity import Entity
from datetime import timedelta
import random


class Generator(Sandbox):
    def __init__(self, hourly_rate):
        super().__init__()
        self.hourly_rate = hourly_rate
        self.count = self.add_hour_counter()
        self.on_generate = Action(Entity)

        self.schedule(self.generate)

    def generate(self):
        if self.count.last_count > 0:
            load = Entity()
            print("{}\t{}\tGenerate. Count: {}. Load: {}".format(self.clock_time, type(self).__name__,
                                                                 self.count.last_count, load.id))
            self.on_generate.invoke(load)
        self.count.observe_change(1)
        self.schedule(self.generate, timedelta(hours=round(random.expovariate(self.hourly_rate), 2)))
