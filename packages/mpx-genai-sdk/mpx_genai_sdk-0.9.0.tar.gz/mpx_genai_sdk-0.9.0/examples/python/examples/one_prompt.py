# We will use the Masterpiece X SDK to generate a 3D object from a simple text prompt

import time

from dotenv import load_dotenv
from mpx_genai_sdk import Masterpiecex
from mpx_genai_sdk.types import StatusResponseObject

load_dotenv()
mpx_client = Masterpiecex()

# Get the status of a Request
# Wait until the object has been generated (status = 'complete')
def retrieve_request_status(request_id) -> StatusResponseObject: 
  status_resp = mpx_client.status.retrieve(request_id)
  print(status_resp)
  # Wait until the object has been generated (status = 'complete')
  while status_resp.status not in ["complete", "failed"]:
      time.sleep(10)
      status_resp = mpx_client.status.retrieve(request_id)
      print ('*', end='')
  print('') # clears waiting indicators
  print(status_resp)
  return status_resp

# Ensure the connection is working
print("Connection test:")
connection_test = mpx_client.connection_test.retrieve()
print(connection_test)

# Generate a 3D object from a simple text prompt
general_response = mpx_client.functions.create_general(
    prompt= "cute dog"
)
print(general_response)

status_resp = retrieve_request_status(general_response.request_id)
print(f'generated response: {status_resp}')
print(f'GLB object url: {status_resp.outputs.glb}')