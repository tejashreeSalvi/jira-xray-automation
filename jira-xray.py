import requests
import urllib3
import time
urllib3.disable_warnings()

JIRA_XRAY_URL = "https://xray.cloud.getxray.app/api/v2/graphql"

#3 sdz creds
headers = {
        #   "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer <<DESTINATION_TOKEN>>"
    }


def get_nvs_test_plans(project_name):
    
    ''' Test plans '''
    
    ## nvs creds
    headers = {
        #   "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer <<SOURCE_TOKEN>>"
    }
    
    query_get_test_plans = f"""
    {{
        getTestPlans(jql: "project = '{project_name}'", limit: 10) {{
            total
            results {{
                issueId
                tests(limit: 10) {{
                    total
                    results {{
                        jira(fields: ["key"])
                    }}
                }}
                testExecutions(limit: 10) {{
                    total
                    results {{
                        jira(fields: ["key"])
                    }}
                }}
                jira(fields: ["key"])
            }}
        }}
    }}
    """
    
    response = requests.post(JIRA_XRAY_URL, json={'query': query_get_test_plans}, headers=headers, verify=False)
    with open("testplan.json", "a") as file:
        file.write(response.text)
    if response.status_code == 200:
        return response.json()['data']['getTestPlans']['results']
    else:
        return []
    
# print(get_nvs_test_plans('SANITY'))

def get_test_plan_id(jira_key):
    
    test_plan = f"""
        {{
        getTestPlans(jql: "issuekey IN ('{jira_key}')", limit: 100) {{
                results {{
                    issueId
                    jira(fields: ["key"])
                }}
            }}
        }}
    """
    response = requests.post(JIRA_XRAY_URL, json={'query': test_plan}, headers=headers, verify=False)
    with open("test_plan_id.json", "a") as file:
        file.write(response.text)
    if 'results' in response.json()['data']['getTestPlans'] and len(response.json()['data']['getTestPlans']['results']) and response.status_code == 200:
        return response.json()['data']['getTestPlans']['results']
    else:
        return []
    
# get_test_plan_id('SIGSE-21185')

def get_tests_issue_id(jira_key):
    
    '''get tests issue id'''
    
    fetch_tests = f"""
        {{
            getTests(jql: "issuekey IN ('{jira_key}')", limit: 100) {{
                    results {{
                        issueId
                        jira(fields: ["key"])
                    }}
                }}
        }}
    """
    response = requests.post(JIRA_XRAY_URL, json={'query': fetch_tests}, headers=headers, verify=False)
    with open("tests_id.json", "a") as file:
        file.write(response.text)
    if 'results' in response.json()['data']['getTests'] and len(response.json()['data']['getTests']['results']) and response.status_code == 200:
        return response.json()['data']['getTests']['results']
    else:
        return []

# get_tests_issue_id('SIGSE-21207')
def get_test_execution_id(jira_key):
    
    ''' get test execution id from sandoz '''
    
    sdz_test_execution = f"""{{
        getTestExecutions(jql: "issuekey IN ('{jira_key}')", limit: 100) {{
                total
                results {{
                    issueId
                    jira(fields: ["key"])
                }}
            }}
    }}
    """
    response = requests.post(JIRA_XRAY_URL, json={'query': sdz_test_execution}, headers=headers, verify=False)
    with open("test_execution_id.json", "a") as file:
        file.write(response.text)
    if 'results' in response.json()['data']['getTestExecutions'] and len(response.json()['data']['getTestExecutions']['results']) and response.status_code == 200:
        return response.json()['data']['getTestExecutions']['results']
    else:
        return []
    

