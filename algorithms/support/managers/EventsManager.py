from algorithms.support.dih_search import dih_search


class EventManager:
    def __init__(self):
        self.events = []

    def get_insert_id(self, event_time):
        insert_id = dih_search(
            event_time, 0, len(self.events) - 1,
            key=lambda i: self.events[i][0]
        )
        return insert_id

    def add_event(self, event_time, event_type, obj_id):
        event = (event_time, event_type, obj_id)
        if len(self.events) > 0:
            self.events.insert(self.get_insert_id(event_time), event)
        else:
            self.events.append(event)

    def delete_event(self, del_event_type, del_obj_id):
        for i in range(len(self.events)):
            _, event_type, obj_id = self.events[i]
            if del_event_type == event_type and del_obj_id == obj_id:
                self.events.pop(i)
                break

    def get_nearest_event(self):
        return self.events.pop(0)

    def all_events_over(self):
        return False if self.events else True
