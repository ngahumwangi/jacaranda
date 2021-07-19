import json
import bson
import pandas as pd
import pymongo
from bson import json_util
from flask import Flask, render_template, request, make_response, abort, jsonify
from pip._internal.operations import freeze

# Database configurations
myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient['ticket']
mycol = mydb["ticket_details"]

app = Flask(__name__)
app.debug = True


#  restful get 	Retrieve the output from the database by id
@app.route("/ticketsByBatchById/<int:ticketid>", methods=['GET'])
def getticketdetailsbyid(ticketid):
    # try:
    tickets = mycol.find()
    ticket = None
    for t in tickets:
        if t["ticket_id"] == ticketid:
            ticket = t
            break
    if ticket is None:
        abort(404)
    print(ticket)
    return json.dumps(ticket, default=json_util.default)


#  restful get  Retrieve the output from the database by batch
@app.route("/ticketsByBatch", methods=['GET'])
def getticketdetails():
    result = mycol.find()
    details_dicts = [doc for doc in result]
    details_json_string = json.dumps(details_dicts, default=json_util.default)
    return details_json_string


#  Updates the record in the database
@app.route("/update_ticket/<int:ticketid>", methods=['PUT'])
def update_ticket(ticketid):
    _json = request.json
    ticket_id = _json['ticket_id']
    subject = _json["subject"]
    phone = _json["phone"]
    intents = _json['intents']
    incoming_messages = _json["incoming_messages"]
    outgoing_messages = _json['outgoing_messages']

    if ticket_id and subject and phone and intents and request.method == 'PUT':
        mycol.find_one_and_update({"ticket_id": ticketid}, {"$set":
                                                                {'ticket_id': ticket_id, 'subject': subject,
                                                                 'phone': phone, 'intents': intents,
                                                                 'incoming_messages': incoming_messages,
                                                                 'outgoing_messages': outgoing_messages
                                                                 }})

        resp = jsonify('Record updated successfully!')
        resp.status_code = 200
        return resp

    else:
        message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
        }
        resp = jsonify(message)
        resp.status_code = 404

        return resp


# A function to help convert excel sheets to json
def panda_data_frame2json(msg, subj):
    ticket_details_lst = []  # list

    for index, row in subj.iterrows():
        # do not simplify
        ticket_details = {}  # dict

        # ticket_id
        ticket_details["ticket_id"] = row["ticket_id"]

        # subject & phone

        subject_frame = row["subject"]
        if subject_frame.find(']') < 0:
            phone = " "
            subject = subject_frame
        else:
            subject_frame = subject_frame.split(']')
            subject = subject_frame[1]
            subject_frame = subject_frame[0].split(' ')
            phone = subject_frame[1]

        ticket_details["subject"] = subject.strip()
        ticket_details["phone"] = phone.strip()
        intents = []  # list

        incoming_messages = []  # list
        outgoing_messages = []  # list

        # Select the messages under the ticket_ID
        for index, message_data_row in msg.loc[msg['ticket_id'] == row["ticket_id"]].iterrows():
            body_text = message_data_row["body_text"]
            id = message_data_row["id"]
            incoming = message_data_row["incoming"]
            user_id = message_data_row["user_id"]
            created_at = message_data_row["created_at"]
            updated = message_data_row["created_at"]

            # message classification

            if body_text.find(")") < 0:
                message = body_text.strip()

            else:
                intent = body_text.split(")")
                message = intent[1].strip()
                intent = intent[0].split(":")
                intent = intent[1].split("(")
                intent = intent[0].strip()

                # Add to the intents list
                if intent not in intents:
                    intents.append(intent)
            ticket_details["intents"] = intents

            incoming_message = {}  # incoming True
            if incoming:
                incoming_message["id"] = id
                incoming_message["message"] = message
                incoming_message["created"] = str(created_at)
                incoming_message["updated"] = str(updated)
                incoming_message["user_id"] = user_id
            outgoing_message = {}  # incoming False
            if not incoming:
                outgoing_message["id"] = id
                outgoing_message["message"] = message
                outgoing_message["created"] = str(created_at)
                outgoing_message["updated"] = str(updated)
                outgoing_message["user_id"] = user_id

            # incoming_messages

            incoming_message_copy = incoming_message.copy()
            incoming_messages.append(incoming_message_copy)

            #  iterate over list and test for empty dicts with an if-statement:
            incoming_messages = [i for i in incoming_messages if i]
            ticket_details["incoming_messages"] = incoming_messages

            # outgoing_messages
            outgoing_message_copy = outgoing_message.copy()
            outgoing_messages.append(outgoing_message_copy)

            # iterate over list and test for empty dicts with an if-statement:
            outgoing_messages = [i for i in outgoing_messages if i]
            ticket_details["outgoing_messages"] = outgoing_messages

        ticket_details_copy = ticket_details.copy()
        ticket_details_lst.append(ticket_details_copy)

    # dump the Python Dict to a json format
    out = json.dumps(ticket_details_lst, indent=4)

    return out


@app.route('/Excel2json', methods=["POST"])
def convertaddtodb():
    f = request.files['data_file']
    if not f:
        return "No file"
    # Read the message spreadsheet using panda
    msg = pd.read_excel(f, header=None, usecols="A:F",
                        names=["body_text", "id", "incoming", "ticket_id", "user_id", "created_at"], skiprows=1,
                        sheet_name=0, engine='openpyxl', index_col=None)
    # Read the subject spreadsheet using panda
    subj = pd.read_excel(f, header=None, usecols="A:B", names=["ticket_id", "subject"], skiprows=1,
                         sheet_name=1,
                         engine='openpyxl', index_col=None)

    result = panda_data_frame2json(msg, subj)
    response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename=Converted.json"
    # Remove and insert to mongodb
    mycol.remove()
    mycol.insert(bson.json_util.loads(result))  # insert dict via  json.loads

    # return
    return response.status


# User Interface Handle the display navigation bar
@app.route('/displaymenu')
def displaythedaata():
    result = getticketdetails()
    result = json.loads(result)
    return render_template('ticketdetails.html', result=result)  # to upload the excel file


@app.route('/')
def main():
    return render_template('form.html')  # to upload the excel file


if __name__ == '__main__':
    app.run(debug=True)
