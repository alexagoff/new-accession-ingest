from login_materials import config
from asnake.client import ASnakeClient

sess = ""

client = ASnakeClient(baseurl=config.aspacebaseurl,
                        username=config.username,
                        password=config.password)

sess = client.authorize()
#print(sess)

#records the session token for use in other tools
with open ('login_materials/current_sess.txt', 'w') as c:
  c.write(sess)
  c.close()