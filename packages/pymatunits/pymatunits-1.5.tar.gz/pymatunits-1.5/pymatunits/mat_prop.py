"""
Material property definitions and interfaces for multiple CAE packages
as part of `pymatunits`

Copyright (C) 2023 Adam Cox, Coleby Friedland

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

mat_prop : Material property module originally built to work with
    Abaqus, using the categorical definitions from Abaqus. Capability
    added to interact with Nastran using nastran_utils.

Dependencies
-----------------  -----------------------------------------------------
Abaqus              Code must be Python 2.7 compatible with no outside
                    packages to be used in Abaqus Python interpreter.
nastran_utils       Module written by Adam Cox to interact with Nastran
                    in object-oriented fashion. (Must have Nastran
                    obviously if you wish to use the created model)
pint                Physical quantity manipulation package
numpy               For mean function and indirectly in utils
"""
from os.path import isfile
from math import sqrt
import json
from json.decoder import JSONDecodeError
from pandas import DataFrame
from . import logger, numerical_tolerance
from .units import Q_, convert, UnitSystem, UnitMixin
from .utils import rotate_vector
try:
    from abaqusConstants import ENGINEERING_CONSTANTS
except ImportError:
    ENGINEERING_CONSTANTS = 'ENGINEERING_CONSTANTS'
try:
    from abaqusConstants import ISOTROPIC
except ImportError:
    ISOTROPIC = 'ISOTROPIC'
try:
    from abaqusConstants import LAMINA
except ImportError:
    LAMINA = 'LAMINA'
try:
    from abaqusConstants import TRACTION
except ImportError:
    TRACTION = 'TRACTION'
try:
    from abaqusConstants import ENERGY
except ImportError:
    ENERGY = 'ENERGY'
try:
    from abaqusConstants import BK
except ImportError:
    BK = 'BK'
try:
    from abaqusConstants import CARTESIAN
except ImportError:
    CARTESIAN = 'CARTESIAN'
try:
    from abaqusConstants import SHELL
except ImportError:
    SHELL = 'SHELL'
try:
    from abaqusConstants import AXIS_1
except ImportError:
    AXIS_1 = 'AXIS_1'
try:
    from abaqusConstants import AXIS_2
except ImportError:
    AXIS_2 = 'AXIS_2'
try:
    from abaqusConstants import AXIS_3
except ImportError:
    AXIS_3 = 'AXIS_3'
try:
    from abaqusConstants import STACK_1
except ImportError:
    STACK_1 = 'STACK_1'
try:
    from abaqusConstants import STACK_2
except ImportError:
    STACK_2 = 'STACK_2'
try:
    from abaqusConstants import STACK_3
except ImportError:
    STACK_3 = 'STACK_3'
try:
    from abaqusConstants import SPECIFY_ORIENT
except ImportError:
    SPECIFY_ORIENT = 'SPECIFY_ORIENT'
try:
    from abaqusConstants import SPECIFY_THICKNESS
except ImportError:
    SPECIFY_THICKNESS = 'SPECIFY_THICKNESS'
try:
    from abaqusConstants import VALUE
except ImportError:
    VALUE = 'VALUE'
try:
    from abaqusConstants import SOLID
except ImportError:
    SOLID = 'SOLID'
try:
    from abaqusConstants import CONTINUUM_SHELL
except ImportError:
    CONTINUUM_SHELL = 'CONTINUUM_SHELL'
try:
    import nastran_utils
except ImportError:
    nastran_utils = None

Quantity = Q_

ROOM_TEMP = Q_(70.0, 'degF')


def check_value(value, type_, unit_system):
    try:
        value = type_(value)
    except TypeError:  # type is unit string
        try:
            magnitude, unit = value
        except TypeError:  # float
            unit = getattr(unit_system, type_).units
            value = Q_(float(value), unit)
        else:  # (magnitude, unit) pair
            value = Q_(float(magnitude), unit)
    return value


def get_value(value, type_, unit_system):
    try:
        value.magnitude
    except AttributeError:  # not a quantity
        try:
            value = type_(value)
        except TypeError:  # type is unit string
            unit = getattr(unit_system, type_)
            value = float(value), str(unit.units)
    else:  # quantity
        value = value.magnitude, str(value.units)
    return value


