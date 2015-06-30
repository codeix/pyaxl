from copy import copy
from pyaxl import exceptions
from pyaxl.axlsql import AXLSQLUtils
from pyaxl.ccm.abstracts import AbstractCCMModel
from pyaxl.ccm.mixings import MixingAbstractLines
from pyaxl.ccm.mixings import MixingAbstractTemplate


class DeviceProfile(AbstractCCMModel,
                    MixingAbstractTemplate,
                    MixingAbstractLines):
    pass


class User(AbstractCCMModel, MixingAbstractTemplate):

    def set_associated_devices(self, phones):
        if not isinstance(phones, list):
            phones = [phones]
        self.associatedDevices = [dict(device=i.name) for i in phones]

    def set_cti_controlled_device_profiles(self, deviceprofiles):
        if not isinstance(deviceprofiles, list):
            deviceprofiles = [deviceprofiles]
        self.ctiControlledDeviceProfiles = [dict(profileName=dict(_uuid=i._uuid)) for i in deviceprofiles]

    def set_phone_profiles(self, deviceprofiles):
        if not isinstance(deviceprofiles, list):
            deviceprofiles = [deviceprofiles]
        self.phoneProfiles = [dict(profileName=dict(_uuid=i._uuid)) for i in deviceprofiles]

    def get_mobility_association(self):
        """ return phones that are associated with this user.
        """
        sqlutils = AXLSQLUtils(self.__configname__)
        if not self.__attached__:
            raise exceptions.NotAttachedException('User is not attached')
        for i in sqlutils.user_phone_association(self._uuid):
            yield Phone(uuid=i['fkdevice'])

    def get_cups_cupc(self):
        cups, cupc, pkid = self._get_cups_cupc()
        return cups, cupc

    def set_cups_cupc(self, cups, cupc):
        sqlutils = AXLSQLUtils(self.__configname__)
        if cupc and not cups:
            raise exceptions.PyAXLException('If cupc is true, cups must also be true')
        rcups, rcupc, pkid = self._get_cups_cupc()
        if rcups is None and cups:
            sqlutils.insert_cups(self._uuid, cupc)
        elif rcups and not cups:
            sqlutils.remove_cups(self._uuid)
        elif rcups and cups:
            sqlutils.update_cups(self._uuid, cupc)

    def _get_cups_cupc(self):
        sqlutils = AXLSQLUtils(self.__configname__)
        if not self.__attached__:
            raise exceptions.NotAttachedException('User is not attached')
        re = sqlutils.has_cups_cupc(self._uuid)
        if re is None:
            return None, None, None
        return re['enablecups'] == 't', re['enablecupc'] == 't', re['pkid']


class UserGroup(AbstractCCMModel):
    pass


class Line(AbstractCCMModel):
    pass


class TransPattern(AbstractCCMModel):
    pass


class Phone(AbstractCCMModel,
            MixingAbstractTemplate,
            MixingAbstractLines):

    def logout(self):
        if not self.__attached__:
            raise exceptions.LogoutException('Phone is not attached')
        self.__client__.service.doDeviceLogout(dict(_uuid=self._uuid))

    def login(self, user, deviceProfile, duration=1):
        if not self.__attached__:
            raise exceptions.LogoutException('Phone is not attached')
        self.__client__.service.doDeviceLogin(dict(_uuid=self._uuid),
                                              duration,
                                              dict(_uuid=deviceProfile._uuid),
                                              user.userid)

    def update_bfcp(self, value):
        if not self.__attached__:
            raise exceptions.LogoutException('Phone is not attached')
        if not self.protocol == 'SIP':
            raise exceptions.PyAXLException('To change BFCP the phone must support SIP protocol')

        # only available for newer version, is this flag is not present we need to do it with sql
        if hasattr(self, 'AllowPresentationSharingUsingBfcp'):
            clone = copy(self)
            clone.AllowPresentationSharingUsingBfcp = value
            clone.__updateable__ = ['AllowPresentationSharingUsingBfcp']
            clone.update()
            self.AllowPresentationSharingUsingBfcp = value
        else:
            sqlutils = AXLSQLUtils(self.__configname__)
            sqlutils.update_bfcp(self._uuid, value)


class AppUser(AbstractCCMModel):
    pass


class CallPickupGroup(AbstractCCMModel):
    pass


class Css(AbstractCCMModel):
    pass


class CtiRoutingPoint(AbstractCCMModel):
    pass


class DevicePool(AbstractCCMModel):
    pass


class HuntList(AbstractCCMModel):
    pass


class HuntPilot(AbstractCCMModel):
    pass


class LineGroup(AbstractCCMModel):
    pass


class PhoneButtonTemplate(AbstractCCMModel):
    pass


class RoutePartition(AbstractCCMModel):
    pass


class VoiceMailPilot(AbstractCCMModel):
    pass


class VoiceMailProfile(AbstractCCMModel):
    pass


class RemoteDestination(AbstractCCMModel):

    def set_single_number_reach(self, value):
        """ Set single number reach flag is not possible in version 10.5
            see ticket: https://supportforums.cisco.com/discussion/12438721/single-number-reach-axl
            The workaround is again to set some value with SQL! Yupiiiii!
        """
        if not self.__attached__:
            raise exceptions.NotAttachedException('User is not attached')
        sqlutils = AXLSQLUtils(self.__configname__)
        sqlutils.set_single_number_reach(self._uuid, value)

    def get_single_number_reach(self):
        if not self.__attached__:
            raise exceptions.NotAttachedException('User is not attached')
        sqlutils = AXLSQLUtils(self.__configname__)
        value = sqlutils.get_single_number_reach(self._uuid)
        return value['enablesinglenumberreach'] == 't'


class RemoteDestinationProfile(AbstractCCMModel,
                               MixingAbstractLines,
                               MixingAbstractTemplate):
    @classmethod
    def template(cls, *args, **kwargs):
        return super(RemoteDestinationProfile, cls).template(*args, typeclass='Remote Destination Profile', **kwargs)


class TodAccess(AbstractCCMModel):
    pass


class TimeSchedule(AbstractCCMModel):

    def removeMembers(self, members):
        if not isinstance(members, list):
            members = [members]
        removeMembers = [dict(member=dict(timePeriodName=dict(_uuid=uuid))) for uuid in members]
        self.__client__.service.updateTimeSchedule(removeMembers=removeMembers, uuid=self._uuid)

    def addMembers(self, members):
        if not isinstance(members, list):
            members = [members]
        addMembers = [dict(member=dict(timePeriodName=dict(_uuid=uuid))) for uuid in members]
        self.__client__.service.updateTimeSchedule(addMembers=addMembers, uuid=self._uuid)


class TimePeriod(AbstractCCMModel):
    pass
