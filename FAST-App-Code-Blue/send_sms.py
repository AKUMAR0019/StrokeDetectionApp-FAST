import os 
from twilio.rest import Client

account_sid = "AC579d98323fea4799e9c97d86594e58e0"
auth_token = "e94c0f1b2a4790085b3d982a6a631c13"

client = Client(account_sid, auth_token)
client.messages.create(
    to = "+18722233043",
    from_= "+15403025704",
    body ="Facial asymmetry was detected for user: corralem@beloit.edu. Please seek medical attention immediately."

)
