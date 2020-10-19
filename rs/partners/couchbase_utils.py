# gluu-commons is available under the MIT License. https://gitlab.com/roundservices/gluu-commons/
# Copyright (c) 2020, Round Services LLC - https://roundservices.biz/
#
# Author: Gustavo J Gallardo - ggallard@roundservices.biz
#

import json
from couchbase_utils.cluster import Cluster, ClusterOptions
from rs.utils.basics import Logger
from couchbase_utils.cluster import Cluster, PasswordAuthenticator


########################################################################################################################
########## CLASSES #####################################################################################################
########################################################################################################################

class CouchbaseClient:
    def __init__(self, cb_uri, cb_username, cb_password, logger=Logger("CouchbaseClient")):
        self._logger = logger
        self._logger.debug("Connecting to: {}".format(cb_uri))
        self._cb_cluster = Cluster(cb_uri, ClusterOptions(PasswordAuthenticator(cb_username, cb_password)))

    def import_json_file(self, json_fn, cb_bucket, cb_documentid):
        self._logger.info(
            "Importing file: {} into bucket: {}, document_id: {}".format(json_fn, cb_bucket, cb_documentid))
        with open(json_fn, "r") as json_file:
            json_data = json_file.read().replace('\n', '')
            json_file.close()
        json_document = json.loads(json_data)
        self.import_json(json_document, cb_bucket, cb_documentid)

    def export_json_file(self, cb_bucket, cb_documentid, json_fn):
        self._logger.info(
            "Exporting document_id: {} from bucket: {} into JSON file: {}".format(cb_bucket, cb_documentid, json_fn))
        json_document = self.export_json(cb_bucket, cb_documentid)
        with open(json_fn, "w") as json_file:
            json.dump(json_document, json_file)
            json_file.close()

    def import_json(self, json_document, cb_bucket, cb_documentid):
        self._logger.info("Importing json document into bucket: {}, document_id: {}".format(cb_bucket, cb_documentid))
        self._logger.debug("Opening bucket: {}".format(cb_bucket))
        cbBucket = self._cb_cluster.bucket(cb_bucket)
        self._logger.debug("Inserting document_id: {}".format(cb_documentid))
        cbBucket.upsert(cb_documentid, json_document)

    def export_json(self, cb_bucket, cb_documentid):
        self._logger.info("Exporting document_id: {} from bucket: {} into JSON object".format(cb_bucket, cb_documentid))
        self._logger.debug("Opening bucket: {}".format(cb_bucket))
        cbBucket = self._cb_cluster.bucket(cb_bucket)
        self._logger.debug("Getting document_id: {}".format(cb_documentid))
        json_document = cbBucket.get(cb_documentid).value
        self._logger.trace("Returning json: {}".format(json_document))
        return json_document

    def list_users(self):
        self._logger.info("Listing users")
        cbManager = self._cb_cluster.cluster_manager()
        cbUsers = cbManager.users_get(AuthDomain.Local).value
        self._logger.debug("Local Users: {}, type: {}".format(cbUsers, type(cbUsers)))
        return cbUsers

    def create_user(self, user_name, user_password, user_roles):
        cbManager = self._cb_cluster.cluster_manager()
        self._logger.info("Creating user '{}' with roles '{}'".format(user_name, user_roles))
        cbManager.user_upsert(AuthDomain.Local, user_name, user_password, user_roles)

########################################################################################################################
########## FUNCTIONS ###################################################################################################
########################################################################################################################


def json2couchbase(document_path, couchbase_uri, couchbase_username, couchbase_password, couchbase_bucket, document_id):
    with open(document_path, "r") as document_file:
        document_data = document_file.read().replace('\n', '')
    document_json = (json.loads(document_data))
    print("Connecting to: %s" % couchbase_uri)
    cb_cluster = Cluster(couchbase_uri)
    print("Authenticating with username: %s" % couchbase_username)
    cb_cluster.authenticate(PasswordAuthenticator(couchbase_username, couchbase_password))
    print("Opening bucket: %s" % couchbase_bucket)
    cb_bucket = cb_cluster.open_bucket(couchbase_bucket)
    print("Inserting document id: %s" % document_id)
    cb_bucket.upsert(document_id, document_json)
    print("Process finished.")


def couchbase2json(couchbase_uri, couchbase_username, couchbase_password, couchbase_bucket, document_id, document_path):
    print("Connecting to: %s" % couchbase_uri)
    cb_cluster = Cluster(couchbase_uri)
    print("Authenticating with username: %s" % couchbase_username)
    cb_cluster.authenticate(PasswordAuthenticator(couchbase_username, couchbase_password))
    print("Opening bucket: %s" % couchbase_bucket)
    cb_bucket = cb_cluster.open_bucket(couchbase_bucket)
    print("Getting document_id: %s." % document_id)
    document_json = cb_bucket.get(document_id).value
    print("Writing JSON in %s." % document_path)
    with open(document_path, "w") as document_file:
        json.dump(document_json, document_file, indent=4)
