# coding=utf-8
import os
import requests
import json
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# from errorList import null_string_error
logging.basicConfig(level=logging.CRITICAL, format='[%(levelname)s] %(lineno)s %(message)s')

username = ''

# Set default MAX_RETRIES, BACKOFF_FACTOR
try:
    MAX_RETRIES = os.environ["MAX_RETRIES"]
except:
    MAX_RETRIES = 2

try:
    BACKOFF_FACTOR = os.environ["BACKOFF_FACTOR"]
except:
    BACKOFF_FACTOR = 1

# urllib3 will sleep for: {backoff factor} * (2 ^ ({number of total retries} - 1)) seconds.
# If the backoff_factor is 0.1, then sleep() will sleep for [0.0s, 0.2s, 0.4s, ...] between retries.
STATUS_FORELIST = (500, 502, 504),
# Create a session
s = requests.Session()
# Set Retry logic
retry = Retry(
    total=MAX_RETRIES,
    read=MAX_RETRIES,
    connect=MAX_RETRIES,
    backoff_factor=BACKOFF_FACTOR,
    status_forcelist=STATUS_FORELIST,
)
# Create adapters with the retry logic for each
a = requests.adapters.HTTPAdapter(max_retries=retry)
b = requests.adapters.HTTPAdapter(max_retries=retry)
# Replace the session's original adapters
s.mount('http://', a)
s.mount('https://', b)

# Define Exceptions:
fail_connect = {"status": "failure", "message": "client_connection_failure"}
CONNECTION_FAILURE = json.dumps(fail_connect)
fail_json = {"status": "failure", "message": "client_json_parse_failure"}
JSON_FAILURE = json.dumps(fail_json)


def _query(url):
    logging.debug(url)
    try:
        response = s.get(url, data=None)
        result = response.content
    except Exception as e:
        logging.debug(e)
        result = CONNECTION_FAILURE
    return result


def _post_query(url, data):
    logging.debug(url)
    try:
        response = s.post(url, data=data)
        result = response.content
    except Exception as e:
        logging.debug(e)
        result = CONNECTION_FAILURE
    return result


def _put_query(url, data=None):
    logging.debug(url)
    try:
        response = s.put(url, data)
        result = response.content
    except Exception as e:
        logging.debug(e)
        result = CONNECTION_FAILURE
    return result


def _post_query_files(url, data, file_path):
    files = {'file': open(file_path, 'r')}
    try:
        response = s.post(url, data=data, files=files)
        result = response.content
    except Exception as e:
        logging.debug(e)
        result = CONNECTION_FAILURE
    return result


def _delete_query(url, data):
    try:
        response = s.delete(url, data=data)
        result = response.content
    except Exception as e:
        logging.debug(e)
        result = CONNECTION_FAILURE
    return result


def _url_assemble(url, parameter):
    if len(parameter) is 1:
        url += parameter[0]
    else:
        for i in range(0, len(parameter)):
            if i != len(parameter) - 1:
                url += parameter[i] + ';'
            else:
                url += parameter[i]
    return url


def _url_dict_assemble(url, parameter):
    l = len(parameter)
    if l > 1:
        i = 0
        for key, value in parameter.items():
            if i != l - 1:
                url += key + '=' + value + '&'
                i += 1
            else:
                url += key + '=' + value
    else:
        for key, value in parameter.items():
            url += key + '=' + value
    return url


def _get_neighbor_inOut_url(url, neighbor_label, edge_label, prop, max_num_vertices=float("inf")):
    if neighbor_label or edge_label or prop or max_num_vertices != float("inf"):
        url += '?'
        if neighbor_label:
            url += "vertex_label="
            url = _url_assemble(url, neighbor_label)
            if edge_label or prop or max_num_vertices != float("inf"):
                url += '&'
        if edge_label:
            url += 'edge_label='
            url = _url_assemble(url, edge_label)
            if prop or max_num_vertices != float("inf"):
                url += '&'
        if prop:
            if isinstance(prop, list):
                if prop:
                    url += 'prop='
                    url = _url_assemble(url, prop)
            elif isinstance(prop, basestring):
                if prop == 'id_only':
                    url += "prop=id_only"
            if max_num_vertices != float("inf"):
                url += '&'
        if max_num_vertices != float("inf"):
            url += "max_num_edges={}".format(max_num_vertices)
    return url


