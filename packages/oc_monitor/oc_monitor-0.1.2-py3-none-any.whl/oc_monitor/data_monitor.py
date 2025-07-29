from SPARQLWrapper import SPARQLWrapper, JSON
import json
import time
from datetime import datetime


class MetaMonitor:
    """
    A class used to monitor the quality of the OpenCitations Meta dataset accessible via a SPARQL endpoint.

    :param config_path: The file path to the configuration file in JSON format.
    :type config_path: str
    :param out_path: The file path where the output JSON report will be saved.
    :type out_path: str

    :ivar config_path: The file path to the configuration file in JSON format.
    :ivar out_path: The file path where the output JSON report will be saved.
    :ivar endpoint: The SPARQL endpoint URL extracted from the configuration file.
    """

    def __init__(self, config_path:str, out_path:str):
        """
        Initializes the MetaMonitor with the provided configuration file path and output file path.

        :param config_path: The file path to the configuration file containing the SPARQL queries and settings.
        :type config_path: str
        :param out_path: The file path where the resulting JSON report will be saved.
        :type out_path: str
        """
        
        self.config_path = config_path
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.endpoint = self.config['endpoint']
        # TODO: possibility to overwrite the endpoint in config via kwargs?
        self.out_path = out_path

    def run_tests(self):
        """
        Executes all the tests listed in the configuration file for the Meta dataset.
        Each test must consist of either an ASK or a SELECT SPARQL query to be evaluated against the specified endpoint.

        The results of the tests are stored in a JSON format, detailing:

        - whether each test passed or failed,
        - any errors encountered during the query execution,
        - the running time of each test.

        The overall running time of the entire test suite is also recorded.

        :return: A dictionary containing the results of the monitoring tests, including pass/fail status and error details.
        :rtype: dict
        """

        output_dict = {
            'endpoint': self.endpoint,
            'collection': 'OpenCitations Meta',
            'datetime': datetime.now().strftime('%d/%m/%Y, %H:%M:%S'), # TODO: extract datetime of the run
            'running_time' : 0.0,
            'config_fp' : self.config_path,
            'monitoring_results': []
            }
        
        general_start = time.time()
        sparql = SPARQLWrapper(self.endpoint)
        for issue in self.config['tests']:
            if issue['to_run']: # specific tests can be switched off in config file
                label = issue['label']
                query = issue['query']
                descr = issue['description']
                query_type = issue.get('query_type', '')

                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                try:
                    res_start = time.time()
                    response = sparql.query().convert()
                    if "ASK" in query or query_type == 'ask':
                        result_value = response['boolean']
                    else:
                        result_value = True if response['results']['bindings'] else False # 'bindings' list is empty if no results
                    if query_type == 'count':
                        count = [list(bind.values())[0]['value'] for bind in response['results']['bindings']][0]  # count query must be built so that it returns a signle integer
                        result_value = bool(int(count))
                    else:
                        count = None
                    test_res = {
                        'label': label,
                        'description': descr,
                        'query': query,
                        'run': {
                            'got_result': True,
                            'running_time': time.time()-res_start,
                            'error': None}}
                    
                    if result_value is True: # did NOT pass the test
                        test_res['passed']= False
                    else:
                        test_res['passed']= True
                    test_res['count'] = count
                    print(test_res, '\n\n')  # TODO: remove line
                    output_dict['monitoring_results'].append(test_res)

                except Exception as e:
                    test_res = {
                        'label': label,
                        'description': descr,
                        'query': query,
                        'run': {
                            'got_result': False,
                            'running_time': time.time()-res_start,
                            'error': str(e)}} # TODO: add other metadata about the error?
                    
                    output_dict['monitoring_results'].append(test_res)
                    print('Esecuzione fallita:', response, '\n\n')  # TODO: remove line
                finally:
                    continue # TODO: implement better error handling strategy?
        
        output_dict['running_time'] = time.time()-general_start
        with open(self.out_path, 'w', encoding='utf-8') as outf:
            json.dump(output_dict, outf, indent=4)
        return output_dict


class IndexMonitor:

    """
    A class used to monitor the quality of the OpenCitations Index dataset accessible via a SPARQL endpoint.

    :param config_path: The file path to the configuration file in JSON format.
    :type config_path: str
    :param out_path: The file path where the output JSON report will be saved.
    :type out_path: str

    :ivar config_path: The file path to the configuration file in JSON format.
    :ivar out_path: The file path where the output JSON report will be saved.
    :ivar endpoint: The SPARQL endpoint URL extracted from the configuration file.
    """

    def __init__(self, config_path:str, out_path:str):
        
        """
        Initializes the IndexMonitor with the provided configuration file path and output file path.

        :param config_path: The file path to the configuration file containing the SPARQL queries and settings.
        :type config_path: str
        :param out_path: The file path where the resulting JSON report will be saved.
        :type out_path: str
        """
        
        self.config_path = config_path
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.endpoint = self.config['endpoint']
        # TODO: possibility to overwrite the endpoint in config via kwargs?
        self.out_path = out_path

    def run_tests(self):

        """
        Executes all the tests listed in the configuration file for the Index dataset.
        Each test must consist of either an ASK or a SELECT SPARQL query (but Qlever does not support ASK queries so far) to evaluate against the specified endpoint.

        The results of the tests are stored in a JSON format, detailing:

        - whether each test passed or failed,
        - any errors encountered during the query execution,
        - the running time of each test.

        The overall running time of the entire test suite is also recorded.

        :return: A dictionary containing the results of the monitoring tests, including pass/fail status and error details.
        :rtype: dict
        """

        output_dict = {
            'endpoint': self.endpoint,
            'collection': 'OpenCitations Index',
            'datetime': datetime.now().strftime('%d/%m/%Y, %H:%M:%S'), # TODO: extract datetime of the run
            'running_time' : 0.0, # overwritten later on
            'config_fp' : self.config_path,
            'monitoring_results': []
            }
        
        general_start = time.time()
        sparql = SPARQLWrapper(self.endpoint)
        for issue in self.config['tests']:
            if issue['to_run']: # specific tests can be switched off in config file
                label = issue['label']
                query = issue['query']
                descr = issue['description']
                query_type = issue.get('query_type', '')

                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                try:
                    res_start = time.time()
                    response = sparql.query().convert()
                    if "ASK" in query or query_type == 'ask':
                        result_value = response['boolean']
                    else:
                        result_value = True if response['results']['bindings'] else False # 'bindings' list is empty if no results
                    if query_type == 'count':
                        count = response['results']['bindings'][0]['count']['value']
                        result_value = bool(int(count))
                    else:
                        count = None
                    test_res = {
                        'label': label,
                        'description': descr,
                        'query': query,
                        'run': {
                            'got_result': True,
                            'running_time': time.time()-res_start,
                            'error': None}}
                    
                    if result_value is True: # did NOT pass the test
                        test_res['passed']= False
                    else:
                        test_res['passed']= True
                    test_res['count'] = count
                    output_dict['monitoring_results'].append(test_res)

                except Exception as e:
                    test_res = {
                        'label': label,
                        'description': descr,
                        'query': query,
                        'run': {
                            'got_result': False,
                            'running_time': time.time()-res_start,
                            'error': str(e)}} # TODO: add other metadata about the error?
                    
                    output_dict['monitoring_results'].append(test_res)
                finally:
                    continue # TODO: implement better error handling strategy?
        
        output_dict['running_time'] = time.time()-general_start
        with open(self.out_path, 'w', encoding='utf-8') as outf:
            json.dump(output_dict, outf, indent=4)
        return output_dict