def get_nvs_test_execution_id(jira_key):
    
    '''get test execution id'''
    # NVS header..
    headers = {
        #   "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer <<SOURCE_TOKEN>>"
    }
    
    fetch_test_execution = f"""
    {{
            getTestExecutions(jql: "issuekey IN ('{jira_key}')", limit: 100) {{
                total
                results {{
                    tests(limit: 10) {{
                        total
                        results {{
                            issueId
                            testType {{
                                name
                            }}
                        jira(fields: ["key"])
                        }}
                    }}
                    testRuns(limit: 10) {{
                        total
                        results {{
                            id
                            startedOn
                            finishedOn
                            executedById
                            status {{
                                name
                            }}
                            test {{
                                jira(fields: ["key"]) 
                            }}
                            steps {{
                                action
                                data
                                result
                                attachments {{
                                    id
                                    filename
                                }}
                                status {{
                                    name
                                }}
                            }}
                        }}
                    }}
                    jira(fields: ["key"])
                }}
            }}
        }}
    """
    
    
    response = requests.post(JIRA_XRAY_URL, json={'query': fetch_test_execution}, headers=headers, verify=False)
    with open("test_execution_id.json", "a") as file:
        file.write(response.text)
    if 'results' in response.json()['data']['getTestExecutions'] and len(response.json()['data']['getTestExecutions']['results']) and response.status_code == 200:
        return response.json()['data']['getTestExecutions']['results']
    else:
        return []

get_nvs_test_execution_id('SIGSE-20933')

# ==========================================================================================================

def add_tests_to_test_plan(testIssueIds, issueId):
    """add test to test plan

    Returns:
        _type_: _description_
    """
    # Convert testIssueIds to a list of double-quoted strings
    quoted_test_ids = [f'"{test_id}"' for test_id in testIssueIds]

    # Remove single quotes from the quoted strings
    quoted_test_ids = [quoted_test_id.replace("'", "") for quoted_test_id in quoted_test_ids]

    add_test_to_test_plan = f"""
        mutation {{
            addTestsToTestPlan(
                issueId: "{issueId}",
                testIssueIds: [{', '.join(quoted_test_ids)}]
            ) {{
                addedTests
            }}
        }}
    """
    
    print("add_test_to_test_plan:", add_test_to_test_plan)
    response = requests.post(JIRA_XRAY_URL, json={'query': add_test_to_test_plan}, headers=headers, verify=False)
    with open("add_test_to_test_plan.json", "a") as file:
        file.write(response.text)
    print("Response of add_test_to_test_plan:", response.text, response.status_code)
    time.sleep(5)
    if response.status_code == 200:
        return response.json()
    
def add_testexecution_to_test_plan(testExecutionIssueId, issueId):
    """ Add the test execution to the test plan 

    Args:
        testExecutionIssueId (_type_): _description_
        issueId (bool): _description_

    Returns:
        _type_: _description_
    """
    print("testExecutionIssueId:", testExecutionIssueId)
    quoted_test_ids = [f'"{test_id}"' for test_id in testExecutionIssueId]
    
    # Remove single quotes from the quoted strings
    quoted_test_ids = [quoted_test_id.replace("'", "") for quoted_test_id in quoted_test_ids]

    add_testexec_to_test_plan = f"""
        mutation {{
            addTestExecutionsToTestPlan(
                issueId: "{issueId}",
                testExecIssueIds: [{', '.join(quoted_test_ids)}]
            ) {{
                addedTestExecutions
            }}
        }}
    """
    
    print("add_testexec_to_test_plan:", add_testexec_to_test_plan)
    response = requests.post(JIRA_XRAY_URL, json={'query': add_testexec_to_test_plan}, headers=headers, verify=False)
    with open("add_testexecution_to_test_plan.json", "a") as file:
        file.write(response.text)
    print("Response of add test exec to test plan:", response.text, response.status_code)
    time.sleep(5)
    if response.status_code == 200:
        return response.json()
    else:
        return []

# ========================================

# Test runs 

def get_test_run_id(testIssueId, testExecIssueId):
    
    test_run = f"""{{
        getTestRun( testIssueId: "{testIssueId}", testExecIssueId: "{testExecIssueId}") {{
            id
            status {{
                name
                color
                description
            }}
            gherkin
            examples {{
                id
                status {{
                    name
                    color
                    description
                }}
            }}
        }}
    }}
    """
    response = requests.post(JIRA_XRAY_URL, json={'query': test_run}, headers=headers, verify=False)
    with open("get_test_runs.json", "w") as file:
        file.write(response.text)
    if response.status_code == 200:
        return response.json()['data']['getTestRun']
    else:
        return []

