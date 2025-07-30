"""
This module provides task scheduling classes for the management of OmniTracker
SRR (NHRR) processing for Department UMH.
    SRR: Sustainability Risk Rating
    NHRR: Nachhaltigkeits Risiko Rating
"""
from ka_uts_dfr.pddf import PdDf
from ka_uts_path.pathnm import PathNm
from ka_uts_xls.pd.ioipathwb import IoiPathWb as PdIoiPathWb

from ka_uts_eviq.xls.utils import Evup
from ka_uts_eviq.xls.cfg import Cfg

import pandas as pd

from typing import Any, TypeAlias
TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyPath = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnPdDf = None | TyPdDf


class TaskIn:

    kwargs_wb = dict(dtype=str, keep_default_na=False, engine='calamine')

    @classmethod
    def evupadm(cls, kwargs: TyDic) -> tuple[TnAoD, TyDoAoD]:
        """
        Administration processsing for evup
        """
        _cfg = kwargs.get('Cfg', Cfg)
        _in_path_evin = PathNm.sh_path(_cfg.InPath.evin, kwargs)
        _in_path_evex = PathNm.sh_path(_cfg.InPath.evex, kwargs)
        _in_sheet_evin_adm = _cfg.InSheet.evin_adm
        _in_sheet_evex = _cfg.InSheet.evex

        _aod_evin: Any = PdIoiPathWb.read_wb_to_aod_or_doaod(
                _in_path_evin, _in_sheet_evin_adm, **cls.kwargs_wb)
        _pddf_evex: Any = PdIoiPathWb.read_wb_to_df_or_dodf(
                _in_path_evex, _in_sheet_evex, **cls.kwargs_wb)
        _doaod_vfy: TyDoAoD = {}
        _aod_evup_adm: TyAoD = Evup.sh_aod_evup_adm(
            _aod_evin, _pddf_evex, _doaod_vfy, kwargs)

        return _aod_evup_adm, _doaod_vfy

    @classmethod
    def evupdel(cls, kwargs: TyDic) -> tuple[TnAoD, TyDoAoD]:
        """
        Delete processsing for evup
        """
        _cfg = kwargs.get('Cfg', Cfg)
        _in_path_evin = PathNm.sh_path(_cfg.InPath.evin, kwargs)
        _in_path_evex = PathNm.sh_path(_cfg.InPath.evex, kwargs)
        _in_sheet_evin_adm = _cfg.InSheet.evin_adm
        _in_sheet_evin_del = _cfg.InSheet.evin_del
        _in_sheet_evex = _cfg.InSheet.evex

        _pddf_evin_adm: TnPdDf = PdIoiPathWb.read_wb_to_df(
                _in_path_evin, _in_sheet_evin_adm, **cls.kwargs_wb)
        _aod_evin_del: TnAoD = PdIoiPathWb.read_wb_to_aod(
                _in_path_evin, _in_sheet_evin_del, **cls.kwargs_wb)

        _doaod_vfy: TyDoAoD = {}
        _sw_del_use_evex: TyBool = kwargs.get('sw_del_use_evex', True)
        if _sw_del_use_evex:
            _pddf_evex: TnPdDf = PdIoiPathWb.read_wb_to_df(
                    _in_path_evex, _in_sheet_evex, **cls.kwargs_wb)
            _aod_evex: TnAoD = PdDf.to_aod(_pddf_evex)
            _aod_evup_del = Evup.sh_aod_evup_del_use_evex(
                    _aod_evin_del, _pddf_evin_adm,
                    _aod_evex, _pddf_evex, _doaod_vfy, kwargs)
        else:
            _aod_evup_del = Evup.sh_aod_evup_del(
                    _aod_evin_del, _pddf_evin_adm, _doaod_vfy, kwargs)

        return _aod_evup_del, _doaod_vfy

    @classmethod
    def evupreg(cls, kwargs: TyDic) -> tuple[TnAoD, TnAoD, TyDoAoD]:
        """
        Regular processsing for evup
        """
        _cfg = kwargs.get('Cfg', Cfg)
        _in_path_evin = PathNm.sh_path(_cfg.InPath.evin, kwargs)
        _in_path_evex = PathNm.sh_path(_cfg.InPath.evex, kwargs)
        _in_sheet_evin_adm = _cfg.InSheet.evin_adm
        _in_sheet_evin_del = _cfg.InSheet.evin_del
        _in_sheet_evex = _cfg.InSheet.evex

        _pddf_evin_adm: TnPdDf = PdIoiPathWb.read_wb_to_df(
                _in_path_evin, _in_sheet_evin_adm, **cls.kwargs_wb)
        _aod_evin_adm: TnAoD = PdDf.to_aod(_pddf_evin_adm)
        _aod_evin_del: TnAoD = PdIoiPathWb.read_wb_to_aod(
                _in_path_evin, _in_sheet_evin_del, **cls.kwargs_wb)

        _pddf_evex: TnPdDf = PdIoiPathWb.read_wb_to_df(
                _in_path_evex, _in_sheet_evex, **cls.kwargs_wb)
        _aod_evex: TnAoD = PdDf.to_aod(_pddf_evex)

        _doaod_vfy: TyDoAoD = {}
        _aod_evup_adm: TyAoD = Evup.sh_aod_evup_adm(
            _aod_evin_adm, _pddf_evex, _doaod_vfy, kwargs)

        _sw_del_use_evex: TyBool = kwargs.get('sw_del_use_evex', True)
        if _sw_del_use_evex:
            _aod_evup_del = Evup.sh_aod_evup_del_use_evex(
                _aod_evin_del, _pddf_evin_adm,
                _aod_evex, _pddf_evex, _doaod_vfy, kwargs)
        else:
            _aod_evup_del = Evup.sh_aod_evup_del(
                _aod_evin_del, _pddf_evin_adm, _doaod_vfy, kwargs)

        return _aod_evup_adm, _aod_evup_del, _doaod_vfy
