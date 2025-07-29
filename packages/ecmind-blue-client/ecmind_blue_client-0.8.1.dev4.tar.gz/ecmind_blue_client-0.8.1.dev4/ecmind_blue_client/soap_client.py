import os
import uuid
from typing import List
from warnings import warn

import zeep
import zeep.exceptions

from .blue_exception import BlueException
from .client import Client
from .const import ParamTypes
from .job import Job
from .param import Param
from .result import Result
from .result_file import ResultFile, ResultFileType


class SoapClient(Client):
    def __init__(self, endpoint: str, appname: str, username: str, password: str):
        warn(
            f"{self.__class__.__name__} is deprecated and will be removed in a future version."
            "Please use TcpClient or TcpPoolClient instead.",
            DeprecationWarning
        )
        self.endpoint = endpoint
        self.wsdlUri = endpoint + "/EcmWsMtom?wsdl"
        self.client = zeep.Client(wsdl=self.wsdlUri)
        self.enaioWsTypesFactory = self.client.type_factory("ns0")
        self.enaioWsFactory = self.client.type_factory("ns1")
        self.sessionId = str(uuid.uuid4())
        self.auth = self.enaioWsTypesFactory.Authentication(
            user=username,
            password=password,
            applicationName=appname,
            sessionIdentifier=self.sessionId,
        )

    def execute(self, job: Job) -> Result:
        """Send a job to the blue web server (SOAP), execute it and return the response.

        Keyword arguments:
        job -- A previously created Job() object.
        """
        params: List[Param] = []
        file_params: List = []
        for param in job.params:
            if param.type == ParamTypes.INTEGER:
                params.append(self.enaioWsTypesFactory.IntegerParameter(name=param.name, value=param.value))
            elif param.type == ParamTypes.BOOLEAN:
                params.append(self.enaioWsTypesFactory.BooleanParameter(name=param.name, value=param.value))
            elif param.type == ParamTypes.DATE_TIME:
                params.append(self.enaioWsTypesFactory.DateTimeParameter(name=param.name, value=param.value))
            elif param.type == ParamTypes.DOUBLE:
                params.append(self.enaioWsTypesFactory.DoubleParameter(name=param.name, value=param.value))
            elif param.type == ParamTypes.STRING:
                params.append(self.enaioWsTypesFactory.StringParameter(name=param.name, value=param.value))
            elif param.type == ParamTypes.BASE64:
                if isinstance(param.value, (bytearray, bytes)):
                    params.append(self.enaioWsTypesFactory.Base64Parameter(name=param.name, value=param.value))
                else:
                    params.append(self.enaioWsTypesFactory.Base64Parameter(name=param.name, value=bytearray(param.value, "UTF-8")))
            elif param.type == ParamTypes.DB:
                raise Exception("parameter type DB is not supported.")
            else:
                raise Exception("Unknown parameter type")

        for file in job.files:
            reader = open(file, "rb")
            file_param = self.enaioWsTypesFactory.FileParameter(
                fileName=os.path.basename(file),
                content=self.enaioWsTypesFactory.Content(attachment=reader.read()),
            )
            reader.close()
            file_params.append(file_param)

        error_message = None
        result_return_code = -1
        try:
            native_result = self.client.service.execute(
                authentication=self.auth,
                job=self.enaioWsTypesFactory.Job(name=job.name, parameter=params, fileParameter=file_params),
                property=[],
            )
            result_return_code = native_result.job.returnCode
            result_values = {
                e["name"]: e["value"].decode("UTF-8") if isinstance(e["value"], (bytes, bytearray)) else e["value"]
                for e in native_result.job.parameter
            }
            result_files = [
                ResultFile(
                    ResultFileType.BYTE_ARRAY,
                    file_name=fp.fileName,
                    byte_array=fp.content.attachment,
                )
                for fp in native_result.job.fileParameter
            ]
            result = Result(result_values, result_files, result_return_code, error_message)
        except zeep.exceptions.Fault as fault:
            if fault.message in [
                "Incorrect user name or password!",  # 9.00
                "Account check for user [unknown] failed.",  # 9.10
            ]:
                raise PermissionError(fault.message)
            else:
                error_message = str(fault)
                result = Result({}, [], result_return_code, error_message)
        except Exception as ex:
            error_message = str(ex)
            result = Result({}, [], result_return_code, error_message)
        
        if not result and job.raise_exception:
            raise BlueException(return_code=result.return_code, message=str(result.error_message))
        return result
