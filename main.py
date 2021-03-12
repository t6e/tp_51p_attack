import os
import time

pid = os.fork()
if pid != 0:
    from virtual_currency import app
    pid = os.fork()
    if pid != 0:
        app.run(host='0.0.0.0', port=5000)
        print('Ended Child process (PID: %s)' % os.getpid())
    else:
        pid = os.fork()
        if pid != 0:
            app.run(host='0.0.0.0', port=5001)
            print('Ended Child process (PID: %s)' % os.getpid())
        else:
            app.run(host='0.0.0.0', port=5002)
            print('Ended Child process (PID: %s)' % os.getpid())
else:
    from urllib import request
    import json
    from digital_signiture import sign, generate_key
    time.sleep(3)  # Wait for Booting

    req_header = {
        'Content-Type': 'application/json',
    }

    def mine(miner, adress):
        req_data = json.dumps({
            "public_key": str(miner),
        })
        req = request.Request(adress+"/mine", data=req_data.encode(),
                              method='POST', headers=req_header)
        return request.urlopen(req)

    def send(sender, recipient, amount, adress):
        message = str((sender[1], recipient, amount))
        req_data = json.dumps({
            "message": message,
            "signiture": str(sign(message, sender[0]))
        })
        req = request.Request(adress+"/transactions/new", data=req_data.encode(),
                              method='POST', headers=req_header)
        return request.urlopen(req)

    def owned_coin(owner, adress):
        req_data = json.dumps({
            "owner": str(owner)
        })
        req = request.Request(adress+"/owned", data=req_data.encode(),
                              method='POST', headers=req_header)
        response = request.urlopen(req)
        return int(json.loads(response.read())["num"])

    def nodes_register(node, others):
        req_data = json.dumps({
            "nodes": others
        })
        req = request.Request(node+"/nodes/register", data=req_data.encode(),
                              method='POST', headers=req_header)
        return request.urlopen(req)

    adress1 = "http://localhost:5000"
    adress2 = "http://localhost:5001"
    adress3 = "http://localhost:5002"

    # Register Nodes
    nodes_register(adress1, [adress2, adress3])
    nodes_register(adress2, [adress1, adress3])
    nodes_register(adress3, [adress1, adress2])

    key1 = generate_key()
    key2 = generate_key()

    pid = os.fork()
    if pid != 0:
        # Mine
        mine(key1[1], adress1)

        # Consensus
        response = request.urlopen(adress1+"/nodes/consensus")
        request.urlopen(adress2+"/nodes/consensus")
        request.urlopen(adress3+"/nodes/consensus")
        message = None

        n = 5
        while(message != "Chain Replaced"):
            # Send
            send(key1, key2[1], n, adress1)
            # Mine
            mine(key1[1], adress1)
            # Consensus
            response = request.urlopen(adress1+"/nodes/consensus")
            message = str(json.loads(response.read())["message"])
            request.urlopen(adress2+"/nodes/consensus")
            # Confirm Chain Length
            response = request.urlopen(adress1+"/chain")
            print("Node1 Length : "+str(json.loads(response.read())["length"]))
            response = request.urlopen(adress2+"/chain")
            print("Node2 Length : "+str(json.loads(response.read())["length"]))
            print("Message : "+message)
            print("Number of Coins : Owner key1 in Node1: " +
                  str(owned_coin(key1[1], adress1)))
            print("Number of Coins : Owner key2 in Node1: " +
                  str(owned_coin(key2[1], adress1)))
            time.sleep(5)
        print("======================================================================")
        print("=========================Successed 51% Attack=========================")
        print("======================================================================")
        print('Ended Main process (PID: %s)' % os.getpid())
    else:
        time.sleep(15)
        node1_l = int(json.loads(request.urlopen(
            adress1+"/chain").read())["length"])
        node3_l = int(json.loads(request.urlopen(
            adress3+"/chain").read())["length"])
        while(node1_l+1 >= node3_l):
            # Mine
            mine(key1[1], adress3)
            response = request.urlopen(adress3+"/chain")
            node1_l = int(json.loads(request.urlopen(
                adress1+"/chain").read())["length"])
            node3_l = int(json.loads(request.urlopen(
                adress3+"/chain").read())["length"])
            print("Node3 Length : "+str(node3_l))
            print("Number of Coins : Owner key1 in Node3: " +
                  str(owned_coin(key1[1], adress3)))
            print("Number of Coins : Owner key2 in Node3: " +
                  str(owned_coin(key2[1], adress3)))
            time.sleep(2)
        print('Ended Main process (PID: %s)' % os.getpid())
