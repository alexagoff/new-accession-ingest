from login_materials import config
from asnake.client import ASnakeClient

sess = ""

client = ASnakeClient(baseurl=config.aspacebaseurl,
                        username=config.username,
                        password=config.password)

sess = client.authorize() # this will not work if the aspacebaseurl is wrong

#records the session token (not necessary with Asnake)
with open ('login_materials/current_sess.txt', 'w') as c:
  c.write(sess)
  c.close()