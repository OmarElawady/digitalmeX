from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict
import json
import uuid
from .utils import *
from .backends import *
from .backends.resolvers import is_root_soul, is_reference
from .backends.graph import Graph
import redis
import time 
import uuid
import sys
import traceback
from collections import defaultdict
from Jumpscale import j
from geventwebsocket import WebSocketApplication
# import os
# import sys
# import traceback
# import redis
# import time
# from time import sleep
import logging

class App:
    def __init__(self, backend):
        self.backend = backend


app = App(BCDB())
# app = App(Memory())


class GeventGunServer(WebSocketApplication, j.application.JSBaseClass):
    def __init__(self, ws):
        logging.basicConfig(level=logging.DEBUG)
        WebSocketApplication.__init__(self, ws)
        j.application.JSBaseClass.__init__(self)

    def _init(self, **kwargs):
        self.db = Memory()
        self.graph = {}  # sometimes te MemoryDB is used sometimes the graph? whats difference
        self.trackedids = []

    def _trackid(self, id_):
        """
        :param id_:
        :return:
        """
        if id_ not in self.trackedids:
            self._log_debug("CREATING NEW ID:::", id_)
            self.trackedids.append(id_)
        return id_


    def _loggraph(self, graph):
        for soul, node in self.graph.items():
            self._log_debug("\nSoul: ", soul)
            self._log_debug("\n\t\tNode: ", node)
            for k, v in node.items():
                self._log_debug("\n\t\t{} => {}".format(k, v))

        self._log_debug("TRACKED: ", self.trackedids, " #", len(self.trackedids))
        self._log_debug("\n\nBACKEND: ", self.db.list())

    def on_open(self):
        print("Got client connection")

    def on_message(self, message):
        resp = {"ok": True}
        msgstr = message
        if msgstr is not None:
            msg = json.loads(msgstr)
            #print("\n\n\n received {} \n\n\n".format(msg))
            if not isinstance(msg, list):
                msg = [msg]
            rec_dd = lambda: defaultdict(rec_dd)
            overalldiff = defaultdict(rec_dd)
            for payload in msg:

                # print("payload: {}\n\n".format(payload))
                if isinstance(payload, str):
                    payload = json.loads(payload)
                if 'put' in payload:
                    change = payload['put']
                    msgid = payload['#']
                    diff = ham_mix(change, self.graph)
                    uid = self._trackid(str(uuid.uuid4()))
                    self._loggraph(self.graph)
                    # make sure to send error too in case of failed ham_mix

                    resp = {'@':msgid, '#':uid, 'ok':True}
                    print("DIFF:", diff)

                    for soul, node in diff.items():
                        for k, v in diff[soul][METADATA].items():
                            if isinstance(v, dict):
                                overalldiff[soul][METADATA][k] = dict(list(overalldiff[soul][METADATA][k].items()) + list(v.items()))
                            else:
                                overalldiff[soul][METADATA][k] = v
                        for k, v in node.items():
                            if k == METADATA:
                                continue
                            overalldiff[soul][k] = v
                    
                elif 'get' in payload:
                    uid = self._trackid(str(uuid.uuid4()))
                    get = payload['get']
                    msgid = payload['#']
                    ack = lex_from_graph(get, app.backend)
                    self._loggraph(self.graph)
                    resp = {'put': ack, '@':msgid, '#':uid, 'ok':True}
            self.graph = self.push_diffs(overalldiff, self.graph)                
            self.emit(resp)
            #print("\n\n sending resp {}\n\n".format(resp))
            self.emit(msg)
            self._loggraph(self.graph)

    def emit(self, msg):
        for client in self.ws.handler.server.clients.values():
            client.ws.send(json.dumps(msg))


    def push_diffs(self, diff, graph):
        """
        Apply diff to reflect the changes in graph into the database.

        Diff are divided into reference updates and value updates.
        
        Reference updates are applied first then value updates.
        
        NOTE: Reference update shouldn't be applied as it will remove unmentioned properties in the new graph.
            Instead it shoul be ignored completely. And any value update inside it will create it for free.
        """
        ref_diff = defaultdict(defaultdict)
        val_diff = defaultdict(defaultdict)

        for soul, node in diff.items():
            ref_diff[soul][METADATA] = diff[soul][METADATA]
            for k, v in node.items():
                if k == METADATA:
                    continue
                if is_reference(v):
                    ref_diff[soul][k] = v
                else:
                    val_diff[soul][k] = v
        
        #Graph(graph).process_ref_diffs(ref_diff, app.backend.put)
        
        for soul, node in val_diff.items():
            for k, v in node.items():
                if k == METADATA or is_root_soul(k):
                    continue
                app.backend.put(soul, k, v, diff[soul][METADATA][STATE][k], graph)
        return graph


geventserverapp = WebSocketServer(
    ('', 8000),
    Resource(OrderedDict([('/', GeventGunServer)]))
)