class Composite(UnitMixin):
    arg_units = {
        'name': str,
        'ply_materials': None,
        'orientations': 'angle',
        'unit_system': None,
        'layup_thickness': 'length',
        'thicknesses': 'length',
        'ply_names': str,
        'symmetric': bool
    }

    def __init__(self, name: str, ply_materials: list,
                 orientations: list[Quantity], unit_system: UnitSystem,
                 layup_thickness: Quantity = None,
                 thicknesses: list[Quantity] = None,
                 ply_names: list[str] = None,
                 symmetric: bool = False):
        """
        Composite object consisting of Material objects with their
        corresponding ply orientations and names

        Parameters
        ----------
        name : str
            Name of composite layup
        unit_system : UnitSystem
            Values will be converted to quantities in this unit system
            for internal consistency
        ply_materials : List[Material]
            List of Material objects to use for plies
        orientations : List[Quantity]
            List of orientation angles
        unit_system : UnitSystem
            Values will be converted to quantities in this unit system
            for internal consistency
        layup_thickness : float, optional
            Thickness of entire layup. Entire this or thicknesses must
            be defined.
        thicknesses : List[Quantity], optional
            List of thickness of each ply. Either this or
            layup_thickness must be defined. If both are defined,
            layup_thickness will be used.
        ply_names : List[str], optional
            List of ply names for building laminate. Default value is
            "ply-{#}"
        symmetric : bool, optional
            Flag for laminate symmetry. Currently only used in Abaqus
            section definition. Default value is False
        """
        self.name = name
        self.ply_materials = ply_materials
        self.orientations = orientations
        self.orientations_ = [convert(unit_system, _, 'angle', True)
                              for _ in orientations]
        if any((all(_ is not None for _ in [layup_thickness, thicknesses]),
                all(_ is None for _ in [layup_thickness, thicknesses]))):
            raise IOError('One of either layup_thickness or thicknesses must '
                          'be defined.')
        elif layup_thickness is not None:
            _t = layup_thickness / len(ply_materials)
            thicknesses = [_t for _ in range(len(ply_materials))]
        elif thicknesses is not None:
            layup_thickness = sum(thicknesses)
        self.layup_thickness = layup_thickness
        self.thicknesses = thicknesses
        self.thicknesses_ = [convert(unit_system, _, 'length', True)
                             for _ in thicknesses]
        if ply_names is None:
            ply_names = ['ply-{}'.format(_) for _ in range(len(ply_materials))]
        self.ply_names = ply_names
        self.symmetric = symmetric
        self._unit_system = unit_system
        super().__convert__(unit_system, layup_thickness=layup_thickness)

    def __eq__(self, other) -> bool:
        try:
            assert isinstance(other, self.__class__)
        except AssertionError:
            return False
        else:
            for key, unit in self.arg_units.items():
                if isinstance(unit, str):  # quantity
                    key += '_'
                try:
                    assert getattr(self, key) == getattr(other, key)
                except AssertionError:
                    return False
            else:
                return True

    def __str__(self) -> str:
        """
        String of information about composite laminate

        Notes
        -----
        Overwrites superclass (Material) __str__

        Returns
        -------
        string : str
        """
        str_ = 'Composite Layup : {}'.format(self.name)
        str_ += '\n' + '-' * len(str_) + '\n'
        str_ += 'Unit System : ' + self.unit_system.name + '\n'
        str_ += 'Symmetric : {}'.format(self.symmetric) + '\n'
        str_ += str(self.data)
        return str_

    @property
    def data(self) -> DataFrame:
        """
        Dataframe of layup

        Notes
        -----
        - Returns full stack, i.e. if symmetric is True, returns
          mirrored stack instead of just input parameter data
        - Doesn't include layup name, unit system, layup thickness, or
          symmetric flag

        Returns
        -------
        data : DataFrame
            Table of ply names, materials, thicknesses, and orientations
        """
        columns = ('Ply Name', 'Material', 'Thickness', 'Orientation')
        data = {'Ply Name': self.ply_names, 'Material': self.ply_materials,
                'Thickness': self.thicknesses,
                'Orientation': self.orientations}
        if self.symmetric:
            for key, value in data.items():
                data[key] = value + list(reversed(value))
        data = DataFrame(data, columns=columns)
        return data

    def define_in_abaqus(self, model, part: str, region: str, axis: int = 2,
                         angles: tuple[float] = (0.0, 0.0, 0.0),
                         unit_system: UnitSystem = None):
        """
        Define Composite Layup in Abaqus.

        Parameters
        ----------
        model : Model
            Current model object
        part : str
            String name of part for composite layup creation
        region : str
            String name of part set for composite layup creation
        axis : int, optional
            Normal/stacking axis for composite layup creation. Default
            value is axis 2.
        angles : tuple[Quantity], optional
            Csys rotation angles (about X, Y, and Z) from global part
            X-Y plane. Default value is (0.0, 0.0, 0.0).
        unit_system : UnitSystem
            If provided, converts to Abaqus model unit system prior to
            definition
        """
        if not unit_system:
            unit_system = self.unit_system
        axis_dict = {1: AXIS_1, 2: AXIS_2, 3: AXIS_3}
        stack_dict = {1: STACK_1, 2: STACK_2, 3: STACK_3}
        material_names = [_.name for _ in self.ply_materials]
        material = None
        for material in self.ply_materials:
            if material not in model.ply_materials:
                material.define_in_abaqus(model)
        part = model.parts[part]
        region = part.sets[region]
        angles = [convert(unit_system, _angle, 'angle') for _angle in angles]
        angles = [_angle.to('degree').m for _angle in angles]
        angles = tuple(angles)
        _csys = part.DatumCsysByThreePoints(
            CARTESIAN, (0.0, 0.0, 0.0), rotate_vector((1.0, 0.0, 0.0), angles),
            rotate_vector((0.0, 1.0, 0.0), angles), name='csys')
        csys = part.datums[_csys.id]
        # elementType could also be CONTINUUM_SHELL or SOLID
        composite = part.CompositeLayup(self.name, elementType=SHELL,
                                        symmetric=self.symmetric)
        composite.Section(poissonDefinition=VALUE, poisson=0.5,
                          thicknessModulus=material.E2.magnitude)
        composite.ReferenceOrientation(localCsys=csys, axis=axis_dict[axis],
                                       stackDirection=stack_dict[axis])
        for name, thickness, orientation, material in zip(
                self.ply_names, self.thicknesses, self.orientations,
                material_names):
            _t = thickness.magnitude
            _o = orientation.to('degree').magnitude
            composite.CompositePly(
                thickness=_t, region=region, material=material, plyName=name,
                orientationType=SPECIFY_ORIENT,
                thicknessType=SPECIFY_THICKNESS, orientationValue=_o)

    @classmethod
    def from_dict(cls, saved: dict):
        """
        Formatted dictionary for creating material definition

        Parameters
        ----------
        saved : dict

        Returns
        -------
        mat
        """
        kwargs = dict()
        unit_system = UnitSystem.from_dict(saved['unit_system'])
        for key in saved:
            if key == 'unit_system':
                kwargs[key] = unit_system
            elif key == 'ply_materials':
                kwargs['ply_materials'] = [Lamina.from_dict(_)
                                           for _ in saved[key]]
            else:
                type_ = cls.arg_units[key]
                value = saved[key]
                if isinstance(value, list):
                    kwargs[key] = [check_value(_, type_, unit_system)
                                   for _ in value]
                else:
                    kwargs[key] = check_value(value, type_, unit_system)
        try:
            kwargs.pop('cls')
        except KeyError:
            pass
        return cls(**kwargs)

    @classmethod
    def read_json(cls, path: str):
        """
        Read a formatted JSON file containing a material definition

        Parameters
        ----------
        path : str
            Either a file path or a direct JSON string

        Returns
        -------
        mat
        """
        if not isfile(path):
            try:
                json_dict = json.loads(path)
            except JSONDecodeError:
                raise FileNotFoundError('Invalid path or JSON string')
        else:
            with open(path, 'r') as f:
                json_dict = json.load(f)
        kwargs = dict()
        unit_system = json_dict.pop('unit_system')
        kwargs['unit_system'] = UnitSystem.read_json(unit_system)
        ply_mats = json_dict.pop('ply_materials')
        kwargs['ply_materials'] = [Material.read_json(_) for _ in ply_mats]
        for key, value in json_dict.items():
            try:
                type_ = cls.arg_units[key]
            except KeyError:
                continue
            if isinstance(value, (list, tuple)):
                value = [check_value(_, type_, kwargs['unit_system'])
                         for _ in value]
            else:
                value = check_value(value, type_, kwargs['unit_system'])
            kwargs[key] = value
        return cls(**kwargs)

    def to_dict(self) -> dict:
        """
        Save material data to dictionary

        Returns
        -------
        mat_dict : dict
        """
        kwargs = {
            'name': self.name,
            'ply_materials': [_.to_dict() for _ in self.ply_materials],
            'orientations': [get_value(_, 'angle', self.unit_system) for _ in
                             self.orientations],
            'unit_system': self.unit_system.to_dict(),
            'thicknesses': [get_value(_, 'length', self.unit_system) for _ in
                            self.thicknesses],
            'symmetric': self.symmetric
        }
        if self.ply_names:
            kwargs['ply_names'] = self.ply_names
        return kwargs

    def to_json(self, path: str = None):
        """
        Save material definition to JSON format, either as a string or
        to a file if path is provided

        Parameters
        ----------
        path : str, optional
            If not provided, will return formatted JSON string

        Returns
        -------
        json : str
        """
        kwargs = {
            'name': self.name,
            'ply_materials': [_.to_json() for _ in self.ply_materials],
            'orientations': [get_value(_, 'angle', self.unit_system) for _ in
                             self.orientations],
            'unit_system': self.unit_system.to_json(),
            'thicknesses': [get_value(_, 'length', self.unit_system) for _ in
                            self.thicknesses],
            'symmetric': self.symmetric,
            'cls': self.__class__.__name__
        }
        if self.ply_names:
            kwargs['ply_names'] = self.ply_names
        if not path:
            return json.dumps(kwargs)
        with open(path, 'w') as f:
            json.dump(kwargs, f)

    @property
    def unit_system(self):
        """
        Unit system for consistency within material property quantities

        Returns
        -------
        unit_system : UnitSystem
            Unit system for storage of created material
        """
        return self._unit_system

    @unit_system.setter
    def unit_system(self, unit_system: UnitSystem):
        """
        Unit system for consistency within material property quantities

        Notes
        -----
        Converts quantities to match new unit system

        Parameters
        ----------
        unit_system : UnitSystem
        """
        for mat in self.ply_materials:
            mat.unit_system = unit_system
        orientations = [Q_(_, self.unit_system.angle) for _ in
                        self.orientations_]
        layup_thickness = Q_(self.layup_thickness_, self.unit_system.length)
        thicknesses = [Q_(_, self.unit_system.length) for _ in
                       self.thicknesses_]
        self.orientations_ = [convert(unit_system, _, 'angle', True)
                             for _ in orientations]
        self.layup_thickness_ = convert(unit_system, layup_thickness,
                                       'length', True)
        self.thicknesses_ = [convert(unit_system, _, 'length', True)
                            for _ in thicknesses]
        self._unit_system = unit_system


