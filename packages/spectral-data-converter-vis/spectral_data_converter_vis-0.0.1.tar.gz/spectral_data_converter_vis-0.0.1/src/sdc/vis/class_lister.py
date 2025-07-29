from typing import List, Dict


def list_classes() -> Dict[str, List[str]]:
    return {
        "seppl.io.Reader": [
            "sdc.vis.reader",
        ],
        "seppl.io.Filter": [
            "sdc.vis.filter",
        ],
        "seppl.io.Writer": [
            "sdc.vis.writer",
        ],
    }
