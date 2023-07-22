from o2despy.sandbox import Sandbox
from o2despy.action import Action
from o2despy.entity import Entity
from datetime import timedelta
import random


class Server(Sandbox):
    def __init__(self, capacity, hourly_service_rate):
        super().__init__()
        self.capacity = capacity
        self.hourly_service_rate = hourly_service_rate
        self.number_pending = self.add_hour_counter()
        self.number_in_service = self.add_hour_counter()
        self.pending_list = list()
        self.service_list = list()
        self.on_start = Action(Entity)

    def request_to_start(self, load):
        self.number_pending.observe_change(1)
        self.pending_list.append(load)
        print("{0}\t{1}\tRequestToStart. #Pending: {2}. #In-Service: {3}. Load: {4}".format(self.clock_time, type(self).__name__,
                                                                                 self.number_pending.last_count,
                                                                                 self.number_in_service.last_count,
                                                                                load.id))
        if self.number_in_service.last_count < self.capacity:
            self.schedule(self.start, load=load, clock_time=timedelta(seconds=0))

    def start(self, load):
        self.number_pending.observe_change(-1)
        self.pending_list.remove(load)
        self.number_in_service.observe_change(1)
        self.service_list.append(load)
        print("{0}\t{1}\tStart. #Pending: {2}. #In-Service: {3}. Load: {4}".format(self.clock_time, type(self).__name__,
                                                                        self.number_pending.last_count,
                                                                        self.number_in_service.last_count,
                                                                        load.id))
        self.schedule(self.finish, load=load, clock_time=timedelta(hours=round(random.expovariate(self.hourly_service_rate), 2)))
        self.on_start.invoke(load)

    def finish(self, load):
        self.number_in_service.observe_change(1)
        self.service_list.remove(load)
        print("{0}\t{1}\tStart. #Pending: {2}. #In_Service: {3}. Load: {4}".format(self.clock_time, type(self).__name__,
                                                                        self.number_pending.last_count,
                                                                        self.number_in_service.last_count,
                                                                        load.id))
        if self.number_pending.last_count > 0:
            next_load = self.pending_list[0]
            self.start(next_load)

