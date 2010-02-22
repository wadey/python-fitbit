import xml.etree.ElementTree as ET
import datetime
import urllib, urllib2
import logging

_log = logging.getLogger("fitbit")

class Client(object):
    """A simple API client for the www.fitbit.com website.
    see README for more details
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
    
    def intraday_sleep(self, date, sleep_id=None):
        """Retrieve the sleep status for every 1 minute interval
        the format is: [(datetime.datetime, sleep_value), ...]
        The statuses are:
            0: no sleep data
            1: asleep
            2: awake
            3: very awake
        For days with multiple sleeps, you need to provide the sleep_id
        or you will just get the first sleep of the day
        """
        return self._graphdata_intraday_sleep_request("intradaySleep", date, sleep_id=sleep_id)
    
    def _request(self, path, parameters):
        # Throw out parameters where the value is not None
        parameters = dict([(k,v) for k,v in parameters.items() if v])
        
        query_str = urllib.urlencode(parameters)

        request = urllib2.Request("%s%s?%s" % (self.url_base, path, query_str), headers={"Cookie": self._request_cookie})
        _log.debug("requesting: %s", request.get_full_url())

        data = None
        try:
            response = urllib2.urlopen(request)
            data = response.read()
            response.close()
        except urllib2.HTTPError as httperror:
            data = httperror.read()
            httperror.close()

        #_log.debug("response: %s", data)

        return ET.fromstring(data.strip())

    def _graphdata_intraday_xml_request(self, graph_type, date, data_version=2108, **kwargs):
        params = dict(
            userId=self.user_id,
            type=graph_type,
            version="amchart",
            dataVersion=data_version,
            chart_Type="column2d",
            period="1d",
            dateTo=str(date)
        )
        
        if kwargs:
            params.update(kwargs)

        return self._request("/graph/getGraphData", params)

    def _graphdata_intraday_request(self, graph_type, date):
        # This method used for the standard case for most intraday calls (data for each 5 minute range)
        xml = self._graphdata_intraday_xml_request(graph_type, date)
        
        base_time = datetime.datetime.combine(date, datetime.time())
        timestamps = [base_time + datetime.timedelta(minutes=m) for m in xrange(0, 288*5, 5)]
        values = [int(float(v.text)) for v in xml.findall("data/chart/graphs/graph/value")]
        return zip(timestamps, values)
    
    def _graphdata_intraday_sleep_request(self, graph_type, date, sleep_id=None):
        # Sleep data comes back a little differently
        xml = self._graphdata_intraday_xml_request(graph_type, date, data_version=2112, arg=sleep_id)
        
        
        elements = xml.findall("data/chart/graphs/graph/value")
        timestamps = [datetime.datetime.strptime(e.attrib['description'].split(' ')[-1], "%I:%M%p") for e in elements]
        
        # TODO: better way to figure this out?
        # Check if the timestamp cross two different days
        last_stamp = None
        datetimes = []
        base_date = date
        for timestamp in timestamps:
            if last_stamp and last_stamp > timestamp:
                base_date -= datetime.timedelta(days=1)
            last_stamp = timestamp
        
        last_stamp = None
        for timestamp in timestamps:
            if last_stamp and last_stamp > timestamp:
                base_date += datetime.timedelta(days=1)
            datetimes.append(datetime.datetime.combine(base_date, timestamp.time()))
            last_stamp = timestamp
        
        values = [int(float(v.text)) for v in xml.findall("data/chart/graphs/graph/value")]
        return zip(datetimes, values)