class Material(UnitMixin):
    type_ = None
    arg_units = {
        'name': str,
        'unit_system': None,
        'rho': 'density',
        'tref': 'temperature'
    }

    def __init__(self, name: str, unit_system: UnitSystem, rho: Quantity,
                 tref: Quantity = None):
        """
        Material class for model generation.

        Parameters
        ----------
        name : str
            Name of material
        unit_system : UnitSystem
            Unit system for storage of created material
        rho : Quantity
            Density of material
        tref : Quantity, optional
            Reference temperature. default value is room temp

        Methods
        -------
        define_in_abaqus
        create_mat_abaqus
        create_density_abaqus
        create_elastic_abaqus

        Notes
        -----
        Currently built from Abaqus notation but will attempt to generalize
        later. Temperature dependence could be built in later by making
        each input lists.
        """
        self.name = name
        self._unit_system = unit_system
        self.rho = rho
        if tref is None:
            tref = ROOM_TEMP
        self.tref = tref
        self._mat = None
        super().__convert__(unit_system, rho=rho, tref=tref)

    def __eq__(self, other) -> bool:
        try:
            assert isinstance(other, self.__class__)
        except AssertionError:
            return False
        else:
            for key, unit in self.arg_units.items():
                if isinstance(unit, str):  # quantity
                    key += '_'
                try:
                    assert getattr(self, key) == getattr(other, key)
                except AssertionError:
                    return False
            else:
                return True

    def __hash__(self) -> int:
        values = list()
        for key, unit in self.arg_units.items():
            if isinstance(unit, str):  # quantity
                key += '_'
            values.append(getattr(self, key))
        return hash(tuple(values))

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        """
        CamelCase representation of material name

        Returns
        -------
        name : str
        """
        return self.name.title().replace(' ', str())

    def create_damage_evolution_abaqus(self):
        raise NotImplementedError('Subclass specific method')

    def create_density_abaqus(self):
        rho = self.rho_
        logger.info('Creating material density in Abaqus: '
                    f'Assumes units are {self.unit_system.density}')
        if rho > 0:
            self._mat.Density(((rho,),))

    def create_elastic_abaqus(self):
        if not any([_ is None for _ in self.elastic_]):
            values, units = list(), list()
            for value in self.elastic_:
                values.append(value)
            elastic = tuple(values)
            logger.info('Creating elastic material properties in Abaqus: '
                        f'Assumes units are {self.unit_system.pressure}')
            self._mat.Elastic((elastic,), self.type_)

    def create_mat_abaqus(self, model):
        """
        Instantiate a material in an Abaqus model

        Parameters
        ----------
        model : Abaqus model object
        """
        logger.info(f'Creating material name in Abaqus: {self.name}')
        self._mat = model.Material(self.name)

    def create_stress_limit_abaqus(self):
        raise NotImplementedError('Subclass specific method')

    def define_2d_nastran(self, model=None, id_=None, add: bool = False):
        raise AttributeError('Only used by some subclasses')

    def define_3d_nastran(self, model=None, id_=None, add: bool = False):
        raise AttributeError('Only used by some subclasses')

    def define_in_abaqus(self, model, damage: bool = True):
        """
        Define material in Abaqus

        Parameters
        ----------
        model : object
            Abaqus model object
        damage : boolean, optional
            Flag to add damage initiation and evolution to material. Default
            value is True.
        """
        logger.info('Creating material in Abaqus:')
        self.create_mat_abaqus(model)
        self.create_density_abaqus()
        self.create_elastic_abaqus()
        if damage:
            self.create_stress_limit_abaqus()
            self.create_damage_evolution_abaqus()

    def define_in_nastran(self, model=None, id_=None, add: bool = False):
        raise NotImplementedError

    def define_in_patran(self, ses, mat_name=None):
        raise NotImplementedError

    @property
    def elastic(self) -> tuple[Quantity]:
        raise ValueError('No elastic properties defined')

    @property
    def elastic_(self) -> tuple[float]:
        raise ValueError('No elastic properties defined')

    @classmethod
    def from_dict(cls, saved: dict):
        """
        Formatted dictionary for creating material definition

        Parameters
        ----------
        saved : dict

        Returns
        -------
        mat
        """
        kwargs = dict()
        unit_system = UnitSystem.from_dict(saved['unit_system'])
        for key in saved:
            if key == 'unit_system':
                kwargs[key] = unit_system
            elif '_' in key[0]:
                type_ = cls.arg_units[1:][key]
                kwargs[key[1:]] = check_value(saved[key], type_, unit_system)
            else:
                type_ = cls.arg_units[key]
                kwargs[key] = check_value(saved[key], type_, unit_system)
        try:
            kwargs.pop('cls')
        except KeyError:
            pass
        return cls(**kwargs)

    @staticmethod
    def read_json(path: str):
        """
        Read a formatted JSON file containing a material definition

        Parameters
        ----------
        path : str
            Either a file path or a direct JSON string

        Returns
        -------
        mat
        """
        if not isfile(path):
            try:
                kwargs = json.loads(path)
            except JSONDecodeError:
                raise FileNotFoundError('Invalid path or JSON string')
        else:
            with open(path, 'r') as f:
                kwargs = json.load(f)
        cls_ = mat_classes[kwargs.pop('cls')]
        if cls_ is Composite:
            return Composite.read_json(path)
        kwargs['unit_system'] = UnitSystem.from_dict(kwargs['unit_system'])
        for key, value in dict(kwargs).items():
            if key == 'unit_system':
                continue
            else:
                if '_' in key[0]:
                    kwargs.pop(key)
                    key = key[1:]
                type_ = cls_.arg_units[key]
                value = check_value(value, type_, kwargs['unit_system'])
                kwargs[key] = value
        return cls_(**kwargs)

    def to_dict(self) -> dict:
        """
        Save material data to dictionary

        Returns
        -------
        mat_dict : dict
        """
        kwargs = dict()
        for key, value in dict(self.__dict__).items():
            if '_' in key[0]:
                key = key[1:]
            if key == 'unit_system':
                kwargs[key] = value.to_dict()
            elif value is None:
                continue
            elif key in self.arg_units:
                type_ = self.arg_units[key]
                kwargs[key] = get_value(value, type_, self.unit_system)
        return kwargs

    def to_json(self, path: str = None):
        """
        Save material definition to JSON format, either as a string or
        to a file if path is provided

        Parameters
        ----------
        path : str, optional
            If not provided, will return formatted JSON string

        Returns
        -------
        json : str
        """
        kwargs = self.to_dict()
        kwargs['cls'] = self.__class__.__name__
        if not path:
            return json.dumps(kwargs)
        with open(path, 'w') as f:
            json.dump(kwargs, f)

    @property
    def stress_limit(self) -> tuple[Quantity]:
        raise ValueError('No stress limit defined')

    @property
    def stress_limit_(self) -> tuple[float]:
        raise ValueError('No stress limit defined')

    @property
    def unit_system(self) -> UnitSystem:
        """
        Unit system for consistency within material property quantities

        Returns
        -------
        unit_system : UnitSystem
            Unit system for storage of created material
        """
        return self._unit_system

    @unit_system.setter
    def unit_system(self, unit_system: UnitSystem):
        """
        Setter for unit system

        Notes
        -----
        Converts magnitude attributes (`<value>_`) to new unit system

        Parameters
        ----------
        unit_system : UnitSystem
        """
        for key, unit in self.arg_units.items():
            if isinstance(unit, str):
                key += '_'
                value = Q_(getattr(self, key), getattr(self.unit_system, unit))
                value = value.to(getattr(unit_system, unit)).magnitude
                setattr(self, key, value)
        self._unit_system = unit_system


