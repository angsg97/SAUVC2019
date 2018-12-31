""" This package implements a simple pair of Client and Server.

It allows data exchange between two computers

The process looks like:

Client                       Server
   |                           |
   |----- TCP Handshake -------|
   |                           |
  w|----- Send Request ------>>|
  a|                           || get request (see get_requests
  i|                           || prepare data
  t|                           || offer data (see offer_data)
   |<<-- Send Required Data ---|
   |                           |
   |---- Close Connection -----|

"""
from network.server import Server
from network.client import Client
