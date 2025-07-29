"""
Unit system and unit handling utilities developed as an extension of the
[`pint` package](https://github.com/hgrecco/pint) as part of
`pymatunits`

Copyright (C) 2023 Adam Cox

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

Dependencies
----------------- -------------------------------------------------------------
pint                Physical quantity manipulation package

Standard example usage of pint
----------------------------------------------------------------
>>> from pint import UnitRegistry
>>> ureg = UnitRegistry()
>>> Q_ = ureg.Quantity  # Standard alias from pint documentation
----------------------------------------------------------------
Optionally can include the following to Imperial mass units

NOTE: These units may be added in a future version of pint
----------------------------------------------------------------
>>> ureg.load_definitions(
>>>     ['slug = lbf * s ** 2 / foot',
>>>      'slinch = lbf * s ** 2 / inch = blob = slugette',
>>>      'pound_force_per_square_foot = lbf / foot ** 2 = psf'])


You can store quantities two different ways:
    - Q_(value, unit)  # Preferred
    - UnitSystem.quantity
You can convert units a number of ways:
    - Quantity.to(unit)  # Preferred
    - value*ureg(from_unit).to(unit)

The UnitSystem static methods are there for porting a UnitSystem
object into a package that doesn't have pint as a dependency.

The UnitSystem class allows you to store a unit system, check for
consistency, and carry a system through your code to use for conversion.

TODO
----
- convert : check dimensionality if no conversion?
    Uses check_consistency to succesfully convert *to* a unit system,
    but can't handle converting *from* non-standard units
"""
from os.path import isfile
import json
from json.decoder import JSONDecodeError
import re
from pint import DimensionalityError, UnitRegistry
from . import logger, numerical_tolerance
ureg = UnitRegistry()
ureg.load_definitions(['slug = lbf * s ** 2 / foot',
                       'slinch = lbf * s ** 2 / inch = blob = slugette',
                       'pound_force_per_square_foot = lbf / foot ** 2 = psf'])
Q_ = ureg.Quantity


def convert(unit_system, value, unit_str, magnitude=False):
    """
    Check if input is a value (float, int) or a Quantity.
    If a Quantity, convert to appropriate unit and return magnitude.

    Parameters
    ----------
    unit_system : UnitSystem
    value : Union[float, Quantity]
        Either a value (float, int) or pint Quantity
    unit_str : str
        Unit system quantity string, e.g. 'length', 'acceleration' or
        combined string, e.g. 'force * length'
    magnitude : bool, optional
        Flag to return float magnitude instead of pint Quantity. Default
        is False.

    Raises
    ------
    AttributeError
        When unit string contains invalid strings
    DimensionalityError
        When converting from non-standard dimensionality. For converting
        to non-standard, should use check_consistency to provide
        appropriate dimensionality correction.

    Returns
    -------
    value : Union[Quantity, float]
    """
    if value is not None:
        words = re.compile(r'[a-z]+')
        unit_strs = re.findall(words, unit_str)
        unit = str(unit_str)
        for unit_type in unit_strs:
            actual = str(getattr(unit_system, unit_type).u)
            unit = unit.replace(unit_type, actual)
        try:
            value.magnitude
        except AttributeError:
            value = Q_(float(value), unit)
        else:  # Quantity
            corrections = unit_system.correction_factors
            try:
                value = (value / corrections[unit_str]).to(unit)
            except KeyError:
                value = value.to(unit)
        if magnitude:
            value = float(value.magnitude)
    return value


