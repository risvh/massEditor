class State:
    def __init__(self):
        self.categories = {}
        self.objects = {}
        self.names = {}
        self.transitions = {}
        self.raw_transitions = {}
        self.depths = {}
        
        self.sprite_tags = set()
        self.object_property_dataTypes = {}
        
state = State()