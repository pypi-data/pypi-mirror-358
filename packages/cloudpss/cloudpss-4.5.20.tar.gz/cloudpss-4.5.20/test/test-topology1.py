
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..\\'))
import cloudpss
import time
import numpy as np
import pandas as pd
import json

if __name__ == '__main__':
    os.environ['CLOUDPSS_API_URL'] = 'http://10.101.10.45/'
    print('CLOUDPSS connected')
    cloudpss.setToken(
        'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInNjb3BlcyI6WyJtb2RlbDo5ODMzNSIsImZ1bmN0aW9uOjk4MzM1IiwiYXBwbGljYXRpb246OTgzMzUiXSwicm9sZXMiOlsiYWRtaW4iXSwidHlwZSI6ImFwcGx5IiwiZXhwIjoxNzI0NTU3MDIzLCJub3RlIjoiYSIsImlhdCI6MTY5MzQ1MzAyM30._Xuyo62ESKLcIAFeNdnfBM44yPiiXli9OPKvXDzL2rPV4J1_qsGZP--bsS1tXAVy-x8ooUIIAAG1yhwmZuk7-Q')
    print('Token done')
    project = cloudpss.Model.fetch('model/admin/asdfsadd')
    # topology = cloudpss.ModelTopology.fetch("-xrS3SewFhpVYKBtIXLk-XDLCQRQnUmlIbXS3s4sdPUkPKeAMhXHjRgZD1JPjPfQ","emtp",{'args':{}})
    topology= project.fetchTopology(config={'args':{}},maximumDepth=50)
    print(topology.components)
    # topology.dump(topology,'test.json')
    
    
    # # topology= project.fetchTopology(config={'args':{}})

    # topology.dump(topology,'test.json')
    
    
    