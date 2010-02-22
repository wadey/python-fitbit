import xml.etree.ElementTree as ET
import datetime
import urllib, urllib2
import logging

_log = logging.getLogger("fitbit")

class Client(object):
    """A simple data dump client for the www.fitbit.com website.
    Uses the internal API used for the flash charts,
    which will probably stop working at some point
    """
    
    def __init__(self, user_id, sid, uid, uis, url_base="http://www.fitbit.com"):
        self.user_id = user_id
        self.sid = sid
        self.uid = uid
        self.uis = uis
        self.url_base = url_base
        self._request_cookie = "sid=%s; uid=%s; uis=%s" % (sid, uid, uis)
    
    def intraday_calories_burned(self, date):
        """Retrieve the calories burned every 5 minutes
        the format is: [(datetime.datetime, calories_burned), ...]
        """
        return self._graphdata_intraday_request("intradayCaloriesBurned", date)
    
    def intraday_active_score(self, date):
        """Retrieve the active score for every 5 minutes
        the format is: [(datetime.datetime, active_score), ...]
        """
        return self._graphdata_intraday_request("intradayActiveScore", date)

    def intraday_steps(self, date):
        """Retrieve the steps for every 5 minutes
        the format is: [(datetime.datetime, steps), ...]
        """
        return self._graphdata_intraday_request("intradaySteps", date)
    
    def _request(self, path, parameters):
        query_str = urllib.urlencode(parameters)

        request = urllib2.Request("%s%s?%s" % (self.url_base, path, query_str), headers={"Cookie": self._request_cookie})
        _log.debug("requesting: %s" % request.get_full_url())

        data = None
        try:
            response = urllib2.urlopen(request)
            data = response.read()
            response.close()
        except urllib2.HTTPError as httperror:
            data = httperror.read()
            httperror.close()

        #_log.debug("response: %s" % data)

        return ET.fromstring(data.strip())

    def _graphdata_intraday_request(self, graph_type, date):
        p = dict(
            userId=self.user_id,
            type=graph_type,
            version="amchart",
            dataVersion=2108,
            chart_Type="column2d",
            period="1d",
            dateTo=str(date)
        )

        xml = self._request("/graph/getGraphData", p)

        base_time = datetime.datetime.combine(date, datetime.time())
        timestamps = [base_time + datetime.timedelta(minutes=m) for m in xrange(0, 288*5, 5)]
        values = [float(v.text) for v in xml.findall("data/chart/graphs/graph/value")]
        return zip(timestamps, values)