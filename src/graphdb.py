# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 18:09:12 2020

@author: Wayne
"""

from . import client_gdb as client
import ast
import json

#Establish connection to the rest server

GRAPHDB_HOST = "http://3.14.253.94" # host ip
GRAPHDB_PORT = "8012" # port
grest_host = GRAPHDB_HOST + ":" + GRAPHDB_PORT
g = client.gc(host=grest_host) # initialize the graphdb obj
print(g.set_current_graph("TaiwanComputerIndustry"))


def get_products(comp_name):
    json_str = {
        "vertices": [{"id": comp_name, "label": "公司"}],
        "depth": 1,
        "edge_direction": "out"
    }
    request_body = {"param": json.dumps(json_str).replace('\\"', '"')}
    res = g.run_analytics(analytic_name="bfs", request_body=request_body)
    data = ast.literal_eval(res.decode("UTF-8"))
    products = [v for v in data['data']['vertices'] if v['id']!=comp_name]
    return products

def get_companies_up(prod_name):
    json_str = {
        "vertices": [{"id": prod_name, "label": "零件"}],
        "depth": 1,
        "edge_direction": "in"
    }
    request_body = {"param": json.dumps(json_str).replace('\\"', '"')}
    res = g.run_analytics(analytic_name="bfs", request_body=request_body)
    data = ast.literal_eval(res.decode("UTF-8"))
    comps = [v['id'] for v in data['data']['vertices'] if v['label']=='公司']
    return comps

def get_companies_down(prod_name):
    json_str = {
        "vertices": [{"id": prod_name, "label": "產品"}],
        "depth": 1,
        "edge_direction": "in"
    }
    request_body = {"param": json.dumps(json_str).replace('\\"', '"')}
    res = g.run_analytics(analytic_name="bfs", request_body=request_body)
    data = ast.literal_eval(res.decode("UTF-8"))
    comps = [v['id'] for v in data['data']['vertices'] if v['label']=='公司']
    return comps

def get_competitor(comp_name):
    products = get_products(comp_name)
    comp_list = set()
    for p in products:
        if p['label'] == '產品':
            comp_list.update(get_companies_down(p['id']))
        else:
            comp_list.update(get_companies_up(p['id']))
    return list(comp_list)
    
def get_upstream(comp_name):
    products = get_products(comp_name)
    upstreamproduct = set()
    comp_list = set()
    for p in products:
        if p['label'] == '產品':
            json_str = {
                "vertices": [{"id": p['id'], "label": "產品"}],
                "depth": 1,
                "edge_direction": "out"
            }
            request_body = {"param": json.dumps(json_str).replace('\\"', '"')}
            res = g.run_analytics(analytic_name="bfs", request_body=request_body)
            data = ast.literal_eval(res.decode("UTF-8"))
            upstreamproduct.update([v['id'] for v in data['data']['vertices'] if v['label']=='零件'])
    for p in upstreamproduct:
        comp_list.update(get_companies_up(p))
    return list(comp_list)

def get_downstream(comp_name):
    products = get_products(comp_name)
    downstreamproduct = set()
    comp_list = set()
    for p in products:
        if p['label'] == '零件':
            json_str = {
                "vertices": [{"id": p['id'], "label": "零件"}],
                "depth": 1,
                "edge_direction": "in"
            }
            request_body = {"param": json.dumps(json_str).replace('\\"', '"')}
            res = g.run_analytics(analytic_name="bfs", request_body=request_body)
            data = ast.literal_eval(res.decode("UTF-8"))
            downstreamproduct.update([v['id'] for v in data['data']['vertices'] if v['label']=='產品'])
    for p in downstreamproduct:
        comp_list.update(get_companies_down(p))
    return list(comp_list)

def get_egonet(comp_name):
    res = g.get_egonet(vertex_id=comp_name, vertex_label="公司", depth = 2)
    data = ast.literal_eval(res.decode("UTF-8"))['data']
    data['nodes'] = data.pop('vertices')
    data['links'] = data.pop('edges')
    for i,n in enumerate(data['nodes']):
        data['nodes'][i].pop('properties')
        if "\\" in data['nodes'][i]['id']:
            data['nodes'][i]['id'] = data['nodes'][i]['id'].replace('\\',',')
        data['nodes'][i]['name'] = data['nodes'][i]['id']
    for i,l in enumerate(data['links']):
        if "\\" in data['links'][i]['source_id']:
            data['links'][i]['source_id'] = data['links'][i]['source_id'].replace('\\',',')
        if "\\" in data['links'][i]['target_id']:
            data['links'][i]['target_id'] = data['links'][i]['target_id'].replace('\\',',')
#        if l['label'] != '生產':
#            data['links'].pop(i)
#            continue
        data['links'][i] = {'source':l['source_id'], 'target':l['target_id'], 'type':l['label']}
    
    return data

#json_str = {
#    "vertices": [{"id": "華碩", "label": "公司"}],
#    "depth": 1,
#    "edge_direction": "out"
#}
#
#request_body = dict()
#request_body["param"] = json.dumps(json_str).replace('\\"', '"')
#
#res = g.run_analytics(analytic_name="bfs", request_body=request_body)
#
##
##res = g.get_egonet(vertex_id="華碩", vertex_label="公司", depth = 1)
#data = ast.literal_eval(res.decode("UTF-8"))
#p = get_competitor(g, '華碩')



