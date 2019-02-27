print(__file__)

# custom callbacks

import apstools.callbacks
import apstools.filewriters


#doc_collector = apstools.callbacks.DocumentCollectorCallback()
#callback_db['doc_collector'] = RE.subscribe(doc_collector.receiver)

specwriter = apstools.filewriters.SpecWriterCallback()
specwriter.newfile(os.path.join("/tmp", specwriter.spec_filename))
callback_db['specwriter'] = RE.subscribe(specwriter.receiver)
print("SPEC data file:", specwriter.spec_filename)
