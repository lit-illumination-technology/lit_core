class History:
    def __init__(self, commands):
        self.ordered_events = []
        self.current_index = 0
        self.commands = commands

    def save(self, state):
        self.ordered_events.append(HistoryEvent(state))
        self.current_index = len(self.ordered_events) - 1

    def back(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.ordered_events[self.current_index].restore(self.commands)
            return True
        else:
            return False

    def forward(self):
        if self.current_index < len(self.ordered_events) - 1:
            self.current_index += 1
            self.ordered_events[self.current_index].restore(self.commands)
            return True
        else:
            return False


class HistoryEvent:
    def __init__(self, state):
        self.state = state

    def restore(self, commands):
        commands.stop_all()
        for effect in self.state:
            properties = {
                "ranges": effect["sections"],
                "opacity": effect["opacity"],
                "overlayed": True,
            }
            commands._start_effect(
                effect["effect_name"],
                effect["effect_state"],
                properties,
                effect["transaction_id"],
            )