class UnitSystem(object):
    logger = logger

    def __init__(self, acceleration=None, angle='radian', area=None,
                 density=None, energy=None, force=None, length=None, mass=None,
                 power=None, pressure=None, speed=None, temperature='kelvin',
                 time='second', volume=None, name=None):
        """
        Class to store unit system and convert units. Works as a
        front-end for the pint python physical quantity package.

        Example Usages
        --------------
        - Default values in code
            - Define default values in code using UnitSystem.quantity
              static method
            - Pass in UnitSystem object
        - Unit consistency
            - Define UnitSystem object
            - Use UnitSystem.check_consistency to check if
                - Length units consistent across system
                - Pressure unit selection correct
                    - m, N, s => Pa
                    - mm, N, s => MPa
                    - mm, kN, ms => GPa

        Links for example sets of consistent units
        ------------------------------------------
        - https://femci.gsfc.nasa.gov/units/
        - http://www.idac.co.uk/services/downloads/consistent.pdf
        - http://www.dynasupport.com/howtos/general/consistent-units

        Parameters
        ----------
        acceleration : str, optional
            Default value is None, will derive unit
            ([length] / [time] ** 2)
        angle : str, optional
            Base unit. Default value is 'radian'.
        area : str, optional
            Default value is None, will derive unit ([length] ** 2)
        density : str, optional
            Default value is None, will derive unit ([mass] / [volume])
        energy : str, optional
            Default value is None, will derived unit
            ([force] * [length])
        force : str, optional
            Default value is None, will derive unit
            ([mass] * [acceleration])
        length : str, optional
            Base unit. If no base units defined, will default to mks.
        mass : str, optional
            Base unit. If no base units defined, will default to mks.
        power : str, optional
            Default value is None, will derive unit ([energy] / [time])
        pressure : str, optional
            Default value is None, will derive unit ([force] / [area])
        speed : str, optional
            Default value is None, will derive unit ([length] / [time])
        temperature : str, optional
            Base unit. Default value is 'kelvin'.
        time : str, optional
            Base unit. Default value is 'second'.
        volume : str, optional
            Default value is None, will derive unit ([length] ** 3)
        name : str, optional

        Notes
        -----
        - Default unit system is meter/kilogram/second
        - Manually added slug to default mass units in pint

        For a list of the units in Pint by default, see
        pint/default_en.txt

        Unit types that could be added later
        ====================================
        EM, Frequency, Heat, Information, Irradiance, Textile,
        Photometry, Radiation, Viscosity

        Examples
        --------
        >>> from pymatunits.units import UnitSystem, Q_, DimensionalityError
        >>> value = Q_(1.0, 'pound')
        >>> print(value.magnitude)  # or value.m
        >>> print(value.units)  # or value.u
        >>> print(value.unitless)  # returns False here
        >>> print(value.dimensionality)
        >>> print(value.dimensionless)  # returns False here
        >>> print(value.compatible_units())
        >>> print(value.to('kg'))
        >>> units = UnitSystem.meter_kilogram_second()  # or UnitSystem.mks()
        >>> value.to(units.mass)
        >>> try:
        >>>     print(value.to(units.force))
        >>> except DimensionalityError:
        >>>     print("Can't convert mass to force")
        >>>     print((value.to(units.mass) * units.g).to(units.force))
        >>> units.check_consistency()
        """
        if not angle:
            raise ValueError('Base unit angle not defined')
        self.angle = ureg(angle)
        if all(_unit is None for _unit in [length, mass]):
            logger.info('Defaulting to MKS unit system')
            if not all((angle == 'radian', temperature == 'kelvin',
                        time == 'second')):
                logger.info('Some parameters may be inconsistent with '
                            'defaulted units')
            energy = 'joule'
            force = 'newton'
            length = 'meter'
            mass = 'kilogram'
            power = 'watt'
            pressure = 'pascal'
            if name is None:
                name = 'Meter-Kilogram-Second'
        elif any(_unit is None for _unit in
                 [angle, length, mass, temperature, time]):
            raise ValueError('Base unit not defined, '
                             'e.g. length, mass, temperature, and time')
        self._acceleration = acceleration
        self._area = area
        self._density = density
        self._energy = energy
        self._force = force
        self.length = ureg(length)
        self.mass = ureg(mass)
        self._power = power
        self._pressure = pressure
        self._speed = speed
        self.temperature = ureg(temperature)
        self.time = ureg(time)
        self._volume = volume
        self.name = name
        self._correction_factors = None

    def __eq__(self, other):
        try:
            assert isinstance(other, UnitSystem)
        except AssertionError:
            return False
        else:
            return repr(self) == repr(other)

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        acceleration = self.acceleration.units
        angle = self.angle.units
        area = self.area.units
        density = self.density.units
        energy = self.energy.units
        force = self.force.units
        length = self.length.units
        mass = self.mass.units
        power = self.power.units
        pressure = self.pressure.units
        speed = self.speed.units
        temperature = self.temperature.units
        time = self.time.units
        volume = self.volume.units
        name = self.name
        return ("UnitSystem(acceleration='{}', angle='{}', area='{}', "
                "density='{}', energy='{}', force='{}', length='{}', "
                "mass='{}', power='{}', pressure='{}', speed='{}', "
                "temperature='{}', time='{}', volume='{}', name='{}')".format(
                        acceleration, angle, area, density, energy, force,
                        length, mass, power, pressure, speed, temperature,
                        time, volume, name))

    def __str__(self):
        str_ = '=' * 42 + '\n' + '{:^42}\n'.format('Unit System')
        if self.name:
            str_ += '{:^42}\n'.format(self.name)
        str_ += '=' * 42 + '\n'
        rows = [
            ('Acceleration', self.acceleration), ('Angle', self.angle),
            ('Area', self.area), ('Density', self.density),
            ('Energy', self.energy), ('Force', self.force),
            ('Length', self.length), ('Mass', self.mass),
            ('Power', self.power), ('Pressure', self.pressure),
            ('Speed', self.speed), ('Temperature', self.temperature),
            ('Time', self.time), ('Volume', self.volume)]
        for key, value in rows:
            str_ += '{} : {}\n'.format(key, value.units)
        str_ += '=' * 42
        return str_

    @property
    def acceleration(self):
        """
        Acceleration unit, given or derived as [length] over [time] squared

        Returns
        -------
        acceleration : Quantity
        """
        if not self._acceleration:
            return ureg('{}/{}**2'.format(self.length.units, self.time.units))
        return ureg(self._acceleration)

    @property
    def area(self):
        """
        Area unit, given or derived as  [length] squared

        Returns
        -------
        area : Quantity
        """
        if not self._area:
            return ureg('{}**2'.format(self.length.units))
        return ureg(self._area)

    @classmethod
    def british_gravitational(cls):
        """
        British Gravitational system of units

        Base Units
        ----------
        force : 'pound'
        length : 'foot'
        mass : 'slug'
        temperature : 'fahrenheit'
        time : 'second'

        Returns
        -------
        unit_system : UnitSystem
        """
        energy = None
        force = 'pound'
        length = 'foot'
        mass = 'slug'
        power = None
        pressure = None
        temperature = 'fahrenheit'
        time = 'second'
        name = 'British Gravitational'
        return cls(energy=energy, force=force, length=length, mass=mass,
                   power=power, pressure=pressure, temperature=temperature,
                   time=time, name=name)

    @classmethod
    def centimeter_gram_second(cls):
        """
        Centimeter-gram-second system of units

        Base Units
        ----------
        energy : 'erg'  # g*cm**2/s**2
        force : 'dyne'  # g*cm/s**2
        length : 'centimeter'
        mass : 'gram'
        power : 'erg/s'  # g*cm**2/s**3
        pressure : 'decipascal'  # g/cm/s**2 (also called a barye)
        temperature : 'kelvin'
        time : 'second'

        Returns
        -------
        unit_system : UnitSystem
        """
        energy = 'erg'
        force = 'dyne'
        length = 'centimeter'
        mass = 'gram'
        power = 'erg/s'
        pressure = 'decipascal'
        temperature = 'kelvin'
        time = 'second'
        name = 'Centimeter-Gram-Second'
        return cls(energy=energy, force=force, length=length, mass=mass,
                   power=power, pressure=pressure, temperature=temperature,
                   time=time, name=name)

    @classmethod
    def cgs(cls):
        """
        Centimeter-gram-second system of units

        Base Units
        ----------
        energy : 'erg'  # g*cm**2/s**2
        force : 'dyne'  # g*cm/s**2
        length : 'centimeter'
        mass : 'gram'
        power : 'erg/s'  # g*cm**2/s**3
        pressure : 'decipascal'  # g/cm/s**2 (also called a barye)
        temperature : 'kelvin'
        time : 'second'

        Returns
        -------
        unit_system : UnitSystem
        """
        return cls.centimeter_gram_second()

    def check_consistency(self, return_log=False):
        """
        Check internal unit consistency of defined system

        Notes
        -----
        Writes to log and returns corrections if not consistent

        Checks
        ------
        [area] :
            [length]**2
        [density] :
            [mass]/[volume], [mass]*[time]**2/[length]**4, or
            [force]/[volume]
        [energy] :
            [force]*[length]
        [force] :
            [mass]*[acceleration]
        [power] :
            [energy]/[time]
        [pressure] :
            [mass]/[length]/[time]**2
        [speed]
            [length]/[time]
        [volume] :
            [length]**3

        Parameters
        ----------
        return_log : bool, optional
            Private optional parameter to return message as string

        Returns
        -------
        message : str, optional
            If `return_log` is True. Otherwise, returns None.

        Examples
        --------
        >>> units = UnitSystem.english_inch_force()
        >>> correct = units.check_consistency()  # writes to log
        >>> quantity = Q_(1.0, units.density)
        >>> # quantity: <Quantity(1.0, 'force_pound / inch ** 3')>
        >>> # quantity.to('kg / m ** 3')  # raises DimensionalityError
        >>> converted = (quantity * correct['density']).to('kg / m ** 3')
        >>> # converted: <Quantity(27679.90471020313, 'kilogram / meter ** 3')>
        """
        tol = numerical_tolerance
        corrections = dict()
        write_level = self.logger.info
        message = (
                '=' * 72 + '\nBegin checking for consistency\n' + '=' * 72 +
                '\n' + '=' * 72 +
                '\n- If off by factor of 10, change SI prefix\n'
                '- If off by factor of 12, check English length units\n'
                '- If off by factor of 9.81, 32.2, or 386, might need to '
                'correct by g\n' + '-' * 72 + '\n')
        message += (
                'Base Units\n' + '-' * 72 + '\n- Angle : ' +
                str(self.angle.units) + '\n' +
                '- Length : ' + str(self.length.units) + '\n' +
                '- Mass : ' + str(self.mass.units) + '\n' +
                '- Temperature : ' + str(self.temperature.units) + '\n' +
                '- Time : ' + str(self.time.units) + '\n' + '-' * 72 + '\n')
        key = 'acceleration'
        if not self._acceleration:
            message += ('- DERIVED UNIT : Acceleration unit not given, '
                        'derived instead\n')
        if self.acceleration.dimensionality != {'[length]': 1, '[time]': -2}:
            write_level = self.logger.warning
            message += ('- WARNING : Acceleration unit is not length per '
                        'squared time\n')
        unit = self.length / self.time ** 2
        value = unit.to(self.acceleration).magnitude
        if abs(value - 1.0) < tol:
            message += ('- PASS : Acceleration consistent with length and '
                        'time\n')
        else:
            write_level = self.logger.warning
            message += (
                '- FAIL : Acceleration inconsistent with length and time: {}\n'
                '  [acceleration] : {} <=> {} : '
                '[length] / [time] ** 2\n'.format(
                    value, self.acceleration.units, unit.units))
            corrections[key] = value
        key = 'area'
        if not self._area:
            message += ('- DERIVED UNIT : Area unit not given, derived '
                        'instead\n')
        if self.area.dimensionality != {'[length]': 2}:
            write_level = self.logger.warning
            message += '- WARNING : Area unit is not squared length\n'
        unit = self.length ** 2
        value = unit.to(self.area).magnitude
        if abs(value - 1.0) < tol:
            message += '- PASS : Area consistent with length\n'
        else:
            write_level = self.logger.warning
            message += (
                '- FAIL : Area inconsistent with length : {}\n'
                '  [area] : {} <=> {} : [length] ** 2\n'.format(
                    value, self.area.units, unit.units))
            corrections[key] = value
        key = 'density'
        if not self._density:
            message += ('- DERIVED UNIT : Density unit not given, derived '
                        'instead\n')
        if self.density.dimensionality != {'[mass]': 1, '[length]': -3}:
            write_level = self.logger.warning
            message += '- WARNING : Density unit is not mass per volume\n'
        if self.density.dimensionality['[time]'] == 0:
            unit = self.mass / self.volume
            value = unit.to(self.density).magnitude
            if abs(value - 1.0) < tol:
                message += '- PASS : Density consistent with mass/volume\n'
            else:
                write_level = self.logger.warning
                message += (
                    '- FAIL : Density inconsistent with mass/volume : {}\n'
                    '  [density] : {} <=> {} : [mass]/[volume]\n'.format(
                        value, self.density.units, unit.units))
                corrections[key] = value
        elif self.density.dimensionality['[time]'] == 2:
            unit = self.mass * self.time ** 2 / self.length ** 4
            value = unit.to(self.density).magnitude
            if abs(value - 1.0) < tol:
                message += ('- PASS : Density consistent with '
                            'mass/time/length\n')
            else:
                write_level = self.logger.warning
                message += (
                    '- FAIL : Density inconsistent with '
                    'mass/time/length : {}\n'
                    '  [density] : {} <=> {} : '
                    '[mass] * [time] ** 2/[length] ** 4\n'.format(
                        value, self.density.units, unit.units))
                corrections[key] = value
        elif self.density.dimensionality['[time]'] == -2:
            values = list()
            unit = self.force / self.volume
            value = unit.to(self.density).magnitude
            if abs(value - 1.0) < tol:
                message += '- PASS : Density consistent with force/volume\n'
            else:
                write_level = self.logger.warning
                self.logger += (
                    '- FAIL : Density inconsistent with force/volume : {}\n'
                    '  [density] : {} <=> {} : [force]/[volume]\n'.format(
                        value, self.density.units, unit.units))
                values.append(value)
            unit = (ureg(str(self.mass.units)) * self.g.units /
                    ureg(str(self.volume.units)))
            try:
                value = unit.to(self.density).magnitude
            except DimensionalityError:
                try:
                    value = (unit / self.g).to(self.density).magnitude
                    value = Q_(value, 1 / self.g.units)
                except DimensionalityError:
                    try:
                        value = (unit * self.g).to(self.density).magnitude
                        value = Q_(value, self.g.units)
                    except DimensionalityError as e:
                        write_level = self.logger.error
                        message += e
            try:
                value.magnitude
            except AttributeError:
                if abs(value - 1.0) < tol:
                    message += ('- PASS : Density consistent with '
                                'mass/gravity/volume\n')
                else:
                    write_level = self.logger.warning
                    message += (
                        '- FAIL : Density inconsistent with '
                        'mass/gravity/volume : {}\n'
                        '  [density] : {} <=> {} : [force]/[volume]\n'.format(
                            value, self.density.units, unit.units))
                    values.append(value)
            else:
                write_level = self.logger.warning
                message += ('- FAIL : Density units inconsistent with mass '
                            'by {}\n'.format(value))
                values.append(value)
            if values:
                if len(values) == 1:
                    corrections[key] = values[0]
                else:
                    corrections[key] = tuple(values)
        key = 'energy'
        if not self._energy:
            message += ('- DERIVED UNIT : Energy unit not given, derived '
                        'instead\n')
        if self.energy.dimensionality != {'[length]': 2, '[mass]': 1,
                                          '[time]': -2}:
            write_level = self.logger.warning
            message += '- WARNING : Energy unit not force times length\n'
        unit = self.force * self.length
        value = unit.to(self.energy).magnitude
        if abs(value - 1.0) < tol:
            message += '- PASS : Energy consistent with length and speed\n'
        else:
            write_level = self.logger.warning
            message += (
                '- FAIL : Energy inconsistent with length and speed : {}\n'
                '  [energy] : {} <=> {} : [force]*[length]\n'.format(
                    value, self.energy.units, unit.units))
            corrections[key] = value
        key = 'force'
        if not self._force:
            message += ('- DERIVED UNIT : Force unit not given, derived '
                        'instead\n')
        if self.force.dimensionality != {'[length]': 1, '[mass]': 1,
                                         '[time]': -2}:
            write_level = self.logger.warning
            message += ('- WARNING : Force unit not length times mass over '
                        'squared time\n')
        unit = self.mass * self.acceleration
        try:
            value = unit.to(self.force).magnitude
        except DimensionalityError:
            try:
                value = (unit / self.g).to(self.force).magnitude
                value = Q_(value, 1 / self.g.units)
            except DimensionalityError:
                try:
                    value = (unit * self.g).to(self.force).magnitude
                    value = Q_(value, self.g.units)
                except DimensionalityError as e:
                    write_level = self.logger.error
                    message += e
        try:
            value.magnitude
        except AttributeError:
            if abs(value - 1.0) < tol:
                message += ('- PASS : Force consistent with mass and '
                            'acceleration\n')
            else:
                write_level = self.logger.warning
                message += (
                    '- FAIL : Force inconsistent with mass and '
                    'acceleration : {}\n'
                    '   [force] : {} <=> {} : [mass]*[acceleration]\n'.format(
                        value, self.force.units, unit.units))
                corrections[key] = value
        else:
            write_level = self.logger.warning
            message += ('- FAIL : Force units inconsistent with mass '
                        'by {}\n'.format(value))
            corrections[key] = value
        key = 'power'
        if not self._power:
            message += ('- DERIVED UNIT : Power unit not given, derived '
                        'instead\n')
        if self.power.dimensionality != {'[length]': 2, '[mass]': 1,
                                         '[time]': -3}:
            write_level = self.logger.warning
            message += '- WARNING : Power unit not energy over time\n'
        unit = self.energy / self.time
        value = unit.to(self.power).magnitude
        if abs(value - 1.0) < tol:
            message += '- PASS : Power consistent with energy and time\n'
        else:
            write_level = self.logger.warning
            message += (
                '- FAIL : Power inconsistent with energy and time : {}\n'
                '  [power] : {} <=> {} : [energy]/[time]\n'.format(
                    value, self.power.units, unit.units))
            corrections[key] = value
        key = 'pressure'
        if not self._pressure:
            message += ('- DERIVED UNIT : Pressure unit not given, derived '
                        'instead\n')
        if self.pressure.dimensionality != {'[length]': -1, '[mass]': 1,
                                            '[time]': -2}:
            write_level = self.logger.warning
            message += ('- WARNING : Pressure unit not mass over length times '
                        'squared time\n')
        unit = self.mass / self.length / self.time ** 2
        try:
            value = unit.to(self.pressure).magnitude
        except DimensionalityError:
            try:
                value = (unit / self.g).to(self.pressure).magnitude
                value = Q_(value, 1 / self.g.units)
            except DimensionalityError:
                try:
                    value = (unit * self.g).to(self.pressure).magnitude
                    value = Q_(value, self.g.units)
                except DimensionalityError as e:
                    write_level = self.logger.error
                    message += e
        try:
            value.magnitude
        except AttributeError:
            if abs(value - 1.0) < tol:
                message += ('- PASS : Pressure consistent with mass, length, '
                            'and time\n')
            else:
                write_level = self.logger.warning
                message += (
                    '- FAIL : Pressure inconsistent by factor : {}\n'
                    '  [pressure] : {} <=> {} : '
                    '[mass]/[length]/[time]**2\n'.format(
                        value, self.pressure.units, unit.units))
                corrections[key] = value
        else:
            write_level = self.logger.warning
            message += (
                '- FAIL : Pressure units inconsistent with mass by '
                '{}\n'.format(
                    value))
            corrections[key] = value
        key = 'speed'
        if not self._speed:
            message += ('- DERIVED UNIT : Speed unit not given, derived '
                        'instead\n')
        if self.speed.dimensionality != {'[length]': 1, '[time]': -1}:
            write_level = self.logger.warning
            message += '- WARNING : Speed unit not length over time\n'
        unit = self.length / self.time
        value = unit.to(self.speed).magnitude
        if abs(value - 1.0) < tol:
            message += '- PASS : Speed consistent with length and time\n'
        else:
            write_level = self.logger.warning
            message += (
                '- FAIL : Speed inconsistent with length and time : {}\n'
                '  [speed] : {} <=> {} : [length]/[time]\n'.format(
                    value, self.speed.units, unit.units))
            corrections[key] = value
        key = 'volume'
        if not self._volume:
            message += ('- DERIVED UNIT : Volume unit not given, derived '
                        'instead\n')
        if self.volume.dimensionality != {'[length]': 3}:
            write_level = self.logger.warning
            message += '- WARNING : Volume unit not cubed length\n'
        unit = self.length ** 3
        value = unit.to(self.volume).magnitude
        if abs(value - 1.0) < tol:
            message += '- PASS : Volume consistent with length\n'
        else:
            write_level = self.logger.warning
            message += (
                '- FAIL : Volume inconsistent with length : {}\n'
                '  [volume] : {} <=> {} : [length]**3\n'.format(
                    value, self.area.units, unit.units))
            corrections[key] = value
        if not corrections:
            message += (
                    '-' * 72 + '\nALL CONSISTENCY CHECKS MET\n' + '=' * 72 +
                    '\n' + '=' * 72)
        else:
            write_level = self.logger.warning
            message += ('-' * 72 + '\nINCONSISTENCIES PRESENT\n' + '=' * 72 +
                        '\n' + '=' * 72)
        if self._correction_factors is None:
            self._correction_factors = corrections
        if return_log:
            return message
        else:
            write_level(message)
            return

    @property
    def correction_factors(self):
        """
        Correction factors if unit system is not internally consistent

        Returns
        -------
        corrections : dict[str: float, Quantity]
        """
        if self._correction_factors is None:
            _ = self.check_consistency(True)
        return self._correction_factors

    @property
    def density(self):
        """
        Density unit, given or derived as [mass] over [length] cubed

        Returns
        -------
        area : Quantity
        """
        if not self._density:
            return ureg('{}/{}**3'.format(self.mass.units, self.length.units))
        return ureg(self._density)

    @property
    def energy(self):
        """
        Energy unit, given or derived as [force] times [length]

        Notes
        -----
        - e.g. N-m or lbf-ft
        - Also the unit of moment, torque, or work

        Returns
        -------
        energy : Quantity
        """
        if not self._energy:
            return ureg('{}*{}'.format(self.force.units, self.length.units))
        return ureg(self._energy)

    @classmethod
    def english_engineering(cls):
        """
        English engineering system of units

        Base Units
        ----------
        force : 'lbf'
        length : 'foot'
        mass : 'pound'
        temperature : 'fahrenheit'
        time : 'second'

        Returns
        -------
        unit_system : UnitSystem
        """
        energy = None
        force = 'lbf'
        length = 'foot'
        mass = 'pound'
        power = None
        pressure = None
        temperature = 'fahrenheit'
        time = 'second'
        name = 'English Engineering'
        return cls(energy=energy, force=force, length=length, mass=mass,
                   power=power, pressure=pressure, temperature=temperature,
                   time=time, name=name)

    @classmethod
    def english_inch_force(cls):
        """
        English system based on inches and force units from FEMCI

        Notes
        -----
        This is a weight/mass inconsistent system and must be adjusted
        in Nastran by ~0.00259 using the WTMASS parameter

        Base Units
        ----------
        density : 'lbf / inch ** 3'
        force : 'lbf'
        length : 'inch'
        mass : 'lbf'
        pressure : 'psi'
        temperature : 'fahrenheit'
        time : 'second'

        Returns
        -------
        unit_system : UnitSystem
        """
        density = 'lbf / inch ** 3'
        energy = None
        force = 'lbf'
        length = 'inch'
        mass = 'lbf'
        power = None
        pressure = 'psi'
        temperature = 'fahrenheit'
        time = 'second'
        name = 'English Inch Force'
        return cls(density=density, energy=energy, force=force,
                   length=length, mass=mass, power=power, pressure=pressure,
                   temperature=temperature, time=time, name=name)

    @classmethod
    def english_inch_mass(cls):
        """
        English system based on inches and mass units from FEMCI

        Base Units
        ----------
        density : 'lbf * s ** 2 / inch ** 4'
        force : 'lbf'
        length : 'inch'
        mass : 'lbf * s ** 2 / inch'
        pressure : 'psi'
        temperature : 'fahrenheit'
        time : 'second'

        Returns
        -------
        unit_system : UnitSystem
        """
        density = 'lbf * s ** 2 / inch ** 4'
        energy = None
        force = 'lbf'
        length = 'inch'
        mass = 'lbf * s ** 2 / inch'
        power = None
        pressure = 'psi'
        temperature = 'fahrenheit'
        time = 'second'
        name = 'English Inch Mass'
        return cls(density=density, energy=energy, force=force,
                   length=length, mass=mass, power=power, pressure=pressure,
                   temperature=temperature, time=time, name=name)

    @property
    def force(self):
        """
        Force unit, given or defined as [mass] * [length] / [time] ** 2

        Notes
        -----
        - e.g. Newtons == 'kg*m/s**2'

        Returns
        -------
        force : Quantity
        """
        if not self._force:
            return ureg('{}*{}/{}**2'.format(
                self.mass.units, self.length.units, self.time.units))
        return ureg(self._force)

    @classmethod
    def from_dict(cls, saved):
        """
        Create UnitSystem object from saved unit_system.__dict__

        Parameters
        ----------
        saved : dict

        Returns
        -------
        unit_system : UnitSystem
        """
        kwargs = dict()
        for _key in saved:
            if '_' in _key[0]:
                key = _key[1:]
            else:
                key = _key
            kwargs[key] = saved[_key]
        return cls(**kwargs)

    @classmethod
    def read_json(cls, path):
        if not isfile(path):
            try:
                return cls.from_dict(json.loads(path))
            except JSONDecodeError:
                raise FileNotFoundError('Invalid path or JSON string')
        with open(path, 'r') as f:
            return cls.from_dict(json.load(f))

    @classmethod
    def from_repr(cls, saved):
        """
        Create UnitSystem object from saved repr string instead of using
        eval on repr

        Parameters
        ----------
        saved : str
            String created using class __repr__

        Returns
        -------
        unit_system : UnitSystem
        """
        args = saved.lstrip('UnitSystem(').rstrip(')').split(', ')
        arg_tuples = [_.split('=') for _ in args]
        kwargs = {key: value.strip("'") for key, value in arg_tuples}
        return cls(**kwargs)

    @property
    def g(self):
        """
        Quantity of gravitational constant with system acceleration units

        Returns
        -------
        g : Quantity
        """
        return ureg('gravity').to(self.acceleration)

    @property
    def gravity(self):
        """
        Quantity of gravitational constant with system acceleration units

        Notes
        -----
        e.g. Quantity(9.80665, 'meter / second ** 2')

        Returns
        -------
        g : Quantity
        """
        return self.g

    @classmethod
    def meter_kilogram_second(cls):
        """
        Meter-kilogram-second system of units

        Base Units
        ----------
        energy : 'joule'
        force : 'newton'
        length : 'meter'
        mass : 'kilogram'
        power : 'watt'
        pressure : 'pascal'
        temperature : 'kelvin'
        time : 'second'

        Returns
        -------
        unit_system : UnitSystem
        """
        energy = 'joule'
        force = 'newton'
        length = 'meter'
        mass = 'kilogram'
        power = 'watt'
        pressure = 'pascal'
        temperature = 'kelvin'
        time = 'second'
        name = 'Meter-Kilogram-Second'
        return cls(energy=energy, force=force, length=length, mass=mass,
                   power=power, pressure=pressure, temperature=temperature,
                   time=time, name=name)

    @classmethod
    def mks(cls):
        """
        Meter-kilogram-second system of units

        Base Units
        ----------
        energy : 'joule'
        force : 'newton'
        length : 'meter'
        mass : 'kilogram'
        power : 'watt'
        pressure : 'pascal'
        temperature : 'kelvin'
        time : 'second'

        Returns
        -------
        unit_system : UnitSystem
        """
        return cls.meter_kilogram_second()

    @classmethod
    def meter_tonne_second(cls):
        """
        Meter-tonne-second system of units

        Base Units
        ----------
        energy : 'kJ' / 'kilojoule'
        force : 'kN' / 'kilonewton'
        length : 'meter'
        mass : 'tonne'
        power : 'kW' / 'kilowatt'
        pressure : 'kPa' / 'kilopascal'
        temperature : 'kelvin'
        time : 'second'

        Returns
        -------
        unit_system : UnitSystem
        """
        energy = 'kJ'
        force = 'kN'
        length = 'meter'
        mass = 'tonne'
        power = 'kW'
        pressure = 'kPa'
        temperature = 'kelvin'
        time = 'second'
        name = 'Meter-Tonne-Second'
        return cls(energy=energy, force=force, length=length, mass=mass,
                   power=power, pressure=pressure, temperature=temperature,
                   time=time, name=name)

    @classmethod
    def mts(cls):
        """
        Meter-tonne-second system of units

        Base Units
        ----------
        energy : 'kJ' / 'kilojoule'
        force : 'kN' / 'kilonewton'
        length : 'meter'
        mass : 'tonne'
        power : 'kW' / 'kilowatt'
        pressure : 'kPa' / 'kilopascal'
        temperature : 'kelvin'
        time : 'second'

        Returns
        -------
        unit_system : UnitSystem
        """
        return cls.meter_tonne_second()

    @classmethod
    def millimeter_tonne_second(cls):
        """
        Millimeter-tonne-second system of units

        Base Units
        ----------
        energy : 'mJ' / 'millijoule'
        force : 'N' / 'newton', also called a sthene
        length : 'millimeter'
        mass : 'tonne'
        power : 'mW' / 'milliwatt'
        pressure : 'MPa' / 'megapascal'
        temperature : 'kelvin'
        time : 'second'

        Returns
        -------
        unit_system : UnitSystem
        """
        energy = 'mJ'
        force = 'N'
        length = 'millimeter'
        mass = 'tonne'
        power = 'mW'
        pressure = 'MPa'
        temperature = 'kelvin'
        time = 'second'
        name = 'Millimeter-Tonne-Second'
        return cls(energy=energy, force=force, length=length, mass=mass,
                   power=power, pressure=pressure, temperature=temperature,
                   time=time, name=name)

    @classmethod
    def mmts(cls):
        """
        Millimeter-tonne-second system of units

        Base Units
        ----------
        energy : 'mJ' / 'millijoule'
        force : 'N' / 'newton', also called a sthene
        length : 'millimeter'
        mass : 'tonne'
        power : 'mW' / 'milliwatt'
        pressure : 'MPa' / 'megapascal'
        temperature : 'kelvin'
        time : 'second'

        Returns
        -------
        unit_system : UnitSystem
        """
        return cls.millimeter_tonne_second()

    @property
    def power(self):
        """
        Power unit, given or derived as [force] times [length] over [time]

        Returns
        -------
        power : Quantity
        """
        if not self._power:
            return ureg('{}*{}/{}'.format(
                self.force.units, self.length.units, self.time.units))
        return ureg(self._power)

    @property
    def pressure(self):
        """
        Pressure unit, given or derived as [force] over [area]

        Notes
        -----
        - e.g. PSI, MPa
        - Also the unit of stress

        Returns
        -------
        pressure : Quantity
        """
        if not self._pressure:
            return ureg('{}/{}'.format(self.force.units, self.area.units))
        return ureg(self._pressure)

    def to_dict(self):
        """
        Create a dictionary for saving and loading UnitSystem

        Returns
        -------
        system_dict : dict
        """
        system_dict = dict()
        dict_ = self.__dict__
        for key in dict_:
            if 'correction' in key:
                continue
            elif dict_[key] is not None:
                try:
                    value = dict_[key].units
                except AttributeError:
                    value = dict_[key]
                value = str(value)
                system_dict[key] = value
            else:
                system_dict[key] = None
        return system_dict

    def to_json(self, path=None):
        if not path:
            return json.dumps(self.to_dict())
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f)

    @property
    def speed(self):
        """
        Speed unit, given or derived as [length] over [time]

        Returns
        -------
        speed : Quantity
        """
        if not self._speed:
            return ureg('{}/{}'.format(self.length.units, self.time.units))
        return ureg(self._speed)

    @property
    def volume(self):
        """
        Volume unit, given or derived as [length] cubed

        Returns
        -------
        volume : Quantity
        """
        if not self._volume:
            return ureg('{}**3'.format(self.length.units))
        return ureg(self._volume)


class UnitMixin(object):
    arg_units = dict()

    def __convert__(self, unit_system: UnitSystem, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
            unit = self.arg_units[key]
            if isinstance(unit, str):
                setattr(self, key + '_',
                        convert(unit_system, value, unit, True))
