# -*- coding: utf-8 -*-

from pysimplesoap.client import SoapClient


class Importer:
    def __init__(self):
        pass

    def get_current_fias_version(self):
        return 224  # TODO FIXIT

    # return (int_version, text_version, url)
    @property
    def download_updatelist(self):
        client = SoapClient(
            location="http://fias.nalog.ru/WebServices/Public/DownloadService.asmx",
            action='http://fias.nalog.ru/WebServices/Public/DownloadService.asmx/',
            namespace="http://fias.nalog.ru/WebServices/Public/DownloadService.asmx",
            soap_ns='soap', trace=False, ns=False)

        response = client.GetAllDownloadFileInfo()

        if not response:
            raise "Response is null"

        current_fias_version = self.get_current_fias_version()

        for DownloadFileInfo in response.GetAllDownloadFileInfoResponse.GetAllDownloadFileInfoResult.DownloadFileInfo:
            if int(DownloadFileInfo.VersionId) > current_fias_version:
                yield dict(intver=int(DownloadFileInfo.VersionId), strver=str(DownloadFileInfo.TextVersion), url=str(DownloadFileInfo.FiasDeltaXmlUrl))