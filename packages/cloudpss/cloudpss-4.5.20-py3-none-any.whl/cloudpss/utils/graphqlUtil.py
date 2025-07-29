# coding=UTF-8
import json
from cloudpss.utils import request


def graphql_request(query, variables=None, baseUrl=None,token=None,**kwargs):
    payload = {'query': query, 'variables': variables}
    
    r = request('POST', 'graphql', data=json.dumps(payload),baseUrl=baseUrl,token=token, **kwargs)

    return json.loads(r.text)
