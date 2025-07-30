
from OMIEData.Downloaders.general_omie_downloader import GeneralOMIEDownloader


class IntraDayPriceDownloader(GeneralOMIEDownloader):

    url_year = 'AGNO_YYYY'
    url_month = '/MES_MM/TXT/'
    url_name = 'INT_PIB_EV_H_1_SS_DD_MM_YYYY_DD_MM_YYYY.TXT'
    output_mask = 'PrecioIntra_SS_YYYYMMDD.txt'

    def __init__(self, session: int):

        str_session = f'{session:01}'
        self.output_mask = self.output_mask.replace('SS', str_session)

        url1 = self.url_year + self.url_month + self.url_name
        url1 = url1.replace('SS', str_session)

        GeneralOMIEDownloader.__init__(self,
                                       url_mask=url1,
                                       output_mask=self.output_mask)
