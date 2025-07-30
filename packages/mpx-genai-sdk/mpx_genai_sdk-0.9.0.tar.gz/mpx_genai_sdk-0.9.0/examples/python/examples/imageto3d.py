# We will use the Masterpiece X SDK to generate a 3D object from an image
# Steps:
# 1. Create an asset id for the image you want to upload
# 2. Upload the image to the created asset url
# 3. Create a request to generate a 3D object from the uploaded image
# 4. Wait for the request to complete
# 5. Retrieve the generated 3D object

import time

from dotenv import load_dotenv
from mpx_genai_sdk import Masterpiecex
from mpx_genai_sdk.types import StatusResponseObject


load_dotenv()
client = Masterpiecex()

# Get the status of a Request
# Wait until the object has been generated (status = 'complete')
def retrieve_request_status(request_id) -> StatusResponseObject:
  status_resp = client.status.retrieve(request_id)
  print(status_resp)
  # Wait until the object has been generated (status = 'complete')
  while status_resp.status not in ["complete", "failed"]:
      time.sleep(10)
      status_resp = client.status.retrieve(request_id)
      print ('*', end='')
  print('') # clears waiting indicators
  print(status_resp)
  return status_resp

# Ensure the connection is working
print("Connection test:")
connection_test = client.connection_test.retrieve()
print(connection_test)

# Create an asset id for the image you want to upload
print("Create asset Id:")
asset_id_response = client.assets.create(
    description="Robot toy",
    name="robot.png",
    type="image/png",
)
upload_url = asset_id_response.asset_url
asset_id = asset_id_response.request_id

print(f'Asset id: {asset_id}')
print(f'asset upload url: {upload_url}')

# Upload the image to the created asset url
image_path = './robot.png'
headers = {
    'Content-Type': 'image/png',  # make sure it matches the type identified in the asset id creation
}

# Open the image file in binary mode and upload it
print("Uploading image...")
with open(image_path, 'rb') as image_file:
    image_data = image_file.read()
    response = requests.put(upload_url, data=image_data, headers=headers)

# Print the response from the server
print(f'Upload complete. Reponse: ({response.status_code})')  # Should be 200

# Create a request to generate a 3D object from the uploaded image
print("Creating the generate request:")
imageto3d_resp = client.functions.imageto3d(
    image_request_id = asset_id,
    seed=1,
    texture_size=1024,
)
print(imageto3d_resp)
imageto3d_request_id = imageto3d_resp.request_id
print(f'mesh genrequest_id: {imageto3d_request_id}')

# wait for the request to complete
imageto3d_response: StatusResponseObject = retrieve_request_status(imageto3d_request_id)
print(f'status_response: {imageto3d_response}')

# Retrieve the generated 3D object urls
# example response
# StatusResponseObject(outputs=Outputs(fbx='https://storage.googleapis.com/processors-bucket.masterpiecex.com/api-sessions/google-oauth2|106513587070086030188/unknown_appid/ml-requests_OGSsSuHXIN8YLzenRbgN/exports/output.fbx', glb='https://storage.googleapis.com/processors-bucket.masterpiecex.com/api-sessions/google-oauth2|106513587070086030188/unknown_appid/ml-requests_OGSsSuHXIN8YLzenRbgN/exports/output.glb', thumbnail='https://storage.googleapis.com/processors-bucket.masterpiecex.com/api-sessions/google-oauth2|106513587070086030188/unknown_appid/ml-requests_OGSsSuHXIN8YLzenRbgN/exports/thumbnail.png', usdz='https://storage.googleapis.com/processors-bucket.masterpiecex.com/api-sessions/google-oauth2|106513587070086030188/unknown_appid/ml-requests_OGSsSuHXIN8YLzenRbgN/exports/output.usdz'), output_url=None, processing_time_s=126.74, progress=None, request_id='OGSsSuHXIN8YLzenRbgN', status='complete', requestId='OGSsSuHXIN8YLzenRbgN', processingTime_s=126.74)

print("Generated 3D object urls:")
print(f'glb: {imageto3d_response.outputs.glb}')
print(f'fbx: {imageto3d_response.outputs.fbx}')
print(f'usdz: {imageto3d_response.outputs.usdz}')
print(f'thumbnail: {imageto3d_response.outputs.thumbnail}')



