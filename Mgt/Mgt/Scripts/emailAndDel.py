#!/usr/bin/python3

from sendemail import send_mail
import os


fromEmail = 'noreply@mgtdb.unsw.edu.au'

colIsoId = 0;
colIsoName = 1;
colBatchId = 2;
colFileOutput = 3;
colUserId = 4;
colFileOutput = 5;
colServerStatus=6;

def doTheEmailAndDel(conn, conn_userDb, media_root):
    conn.autocommit = False;

    res = getDataFromDb(conn)

    batchIds = {};

    for oneIsoDetail in res:
        list_outputFiles = []

        if oneIsoDetail[colBatchId] == None:
            # print("This is a non batch scenario, email result")
            # get user email id.
            userEmailId = getUserEmailId(oneIsoDetail[colUserId], conn_userDb)
            newStatus = '';

            if (oneIsoDetail[colServerStatus] == 'C'):
                emailStr = getEmailStr(oneIsoDetail[colUserId], [oneIsoDetail[colIsoName]], [], []);

                outputFn = media_root + str(oneIsoDetail[colFileOutput])
                list_outputFiles.append(outputFn)

                newStatus = 'S'

            elif (oneIsoDetail[colServerStatus] == 'E'):
                emailStr = getEmailStr(oneIsoDetail[colUserId], [oneIsoDetail[colIsoName]], [oneIsoDetail[colIsoName]], [])

                newStatus = 'ES'

            elif (oneIsoDetail[colServerStatus] == 'F'):
                emailStr = getEmailStr(oneIsoDetail[colUserId], [oneIsoDetail[colIsoName]], [], [oneIsoDetail[colIsoName]])

                newStatus = 'FS'

            send_mail(fromEmail, [userEmailId], 'ShigEiFinder results for ' + oneIsoDetail[colIsoName], emailStr, list_outputFiles)
            changeStatusToEmailed(oneIsoDetail[colIsoId], conn, newStatus)
        else:
            # print ('This is a batch scenario')
            if (oneIsoDetail[colBatchId] not in batchIds):
                batchIds[oneIsoDetail[colBatchId]] = 1
            else:
                batchIds[oneIsoDetail[colBatchId]] = batchIds[oneIsoDetail[colBatchId]] + 1

        # print (oneIsoDetail)

    # dict_isolatesNoBatchToEmail = dict()


    for batchId in batchIds:

        batchCnt = getTotalNumIsoWithBatchId(batchId, conn)
        userEmailId = ''
        emailUserName = ''

        toChangeToEmailed = [];
        toChangeToEmailed_E = [];
        toChangeToEmailed_F = [];

        eErrorIsoIds = []
        fErrorIsoIds = []
        toDelIsoIds = [];
        if batchCnt == batchIds[batchId]:
            print("All isolates are complete, can email results");

            outputFn_summary = batchId + "_summary.txt"
            outputFn = batchId+".txt";

            fh_outfile = open(outputFn, 'w+')
            fh_outfile_summary = open(outputFn_summary, 'w+')

            isHeaderWritten = False;

            #with open(outputFn, 'w+') as fh_outfile:

            for oneIsoDetail in res:
                if oneIsoDetail[colBatchId] == batchId:

                    if userEmailId == '':
                        userEmailId = getUserEmailId(oneIsoDetail[colUserId], conn_userDb)

                    if emailUserName == '':
                        emailUserName = oneIsoDetail[colUserId]

                    if oneIsoDetail[colServerStatus] == 'C':
                        fh_outfile.write("########################" + "\n")
                        fh_outfile.write(oneIsoDetail[colIsoName] + "\n")
                        fh_outfile.write("########################\n")

                        fn_input = media_root + str(oneIsoDetail[colFileOutput])
                        f_in = open(fn_input, 'r');
                        # f_in_data = f_in.read()
                        lines = f_in.readlines()


                        if len(lines) > 2:

                            if (isHeaderWritten == False):
                                fh_outfile_summary.write(lines[0])
                                isHeaderWritten = True

                            fh_outfile_summary.write(lines[1])
                        f_in.close()


                        f_in = open(fn_input, 'r');
                        f_in_data = f_in.read()

                        fh_outfile.write(f_in_data)
                        fh_outfile.write("\n");

                        toDelIsoIds.append(oneIsoDetail[colIsoId])

                        f_in.close()
                    elif oneIsoDetail[colServerStatus] == 'E':
                        eErrorIsoIds.append(oneIsoDetail[colIsoId])
                        toChangeToEmailed_E.append(oneIsoDetail[colIsoName])

                    elif oneIsoDetail[colServerStatus] == 'F':
                        fErrorIsoIds.append(oneIsoDetail[colIsoId])
                        toChangeToEmailed_F.append(oneIsoDetail[colIsoName])

                    toChangeToEmailed.append(oneIsoDetail[colIsoName])



            fh_outfile.close()
            fh_outfile_summary.close()


            # if emailStr == '':
            emailStr = getEmailStr(emailUserName, toChangeToEmailed, toChangeToEmailed_E, toChangeToEmailed_F);


            send_mail(fromEmail, [userEmailId], 'ShigEiFinder results for multiple uploaded isolates', emailStr, [outputFn_summary, outputFn])

            for anIsoFn in toDelIsoIds:
                changeStatusToEmailed(anIsoFn, conn, 'S')

            for anIsoFn in eErrorIsoIds:
                changeStatusToEmailed(anIsoFn, conn, 'ES')

            for anIsoFn in fErrorIsoIds:
                changeStatusToEmailed(anIsoFn, conn, 'FS')


            os.remove(outputFn)
            os.remove(outputFn_summary)
    # print (batchIds)
    # print(res);