class EngineeringConstants(Material):
    arg_units = {
        'name': str,
        'unit_system': None,
        'rho': 'density',
        'E1': 'pressure', 'E2': 'pressure', 'E3': 'pressure',
        'nu12': float, 'nu13': float, 'nu23': float,
        'G12': 'pressure', 'G13': 'pressure', 'G23': 'pressure',
        'tref': 'temperature',
        'Xt': 'pressure', 'Xc': 'pressure',
        'Yt': 'pressure', 'Yc': 'pressure',
        'S': 'pressure'
    }

    def __init__(self, name: str, unit_system: UnitSystem, rho: Quantity,
                 E1: Quantity, E2: Quantity, E3: Quantity,
                 nu12: float, nu13: float, nu23: float,
                 G12: Quantity, G13: Quantity, G23: Quantity,
                 tref: Quantity = None,
                 Xt: Quantity = None, Xc: Quantity = None,
                 Yt: Quantity = None, Yc: Quantity = None,
                 S: Quantity = None):
        """
        Engineering Constants material class

        Parameters
        ----------
        name : str
            Name of material
        unit_system : UnitSystem
            Values will be converted to quantities in this unit system
            for internal consistency
        rho : Quantity
            Density of material
        E1, E2, E3 : Quantity
            Young's modulus
        nu12, nu13, nu23 : float
            Poisson ratio
        G12, G13, G23 : Quantity
            Shear modulus
        tref : Quantity, optional
            Reference temperature. Default value is room temperature.
        Xt, Xc : Quantity, optional
            Stress limits in longitudinal tensile/compressive directions
        Yt, Yc : Quantity, optional
            Stress limits in transverse tensile/compressive directions
        S : Quantity, optional
            Stress limit in shear direction
        """
        super(EngineeringConstants, self).__init__(
            name, unit_system, rho, tref)
        self.E1 = E1
        self.E2 = E2
        self.E3 = E3
        self.nu12 = float(nu12)
        self.nu13 = float(nu13)
        self.nu23 = float(nu23)
        self.G12 = G12
        self.G13 = G13
        self.G23 = G23
        self.Xt = Xt
        self.Xc = Xc
        self.Yt = Yt
        self.Yc = Yc
        self.S = S
        super().__convert__(unit_system,
                            E1=E1, E2=E2, E3=E3,
                            G12=G12, G13=G13, G23=G23,
                            Xt=Xt, Xc=Xc, Yt=Yt, Yc=Yc, S=S)

    def __repr__(self) -> str:
        return ('EngineeringConstants(name={x.name!r}, rho={x.rho!s}, '
                'E1={x.E1!s}, E2={x.E2!s}, E3={x.E3!s}, nu12={x.nu12!s}, '
                'nu13={x.nu13!s}, nu23={x.nu23!s}, G12={x.G12!s}, '
                'G13={x.G13!s}, G23={x.G23!s}, tref={x.tref!s}, Xt={x.Xt!s}, '
                'Xc={x.Xc!s}, Yt={x.Yt!s}, Yc={x.Yc!s}, '
                'S={x.S!s})'.format(x=self))

    def create_damage_evolution_abaqus(self):
        """
        Create damage evolution in Abaqus

        Notes
        -----
        Only implemented in Lamina and Traction
        """
        pass

    def create_stress_limit_abaqus(self):
        """Create stress limit/damage initiation in Abaqus"""
        if not any(_ is None for _ in self.stress_limit):
            stress_limit = tuple(self.stress_limit_)
            logger.info('Creating stress limit in Abaqus: '
                        f'Assumes units are {self.unit_system.pressure}')
            self._mat.elastic.FailStress((stress_limit,))

    def define_2d_nastran(self, model=None, id_: int = None,
                          add: bool = False):
        """
        Define material entry (MAT8) for Nastran model for 2D elements

        Parameters
        ----------
        model : obj, optional
            NatranInputFile object. If provided, will get material ID based on
            max ID in model and will add material to bulk entries.
        id_ : int, optional
            Material ID for Nastran file. Needed if model is not provided.
            Default value is 1.
        add : bool, optional
            Flag to add new entry to model bulk entries. Default value is
            False.

        Returns
        -------
        material : obj
            nastran_utils.MAT1 object
        """
        E1, E2 = self.E1_, self.E2_
        nu12, G12 = self.nu12, self.G12_
        rho, G13 = self.rho_, self.G13_
        G23, tref = self.G23_, self.tref_
        if id_ is None:
            if model is not None:
                id_ = model.get_max_id('Material') + 1
            else:
                id_ = 1
        properties = {'name': self.name, 'mid': id_, 'E1': E1, 'E2': E2,
                      'nu12': nu12, 'G12': G12, 'rho': rho, 'G1z': G13,
                      'G2z': G23, 'tref': tref}
        for name, value in zip(
                ['Xt', 'Xc', 'Yt', 'Yc', 'S'],
                [self.Xt_, self.Xc_, self.Yt_, self.Yc_, self.S_]):
            properties[name] = value
        if nastran_utils:
            material = nastran_utils.MAT8(**properties)
            if model is not None:
                if add:
                    model.add(material)
            return material
        else:
            raise ImportError('Nastran utils does not seem to have imported.')

    def define_3d_nastran(self, model=None, id_: int = None,
                          add: bool = False):
        """
        Define material entry (MAT9) for Nastran model for 3D elements

        Parameters
        ----------
        model : obj, optional
            NatranInputFile object. If provided, will get material ID based on
            max ID in model and will add material to bulk entries.
        id_ : int, optional
            Material ID for Nastran file. Needed if model is not provided.
            Default value is 1.
        add : bool, optional
            Flag to add new entry to model bulk entries. Default value is
            False.

        Returns
        -------
        material : obj
            nastran_utils.MAT1 object
        """
        if id_ is None:
            if model is not None:
                id_ = model.get_max_id('Material') + 1
            else:
                id_ = 1
        properties = {'name': self.name, 'mid': id_, 'rho': self.rho}
        E1, E2, E3 = self.E1_, self.E2_, self.E3_
        nu12, nu13 = self.nu12, self.nu13
        nu23, nu21 = self.nu23, self.nu21
        nu31, nu32 = self.nu31, self.nu32
        G44, G66 = self.G12_, self.G13_
        G55, tref = self.G23_, self.tref_
        delta = (1 - nu12 * nu21 - nu23 * nu32 - nu31 * nu13 -
                 2 * nu21 * nu32 * nu13) / (E1 * E2 * E3)
        G11 = (1 - nu23 * nu32) / (E2 * E3 * delta)
        G12 = (nu21 + nu31 * nu23) / (E2 * E3 * delta)
        G13 = (nu31 + nu21 * nu32) / (E2 * E3 * delta)
        G22 = (1 - nu13 * nu31) / (E1 * E3 * delta)
        G23 = (nu32 + nu23 * nu31) / (E1 * E3 * delta)
        G33 = (1 - nu12 * nu21) / (E1 * E2 * delta)
        G14, G15, G16, G24, G25, G26 = (0.0 for _ in range(6))
        G34, G35, G36, G45, G46, G56 = (0.0 for _ in range(6))
        for _name, _value in zip(['tref', 'G11', 'G12', 'G13', 'G14', 'G15',
                                  'G16', 'G22', 'G23', 'G24', 'G25', 'G26',
                                  'G33', 'G34', 'G35', 'G36', 'G44', 'G45',
                                  'G46', 'G55', 'G56', 'G66'],
                                 [tref, G11, G12, G13, G14, G15, G16, G22, G23,
                                  G24, G25, G26, G33, G34, G35, G36, G44, G45,
                                  G46, G55, G56, G66]):
            properties[_name] = _value
        if nastran_utils:
            material = nastran_utils.MAT9(**properties)
            if model is not None:
                if add:
                    model.add(material)
            return material
        else:
            raise ImportError('Nastran utils does not seem to have imported.')

    def define_in_nastran(self, model=None, id_: int = None,
                          add: bool = False):
        raise AttributeError('Not valid for this material type, use 2d or 3d')

    def define_in_patran(self, ses, mat_name=None):
        raise NotImplementedError

    @property
    def elastic(self) -> tuple[Quantity]:
        """
        Elastic properties table

        Returns
        -------
        tuple
        """
        return (self.E1, self.E2, self.E3, self.nu12, self.nu13, self.nu23,
                self.G12, self.G13, self.G23)

    @property
    def elastic_(self) -> tuple[float]:
        """
        Elastic properties table, magnitudes and coverted to central
        unit system

        Returns
        -------
        tuple
        """
        return (self.E1_, self.E2_, self.E3_,
                self.nu12_, self.nu13_, self.nu23_,
                self.G12_, self.G13_, self.G23_)

    @elastic.setter
    def elastic(self, damage: float):
        if damage == 1:
            tol = Q_(numerical_tolerance, self.unit_system.pressure)
        else:
            tol = Q_(0, self.unit_system.pressure)
        self.E1 = (1 - damage) * self.E1 + tol
        self.E2 = (1 - damage) * self.E2 + tol
        self.E3 = (1 - damage) * self.E3 + tol
        self.G12 = (1 - damage) * self.G12 + tol
        self.G13 = (1 - damage) * self.G13 + tol
        self.G23 = (1 - damage) * self.G23 + tol
        tol = float(tol.magnitude)
        self.E1_ = (1 - damage) * self.E1_ + tol
        self.E2_ = (1 - damage) * self.E2_ + tol
        self.E3_ = (1 - damage) * self.E3_ + tol
        self.G12_ = (1 - damage) * self.G12_ + tol
        self.G13_ = (1 - damage) * self.G13_ + tol
        self.G23_ = (1 - damage) * self.G23_ + tol

    @property
    def nu21(self) -> float:
        return self.E2_ * self.nu12 / self.E1_

    @property
    def nu31(self) -> float:
        return self.E3_ * self.nu13 / self.E1_

    @property
    def nu32(self) -> float:
        return self.E3_ * self.nu23 / self.E2_

    @property
    def stress_limit(self) -> tuple[Quantity]:
        """
        Stress limit table

        Returns
        -------
        tuple
        """
        return self.Xt, self.Xc, self.Yt, self.Yc, self.S

    @property
    def stress_limit_(self) -> tuple[float]:
        """
        Stress limit table, magnitudes and convered to central unit
        system

        Returns
        -------
        tuple
        """
        return self.Xt_, self.Xc_, self.Yt_, self.Yc_, self.S_


