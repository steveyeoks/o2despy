from o2despy.sandbox import Sandbox


class Queue(Sandbox):
    def __init__(self):
        super().__init__()
        self.number_waiting = self.add_hour_counter()
        self.queue = list()

    def enqueue(self, load):
        self.number_waiting.observe_change(1)
        self.queue.append(load)
        print("{0}\t{1}\tEnqueue. #Waiting: {2}, Load: {3}".format(self.clock_time,
                                                        type(self).__name__,
                                                        self.number_waiting.last_count,
                                                                   load.id))

    def dequeue(self, load):
        self.number_waiting.observe_change(-1)
        self.queue.remove(load)
        print("{0}\t{1}\tDequeue. #Waiting: {2}, Load: {3}".format(self.clock_time,
                                                        type(self).__name__,
                                                        self.number_waiting.last_count,
                                                                   load.id))
