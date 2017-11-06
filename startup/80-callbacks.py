print(__file__)

# custom callbacks


class CustomCallbackCollector(object):
    """
    My BlueSky support to collect *all* documents emitted
    """
    
    def __init__(self):
        self.documents = {}

    def receiver(self, key, document):
        """keep all documents from recent plan in memory"""
        if key == "start":
            self.documents = {key: document}
        elif key in ("descriptor", "event"):
            if key not in self.documents:
                self.documents[key] = []
            self.documents[key].append(document)
        elif key == "stop":
            self.documents[key] = document
            print("exit status:", document["exit_status"])
            if "descriptor" in self.documents:
                print("# descriptor(s):", len(self.documents["descriptor"]))
            if "event" in self.documents:
                print("# event(s):", len(self.documents["event"]))
        else:
            print("custom_callback (unhandled):", key, document)
        return


cb_collector = CustomCallbackCollector()
callback_db['cb_collector'] = RE.subscribe(cb_collector.receiver)
