from os import environ
# from tools import get_bot_username


# BOT CONFIG
API_ID = environ.get("API", 28015381) # api id
API_HASH = environ.get("API_HASH","d1be9454b29326ed41b0acdef11d202c")   # api hash
BOT_TOKEN = environ.get("BOT_TOKEN","7088928556:AAFulnC-duhQj2mMgyQSt0vob-KKBz3Gk-0")  # bot token

# ## REDIS
# HOST = environ.get("REDIS","redis-12832.c267.us-east-1-4.ec2.cloud.redislabs.com")   # redis host uri
# PORT = environ.get("REDISPORT", 12832)  # redis port
# PASSWORD = environ.get("REDISPASSWORD", "q8vcRgGfoZgwKT6irvJ6AixPs1lFZdW8")   # redis password


ADMINS = [6791744215]
OWNER_ID = environ.get("OWNER_ID", 6791744215) # Replace with your Telegram user ID
PRIVATE_CHAT_ID = environ.get("PRIVATE_CHAT_ID", -1001751118413) # CHAT WHERE YOU WANT TO STORE VIDEOS
USER_CHANNEL = environ.get("USER_CHANNEL", -1002038588409)


# BOT_USERNAME = get_bot_username(BOT_TOKEN)
UPCHANNEL = environ.get("UP_CHANNEL", "mustjoin11")
UPGROUP = environ.get("UP_GROUP", "mustjoin10")
REQUEST_CHANNEL = -1002085635190

# COOKIE = "csrfToken=W7CoOd53s0CPNDU_0YDwwxcr; browserid=u3bzYPAgXhzsAezc1RjXjNrFuTkh-guoj3cutwkuh_nyvwEyPaqVKJC74AM=; lang=en; TSID=4Fe8lz2UV3i06ZSTKZCH7iQTosaD55NN; __bid_n=18db609b9c129bcb704207; _ga=GA1.1.999843767.1708156111; __stripe_mid=f28f9689-c4e8-4c51-a3b0-fac76f69b8fcd804ab; __stripe_sid=2d6f2523-0772-4b3c-8e37-5a38e747df068d39c2; ndus=YexnDKeteHui3iFnSMlkMYtLlH_QbVKPOXpYgDb8; ndut_fmt=F61E378E0702EBB99D631E9B92011476A3CE8EE6B4A4B872AA07970159D86EF3; _ga_06ZNKL8C2E=GS1.1.1712059905.3.1.1712060952.20.0.0"
# COOKIE = "csrfToken=WVgTnyjwKPqgn2dakDaA3LdT; browserid=u3bzYPAgXhzsAezc1RjXjNrFuTkh-guoj3cutwkuh_nyvwEyPaqVKJC74AM=; lang=en; TSID=4Fe8lz2UV3i06ZSTKZCH7iQTosaD55NN; __bid_n=18db609b9c129bcb704207; _ga=GA1.1.999843767.1708156111; __stripe_mid=f28f9689-c4e8-4c51-a3b0-fac76f69b8fcd804ab; __stripe_sid=fc21430e-c521-4415-9751-fc3550cb09ed477b62; ndus=YV5qy84teHuioLedCMKLx6OKH7HW7P50Fodb2yrN;  ndut_fmt=58935574F1C08B095CAD18CDB119A2C3877D78C972E2946F48295B6DD7100CCA; _ga_06ZNKL8C2E=GS1.1.1708156111.1.1.1708160441.45.0.0"  # COOKIE FOR AUTHENTICATION (get from chrome dev tools) ex: "PANWEB=1; csrfToken=; lang=en; TSID=; __bid_n=; _ga=; __stripe_mid=; ndus=; browserid==; ndut_fmt=; _ga_06ZNKL8C2E=" (dont use this)
COOKIE = "browserid=u3bzYPAgXhzsAezc1RjXjNrFuTkh-guoj3cutwkuh_nyvwEyPaqVKJC74AM=; TSID=4Fe8lz2UV3i06ZSTKZCH7iQTosaD55NN; __bid_n=18db609b9c129bcb704207; _ga=GA1.1.999843767.1708156111; __stripe_mid=f28f9689-c4e8-4c51-a3b0-fac76f69b8fcd804ab; lang=en; csrfToken=JSUgRrotXGVUKPPCkAH3a538; ndus=Ydsjs3eteHuimm9BDnSiPko1ftXF21KZE366rpUC; __stripe_sid=418f5125-3ab0-4712-bdf5-92be6ca58d2f0b911c; _ga_06ZNKL8C2E=GS1.1.1712139064.4.1.1712139204.5.0.0; ndut_fmt=1B3D34DEBB1FE52CB2874955687E697C2E278B530E2C4867B9491A97389ED803"
