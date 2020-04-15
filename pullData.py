from sqlalchemy import create_engine, MetaData, Table
import json
import pdb

#Edited by Nick on 4/24/20, now dumps everything to a JSON file
#Edited by Guillaume and Dan on 1/26/2018, should work now
#This version was moved to psiturk/Andrew
#This creates a csv file named 'ramp'. Change at line 67 if you want it to be named something else. Will deposit in w/e directory this is in.
def main(table_name, database_name = "participants.db"):

    ##### ~~~~~ BEGIN Interact with SQL database #######
    db_url = "sqlite:///" + database_name
    data_column_name = 'datastring'
    print(db_url)

    # boilerplace sqlalchemy setup
    engine = create_engine(db_url)
    metadata = MetaData()
    metadata.bind = engine

    table = Table(table_name, metadata, autoload=True)
    # make a query and loop through
    s = table.select()
    rows = s.execute()

    data = []
    #status codes of subjects who completed experiment
    statuses = [3,4,5,7]
    # if you have workers you wish to exclude, add them here
    exclude = []
    for row in rows:
        # only use subjects who completed experiment and aren't excluded
        #if row['uniqueid'] not in exclude:
        if row['status'] in statuses and row['uniqueid'] not in exclude:
            data.append(row[data_column_name])

    ##### ~~~~~ END Interact with SQL database #######

    # Now we have all participant datastrings in a list.

    # first we'll pull any questionaires we've asked the subject to complete:
    question_data = []
    for part in data: # part == particpant
        _q = json.loads(part)['questiondata']
        _q['assignmentId'] = json.loads(part)['assignmentId']
        _q['workerId'] = json.loads(part)['workerId']
        _q['hitId'] = json.loads(part)['hitId']
        _q['bonus'] = json.loads(part)['bonus']
        question_data.append(_q)

    ### N.B. we can also get the event data (i.e. screen resizing) via json.loads(part)['eventdata]

    # questions = {json.loads(part)['workerId']: json.loads(part)['questiondata'] for part in data}
    # questions = [pd.DataFrame(value, index=[key]) for key, value in questions.items()]

    # next, we will pull the trial-by-trial data
    # and make it a bit easier to work with:

    # parse each participant's datastring as json object
    # and take the 'data' sub-object
    data = [json.loads(part)['data'] for part in data]

    # insert uniqueid field into trialdata in case it wasn't added
    # in experiment:
    for part in data:
        for record in part:
            bad_record = (not isinstance(record['trialdata'],dict))
            if bad_record:
                # print("Bad record['trialdata']:", record['trialdata'])
                record['trialdata'] = {record['trialdata']: record['uniqueid']}
                next
            else:
                record['trialdata']['uniqueid'] = record['uniqueid']
                # flatten nested list so we just have a list of the trialdata recorded
                # each time psiturk.recordTrialData(trialdata) was called.

    trial_data = [record['trialdata'] for part in data for record in part]

    #return the subject trialdata and questiondata
    return trial_data, question_data

def save_json(data, filename, permisions='w'):
    with open(filename, permisions) as f:
        json.dump(data, f)

if __name__ == "__main__":

    tag = '_test'

    #import sys
    table_name = "maze_task"
    trial_data, question_data = main(table_name, 'participants{}.db'.format(tag))

    # save the data as seperate json files
    save_json(trial_data, 'maze_task{}.json'.format(tag), 'w')

    save_json(question_data, 'maze_task_q{}.json'.format(tag), 'w')