class gc:
    """
    The graphdb client class.
    The class wraps the graph database REST services and translates the REST calls into functions.
    All functions are based on Graph API.

    Examples
    --------
    .. code-block:: python

        GRAPHDB_HOST = "http://localhost"
        GRAPHDB_PORT = "8012"
        grest_host = GRAPHDB_HOST + ":" + GRAPHDB_PORT
        g = client.gc(host=grest_host)

    """

    def __init__(self, host):
        self.vertex_prop_name_list = []
        self.graph_name = ''
        self.root_url = host

    # Graph Management
    def list_graphs(self, opened=False):
        """
        Get a list of graphs.

        Parameters
        ----------
        opened
            int
                on disk (opened=0 or unspecified) or opened in memory (opened=1)

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "fail to get graph list"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "data": {
                        "graphs": [
                          "<graph_name_1>",
                          "<graph_name_2>",
                          "..."
                        ]
                      }
                    }

        Examples
        --------
        .. code-block:: python

            g.list_graphs()
            g.list_graphs(opened=1)

        """
        if opened is False:
            url = self.root_url + '/graphs?opened=0'
            return _query(url)
            # print _query(url)
        elif opened is True:
            url = self.root_url + '/graphs?opened=1'
            # print _query(url)
            return _query(url)

    def print_graph(self, graph_name):
        """
        Print all content of a graph.

        Parameters
        ----------
        graph_name
            str
                an existing graph name

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                        "status": "failure",
                        "message": "cannot find graph 'not_exist'"
                    }

            DB_OK

                .. code-block:: json

                    {
                        "status": "success",
                        "statistics": {
                            "num_vertices": 2,
                            "num_edges": 1
                        },
                        "data": {
                            "edges": [
                                {
                                    "source_label": "v1",
                                    "target_label": "v1",
                                    "target_id": "2",
                                    "label": "e1",
                                    "eid": "13835058055282163712",
                                    "source_id": "1",
                                    "properties": [
                                        {
                                            "p1": "first"
                                        },
                                        {
                                            "p2": 1
                                        }
                                    ]
                                }
                            ],
                            "vertices": [
                                {
                                    "label": "v1",
                                    "properties": [
                                        {
                                            "p1": "first"
                                        },
                                        {
                                            "p2": 1.1
                                        }
                                    ],
                                    "id": "1"
                                },
                                {
                                    "label": "v1",
                                    "properties": [
                                        {
                                            "p1": "second"
                                        },
                                        {
                                            "p2": 1.2
                                        }
                                    ],
                                    "id": "2"
                                }
                            ]
                        }
                    }


        Examples
        --------
        .. code-block:: python

            g.print_graph(graph_name="test")

        Warnings
        --------
        Only use this method for small graphs, or the huge return str may kill your terminal!

        """
        url = self.root_url + '/graphs/' + graph_name
        return _query(url)

    def create_graph(self, graph_name, graph_type=0, schema_str='', schema_path='', schema_url='', create_mode='w',
                     request_type='sync', expiration=1200, job_id=""):
        """
        Create a graph with or without a schema string or schema file, with or without async or async_kafka, and set the current graph to the new created graph.

        Parameters
        ----------
        graph_name
            str
                a new graph name
        graph_type
            int
                0 for "directed", 1 for "undirected", 2 for "directed" with support for optimized initial batch loading, default is 0
        schema_str
            str
                optional, the schema in str
        schema_path
            str
                optional, where the schema file is located on the server
        schema_url
            str
                optional, where the schema file is on the internet
        create_mode
            str
                "w"|"x" // "w" for overwriting existing graph of the same name, "x" for no overwrite, default is "w", only used for non-schema create
        request_type
            str
                optional, if using async, kafka, default is for sync load, option for async, async_kafka, only used for non-schema create

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid request body"
                    }
                    {
                      "status": "failure",
                      "message": "invalid graph type '<graph_type>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid schema"
                    }
                    {
                      "status": "failure",
                      "message": "already exist graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to create graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid schema path '<server_schema_path>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to read schema file '<server_schema_path>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid schema path '<schema_url>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to read schema file '<schema_url>'"
                    }


            DB_OK

                .. code-block:: json

                    {
                      "status": "success"
                    }

        Examples
        --------
        .. code-block:: python

            schema_str = '''{
              "vertex_labels": [
                "v1",
                "v2"
              ],
              "edge_labels": [
                "e1",
                "e2"
              ],
              "vertex_props": [
                {
                  "prop_name": "p1",
                  "prop_type": "STRING"
                },
                {
                  "prop_name": "p2",
                  "prop_type": "DOUBLE"
                }
              ],
              "edge_props": [
                {
                  "prop_name": "p1",
                  "prop_type": "STRING"
                },
                {
                  "prop_name": "p2",
                  "prop_type": "INT"
                }
              ]
            }'''

            g.create_graph(graph_name="test", schema_str=schema_str)
            g.create_graph(graph_name="test", schema_path="schema_folder/schema.json")
            g.create_graph(graph_name="test")
            g.create_graph(graph_name="test_for_id", job_id="I-AM-JOB_ID", request_type="async_kafka")
            g.create_graph(graph_name="test_for_id", request_type="async_kafka")
            g.create_graph(graph_name="test", schema_str=schema_str, create_mode="x")

        Notes
        -----
        Schema Format
            .. code-block:: json

                {
                  "vertex_labels": [
                    "<vertex_label_1>",
                    "<vertex_label_2>"
                  ],
                  "edge_labels": [
                    "<edge_label_1>",
                    "<edge_label_2>"
                  ],
                  "vertex_props": [
                    {
                      "prop_name": "<prop_name_1>",
                      "prop_type": "<prop_type_1>"
                    },
                    {
                      "prop_name": "<prop_name_2>",
                      "prop_type": "<prop_type_2>"
                    }
                  ],
                  "edge_props": [
                    {
                      "prop_name": "<prop_name_1>",
                      "prop_type": "<prop_type_1>"
                    },
                    {
                      "prop_name": "<prop_name_2>",
                      "prop_type": "<prop_type_2>"
                    }
                  ]
                }

        Property Types
            - STRING
            - INT
            - LONG
            - FLOAT
            - DOUBLE
            - DATETIME (stored as LONG)
            - VECTORSTRING
            - VECTORINT
            - VECTORLONG
            - VECTORDOUBLE00
            - VECTORFLOAT
            - VECTORDATETIME
            - TS_STRING (for timestamped property values)
            - TS_INT (for timestamped property values)
            - TS_LONG (for timestamped property values)
            - TS_FLOAT (for timestamped property values)
            - TS_DOUBLE (for timestamped property values)


        """
        self.graph_name = graph_name  # set new created graph as current graph
        config_param = {}
        # logging.debug("{}-{}-{}".format(schema_str, schema_path, schema_url))
        if schema_str or schema_path or schema_url:
            url = self.root_url + '/graphs/' + graph_name
            if schema_str:
                try:
                    schema = json.loads(schema_str)
                except Exception as e:
                    logging.debug(e)
                    result = JSON_FAILURE
                    return result
                data = {
                    'graph_type': graph_type,
                    'schema': schema
                }
                config_param['param'] = json.dumps(data)
                return _post_query(url, config_param)
            if schema_path:
                if 'file=@' in schema_path:
                    return _post_query(url, schema_path)
                else:
                    data = {
                        'graph_type': graph_type
                    }
                    config_param['param'] = json.dumps(data)
                    return _post_query_files(url, config_param, schema_path)
            elif schema_url:
                data = {
                    'graph_type': graph_type,
                    'schema_url': schema_url
                }
                config_param['param'] = json.dumps(data)
                return _post_query(url, config_param)
        else:
            url = self.root_url + "/{}/graphs/".format(request_type) + graph_name
            data = {}
            data['graph_type'] = graph_type
            data["create_mode"] = create_mode
            config_param['param'] = json.dumps(data)

            async_setting = {}
            async_setting["expiration"] = expiration
            if job_id:
                async_setting["job_id"] = job_id
            else:
                async_setting["job_id"] = "create::" + graph_name
            config_param["async"] = json.dumps(async_setting)

            return _post_query(url, config_param)

    def close_graph(self, graph_name):
        """
        Close an opened graph.

        Parameters
        ----------
        graph_name
            str
                a graph name

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to close graph '<graph_name>'"
                    }

            DB_WARNING

                .. code-block:: json

                    {
                      "status": "warning",
                      "message": "cannot find opened graph '<graph_name>'"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success"
                    }

        Examples
        --------
        .. code-block:: python

            g.close_graph(graph_name="test")

        """
        url = self.root_url + "/graphs/" + graph_name
        return _put_query(url)

    def close_graphs(self):
        """
        Close all opened graphs.

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "fail to close graphs"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success"
                    }

        Examples
        --------
        .. code-block:: python

            g.close_graphs()
        """
        url = self.root_url + '/graphs'
        return _put_query(url)

    def delete_graph(self, graph_name):
        """
        Delete a graph on disk.

        Parameters
        ----------
        graph_name
            str
                a graph name

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to delete graph '<graph_name>'"
                    }

            DB_WARNING

                .. code-block:: json

                    {
                      "status": "warning",
                      "message": "cannot find graph '<graph_name>'"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success"
                    }

        Examples
        --------
        .. code-block:: python

            g.delete_graph(graph_name="test")

        """
        url = self.root_url + '/graphs/' + graph_name
        return _delete_query(url, None)

    def set_current_graph(self, graph_name):
        """
        Set a current graph.

        Parameters
        ----------
        graph_name
            str
                a graph name

        Returns
        -------
            str
                current graph set to <graph_name>

        """
        self.graph_name = graph_name
        return "current graph set to " + self.graph_name

    def get_current_graph(self):
        """
        Get the current graph.

        Returns
        -------
            str
                current graph is <graph_name>

        """
        return "current graph is " + self.graph_name

    ############
    ############ add/update/delete graph data #############
    ############
    # def set_schema(self, file_path='', file_url=''):
    #     config_param = {}
    #     data = {}
    #     if file_path is not '':
    #         if 'server://' not in file_path:
    #             data = {'file_path': file_path}
    #         else:
    #             files = {'file': open(file_path, 'r')}
    #             print
    #             "open file in loacal"
    #             return
    #
    #     if file_url is not '':
    #         data = {'file_url': file_url}
    #
    #     config_param['param'] = json.dumps(data)
    #     url = self.root_url + '/' + self.graph_name + '/schema'
    #     return _post_query(url, config_param)

    # def set_user(self, user):
    #     global username
    #     username = user
    #     user_url = self.root_url + "/graphs/" + username
    #     response = requests.get(user_url)
    #     return response.content

    ##### column_header_map, column_number_map both parse and pass to the deeper level, not only one, but need to check with has header = n
    def load_table_vertex(self, column_delimiter, has_header, default_vertex_label, column_header_map,
                          column_number_map,
                          file_path='', file_url='', content_type='', data_row_start=0, data_row_end=0,
                          batch_size=10000, mode="standard", request_type='', expiration=1200, job_id=""):
        """
        Load vertex file in tabular format (require UTF-8 content type).

        Parameters
        ----------
        mode
            str
                "standard"|"timestamp_add"|"timestamp_update"|"timestamp_delete"|"optimized_init",
                // optional, default is "standard"; graph type must be 2 and graph must be empty for "optimized_init"
        column_delimiter
            str
                usually is comma for csv
        has_header
            int
                0 for no hearder and 1 for with header
        default_vertex_label
            str
                default vertex label for vertices in the file
        column_header_map
            dict
                .. code-block:: javascript

                    // only when has_header is 1
                    {
                      "vertex_id": "<column_header_for_vertex_id>",
                      // mandatory if not specified in column_number_map
                      "vertex_label": "<column_header_for_vertex_label>",
                      // optional, default is default_vertex_label
                      "timestamp":"<column_header_for_timestamp>",
                      // when mode is "timestamp_add" or "timestamp_delete", values in this column must be integers representing the Unix epoch
                      "properties": // optional, default is using column header as property name and STRING as value type
                      [
                        {
                          "<prop_name_1>": [
                            "<column_header_for_prop_name_1>",
                            "<prop_type_1>"
                          ]
                        },
                        {
                          "prop_name": <prop_name_1>,
                          "col_header": <column_header_1>,
                          "prop_type": <prop_type_1>
                        },
                        ...
                      ],
                      "ignore": [
                        "<column_header_to_ignore_1>",
                        // optional, column not to load into graph
                        ...
                      ]
                    }
        column_number_map
            dict
                .. code-block:: javascript

                    // mandatory if has_header is 0
                    {
                      "vertex_id": <column_number_for_vertex_id>,
                      // mandatory if not specified in column_header_map
                      "vertex_label": <column_number_for_vertex_label>,
                      // optional, default is default_vertex_label
                      "timestamp":<column_number_for_timestamp>,
                      // when mode is "timestamp_add" or "timestamp_delete", values in this column must be integers representing the Unix epoch
                      "properties": // mandatory if has_header is 0
                      [
                        {
                          "<prop_name_1>": [
                            <column_number_for_prop_name_1>,
                            "<prop_type_1>"
                          ]
                        },
                        {
                          "prop_name": <prop_name_1>,
                          "col_num": <column_number_1>,
                          "prop_type": <prop_type_1>
                        },
                        ...
                      ],
                      "ignore": [
                        <column_number_to_ignore_1>,
                        // optional, column not to load into graph
                        ...
                      ]
                    }
        file_path
            str
                mandatory to specify one if not file_url
        file_url
            str
                provide file content in request.files["file"], mandatory to specify one if not file_path
        data_row_start
            int
                optional, to support loading a chunk of data, start from 1
        data_row_end
            int
                optional, to support loading a chunk of data, use 0 to indicate last row
        batch_size
            int
                optional, load chunk size for one batch, default 10000
        request_type
            str
                optional, default is "", "async" | "async_kafka"
        expiration
            int
                optional, number of seconds, default 1200
        job_id
            str
                optional, the name of job_id, default ""
        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid request body"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'has_header'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid has_header '<has_header>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'default_source_label'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'default_target_label'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'default_edge_label'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column_delimiter '<column_delimiter>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid data_row_start '<start_row_number_for_data>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid data_row_end '<end_row_number_for_data>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column number for source_id '<column_number>'"
                    }
                    {
                      "status": "failure",
                      "message": "conflicting source_id in column_header_map and column_number_map"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'source_id'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column header for target_id '<column_header>'"
                    }
                    {
                      "status": "failure",
                      "message": "conflicting target_id in column_header_map and column_number_map"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'target_id'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column number for edge_label '<column_number>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column header for edge_label '<column_header>'"
                    }
                    {
                      "status": "failure",
                      "message": "conflicting edge_label in column_header_map and column_number_map"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column number for ignore '<column_number>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column header for ignore '<column_header>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid specification for property '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property name '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property type '<prop_type>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column number for property '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column header for property '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'col_num'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'col_header'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'prop_name'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'prop_type'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find specification for data file path"
                    }
                    {
                      "status": "failure",
                      "message": "invalid data file path '<file_path>'"
                    }
                    {
                      "status": "failure",
                      "message": "<the_error_message_returned_by_loading_function>"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "message": "<num_edges_added> edges are added"
                    }

            Examples
            --------
            .. code-block:: python

                vertex_file_path = "PATH_TO/VERTEX_CUSTOMER.csv"
                has_header = 0
                column_delimiter = ','
                default_vertex_label = "CUSTOMER"
                vertex_content_type = [
                                            {"orgno": [2, "STRING"]},
                                            {"origin_cino": [2, "STRING"]},
                                            {"orgno": [3, "STRING"]},
                                            {"regno": [4, "STRING"]},
                                            {"cust_name": [5, "STRING"]},
                                            {"cust_area": [6, "STRING"]},
                                            {"contrast_class": [7, "STRING"]},
                                            {"nature": [8, "STRING"]},
                                            {"scale": [9, "STRING"]},
                                            {"trace_code": [10, "STRING"]},
                                            {"establish_date": [11, "STRING"]},
                                            {"finance_flat_custom_flag": [12, "STRING"]},
                                            {"bad_flag": [13, "STRING"]},
                                            {"loan_cust": [14, "STRING"]},
                                            {"loan_bal": [15, "DOUBLE"]},
                                            {"loan_bal_other": [16, "DOUBLE"]},
                                            {"loan_bad": [17, "DOUBLE"]},
                                            {"loan_bad_other": [18, "DOUBLE"]},
                                            {"trade_bal": [19, "DOUBLE"]},
                                            {"guar_bal": [20, "DOUBLE"]},
                                            {"asset": [21, "DOUBLE"]},
                                            {"net_asset": [22, "DOUBLE"]},
                                            {"data_source": [23, "STRING"]},
                                            {"data_date": [24, "STRING"]},
                                            {"dafult_date": [25, "STRING"]},
                                            {"risk_flag": [26, "STRING"]},
                                            {"reg_area": [27, "STRING"]},
                                            {"latent_risk_custom_flag": [28, "STRING"]},
                                            {"register_capital": [29, "STRING"]},
                                            {"listing_flag": [30, "STRING"]},
                                            {"cust_policy_class": [31, "STRING"]},
                                            {"credit_set_date": [32, "STRING"]},
                                            {"five_class": [33, "STRING"]},
                                            {"latent_risk_custom_flag_date": [34, "STRING"]},
                                            {"watch_list_flag": [35, "STRING"]},
                                            {"risk_flag2": [36, "STRING"]},
                                            {"business_bal": [37, "STRING"]},
                                            {"group_id": [38, "STRING"]},
                                            {"group_id_bank": [39, "STRING"]},
                                            {"oic": [40, "STRING"]},
                                            {"group_relation_id": [41, "STRING"]},
                                            {"group_approved_amount_new": [42, "STRING"]},
                                            {"group_occupy_amount": [43, "STRING"]},
                                            {"group_maturity_date": [44, "STRING"]},
                                            {"group_name": [45, "STRING"]},
                                            {"is_per_commericial": [46, "STRING"]},
                                        ]
                column_number_map = {"vertex_id": 1, "properties": vertex_content_type}
                g.load_table_vertex(
                    file_path=vertex_file_path,
                    has_header=has_header,
                    column_delimiter=column_delimiter,
                    default_vertex_label=default_vertex_label,
                    column_number_map=column_number_map,
                    column_header_map={},
                    content_type=vertex_content_type,
                    data_row_start=0,
                    data_row_end=0,
                    batch_size=10000)

        """
        config_param = {}
        data = {}
        async_setting = {"expiration": expiration}

        if job_id:
            async_setting["job_id"] = job_id
        else:
            if file_path:
                async_setting["job_id"] = "load_vertex::" + file_path
            if file_url:
                async_setting["job_id"] = "load_vertex::" + file_url
        config_param["async"] = json.dumps(async_setting)

        if request_type:
            url = self.root_url + "/{}/graphs/".format(request_type) + self.graph_name + '/table/vertex'
        else:
            url = self.root_url + "/graphs/" + self.graph_name + '/table/vertex'

        if file_path is not '':
            if 'server://' in file_path:

                if has_header == 1:
                    if column_header_map.has_key('vertex_id'):
                        data = {
                            "mode": mode,
                            "file_path": file_path[9:],
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            'default_vertex_label': default_vertex_label,
                            'column_header_map': column_header_map,
                            'data_row_start': data_row_start,
                            'data_row_end': data_row_end,
                            "batch_size": batch_size
                        }
                    else:
                        return "column header for vertex_id is required"
                else:
                    if column_number_map.has_key('vertex_id'):
                        data = {
                            "mode": mode,
                            "file_path": file_path[9:],
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            'default_vertex_label': default_vertex_label,
                            'column_number_map': column_number_map,
                            'data_row_start': data_row_start,
                            'data_row_end': data_row_end,
                            "batch_size": batch_size
                        }
                config_param['param'] = json.dumps(data)
                return _post_query(url, config_param)

            else:
                if has_header == 1:
                    if column_header_map.has_key('vertex_id'):
                        data = {
                            "mode": mode,
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            "default_vertex_label": default_vertex_label,
                            "column_header_map": column_header_map,
                            "data_row_start": data_row_start,
                            "data_row_end": data_row_end,
                            "batch_size": batch_size
                        }
                        config_param['param'] = json.dumps(data)
                        return _post_query_files(url, config_param, file_path)

                    else:
                        return "column header for vertex_id is required"
                else:
                    if column_number_map.has_key('vertex_id'):
                        data = {
                            "mode": mode,
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            'default_vertex_label': default_vertex_label,
                            'column_number_map': column_number_map,
                            'data_row_start': data_row_start,
                            'data_row_end': data_row_end,
                            "batch_size": batch_size

                        }
                        config_param['param'] = json.dumps(data)
                        return _post_query_files(url, config_param, file_path)

                    else:
                        return "column number for vertex_id is required"

        elif file_url is not '':
            if has_header == 1:
                if column_header_map.has_key('vertex_id'):
                    data = {
                        "mode": mode,
                        "file_url": file_url,
                        "column_delimiter": column_delimiter,
                        "has_header": has_header,
                        'default_vertex_label': default_vertex_label,
                        'column_header_map': column_header_map,
                        'data_row_start': data_row_start,
                        'data_row_end': data_row_end,
                        "batch_size": batch_size
                    }
                else:
                    return "column header for vertex_id is required"
            else:
                if column_number_map.has_key('vertex_id'):
                    data = {
                        "mode": mode,
                        "file_url": file_url,
                        "column_delimiter": column_delimiter,
                        "has_header": has_header,
                        'default_vertex_label': default_vertex_label,
                        'column_number_map': column_number_map,
                        'data_row_start': data_row_start,
                        'data_row_end': data_row_end,
                        "batch_size": batch_size
                    }
            config_param['param'] = json.dumps(data)
            return _post_query(url, config_param)

        else:
            pass

    def load_table_edge(self, column_delimiter, has_header, default_source_label, default_target_label,
                        default_edge_label, column_header_map, column_number_map,
                        file_path='', file_url='', content_type='', data_row_start=0, data_row_end=0, batch_size=10000,
                        mode="standard", request_type='', expiration=1200, job_id=""):
        """
        Load edge file in tabular format (require UTF-8 content type).

        Parameters
        ----------
        mode
            str
                "standard"|"timestamp_add"|"timestamp_update"|"timestamp_delete"|"optimized_init",
                // optional, default is "standard"; graph type must be 2 and graph must be empty for "optimized_init"
        column_delimiter
            str
                usually is comma for csv
        has_header
            int
                0 for no hearder and 1 for with header
        default_source_label
            str
                all source vertices in the data file should have the same vertex label which is equal to the value of default_source_label
        default_target_label
            str
                all target vertices in the data file should have the same vertex label which is equal to the value of default_target_label
        default_edge_label
            str
                default edge label for edges in the file
        column_header_map
            dict
                .. code-block:: javascript

                    // only when has_header is 1
                    {
                      "source_id": "<column_header_for_source_vertex_id>",
                      // mandatory if not specified in column_number_map
                      "target_id": "<column_header_for_target_vertex_id>",
                      // mandatory if not specified in column_number_map
                      "edge_label": "<column_header_for_edge_label>",
                      // optional, default is default_edge_label
                      "source_label":"<column_header_for_source_vertex_label>",
                      // optional, default is default_source_label
                      "target_label":"<column_header_for_target_vertex_label>",
                      // optional, default is default_target_label
                      "timestamp":"<column_header_for_timestamp>",
                      // when mode is "timestamp_add" or "timestamp_delete", values in this column must be integers representing the Unix epoch
                      "properties": // optional, default is using column header as property name and STRING as value type
                      [
                        {
                          "<prop_name_1>": [
                            "<column_header_for_prop_name_1>",
                            "<prop_type_1>"
                          ]
                        },
                        {
                          "prop_name": <prop_name_1>,
                          "col_header": <column_header_1>,
                          "prop_type": <prop_type_1>
                        },
                        ...
                      ],
                      "ignore": [
                        "<column_header_to_ignore_1>",
                        // optional, column not to load into graph
                        ...
                      ]
                    }

        column_number_map
            dict
                .. code-block:: javascript

                    // only when has_header is 1
                    {
                      "source_id": "<column_header_for_source_vertex_id>",
                      // mandatory if not specified in column_number_map
                      "target_id": "<column_header_for_target_vertex_id>",
                      // mandatory if not specified in column_number_map
                      "edge_label": "<column_header_for_edge_label>",
                      // optional, default is default_edge_label
                      "source_label":"<column_number_for_source_vertex_label>",
                      // optional, default is default_source_label
                      "target_label":"<column_number_for_target_vertex_label>",
                      // optional, default is default_target_label
                      "timestamp":<column_number_for_timestamp>,
                      // when mode is "timestamp_add" or "timestamp_delete", values in this column must be integers representing the Unix epoch
                      "properties": // optional, default is using column header as property name and STRING as value type
                      [
                        {
                          "<prop_name_1>": [
                            "<column_header_for_prop_name_1>",
                            "<prop_type_1>"
                          ]
                        },
                        {
                          "prop_name": <prop_name_1>,
                          "col_header": <column_header_1>,
                          "prop_type": <prop_type_1>
                        },
                        ...
                      ],
                      "ignore": [
                        "<column_header_to_ignore_1>",
                        // optional, column not to load into graph
                        ...
                      ]
                    }

        file_path
            str
                mandatory to specify one if not file_url
        file_url
            str
                provide file content in request.files["file"], mandatory to specify one if not file_path
        data_row_start
            int
                optional, to support loading a chunk of data, start from 1
        data_row_end
            int
                optional, to support loading a chunk of data, use 0 to indicate last row
        batch_size
            int
                optional, load chunk size for one batch, default 10000
        request_type
            str
                optional, default is "", "async" | "async_kafka"
        expiration
            int
                optional, number of seconds, default 1200
        job_id
            str
                optional, the name of job_id, default ""

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid request body"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'has_header'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid has_header '<has_header>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'default_source_label'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'default_target_label'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'default_edge_label'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column_delimiter '<column_delimiter>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid data_row_start '<start_row_number_for_data>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid data_row_end '<end_row_number_for_data>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column number for source_id '<column_number>'"
                    }
                    {
                      "status": "failure",
                      "message": "conflicting source_id in column_header_map and column_number_map"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'source_id'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column header for target_id '<column_header>'"
                    }
                    {
                      "status": "failure",
                      "message": "conflicting target_id in column_header_map and column_number_map"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'target_id'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column number for edge_label '<column_number>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column header for edge_label '<column_header>'"
                    }
                    {
                      "status": "failure",
                      "message": "conflicting edge_label in column_header_map and column_number_map"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column number for ignore '<column_number>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column header for ignore '<column_header>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid specification for property '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property name '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property type '<prop_type>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column number for property '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid column header for property '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'col_num'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'col_header'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'prop_name'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find key 'prop_type'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find specification for data file path"
                    }
                    {
                      "status": "failure",
                      "message": "invalid data file path '<file_path>'"
                    }
                    {
                      "status": "failure",
                      "message": "<the_error_message_returned_by_loading_function>"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "message": "<num_edges_added> edges are added"
                    }

        Examples
        --------
        .. code-block:: python

            edge_file_path = "PATH_TO/EDGE_TX.csv"
            has_header = 0
            column_delimiter = ','
            default_source_label = "CUSTOMER"
            default_target_label = "CUSTOMER"
            default_edge_label = "_"  # We have defined edge lable in csv file column 1
            edge_content_type = [
                                    {"cino_source_name": [4, "STRING"]},
                                    {"cino_target_name": [5, "STRING"]},
                                    {"tx_cnt": [6, "DOUBLE"]},
                                    {"tx_amt": [7, "DOUBLE"]},
                                    {"data_source": [8, "STRING"]},
                                    {"data_date": [9, "STRING"]},
                                    {"p_date": [10, "STRING"]},
                                    {"main_rela": [11, "STRING"]},
                                ]
            edge_column_number_map = {
                "source_id": 2,
                "target_id": 3,
                "edge_label": 1,
                "properties": edge_content_type
            }
            g.load_table_edge(
                file_path=edge_file_path,
                has_header=has_header,
                column_delimiter=column_delimiter,
                default_source_label=default_source_label,
                default_target_label=default_target_label,
                default_edge_label=default_edge_label,
                column_header_map={},
                column_number_map=edge_column_number_map,
                data_row_start=0,
                data_row_end=0,
                batch_size=10000)

        Notes
        -----
        - "column_number_map" and "column_header_map" allow the caller to specify property name and property value type by either referring to the column index number or the column header of the csv file. When there is no header, column_number_map must be used. When there is header, either column_number_map or column_header_map or both can be used. Specifications from both column_number_map and column_header_map are merged. Any conflict will return in an error message.
        - "default_X_label" (X can be vertex, edge, source, target) is applied when neither "column_header_map" nor "column_number_map" specify the column for the label of vertex/edge/source/target, or when the specified column has empty value for a row.
        - "data_row_start" and "data_row_end" (optional) are used to specify the block of data to be loaded if not all data are to be loaded. 0 means all are loaded.
        - The row/column number starts from 1.
        - When there is no header in the data file, any column that is not specified in column_number_map is ignored. When there is header in the data file, only columns specified in column_header_map's ignore or column_number_map's ignore are ignored.
        - All columns in column_header_map's ignore or column_number_map's ignore are ignored (not loaded), even when they occur in column_header_map's properties or column_number_map's properties at the same time.
        - The columns to indicate vertex_id, source_id, and target_id can’t occur in the ignore list.
        - If the value type of a property is not specified, the property value type specified in the graph schema is used. If the graph doesn’t already have a schema, the default STRING value type is used.
        - Currently the maximum length for a string property value is 512. The maximum size of a numerical vector property value is 512/sizeof(type) (4 for int and float, 8 for int64 and double).

        """

        config_param = {}
        data = {}
        async_setting = {"expiration": expiration}

        if job_id:
            async_setting["job_id"] = job_id
        else:
            if file_path:
                async_setting["job_id"] = "load_vertex::" + file_path
            if file_url:
                async_setting["job_id"] = "load_vertex::" + file_url
        config_param["async"] = json.dumps(async_setting)

        if request_type:
            url = self.root_url + "/{}/graphs/".format(request_type) + self.graph_name + '/table/edge'
        else:
            url = self.root_url + "/graphs/" + self.graph_name + '/table/edge'

        if file_path is not '':
            if 'server://' in file_path:
                if has_header == 1:
                    if column_header_map.has_key('source_id') and column_header_map.has_key('target_id'):
                        data = {
                            "mode": mode,
                            "file_path": file_path[9:],
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            'default_source_label': default_source_label,
                            'default_target_label': default_target_label,
                            'default_edge_label': default_edge_label,
                            'column_header_map': column_header_map,
                            'content_type': content_type,
                            'data_row_start': data_row_start,
                            'data_row_end': data_row_end,
                            "batch_size": batch_size
                        }
                    else:
                        return "column header for vertex_id is required"
                else:
                    if column_number_map.has_key('source_id'):
                        data = {
                            "mode": mode,
                            "file_path": file_path[9:],
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            'default_source_label': default_source_label,
                            'default_target_label': default_target_label,
                            'default_edge_label': default_edge_label,
                            'column_number_map': column_number_map,
                            'content_type': content_type,
                            'data_row_start': data_row_start,
                            'data_row_end': data_row_end,
                            "batch_size": batch_size
                        }
                config_param['param'] = json.dumps(data)
                return _post_query(url, config_param)
            else:
                if has_header == 1:
                    if column_header_map.has_key('source_id') and column_header_map.has_key('target_id'):
                        data = {
                            "mode": mode,
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            'default_source_label': default_source_label,
                            'default_target_label': default_target_label,
                            'default_edge_label': default_edge_label,
                            'column_header_map': column_header_map,
                            'content_type': content_type,
                            'data_row_start': data_row_start,
                            'data_row_end': data_row_end,
                            "batch_size": batch_size
                        }
                        config_param['param'] = json.dumps(data)
                        return _post_query_files(url, config_param, file_path)
                    else:
                        return "column header for vertex_id is required"
                else:
                    if column_number_map.has_key('source_id'):
                        data = {
                            "mode": mode,
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            'default_source_label': default_source_label,
                            'default_target_label': default_target_label,
                            'default_edge_label': default_edge_label,
                            'column_number_map': column_number_map,
                            'content_type': content_type,
                            'data_row_start': data_row_start,
                            'data_row_end': data_row_end,
                            "batch_size": batch_size
                        }
                        config_param['param'] = json.dumps(data)
                        return _post_query_files(url, config_param, file_path)

        elif file_url is not '':
            if has_header == 1:
                if column_header_map.has_key('source_id') and column_header_map.has_key('target_id'):
                    data = {
                        "mode": mode,
                        "file_url": file_url,
                        "column_delimiter": column_delimiter,
                        "has_header": has_header,
                        'default_source_label': default_source_label,
                        'default_target_label': default_target_label,
                        'default_edge_label': default_edge_label,
                        'column_header_map': column_header_map,
                        'content_type': content_type,
                        'data_row_start': data_row_start,
                        'data_row_end': data_row_end,
                        "batch_size": batch_size
                    }
                else:
                    return "column header for vertex_id is required"
            else:
                if column_number_map.has_key('source_id'):
                    data = {
                        "mode": mode,
                        "file_url": file_url,
                        "column_delimiter": column_delimiter,
                        "has_header": has_header,
                        'default_source_label': default_source_label,
                        'default_target_label': default_target_label,
                        'default_edge_label': default_edge_label,
                        'column_number_map': column_number_map,
                        'content_type': content_type,
                        'data_row_start': data_row_start,
                        'data_row_end': data_row_end,
                        "batch_size": batch_size
                    }
            config_param['param'] = json.dumps(data)
            return _post_query(url, config_param)
        else:
            pass

    def load_json_file(self, file_path='', file_url=''):
        """
        Load vertices and edges from json file (the graph MUST be created with a schema that contains all vertices/edges labels and property names and value types that occur in json).

        Parameters
        ----------
        file_path
            str
                json file path, mandatory if file_url not provided
        file_url
            str
                json file url, mandatory if file_path not provided

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid request body"
                    }
                    {
                      "status": "failure",
                      "message": "invalid data file path '<file_path>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to save data file '<data_file_name_or_url>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to load json data"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_edges": "<num_edges_added>",
                        "num_vertices": "<num_vertices_added>"
                      }
                    }

        Examples
        --------
        .. code-block:: python

            g.load_json_file(file_path="PATH_TO/json_load_test.json")

        Notes
        -----
        Json File Format
            .. code-block:: json

                {
                  "data": {
                    "vertices": [
                      {
                        "id": "<vertex_id_1>",
                        "label": "<vertex_label_1>",
                        "properties": [
                          {
                            "<prop_name_1>": "<prop_value_1>"
                          },
                          {
                            "<prop_name_2>": "<prop_value_2>"
                          },
                          "..."
                        ]
                      },
                      "..."
                    ],
                    "edges": [
                      {
                        "source_id": "<source_id>",
                        "source_label": "<source_label>",
                        "target_id": "<target_id>",
                        "target_label": "<target_label>",
                        "label": "<edge_label>",
                        "properties": [
                          {
                            "<prop_name_1>": "<prop_value_1>"
                          },
                          {
                            "<prop_name_2>": "<prop_value_2>"
                          },
                          "..."
                        ]
                      },
                      "..."
                    ]
                  }
                }

        """
        url = self.root_url + '/graphs/' + self.graph_name + '/json'
        config_param = {}
        data = {}
        if file_path and file_url:
            return "Only one file should be given."
        elif file_path:
            data["file_path"] = file_path
        elif file_url:
            data["file_url"] = file_url
        else:
            return "No file is give."
        config_param["param"] = json.dumps(data)
        logging.debug(config_param)
        return _post_query(url, config_param)

    def load_json_string(self, json_str):
        """
        Load vertices and edges from json string (the graph MUST be created with a schema to cover all vertices/edges labels and property names and value types to be included in json).

        Parameters
        ----------
        json_str
            str
                string with the format in notes of load_json_file().

        Returns
        -------
            str
                DB_ERROR

                    .. code-block:: json

                        {
                          "status": "failure",
                          "message": "invalid graph name '<graph_name>'"
                        }
                        {
                          "status": "failure",
                          "message": "cannot find graph '<graph_name>'"
                        }
                        {
                          "status": "failure",
                          "message": "fail to open graph '<graph_name>'"
                        }
                        {
                          "status": "failure",
                          "message": "invalid request body"
                        }
                        {
                          "status": "failure",
                          "message": "fail to load json data"
                        }

                DB_OK

                    .. code-block:: json

                        {
                          "status": "success",
                          "statistics": {
                            "num_edges": "<num_edges_added>",
                            "num_vertices": "<num_vertices_added>"
                          }
                        }

        Examples
        --------
        .. code-block:: python

            json_str = '''
                        {
                          "data": {
                            "vertices": [
                              {
                                "label": "v2",
                                "properties": [
                                  {
                                    "p1": "first"
                                  },
                                  {
                                    "p2": 1.1
                                  }
                                ],
                                "id": "1"
                              },
                              {
                                "label": "v2",
                                "properties": [
                                  {
                                    "p1": "second"
                                  },
                                  {
                                    "p2": 1.2
                                  }
                                ],
                                "id": "2"
                              },
                              {
                                "label": "v2",
                                "properties": [
                                  {
                                    "p1": "third"
                                  },
                                  {
                                    "p2": 1.3
                                  }
                                ],
                                "id": "3"
                              },
                              {
                                "label": "v1",
                                "properties": [
                                  {
                                    "p1": "first"
                                  },
                                  {
                                    "p2": 1.1
                                  }
                                ],
                                "id": "1"
                              },
                              {
                                "label": "v1",
                                "properties": [
                                  {
                                    "p1": "second"
                                  },
                                  {
                                    "p2": 1.2
                                  }
                                ],
                                "id": "2"
                              },
                              {
                                "label": "v1",
                                "properties": [
                                  {
                                    "p1": "third"
                                  },
                                  {
                                    "p2": 1.3
                                  }
                                ],
                                "id": "3"
                              }
                            ],
                            "edges": [
                              {
                                "source_label": "v2",
                                "target_label": "v2",
                                "target_id": "2",
                                "label": "e2",
                                "source_id": "1",
                                "properties": [
                                  {
                                    "p1": "first"
                                  },
                                  {
                                    "p2": 1
                                  }
                                ]
                              },
                              {
                                "source_label": "v2",
                                "target_label": "v2",
                                "target_id": "3",
                                "label": "e2",
                                "source_id": "2",
                                "properties": [
                                  {
                                    "p1": "second"
                                  },
                                  {
                                    "p2": 2
                                  }
                                ]
                              },
                              {
                                "source_label": "v2",
                                "target_label": "v2",
                                "target_id": "1",
                                "label": "e2",
                                "source_id": "3",
                                "properties": [
                                  {
                                    "p1": "third"
                                  },
                                  {
                                    "p2": 3
                                  }
                                ]
                              },
                              {
                                "source_label": "v1",
                                "target_label": "v1",
                                "target_id": "2",
                                "label": "e1",
                                "source_id": "1",
                                "properties": [
                                  {
                                    "p1": "first"
                                  },
                                  {
                                    "p2": 1
                                  }
                                ]
                              },
                              {
                                "source_label": "v1",
                                "target_label": "v1",
                                "target_id": "3",
                                "label": "e1",
                                "source_id": "2",
                                "properties": [
                                  {
                                    "p1": "second"
                                  },
                                  {
                                    "p2": 2
                                  }
                                ]
                              },
                              {
                                "source_label": "v1",
                                "target_label": "v1",
                                "target_id": "1",
                                "label": "e1",
                                "source_id": "3",
                                "properties": [
                                  {
                                    "p1": "third"
                                  },
                                  {
                                    "p2": 3
                                  }
                                ]
                              }
                            ]
                          }
                        }
                        '''
            g.load_json_string(json_str=json_str)

        """
        url = self.root_url + '/graphs/' + self.graph_name + '/json'
        config_param = {}
        config_param["param"] = json_str
        # logging.debug(config_param)
        return _post_query(url, config_param)

    def add_vertex(self, vertex_label, vertex_id, prop_dict=[]):
        """
        Add a new vertex to the graph (optional properties).

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        prop_dict
            list (optional, list of properties)
                .. code-block:: javascript

                    [
                      {
                        "prop_name": <prop_name_1>,
                        "prop_value": <prop_value_1>,
                        "prop_type": <prop_type_1>
                      },
                      ...
                    ]

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex id '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid request body"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property name '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property type '<prop_type>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property value '<prop_value>'"
                    }
                    {
                      "status": "failure",
                      "message": "already exist vertex '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to set vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to add vertex '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "conflicting property type for '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to set property id for '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to set property for '<prop_name>'"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success"
                    }

        Examples
        --------
        .. code-block:: python

            g.add_vertex(vertex_id="1", vertex_label="v1", prop_dict=[
                        {
                        "prop_name": "p1",
                        "prop_value": "first",
                        "prop_type": "STRING"
                        },
                        {
                        "prop_name": "p2",
                        "prop_value": 1.1,
                        "prop_type": "DOUBLE"
                        }
                        ])


        """
        config_param = {}
        data = {}
        data['properties'] = prop_dict
        config_param['param'] = json.dumps(data)
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id
        return _post_query(url, config_param)

    def add_edge(self, source_id, source_label, target_id, target_label, edge_label, prop_dict=[],
                 add_vertex_if_not_exist=1):
        """

        Parameters
        ----------
        source_id
            str
                source vertex id
        source_label
            str
                source vertex label
        target_id
            str
                target vertex id
        target_label
            str
                target vertex label
        edge_label
            str
                edge label
        prop_dict
            list (optional, list of properties)
                .. code-block:: javascript

                    [
                      {
                        "prop_name": <prop_name_1>,
                        "prop_value": <prop_value_1>,
                        "prop_type": <prop_type_1>
                      },
                      ...
                    ]

        add_vertex_if_not_exist
            int
                optional, 0|1, if the vertex that occurs in the edge doesn not exist in the graph, whether to add it or report error, default is 1

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid source label '<source_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid source id '<source_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid target label '<target_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid target id '<target_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid request body"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property name '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property type '<prop_type>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property value '<prop_value>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<source_label>' (when add_vertex_if_not_exist=0)"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<target_label> (when add_vertex_if_not_exist=0)'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<source_id>' (when add_vertex_if_not_exist=0)"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get vertex '<source_id>' (when add_vertex_if_not_exist=0)"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<target_id>' (when add_vertex_if_not_exist=0)"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get vertex '<target_id>' (when add_vertex_if_not_exist=0)"
                    }
                    {
                      "status": "failure",
                      "message": "fail to set vertex label '<source_label>' (when add_vertex_if_not_exist=1)"
                    }
                    {
                      "status": "failure",
                      "message": "fail to set vertex label '<target_label>' (when add_vertex_if_not_exist=1)"
                    }
                    {
                      "status": "failure",
                      "message": "fail to add vertex '<source_id>' (when add_vertex_if_not_exist=1)"
                    }
                    {
                      "status": "failure",
                      "message": "fail to add vertex '<target_id>' (when add_vertex_if_not_exist=1)"
                    }
                    {
                      "status": "failure",
                      "message": "fail to set edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to add edge"
                    }
                    {
                      "status": "failure",
                      "message": "conflicting property type for '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to set property id for '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to set property for '<prop_name>'"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success"
                    }


        Examples
        --------
        .. code-block:: python

            g.add_edge(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_label="e1", prop_dict=[
                      {
                      "prop_name": "p1",
                      "prop_value": "first",
                      "prop_type": "STRING"
                      },
                      {
                      "prop_name": "p2",
                      "prop_value": 1,
                      "prop_type": "INT"
                      }
                      ])

        """
        config_param = {}
        data = {}
        data['properties'] = prop_dict
        data["add_vertex_if_not_exist"] = add_vertex_if_not_exist
        config_param['param'] = json.dumps(data)
        url = self.root_url + '/graphs/' + self.graph_name + '/edges/' + source_label + '/' + source_id + '/' + target_label + '/' + target_id + '/' + edge_label
        return _post_query(url, config_param)

    def update_vertex(self, vertex_label, vertex_id, prop):
        """
        Update an existing vertex.

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        prop
            list (optional, list of properties)
                .. code-block:: javascript

                    [
                      {
                        "prop_name": <prop_name_1>,
                        "prop_value": <prop_value_1>,
                        "prop_type": <prop_type_1>
                      },
                      ...
                    ]

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex id '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid request body"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property name '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property type '<prop_type>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property value '<prop_value>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "conflicting property type for '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to set property id for '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to set property for '<prop_name>'"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success"
                    }

        Examples
        --------
        .. code-block:: python

            g.update_vertex(vertex_id="1", vertex_label="v1", prop=[
                            {
                            "prop_name": "p1",
                            "prop_value": "first_changed",
                            "prop_type": "STRING"
                            },
                            {
                            "prop_name": "p2",
                            "prop_value": 2.3,
                            "prop_type": "DOUBLE"
                            }
                            ])

        """
        config_param = {}
        data = {}
        data['properties'] = prop
        config_param['param'] = json.dumps(data)
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id
        return _put_query(url, config_param)

    def update_edge(self, source_id, source_label, target_id, target_label, prop, edge_id='', edge_label=""):
        """
        Update a specific edge between two existing vertices.

        Parameters
        ----------
        source_id
            str
                source vertex id
        source_label
            str
                source vertex label
        target_id
            str
                target vertex id
        target_label
            str
                target vertex label
        prop
            list (optional, list of properties)
                .. code-block:: javascript

                    [
                      {
                        "prop_name": <prop_name_1>,
                        "prop_value": <prop_value_1>,
                        "prop_type": <prop_type_1>
                      },
                      ...
                    ]

        edge_id
            str
                internal edge id
        edge_label
            str
                edge label

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid source label '<source_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid source id '<source_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid target label '<target_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid target id '<target_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid edge id '<eid>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid request body"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property name '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property type '<prop_type>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid property value '<prop_value>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<source_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<source_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<target_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<target_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge '<eid>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edge '<eid>'"
                    }
                    {
                      "status": "failure",
                      "message": "conflicting property type for '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to set property id for '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to set property for '<prop_name>'"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success"
                    }


        Examples
        --------
        .. code-block:: python

            g.update_edge(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_label="e1", edge_id="13835058055282163712", prop=[
              {
              "prop_name": "p1",
              "prop_value": "changed",
              "prop_type": "STRING"
              },
              {
              "prop_name": "p2",
              "prop_value": 23,
              "prop_type": "INT"
              }
              ])


        """
        url = self.root_url
        if edge_id is not '' and not edge_label:
            url = self.root_url + '/graphs/' + self.graph_name + '/edges/' + source_label + '/' + source_id + '/' + target_label + '/' + target_id + '/' \
                  + edge_id + '/' + edge_label
        # Update all existing edges between two existing vertices
        elif edge_id is '' and not edge_label:
            url = self.root_url + '/graphs/' + self.graph_name + '/edges/' + source_label + '/' + source_id + '/' + target_label + '/' + target_id
        # Update all existing edges of a specific label between two existing vertices
        elif edge_id is not '' and edge_label:
            url = self.root_url + '/graphs/' + self.graph_name + '/edges/' + source_label + '/' + source_id + '/' + target_label + '/' + target_id + '/' + edge_label + '/' + edge_id
        config_param = {}
        data = {}
        data['properties'] = prop
        config_param['param'] = json.dumps(data)
        logging.debug(config_param)
        return _put_query(url, config_param)

    def delete_vertex(self, vertex_label, vertex_id=''):
        """
        Delete a vertex or delete all vertices given one or more labels

        Parameters
        ----------
        vertex_label
            str | list
                vertex label of a specific vertex | vertex labels
        vertex_id
            str
                if vertex_label is string, need to specify the vertex id

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get vertices of label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to delete vertex '<vertex_id>'"
                    }

            DB_WARNING

                .. code-block:: json

                    {
                      "status": "warning",
                      "message": "cannot find vertices of given label/s"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success"
                    }

        Examples
        --------
        .. code-block:: python

            g.delete_vertex(vertex_id="1", vertex_label="v1")
            g.delete_vertex(vertex_label=["v1", "v2"])

        """
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/'
        if isinstance(vertex_label, basestring):
            url += vertex_label + '/' + vertex_id
        elif isinstance(vertex_label, list):
            url = _url_assemble(url, vertex_label)
        logging.debug(url)
        return _delete_query(url, None)

    def delete_edge(self, source_id, source_label, target_id, target_label, edge_label=[], edge_id=''):
        """
        Delete a specific edge between two existing vertices, or delete all edges between two existing vertices, or delete all edges of one or more specific labels between two existing vertices.

        Parameters
        ----------
        source_id
            str
                source vertex id
        source_label
            str
                source vertex label
        target_id
            str
                target vertex id
        target_label
            str
                target vertex label
        edge_label
            str | list
                optional, edge label for a specific edge | list of edge labels
        edge_id
            str
                optional, internal id to specify an edge

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid source label '<source_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid source id '<source_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid target label '<target_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid target id '<target_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<source_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<source_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<target_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<target_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get schema"
                    }
                    {
                      "status": "failure",
                      "message": "fail to delete edge between given source and target"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge '<eid>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to delete edge '<eid>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to delete edge between given source and target of label '<edge_label>'"
                    }

            DB_WARNING

                .. code-block:: json

                    {
                      "status": "warning",
                      "message": "cannot find edge between given source and target"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "message": "<num_edge_deleted> edge/s is/are deleted"
                    }

        Examples
        --------
        .. code-block:: python

            g.delete_edge(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_id="13835058055282163717", edge_label="e1")
            g.delete_edge(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_label="e1")
            g.delete_edge(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_label=["e2"])
            g.delete_edge(source_id="1", source_label="v1", target_id="2", target_label="v1")


        """
        url = self.root_url + '/graphs/' + self.graph_name + '/edges/' + source_label + '/' + source_id + '/' + target_label + '/' + target_id + '/'
        if isinstance(edge_label, basestring):
            if edge_id is '':
                url += edge_label
            else:
                url += edge_label + '/' + edge_id
        elif isinstance(edge_label, list):
            if edge_label:
                logging.debug("print the edge_label {}".format(edge_label))
                url = _url_assemble(url, edge_label)
                if edge_id is not '':
                    return "Input of edge_id({}) is not '' for a list of edge_label!".format(edge_id)
            else:
                url = self.root_url + '/graphs/' + self.graph_name + '/edges/' + source_label + '/' + source_id + '/' + target_label + '/' + target_id
                if edge_id is not '':
                    return "Input of edge_id({}) is not '' for a list of edge_label!".format(edge_id)
        logging.debug(url)
        return _delete_query(url, None)

        # if edge_id is '' and not edge_label:
        #     url = self.root_url + '/graphs/' + self.graph_name + '/edges/' + source_label + '/' + source_id + '/' + target_label + '/' + target_id
        # # Delete a specific edge between two existing vertices
        # if edge_id is not '' and edge_label:
        #     url = self.root_url + '/graphs/' + self.graph_name + '/edges/' + source_label + '/' + source_id + '/' + target_label + '/' + target_id + '/' + edge_label + '/' + edge_id + \
        #           '/'
        #     url = _url_assemble(url, edge_label)
        # if edge_id is '' and edge_label:
        #     url = self.root_url + '/graphs/' + self.graph_name + '/edges/' + source_label + '/' + source_id + '/' + target_label + '/' + target_id + '/'
        #     url = _url_assemble(url, edge_label)
        # return _delete_query(url, None)

    def delete_vprop(self, vertex_label, vertex_id, prop_dict):
        """
        Delete specific properties from a vertex.

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        prop_dict
            list
                .. code-block:: javascript

                    [
                      {
                        "prop_name": <prop_name_1>,
                        "prop_value": <prop_value_1>,
                        "prop_type": <prop_type_1>
                      },
                      ...
                    ]

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex id '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid request body"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex property '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get vertex property '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to delete property '<prop_name>'"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success"
                    }

        Examples
        --------
        .. code-block:: python

            g.delete_vprop(vertex_label="v1", vertex_id="1", prop_dict=["p1", "p2"])


        """
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id + '/properties'
        config_param = {}
        data = {}
        data['properties'] = prop_dict
        config_param['param'] = json.dumps(data)
        return _delete_query(url, config_param)

    def delete_eprop(self, source_id, source_label, target_id, target_label, prop_dict, edge_label=[], edge_id=''):
        """
        Delete specific properties of a specific edge between two existing vertices, or delete specific properties of all edges between two existing vertices, or delete specific properties of all edges of one or more specific labels between two existing vertices.

        Parameters
        ----------
        source_id
            str
                source vertex id
        source_label
            str
                source vertex label
        target_id
            str
                target vertex id
        target_label
            str
                target vertex label
        prop_dict
            list
                .. code-block:: javascript

                    [
                      {
                        "prop_name": <prop_name_1>,
                        "prop_value": <prop_value_1>,
                        "prop_type": <prop_type_1>
                      },
                      ...
                    ]

        edge_label
            str | list
                optional, edge label for a specific edge | list of edge labels
        edge_id
            str
                optional, internal id to specify an edge

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid source label '<source_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid source id '<source_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid target label '<target_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid target id '<target_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid edge id '<eid>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<source_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<source_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<target_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<target_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge '<eid>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edge '<eid>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid request body"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge property '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edge property '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to delete property '<prop_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edge between given source and target of label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge '<eid>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edge '<eid>'"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success"
                    }

        Examples
        --------
        .. code-block:: python

            g.delete_eprop(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_id="13835058055282163712", edge_label="e1", prop_dict=["p1", "p2"])
            g.delete_eprop(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_label="e1", prop_dict=["p1", "p2"])
            g.delete_eprop(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_label=["e2"], prop_dict=["p1", "p2"])
            g.delete_eprop(source_id="1", source_label="v1", target_id="2", target_label="v1", prop_dict=["p1", "p2"])


        """
        url = self.root_url + '/graphs/' + self.graph_name + '/edges/' + source_label + '/' + source_id + '/' + target_label + '/' + target_id + '/'
        if isinstance(edge_label, basestring):
            if edge_id is '':
                url += edge_label
            else:
                url += edge_label + '/' + edge_id
        elif isinstance(edge_label, list):
            if edge_label:
                logging.debug("print the edge_label {}".format(edge_label))
                url = _url_assemble(url, edge_label)
                if edge_id is not '':
                    return "Input of edge_id({}) is not '' for a list of edge_label!".format(edge_id)
            else:
                url = self.root_url + '/graphs/' + self.graph_name + '/edges/' + source_label + '/' + source_id + '/' + target_label + '/' + target_id
                if edge_id is not '':
                    return "Input of edge_id({}) is not '' for a list of edge_label!".format(edge_id)
        url += "/properties"
        logging.debug(url)
        config_param = {}
        data = {}
        data['properties'] = prop_dict
        config_param['param'] = json.dumps(data)
        return _delete_query(url, config_param)

    #############
    ##############  Get Graph Data ################
    #############

    # def get_graph(self):
    #     url = self.root_url + "/graphs/whole/" + username
    #     data = None
    #     response = requests.post(url, data=data)
    #     result = json.loads(response.content)
    #     result = json.dumps(result, indent=4, sort_keys=True)
    #     return result

    def get_schema(self, graph_name):
        """
        Get the schema of the graph.

        Parameters
        ----------
        graph_name
            str
                a graph name

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get schema"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "schema": {
                        "vertex_labels": [
                          "<vertex_label_1>",
                          "<vertex_label_2>"
                        ],
                        "edge_labels": [
                          "<edge_label_1>",
                          "<edge_label_2>"
                        ],
                        "vertex_props": [
                          {
                            "prop_name": "<prop_name_1>",
                            "prop_type": "<prop_type_1>"
                          },
                          "..."
                        ],
                        "edge_props": [
                          {
                            "prop_name": "<prop_name_1>",
                            "prop_type": "<prop_type_1>"
                          },
                          "..."
                        ]
                      }
                    }

        Examples
        --------
        .. code-block:: python

            g.get_schema(graph_name="test")

        """
        url = self.root_url + '/graphs/' + graph_name + '/schema'
        return _query(url)

    # Get a vertex given id and label
    def get_vertex(self, vertex_label=[], vertex_id='', prop=[], max_num_vertices=float("inf")):
        """
        Get a vertex given id and label, or get vertices given id without label, or get all vertices given one or more labels.

        Parameters
        ----------
        vertex_label
            str | list
                a vertex label for the specific vertex | list of vertex labels
        vertex_id
            str
                mandatory when vertex_label is string
        prop
            list | "id_only"
                optional, properties to be returned, "id_only" is a reserved keyword for no property return
        max_num_vertices
            int
                optional, limited the returning number of vertices, should > 0

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get vertices of label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get vertex properties"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex id '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get schema"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<vertex_id>'"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_vertices": "<num_vertices_returned>"
                      },
                      "data": {
                        "vertices": [
                          {
                            "id": "<vertex_id_1>",
                            "label": "<vertex_label_1>",
                            "properties": [
                              {
                                "<prop_name_1>": "<prop_value_1>"
                              },
                              {
                                "<prop_name_2>": "<prop_value_2>"
                              },
                              "..."
                            ]
                          },
                          "..."
                        ]
                      }
                    }

        Examples
        --------
        .. code-block:: python

            g.get_vertex(vertex_id="1")
            g.get_vertex(vertex_label="v1", vertex_id="1")
            g.get_vertex(vertex_label=["v2"])
            g.get_vertex(vertex_label=["v1", "v2"], prop=["p1"])
            g.get_vertex(vertex_label=["v1", "v2"], prop="id_only")
            g.get_vertex(vertex_label="v1", vertex_id="1", prop="id_only")
            g.get_vertex(vertex_label=["v1", "v2"], prop="id_only", max_num_vertices=4)

        """
        url = self.root_url + "/graphs/" + self.graph_name + "/vertices/"
        if isinstance(vertex_label, basestring):
            url += vertex_label + '/' + vertex_id
        # Get all vertices given one or more labels
        elif isinstance(vertex_label, list):
            if vertex_label:
                url = _url_assemble(url, vertex_label)
            else:
                if vertex_id == '':
                    return "No parameters are set!"
                else:
                    url += "*/" + vertex_id
        if isinstance(prop, list):
            if prop:
                url += '?prop='
                url = _url_assemble(url, prop)
        elif isinstance(prop, basestring):
            if prop == 'id_only':
                url += "?prop=id_only"
        if prop:
            if max_num_vertices != float("inf"):
                url += "&max_num_vertices={}".format(max_num_vertices)
        else:
            if max_num_vertices != float("inf"):
                url += "?max_num_vertices={}".format(max_num_vertices)
        # logging.debug(url)
        return _query(url)

    def get_edge(self, source_id, source_label, target_id, target_label, edge_label=[], edge_id='', prop=[],
                 max_num_edges=float("inf")):
        """
        Get a specific edge between two vertices, or get all edges between two vertices, or get all edges of one or more specific labels between two vertices(only output the specified properties if prop is present; only output id and label if prop=id_only).

        Parameters
        ----------
        source_id
            str
                source vertex id
        source_label
            str
                source vertex label
        target_id
            str
                target vertex id
        target_label
            str
                target vertex label
        edge_label
            str | list
                optional, edge label for a specific edge | list of edge labels
        edge_id
            str
                optional, internal id to specify an edge
        prop
            list | "id_only"
                optional, properties to be returned, "id_only" is a reserved keyword for no property return
        max_num_edges
            int
                optional, limited the returning number of edges, should > 0



        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid source label '<source_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid source id '<source_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid target label '<target_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid target id '<target_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<source_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<source_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<target_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<target_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edge between given source and target of label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edge properties"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge '<eid>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edge '<eid>'"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_vertices": 2,
                        "num_edges": "<number_of_edges_returned>"
                      },
                      "data": {
                        "vertices": [
                          {
                            "id": "<source_id>",
                            "label": "<source_label>"
                          },
                          {
                            "id": "<target_id>",
                            "label": "<target_label>"
                          }
                        ],
                        "edges": [
                          {
                            "source_id": "<source_id>",
                            "source_label": "<source_label>",
                            "target_id": "<target_id>",
                            "target_label": "<target_label>",
                            "eid": "<eid>",
                            "label": "<edge_label>",
                            "properties": [
                              {
                                "<prop_name_1>": "<prop_value_1>"
                              },
                              {
                                "<prop_name_2>": "<prop_value_2>"
                              },
                              "..."
                            ]
                          },
                          "..."
                        ]
                      }
                    }

        Examples
        --------
        .. code-block:: python

            g.get_edge(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_id="13835058055282163712", edge_label="e1")
            g.get_edge(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_label="e1")
            g.get_edge(source_id="1", source_label="v1", target_id="2", target_label="v1")
            g.get_edge(source_id="1", source_label="v1", target_id="2", target_label="v1", prop="id_only")
            g.get_edge(source_id="1", source_label="v1", target_id="2", target_label="v1", prop=["p2"], )
            g.get_edge(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_label=["e2"], prop=["p2"], )
            g.get_edge(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_label=["e1"], prop=["p2"], )
            g.get_edge(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_label=["e1"], prop=["p2"], max_num_edges=4)
            g.get_edge(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_label=["e1"], max_num_edges=1)




        """
        url = self.root_url + '/graphs/' + self.graph_name + '/edges/' + source_label + '/' + source_id + '/' + target_label + '/' + target_id + '/'
        if isinstance(edge_label, basestring):
            if edge_id is '':
                url += edge_label
            else:
                url += edge_label + '/' + edge_id
        elif isinstance(edge_label, list):
            if edge_label:
                logging.debug("print the edge_label {}".format(edge_label))
                url = _url_assemble(url, edge_label)
                if edge_id is not '':
                    return "Input of edge_id({}) is not '' for a list of edge_label!".format(edge_id)
            else:
                url = self.root_url + '/graphs/' + self.graph_name + '/edges/' + source_label + '/' + source_id + '/' + target_label + '/' + target_id
                if edge_id is not '':
                    return "Input of edge_id({}) is not '' for a list of edge_label!".format(edge_id)
        if isinstance(prop, list):
            if prop:
                url += '?prop='
                url = _url_assemble(url, prop)
        elif isinstance(prop, basestring):
            if prop == 'id_only':
                url += "?prop=id_only"
        if prop:
            if max_num_edges != float("inf"):
                url += "&max_num_edges={}".format(max_num_edges)
        else:
            if max_num_edges != float("inf"):
                url += "?max_num_edges={}".format(max_num_edges)
        return _query(url)

    ## need to check
    def get_edge_count(self, source_id, source_label, target_id, target_label, edge_label=[]):
        """
        Get number of edges of one or more specific labels between two vertices.

        Parameters
        ----------
        source_id
            str
                source vertex id
        source_label
            str
                source vertex label
        target_id
            str
                target vertex id
        target_label
            str
                target vertex label
        edge_label
            list
                optional, list of edge labels

        Returns
        -------
        str
            .. code-block:: json

                {
                  "status": "success",
                  "statistics": {
                    "num_edges": "<number_of_edges>"
                  }
                }

        Examples
        --------
        .. code-block:: python

            g.get_edge_count(source_id="1", source_label="v1", target_id="2", target_label="v1")
            g.get_edge_count(source_id="1", source_label="v1", target_id="2", target_label="v1", edge_label=["e1", "e2"])

        """
        url = self.root_url + '/graphs/' + self.graph_name + '/edges/' + source_label + '/' + source_id + '/' + target_label + '/' + target_id
        if edge_label:
            url += "/"
            url = _url_assemble(url, edge_label)
        url += "/count"
        logging.debug(url)
        return _query(url)

    def get_edge_out(self, vertex_label, vertex_id, edge_label=[], prop=[], max_num_edges=float("inf")):
        """
        Get a vertex's outgoing edges (with optional edge label constraint).

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        edge_label
            list
                optional, list of edge labels
        prop
            list | "id_only"
                optional, properties to be returned, "id_only" is a reserved keyword for no property return
        max_num_edges
            int
                optional, limited the returning number of edges, should > 0

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex id '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get schema"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edges"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edge properties"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_edges": "<number_of_edges_returned>"
                      },
                      "data": {
                        "edges": [
                          {
                            "source_id": "<source_id_1>",
                            "source_label": "<source_label_1>",
                            "target_id": "<target_id_1>",
                            "target_label": "<target_label_1>",
                            "eid": "<eid>",
                            "label": "<edge_label>",
                            "properties": [
                              {
                                "<prop_name_1>": "<prop_value_1>"
                              },
                              {
                                "<prop_name_2>": "<prop_value_2>"
                              },
                              "..."
                            ]
                          },
                          "..."
                        ]
                      }
                    }

        Examples
        --------
        .. code-block:: python

            g.get_edge_out(vertex_id="1", vertex_label="v1")
            g.get_edge_out(vertex_id="1", vertex_label="v1", edge_label=["e1"], prop=["p2"])
            g.get_edge_out(vertex_id="1", vertex_label="v1", edge_label=["e2"])
            g.get_edge_out(vertex_id="1", vertex_label="v1", prop=["p2"])
            g.get_edge_out(vertex_id="1", vertex_label="v1", prop="id_only")

        """
        # Get a vertex's outgoing edges
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id + '/outE'
        # Get a vertex's outgoing edges of one or more specific edge labels
        if edge_label or prop:
            url += '?'
            if edge_label:
                url += 'edge_label='
                url = _url_assemble(url, edge_label)
                if prop:
                    url += '&'
            if prop:
                if isinstance(prop, list):
                    if prop:
                        url += 'prop='
                        url = _url_assemble(url, prop)
                elif isinstance(prop, basestring):
                    if prop == 'id_only':
                        url += "prop=id_only"
        # logging.debug(url)
        if prop:
            if max_num_edges != float("inf"):
                url += "&max_num_edges={}".format(max_num_edges)
        else:
            if max_num_edges != float("inf"):
                url += "?max_num_edges={}".format(max_num_edges)
        return _query(url)

    def get_edge_out_count(self, vertex_label, vertex_id, edge_label=[]):
        """
        Get a vertex's number of outgoing edges (with optional edge label constraint).

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        edge_label
            list
                optional, list of edge labels

        Returns
        -------
        str
            .. code-block:: json

                {
                  "status": "success",
                  "statistics": {
                    "num_edges": "<number_of_edges>"
                  }
                }


        Examples
        --------
        .. code-block:: python

            g.get_neighbor_out(vertex_id="1", vertex_label="v1")
            g.get_neighbor_out(vertex_id="1", vertex_label="v1", edge_label=["e1"], prop=["p2"])
            g.get_neighbor_out(vertex_id="1", vertex_label="v1", edge_label=["e2"])
            g.get_neighbor_out(vertex_id="1", vertex_label="v1", neighbor_label=["v1","v2"], prop=["p1"])
            g.get_neighbor_out(vertex_id="1", vertex_label="v1", prop=["p1"])
            g.get_neighbor_out(vertex_id="1", vertex_label="v1", prop="id_only")

        """
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id + '/outE/count'
        # Get a vertex's outgoing edges of one or more specific edge labels
        if edge_label:
            url += '?edge_label='
            url = _url_assemble(url, edge_label)
        return _query(url)

    def get_edge_in(self, vertex_label, vertex_id, edge_label=[], prop=[], max_num_edges=float("inf")):
        """
        Get a vertex's incoming edges (with optional edge label constraint).

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        edge_label
            list
                optional, list of edge labels
        prop
            list | "id_only"
                optional, properties to be returned, "id_only" is a reserved keyword for no property return
        max_num_edges
            int
                optional, limited the returning number of edges, should > 0

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex id '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get schema"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edges"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edge properties"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_edges": "<number_of_edges_returned>"
                      },
                      "data": {
                        "edges": [
                          {
                            "source_id": "<source_id_1>",
                            "source_label": "<source_label_1>",
                            "target_id": "<target_id_1>",
                            "target_label": "<target_label_1>",
                            "eid": "<eid>",
                            "label": "<edge_label>",
                            "properties": [
                              {
                                "<prop_name_1>": "<prop_value_1>"
                              },
                              {
                                "<prop_name_2>": "<prop_value_2>"
                              },
                              "..."
                            ]
                          },
                          "..."
                        ]
                      }
                    }

        Examples
        --------
        .. code-block:: python

            g.get_edge_in(vertex_id="1", vertex_label="v1")
            g.get_edge_in(vertex_id="1", vertex_label="v1", edge_label=["e1"], prop=["p2"])
            g.get_edge_in(vertex_id="1", vertex_label="v1", edge_label=["e2"])
            g.get_edge_in(vertex_id="1", vertex_label="v1", neighbor_label=["v1","v2"], prop=["p1"])
            g.get_edge_in(vertex_id="1", vertex_label="v1", prop=["p1"])
            g.get_edge_in(vertex_id="1", vertex_label="v1", prop="id_only")

        """
        if vertex_id is '' or vertex_label is '':
            return "null_string_error"
        # Get a vertex's incoming edges
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id + '/inE'
        # Get a vertex's incoming edges of one or more specific edge labels
        if edge_label or prop:
            url += '?'
            if edge_label:
                url += 'edge_label='
                url = _url_assemble(url, edge_label)
                if prop:
                    url += '&'
            if prop:
                if isinstance(prop, list):
                    if prop:
                        url += 'prop='
                        url = _url_assemble(url, prop)
                elif isinstance(prop, basestring):
                    if prop == 'id_only':
                        url += "prop=id_only"
        # logging.debug(url)
        if prop:
            if max_num_edges != float("inf"):
                url += "&max_num_edges={}".format(max_num_edges)
        else:
            if max_num_edges != float("inf"):
                url += "?max_num_edges={}".format(max_num_edges)
        return _query(url)

    def get_edge_in_count(self, vertex_label, vertex_id, edge_label=[]):
        """
        Get a vertex's number of incoming edges (with optional edge label constraint).

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        edge_label
            list
                optional, list of edge labels

        Returns
        -------
        str
            .. code-block:: json

                {
                  "status": "success",
                  "statistics": {
                    "num_edges": "<number_of_edges>"
                  }
                }


        Examples
        --------
        .. code-block:: python

            g.get_neighbor_in_count(vertex_id="1", vertex_label="v1")
            g.get_neighbor_in_count(vertex_id="1", vertex_label="v1", edge_label=["e1"])
            g.get_neighbor_in_count(vertex_id="1", vertex_label="v1", edge_label=["e2"])
            g.get_neighbor_in_count(vertex_id="1", vertex_label="v1", neighbor_label=["v1","v2"])
            g.get_neighbor_in_count(vertex_id="1", vertex_label="v1", neighbor_label=["v2"])

        """
        # Get a vertex's incoming edges
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id + '/inE/count'
        # Get a vertex's incoming edges of one or more specific edge labels
        if edge_label:
            url += '?edge_label='
            url = _url_assemble(url, edge_label)
        return _query(url)

    def get_edge_all(self, vertex_label, vertex_id, edge_label=[], prop=[], max_num_edges=float("inf")):
        """
        Get a vertex's all edges (with optional edge label constraint).

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        edge_label
            list
                optional, list of edge labels
        prop
            list | "id_only"
                optional, properties to be returned, "id_only" is a reserved keyword for no property return
        max_num_edges
            int
                optional, limited the returning number of edges, should > 0

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex id '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get schema"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edges"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edge properties"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_edges": "<number_of_edges_returned>"
                      },
                      "data": {
                        "edges": [
                          {
                            "source_id": "<source_id_1>",
                            "source_label": "<source_label_1>",
                            "target_id": "<target_id_1>",
                            "target_label": "<target_label_1>",
                            "eid": "<eid>",
                            "label": "<edge_label>",
                            "properties": [
                              {
                                "<prop_name_1>": "<prop_value_1>"
                              },
                              {
                                "<prop_name_2>": "<prop_value_2>"
                              },
                              "..."
                            ]
                          },
                          "..."
                        ]
                      }
                    }

        Examples
        --------
        .. code-block:: python

                g.get_edge_all(vertex_id="1", vertex_label="v1")
                g.get_edge_all(vertex_id="1", vertex_label="v1", edge_label=["e1"], prop=["p2"])
                g.get_edge_all(vertex_id="1", vertex_label="v1", edge_label=["e2"])
                g.get_edge_all(vertex_id="1", vertex_label="v1", edge_label=["e1","e2"], prop=["p1"])
                g.get_edge_all(vertex_id="1", vertex_label="v1", prop=["p1"])
                g.get_edge_all(vertex_id="1", vertex_label="v1", prop="id_only")

        """
        if vertex_id is '' or vertex_label is '':
            return "null_string_error"
        # Get a vertex's incoming edges
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id + '/allE'
        # Get a vertex's incoming edges of one or more specific edge labels
        if edge_label or prop:
            url += '?'
            if edge_label:
                url += 'edge_label='
                url = _url_assemble(url, edge_label)
                if prop:
                    url += '&'
            if prop:
                if isinstance(prop, list):
                    if prop:
                        url += 'prop='
                        url = _url_assemble(url, prop)
                elif isinstance(prop, basestring):
                    if prop == 'id_only':
                        url += "prop=id_only"
        # logging.debug(url)
        if prop:
            if max_num_edges != float("inf"):
                url += "&max_num_edges={}".format(max_num_edges)
        else:
            if max_num_edges != float("inf"):
                url += "?max_num_edges={}".format(max_num_edges)
        return _query(url)

    def get_edge_all_count(self, vertex_label, vertex_id, edge_label=[]):
        """
        Get a vertex's total number of edges (with optional edge label constraint).

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        edge_label
            list
                optional, list of edge labels

        Returns
        -------
        str
            .. code-block:: json

                {
                  "status": "success",
                  "statistics": {
                    "num_edges": "<number_of_edges>"
                  }
                }


        Examples
        --------
        .. code-block:: python

            g.get_edge_all_count(vertex_id="1", vertex_label="v1")
            g.get_edge_all_count(vertex_id="1", vertex_label="v1", edge_label=["e1"])
            g.get_edge_all_count(vertex_id="1", vertex_label="v1", edge_label=["e2"])
            g.get_edge_all_count(vertex_id="1", vertex_label="v1", edge_label=["e1","e2"])
            g.get_edge_all_count(vertex_id="1", vertex_label="v1", edge_label=["e2"])

        """
        # Get a vertex's incoming edges
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id + '/allE/count'
        # Get a vertex's incoming edges of one or more specific edge labels
        if edge_label:
            url += '?edge_label='
            url = _url_assemble(url, edge_label)
        return _query(url)

    def get_neighbor_out(self, vertex_label, vertex_id, edge_label=[], neighbor_label=[], prop=[],
                         max_num_vertices=float("inf")):
        """
        Get a vertex's outgoing neighbors (with optional vertex and edge label constraints).

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        edge_label
            list
                optional, list of edge labels
        neighbor_label
            list
                optional, list of neighbor vertex labels
        prop
            list | "id_only"
                optional, properties to be returned, "id_only" is a reserved keyword for no property return
        max_num_vertices
            int
                optional, limited the returning number of edges, should > 0

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex id '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get schema"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<neighbor_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edges"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get neighbor vertex id"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get vertex properties"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_vertices": "<number_of_vertices_returned>"
                      },
                      "data": {
                        "vertices": [
                          {
                            "id": "<vertex_id_1>",
                            "label": "<vertex_label_1>",
                            "properties": [
                              {
                                "<prop_name_1>": "<prop_value_1>"
                              },
                              {
                                "<prop_name_2>": "<prop_value_2>"
                              },
                              "..."
                            ]
                          },
                          "..."
                        ]
                      }
                    }


        Examples
        --------
        .. code-block:: python

            g.get_neighbor_out(vertex_id="1", vertex_label="v1")
            g.get_neighbor_out(vertex_id="1", vertex_label="v1", edge_label=["e1"], prop=["p2"])
            g.get_neighbor_out(vertex_id="1", vertex_label="v1", edge_label=["e2"])
            g.get_neighbor_out(vertex_id="1", vertex_label="v1", neighbor_label=["v1","v2"], prop=["p1"])
            g.get_neighbor_out(vertex_id="1", vertex_label="v1", prop=["p1"])
            g.get_neighbor_out(vertex_id="1", vertex_label="v1", prop="id_only")

        """
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id + '/outV'
        url = _get_neighbor_inOut_url(url, neighbor_label, edge_label, prop, max_num_vertices)
        return _query(url)

    def get_neighbor_out_count(self, vertex_label, vertex_id, edge_label=[], neighbor_label=[]):
        """
        Get a vertex's number of outgoing neighbors (with optional vertex and edge label constraints).

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        edge_label
            list
                optional, list of edge labels
        neighbor_label
            list
                optional, list of neighbor vertex labels

        Returns
        -------
        str
            .. code-block:: json

                {
                  "status": "success",
                  "statistics": {
                    "num_vertices": "<number_of_vertices>"
                  }
                }

        Examples
        --------
        .. code-block:: python

            g.get_neighbor_out_count(vertex_id="1", vertex_label="v1")
            g.get_neighbor_out_count(vertex_id="1", vertex_label="v1", edge_label=["e1"])
            g.get_neighbor_out_count(vertex_id="1", vertex_label="v1", edge_label=["e2"])
            g.get_neighbor_out_count(vertex_id="1", vertex_label="v1", neighbor_label=["v1","v2"])
            g.get_neighbor_out_count(vertex_id="1", vertex_label="v1", neighbor_label=["v2"])


        """
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id + '/outV/count'
        url = _get_neighbor_inOut_url(url, neighbor_label, edge_label, [])
        return _query(url)

    def get_neighbor_in(self, vertex_label, vertex_id, edge_label=[], neighbor_label=[], prop=[],
                        max_num_vertices=float("inf")):
        """
        Get a vertex's incoming neighbors (with optional vertex and edge label constraints).

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        edge_label
            list
                optional, list of edge labels
        neighbor_label
            list
                optional, list of neighbor vertex labels
        prop
            list | "id_only"
                optional, properties to be returned, "id_only" is a reserved keyword for no property return
        max_num_vertices
            int
                optional, limited the returning number of edges, should > 0

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex id '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get schema"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<neighbor_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edges"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get neighbor vertex id"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get vertex properties"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_vertices": "<number_of_vertices_returned>"
                      },
                      "data": {
                        "vertices": [
                          {
                            "id": "<vertex_id_1>",
                            "label": "<vertex_label_1>",
                            "properties": [
                              {
                                "<prop_name_1>": "<prop_value_1>"
                              },
                              {
                                "<prop_name_2>": "<prop_value_2>"
                              },
                              "..."
                            ]
                          },
                          "..."
                        ]
                      }
                    }


        Examples
        --------
        .. code-block:: python

            g.get_neighbor_in(vertex_id="1", vertex_label="v1")
            g.get_neighbor_in(vertex_id="1", vertex_label="v1", edge_label=["e1"], prop=["p2"])
            g.get_neighbor_in(vertex_id="1", vertex_label="v1", edge_label=["e2"])
            g.get_neighbor_in(vertex_id="1", vertex_label="v1", neighbor_label=["v1","v2"], prop=["p1"])
            g.get_neighbor_in(vertex_id="1", vertex_label="v1", prop=["p1"])
            g.get_neighbor_in(vertex_id="1", vertex_label="v1", prop="id_only")

        """
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id + '/inV'
        url = _get_neighbor_inOut_url(url, neighbor_label, edge_label, prop, max_num_vertices)
        return _query(url)

    def get_neighbor_in_count(self, vertex_label, vertex_id, edge_label=[], neighbor_label=[]):
        """
        Get a vertex's number of incoming neighbors (with optional vertex and edge label constraints).

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        edge_label
            list
                optional, list of edge labels
        neighbor_label
            list
                optional, list of neighbor vertex labels

        Returns
        -------
        str
            .. code-block:: json

                {
                  "status": "success",
                  "statistics": {
                    "num_vertices": "<number_of_vertices>"
                  }
                }

        Examples
        --------
        .. code-block:: python

            g.get_neighbor_in_count(vertex_id="1", vertex_label="v1")
            g.get_neighbor_in_count(vertex_id="1", vertex_label="v1", edge_label=["e1"])
            g.get_neighbor_in_count(vertex_id="1", vertex_label="v1", edge_label=["e2"])
            g.get_neighbor_in_count(vertex_id="1", vertex_label="v1", neighbor_label=["v1","v2"])
            g.get_neighbor_in_count(vertex_id="1", vertex_label="v1", neighbor_label=["v2"])

        """
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id + '/inV/count'
        url = _get_neighbor_inOut_url(url, neighbor_label, edge_label, [])
        return _query(url)

    def get_neighbor_all(self, vertex_label, vertex_id, edge_label=[], neighbor_label=[], prop=[],
                         max_num_vertices=float("inf")):
        """
        Get a vertex's all neighbors of specific vertex label/s along edges of specific edge label/s.

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        edge_label
            list
                optional, list of edge labels
        neighbor_label
            list
                optional, list of neighbor vertex labels
        prop
            list | "id_only"
                optional, properties to be returned, "id_only" is a reserved keyword for no property return
        max_num_vertices
            int
                optional, limited the returning number of edges, should > 0

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to open graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "invalid vertex id '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<vertex_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex '<vertex_id>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get schema"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<neighbor_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge label '<edge_label>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edges"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get neighbor vertex id"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get vertex properties"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_vertices": "<number_of_vertices_returned>"
                      },
                      "data": {
                        "vertices": [
                          {
                            "id": "<vertex_id_1>",
                            "label": "<vertex_label_1>",
                            "properties": [
                              {
                                "<prop_name_1>": "<prop_value_1>"
                              },
                              {
                                "<prop_name_2>": "<prop_value_2>"
                              },
                              "..."
                            ]
                          },
                          "..."
                        ]
                      }
                    }


        Examples
        --------
        .. code-block:: python

            g.get_neighbor_all(vertex_id="1", vertex_label="v1")
            g.get_neighbor_all(vertex_id="1", vertex_label="v1", edge_label=["e1"], prop=["p2"])
            g.get_neighbor_all(vertex_id="1", vertex_label="v1", edge_label=["e2"])
            g.get_neighbor_all(vertex_id="1", vertex_label="v1", neighbor_label=["v1","v2"], prop=["p1"])
            g.get_neighbor_all(vertex_id="1", vertex_label="v1", prop=["p1"])
            g.get_neighbor_all(vertex_id="1", vertex_label="v1", prop="id_only")

        """
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id + '/allV'
        url = _get_neighbor_inOut_url(url, neighbor_label, edge_label, prop, max_num_vertices)
        return _query(url)

    def get_neighbor_all_count(self, vertex_label, vertex_id, edge_label=[], neighbor_label=[]):
        """
        Get a vertex's number of all neighbors (with optional vertex and edge label constraints).

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        edge_label
            list
                optional, list of edge labels
        neighbor_label
            list
                optional, list of neighbor vertex labels

        Returns
        -------
        str
            .. code-block:: json

                {
                  "status": "success",
                  "statistics": {
                    "num_vertices": "<number_of_vertices>"
                  }
                }

        Examples
        --------
        .. code-block:: python

            g.get_neighbor_all_count(vertex_id="1", vertex_label="v1")
            g.get_neighbor_all_count(vertex_id="1", vertex_label="v1", edge_label=["e1"])
            g.get_neighbor_all_count(vertex_id="1", vertex_label="v1", edge_label=["e2"])
            g.get_neighbor_all_count(vertex_id="1", vertex_label="v1", neighbor_label=["v1","v2"])
            g.get_neighbor_all_count(vertex_id="1", vertex_label="v1", neighbor_label=["v2"])

        """
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/' + vertex_label + '/' + vertex_id + '/allV/count'
        url = _get_neighbor_inOut_url(url, neighbor_label, edge_label, [])
        return _query(url)

    # # Search Graph
    # # Find vertices that satisfy given search criteria
    def search_vertex(self, query):
        """

        Parameters
        ----------
        query
            str | dict
                <query_string_in_elasticsearch_syntax> or properties dict
                // please refer to Elasticsearch query documentation online

        Returns
        -------
        str
            .. code-block:: json

                INDEX_ERROR
                {"status":"failure", "message":"index error"}
                INDEX_OK:
                {"status":"success", "message":"no match found"}
                or
                {
                    "status":"success",
                    "statistics":
                    {
                        "num_vertices":<number_of_vertices_returned>,
                    },
                    "data":
                    {
                        "vertices":
                        [
                            {
                                "id":"<vertex_id_1>",
                                "label":"<vertex_label_1>",
                                "properties":
                                [
                                    {"<prop_name_1>":<prop_value_1>},
                                    {"<prop_name_2>":<prop_value_2>},
                                    ...
                                ]
                            },
                            ...
                        ]
                    }
                }


        """
        config_param = {}
        url = self.root_url + '/graphs/' + self.graph_name + '/vertices/search'
        if isinstance(query, basestring):
            config_param["param"] = query
            return _post_query(url, config_param)
        if type(query) is dict:
            url += '?'
            url = _url_dict_assemble(url, query)
            return _query(url)

    def search_edge(self, query):
        """

        Parameters
        ----------
        query
            str | dict
                <query_string_in_elasticsearch_syntax> or properties dict
                // please refer to Elasticsearch query documentation online

        Returns
        -------
        str
            .. code-block:: json

                INDEX_ERROR
                {"status":"failure", "message":"index error"}
                INDEX_OK:
                {"status":"success", "message":"no match found"}
                or
                {
                    "status":"success",
                    "statistics":
                    {
                        "num_vertices":<number_of_vertices_returned>,
                    },
                    "data":
                    {
                        "vertices":
                        [
                            {
                                "id":"<vertex_id_1>",
                                "label":"<vertex_label_1>",
                                "properties":
                                [
                                    {"<prop_name_1>":<prop_value_1>},
                                    {"<prop_name_2>":<prop_value_2>},
                                    ...
                                ]
                            },
                            ...
                        ]
                    }
                }

        Notes
        -----
            When the Elasticsearch index is not available, vertex and edge filters can be used to constrain which vertices or edges are reachable during graph traversal (bfs and egonet) based on the values of certain properties. Multiple filters are ANDed together. Each filter requires a property name, a property value, and a predicate to be specified. The following predicates are supported: LESS LESS_EQUAL GREATER GREATER_EQUAL EQUAL_TO NOT_EQUAL_TO CONTAINS (for partial string matching) IN (for matching any of the values in a list)
            When time-based properties are added to vertices and edges, vertex and edge filters can be applied to support search based on time constraints. To search vertices or edges without an end time, the property name must be “end_time”, the predicate must be “EQUAL_TO”, and the property value must be “NULL”.
            For timestamped property values, an additional key “between” (whose value is a list containing a starting time and an ending time) can be added to a filter to limit property value matching only to the values whose timestamps are within the specified time range. As long as at least one timestamped value matches the constraint set by the predicate, the filter returns true.


        """
        config_param = {}
        url = self.root_url + '/graphs/' + self.graph_name + '/edges/search'
        if isinstance(query, basestring):
            config_param["param"] = query
            return _post_query(url, config_param)
        if isinstance(query, dict):
            url += '?'
            url = _url_dict_assemble(url, query)
            return _query(url)

    #
    ######## Graph Analysis ##########
    #
    #
    # Get total number of vertices
    def get_num_vertex(self, graph_name, vertex_label=[]):
        """
        Get total number of vertices (with optional label constraint).

        Parameters
        ----------
        graph_name
            str
                a graph name
        vertex_label
            list
                optional, list of vertex labels

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get vertex label '<vertex_lable>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find vertex label '<vertex_label>'"
                    }


            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_vertices": "<number_of_vertices>"
                      }
                    }


        Examples
        --------
        .. code-block:: python

            rc = g.get_num_vertex(graph_name="test", vertex_label=["v1", "v2"])
            rc = g.get_num_vertex(graph_name="test", vertex_label=["v1"])
            rc = g.get_num_vertex(graph_name="test", vertex_label=["v3", "v1"])


        """
        url = self.root_url + '/graphs/' + graph_name + '/vertices/count'
        if vertex_label:
            url += '?label='
            url = _url_assemble(url, vertex_label)
        return _query(url)

    # Get total number of edges
    def get_num_edge(self, graph_name, edge_label=[]):
        """
        Get total number of edges (with optional label constraint)

        Parameters
        ----------
        graph_name
            str
                a graph name
        edge_label
            list
                optional, list of edge labels

        Returns
        -------
        str
            DB_ERROR

                .. code-block:: json

                    {
                      "status": "failure",
                      "message": "invalid graph name '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find graph '<graph_name>'"
                    }
                    {
                      "status": "failure",
                      "message": "fail to get edge label '<edge_lable>'"
                    }
                    {
                      "status": "failure",
                      "message": "cannot find edge label '<edge_label>'"
                    }

            DB_OK

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_edges": "<number_of_edges>"
                      }
                    }

        Examples
        --------
        .. code-block:: python

            rc = g.get_num_edge(graph_name="test", edge_label=["e1", "e2"])
            rc = g.get_num_edge(graph_name="test", edge_label=["e1"])
            rc = g.get_num_edge(graph_name="test", edge_label=["e1", "e3"])

        """
        url = self.root_url + '/graphs/' + graph_name + '/edges/count'
        if edge_label:
            url += '?label='
            url = _url_assemble(url, edge_label)
        return _query(url)

    ######### Graph Analytics ####################

    def run_analytics(self, analytic_name, request_body, request_type=""):
        """
        This set of analytics are for calculating graph analytics.

        - There are three types of output produced by various graph analytics:

            - **Subgraph** containing a list of vertices and a list of edges: output by BFS (breath-first search), egonet, subgraph, and shortest path analytics.
            - **Components** containing a list of components, each of which is subgraph: output by weakly/strongly connected components and cycle analytics.
            - **Metrics** containing a list of vertices with metric values as vertex properties: output by centrality, degree, and pagerank analytics.

        - Components can be saved to a component store, and metrics can be saved to a metric store. A store only contains internal identifiers of the relevant vertices/edges, so it is dependent on the underlying graph from which results are created. As a result, the graph based on which the store is created must be specified in order to retrieve results from the store.



        Parameters
        ----------
        analytic_name
            str
                bfs | egonet | subgraph | path | connected/strong | connected/weak | cycle | cycle/connected/composite | community/louvain | metrics | metrics/subgraph | pagerank
        request_body
            dict
                defined by the keys and json strings for each analytic name as below)
        request_type
            str
                optional, default is "", "async" | "async_kafka"

            *bfs*: Traverse via breath-first search from one or multiple vertices with constraints - Analytics that produce subgraph. The "request_body "is a json object  as below:

                .. code-block:: javascript

                    {
                    "param":
                    json_string_of(
                    {
                        "vertices": // mandatory
                        [
                            {"id":"<vertex_id_1>", "label":"<vertex_label_1>"},
                            {"id":"<vertex_id_2>", "label":"<vertex_label_2>"},
                            ...
                        ],
                        "depth":<depth>, // default is no limit if unspecified
                        "edge_labels":[<edge_label_1>", "<edge_label_2>", ...], // optional
                    "edge_direction":"in"|"out"|"all", // default is "all"
                        "vertex_filters": // optional, invalid filter is ignored
                        [
                           {
                              "prop_name":"<vertex_prop_name_1>",
                              "prop_value":"<vertex_prop_value_1>", // always specified as a string
                              "predicate":"LESS"|"LESS_EQUAL"|"GREATER"|"GREATER_EQUAL"|
                                                "EQUAL_TO"|"NOT_EQUAL_TO"|"CONTAINS"|"IN",
                              "between":["<start_time>", "<end_time>"] // only for timestamped property value types
                           },
                           ...
                        ],
                        "edge_filters": //optional, invalid filter is ignored
                        [
                           {
                              "prop_name":"<edge_prop_name_1>",
                              "prop_value":"<edge_prop_value_1>", // always specified as a string
                              "predicate":"LESS"|"LESS_EQUAL"|"GREATER"|"GREATER_EQUAL"|
                                                "EQUAL_TO"|"NOT_EQUAL_TO"|"CONTAINS"|"IN",
                              "between":["<start_time>", "<end_time>"] // only for timestamped property value types
                           },
                           ...
                        ],
                        "with_vertex_props":"true"|"false", // whether to output vertex properties, default is "false"
                        "with_edge_props":"true"|"false", // whether to output edge properties, default is "false"
                        "exclude_vertices":"true"|"false", // whether to exclude vertices from output, default is "false"
                        "exclude_edges":"true"|"false", // whether to exclude edges from output, default is "false"
                        "result_type":"DB_JSON"|"DB_JSON_FILE"|"DB_SUBGRAPH", // default is "DB_JSON"
                        "result_name":"<json_file_name_or_subgraph_name>",
                        "max_time":<max_run_time_in_seconds>
                    }
                    ),
                    "async":"{\"expiration\":<num_seconds>, \"job_id\":\"<string_job_id>\"}" // for async and async_kafka
                    }


            *egonet*: Get the aggregate egonet of multiple vertices (ignore edge direction) - Analytics that produce subgraph. The "request_body "is a json object  as below:

                .. code-block:: javascript

                    {
                    "param":
                    json_string_of(
                    {
                        "vertices": // mandatory
                        [
                            {"id":"<vertex_id_1>", "label":"<vertex_label_1>"},
                            {"id":"<vertex_id_2>", "label":"<vertex_label_2>"},
                            ...
                        ],
                        "depth":<depth>, // default is no limit if unspecified
                    "edge_labels":["<edge_label_1>", "<edge_label_2>", ...], // optional
                        "vertex_filters": // optional, invalid filter is ignored
                        [
                           {
                              "prop_name":"<vertex_prop_name_1>",
                              "prop_value":"<vertex_prop_value_1>", // always specified as a string
                              "predicate":"LESS"|"LESS_EQUAL"|"GREATER"|"GREATER_EQUAL"|
                                                "EQUAL_TO"|"NOT_EQUAL_TO"|"CONTAINS"|"IN",
                              "between":["<start_time>", "<end_time>"] // only for timestamped property value types
                           },
                           ...
                        ],
                        "edge_filters": //optional, invalid filter is ignored
                        [
                           {
                              "prop_name":"<edge_prop_name_1>",
                              "prop_value":"<edge_prop_value_1>", // always specified as a string
                              "predicate":"LESS"|"LESS_EQUAL"|"GREATER"|"GREATER_EQUAL"|
                                                "EQUAL_TO"|"NOT_EQUAL_TO"|"CONTAINS"|"IN",
                              "between":["<start_time>", "<end_time>"] // only for timestamped property value types
                           },
                           ...
                        ],
                        "with_vertex_props":"true"|"false", // whether to output vertex properties, default is "false"
                        "with_edge_props":"true"|"false", // whether to output edge properties, default is "false"
                        "exclude_vertices":"true"|"false", // whether to exclude vertices from output, default is "false"
                        "exclude_edges":"true"|"false", // whether to exclude edges from output, default is "false"
                        "result_type":"DB_JSON"|"DB_JSON_FILE"|"DB_SUBGRAPH", // default is "DB_JSON"
                        "result_name":"<json_file_name_or_subgraph_name>",
                        "max_time":<max_run_time_in_seconds>
                    }
                    ),
                    "async":"{\"expiration\":<num_seconds>, \"job_id\":\"<string_job_id>\"}" // for async and async_kafka
                    }


            *subgraph*: Get the subgraph of multiple vertices (with optional edge label constraint) - Analytics that produce subgraph. The "request_body "is a json object  as below:

                .. code-block:: javascript

                    {
                    "param":
                    json_string_of(
                    {
                        "vertices":[ //mandatory
                            {"id":"<vertex_id_1>", "label":"<vertex_label_1>"},
                            {"id":"<vertex_id_2>", "label":"<vertex_label_2>"},
                            ...
                        ],
                    "edge_labels":["<edge_label_1>", "<edge_label_2>", ...], // optional
                        "with_vertex_props":"true"|"false", // whether to output vertex properties, default is "false"
                        "with_edge_props":"true"|"false", // whether to output edge properties, default is "false"
                        "exclude_vertices":"true"|"false", // whether to exclude vertices from output, default is "false"
                        "exclude_edges":"true"|"false", // whether to exclude edges from output, default is "false"
                        "result_type":"DB_JSON"|"DB_JSON_FILE"|"DB_SUBGRAPH", // default is "DB_JSON"
                        "result_name":"<json_file_name_or_subgraph_name>",
                        "max_time":<max_run_time_in_seconds>
                    }
                    ),
                    "async":"{\"expiration\":<num_seconds>, \"job_id\":\"<string_job_id>\"}" // for async and async_kafka
                    }


            *path*: Get the shortest path between two vertices (along edges of certain labels and up to a certain length if depth is specified) - Analytics that produce subgraph. The "request_body "is a json object  as below:

                .. code-block:: javascript

                    {
                    "param":
                    json_string_of(
                    {
                        "vertex_source":{"id":"<source_id>", "label":"<source_label>"}, // mandatory
                    "vertex_target":{"id":"<target_id>", "label":"<target_label>"}, // mandatory
                    "edge_direction":"in"|"out"|"all", // default is "out"
                        "depth":<depth>, // length of the path, default is no limit if unspecified
                    "edge_labels":["<edge_label_1>", "<edge_label_2>", ...], // optional
                    "edge_weight_prop":"<edge_prop_name_for_weight>" // optional, for weighted path
                        "with_vertex_props":"true"|"false", // whether to output vertex properties, default is "false"
                        "with_edge_props":"true"|"false", // whether to output edge properties, default is "false"
                        "exclude_vertices":"true"|"false", // whether to exclude vertices from output, default is "false"
                        "exclude_edges":"true"|"false", // whether to exclude edges from output, default is "false"
                        "result_type":"DB_JSON"|"DB_JSON_FILE"|"DB_SUBGRAPH", // default is "DB_JSON"
                        "result_name":"<json_file_name_or_subgraph_name>",
                        "max_time":<max_run_time_in_seconds>
                    }
                    ),
                    "async":"{\"expiration\":<num_seconds>, \"job_id\":\"<string_job_id>\"}" // for async and async_kafka
                    }


            *connected/strong*: Compute the strongly connected components of the graph (consider edge direction) - Analytics that produce components. The "request_body "is a json object  as below:

                .. code-block:: javascript

                    {
                    "param":
                    json_string_of(
                    {
                        "edge_labels":["<edge_label_1>", "<edge_label_2>", ...], //optional
                        "with_vertex_props":"true"|"false", // whether to output vertex properties, default is "false"
                        "with_edge_props":"true"|"false", // whether to output edge properties, default is "false"
                        "exclude_vertices":"true"|"false", // whether to exclude vertices from output, default is "false"
                        "exclude_edges":"true"|"false", // whether to exclude edges from output, default is "false"
                        "min_size":<min_component_size_to_be_included>, // default is 0
                        "max_size":<max_component_size_to_be_included>, // default is max_long
                        "sort":"by size desc"|"by size asc", // default is no sorting
                        "result_type":"DB_JSON"|"DB_JSON_FILE"|"DB_STORE"|"DB_STORE_AND_JSON"| "DB_STORE_AND_JSON_FILE"|"DB_SUBGRAPH"|"DB_SUBGRAPH_JSON", // default is DB_JSON
                        "result_name":"< json_file_name_or_store_name_or_subgraph_name>",
                        "max_time":<max_run_time_in_seconds>
                    }
                    ),
                    "async":"{\"expiration\":<num_seconds>, \"job_id\":\"<string_job_id>\"}" // for async and async_kafka
                    }


            *connected/weak*: Compute the weakly connected components of the graph (ignore edge direction) - Analytics that produce components. The "request_body "is a json object  as below:

                .. code-block:: javascript

                    {
                    "param":
                    json_string_of(
                    {
                    "mode":"one"|"select"|"all", //mandatory
                        "vertex_ego":{"id":"<vertex_id>", "label":"<vertex_label>"}, // when mode is "one"
                        "vertices": // when mode is "select", compute weakly connected components starting from specified vertices
                        [
                            {"id":"<vertex_id_1>", "label":"<vertex_label_1>"},
                            {"id":"<vertex_id_2>", "label":"<vertex_label_2>"},
                            ...
                    ],
                        "vertex_props": // when mode is "select", alternative to "vertices", compute weakly connected components starting from vertices satisfying property constraints
                        [
                            {
                                "prop_name":"<vertex_prop_name_1>",
                                "prop_value":"<vertex_prop_value_1>",
                            },
                            ...
                        ],
                        "edge_labels":["<edge_label_1>", "<edge_label_2>", ...], //optional
                        "with_vertex_props":"true"|"false", // whether to output vertex properties, default is "false"
                        "with_edge_props":"true"|"false", // whether to output edge properties, default is "false"
                        "exclude_vertices":"true"|"false", // whether to exclude vertices from output, default is "false"
                        "exclude_edges":"true"|"false", // whether to exclude edges from output, default is "false"
                        "min_size":<min_component_size_to_be_included>, // default is 0
                        "max_size":<max_component_size_to_be_included>, // default is max_long
                        "sort":"by size desc"|"by size asc", // default is no sorting
                        "result_type":"DB_JSON"|"DB_JSON_FILE"|"DB_STORE"|"DB_STORE_AND_JSON"| "DB_STORE_AND_JSON_FILE"|"DB_SUBGRAPH"|"DB_SUBGRAPH_JSON", // default is DB_JSON
                        "result_name":"< json_file_name_or_store_name_or_subgraph_name>",
                        "max_time":<max_run_time_in_seconds>
                    }
                    ),
                    "async":"{\"expiration\":<num_seconds>, \"job_id\":\"<string_job_id>\"}" // for async and async_kafka
                    }


            *cycle*: Compute the directed cycles (simple loops) in the graph given constraints - Analytics that produce components. The "request_body "is a json object  as below:

                .. code-block:: javascript

                    // When edge_props is specified, the values of the corresponding property on the adjacent edges A and B in a cycle must satisfy edge_prop_x_value_of_A*(1-edge_prop_value_threshold_x) <= edge_prop_y_value_of_B <= edge_prop_x_value_of_A*(1+edge_prop_value_threshold_x) for any combination of x and y, where x or y ranges from 1 to the number of properties specified in edge_props.
                    // When mode is "one", all cycles starting from the single specified vertex are returned. When mode is "select" or "onebyone", all cycles starting from the specified vertices via id/label or vertex property constraints are returned. Multiple vertex property constraints are ANDed together. When mode is "all", all unique simple cycles (no revisiting of a vertex in the cycle) are returned.
                    // The difference between "select" and "onebyone" is that the "select" mode skips V¬i for i=0 to n-1 when it looks for cycles starting from V¬n to reduce redundant checking. This works for regular cycles, but for cycles with edge property constraint which is sensitive to the starting vertex of a cycle (i.e. the edge property constraint may only be satisfied when starting from certain vertices but not every vertex in a cycle), the "select" mode may miss some cycles. In contrast, the "onebyone" mode is equivalent to calling the mode "one" for a list of vertices one at a time, then deduplicating cycles in the end. As a result, the "onebyone" mode may be less efficient, but guarantees completeness of the result when edge_props is specified.


                    {
                    "param":
                    json_string_of(
                    {
                        "mode":"one"|"onebyone"|"select"|"all", //mandatory
                        "vertex_ego":{"id":"<vertex_id>", "label":"<vertex_label>"}, // when mode is "one"
                        "vertices": // when mode is "select" or "onebyone", compute cycles starting from specified vertices
                        [
                            {"id":"<vertex_id_1>", "label":"<vertex_label_1>"},
                            {"id":"<vertex_id_2>", "label":"<vertex_label_2>"},
                            ...
                        ],
                        "vertex_props": // when mode is "select" or "onebyone", compute cycles starting from vertices satisfying property constraints, alternative to "vertices"
                        [
                            {
                                "prop_name":"<vertex_prop_name_1>",
                                "prop_value":"<vertex_prop_value_1>",
                            },
                            ...
                        ],
                        "depth":<max_length_of_cycle>, // default is unlimited
                        "edge_labels":["<edge_label_1>", "<edge_label_2>", ...], //optional
                        "edge_props": //optional
                        [
                            {
                                "prop_name":"<edge_prop_name_1>",
                                "threshold":"<edge_prop_value_threshold_1>",
                            },
                            …
                        ],
                        "with_vertex_props":"true"|"false", // whether to output vertex properties, default is "false"
                        "with_edge_props":"true"|"false", // whether to output edge properties, default is "false"
                        "exclude_vertices":"true"|"false", // whether to exclude vertices from output, default is "false"
                        "exclude_edges":"true"|"false", // whether to exclude edges from output, default is "false"
                        "min_size":<min_component_size_to_be_included>, // default is 0
                        "max_size":<max_component_size_to_be_included>, // default is max_long
                        "sort":"by size desc"|"by size asc",  // default is no sorting
                        "result_type":"DB_JSON"|"DB_JSON_FILE"|"DB_STORE"|"DB_STORE_AND_JSON"|  "DB_STORE_AND_JSON_FILE"|"DB_SUBGRAPH"|"DB_SUBGRAPH_JSON", // default is DB_JSON
                        "result_name":"<json_file_name_or_store_name_or_subgraph_name>",
                        "max_time":<max_run_time_in_seconds>
                    }
                    ),
                    "async":"{\"expiration\":<num_seconds>, \"job_id\":\"<string_job_id>\"}" // for async and async_kafka
                    }


            *cycle/connected/composite*: Compute the weakly connected components of the directed cycles (simple loops) in the graph given constraints - Analytics that produce components. **{"param_cycle": json_str1, "param_connected": json_str2}** the json_str1 and json_str2 are json-like string as below:

                .. code-block:: javascript

                    {
                    "param_cycle":
                    json_string_of(
                    {
                        "mode":"onebyone"|"select"|"all", //mandatory
                        "vertices": // compute cycles starting from specified vertices
                        [
                            {"id":"<vertex_id_1>", "label":"<vertex_label_1>"},
                            {"id":"<vertex_id_2>", "label":"<vertex_label_2>"},
                            ...
                        ],
                        "vertex_props": // alternative to "vertices", compute cycles starting from vertices satisfying property constraints
                        [
                            {
                                "prop_name":"<vertex_prop_name_1>",
                                "prop_value":"<vertex_prop_value_1>",
                            },
                            ...
                        ],
                        "depth":<max_length_of_cycle>, // default is unlimited
                        "edge_labels":["<edge_label_1>", "<edge_label_2>", ...], // optional
                        "edge_props": // optional
                        [
                            {
                                "prop_name":"<edge_prop_name_1>",
                                "threshold":"<edge_prop_value_threshold_1>",
                            },
                            ...
                        ],
                        "with_vertex_props":"true",
                        "with_edge_props":"true",
                    "result_type":"DB_SUBGRAPH",
                        "result_name":"<name_of_cycle_subgraph>",
                        "max_time":<max_run_time_in_seconds>
                    }
                    ),
                    "param_connected":
                    json_string_of(
                    {
                    "mode":"all",
                        "with_vertex_props":"true"|"false", // whether to output vertex properties, default is "false"
                        "with_edge_props":"true"|"false", // whether to output edge properties, default is "false"
                        "exclude_vertices":"true"|"false", // whether to exclude vertices from output, default is "false"
                        "exclude_edges":"true"|"false", // whether to exclude edges from output, default is "false"
                    "min_size":<min_component_size_to_be_included>, // default is 0
                    "max_size":<max_component_size_to_be_included>, // default is max_long
                    "sort":"by size desc"|"by size asc",
                    "result_type":"DB_JSON"|"DB_JSON_FILE"|"DB_STORE"|"DB_STORE_AND_JSON"| "DB_STORE_AND_JSON_FILE"|"DB_SUBGRAPH"|"DB_SUBGRAPH_JSON", // default is DB_JSON
                        "result_name":"<json_file_name_or_store_name_or_subgraph_name>",
                        "max_time":<max_run_time_in_seconds>
                    }
                    ),
                    "async":"{\"expiration\":<num_seconds>, \"job_id\":\"<string_job_id>\"}" // for async and async_kafka
                    }

            *community/louvain*: Compute centrality and degree metrics - Analytics that produce metrics. The "request_body "is a json object  as below:

                .. code-block:: javascript

                    {
                    "param":
                    json_string_of(
                    {
                    "edge_labels":["<edge_label_1>", "<edge_label_2>", ...], //optional
                    "edge_weight_prop":"<edge_prop_name_for_weight>", //optional
                    "iterations":<num_iterations>, // default is max_long
                    "edge_direction":"out"|"all", // use "out" for directed and "all" for undirected, default is "all"
                        "with_vertex_props":"true"|"false", // whether to output vertex properties, default is "false"
                        "with_edge_props":"true"|"false", // whether to output edge properties, default is "false"
                        "exclude_vertices":"true"|"false", // whether to exclude vertices from output, default is "false"
                        "exclude_edges":"true"|"false", // whether to exclude edges from output, default is "false"
                        "min_size":<min_component_size_to_be_included>, // default is 0
                        "max_size":<max_component_size_to_be_included>, // default is max_long
                        "sort":"by size desc"|"by size asc", // default is no sorting
                        "result_type":"DB_JSON"|"DB_JSON_FILE"|"DB_STORE"|"DB_STORE_AND_JSON"| "DB_STORE_AND_JSON_FILE"|"DB_SUBGRAPH"|"DB_SUBGRAPH_JSON", // default is DB_JSON
                        "result_name":"< json_file_name_or_store_name_or_subgraph_name>",
                        "max_time":<max_run_time_in_seconds>
                    }
                    ),
                    "async":"{\"expiration\":<num_seconds>, \"job_id\":\"<string_job_id>\"}" // for async and async_kafka
                    }

            *metrics*: Compute Louvain communities. The "request_body "is a json object  as below:

                .. code-block:: javascript

                    // The following metrics are supported:
                    //	b: betweenness centrality
                    //	c: closeness centrality
                    //	e: eccentricity
                    //	i: in degree
                    //	o: out degree
                    //	p: is peripheral vertex
                    //	v: is central vertex

                    {
                    "param":
                    json_string_of(
                    {
                        "depth":<depth>, // for centrality computation based on shortest-paths
                        "edge_labels":["<edge_label_1>", "<edge_label_2>", ...], // optional
                        "edge_weight_prop":"<edge_prop_name_for_weight>", // for centrality computation using weighted shortest-paths
                        "metrics": "<concatenated_acronyms_for_metrics>", // mandatory, invalid metric acronym is ignored
                        "bc_norm":0|1, // whether to calculate normalized betweenness centrality, default is 1
                    "result_type":"DB_JSON"|"DB_JSON_FILE"|"DB_STORE", // default is DB_JSON
                        "result_name":"<json_file_name_or_store_name>",
                    "max_time":<max_run_time_in_seconds>
                    }
                    ),
                    "async":"{\"expiration\":<num_seconds>, \"job_id\":\"<string_job_id>\"}" // for async and async_kafka
                    }


            *metrics/subgraph*: Compute centrality and degree metrics on a subgraph provided in request - Analytics that produce metrics. The "request_body "is a json object  as below:

                .. code-block:: javascript

                    {
                    "param":
                    json_string_of(
                    {
                        "depth":<depth>, // for centrality computation based on shortest-paths
                        "edge_labels":["<edge_label_1>", "<edge_label_2>", ...], // optional
                        "edge_weight_prop":"<edge_prop_name_for_weight>", // for centrality computation using weighted shortest-paths
                    "metrics": "<concatenated_acronyms_for_metrics>", // mandatory, invalid metric acronym is ignored
                        "data": // specify the subgraph, which must have the same schema as the original graph named <graph_name>
                        {
                            "vertices":
                            [
                                {
                                    "id":"<vertex_id_1>",
                                    "label":"<vertex_label_1>",
                                    "properties":
                                    [
                                        {"<prop_name_1>":<prop_value_1>},
                                        {"<prop_name_2>":<prop_value_2>},
                                        ...
                                    ]
                                },
                                ...
                            ],
                            "edges":
                            [
                                {
                                    "source_id":"<source_id_1>",
                                    "source_label":"<source_label_1>",
                                    "target_id":"<target_id_1>",
                                    "target_label":"<target_label_1>",
                                    "label":"<edge_label>",
                                    "properties":
                                    [
                                        {"<prop_name_1>":<prop_value_1>},
                                        {"<prop_name_2>":<prop_value_2>},
                                        ...
                                    ]
                                },
                                ...
                            ]
                        },
                    "result_type":"DB_JSON"|"DB_JSON_FILE"|"DB_STORE", // default is DB_JSON
                        "result_name":"<json_file_name_or_store_name>",
                    "max_time":<max_run_time_in_seconds>
                    }
                    )
                    }


            *pagerank*: Compute the pagerank values of vertices with specific vertex label(s) connected via specific edge label(s) - Analytics that produce metrics. The "request_body "is a json object  as below:

                .. code-block:: javascript

                    {
                    "param":
                    json_string_of(
                    {
                        "edge_labels":["<edge_label_1>", "<edge_label_2>", ...],
                    "iterations":<num_iterations>, // default is 1000
                    "damping_factor":<damping_factor>, // default is 0.85
                        "result_type":"DB_JSON"|"DB_JSON_FILE"|"DB_STORE", // default is DB_JSON
                        "result_name":"<json_file_name_or_store_name>",
                    "max_time":<max_run_time_in_seconds>
                    }
                    ),
                    "async":"{\"expiration\":<num_seconds>, \"job_id\":\"<string_job_id>\"}" // for async and async_kafka
                    }


        Returns
        -------
        Analytics that produce subgraph

            This set of analytics produce a subgraph (extracted from the original graph on which an analytic is run) represented as a list of vertices and a list of edges. The following result types are supported:

            - DB_JSON: result is returned as json string in http response.
            - DB_JSON_FILE: result is saved to a file on the server.
            - DB_SUBGRAPH: result is saved to a new graph on disk.

            By default, the result type is DB_JSON when unspecified.

            *When the result type is DB_JSON, the result format is:*

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_vertices": "<number_of_vertices_returned>",
                        "num_edges": "<number_of_edges_returned>"
                      },
                      "data": {
                        "vertices": [
                          {
                            "id": "<vertex_id_1>",
                            "label": "<vertex_label_1>",
                            "properties": [
                              {
                                "<prop_name_1>": "<prop_value_1>}"
                              },
                              {
                                "<prop_name_2>": "<prop_value_2>"
                              },
                              "..."
                            ]
                          },
                          "..."
                        ],
                        "edges": [
                          {
                            "source_id": "<source_id_1>",
                            "source_label": "<source_label_1>",
                            "target_id": "<target_id_1>",
                            "target_label": "<target_label_1>",
                            "eid": "<eid>",
                            "label": "<edge_label>",
                            "properties": [
                              {
                                "<prop_name_1>": "<prop_value_1>"
                              },
                              {
                                "<prop_name_2>": "<prop_value_2>"
                              },
                              "..."
                            ]
                          },
                          "..."
                        ]
                      }
                    }

            *When the result format is DB_JSON_FILE, the result format is:*

                .. code-block:: json

                    {
                      "status": "success",
                      "path": "<path_to_json_file_on_server"
                    }

            *When the result format is DB_SUBGRAPH, the result format is:*

                .. code-block:: json

                    {
                      "status": "success",
                      "path": "<subgraph_name>"
                    }

        Analytics that produce components

            This set of analytics produce a list of components. Each component (e.g. a connected component, a cycle) is a subgraph represented by a list of vertices and a list of edges. The following result types are supported:

            - DB_JSON: result is returned as json string in http response.
            - DB_JSON_FILE: result is saved to a file on the server.
            - DB_STORE: result is saved to a store on disk.
            - DB_STORE_AND_JSON: result is saved to a store on disk and returned as json string in http response.
            - DB_STORE_AND_JSON_FILE: result is saved to a store on disk and a file on the server.
            - DB_SUBGRAPH (only applicable to cycle): all components are merged to create an aggregate graph saved on disk.
            - DB_SUBGRAPH_JSON (only applicable to cycle): all components are merged and returned as json string in http response.

            By default, the result type is DB_JSON (when unspecified).

            *When the result type is DB_JSON or DB_STORE_AND_JSON, the result format is:*

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_components": "<number_of_components_returned>"
                      },
                      "components": [
                        {
                          "id": "<component_id>",
                          "statistics": {
                            "num_vertices": "<number_of_vertices_in_component_1>",
                            "num_edges": "<number_of_edges_in_component_1>"
                          },
                          "data": {
                            "vertices": [
                              {
                                "id": "<vertex_id_1>",
                                "label": "<vertex_label_1>",
                                "properties": [
                                  {
                                    "<prop_name_1>": "<prop_value_1>"
                                  },
                                  {
                                    "<prop_name_2>": "<prop_value_2>"
                                  },
                                  "..."
                                ]
                              },
                              "..."
                            ],
                            "edges": [
                              {
                                "source_id": "<source_id_1>",
                                "source_label": "<source_label_1>",
                                "target_id": "<target_id_1>",
                                "target_label": "<target_label_1>",
                                "eid": "<eid>",
                                "label": "<edge_label>",
                                "properties": [
                                  {
                                    "<prop_name_1>": "<prop_value_1>"
                                  },
                                  {
                                    "<prop_name_2>": "<prop_value_2>"
                                  },
                                  "..."
                                ]
                              },
                              "..."
                            ]
                          }
                        },
                        "..."
                      ]
                    }

            *When the result format is DB_JSON_FILE, the result format is:*

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_components": "<num_components>"
                      },
                      "path": "<path_to_json_file_on_server>"
                    }

            *When the result format is DB_STORE, the result format is:*

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_compnents": "<num_components>"
                      },
                      "store_name": "<store_name>"
                    }

            *When the result format is DB_STORE_AND_JSON_FILE, the result format is:*

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_components": "<num_components>"
                      },
                      "store_name": "<store_name>",
                      "file_name": "<path_to_json_file_on_server>"
                    }

            *When the result format is DB_SUBGRAPH, the result format is:*

                .. code-block:: json

                    {
                      "status": "success",
                      "path": "<subgraph_name>"
                    }

            *When the result format is DB_SUBGRAPH_JSON, the result format is:*

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_components": "<num_components>",
                        "num_vertices": "<number_of_vertices_returned>",
                        "num_edges": "<number_of_edges_returned>"
                      },
                      "data": {
                        "vertices": [
                          {
                            "id": "<vertex_id_1>",
                            "label": "<vertex_label_1>",
                            "properties": [
                              {
                                "<prop_name_1>": "<prop_value_1>"
                              },
                              {
                                "<prop_name_2>": "<prop_value_2>"
                              },
                              "..."
                            ]
                          },
                          "..."
                        ],
                        "edges": [
                          {
                            "source_id": "<source_id_1>",
                            "source_label": "<source_label_1>",
                            "target_id": "<target_id_1>",
                            "target_label": "<target_label_1>",
                            "eid": "<eid>",
                            "label": "<edge_label>",
                            "properties": [
                              {
                                "<prop_name_1>": "<prop_value_1>"
                              },
                              {
                                "<prop_name_2>": "<prop_value_2>"
                              },
                              "..."
                            ]
                          },
                          "..."
                        ]
                      }
                    }

        Analytics that produce metrics

            This set of analytics produce results in the form of key-value pairs. Usually the key is vertex ID and the value is the metric value. The following result types are supported:

            - DB_JSON: result is returned as json string in http response.
            - DB_JSON_FILE: result is saved to a file on the server.
            - DB_STORE: result is saved to a store on disk.
            - DB_STORE_AND_JSON: result is saved to a store on disk and returned as json string in http response.
            - DB_STORE_AND_JSON_FILE: result is saved to a store on disk and a file on the server.

            *When the result type is DB_JSON, the result has the following format (metrics may vary):*

                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_edges": 0,
                        "num_vertices": "<num_vertices_returned>"
                      },
                      "data": {
                        "edges": [],
                        "vertices": [
                          {
                            "id": "<vertex_id>",
                            "label": "<vertex_label>",
                            "properties": [
                              {
                                "closeness": "<value_1>"
                              },
                              {
                                "betweenness": "<value_2>"
                              },
                              {
                                "eccentricity": "<value_3>"
                              },
                              {
                                "is_center": "1.000000"
                              },
                              {
                                "is_periphery": "1.000000"
                              },
                              {
                                "in_degree": "<value_4>"
                              },
                              {
                                "out_degree": "<value_5>"
                              }
                            ]
                          },
                          "…"
                        ]
                      }
                    }

        Examples
        --------
        .. code-block:: python

            g.set_current_graph(graph_name="crem_graphdb_es_20180301")

            json_str = '''
             {
              "vertices": [
                {
                  "id": "n1",
                  "label": "1"
                },
                {
                  "id": "n2",
                  "label": "1"
                }
              ],
              "depth": 2,
              "edge_labels": [
                "TX",
                "INV_CONTROL"
              ]
            }'''

            request_body = {"param": json_str}

            json_str1 = '''
             {
              "mode": "select",
              "vertices": [
                {
                  "id": "n1",
                  "label": "1"
                },
                {
                  "id": "n2",
                  "label": "1"
                }
              ],
              "depth": 2,
              "edge_labels": [
                "TX",
                "INV_CONTROL"
              ],
              "with_vertex_props": "true",
              "with_edge_props": "true",
              "result_type": "DB_SUBGRAPH",
              "result_name": "crem_graphdb_es_20180301_test"
            }'''

            json_str2 = '''
            {
              "mode": "all",
              "with_vertex_props": "true",
              "with_edge_props": "false",
              "exclude_vertices": "false",
              "exclude_edges": "false",
              "min_size": 2,
              "max_size": 23,
              "sort": "by size desc",
              "result_type": "DB_JSON",
              "result_name": "test"
            }'''

            request_body_ccc = {
                "param_cycle": json_str1,
                "param_connected": json_str2
            }

            g.run_analytics(analytic_name="cycle/connected/composite", request_body=request_body_ccc)

            g.run_analytics(analytic_name="egonet", request_body=request_body)

            g.run_analytics(analytic_name="bfs", request_body=request_body)

            g.run_analytics(analytic_name="cycle", request_body=request_body)

            g.run_analytics(analytic_name="connected/weak", request_body=request_body)


            json_str = '''
            {
              "start_date": "20180301",
              "end_date": "20180307",
              "result_type": "DB_JSON",
              "output_type": "individual",
              "analytics": [
                {
                  "analytic": "bfs_connected",
                  "graph": "crem_graphdb_es_",
                  "vertices": [
                    {
                      "id": "n23",
                      "label": "1"
                    }
                  ],
                  "edge_labels": [
                    "GROUP",
                    "INV_TOPNONCONTROL",
                    "INV_OTHER",
                    "FACTORING",
                    "SUPPLY_CHAIN",
                    "MANAGER_CORP_CARD",
                    "CORP_CARD_HOLDER",
                    "MANAGER_INDV_SAME_CARD",
                    "MANAGER_INDV_CARD",
                    "GEN_GUAR",
                    "CORP_TWO_LEGAL_PERSON",
                    "SAME_PHONE_AND_ADDRESS",
                    "CORP_OTHER_MANAGER"
                  ],
                  "edge_direction": "ALL",
                  "depth": 1,
                  "exclude_vertices": "false",
                  "exclude_edges": "false",
                  "with_vertex_props": "true",
                  "with_edge_props": "true"
                },
                {
                  "analytic": "bfs_connected",
                  "graph": "crem_graphdb_es_",
                  "vertices": [
                    {
                      "id": "n23",
                      "label": "1"
                    }
                  ],
                  "edge_labels": [
                    "BANK_NOTES",
                    "LOC",
                    "ENTRUSTED_PAYMENT",
                    "INDV_THIRD_PARTY",
                    "INDV_LEGAL_PERSON",
                    "INDV_OTHER_MANAGER"
                  ],
                  "edge_direction": "IN",
                  "depth": 1,
                  "exclude_vertices": "false",
                  "exclude_edges": "false",
                  "with_vertex_props": "true",
                  "with_edge_props": "true"
                },
                {
                  "analytic": "bfs_connected",
                  "graph": "crem_graphdb_es_",
                  "vertices": [
                    {
                      "id": "n23",
                      "label": "1"
                    }
                  ],
                  "edge_labels": [
                    "INV_CONTROL",
                    "CORP_LEGAL_THIRD_PARTY",
                    "CORP_LEGAL_INV_CONTROL",
                    "CORP_ONE_LEGAL_PERSON",
                    "CORP_LEGAL_INV_NONCONTROL"
                  ],
                  "edge_direction": "OUT",
                  "depth": 1,
                  "exclude_vertices": "false",
                  "exclude_edges": "false",
                  "with_vertex_props": "true",
                  "with_edge_props": "true"
                },
                {
                  "analytic": "component_to_json",
                  "mode": "ONE",
                  "vertex_ego": {
                    "id": "n23",
                    "label": "1"
                  },
                  "edge_labels": [
                    "INV_CONTROL"
                  ],
                  "graph": "crem_graphdb_es_",
                  "store_name": "crem_graphdb_es_21_",
                  "exclude_vertices": "false",
                  "exclude_edges": "false",
                  "with_vertex_props": "true",
                  "with_edge_props": "true"
                },
                {
                  "analytic": "component_to_json",
                  "mode": "ONE",
                  "vertex_ego": {
                    "id": "n23",
                    "label": "1"
                  },
                  "edge_labels": [
                    "CORP_THIRD_PARTY"
                  ],
                  "graph": "crem_graphdb_es_",
                  "store_name": "crem_graphdb_es_61_",
                  "exclude_vertices": "false",
                  "exclude_edges": "false",
                  "with_vertex_props": "true",
                  "with_edge_props": "true"
                },
                {
                  "analytic": "component_to_json",
                  "mode": "ONE",
                  "vertex_ego": {
                    "id": "n23",
                    "label": "1"
                  },
                  "edge_labels": [
                    "JOINT_GUAR",
                    "INV_GUAR",
                    "GEN_GUAR"
                  ],
                  "graph": "crem_graphdb_es_",
                  "store_name": "crem_graphdb_es_75_",
                  "exclude_vertices": "false",
                  "exclude_edges": "false",
                  "with_vertex_props": "true",
                  "with_edge_props": "true"
                },
                {
                  "analytic": "component_to_json",
                  "mode": "ONE",
                  "vertex_ego": {
                    "id": "n23",
                    "label": "1"
                  },
                  "edge_labels": [
                    "TX"
                  ],
                  "graph": "crem_graphdb_es_32_",
                  "store_name": "crem_graphdb_es_32_",
                  "exclude_vertices": "false",
                  "exclude_edges": "false",
                  "with_vertex_props": "true",
                  "with_edge_props": "true"
                },
                {
                  "analytic": "component_to_json",
                  "mode": "ONE",
                  "vertex_ego": {
                    "id": "n23",
                    "label": "1"
                  },
                  "edge_labels": [
                    "TX"
                  ],
                  "graph": "crem_graphdb_es_33_",
                  "store_name": "crem_graphdb_es_33_",
                  "exclude_vertices": "false",
                  "exclude_edges": "false",
                  "with_vertex_props": "true",
                  "with_edge_props": "true"
                },
                {
                  "analytic": "component_to_json",
                  "mode": "ONE",
                  "vertex_ego": {
                    "id": "n23",
                    "label": "1"
                  },
                  "edge_labels": [
                    "BANK_NOTES",
                    "FACTORING",
                    "SUPPLY_CHAIN",
                    "LOC",
                    "ENTRUSTED_PAYMENT"
                  ],
                  "graph": "crem_graphdb_es_46_",
                  "store_name": "crem_graphdb_es_46_",
                  "exclude_vertices": "false",
                  "exclude_edges": "false",
                  "with_vertex_props": "true",
                  "with_edge_props": "true"
                },
                {
                  "analytic": "component_to_json",
                  "mode": "ONE",
                  "vertex_ego": {
                    "id": "n23",
                    "label": "1"
                  },
                  "edge_labels": [
                    "JOINT_GUAR",
                    "INV_GUAR",
                    "GEN_GUAR"
                  ],
                  "graph": "crem_graphdb_es_71_",
                  "store_name": "crem_graphdb_es_71_",
                  "exclude_vertices": "false",
                  "exclude_edges": "false",
                  "with_vertex_props": "true",
                  "with_edge_props": "true"
                },
                {
                  "analytic": "component_to_json",
                  "mode": "ONE",
                  "vertex_ego": {
                    "id": "n23",
                    "label": "1"
                  },
                  "edge_labels": [
                    "JOINT_GUAR",
                    "INV_GUAR",
                    "GEN_GUAR"
                  ],
                  "graph": "crem_graphdb_es_74_",
                  "store_name": "crem_graphdb_es_74_",
                  "exclude_vertices": "false",
                  "exclude_edges": "false",
                  "with_vertex_props": "true",
                  "with_edge_props": "true"
                }
              ]
            }'''

            request_body = {"param": json_str}

            g.run_analytics(analytic_name="aggregate_bfs_cycle_connected", request_body=request_body)

            json_str = '''
            {
              "metrics": "cbio",
              "result_type": "DB_STORE",
              "result_name": "crem_graphdb_es_metrics_20180301"
            }'''

            request_body = {"param": json_str}

            g.run_analytics(analytic_name="metrics", request_body=request_body)

        """

        if request_type:
            url = self.root_url + "/{}/graphs/".format(request_type) + self.graph_name + "/analytics/" + analytic_name
        else:
            url = self.root_url + "/graphs/" + self.graph_name + "/analytics/" + analytic_name

        # config_param = {}
        # config_param["param"] = json_str
        return _post_query(url, request_body)

    # Get the egonet of a vertex
    def get_egonet(self, vertex_label, vertex_id, depth='', edge_label=[]):
        """
        Get the egonet of a vertex (ignore edge direction, which is K-hop neighbors up to a certain depth and edges among these vertices; if one or more edge labels are specified, only edges of these labels are included)

        Parameters
        ----------
        vertex_label
            str
                vertex label
        vertex_id
            str
                vertex id
        depth
            int
                steps from the vertex
        edge_label
            list
                optional, list of edge labels

        Returns
        -------
            str
                .. code-block:: json

                    {
                      "status": "success",
                      "statistics": {
                        "num_vertices": "<number_of_vertices_returned>",
                        "num_edges": "<number_of_edges_returned>"
                      },
                      "data": {
                        "vertices": [
                          {
                            "id": "<vertex_id_1>",
                            "label": "<vertex_label_1>",
                            "properties": [
                              {
                                "<prop_name_1>": "<prop_value_1>}"
                              },
                              {
                                "<prop_name_2>": "<prop_value_2>"
                              },
                              "..."
                            ]
                          },
                          "..."
                        ],
                        "edges": [
                          {
                            "source_id": "<source_id_1>",
                            "source_label": "<source_label_1>",
                            "target_id": "<target_id_1>",
                            "target_label": "<target_label_1>",
                            "eid": "<eid>",
                            "label": "<edge_label>",
                            "properties": [
                              {
                                "<prop_name_1>": "<prop_value_1>"
                              },
                              {
                                "<prop_name_2>": "<prop_value_2>"
                              },
                              "..."
                            ]
                          },
                          "..."
                        ]
                      }
                    }

        Examples
        --------
        .. code-block:: python

            g.get_egonet(vertex_id="1", vertex_label="v1")
            g.get_egonet(vertex_id="1", vertex_label="v1", depth=0, edge_label=["e1", "e2"])

        """
        url = self.root_url + '/graphs/' + self.graph_name + "/vertices/" + vertex_label + '/' + vertex_id + '/analytics/egonet'
        if depth or edge_label:
            url += "?"
            if str(depth):
                url += "depth=" + str(depth)
                if edge_label:
                    url += '&'
            if edge_label:
                url += "edge_label="
                url = _url_assemble(url, edge_label)
        logging.debug(url)
        return _query(url)

    # def get_egonet_multi(self, vertex_label, vertex_id, depth, edge_label=[]):
    #     url = self.root_url + '/graphs/' + self.graph_name + '/analytics/egonet'
    #     config_param = {}
    #     vertex_list = []
    #     len_ids = len(vertex_ids)
    #     len_labels = len(vertex_labels)
    #     if len_ids != len_labels:
    #         return "vertex_id and vertex_label do not match!"
    #     for i in xrange(len_ids):
    #         d = {"id": vertex_ids[i], "label": vertex_labels[i]}
    #         vertex_list.append(d)
    #     data = {
    #         "vertices": vertex_list,
    #         "depth": depth,
    #         "edge_labels": edge_label
    #     }
    #     config_param['param'] = json.dumps(data)
    #     return _post_query(url, config_param)

    # def get_egonet_priority(self, vertex_ids, vertex_labels, depths, edge_label=[]):
    #     url = self.root_url + '/graphs/' + self.graph_name + '/analytics/egonet/priority'
    #     config_param = {}
    #     vertex_list = []
    #     len_ids = len(vertex_ids)
    #     len_labels = len(vertex_labels)
    #     len_depths = len(depths)
    #     if len_ids != len_labels or len_ids != len_depths:
    #         return "vertex_id, vertex_label and depth do not match!"
    #     for i in xrange(len_ids):
    #         d = {"id": vertex_ids[i], "label": vertex_labels[i]}
    #         vertex_list.append(d)
    #     data = {
    #         "vertices": vertex_list,
    #         "depth": depths,
    #         "edge_labels": edge_label
    #     }
    #     config_param['param'] = json.dumps(data)
    #     return _post_query(url, config_param)

    # def get_subgraph(self, vertex_ids, vertex_labels, edge_labels=[]):
    #     url = self.root_url + '/graphs/' + self.graph_name + '/analytics/subgraph'
    #     config_param = {}
    #     # data = {}
    #     # data['vertices'] = []
    #     # data['edge_labels'] = edge_labels
    #     # if len(vertex_ids) == len(vertex_labels):
    #     #     for i in range(0, len(vertex_ids)):
    #     #         field = {}
    #     #         field['id'] = vertex_ids[i]
    #     #         field['label'] = vertex_labels[i]
    #     #         data['vertices'].append(field)
    #     vertex_list = []
    #     len_ids = len(vertex_ids)
    #     len_labels = len(vertex_labels)
    #     if len_ids != len_labels:
    #         return "vertex_id, vertex_label and depth do not match!"
    #     for i in xrange(len_ids):
    #         d = {"id": vertex_ids[i], "label": vertex_labels[i]}
    #         vertex_list.append(d)
    #     data = {
    #         "vertices": vertex_list,
    #         "edge_labels": edge_labels
    #     }
    #     config_param['param'] = json.dumps(data)
    #     logging.debug(config_param)
    #     return _post_query(url, config_param)
    #
    # def get_path(self, source_id, source_label, target_id, target_label, edge_labels, depth):
    #     url = self.root_url + '/graphs/' + self.graph_name + '/analytics/path'
    #     config_param = {}
    #     data = {}
    #     data['vertex_source'] = {}
    #     data['vertex_source']['id'] = source_id
    #     data['vertex_source']['label'] = source_label
    #     data['vertex_target'] = {}
    #     data['vertex_target']['id'] = target_id
    #     data['vertex_target']['label'] = target_label
    #     data['depth'] = depth
    #     data['edge_labels'] = edge_labels
    #     config_param['param'] = json.dumps(data)
    #     logging.debug(config_param)
    #     return _post_query(url, config_param)
    #
    # def get_cycle(self, vertex_label, vertex_id, vertex_props, depth, edge_labels, edge_props, result_name):
    #     url = self.root_url + "/graphs/" + self.graph_name + "/analytics/cycle"
    #     config_param = {}
    #     data = {
    #         "vertex_ego": {"id": vertex_id, "label": vertex_label},
    #         "vertex_props": vertex_props,
    #         "depth": depth,
    #         "edge_labels": edge_labels,
    #         "edge_props": edge_props,
    #         "result_name": result_name
    #     }
    #     config_param['param'] = json.dumps(data)
    #     logging.debug(config_param)
    #     return _post_query(url, config_param)
    #
    # def get_cycle_new(self, vertices, depth, edge_labels, vertex_props='', edge_props='', result_name='',
    #                   result_type=''):
    #     url = self.root_url + "/graphs/" + self.graph_name + "/analytics/cycle"
    #     config_param = {}
    #     data = {
    #         # "vertex_ego": {"id": vertex_id, "label": vertex_label},
    #         "vertices": vertices,
    #         "vertex_props": vertex_props,
    #         "depth": depth,
    #         "edge_labels": edge_labels,
    #         "edge_props": edge_props,
    #         "result_name": result_name,
    #         "result_type": result_type
    #     }
    #     config_param['param'] = json.dumps(data)
    #     logging.debug(config_param)
    #     return _post_query(url, config_param)
    #
    # def get_bfs(self, with_vertex_props, with_edge_props, exclude_edges, exclude_vertices, vertices, edge_direction,
    #             edge_labels, depth):
    #     ## with_vertex_props, exclude_edges, vertices, edge_direction, edge_labels, depth
    #     ## "with_vertex_props":"true", "exclude_edges":"true", "vertices":[{"id":"node2", "label":"LABEL"}, {"id":"node4", "label":"LABEL"}], "edge_direction":"ALL", "edge_labels":["A"], "depth":2}
    #     url = self.root_url + "/graphs/" + self.graph_name + "/analytics/bfs"
    #     config_param = {}
    #     data = {
    #         "with_vertex_props": with_vertex_props,
    #         "with_edge_props": with_edge_props,
    #         "exclude_edges": exclude_edges,
    #         "exclude_vertices": exclude_vertices,
    #         "vertices": vertices,
    #         "edge_direction": edge_direction,
    #         "edge_labels": edge_labels,
    #         "depth": depth
    #     }
    #     config_param['param'] = json.dumps(data)
    #     logging.debug(config_param)
    #     return _post_query(url, config_param)

    def retrieve_store_components(self, graph_name, json_str):
        """
        Retrieve from store the components for one or selected or all vertices.

        Parameters
        ----------
        graph_name
            str
                the graph name that calculated the store
        json_str
            str (string of json format defined as below)

                .. code-block:: javascript

                    {
                      "mode": "one | select | all",
                      // mandatory
                      "store_name": "<store_name>",
                      // mandatory
                      "vertex_ego": {
                        "id": "<vertex_id>",
                        "label": "<vertex_label>"
                      },
                      // when mode is “one”
                      "vertices": // when mode is “select”, result is the union of the components containing these vertices
                      [
                        {
                          "id": "<vertex_id_1>",
                          "label": "<vertex_label_1>"
                        },
                        {
                          "id": "<vertex_id_2>",
                          "label": "<vertex_label_2>"
                        },
                        ...
                      ],
                      "vertex_props": // when mode is “select”, alternative to "vertices"
                      [
                        {
                          "prop_name": "<vertex_prop_name_1>",
                          "prop_value": "<vertex_prop_value_1>"
                        },
                        ...
                      ],
                      "edge_labels": [
                        "<edge_label_1>",
                        "<edge_label_2>",
                        ...
                      ],
                      // must be the same as used for creating the component store
                      "with_vertex_props": "true | false",
                      // default is "false"
                      "with_edge_props": "true | false",
                      // default is "false"
                      "exclude_vertices": "true | false",
                      // default is "false"
                      "exclude_edges": "true | false",
                      // default is "false"
                      "min_size": <min_component_size_to_be_included>,
                      // default is 0
                      "max_size": <max_component_size_to_be_included>,
                      // default is max_long
                      "sort": "by size desc | by size asc",
                      "result_type": "DB_JSON | DB_JSON_FILE",
                      // default is DB_JSON
                      "result_name": "<path_to_json_file_on_server_or_subgraph_name>"
                    }



        Returns
        -------
        str
            same as the components result in run_analytics()

        Examples
        --------
        .. code-block:: python

            json_str = '''
            {
              "mode": "all",
              "store_name": "crem_graphdb_es_21_20180301"
            }'''
            g.retrieve_store_components(graph_name="crem_graphdb_es_20180301", json_str=json_str)


        """
        url = self.root_url + '/graphs/' + graph_name + "/results/components"
        config_param = {}
        config_param["param"] = json_str
        return _post_query(url, config_param)

    def retrieve_store_metrics(self, graph_name, store_name, metric_names, vertex_label='', vertex_id='',
                               request_body="", request_type=""):
        """
        Retrieve from store the metrics for all vertices, or a specific vertex, for one or selected or all vertices using request_body.

        Parameters
        ----------
        graph_name
            str
                the graph name generates the store
        store_name
            str
                the store that contains the metrics
        metric_names
            str

                b: betweenness centrality
                c: closeness centrality
                e: eccentricity
                i: in degree
                o: out degree
                p: is peripheral vertex
                v: is central vertex
                r: pagerank
                a: all metrics stored in a single store

        vertex_label
            str
                optional, for a specific vertex
        vertex_id
            str
                optional, for a specific vertex
        request_type
            str
                optional, only used when using request_body, default is "" for sync, chosen from "async", "async_kafka".
        request_body
            dict
                optional, retrieve from store the metrics for one or selected or all vertices by define below:

                .. code-block:: javascript

                    {
                    "param":
                    json_string_of(
                    {
                        "mode":"one"|"select"|"all", // mandatory
                        "store_name":"<store_name>", // mandatory
                    "vertex_ego":{"id":"<vertex_id>", "label":"<vertex_label>"}, // when mode is “one”
                        "vertices": // when mode is “select”
                        [
                            {"id":"<vertex_id_1>", "label":"<vertex_label_1>"},
                            {"id":"<vertex_id_2>", "label":"<vertex_label_2>"},
                            ...
                        ],
                        "vertex_props": // when mode is “select”, alternative to "vertices"
                        [
                            {
                                "prop_name":"<vertex_prop_name_1>",
                                "prop_value":"<vertex_prop_value_1>",
                            },
                            ...
                        ],
                    "metrics": "<concatenated_acronyms_for_metrics>", // mandatory, invalid metric acronym is ignored
                        "result_type":"DB_JSON"|"DB_JSON_FILE", // default is DB_JSON
                        "result_name":"<json_file_name>",
                        "max_time":<max_run_time_in_seconds>
                    }
                    ),
                    "async":"{\"expiration\":<num_seconds>, \"job_id\":\"<string_job_id>\"}" // for async and async_kafka
                    }



        Returns
        -------
        str
            same as run_analytics() for metrics

        Examples
        --------
        .. code-block:: python

            g.set_current_graph(graph_name="crem_graphdb_es_20180301")
            json_str = '''
            {
              "metrics": "cbio",
              "result_type": "DB_STORE",
              "result_name": "crem_graphdb_es_metrics_20180301"
            }'''
            g.run_analytics(analytic_name="metrics", json_str=json_str)

            g.retrieve_store_metrics(graph_name="crem_graphdb_es_20180301", store_name="crem_graphdb_es_metrics_20180301", metric_names="cbio")
            g.retrieve_store_metrics(graph_name="crem_graphdb_es_20180301", store_name="crem_graphdb_es_metrics_20180301", metric_names="cbio", vertex_label="1", vertex_id="n23")

        """
        if request_body:
            if request_type:
                url = self.root_url + "/{}/graphs/".format(
                    request_type) + graph_name + "/results/metrics"
            else:
                url = self.root_url + "/graphs/" + graph_name + "/results/metrics"
            return _post_query(url, request_body)

        url = self.root_url + '/graphs/' + graph_name + '/results/metrics/' + store_name + '/' + metric_names
        if vertex_id and vertex_label:
            url = url + '/' + vertex_label + '/' + vertex_id
        return _query(url)

    ############################ async ##################################

    def load_table_vertex_async(self, column_delimiter, has_header, default_vertex_label, column_header_map,
                                column_number_map, request_setting,
                                file_path='', file_url='', content_type='', data_row_start=0, data_row_end=0,
                                batch_size=10000, input_mode='standard', mode='standard'):
        """

        Notes
        -----
        Special function reserved for ICBC acync kafka loading, please refer to load_table_vertex().

        """
        config_param = {}
        data = {}
        url = self.root_url + "/async_kafka/graphs/" + self.graph_name + '/table/vertex'
        if file_path is not '':
            if 'server://' in file_path:
                if has_header == 1:
                    if column_header_map.has_key('vertex_id'):
                        data = {
                            "request_setting": request_setting,
                            "file_path": file_path[9:],
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            'default_vertex_label': default_vertex_label,
                            'column_header_map': column_header_map,
                            'content_type': content_type,
                            'data_row_start': data_row_start,
                            'data_row_end': data_row_end,
                            'input_mode': input_mode,
                            "mode": mode,
                            "batch_size": batch_size
                        }
                    else:
                        print
                        "column header for vertex_id is required"
                else:
                    if column_number_map.has_key('vertex_id'):
                        data = {
                            "request_setting": request_setting,
                            "file_path": file_path[9:],
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            'default_vertex_label': default_vertex_label,
                            'column_number_map': column_number_map,
                            'content_type': content_type,
                            'data_row_start': data_row_start,
                            'data_row_end': data_row_end,
                            'input_mode': input_mode,
                            "mode": mode,
                            "batch_size": batch_size
                        }
                config_param['param'] = json.dumps(data)
                return _post_query(url, config_param)

            else:
                if has_header == 1:
                    if column_header_map.has_key('vertex_id'):
                        data = {
                            "request_setting": request_setting,
                            "file_path": file_path,
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            "default_vertex_label": default_vertex_label,
                            "column_header_map": column_header_map,
                            "content_type": content_type,
                            "data_row_start": data_row_start,
                            "data_row_end": data_row_end,
                            "input_mode": input_mode,
                            "mode": mode,
                            "batch_size": batch_size
                        }
                        config_param['param'] = json.dumps(data)
                        return _post_query_files(url, config_param, file_path)

                    else:
                        print
                        "column header for vertex_id is required"
                else:
                    if column_number_map.has_key('vertex_id'):
                        data = {
                            "request_setting": request_setting,
                            "file_path": file_path,
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            'default_vertex_label': default_vertex_label,
                            'column_number_map': column_number_map,
                            'content_type': content_type,
                            'data_row_start': data_row_start,
                            'data_row_end': data_row_end,
                            "input_mode": input_mode,
                            "mode": mode,
                            "batch_size": batch_size
                        }
                        config_param['param'] = json.dumps(data)
                        return _post_query_files(url, config_param, file_path)

                    else:
                        print
                        "column number for vertex_id is required"

        elif file_url is not '':
            if has_header == 1:
                if column_header_map.has_key('vertex_id'):
                    data = {
                        "request_setting": request_setting,
                        "file_url": file_url,
                        "column_delimiter": column_delimiter,
                        "has_header": has_header,
                        'default_vertex_label': default_vertex_label,
                        'column_header_map': column_header_map,
                        'content_type': content_type,
                        'data_row_start': data_row_start,
                        'data_row_end': data_row_end,
                        "input_mode": input_mode,
                        "mode": mode,
                        "batch_size": batch_size
                    }
                else:
                    print
                    "column header for vertex_id is required"
            else:
                if column_number_map.has_key('vertex_id'):
                    data = {
                        "request_setting": request_setting,
                        "file_url": file_url,
                        "column_delimiter": column_delimiter,
                        "has_header": has_header,
                        'default_vertex_label': default_vertex_label,
                        'column_number_map': column_number_map,
                        'content_type': content_type,
                        'data_row_start': data_row_start,
                        'data_row_end': data_row_end,
                        "input_mode": input_mode,
                        "mode": mode,
                        "batch_size": batch_size
                    }
            config_param['param'] = json.dumps(data)
            return _post_query(url, config_param)

        else:
            pass

    def load_table_edge_async(self, column_delimiter, has_header, default_source_label, default_target_label,
                              default_edge_label, column_header_map, column_number_map, request_setting,
                              file_path='', file_url='', content_type='', data_row_start=0, data_row_end=0,
                              batch_size=10000, input_mode='standard', mode='standard'):
        """

        Notes
        -----
        Special function reserved for ICBC acync kafka loading, please refer to load_table_edge().

        """
        config_param = {}
        data = {}
        url = self.root_url + "/async_kafka/graphs/" + self.graph_name + '/table/edge'
        if file_path is not '':
            if 'server://' in file_path:
                if has_header == 1:
                    if column_header_map.has_key('source_id') and column_header_map.has_key('target_id'):
                        data = {
                            "request_setting": request_setting,
                            "file_path": file_path[9:],
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            'default_source_label': default_source_label,
                            'default_target_label': default_target_label,
                            'default_edge_label': default_edge_label,
                            'column_header_map': column_header_map,
                            'content_type': content_type,
                            'data_row_start': data_row_start,
                            'data_row_end': data_row_end,
                            "input_mode": input_mode,
                            "mode": mode,
                            "batch_size": batch_size
                        }
                    else:
                        print
                        "column header for vertex_id is required"
                else:
                    if column_number_map.has_key('source_id'):
                        data = {
                            "request_setting": request_setting,
                            "file_path": file_path[9:],
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            'default_source_label': default_source_label,
                            'default_target_label': default_target_label,
                            'default_edge_label': default_edge_label,
                            'column_number_map': column_number_map,
                            'content_type': content_type,
                            'data_row_start': data_row_start,
                            'data_row_end': data_row_end,
                            "input_mode": input_mode,
                            "mode": mode,
                            "batch_size": batch_size
                        }
                config_param['param'] = json.dumps(data)
                return _post_query(url, config_param)
            else:
                if has_header == 1:
                    if column_header_map.has_key('source_id') and column_header_map.has_key('target_id'):
                        data = {
                            "request_setting": request_setting,
                            "file_path": file_path,
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            'default_source_label': default_source_label,
                            'default_target_label': default_target_label,
                            'default_edge_label': default_edge_label,
                            'column_header_map': column_header_map,
                            'content_type': content_type,
                            'data_row_start': data_row_start,
                            'data_row_end': data_row_end,
                            "input_mode": input_mode,
                            "mode": mode,
                            "batch_size": batch_size
                        }
                        config_param['param'] = json.dumps(data)
                        return _post_query_files(url, config_param, file_path)
                    else:
                        print
                        "column header for vertex_id is required"
                else:
                    if column_number_map.has_key('source_id'):
                        data = {
                            "request_setting": request_setting,
                            "file_path": file_path,
                            "column_delimiter": column_delimiter,
                            "has_header": has_header,
                            'default_source_label': default_source_label,
                            'default_target_label': default_target_label,
                            'default_edge_label': default_edge_label,
                            'column_number_map': column_number_map,
                            'content_type': content_type,
                            'data_row_start': data_row_start,
                            'data_row_end': data_row_end,
                            "input_mode": input_mode,
                            "mode": mode,
                            "batch_size": batch_size
                        }
                        config_param['param'] = json.dumps(data)
                        return _post_query_files(url, config_param, file_path)

        elif file_url is not '':
            if has_header == 1:
                if column_header_map.has_key('source_id') and column_header_map.has_key('target_id'):
                    data = {
                        "request_setting": request_setting,
                        "file_url": file_url,
                        "column_delimiter": column_delimiter,
                        "has_header": has_header,
                        'default_source_label': default_source_label,
                        'default_target_label': default_target_label,
                        'default_edge_label': default_edge_label,
                        'column_header_map': column_header_map,
                        'content_type': content_type,
                        'data_row_start': data_row_start,
                        'data_row_end': data_row_end,
                        "input_mode": input_mode,
                        "mode": mode,
                        "batch_size": batch_size
                    }
                else:
                    print
                    "column header for vertex_id is required"
            else:
                if column_number_map.has_key('source_id'):
                    data = {
                        "request_setting": request_setting,
                        "file_url": file_url,
                        "column_delimiter": column_delimiter,
                        "has_header": has_header,
                        'default_source_label': default_source_label,
                        'default_target_label': default_target_label,
                        'default_edge_label': default_edge_label,
                        'column_number_map': column_number_map,
                        'content_type': content_type,
                        'data_row_start': data_row_start,
                        'data_row_end': data_row_end,
                        "input_mode": input_mode,
                        "mode": mode,
                        "batch_size": batch_size
                    }
            config_param['param'] = json.dumps(data)
            return _post_query(url, config_param)
        else:
            pass

    def list_jobs(self):
        """
        List existing requests.

        Returns
        -------
            str
                .. code-block:: json

                    {
                        "jobs": [
                            {
                                "QUEUED": []
                            },
                            {
                                "RUNNING": []
                            },
                            {
                                "TERMINATED": []
                            },
                            {
                                "FINISHED": []
                            }
                        ]
                    }

        """
        url = self.root_url + "/requests"
        return _query(url)

    def clear_jobs(self, num_seconds):
        """
        Clear records of old requests.

        Parameters
        ----------
        num_seconds
            int
                num seconds since request is completed

        Returns
        -------
            str
                .. code-block:: json

                    {
                        "jobs_deleted": 0
                    }

        """
        url = self.root_url + "/requests"
        config_param = {}
        data = {"elapsed_seconds": num_seconds}
        config_param['param'] = json.dumps(data)
        return _delete_query(url, config_param)

    def job_status(self, job_id):
        """
        Get the status of a request.

        Parameters
        ----------
        job_id
            str
                the job_id that queried

        Returns
        -------
            str
                .. code-block:: json

                    {
                        "STATUS": "FINISHED",
                        "NEPS": 0,
                        "JOB_MESSAGE": "load edges finished",
                        "PID": 17,
                        "NE": 0,
                        "EXPIRATION": 1200,
                        "NVPS": 0,
                        "JSON_PARAMS": {
                            "job_id": "TEST",
                            "graph": "roy",
                            "input_file_path": "/opt/systemG/async-server/csv/TABLE_GROUP_20180301.csv",
                            "param": "{\"data_row_end\":0,\"target_id_col\":3,\"default_target_label\":\"1\",\"ignore_cols\":[],\"edge_label_col\":1,\"default_source_label\":\"1\",\"prop_type_col_map\":{\"4\":\"STRING\",\"5\":\"STRING\",\"6\":\"STRING\",\"7\":\"STRING\",\"8\":\"STRING\",\"9\":\"STRING\",\"10\":\"STRING\",\"11\":\"STRING\"},\"data_row_start\":0,\"source_id_col\":2,\"prop_name_col_map\":{\"4\":\"cino_source_name\",\"5\":\"cino_target_name\",\"6\":\"group_id\",\"7\":\"data_source\",\"8\":\"data_date\",\"9\":\"p_date\",\"10\":\"main_rela\",\"11\":\"eid_ui\"},\"batch_size\":10000,\"source_label_col\":0,\"default_edge_label\":\"_\",\"has_header\":0,\"target_label_col\":0,\"column_delimiter\":\",\",\"file_path\":\"/opt/systemG/graphdb-rest/app/csv/JOB_INFO/server-25--opt-systemG-async-server-csv-JOB_INFO-TEST:-opt-systemG-async-server-csv-TABLE_GROUP_20180301.csv_1.csv\",\"mode\":\"standard\"}",
                            "analytic": "load_edges",
                            "expiration": "1200",
                            "result_type": "DB_JSON",
                            "command_name": "start_async_kafka"
                        },
                        "JOB_NAME": "TEST:-opt-systemG-async-server-csv-TABLE_GROUP_20180301.csv_1",
                        "NV": 0
                    }

        """
        url = self.root_url + "/requests/" + job_id + "/status"
        return _query(url)

    def job_result(self, job_id):
        """
        Get the result of a request.

        Parameters
        ----------
        job_id
            str
                the job_id that queried

        Returns
        -------
            str
                .. code-block:: json

                    {
                        "status": "success",
                        "message": "job already executed#TEST:-opt-systemG-async-server-csv-TABLE_GROUP_20180301.csv_1#Job Scheduled:2018-11-09-19:18:48"
                    }


        """
        url = self.root_url + "/requests/" + job_id + "/result"
        return _query(url)

    def job_terminate(self, job_id):
        """
        Terminate a request.

        Parameters
        ----------
        job_id
            str
                the job_id that terminated

        Returns
        -------

        """
        url = self.root_url + "/requests/" + job_id
        return _delete_query(url, None)

    def system_status(self):
        """
        System performance monitoring.

        Returns
        -------
            str
                .. code-block:: json

                    {
                        "performance_monitor": {
                            "server_main": {
                                "mem %": "0.44",
                                "nthreads": "9",
                                "pid": "11",
                                "cpu %": "8.82",
                                "command ": "./server_main config.txt",
                                "file descriptors": "22",
                                "user": "root"
                            },
                            "nginx": {
                                "mem %": "0.05",
                                "nthreads": "1",
                                "pid": "24",
                                "cpu %": "0.00",
                                "command ": "nginx: worker process",
                                "file descriptors": "13",
                                "user": "nginx"
                            },
                            "Graphdb System Statistics": {
                                "CPU Load (%)": "30.00",
                                "Time Stamp": "2018-11-09-19:46:13",
                                "Memory Load (%)": "63.09",
                                "FileSys Load (%)": {
                                    "/dev/sda1": "69.64",
                                    "overlay": "69.64"
                                }
                            },
                            "uwsgi": {
                                "mem %": "0.88",
                                "nthreads": "1",
                                "pid": "28",
                                "cpu %": "0.00",
                                "command ": "/usr/local/bin/uwsgi --ini /etc/uwsgi/uwsgi.ini --die-on-term",
                                "file descriptors": "11",
                                "user": "root"
                            }
                        }
                    }

        """
        return _query(self.root_url + "/systems/status")

    def async_analytic(self, graph_name, analytic_name, life_span, job_id, **kwargs):
        """

        Notes
        -----
        Special function reserved for ICBC acync kafka analytics, please refer to run_analytics().

        """

        url = self.root_url + "/async_kafka/graphs/" + graph_name + "/analytics/" + analytic_name
        request_setting = {"async": 1, "life_span": life_span, "job_id": job_id}
        config_param = {}
        data = {
            "request_setting": request_setting
        }
        for key, value in kwargs.items():
            data[key] = value
        config_param['param'] = json.dumps(data)

        if analytic_name == "cycle/connected/composite":
            config_param['param'] = json.dumps({"request_setting": request_setting})
            for key, value in kwargs.items():
                config_param[key] = value
        logging.debug(config_param)
        return _post_query(url, config_param)

    def create_graph_via_plugin(self, graph_name, param=None):
        """

        Notes
        -----
        Special function reserved for ICBC acync kafka create, please refer to create_graph().

        """
        url = self.root_url + "/async_kafka/graphs/" + graph_name
        self.graph_name = graph_name  # set new created graph as current graph
        param_config = param
        if param:
            param_config = {}
            param_config['param'] = param
        return _post_query(url, param_config)

    def get_file(self, remote_file_name, local_file_name):
        data = {
            "remote_file_name": remote_file_name,
            "local_file_name": local_file_name
        }
        url = self.root_url + "/async/results/files/json"
        param_config = {"param": json.dumps(data)}
        return _post_query(url, param_config)

        # curl -X POST -F 'param={"remote_file_name":"server.cc", "local_file_name":"TMP/from_gdb_server.cc"}' http://localhost:5000/async/results/files/json

