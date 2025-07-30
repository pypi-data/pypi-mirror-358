from enum import Enum
from os import getlogin

class Settings(Enum):

    TOOL_NAME= "Texas_Extraction"
    VERSION= 1.1

    CHUNK_SIZE = 10              # Number of URLs per chunk
    MAX_THREADS = 20              # Download threads
    MAX_POOLS = 4                 # Parsing processes
    MAX_MAIN_PROCESSES = 2        # Chunk-level parallelism

    LOG_FILE = r"C:\Users\{}\Documents\logger.log".format(getlogin())

    AUTO_ENGINE_SERVER= r"\\10.199.104.160"

    #data base creadintion
    ORC_USERNAME= "A157336"
    PASSWORD= "hamdiemada157336"
    HOST= "10.199.104.126"
    SID=    "analytics"
    DB_URL = f"oracle+cx_oracle://{ORC_USERNAME}:{PASSWORD}@{HOST}/{SID}"