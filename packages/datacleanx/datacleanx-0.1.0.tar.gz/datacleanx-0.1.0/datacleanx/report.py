import json

class DataCleanerReport:
    def __init__(self, report_dict):
        self.report = report_dict

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.report, f, indent=4)
