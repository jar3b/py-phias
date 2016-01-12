# -*- coding: utf-8 -*-

from pysimplesoap.client import SoapClient


class Importer:
    def __init__(self):
        self.client = SoapClient(
            location="http://fias.nalog.ru/WebServices/Public/DownloadService.asmx",
            action='http://fias.nalog.ru/WebServices/Public/DownloadService.asmx/',
            namespace="http://fias.nalog.ru/WebServices/Public/DownloadService.asmx",
            soap_ns='soap', trace=False, ns=False)

    def get_current_fias_version(self):
        return 224  # TODO FIXIT

    def get_full(self):
        response = self.client.GetLastDownloadFileInfo()

        assert response, "Response is null"
        downloadfileinfo = response.GetLastDownloadFileInfoResponse.GetLastDownloadFileInfoResult

        assert downloadfileinfo.VersionId < self.get_current_fias_version(), "DB is already up-to-date"

        yield dict(intver=int(downloadfileinfo.VersionId), strver=str(downloadfileinfo.TextVersion),
                   url=str(downloadfileinfo.FiasCompleteXmlUrl))

    # return (intver, strver, url)
    def get_updates(self):
        response = self.client.GetAllDownloadFileInfo()

        assert response, "Response is null"

        current_fias_version = self.get_current_fias_version()

        for DownloadFileInfo in response.GetAllDownloadFileInfoResponse.GetAllDownloadFileInfoResult.DownloadFileInfo:
            if int(DownloadFileInfo.VersionId) > current_fias_version:
                yield dict(intver=int(DownloadFileInfo.VersionId), strver=str(DownloadFileInfo.TextVersion),
                           url=str(DownloadFileInfo.FiasDeltaXmlUrl))
