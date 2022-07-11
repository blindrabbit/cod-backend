
import gnocchiclient
from gnocchiclient.exceptions import ArchivePolicyNotFound, MetricNotFound, NamedMetricAlreadyExists, ResourceTypeAlreadyExists, ResourceTypeNotFound
from gnocchiclient.v1 import client, metric, resource
import datetime
import pandas as pd
from flask import json

# Class to get measures from Gnocchi
class Gnocchi():
    def __init__(self, session):
        # param verify : ignore self-signed certificate
        self.gnocchi_client = client.Client(session=session)

    # check if resource_type exists
    def get_resource_type(self,name):
        try:
            return self.gnocchi_client.resource_type.get(name)
        except ResourceTypeNotFound:
            return False

    # check if resource_type exists
    def get_check_resource_type(self,name):
        try:
            self.gnocchi_client.resource_type.get(name)
            return True
        except ResourceTypeNotFound:
            return False
    
    def set_create_resource_type(self,name):
        try:
            self.resource_type = {"name": name,'attributes':{"host":{"type": "string", "min_length": 0, "max_length": 255,"required": True}}}
            self.gnocchi_client.resource_type.create(self.resource_type)
        except ResourceTypeAlreadyExists:
            return "ResourceTypeJaExiste"
    
    #Create resource
    def set_create_resource(self,resource_type,resource_name):
        try:
            print ("set_create_resource")
            self.resource=self.gnocchi_client.resource.create(resource_type,{"host":"","id":resource_name})
        except Exception as e:
        #except ResourceTypeNotFound:
            print (e)
            return "ResourceTypeNotFound"

    #check if exists resource
    def get_resource(self,name):
        try:
            resource=self.gnocchi_client.resource.search(resource_type=name,limit=1)
            print (resource)
            #return True
        except ResourceTypeNotFound:
            return False

    #return resource id
    def get_resource_id(self,name):
        try:
            self.resource=self.gnocchi_client.resource.search(resource_type=name,limit=1,details=True)
            if(len(self.resource))==0:
                return -1
            else:
                return self.resource[0]["id"]
        except ResourceTypeNotFound:
            return ""

    #Check if metris to exists and return this
    def get_metric(self,name,resource_id):
        try:
            print ("consultando metrica usando resource_id")
            print (resource_id)
            print(name)
            return self.gnocchi_client.metric.get(name,resource_id)
        except MetricNotFound:
            return ""

    #Check if metris to exists and return the id
    def get_metric_id(self,name,resource_id):
        try:
            self.resp= self.gnocchi_client.metric.get(name,resource_id)
            return self.resp.get('id')
        except MetricNotFound:
            return ""

    #To create metric
    def set_create_metric(self,name,archive_policy,resource_id,unit):
        try:
            self.create_metric=self.gnocchi_client.metric._create_new(name,archive_policy,resource_id,unit)
        except NamedMetricAlreadyExists:
            return "MetricaJaExiste"

    #To create archive-policy
    def set_create_archive_policy(self,name):      
        try:
            self.create_metric=self.gnocchi_client.archive_policy.create({'name': name, 'back_window': 0, 'definition': [{'timespan': '60 days, 0:00:00', 'granularity': '0:01:00', 'points': 86400}], 'aggregation_methods': ['mean', 'sum', 'min', 'std', 'count', 'max']})
        except:
            return "NoAccess"

    #To get archive-policy and reply True  our False if archive-policy exist
    def get_archive_policy(self,name):
        try:
            archive_id=self.gnocchi_client.archive_policy.get(name)
            #print(archive_id)
            #print(len(archive_id))
            if(len(archive_id))==0:
                return False
            else:
                return True
        except ArchivePolicyNotFound:
            return "ArquivePolicyNotFound"
    
    #To clean measures of all metrics
    #def set_clean_all_measures_metrics

    #To delete all metrics in plao
    #def set_delete_all_metrics


    #add measures in metrics
    def set_add_measures_metric(self,id,value):
        #print ("id da metrica in set_add_measures_metric: "+id)
        self.timestamp = str(datetime.now().utcnow()).split('.')[0]
        self.addmeasures=self.gnocchi_client.metric.add_measures(id, [{'timestamp': self.timestamp,'value': value}])


    def get_metric_cpu_utilization(self, resource_id, granularity, vcpus, start, stop):
        # Divide per vcpus (OpenStack sum all processors times)
        operations = "(/ (* (/ (metric cpu rate:mean) "+str(granularity*1000000000.0)+") 100) "+str(vcpus)+")"
        # print(operations)
        meters = self.gnocchi_client.aggregates.fetch(operations,
                                                    # resource_type='generic',
                                                    search="id="+resource_id,
                                                    start=start,
                                                    stop=stop,
                                                    granularity=granularity)


    #If dont data, return -1, else return data
    def get_measure(self, name_metric, resource_id, aggregation, granularity, start, stop):
        #metric_id=self.get_metric_id(name_metric,resource_id)
        #print(metric_id)
        dados=self.gnocchi_client.metric.get_measures(name_metric,start,stop, aggregation, granularity,resource_id)
        #if len(dados) != 0:     
        #    return dados[0][2]
        #return -1
        df = pd.DataFrame(dados, columns =['timestamp', 'granularity', 'value'])
        print("\n")
        print(df.head())
        return (df)

    #If dont data, return -1, else return data
    def get_last_measure(self, name_metric, resource_id, aggregation, granularity, start, stop):
        
        df3 =(self.gnocchi_client.metric.list())
        df4 = pd.DataFrame(df3)
        # print(df4.to_csv("teste.txt"))

        print(str(name_metric)+"-"+str(resource_id)+"-"+ str(aggregation)+"-"+str(granularity)+"-"+str(start)+"-"+str(stop))
        dados=self.gnocchi_client.metric.get_measures(name_metric,start,stop, aggregation, granularity, resource_id)
        df = pd.DataFrame(dados, columns =['timestamp', 'granularity', ''])
        print(df)
        if (df.__len__() == 0):
            return -1
        last_row = df.iloc[-1,2] #colect the last register
        return (last_row)

    #If dont data, return -1, else return data
    def get_last_measure_Date(self, name_metric, resource_id, aggregation, granularity, start, stop):
        try:
            dados=self.gnocchi_client.metric.get_measures(name_metric,start,stop, aggregation, granularity,resource_id)
            df = pd.DataFrame(dados, columns =['timestamp', 'granularity', 'value'])
            #df = pd.DataFrame(dados, columns =['timestamp', 'granularity', ''])
            if (df.__len__() == 0):
                return -1
            df2=json.dumps(json.loads(df.to_json(orient = 'records')), indent=2)
            return (df2)            
        except:
            return -1