# get_test_execution_id('SIGSE-20933')
# get_tests_issue_id('SIGSE-20927')
get_test_run_id('87751', '91607')


def update_test_run_status(testRunId, status):
    """update test run status

    Returns:
        _type_: _description_
    """
    update_test_run = f"""
        mutation {{
            updateTestRun(
                id: "{testRunId}",
                status: "{status}"
            )
        }}
    """
    response = requests.post(JIRA_XRAY_URL, json={'query': update_test_run}, headers=headers, verify=False)
    with open("update_test_run.json", "w") as file:
        file.write(response.text)
    if response.status_code == 200:
        return response.json()
    else:
        return []

# ==========================================================================================================
def initiate_jira_xray_sync(project_name):
    """
    Initiate the Jira Xray Process.
    Pass the parameters project_name.
    """    
    
    test_plans_list = get_nvs_test_plans(project_name)
    for test_plans in test_plans_list:
        
        test_plan_key = test_plans['jira']['key']
        
        # Test plan issue id
        test_plan_id_resp = get_test_plan_id(test_plan_key)
        
        test_plan_id = test_plan_id_resp[0]['issueId']
            
        print("Test Plan ID:", test_plan_id)
            
        # Tests issue ids
        tests_issue_ids = []
        for tests in test_plans['tests']['results']:
            
            test_key = tests['jira']['key']

            # Tests issue id
            tests_id_resp = get_tests_issue_id(test_key)
            
            tests_issue_ids.append(tests_id_resp[0]['issueId'])
                
        
        print("Tests Issue ID:", tests_issue_ids)
        
        test_execution_issue_ids = []  
        for testexecution in test_plans['testExecutions']['results']:
            
            test_execution_key = testexecution['jira']['key']
            
            print("Test Execution Key:", test_execution_key)
            
            # Test execution issue id
            test_execution_id_resp = get_test_execution_id(test_execution_key)
            
            
            test_execution_id = test_execution_id_resp[0]['issueId']
            test_execution_issue_ids.append(test_execution_id)
                
            # test execution for test runs...
            test_executions_nvs = get_nvs_test_execution_id(test_execution_key)
            
            for test_execution in test_executions_nvs:
                
                nvs_test_execution_issue_id = test_execution['jira']['key']
                print("NVS Test Execution Issue ID:", nvs_test_execution_issue_id)
                
                # get the issue id for the test execution
                nvstestExecIssueIds = get_test_execution_id(nvs_test_execution_issue_id)
                if nvstestExecIssueIds:
                    
                    testExecIssueIds = nvstestExecIssueIds[0]['issueId']
                
                    for tests in test_execution['tests']['results']:
                        test_issue_id = tests['jira']['key']
                        print("Test  ID:", test_issue_id)
                        
                        # get the tests issue id
                        testIssueIds = get_tests_issue_id(test_issue_id)[0]['issueId']
                        
                        test_run_resp = get_test_run_id(testIssueIds, testExecIssueIds)
                        
                        test_run_id = test_run_resp['id']
                        print("Test Run ID:", test_run_id)
                        test_run_status = test_run_resp['status']['name']
                        print("Test Run Status:", test_run_status)
                        
                        
                        # not sure we can use this function here or later we need to modfiy it.
                        
                        update_test_run_status(test_run_id, test_run_status)
                    
            print("Test Runs updated successfully...")
            

            print("Test Execution Issue ID:", test_execution_issue_ids)
            
        
        # add tests to test plan
        add_tests_to_test_plan(tests_issue_ids, test_plan_id)
        
        # add test execution to test plan
        add_testexecution_to_test_plan(test_execution_issue_ids, test_plan_id)
        
        print("Test Plan Synced Successfully")

print("Initiating Jira Xray Sync...")
initiate_jira_xray_sync('F1DDM')
print("Jira Xray Sync Completed...")
            
            
            
            
        
            
            
        
        
        
