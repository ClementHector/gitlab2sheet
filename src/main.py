import functions_framework
import logging

logger = logging.getLogger()


@functions_framework.http
def push_to_sheet(request):
    logging.info("Receive Event from gitlab")
    data = request.json
    logging.info(f"Event is {data['event_type']}")
    return {"status": True}
