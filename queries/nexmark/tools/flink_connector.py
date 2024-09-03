import requests
import logging
import json
from pprint import pprint
import math

class FlinkException(Exception):
    pass


class Flink:
    '''
    Flink REST API connector.

    TODO: Parse the response and return a dict.
    '''

    def __init__(self, endpoint="http://localhost:8081"):
        self._endpoint = endpoint

    def get_endpoint(self):
        return self._endpoint
    
    def set_endpoint(self, endpoint):
        self._endpoint = endpoint

    def get_cluster(self):
        '''
        Show cluster information.

        `/cluster`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#cluster

        '''        
        url = "{}/taskmanagers/10.0.0.235:33307-153094/logs".format(self._endpoint)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def list_jobs(self):
        '''
        List all jobs.

        `/jobs`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs

        '''
        url = "{}/jobs".format(self._endpoint)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_job_agg_metrics(self):
        '''
        Get job aggregated metrics.

        `/jobs/metrics`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#job-metrics

        '''
        url = "{}/jobs/metrics".format(self._endpoint)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_job_details(self, jobid):
        '''
        Get job details by ID

        `/jobs/{jobid}`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#job-details

        '''
        url = "{}/jobs/{}".format(self._endpoint, jobid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_job_metrics(self, jobid):
        '''
        Get job metrics by ID

        `/jobs/{jobid}/metrics`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-metrics

        '''
        url = "{}/jobs/{}/metrics".format(self._endpoint, jobid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_job_plan(self, jobid):
        '''
        Get job plan by ID

        `/jobs/{jobid}/plan`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-plan

        '''
        url = "{}/jobs/{}/plan".format(self._endpoint, jobid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_upstream_id(self, job_id, task_id):
        '''
        Get ID of upstream operator
        '''
        res=[]
        job_plan = self.get_job_plan(job_id)
        opr_list=job_plan['plan']['nodes']
        for oprs in opr_list:
            if(oprs['id']==task_id):
                if('inputs' in oprs.keys()):
                    for input_id in oprs['inputs']:
                        res.append(input_id['id'])
        return(res)

    def get_task_status(self, jobid, taskid):
        '''
        Get task status by ID

        `/jobs/:jobid/vertices/:vertexid`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-tasks-taskid

        '''
        url = "{}/jobs/{}/vertices/{}".format(self._endpoint, jobid, taskid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_task_backpressure(self, jobid, taskid):
        '''
        Get task backpressure by ID

        `/jobs/:jobid/vertices/:vertexid/backpressure`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-tasks-taskid-backpressure

        '''
        url = "{}/jobs/{}/vertices/{}/backpressure".format(self._endpoint, jobid, taskid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_task_metrics(self, jobid, taskid):
        '''
        Get task metrics by ID

        `/jobs/:jobid/vertices/:vertexid/metrics`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-tasks-taskid-metrics

        '''
        url = "{}/jobs/{}/vertices/{}/metrics".format(self._endpoint, jobid, taskid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_task_metrics_details(self, jobid, taskid, fieldid):
        '''
        Get task metrics by ID

        `/jobs/:jobid/vertices/:vertexid/metrics`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-tasks-taskid-metrics

        '''
        url = "{}/jobs/{}/vertices/{}/metrics?get={}".format(self._endpoint, jobid, taskid, fieldid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_subtask_metrics(self, jobid, taskid):
        '''
        Get subtask metrics by ID

        `/jobs/:jobid/vertices/:vertexid/subtasks/metrics`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-tasks-taskid-metrics-subtaskid

        '''
        url = "{}/jobs/{}/vertices/{}/subtasks/metrics".format(
            self._endpoint, jobid, taskid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_subtask_metrics_details(self, jobid, taskid, subtaskid, fieldid):
        '''
        Get subtask metrics by ID

        `/jobs/:jobid/vertices/:vertexid/subtasks/metrics`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-tasks-taskid-metrics-subtaskid

        '''
        url = "{}/jobs/{}/vertices/{}/subtasks/metrics?get={}".format(
            self._endpoint, jobid, taskid, subtaskid, fieldid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


def _test():
    flink = Flink(endpoint="http://192.168.1.104:8081/")
    print("Endpoint is:", flink.get_endpoint())
    jobs = flink.list_jobs()
    print("Jobs:", jobs)
    print("Job aggregated metrics:", flink.get_job_agg_metrics())
    for job in jobs['jobs']:
        job_id = job['id']
        print("Job ID:", job_id)
        print("Job details:")
        job_details = flink.get_job_details(job_id)
        pprint(job_details)
        print("Job metrics:")
        pprint(flink.get_job_metrics(job_id))
        print("Job plan:")
        pprint(flink.get_job_plan(job_id))
        for task in job_details['vertices']:
            task_id = task['id']
            print("Task ID:", task_id)
            print("Task status:")
            pprint(flink.get_task_status(job_id, task_id))
            print("Task backpressure:")
            pprint(flink.get_task_backpressure(job_id, task_id))
            print("Task metrics:")
            pprint(flink.get_task_metrics(job_id, task_id))
            print("Task Metrics Details:")
            pprint(flink.get_task_metrics_details(
                job_id, task_id, '0.numRecordsInPerSecond'))
            print("Subtask metrics:")
            pprint(flink.get_subtask_metrics(job_id, task_id))


def _testq5():
    metricset=dict()
    flink = Flink(endpoint="http://192.168.1.104:8081/")
    print("Endpoint is:", flink.get_endpoint())
    jobs = flink.list_jobs()
    print("Jobs:", jobs)
    for job in jobs['jobs']:
        job_id = job['id']
        print("Job ID:", job_id)
        job_details = flink.get_job_details(job_id)
        print("Job plan:")
        job_plan=flink.get_job_plan(job_id)
        pprint(job_plan)
        _task_metrics=dict()
        for task in job_details['vertices']:
            task_id = task['id']
            _task_metrics[task_id]=dict()
            task_status=flink.get_task_status(job_id, task_id)
            subtask_list=task_status['subtasks']
            _task_metrics[task_id]['name']=task_status['name']
            _task_metrics[task_id]['task_id']=task_id
            _task_metrics[task_id]['parallelism']=task_status['parallelism']
            _task_metrics[task_id]['num_subtasks']=len(subtask_list)
            _task_metrics[task_id]['upstream_task_id']=flink.get_upstream_id(job_id, task_id)
            _task_metrics[task_id]['subtasks']=dict()
            for st in subtask_list:
                stid=st['subtask']
                _task_metrics[task_id]['subtasks'][stid]=dict()
                _task_metrics[task_id]['subtasks'][stid]['host']=st['host']
                _task_metrics[task_id]['subtasks'][stid]['taskmanager-id']=st['taskmanager-id']
                _task_metrics[task_id]['subtasks'][stid]['numRecordsInPerSecond']=float(flink.get_task_metrics_details(job_id, task_id, str(stid)+'.numRecordsInPerSecond')[0]['value'])
                _task_metrics[task_id]['subtasks'][stid]['numRecordsOutPerSecond']=float(flink.get_task_metrics_details(job_id, task_id, str(stid)+'.numRecordsOutPerSecond')[0]['value'])
                _task_metrics[task_id]['subtasks'][stid]['busyTimeMsPerSecond']=max(float(flink.get_task_metrics_details(job_id, task_id, str(stid)+'.busyTimeMsPerSecond')[0]['value']), 0.0001)
                _task_metrics[task_id]['subtasks'][stid]['backPressuredTimeMsPerSecond']=float(flink.get_task_metrics_details(job_id, task_id, str(stid)+'.backPressuredTimeMsPerSecond')[0]['value'])
                _task_metrics[task_id]['subtasks'][stid]['idleTimeMsPerSecond']=float(flink.get_task_metrics_details(job_id, task_id, str(stid)+'.idleTimeMsPerSecond')[0]['value'])
                _task_metrics[task_id]['subtasks'][stid]['selectivity']=_task_metrics[task_id]['subtasks'][stid]['numRecordsOutPerSecond'] / max(_task_metrics[task_id]['subtasks'][stid]['numRecordsInPerSecond'], 1)
        metricset[job_id]=_task_metrics

    for jid in metricset.keys():
        for tid in metricset[jid].keys():
            for i in metricset[jid][tid]['subtasks'].keys():
                uid=metricset[jid][tid]['upstream_task_id']
                if(len(uid)==0):                                                   # for source operator:
                    metricset[jid][tid]['subtasks'][i]['ibatch']=2000              #    ibatch := num of records in the output buffer of source opr. currently hard coded
                    metricset[jid][tid]['subtasks'][i]['true_output_rate']=2000    #    true_output_rate := actual source rate
                    metricset[jid][tid]['subtasks'][i]['true_input_rate']=1        #    true_input_rate does not make sense for source
                    metricset[jid][tid]['subtasks'][i]['selectivity']=1            #    selectivity does not make sense for source
                else:
                    metricset[jid][tid]['subtasks'][i]['true_input_rate'] = (metricset[jid][tid]['subtasks'][i]['numRecordsInPerSecond']) / ( metricset[jid][tid]['subtasks'][i]['busyTimeMsPerSecond']/1000 )
                    metricset[jid][tid]['subtasks'][i]['true_output_rate'] = (metricset[jid][tid]['subtasks'][i]['numRecordsOutPerSecond']) / ( metricset[jid][tid]['subtasks'][i]['busyTimeMsPerSecond']/1000 )


    for jid in metricset.keys():
        for tid in metricset[jid].keys():
            for i in metricset[jid][tid]['subtasks'].keys():                       # TODO: iBatch is not accurate for now
                uid=metricset[jid][tid]['upstream_task_id']                        # iBatch[i]=iBatch[j]*selectivity[j], where j is the upstream operator of i
                if(len(uid)>0):
                    #jid_uid=jid_tid.split('.')[0]+'.'+uid[0]
                    metricset[jid][tid]['subtasks'][i]['ibatch']=metricset[jid][uid[0]]['subtasks'][0]['ibatch']*metricset[jid][uid[0]]['subtasks'][0]['selectivity']    # num of records in a batch of input for opr i

    print('=============================================================================================')
    for jid in metricset.keys():
        for tid in metricset[jid].keys():
            print('\n----------------------------------------------')
            print(jid,tid)
            uid=metricset[jid][tid]['upstream_task_id']
            if(len(uid)>0):
                #jid_uid=jid_tid.split('.')[0]+'.'+uid[0]
                t_proc_max=-1
                for i in metricset[jid][tid]['subtasks'].keys():
                    t_proc=metricset[jid][tid]['subtasks'][i]['ibatch'] / metricset[jid][tid]['subtasks'][i]['true_input_rate'] *1000    # process time (ms)
                    metricset[jid][tid]['subtasks'][i]['t_proc_ms']=t_proc
            for st in metricset[jid][tid].keys():
                print(st, '==', json.dumps(metricset[jid][tid][st], indent=4))

    print('=============================================================================================')
    print(metricset)

if __name__ == "__main__":
    _testq5()