class Fluid(Material):
    arg_units = {
        'name': str,
        'unit_system': None,
        'rho': 'density',
        'pref': 'pressure',
        'tref': 'temperature',
        'bulk_modulus': 'pressure',
        'c': 'speed',
        'ge': float,
        'alpha': float
    }

    def __init__(self, name: str, unit_system: UnitSystem, rho: Quantity,
                 pref: Quantity = None, tref: Quantity = None,
                 bulk_modulus: Quantity = None, c: Quantity = None,
                 ge: float = None, alpha: float = None):
        """
        Fluid material property definition

        Parameters
        ----------
        name : str
            Name of material
        unit_system : UnitSystem
            Values will be converted to quantities in this unit system
            for internal consistency
        rho : Quantity
            Density of material at given pressure and temperature
        pref : Quantity, optional
            Reference pressure. Used for cryogenic propellants. Not used
            by Nastran. Default value is 1 atmosphere.
        tref : Quantity, optional
            Reference temperature. Default value is room temperature.
        bulk_modulus : Quantity, optional
            Bulk modulus, equivalent to c ** 2 * rho
        c : Quantity, optional
            Speed of sound in fluid
        ge : float, optional
            Fluid element damping coefficient
        alpha : float, optional
            Normalized admittance coefficient for porous material, also
            known as alpha. If a value of alpha is entered in Nastran,
            bulk_modulus, rho, and ge may have negative values.
        """
        super(Fluid, self).__init__(name, unit_system, rho, tref)
        if pref is None:
            pref = Q_(1.0, 'atm')
        self.pref = pref
        self.bulk_modulus = bulk_modulus
        self.c = c
        if ge is not None:
            ge = float(ge)
        self.ge = ge
        if alpha is not None:
            alpha = float(alpha)
        self.alpha = alpha
        super().__convert__(unit_system, pref=pref,
                            bulk_modulus=bulk_modulus, c=c)

    def create_damage_evolution_abaqus(self):
        raise NotImplementedError

    def create_stress_limit_abaqus(self):
        raise NotImplementedError

    def define_in_nastran(self, model=None, id_: int = None,
                          add: bool = False):
        if id_ is None:
            if model is not None:
                id_ = model.get_max_id('Material') + 1
            else:
                id_ = 1
        bulk = self.bulk_modulus_
        rho = self.rho_
        c = self.c_
        ge = self.ge
        alpha = self.alpha
        if nastran_utils:
            nastran_utils.MAT10(id_, bulk, rho, c, ge, alpha)
        else:
            raise ImportError('Nastran utils does not seem to have imported.')

    def define_in_patran(self, ses, mat_name=None):
        raise NotImplementedError


