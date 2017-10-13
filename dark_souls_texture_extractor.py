import texture_extractor as te

import logging
log = logging.getLogger(__name__)
                
if __name__ == "__main__":
    LOG_FILE = "unpackTPF-latestlog.txt"
    
    with open(LOG_FILE, "w") as f:
        logging.basicConfig(stream=f, level=logging.INFO)
        try:
            te.create_extract_dirs()
            te.attempt_unpack()
        except Exception:
            log.exception("Encountered critical error in unpacking.") 
