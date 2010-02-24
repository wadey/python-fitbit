# Overview

This client provides a simple way to access your data on www.fitbit.com.
I love my fitbit and I want to be able to use the raw data to make my own graphs.
Currently, this client uses the endpoints used by the flash graphs.
Once the official API is announced, this client will be updated to use it.

Right now, you need to log in to the site with your username / password, and then grab some information from the cookie.
The cookie will look like:

    Cookie: sid=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX; uid=12345; uis=XX%3D%3D;
  
Create a `fitbit.Client` with this data, plus the userId (which you can find at the end of your profile url)

# Example

    import fitbit

    client = fitbit.Client(user_id="XXX", sid="XXX", uid="XXX", uis="XXX")

    # example data
    data = client.intraday_steps(datetime.date(2010, 2, 21))

    # data will be a list of tuples. example:
    # [
    #   (datetime.datetime(2010, 2, 21, 0, 0), 0),
    #   (datetime.datetime(2010, 2, 21, 0, 5), 40),
    #   ....
    #   (datetime.datetime(2010, 2, 21, 23, 55), 64),
    # ]
    
    # The timestamp is the beginning of the 5 minute range the value is for
    
    # Other API calls:
    data = client.intraday_calories_burned(datetime.date(2010, 2, 21))
    data = client.intraday_active_score(datetime.date(2010, 2, 21))
    
    # Sleep data is a little different:
    data = client.intraday_sleep(datetime.date(2010, 2, 21))
    
    # data will be a similar list of tuples, but spaced one minute apart
    # [
    #   (datetime.datetime(2010, 2, 20, 23, 59), 2),
    #   (datetime.datetime(2010, 2, 21, 0, 0), 1),
    #   (datetime.datetime(2010, 2, 21, 0, 1), 1),
    #   ....
    #   (datetime.datetime(2010, 2, 21, 8, 34), 1),
    # ]
    
    # The different values for sleep are:
    #   0: no sleep data
    #   1: asleep
    #   2: awake
    #   3: very awake

There is also an example dump script provided: `examples/dump.py`.  This script can be set up as a cron job to dump data nightly.