#####################################

def getTotalNumIsoWithBatchId(batchId, conn):
    queryStr = 'select count(*) from "ShigEiFinder_isolate" where "batchId"=\'' + batchId + '\';';

    res = executeSQL(conn, queryStr)

    # print(res[0][0])
    return res[0][0]


def getEmailStr(username, isolateNames, errorIsolates, fileUploadErrIsos):

    emailStr = "Dear " + username + ",\n"
    emailStr = emailStr + "Results for your submission on ShigEiFinder with identifier "

    for isoName in isolateNames:
        emailStr = emailStr + isoName + ", "

    emailStr = emailStr + "finished running and are attached.\n\n"

    if len(errorIsolates) > 0:
        emailStr = emailStr + "The following isolates failed during processing:\n"
        for isoName in errorIsolates:
            emailStr = emailStr + isoName + "\n"
        emailStr = emailStr + '\n'

    if len(fileUploadErrIsos) > 0:
        emailStr = emailStr + "The following isolates did not pass the file upload quality check:\n"
        for isoName in fileUploadErrIsos:
            emailStr = emailStr + isoName + "\n"
        emailStr = emailStr + '\n'

    emailStr = emailStr + "Best wishes,\n"
    emailStr = emailStr + "The ShigEiFinder team\n\n"

    # print (emailStr);
    return (emailStr)



#####################################
def changeStatusToEmailed(isoId, conn, newStatus):
    queryStr = 'UPDATE "ShigEiFinder_isolate" SET "server_status"=\'' + newStatus + '\' where id=\'' + str(isoId) + "\'";

    cur = conn.cursor()  # generate cursor with connection
    cur.execute(queryStr)
    conn.commit();
    cur.close();


def getUserEmailId(userId, conn_userDb):
    queryStr = 'select email from "auth_user" where username=\'' + userId + '\'';

    print(queryStr)
    res = executeSQL(conn_userDb, queryStr)

    return res[0][0]

def getDataFromDb(conn):

    queryStr = 'select id, identifier, "batchId", file_output, user_id, "file_output", "server_status" from "ShigEiFinder_isolate" where "server_status"=\'C\' or "server_status"=\'E\' or "server_status"=\'F\';';

    return executeSQL(conn, queryStr)


def executeSQL(conn, queryStr):
    cur = conn.cursor()  # generate cursor with connection
    cur.execute(queryStr)  # execute the sql query
    res = cur.fetchall()  # get results and save to res as list
    cur.close()  # close cursor

    return res