class Isotropic(Material):
    arg_units = {
        'name': str,
        'unit_system': None,
        'rho': 'density',
        'E': 'pressure',
        'nu': float,
        'G': 'pressure',
        'tref': 'temperature',
        'Xt': 'pressure', 'Xc': 'pressure', 'Xs': 'pressure'
    }

    def __init__(self, name: str, unit_system: UnitSystem, rho: Quantity,
                 E: Quantity, nu: float = None, G: Quantity = None,
                 tref: Quantity = None, Xt: Quantity = None,
                 Xc: Quantity = None, Xs: Quantity = None):
        """
        Isotropic material class

        Parameters
        ----------
        name : str
            Name of material
        unit_system : UnitSystem
            Values will be converted to quantities in this unit system
            for internal consistency
        rho : Quantity
            Density of material
        E : Quantity
            Young's modulus
        nu : float, optional
            Poisson ratio. If not assigned, will be calculated using linear
            elastic relationship from E and G.
        G : Quantity, optional
            Shear modulus, also sometimes called mu, not used as an input for
            Abaqus. If not assigned will be calculated using linear elastic
            relationship from E and nu.
        tref : Quantity, optional
            Reference temperature. Default value is room temperature.
        Xt, Xc, Xs : Quantity, optional
            Stress limits in tension, compression, and shear

        Notes
        -----
        Either nu or G must be defined. If only one is defined, linear elastic
        relationship will be used to define the other.

        Raises
        ------
        ValueError
            If E/nu/G ratio under-defined or not linearly elastic
        """
        super(Isotropic, self).__init__(name, unit_system, rho, tref)
        self.E = E
        self.G = G
        super().__convert__(unit_system, E=E, G=G)
        if nu is not None:
            nu = float(nu)
        if nu is not None and G is not None:
            if 1 - self.E_ / float(2 * self.G_ * (1 + nu)) >= 0.01:
                raise ValueError(
                    'Ratio of E, G, and nu not linearly elastic, recommend '
                    'changing values or going with another material type.')
        elif nu is not None and G is None:
            self.G = self.E / 2 / (1 + nu)
            self.G_ = self.E_ / 2 / (1 + nu)
        elif nu is None and G is not None:
            nu = (self.E_ - 2 * self.G_) / (2 * self.G_)
        elif nu is None and G is None:
            raise ValueError('Either nu or G must be defined')
        self.nu = nu
        self.Xt = Xt
        self.Xc = Xc
        self.Xs = Xs
        super().__convert__(unit_system, Xt=Xt, Xc=Xc, Xs=Xs)

    def __repr__(self) -> str:
        return ('Isotropic(name={x.name!r}, rho={x.rho!s}, E={x.E!s}, '
                'nu={x.nu!s}, G={x.G!s}, tref={x.tref!s}, Xt={x.Xt!s}, '
                'Xc={x.Xc!s}, Xs={x.Xs!s})'.format(x=self))

    def create_damage_evolution_abaqus(self):
        """
        Create damage evolution in Abaqus

        Notes
        -----
        Only implemented in Lamina and Traction
        """
        pass

    def create_stress_limit_abaqus(self):
        """
        Create stress limit/damage initiation in Abaqus
        """
        if not any([_ is None for _ in self.stress_limit]):
            stress_limit = tuple(self.stress_limit_)
            self._mat.elastic.FailStress((stress_limit,))

    def define_in_nastran(self, model=None, id_: int = None,
                          add: bool = False):
        """
        Define material entry (MAT1) for Nastran model

        Parameters
        ----------
        model : obj, optional
            NatranInputFile object. If provided, will get material ID based on
            max ID in model and will add material to bulk entries.
        id_ : int, optional
            Material ID for Nastran file. Needed if model is not provided.
            Default value is 1.
        add : bool, optional
            Flag to add new entry to model bulk entries. Default value is
            False.

        Returns
        -------
        material : obj
            nastran_utils.MAT1 object
        """
        if id_ is None:
            if model is not None:
                id_ = model.get_max_id('Material') + 1
            else:
                id_ = 1
        E, G, nu = self.E_, self.G_, self.nu
        rho, tref = self.rho_, self.tref_
        properties = {'name': self.name, 'mid': id_, 'E': E, 'G': G, 'nu': nu,
                      'rho': rho, 'tref': tref}
        for name, value in zip(['St', 'Sc', 'Ss'],
                               [self.Xt_, self.Xc_, self.Xs_]):
            properties[name] = value
        if nastran_utils:
            material = nastran_utils.MAT1(**properties)
            if model is not None and add:
                model.add(material)
            return material
        else:
            raise ImportError('Nastran utils does not seem to have imported.')

    def define_in_patran(self, ses, mat_name: str = None):
        """
        Define material in Patran

        Parameters
        ----------
        ses : File
            Open Patran session file object
        mat_name : str, optional
            Material name to use in Patran. Default will get object's name.

        Notes
        -----
        - Only implemented for Isotropic
        """
        E, G, nu = self.E_, self.G_, self.nu
        rho = self.rho_
        if mat_name is None:
            mat_name = self.name
        if self.tref is None:
            tref = str()
        else:
            tref = self.tref_
        ses.write(self.patran_material_string.format(
            name=mat_name, E=E, nu=nu, G=G, rho=rho, alpha=str(), GE=str(),
            tref=tref))

    @property
    def elastic(self) -> tuple[Quantity]:
        """
        Elastic properties table

        Returns
        -------
        tuple
        """
        return self.E, self.nu

    @property
    def elastic_(self) -> tuple[float]:
        """
        Elastic properties table, magnitude and converted to central
        unit system

        Returns
        -------
        tuple
        """
        return self.E_, self.nu

    @elastic.setter
    def elastic(self, damage: float):
        if damage == 1:
            tol = Q_(numerical_tolerance, self.unit_system.pressure)
        else:
            tol = Q_(0, self.unit_system.pressure)
        self.E = (1 - damage) * self.E + tol
        tol = float(tol.magnitude)
        self.E_ = (1 - damage) * self.E_ + tol

    @property
    def patran_material_string(self) -> str:
        """
        PCL material creation command string

        String Arguments
        ----------------
        name, E, nu, G, rho, alpha, GE, tref

        Returns
        -------
        material_string : str
            Formatted Patran command language string
        """
        material_string = ('material.create( "Analysis code ID", 1, "Analysis '
                           'type ID", 1, "{name}", 0, "", "Isotropic", 1, '
                           '"Directionality", 1, "Linearity", 1, "Homogeneous"'
                           ', 0, "Linear Elastic", 1, "Model Options & IDs", '
                           '["", "", "", "", ""], [0, 0, 0, 0, 0], "Active '
                           'Flag", 1, "Create", 10, "External Flag",  FALSE, '
                           '"Property IDs", ["Elastic Modulus", "Poisson '
                           'Ratio", "Shear Modulus", "Density", "Thermal '
                           'Expan. Coeff", "Structural Damping Coeff", '
                           '"Reference Temperature"], [2, 5, 8, 16, 24, 30, 1,'
                           ' 0], "Property Values", ["{E}", "{nu}", "{G}", '
                           '"{rho}", "{alpha}", "{GE}", "{tref}", ""] )\n')
        return material_string

    @property
    def stress_limit(self) -> tuple[Quantity]:
        """
        Stress limit table

        Returns
        -------
        tuple
        """
        return self.Xt, self.Xc, self.Xt, self.Xc, self.Xs

    @property
    def stress_limit_(self) -> tuple[float]:
        """
        Stress limit table, magnitude and converted to central unit
        system

        Returns
        -------
        tuple
        """
        return self.Xt_, self.Xc_, self.Xt_, self.Xc_, self.Xs_

    @property
    def bulk_modulus(self) -> Quantity:
        """
        Bulk modulus of the material

        Returns
        -------
        bulk_modulus : Quantity
        """
        return self.E / 3 / (1 - 2 * self.nu)

    @property
    def bulk_modulus_(self) -> float:
        """
        Bulk modulus of the material, magnitude and converted to central
        unit system

        Returns
        -------
        bulk_modulus : float
        """
        return self.E_ / 3 / (1 - 2 * self.nu)

    @property
    def wave_speed(self) -> Quantity:
        """
        Speed of wave through material

        Notes
        -----
        Assumes pressure-density unit compatibility

        Returns
        -------
        wave_speed : Quantity
        """
        return sqrt(self.bulk_modulus / self.rho)

    @property
    def wave_speed_(self) -> float:
        """
        Speed of wave through material, magnitude and converted to
        central unit system speed unit

        Notes
        -----
        Assumes pressure-density unit compatibility

        Returns
        -------
        wave_speed : float
        """
        return sqrt(self.bulk_modulus_ / self.rho_)

    @classmethod
    def generic_aluminum(cls, name: str = 'Aluminum',
                         unit_system: UnitSystem = None):
        """
        Based on Aluminum 6061-T6

        Parameters
        ----------
        name : str, optional
        unit_system : UnitSystem, optional

        Notes
        -----
        - Default tref is ~70 degrees Fahrenheit "room temperature"
        - Default failure stresses are yield
        - Tensile/shear stress relation from
          http://www.roymech.co.uk/Useful_Tables/Matter/shear_tensile.htm
        - Properties from
          http://asm.matweb.com/search/SpecificMaterial.asp?bassnum=ma6061t6

        Returns
        -------
        material : Isotropic
        """
        rho = Q_(2.7, 'g/cc')
        E = Q_(68.9, 'GPa')
        nu = 0.33
        G = Q_(26.0, 'GPa')
        tref = ROOM_TEMP
        Xt = Q_(276.0, 'MPa')
        Xc = Xt
        Xs = 0.55 * Xt
        if not unit_system:
            unit_system = UnitSystem.mks()
        return cls(name, unit_system, rho, E, nu, G, tref, Xt, Xc, Xs)

    @classmethod
    def generic_steel(cls, name: str = 'Steel', unit_system: Quantity = None):
        """
        Based on AISI 4140 Steel

        Parameters
        ----------
        name : str, optional
        unit_system : UnitSystem, optional

        Notes
        -----
        - Uses upper value when given a range.
        - Default tref is ~70 degrees Fahrenheit "room temperature"
        - Default failure stresses are yield
        - Tensile/shear stress relation from
          http://www.roymech.co.uk/Useful_Tables/Matter/shear_tensile.htm
        - Properties from http://www.azom.com/article.aspx?ArticleID=6769

        Returns
        -------
        material : Isotropic
        """
        rho = Q_(7.85, 'g/cc')
        E = Q_(210.0, 'GPa')
        nu = 0.3
        G = Q_(80.0, 'GPa')
        tref = ROOM_TEMP
        Xt = Q_(415.0, 'MPa')
        Xc = Xt
        Xs = 0.58 * Xt
        if not unit_system:
            unit_system = UnitSystem.mks()
        return cls(name, unit_system, rho, E, nu, G, tref, Xt, Xc, Xs)

    @classmethod
    def unobtanium(cls, name: str = 'Unobtanium',
                   unit_system: Quantity = None):
        """
        Generic very-high stiffness, negligible density material for rigid
        structures

        Parameters
        ----------
        name : str, optional
        unit_system : UnitSystem, optional

        Returns
        -------
        material : Isotropic
        """
        rho = Q_(1e-8, 'g/cc')
        E = Q_(1e9, 'psi')
        nu = 0.3
        G = None
        tref = ROOM_TEMP
        Xt = Q_(1.0, 'GPa')
        Xc = Q_(1.0, 'GPa')
        Xs = Q_(1.0, 'GPa')
        if not unit_system:
            unit_system = UnitSystem.mks()
        return cls(name, unit_system, rho, E, nu, G, tref, Xt, Xc, Xs)


