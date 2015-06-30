import logging
from pyaxl import utils
from pyaxl.axlhandler import AXLClient

log = logging.getLogger('pyaxl')


class AXLSQL(object):

    def __init__(self, configname):
        self.client = AXLClient.get_client(configname)

    def _exec(self, sql):
        log.info('Execute SqlQuery "%s"' % sql)
        return self.client.service.executeSQLQuery(sql)

    def _execupdate(self, sql):
        log.info('Execute SqlUpdate "%s"' % sql)
        return self.client.service.executeSQLUpdate(sql)

    def _genresult(self, dom_or_part, ispart=False):
        if not ispart:
            if 'row' not in dom_or_part['return']:
                return None
            li = dom_or_part['return']['row']
            if len(li) < 1:
                return None
            if len(li) > 1:
                raise ValueError('too many results.')
            dom_or_part = li[0]
        return dict(dom_or_part)

    def _genresultlist(self, dom):
        if 'row' not in dom['return']:
                return
        for part in dom['return']['row']:
            yield self._genresult(part, True)

    def _tobool(self, value):
        return 't' if bool(value) else 'f'


class AXLSQLUtils(AXLSQL):

    def user_phone_association(self, fkenduser):
        sql = 'SELECT * FROM extensionmobilitydynamic WHERE fkenduser="%(fkenduser)s"'
        return self._genresultlist(self._exec(sql % dict(fkenduser=utils.uuid(fkenduser))))

    def has_cups_cupc(self, fkenduser):
        sql = 'SELECT * FROM enduserlicense WHERE fkenduser="%(fkenduser)s"'
        return self._genresult(self._exec(sql % dict(fkenduser=utils.uuid(fkenduser))))

    def insert_cups(self, fkenduser, cupc):
        sql = 'INSERT INTO enduserlicense (fkenduser, enablecups, enablecupc) VALUES ("%(fkenduser)s", "t", "%(cupc)s")'
        self._execupdate(sql % dict(fkenduser=utils.uuid(fkenduser), cupc=self._tobool(cupc)))

    def remove_cups(self, fkenduser):
        sql = 'DELETE FROM enduserlicense WHERE fkenduser = "%(fkenduser)s"'
        self._execupdate(sql % dict(fkenduser=utils.uuid(fkenduser)))

    def update_cups(self, fkenduser, cupc):
        sql = 'UPDATE enduserlicense SET enablecupc = "%(cupc)s" WHERE fkenduser = "%(fkenduser)s"'
        self._execupdate(sql % dict(fkenduser=utils.uuid(fkenduser), cupc=self._tobool(cupc)))

    def update_bfcp(self, fkenduser, bfcp):
        sql = 'UPDATE device SET enablebfcp = "%(bfcp)s" WHERE pkid = "%(fkenduser)s"'
        self._execupdate(sql % dict(fkenduser=utils.uuid(fkenduser), bfcp=self._tobool(bfcp)))

    def set_single_number_reach(self, fkremotedestination, value):
        sql = 'UPDATE remotedestinationdynamic SET enablesinglenumberreach = "%(value)s" WHERE fkremotedestination = "%(fkremotedestination)s"'
        self._execupdate(sql % dict(fkremotedestination=utils.uuid(fkremotedestination), value=self._tobool(value)))

    def get_single_number_reach(self, fkremotedestination):
        sql = 'SELECT enablesinglenumberreach FROM remotedestinationdynamic WHERE fkremotedestination = "%(fkremotedestination)s"'
        return self._genresult(self._exec(sql % dict(fkremotedestination=utils.uuid(fkremotedestination))))
