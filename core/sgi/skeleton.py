class Organ:
    """
    Base Tissue for all SGI Components.
    """
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.active = True
        
    def status(self):
        return f"[{self.name}] Health: {self.health}% | Active: {self.active}"

class Body:
    """
    The Vessel.
    """
    def __init__(self):
        self.organs = {}
        
    def add_organ(self, organ):
        self.organs[organ.name] = organ
        
    def check_vitals(self):
        report = []
        for name, organ in self.organs.items():
            report.append(organ.status())
        return "\n".join(report)

# Singleton Body
sgi_body = Body()
