from db import PushToMongo
import datetime
from datetime import datetime, timezone

from llm_part.gemma3 import LLMProcessor

if __name__ == "__main__":
    mongo_uploader = PushToMongo(col="raw_data")
    mongo_uploader.start_watcher_thread()
    model = LLMProcessor()

   

    # # Insert example doc
    # test_doc = {
    #     "location": "Chennai",
    #     "severity": "low",
    #     "description": "Sample update test",
    #     "processed_by": "AI Analysis System",
    #     "recommendations": ["Stay informed", "No action required"]
    # }
    # mongo_uploader.push_json(test_doc)

    # Keep the main thread alive to see real-time inserts
    import time
    while True:
         result = mongo_uploader.get_next_insert(timeout=3)
         if result:
            print("📥 Received from watcher thread:\n", result)
            response = model.generate_response(result)
            result = ""

         else:
            print(" No insert detected in time.")

         time.sleep(2)
