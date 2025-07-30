"""
This module provides utility classes for the management of OmniTracker
EcoVadis NHRR (Nachhaltigkeits Risiko Rating) processing for Department UMH
"""
from __future__ import annotations
from typing import Any, TypeAlias

import pandas as pd

from ka_uts_dic.dic import Dic
from ka_uts_dic.doa import DoA

from ka_uts_eviq.xls.cfg import Cfg

TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyAoStr = list[str]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyDoB = dict[Any, bool]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyPath = str
TyStr = str
TyTup = tuple[Any]
TyTask = Any
TyDoPdDf = dict[Any, TyPdDf]
TyPdDf_DoPdDf = TyPdDf | TyDoPdDf
TyToAoDDoAoD = tuple[TyAoD, TyDoAoD]

TnDic = None | TyDic
TnAoD = None | TyAoD
TnDoAoA = None | TyDoAoA
TnDoAoD = None | TyDoAoD
TnPdDf = None | TyPdDf
TnStr = None | str

CfgUtils = Cfg.Utils


class EvinVfy:
    """
    OmniTracker EcoVadis class
    """
    @staticmethod
    def vfy_duns(d_evin: TyDic, doaod_vfy: TyDoAoD) -> tuple[TyBool, TnStr]:
        """
        Verify DUNS number
        """
        _duns: TnStr = Dic.get(d_evin, CfgUtils.evin_key_duns)
        if not _duns:
            DoA.append_unique_by_key(doaod_vfy, 'duns_is_empty', d_evin)
            return False, _duns
        if not _duns.isdigit():
            DoA.append_unique_by_key(doaod_vfy, 'duns_is_not_numeric', d_evin)
            return False, _duns
        if len(_duns) < 9:
            _duns = f"{_duns:09}"
        return True, _duns

    @staticmethod
    def vfy_cmpdinm(d_evin: TyDic, doaod_vfy: TyDoAoD) -> TyBool:
        """
        Verify Company display name
        """
        _cmpdinm = Dic.get(d_evin, CfgUtils.evin_key_cmpdinm)
        if not _cmpdinm:
            DoA.append_unique_by_key(doaod_vfy, 'cmpdinm_is_empty', d_evin)
            return False
        return True

    @staticmethod
    def vfy_regno(d_evin: TyDic, doaod_vfy: TyDoAoD) -> TyBool:
        """
        Verify Registration number
        """
        _cmpdinm = Dic.get(d_evin, CfgUtils.evin_key_regno)
        if not _cmpdinm:
            DoA.append_unique_by_key(doaod_vfy, 'regno_is_empty', d_evin)
            return False
        return True

    @staticmethod
    def vfy_coco(d_evin: TyDic, doaod_vfy: TyDoAoD) -> TyBool:
        """
        Verify Country Code
        """
        _coco: TnStr = Dic.get(d_evin, CfgUtils.evin_key_coco)
        if not _coco:
            DoA.append_unique_by_key(doaod_vfy, 'coco_is_empty', d_evin)
            return False
        else:
            import pycountry
            try:
                country = pycountry.countries.get(alpha_2=_coco.upper())
            except KeyError:
                DoA.append_unique_by_key(doaod_vfy, 'coco_is_invalid', d_evin)
                return False
        return True

    @staticmethod
    def vfy_objectid(d_evin: TyDic, doaod_vfy: TyDoAoD) -> TyBool:
        """
        Verify Country Code
        """
        _objectid = Dic.get(d_evin, CfgUtils.evin_key_objectid)
        if not _objectid:
            DoA.append_unique_by_key(doaod_vfy, 'objectid_is_empty', d_evin)
            return False
        return True

    @staticmethod
    def vfy_town(d_evin: TyDic, doaod_vfy: TyDoAoD) -> TyBool:
        """
        Verify Town by Country Code
        """
        _town: TnStr = Dic.get(d_evin, CfgUtils.evin_key_town)
        if not _town:
            DoA.append_unique_by_key(doaod_vfy, 'town_is_empty', d_evin)
            return False
        else:
            _coco = Dic.get(d_evin, CfgUtils.evin_key_coco)
            if not _coco:
                return True
            from geopy.geocoders import Nominatim
            from geopy.exc import GeocoderTimedOut
            geolocator = Nominatim(user_agent="geo_verifier")
            try:
                location = geolocator.geocode(_town)
                if location is None:
                    DoA.append_unique_by_key(doaod_vfy, 'town_is_invalid', d_evin)
                else:
                    if _coco.lower() not in location.address.lower():
                        DoA.append_unique_by_key(
                                doaod_vfy, 'town_is_invalid', d_evin)
                        return False
            except GeocoderTimedOut:
                DoA.append_unique_by_key(doaod_vfy, 'town_is_invalid', d_evin)
                return False
        return True

    @staticmethod
    def vfy_poco(d_evin: TyDic, doaod_vfy: TyDoAoD) -> TyBool:
        """
        Verify Post Code
        """
        _poco: TnStr = Dic.get(d_evin, CfgUtils.evin_key_poco)
        if not _poco:
            DoA.append_unique_by_key(doaod_vfy, 'poco_is_empty', d_evin)
            return False
        else:
            _coco = Dic.get(d_evin, CfgUtils.evin_key_coco)
            from postal_codes_tools.postal_codes import verify_postal_code_format
            if not verify_postal_code_format(postal_code=_poco, country_iso2=_coco):
                DoA.append_unique_by_key(doaod_vfy, 'poco_is_invalid', d_evin)
                return False
        return True

    @staticmethod
    def vfy_iq_id(d_evin: TyDic, doaod_vfy: TyDoAoD) -> TyBool:
        """
        Verify Company display name
        """
        _iq_id = Dic.get(d_evin, CfgUtils.evin_key_iq_id)
        if not _iq_id:
            DoA.append_unique_by_key(doaod_vfy, 'iq_id_is_empty', d_evin)
            return False
        return True


