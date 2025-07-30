from Texas_Extraction.helper.config import Settings # Adjust import path accordingly
from os import getlogin
from datetime import datetime

def insert_query(
    total_rows: int,
    num_done: int,
    num_broken: int,
    runningtime: int
) -> str:
    """Builds insert query when starting resize process."""
    return f"""
        INSERT INTO CUSTOMS_STATUS (
            USER_ID,
            DATE_TIME,
            NUM_ROWS,
            NUM_FOUND,
            NUM_CHECKS,
            RUNTIME,
            TOOL_USED,
            VERSION,
            COMMENTS
        ) VALUES (
            '{getlogin()}', '{datetime.now().date()}', '{total_rows}', '{num_done}', '{num_broken}','{runningtime}',
            '{Settings.TOOL_NAME.value}', '{Settings.VERSION.value}', 'Counts per PDF'
        )
    """

