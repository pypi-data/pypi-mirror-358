# We will use the Masterpiece X SDK to generate a 3D object by using the components of the SDK
# Steps:
# 1. Generate a mesh obj
# 2. Generate a texture
# 3. Generate an animation
# 4. Generate a 3D object by combining the mesh obj, texture, and animation

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

# Generate a mesh obj using the mesh select model
# This model generates quality meshes, but they do not have the creativity level of the base_mesh_gen model
mesh_select = mpx_client.components.base_mesh_select(
    category= "ball, sports equipment",
    text_prompt= "basketball, sports equipment, A basketball with a black and orange pattern, shiny, classic",
    mesh_type= "object",
    mesh_variability= 2
)
print(f'mesh select response = {mesh_select}')
mesh_select_resp = retrieve_request_status(mesh_select.request_id)

# This model generates more creative meshes, but they may not be as high quality as the mesh select model
mesh_gen = mpx_client.components.base_mesh_gen(
    image_request_id= "",
    category= "ball, sports equipment",
    text_prompt= "basketball, sports equipment, A basketball with a black and orange pattern, shiny, classic",
    mesh_type= "object",
    mesh_variability= 2
)
print(f'mesh gen response = {mesh_gen}')
mesh_gen_resp = retrieve_request_status(mesh_gen.request_id)

# Generate a texture for the 3D object using the mesh_select request id
texture_object = mpx_client.components.texture_object(
    mesh_request_id= mesh_select.request_id,
    prompt_pos= "red ball with yellow stripes. Mat finish with small bumps",
    prompt_neg= "blurry, low quality, low res, pixel",
    seed= 2
)
print(f'texture response = {texture_object}')
texture_resp = retrieve_request_status(texture_object.request_id)
#print(f'texture url = {texture_resp.output.texture}')

# Generate a 3D object by combining the mesh obj, texture
generate_glb = mpx_client.components.generate_glb(
    mesh_request_id= mesh_select.request_id,
    texture_request_id= texture_object.request_id,
    animation_request_id= "",
    mesh_type= "object",
    rig_only= False,
)
print(generate_glb)
glb_resp = retrieve_request_status(generate_glb.request_id)
print (f'glb url = {glb_resp.outputs.glb}')
print (f'thumbnail url = {glb_resp.outputs.thumbnail}')