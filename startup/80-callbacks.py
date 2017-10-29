print(__file__)

# custom callbacks

plan_documents = {}

def custom_callback(key, document):
	"""keep all documents from recent plan in memory"""
	global plan_documents
	if key == "start":
		plan_documents = {key: document}
	elif key in ("descriptor", "event"):
		if key not in plan_documents:
			plan_documents[key] = []
		plan_documents[key].append(document)
	elif key == "stop":
		plan_documents[key] = document
		print("all documents from last plan in variable: plan_documents")
		print("exit status:", document["exit_status"])
		if "descriptor" in plan_documents:
			print("# descriptor(s):", len(plan_documents["descriptor"]))
		if "event" in plan_documents:
			print("# event(s):", len(plan_documents["event"]))
	else:
		print("custom_callback (unhandled):", key, document)
	return

callback_db['custom_callback'] = RE.subscribe(custom_callback)