class Lamina(Material):
    arg_units = {
        'name': str,
        'unit_system': None,
        'rho': 'density',
        'E1': 'pressure', 'E2': 'pressure',
        'nu12': float,
        'G12': 'pressure', 'G13': 'pressure', 'G23': 'pressure',
        'tref': 'temperature',
        'Xt': 'pressure', 'Xc': 'pressure',
        'Yt': 'pressure', 'Yc': 'pressure',
        'SL': 'pressure', 'St': 'pressure',
        'Gft': 'energy', 'Gfc': 'energy', 'Gmf': 'energy', 'Gmc': 'energy'
    }

    def __init__(self, name: str, unit_system: UnitSystem, rho: Quantity,
                 E1: Quantity, E2: Quantity, nu12: float,
                 G12: Quantity, G13: Quantity = None, G23: Quantity = None,
                 tref: Quantity = None,
                 Xt: Quantity = None, Xc: Quantity = None,
                 Yt: Quantity = None, Yc: Quantity = None,
                 SL: Quantity = None, St: Quantity = None,
                 Gft: Quantity = None, Gfc: Quantity = None,
                 Gmf: Quantity = None, Gmc: Quantity = None):
        """
        Lamina material class for shell orthotropic materials

        Parameters
        ----------
        name : str
            Name of material
        unit_system : UnitSystem
                Values will be converted to quantities in this unit system
                for internal consistency
        rho : Quantity
            Density of material
        E1, E2 : Quantity
            Young's modulus
        nu12 : float
            Poisson ratio
        G12, G13, G23 : Quantity
            Shear modulus
        tref : Quantity, optional
            Reference temperature
        Xt, Xc : Quantity, optional
            Lamina stress limits in longitudinal tensile/compressive directions
        Yt, Yc : Quantity, optional
            Lamina stress limits in transverse tensile/compressive directions
        SL, St : Quantity, optional
            Lamina stress limits in shear longitudinal/transverse directions
        Gft, Gfc : Quantity, optional
            Fiber fracture energies in tensile and compressive directions
        Gmf, Gmc : Quantity, optional
            Matrix fracture energies in tensile and compressive directions
        """
        super(Lamina, self).__init__(name, unit_system, rho, tref)
        self.E1 = E1
        self.E2 = E2
        self.nu12 = float(nu12)
        self.G12 = G12
        self.G13 = G13
        self.G23 = G23
        self.Xt = Xt
        self.Xc = Xc
        self.Yt = Yt
        self.Yc = Yc
        self.SL = SL
        self.St = St
        self.Gft = Gft
        self.Gfc = Gfc
        self.Gmf = Gmf
        self.Gmc = Gmc
        super().__convert__(unit_system,
                            E1=E1, E2=E2, G12=G12, G13=G13, G23=G23,
                            Xt=Xt, Xc=Xc, Yt=Yt, Yc=Yc, SL=SL, St=St,
                            Gft=Gft, Gfc=Gfc, Gmf=Gmf, Gmc=Gmc)

    def __repr__(self) -> str:
        return ('Lamina(name={x.name!r}, rho={x.rho!s}, E1={x.E1!s}, '
                'E2={x.E2!s}, nu12={x.nu12!s}, G12={x.G12!s}, G13={x.G13!s}, '
                'G23={x.G23!s}, tref={x.tref!s}, Xt={x.Xt!s}, Xc={x.Xc!s}, '
                'Yt={x.Yt!s}, Yc={x.Yc!s}, SL={x.SL!s}, St={x.St!s}, '
                'Gft={x.Gft!s}, Gfc={x.Gfc!s}, Gmf={x.Gmf!s}, '
                'Gmc={x.Gmc!s})'.format(x=self))

    def create_damage_evolution_abaqus(self):
        """
        Create damage evolution in Abaqus

        Notes
        -----
        - Only implemented in Lamina and Traction
        - Hashin damage evolution
        """
        if not any([_ is None for _ in self.fracture_energy]):
            fracture_energy = tuple(self.fracture_energy_)
            self._mat.hashinDamageInitiation.DamageEvolution(
                ENERGY, (fracture_energy,))

    def create_stress_limit_abaqus(self):
        """
        Create stress limit/damage initiation in Abaqus

        Notes
        -----
        Hashin damage criterion
        """
        if not any([_ is None for _ in self.stress_limit]):
            stress_limit = tuple(self.stress_limit_)
            self._mat.HashinDamageInitiation((stress_limit,))

    def define_in_nastran(self, model=None, id_: int = None,
                          add: bool = False):
        """
        Define material entry (MAT8) for Nastran model

        Parameters
        ----------
        model : obj, optional
            NatranInputFile object. If provided, will get material ID based on
            max ID in model and will add material to bulk entries.
        id_ : int, optional
            Material ID for Nastran file. Needed if model is not provided.
            Default value is 1.
        add : bool, optional
            Flag to add new entry to model bulk entries. Default value is
            False.

        Returns
        -------
        material : obj
            nastran_utils.MAT1 object
        """
        if id_ is None:
            if model is not None:
                id_ = model.get_max_id('Material') + 1
            else:
                id_ = 1
        E1, E2 = self.E1_, self.E2_
        nu12, rho = self.nu12, self.rho_
        G12, G13 = self.G12_, self.G13_
        G23, tref = self.G23_, self.tref_
        properties = {'name': self.name, 'mid': id_, 'E1': E1, 'E2': E2,
                      'nu12': nu12, 'G12': G12, 'rho': rho, 'G1z': G13,
                      'G2z': G23, 'tref': tref}
        for name, value in zip(['Xt', 'Xc', 'Yt', 'Yc'],
                               [self.Xt, self.Xc, self.Yt, self.Yc]):
            if value is not None:
                properties[name] = value
        S = max([0] + [_ for _ in [self.SL_, self.St_] if _ is not None])
        if S:
            properties['S'] = S_
        try:
            material = nastran_utils.MAT8(**properties)
        except AttributeError:
            raise ImportError('Nastran utils does not seem to have imported.')
        else:
            if model is not None:
                if add:
                    model.add(material)
            return material

    def define_in_patran(self, ses, mat_name=None):
        raise NotImplementedError

    @property
    def elastic(self) -> tuple[Quantity]:
        """
        Elastic properties table
        Returns
        -------
        tuple
        """
        return self.E1, self.E2, self.nu12, self.G12, self.G13, self.G23

    @property
    def elastic_(self) -> tuple[float]:
        """
        Elastic properties table, magnitude and converted to central
        unit system pressure unit

        Returns
        -------
        tuple
        """
        return self.E1_, self.E2_, self.nu12_, self.G12_, self.G13_, self.G23_

    @elastic.setter
    def elastic(self, damage: float):
        if damage == 1:
            tol = Q_(numerical_tolerance, self.unit_system.pressure)
        else:
            tol = Q_(0, self.unit_system.pressure)
        self.E1 = (1 - damage) * self.E1 + tol
        self.E2 = (1 - damage) * self.E2 + tol
        self.G12 = (1 - damage) * self.G12 + tol
        self.G13 = (1 - damage) * self.G13 + tol
        self.G23 = (1 - damage) * self.G23 + tol
        tol = float(tol.magnitude)
        self.E1_ = (1 - damage) * self.E1_ + tol
        self.E2_ = (1 - damage) * self.E2_ + tol
        self.G12_ = (1 - damage) * self.G12_ + tol
        self.G13_ = (1 - damage) * self.G13_ + tol
        self.G23_ = (1 - damage) * self.G23_ + tol

    @property
    def fracture_energy(self) -> tuple[Quantity]:
        """
        Fracture energy properties table

        Returns
        -------
        tuple
        """
        return self.Gft, self.Gfc, self.Gmf, self.Gmc

    @property
    def fracture_energy_(self) -> tuple[float]:
        """
        Fracture energy properties table, magnitude and converted to
        central unit system

        Returns
        -------
        tuple
        """
        return self.Gft_, self.Gfc_, self.Gmf_, self.Gmc_

    @property
    def nu21(self):
        return self.nu12 * self.E2_ / self.E1_

    @property
    def stress_limit(self) -> tuple[Quantity]:
        """
        Stress limit properties table

        Returns
        -------
        tuple
        """
        return self.Xt, self.Xc, self.Yt, self.Yc, self.SL, self.St

    @property
    def stress_limit_(self) -> tuple[float]:
        """
        Stress limit properties table, magnitude and converted to
        central unit system pressure unit

        Returns
        -------
        tuple
        """
        return self.Xt_, self.Xc_, self.Yt_, self.Yc_, self.SL_, self.St_


