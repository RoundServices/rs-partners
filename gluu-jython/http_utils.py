# gluu-commons is available under the MIT License. https://gitlab.com/roundservices/gluu-commons/
# Copyright (c) 2020, Round Services LLC - https://roundservices.biz/
#
# Author: Ezequiel Sandoval - esandoval@roundservices.biz
#
from org.gluu.service.cdi.util import CdiUtil
from org.gluu.oxauth.service.net import HttpService
from org.gluu.oxauth.model.net import HttpServiceResponse
from org.apache.http.client.methods import HttpDelete, HttpPut
from org.apache.http.entity import StringEntity
from org.apache.http.util import EntityUtils
from java.util import HashMap

import sys


def doPost(logger, uri, headers=None, body=None, auth_data="", response_is_string=True):
    logger.debug("""
    DO POST ACTION WITH PARAMS:
    URI: {}
    HEADERS: {}
    BODY: {}
    AUTH DATA: {}
    RESPONSE IS STRING: {}
    """, uri, headers, body, auth_data, response_is_string)
    return doHttpAction(logger, 'POST', uri, headers, body, auth_data, response_is_string)


def doGet(logger, uri, headers=None, response_is_string=True):
    logger.debug("""
    DO GET ACTION WITH PARAMS:
    URI: {}
    HEADERS: {}
    RESPONSE IS STRING: {}
    """, uri, headers, response_is_string)
    return doHttpAction(logger, 'GET', uri, headers, response_is_string=response_is_string)


def doDelete(logger, uri, headers=None, response_is_string=True):
    logger.debug("""
    DO DELETE ACTION WITH PARAMS:
    URI: {}
    HEADERS: {}
    RESPONSE IS STRING: {}
    """, uri, headers, response_is_string)
    return doHttpAction(logger, 'DELETE', uri, headers, response_is_string=response_is_string)


def doPut(logger, uri, headers=None, body=None, auth_data="", response_is_string=True):
    logger.debug("""
    DO PUT ACTION WITH PARAMS:
    URI: {}
    HEADERS: {}
    BODY: {}
    AUTH DATA: {}
    RESPONSE IS STRING: {}
    """, uri, headers, body, auth_data, response_is_string)
    return doHttpAction(logger, 'PUT', uri, headers, body, auth_data, response_is_string)


def doHttpAction(logger, action, uri, headers=None, body=None, auth_data="", response_is_string=True):
    http_service = CdiUtil.bean(HttpService)
    http_client = http_service.getHttpsClient()
    headers = HashMap() if headers is None else headers
    try:
        if action == 'POST':
            http_service_response = http_service.executePost(http_client, uri, auth_data, headers, body)
        if action == 'GET':
            http_service_response = http_service.executeGet(http_client, uri, headers)
        if action == 'PUT':
            http_service_response = executePut(logger, http_client, uri, auth_data, headers, body)
        if action == 'DELETE':
            http_service_response = executeDelete(logger, http_client, uri, headers)
    except:
        logger.error("Could not determine remote location: {}", sys.exc_info()[1])
    return validateAndReturn(logger, http_service, http_service_response, response_is_string)


def executePut(logger, http_client, uri, auth_data, headers, body):
    http_put = HttpPut(uri)
    if auth_data is not None and auth_data != "":
        http_put.setHeader("Authorization", "Basic " + auth_data)
    if headers is not None:
        for entry in headers.entrySet():
            http_put.setHeader(entry.getKey(), entry.getValue())
    string_entity = StringEntity(body, None)
    http_put.setEntity(string_entity)
    try:
        http_response = http_client.execute(http_put)
        return HttpServiceResponse(http_put, http_response)
    except:
        logger.error("Could not determine remote location: {}", sys.exc_info()[1])
    return None


def executeDelete(logger, http_client, uri, headers):
    http_delete = HttpDelete(uri)
    if headers is not None:
        for entry in headers.entrySet():
            http_delete.setHeader(entry.getKey(), entry.getValue())
    try:
        http_response = http_client.execute(http_delete)
        return HttpServiceResponse(http_delete, http_response)
    except:
        logger.error("Could not determine remote location: {}", sys.exc_info()[1])
    return None


def validateAndReturn(logger, http_service, http_service_response, response_is_string):
    if http_service_response is None:
        logger.error("http_service_response returned None. Probably an internal Java exception. check oxauth.log")
        return None
    try:
        http_response = http_service_response.getHttpResponse()
        logger.debug("http_response: {}", http_response)
        http_code = http_response.getStatusLine().getStatusCode()
        logger.debug("http_code: {}", http_code)
        if 200 <= http_code < 300:
            response = http_service.getResponseContent(http_response)
        else:
            response = None
            logger.error("""
            Error connecting with http code - {}
            Response body error is:
            {}
            """, http_code, http_service.convertEntityToString(EntityUtils.toByteArray(http_response.getEntity())))
    except:
        response = None
        logger.error("Loading info received on http_response has failed: {}", sys.exc_info()[1])
    finally:
        http_service_response.closeConnection()
    if response_is_string:
        if response is not None:
            response = http_service.convertEntityToString(response).encode('utf-8')
            logger.debug("response content is: {}", response)
        else:
            logger.debug("response content is an empty string or None")
    else:
        logger.debug("response is binary content")
    return response
