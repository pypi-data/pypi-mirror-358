#!/usr/bin/env python
"""
Contains the Survey class definition

Please note that this module is private. The Survey class is
available in the main ``Galaxia`` namespace - use that instead.
"""
from __future__ import annotations
from types import MappingProxyType
from typing import TYPE_CHECKING, Optional, Union, Tuple, List, Set, Dict, Iterable
from numpy.typing import NDArray, ArrayLike
from warnings import warn
from functools import cached_property
import re
import pathlib
from pprint import PrettyPrinter

from ._constants import *
from ._templates import *
from ._defaults import *
from .utils import CallableDFtoInt, execute, lexicalorder_dict, hash_iterable
from . import photometry
from .photometry.PhotoSystem import PhotoSystem
from .Output import Output

if TYPE_CHECKING:
    from . import Input

__all__ = ['Survey']


class Survey:
    def __init__(self, input: Input, photo_sys: Union[str,List[str]] = DEFAULT_PSYS, surveyname: str = DEFAULT_SURVEYNAME, verbose: bool = True) -> None:
        """
            Driver to exploit the input object and run Galaxia with it.

            Call signature::

                survey = Survey(input,
                                photo_sys={DEFAULT_PSYS},
                                surveyname='{DEFAULT_SURVEYNAME}')

            Parameters
            ----------
            input : :obj:`Input`
                Input object storing the particle data.
            
            photo_sys : string or list
                Name(s) of the photometric system(s) Galaxia should use to
                generate the survey. Default to {DEFAULT_PSYS}.
                Available photometric systems can be found with the photometry
                submodule - please refer to its documentation for further
                details.

            surveyname : string
                Optional name Galaxia should use for the output files. Default
                to '{DEFAULT_SURVEYNAME}'.
        """
        self.__surveyname: str = surveyname
        self.__input: Input = input
        self.__photosystems: List[PhotoSystem] = self.prepare_photosystems(photo_sys)
        self.__verbose: bool = verbose
        self.__fileparam: MappingProxyType[str, Union[str,float,int]] = None
        self.__extraparam: MappingProxyType[str, Union[str,float,int]] = None
        self.__output: Output = None

    __init__.__doc__ = __init__.__doc__.format(DEFAULT_SURVEYNAME=DEFAULT_SURVEYNAME,
                                               DEFAULT_PSYS=DEFAULT_PSYS)
    
    def __repr__(self) -> str:
        cls = self.__class__.__name__
        description = ', '.join([(f"{prop}={getattr(self, prop)}") for prop in ['surveyname', 'photo_sys']])
        return f'{cls}({description})'

    @classmethod
    def prepare_photosystems(cls, photo_sys: str) -> list[PhotoSystem]:
        if isinstance(photo_sys, str):
            photo_sys = [photo_sys]
        return [photometry.available_photo_systems[psys] for psys in photo_sys]

    @classmethod
    def set_isochrones_from_photosys(cls, photo_sys: str) -> list[PhotoSystem]:
        warn('This class method will be deprecated, please use instead class method prepare_photosystems', DeprecationWarning, stacklevel=2)
        return cls.prepare_photosystems(photo_sys)

    def _prepare_survey_parameters_and_output(self, cmd_magnames: Union[str,Dict[str,str]], n_gens: Iterable[int], **kwargs) -> None:
        photosys = self.photosystems[0]
        cmd_magnames: str = photosys.check_cmd_magnames(cmd_magnames)
        parameters: Dict[str, Union[str,float,int]] = DEFAULTS_FOR_PARFILE.copy()
        parameters.update(**{FTTAGS.photo_categ: photosys.category, FTTAGS.photo_sys: photosys.name, FTTAGS.mag_color_names: cmd_magnames, FTTAGS.nres: self.ngb}, **kwargs)
        n_gen_tag_length = len(str(max(n_gens)))
        self.__fileparam = MappingProxyType(parameters)
        self.__extraparam = MappingProxyType({
            **{f"n_gen_{i:0{n_gen_tag_length}d}": n for i,n in enumerate(n_gens)},
            **{k: v for n,PS in enumerate(self.photosystems[1:], start=1)
                    for k,v in zip(FTTAGS.append_photo(n), PS.categ_and_name)}
                    })
        self.__output = Output(self)

    def _write_parameter_file(self) -> Tuple[pathlib.Path, Dict[str, Union[str,float,int]]]:
        parameters: Dict[str, Union[str,float,int]] = self.fileparam
        surveyname_hash: str = self.surveyname_hash
        parfile: pathlib.Path = self.inputdir / PARFILENAME_TEMPLATE.substitute({FTTAGS.name: surveyname_hash})  # TODO make temporary? create a global record of temporary files?
        parfile_text: str = PARFILE_TEMPLATE.substitute({FTTAGS.output_file: surveyname_hash, **parameters})
        if ((parfile.read_text() != parfile_text # proceed if parfile_text is not in parfile,
            if parfile.exists()                  # only if parfile exist,
            else True)                           # otherwise proceed if doesn't exist
            if self.caching else True):          # -> proceed anyway if self.caching is False
            parfile.write_text(parfile_text)
        return parfile, parameters

    def _run_survey(self, parfile: pathlib.Path, n_gens: Iterable[int], max_gen_workers: int) -> None:
        cmds = [RUN_TEMPLATE.substitute(**{
            CTTAGS.hdim_block : '' if self.hdim is None
                                else HDIMBLOCK_TEMPLATE.substitute(**{CTTAGS.hdim: self.hdim}),
            CTTAGS.nfile      : self.inputname_hash,
            CTTAGS.ngen       : ngen,
            CTTAGS.parfile    : parfile
        }) for ngen in n_gens]
        execute(cmds, max_workers=max_gen_workers, verbose=self.verbose)

    def _append_survey(self, photosystem: PhotoSystem, max_gen_workers: Optional[int]) -> None:
        if max_gen_workers is None:
            max_gen_workers = len(list(self.__ebf_output_files_glob))
        cmds = [APPEND_TEMPLATE.substitute(**{
            CTTAGS.pcat     : photosystem.category,
            CTTAGS.psys     : photosystem.name,
            CTTAGS.filename : filename
        }) for filename in self.__ebf_output_files_glob]
        execute(cmds, max_workers=max_gen_workers, verbose=self.verbose)

    def _vanilla_survey(self, cmd_magnames: Union[str,Dict[str,str]] = DEFAULT_CMD,
                              fsample: float = 1, input_sorter: ArrayLike = None,
                              n_jobs: int = None, n_gens: Union[int, Iterable[int]] = (0,),
                              max_gen_workers: int = None, **kwargs) -> None:
        """
            TODO
        """
        if isinstance(n_jobs, int):
            n_gens = n_jobs
            warn('Keyword argument n_jobs will be deprecated, please use instead keyword argument n_gens. Consider also reading doc regarding keyword argument max_pp_workers.', DeprecationWarning, stacklevel=2)
        if isinstance(n_gens, int):
            n_gens = range(n_gens)
        if max_gen_workers is None:
            max_gen_workers = len(n_gens)
        else:
            warn('The keyword argument max_gen_workers is currently not implemented.', stacklevel=2)
        self.input.input_sorter = input_sorter
        self._prepare_survey_parameters_and_output(cmd_magnames, n_gens, fsample=fsample, **kwargs)
        inputname, parfile, for_parfile = self.input.prepare_input(self)
        #
        self.check_state_before_running(description='run_survey_complete')(self._run_survey)(parfile, n_gens=n_gens, max_gen_workers=max_gen_workers)
        for photosystem in self.photosystems[1:]:
            self.check_state_before_running(description=f'append_{photosystem.name}_complete', level=1)(self._append_survey)(photosystem, max_gen_workers=max_gen_workers)

    def make_survey(self, *, verbose: bool = True, partitioning_rule: CallableDFtoInt = None,
                             max_pp_workers: int = 1, pp_auto_flush: bool = True, **kwargs) -> Output:
        """
            Driver to exploit the input object and run Galaxia with it.
            
            Call signature::
            
                output = self.make_survey(cmd_magnames= '{DEFAULT_CMD}' ,
                                          fsample=1, verbose=True, **kwargs)
            
            Parameters
            ----------
            cmd_magnames : string
                Names of the filters Galaxia should use for the color-
                magnitude diagram box selection. The given string must meet
                the following format::

                    "band1,band2-band3"
                
                where ``band1`` is the magnitude filter and ``(band2, band3)``
                are the filters that define the ``band2-band3`` color index.
                The filter names must correspond to filters that are part of
                the first chosen photometric system in photo_sys. Default to
                ``'{DEFAULT_CMD}'``
            
            fsample : float
                Sampling rate from 0 to 1 for the resulting synthetic star
                survey. 1 returns a full sample while any value under returns
                partial surveys. Default to 1.

            input_sorter : array_like
                TODO
            
            n_gens, n_jobs : int or iterable of int
                Number of independent catalog generations ran in parallel. Can
                also receive an iterable containing each generation number to
                run in parallel. Default to 1. Usage of n_jobs is deprecated
                and will be removed.

            max_gen_workers : int
                CURRENTLY NOT PROPERLY IMPLEMENTED
                Maximum number of workers to parallelize the initial catalog
                generations. Default to the number of independent generations
                in n_gens.
            
            max_pp_workers : int
                Maximum number of workers to parallelize the post-processing
                pipelines after the initial catalog generation. Default to 1.
            
            pp_auto_flush : bool
                TODO
            
            verbose : bool
                Verbose boolean flag to allow pipeline to print what it's doing
                to stdout. Default to True.
            
            partitioning_rule : TODO
                TODO
            
            parfile : string
                Name of file where Input should save the parameters for
                Galaxia. Default to '{DEFAULT_PARFILE}'
            
            output_dir : string or pathlib.Path
                Path to directory where to save the input/output files of
                Galaxia. Default to '{TTAGS_output_dir}'
            
            app_mag_lim_lo, app_mag_lim_hi, abs_mag_lim_lo, abs_mag_lim_hi, color_lim_lo, color_lim_hi : float
                These allow to specify the limits of the chosen color-magnitude
                diagram box selection (``lo`` for lower and ``hi`` for upper).
                ``app_mag``, ``abs_mag`` and ``color`` represent respectively
                limits in apparent magnitudes, absolute magnitudes and color
                index. Default values follow those set in the dictionary::
                {DEFAULT_CMD_BOX} 
            
            rSun0, rSun1, rSun2 : float
                Coordinates for the observer position in kpc. Respectively
                default to::

                    {TTAGS_rSun0}, {TTAGS_rSun1} & {TTAGS_rSun2}
            
            vSun0, vSun1, vSun2 : float
                Coordinates for the observer velocity in km/s. Respectively
                default to::

                    {TTAGS_vSun0}, {TTAGS_vSun1} & {TTAGS_vSun2}
            
            r_max, r_min : float
                Extent of the shell of radii from observer location within
                which particles should be considered by Galaxia. Respectively
                default to::

                    {TTAGS_r_max} & {TTAGS_r_min}
            
            rand_seed : int
                Seed to be used by Galaxia's pseudorandom number generator.
                Default to {TTAGS_rand_seed}

            nstart : int
                Index at which to start indexing synthetic stars. Default
                to {TTAGS_nstart}

            longitude, latitude : float
                Currently not implemented. Respectively default to::
                
                    {TTAGS_longitude} & {TTAGS_latitude}
            
            star_type : int
                Currently not implemented. Default to {TTAGS_star_type}

            geometry_opt : int
                Currently not implemented. Default to {TTAGS_geometry_opt}

            survey_area : float
                Currently not implemented. Default to {TTAGS_survey_area}
                
            pop_id : int
                Currently not implemented. Default to {TTAGS_pop_id}

            warp_flare_on : int
                Currently not implemented. Default to {TTAGS_warp_flare_on}

            photo_error : int
                Currently not implemented. Default to {TTAGS_photo_error}

            Returns
            -------
            output : :obj:`Output`
                Handler with utilities to utilize the output survey and its
                data.
        """  # TODO Move documentation around to the subroutines where they should go
        self.verbose = verbose
        self._vanilla_survey(**kwargs)
        self.output.read_galaxia_output(partitioning_rule, max_pp_workers, pp_auto_flush)
        self.output.post_process_output()
        return self.output

    make_survey.__doc__ = make_survey.__doc__.format(DEFAULT_CMD=DEFAULT_CMD,
                                                     DEFAULT_PARFILE=DEFAULT_PARFILE,
                                                     DEFAULT_CMD_BOX=('\n'+PrettyPrinter(width=60).
                                                                      pformat(DEFAULT_CMD_BOX)).
                                                                     replace('\n','\n                  '),
                                                     **{f"TTAGS_{key}": val
                                                        for key,val in DEFAULTS_FOR_PARFILE.items()})

    @property
    def has_no_fileparam(self) -> bool:
        return self.__fileparam is None

    @property
    def fileparam(self) -> Dict[str, Union[str,float,int]]:
        if self.has_no_fileparam:
            raise RuntimeError("Survey hasn't been made yet, run method `make_survey` first")
        else:
            return dict(self.__fileparam)

    @property
    def _extraparam(self) -> Dict[str, Union[str,float,int]]:
        return self.__extraparam

    @property
    def parameters(self) -> Dict[str, Union[str,float,int]]:
        return {**self.fileparam, **self._extraparam}

    @property
    def n_gens(self) -> List[int]:
        return list(lexicalorder_dict({
            int(n_gen[0]): value
            for key, value in self._extraparam.items()
            if (n_gen:=re.findall("n_gen_(\d*)", key))
            }).values())

    @property
    def fsample(self) -> float:
        return len(self.n_gens)*self.fileparam[FTTAGS.fsample]

    @cached_property
    def _surveyhash(self) -> bytes:
        return hash_iterable(map(lambda el: str(el).encode(HASH_ENCODING),
                                 lexicalorder_dict(self.parameters).values()))

    @property
    def hash(self) -> str:
        return self._surveyhash.decode()

    @property
    def surveyname(self) -> str:
        return self.__surveyname
    
    @property
    def append_hash(self) -> bool:
        return self.input.append_hash

    @property
    def surveyname_hash(self) -> str:
        return self.surveyname + (f"_{self.hash[:7]}" if self.append_hash else "")
    
    @property
    def input(self) -> Input:
        return self.__input

    @property
    def photosystems(self) -> List[PhotoSystem]:
        return self.__photosystems

    @property
    def isochrones(self):
        warn('This property will be deprecated, please use instead property photosystems', DeprecationWarning, stacklevel=2)
        return self.photosystems

    @property
    def photo_sys(self) -> Set[str]:
        return {photosystem.key for photosystem in self.photosystems}

    @property
    def verbose(self) -> bool:
        return self.__verbose

    @verbose.setter
    def verbose(self, value: Optional[bool]) -> None:
        if value is not None:
            self.__verbose = value

    @property
    def has_no_output(self) -> bool:
        return self.__output is None

    @property
    def output(self):
        if self.has_no_output:
            raise RuntimeError("Survey hasn't been made yet, run method `make_survey` first")
        else:
            return self.__output
    
    @property
    def caching(self) -> bool:
        return self.input.caching

    @property
    def hdim(self) -> int:
        return self.input.hdim
    
    @property
    def inputname_hash(self) -> str:
        return self.input.name_hash
    
    @property
    def inputdir(self) -> pathlib.Path:
        return self.input._input_dir
    
    @property
    def ngb(self) -> int:
        return self.input.ngb

    @property
    def check_state_before_running(self):
        return self.output.check_state_before_running

    @property
    def __ebf_output_files_glob(self):
        return self.output._ebf_glob


if __name__ == '__main__':
    raise NotImplementedError()