class Traction(Material):
    arg_units = {
        'name': str,
        'unit_system': None,
        'rho': 'density',
        'Enn': 'pressure', 'Ess': 'pressure', 'Ett': 'pressure',
        'tref': 'temperature',
        'tn': 'pressure', 'ts': 'pressure', 'tt': 'pressure',
        'Gn': 'energy', 'Gs': 'energy', 'Gt': 'energy',
        'bk': float
    }

    def __init__(self, name: str, unit_system: UnitSystem, rho: Quantity,
                 Enn: Quantity, Ess: Quantity, Ett: Quantity,
                 tref: Quantity = None, tn: Quantity = None,
                 ts: Quantity = None, tt: Quantity = None,
                 Gn: Quantity = None, Gs: Quantity = None, Gt: Quantity = None,
                 bk: float = 1.5):
        """
        Traction material class

        Parameters
        ----------
        name : str
            Name of material
        unit_system : UnitSystem
            Values will be converted to quantities in this unit system
            for internal consistency
        rho : Quantity
            Density of material
        Enn, Ess, Ett : Quantity
            Stiffnesses
        tref : Quantity, optional
            Reference temperature
        tn, ts, tt : Quantity, optional
            Quads damage initiation stress in normal and first and
            second shear directions
        Gn, Gs, Gt : Quantity, optional
            Quads damage evolution energies in normal and first and
            second shear directions
        bk : float, optional
            Benzeggagh-Kenane fracture criterion

        Notes
        -----
        - Specified for cohesive elements currently
        - Quads damage initiation is the only method implemented currently
        """
        super(Traction, self).__init__(name, unit_system, rho, tref)
        self.Enn = Enn
        self.Ess = Ess
        self.Ett = Ett
        self.tn = tn
        self.ts = ts
        self.tt = tt
        self.Gn = Gn
        self.Gs = Gs
        self.Gt = Gt
        self.bk = float(bk)
        super().__convert__(unit_system, Enn=Enn, Ess=Ess, Ett=Ett,
                            tn=tn, ts=ts, tt=tt, Gn=Gn, Gs=Gs, Gt=Gt)

    def __repr__(self) -> str:
        return ('Traction(name={x.name!r}, rho={x.rho!s}, Enn={x.Enn!s}, '
                'Ess={x.Ess!s}, Ett={x.Ett!s}, tref={x.tref!s}, tn={x.tn!s}, '
                'ts={x.ts!s}, tt={x.tt!s}, Gn={x.Gn!s}, Gs={x.Gs!s}, '
                'Gt={x.Gt!s}, bk={x.bk!s})'.format(x=self))

    def create_damage_evolution_abaqus(self):
        """
        Create damage evolution in Abaqus

        Notes
        -----
        - Only implemented in Lamina and Traction
        - Quads damage evolution
        """
        if not any([_ is None for _ in self.fracture_energy]):
            fracture_energy = tuple(self.fracture_energy_)
            self._mat.quadsDamageInitiation.DamageEvolution(
                ENERGY, (fracture_energy,), mixedModeBehavior=BK,
                power=self.bk)

    def define_in_nastran(self, model=None, id_: int = None,
                          add: bool = False):
        raise NotImplementedError

    def define_in_patran(self, ses, mat_name=None):
        raise NotImplementedError

    def create_stress_limit_abaqus(self):
        """
        Create stress limit/damage initiation in Abaqus

        Notes
        -----
        Limited for now to Quads damage initiation
        """
        if not any([_ is None for _ in self.stress_limit]):
            stress_limit = tuple(self.stress_limit_)
            self._mat.QuadsDamageInitiation((stress_limit,))

    @property
    def elastic(self) -> tuple[Quantity]:
        """
        Elastic properties table

        Returns
        -------
        tuple
        """
        return self.Enn, self.Ess, self.Ett

    @property
    def elastic_(self) -> tuple[float]:
        """
        Elastic properties table, magnitude and converted to central
        unit system pressure unit

        Returns
        -------
        tuple
        """
        return self.Enn_, self.Ess_, self.Ett_

    @elastic.setter
    def elastic(self, damage: float):
        if damage == 1:
            tol = Q_(numerical_tolerance, self.unit_system.pressure)
        else:
            tol = Q_(0, self.unit_system.pressure)
        self.Enn = (1 - damage) * self.Enn + tol
        self.Ess = (1 - damage) * self.Ess + tol
        self.Ett = (1 - damage) * self.Ett + tol
        tol = float(tol.magnitude)
        self.Enn_ = (1 - damage) * self.Enn_ + tol
        self.Ess_ = (1 - damage) * self.Ess_ + tol
        self.Ett_ = (1 - damage) * self.Ett_ + tol

    @property
    def fracture_energy(self) -> tuple[Quantity]:
        """
        Fracture energy properties table

        Returns
        -------
        tuple
        """
        return self.Gn, self.Gs, self.Gt

    @property
    def fracture_energy_(self) -> tuple[float]:
        """
        Fracture energy properties table, magnitude and converted to
        central unit system

        Returns
        -------
        tuple
        """
        return self.Gn_, self.Gs_, self.Gt_

    @property
    def stress_limit(self) -> tuple[Quantity]:
        """
        Stress limit table

        Returns
        -------
        tuple
        """
        return self.tn, self.ts, self.tt

    @property
    def stress_limit_(self) -> tuple[float]:
        """
        Stress limit table, magnitude and converted to central unit
        system

        Returns
        -------
        tuple
        """
        return self.tn_, self.ts_, self.tt_


mat_classes = {
    'Composite': Composite, 'Material': Material,
    'EngineeringConstants': EngineeringConstants, 'Fluid': Fluid,
    'Isotropic': Isotropic, 'Lamina': Lamina, 'Traction': Traction
}
