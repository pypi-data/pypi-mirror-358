#!/usr/bin/env python
"""
Docstring
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List, Dict
from numpy.typing import ArrayLike, NDArray
from functools import cached_property
from operator import itemgetter
import dataclasses as dc

import numpy as np
import pandas as pd
from astropy import table, units, constants

from .._constants import *
from ..utils import classproperty

if TYPE_CHECKING:
    from .Isochrone import Isochrone
    from .IsochroneFile import IsochroneFile

__all__ = ['default_formatting', 'padova_formatting', 'oldpadova_fomatting', 'oldpadova_fomatting_withlogage']


units.Zsun = units.def_unit('Zsun') # TODO could define PhysicalType "abundance" ?
units.integer = units.Quantity(1, dtype='int') # units.def_unit('integer', units.Quantity(1, dtype='int')) # TODO pull issue in astropy for integer dtype unit?


class _BaseFormatting:
    _zini = 'Z_ini'
    _unit_zini = units.LogUnit(units.Zsun)
    _age = 'Age'
    _unit_age = units.LogUnit(units.yr)
    _mini = 'M_ini'
    _mact = 'M_act'
    _unit_mass = units.Msun
    _radi = 'Radius'
    _unit_radi = units.Rsun
    _lum = 'Lum'
    _unit_lum = units.LogUnit(units.Lsun)
    _teff = 'T_eff'
    _unit_temp = units.LogUnit(units.Kelvin)
    _grav = 'Grav'
    _unit_grav = units.LogUnit(units.Gal)
    _label = 'Label'
    _unit_label = units.integer
    @classproperty
    def units_mapper(cls):
        return {
            cls._zini: cls._unit_zini,
            cls._age: cls._unit_age,
            cls._mini: cls._unit_mass,
            cls._mact: cls._unit_mass,
            cls._radi: cls._unit_radi,
            cls._lum: cls._unit_lum,
            cls._teff: cls._unit_temp,
            cls._grav: cls._unit_grav,
            cls._label: cls._unit_label
        }

@dc.dataclass()
class Formatting(_BaseFormatting):
    """
    Formatting object
    """
    i_age: int
    i_mini: int
    i_mact: int
    i_lum: int
    i_teff: int
    i_grav: int
    i_label: int
    lin_age: bool = False
    feh_sun: float = 0.0152  # TODO figure out that conversion situation

    @cached_property
    def format_mapper(self) -> Dict[int,str]:
        return {
            self.i_age: self._age,
            self.i_mini: self._mini,
            self.i_mact: self._mact,
            self.i_lum: self._lum,
            self.i_teff: self._teff,
            self.i_grav: self._grav,
            self.i_label: self._label
            }

    @cached_property
    def nonmagnitude_itemgetter(self) -> itemgetter:
        return itemgetter(*self.format_mapper.keys())

    def metallicity_converter(self, metallicity: ArrayLike) -> NDArray:
        return np.log10(metallicity/np.array(self.feh_sun))

    def qtable_per_age_from_isochronefile(self, iso_file: IsochroneFile) -> table.QTable:
        isochrone: Isochrone = iso_file._isochrone
        units_mapper = self.units_mapper
        column_names: Tuple[str] = self.nonmagnitude_itemgetter(iso_file.data.keys()) + isochrone.magnitude_itemgetter(iso_file.data.keys())
        final_names: List[str] = list(self.format_mapper.values()) + isochrone.mag_names
        column_mapper: Dict[str,str] = dict(zip(column_names, final_names))
        reduced_data: pd.DataFrame = iso_file.data[column_names].to_pandas().rename(columns=column_mapper).reset_index().sort_values([self._age, self._mini, 'index']).drop('index', axis=1)
        reduced_data.insert(0, self._zini, self.metallicity_converter(iso_file.metallicity))
        reduced_data.insert(5, self._radi, np.sqrt(constants.G*reduced_data[self._mact].to_numpy()*self._unit_mass/(reduced_data[self._grav].to_numpy()*self._unit_grav).to(self._unit_grav.physical_unit)).to(self._unit_radi).value)
        if self.lin_age:
            reduced_data[self._age] = np.log10(reduced_data[self._age])
        return {
            age: table.QTable({
                key: units.Magnitude(value)
                if key in isochrone.mag_names
                else value*units_mapper[key]
                for key,value in df.to_dict(orient='list').items()
                })
            for age,df in reduced_data.groupby(self._age)
            }


default_formatting = Formatting(0, 1, 2, 3, 4, 5, 6, False)  # Python and others
padova_formatting = Formatting(2, 3, 5, 6, 7, 8, 9, False)  # CTIO__DECam, LSST_DP0, Roman, Euclid, JWST
oldpadova_fomatting = Formatting(1, 2, 3, 4, 5, 6, 7, True)  # WFIRST, LSST, GAIA__0, GAIA__DR2
oldpadova_fomatting_withlogage = Formatting(1, 2, 3, 4, 5, 6, 7, False)  # WFIRST+HST__WFC3


if __name__ == '__main__':
    raise NotImplementedError()
