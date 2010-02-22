# Overview

This client provides a simple way to dump fitbit data from www.fitbit.com until the official API is available

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
    #   (datetime.datetime(2010, 2, 21, 0, 0), 0.0),
    #   (datetime.datetime(2010, 2, 21, 0, 5), 40.0),
    #   ....
    #   (datetime.datetime(2010, 2, 21, 23, 55), 64.0),
    # ]
    
    # The timestamp is the beginning of the 5 minute range the value is for