class EvinVfyAdm:
    """
    OmniTracker EcoVadis class
    """
    @classmethod
    def vfy_d_evin(
            cls, d_evin: TyDic, doaod_vfy: TyDoAoD, kwargs: TyDic
    ) -> TyBool:
        # Set verification summary switch
        _d_sw: TyDoB = {}

        # Verify DUNS
        if kwargs.get('sw_vfy_duns', True):
            _d_sw['duns'], _duns = EvinVfy.vfy_duns(d_evin, doaod_vfy)
            Dic.set_by_key(d_evin, CfgUtils.evin_key_duns, _duns)

        # Verify Country display name
        if kwargs.get('sw_vfy_cmpdinm', True):
            _d_sw['cmpdinm'] = EvinVfy.vfy_cmpdinm(d_evin, doaod_vfy)

        # Verify Country display name
        if kwargs.get('sw_vfy_regno', True):
            _d_sw['regno'] = EvinVfy.vfy_regno(d_evin, doaod_vfy)

        # Verify Country Code
        if kwargs.get('sw_vfy_coco', True):
            _d_sw['coco'] = EvinVfy.vfy_coco(d_evin, doaod_vfy)

        # Verify ObjectID
        if kwargs.get('sw_vfy_objectid', True):
            _d_sw['objectid'] = EvinVfy.vfy_objectid(d_evin, doaod_vfy)

        # Verify Town in Country
        if kwargs.get('sw_vfy_town', False):
            _d_sw['town'] = EvinVfy.vfy_town(d_evin, doaod_vfy)

        # Verify Postal Code
        if kwargs.get('sw_vfy_poco', True):
            _d_sw['poco'] = EvinVfy.vfy_poco(d_evin, doaod_vfy)

        _sw_use_duns = kwargs.get('sw_use_duns', True)
        if _sw_use_duns:
            return _d_sw['duns'] and _d_sw['cmpdinm']

        if (_d_sw['duns'] and _d_sw['cmpdinm']) or \
           (_d_sw['regno'] and _d_sw['coco'] and _d_sw['cmpdinm']) or \
           (_d_sw['cmpnm'] and _d_sw['coco'] and _d_sw['cmpdinm']):
            return True

        return False

    @classmethod
    def vfy_aod_evin(
            cls, aod_evin, doaod_vfy, kwargs: TyDic
    ) -> TyAoD:
        _aod_evin: TyAoD = []
        for _d_evin in aod_evin:
            _sw: bool = cls.vfy_d_evin(_d_evin, doaod_vfy, kwargs)
            if _sw:
                _aod_evin.append(_d_evin)
        return _aod_evin


class EvinVfyDel:
    """
    OmniTracker EcoVadis class
    """
    @classmethod
    def vfy_d_evin(
            cls, d_evin: TyDic, doaod_vfy: TyDoAoD, kwargs: TyDic
    ) -> TyBool:
        # Set verification summary switch
        _d_sw: TyDoB = {}

        # Verify ObjectID
        if kwargs.get('sw_vfy_objectid', True):
            _d_sw['objectid'] = EvinVfy.vfy_objectid(d_evin, doaod_vfy)

        # Verify EcoVadis IQ Id
        if kwargs.get('sw_iq_id', False):
            _d_sw['iq_id'] = EvinVfy.vfy_iq_id(d_evin, doaod_vfy)

        if _d_sw['objectid'] or _d_sw['iq_id']:
            return True

        return False

    @classmethod
    def vfy_aod_evin(
            cls, aod_evin, doaod_vfy, kwargs: TyDic
    ) -> TyAoD:
        _aod_evin: TyAoD = []
        for _d_evin in aod_evin:
            _sw: bool = cls.vfy_d_evin(_d_evin, doaod_vfy, kwargs)
            if _sw:
                _aod_evin.append(_d_evin)
        return _aod_evin
