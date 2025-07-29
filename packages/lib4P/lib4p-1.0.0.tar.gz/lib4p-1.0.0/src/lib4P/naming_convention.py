import re
import warnings


class NamingConvention:
    class Utils:

        INTEGER_PATTERN = r"[+-]?\d+"
        FLOAT_PATTERN = r"[+-]?((\d+(\.\d+)+))"
        NUMBER_PATTERN = r"[+-]?((\d+(\.\d+)?))"  # INTEGER OR FLOAT

        class ValueBuilder:
            def __init__(self, value):
                self.value = value
                self.possible_prefixes = set()
                self.possible_suffixes = set()

            def add_possible_prefix(self, prefix):
                self.possible_prefixes.add(prefix)
                return self

            def add_possible_suffix(self, suffix):
                self.possible_suffixes.add(suffix)
                return self

            def add_possible_prefixes(self, prefixes):
                self.possible_prefixes = self.possible_prefixes.union(prefixes)
                return self

            def add_possible_suffixes(self, suffixes):
                self.possible_suffixes = self.possible_suffixes.union(suffixes)
                return self

            def build(self):
                regex = ""
                if len(self.possible_prefixes) > 0:
                    regex += "(" + "|".join(self.possible_prefixes) + ")"
                regex += self.value
                if len(self.possible_suffixes) > 0:
                    regex += "(" + "|".join(self.possible_suffixes) + ")"
                return regex

        @staticmethod
        def remove_start_and_end_tokens(regex):
            if regex.startswith("^"):
                regex = regex[1:]
            if regex.endswith("$"):
                regex = regex[:-1]
            return regex

    class Variable:

        @staticmethod
        def is_valid(value, verbose=True):
            fields = value.split("_")
            if len(fields) != 4:
                if verbose:
                    warnings.warn(f"Variable must be composed of 4 fields, {len(fields)} found")
                return False

            entity, quality, method, unit = fields

            if not NamingConvention.Field.Entity.is_valid(entity):
                if verbose:
                    warnings.warn(f"Entity field does not match any valid value")
                return False

            if not NamingConvention.Field.Quality.is_valid(quality):
                if verbose:
                    warnings.warn(f"Quality field does not match any valid value")
                return False

            if not NamingConvention.Field.Method.is_valid(method):
                if verbose:
                    warnings.warn(f"Method field does not match any valid value")
                return False

            if not any([_quality in quality for _quality in NamingConvention.Field.Method.get_qualities_for(method)]):
                if verbose:
                    warnings.warn(f"The Method and Quality fields do not seem compatible")
                return False

            if not NamingConvention.Field.Unit.is_valid(unit):
                if verbose:
                    warnings.warn(f"Unit field does not match any valid value")
                return False

            return True

    class Module:

        @staticmethod
        def is_valid(value, verbose=False):
            return (NamingConvention.Module.TraitExtractionModule.is_valid(value, verbose=verbose) or
                    NamingConvention.Module.PreProcessingModule.is_valid(value, verbose=verbose))

        class TraitExtractionModule:

            @staticmethod
            def is_valid(value, verbose=True):
                fields = value.split("_")
                if len(fields) != 5:
                    if verbose:
                        warnings.warn(f"TraitModule must be composed of 5 fields, {len(fields)} found")
                    return False

                vector, sensor, trait, method, species = fields

                vector_regex = NamingConvention.Field.Vector.get_regex()
                vector_regex = "^(" + NamingConvention.Utils.remove_start_and_end_tokens(vector_regex) + ")+$"
                if re.compile(vector_regex).match(vector) is None:
                    if verbose:
                        warnings.warn(f"Vector field does not match any valid value")
                    return False

                # if not NamingConvention.Field.Vector.is_valid(vector):
                #     if verbose:
                #         warnings.warn(f"Vector field does not match any valid value")
                #     return False

                if not NamingConvention.Field.Sensor.is_valid(sensor):
                    if verbose:
                        warnings.warn(f"Sensor field does not match any valid value")
                    return False

                trait_regex = NamingConvention.Field.Trait.get_regex(skip_quality_suffixes=True)
                trait_regex = "^(" + NamingConvention.Utils.remove_start_and_end_tokens(trait_regex) + ")+$"
                if re.compile(trait_regex).match(trait) is None:
                    if verbose:
                        warnings.warn(f"Trait field does not match any valid value")
                    return False

                # if not NamingConvention.Field.Trait.is_valid(trait, skip_quality_suffixes=True):
                #     if verbose:
                #         warnings.warn(f"Trait field does not match any valid value")
                #     return False

                if not NamingConvention.Field.Method.is_valid(method):
                    if verbose:
                        warnings.warn(f"Method field does not match any valid value")
                    return False

                if not any(
                        # [_quality in trait for _quality in NamingConvention.Field.Method.get_qualities_for(method)]):
                        [trait.endswith(_quality) for _quality in NamingConvention.Field.Method.get_qualities_for(method)]):
                    if verbose:
                        warnings.warn(f"The Method and Quality fields do not seem compatible")
                    return False

                if species != "Mix":  # If it's just "Mix", OK (we skip)  # TODO : Vraiment valide ?
                    if "Mix" in species:
                        species = species.replace("Mix", "")  # We delete “Mix” to validate the other (pure) values

                    if not NamingConvention.Field.Species.is_valid(species):
                        if verbose:
                            warnings.warn(f"Species field does not match any valid value")
                        return False

                return True

        class PreProcessingModule:

            @staticmethod
            def is_valid(value, verbose=True):
                fields = value.split("_")
                if len(fields) != 5:
                    if verbose:
                        warnings.warn(f"PreProcessingModule must be composed of 5 fields, {len(fields)} found")
                    return False

                vector, sensor, _object, action, species = fields

                if not NamingConvention.Field.Vector.is_valid(vector):
                    if verbose:
                        warnings.warn(f"Vector field does not match any valid value")
                    return False

                if not NamingConvention.Field.Sensor.is_valid(sensor):
                    if verbose:
                        warnings.warn(f"Sensor field does not match any valid value")
                    return False

                if not NamingConvention.Field.Object.is_valid(_object):
                    if verbose:
                        warnings.warn(f"Object field does not match any valid value")
                    return False

                if not NamingConvention.Field.Action.is_valid(action):
                    if verbose:
                        warnings.warn(f"Method field does not match any valid value")
                    return False

                if species != "All" and not NamingConvention.Field.Species.is_valid(species):
                    if verbose:
                        warnings.warn(f"Species field does not match any valid value. "
                                      "In the case of a PreProcessingModule, "
                                      "the Species field can take the special value 'All'.")
                    return False

                return True

    class Field:

        class Action:
            _actions = set()

            @staticmethod
            def add_action(value):
                if isinstance(value, NamingConvention.Utils.ValueBuilder):
                    value = value.build()
                if not isinstance(value, str):
                    raise TypeError("The 'value' argument must be a string")
                NamingConvention.Field.Action._actions.add(value)
                return NamingConvention.Field.Action

            @staticmethod
            def add_actions(actions):
                if not isinstance(actions, list) and not isinstance(actions, set):
                    raise TypeError("The 'actions' argument must be a list or a set")
                for action in actions:
                    NamingConvention.Field.Action.add_action(action)
                return NamingConvention.Field.Action

            @staticmethod
            def get_regex():
                regex = "(" + "|".join(NamingConvention.Field.Action._actions) + ")"

                return "^" + regex + "$"

            @staticmethod
            def is_valid(value):
                return re.compile(NamingConvention.Field.Action.get_regex()).match(value) is not None

        class Entity:
            _entities = set()
            _targeted_part_suffixes = {""}  # Pre-instantiate optional suffix

            @staticmethod
            def add_entity(value):
                if isinstance(value, NamingConvention.Utils.ValueBuilder):
                    value = value.build()
                if not isinstance(value, str):
                    raise TypeError("The 'value' argument must be a string")
                NamingConvention.Field.Entity._entities.add(value)
                return NamingConvention.Field.Entity

            @staticmethod
            def add_entities(entities):
                if not isinstance(entities, list) and not isinstance(entities, set):
                    raise TypeError("The 'entities' argument must be a list or a set")
                for entity in entities:
                    NamingConvention.Field.Entity.add_entity(entity)
                return NamingConvention.Field.Entity

            @staticmethod
            def add_targeted_part_suffix(value):
                if isinstance(value, NamingConvention.Utils.ValueBuilder):
                    value = value.build()
                if not isinstance(value, str):
                    raise TypeError("The 'value' argument must be a string")
                NamingConvention.Field.Entity._targeted_part_suffixes.add(value)
                return NamingConvention.Field.Entity

            @staticmethod
            def add_targeted_part_suffixes(suffixes):
                if not isinstance(suffixes, list) and not isinstance(suffixes, set):
                    raise TypeError("The 'suffixes' argument must be a list or a set")
                for suffix in suffixes:
                    NamingConvention.Field.Entity.add_targeted_part_suffix(suffix)
                return NamingConvention.Field.Entity

            @staticmethod
            def get_regex():
                regex = "(" + "|".join(NamingConvention.Field.Entity._entities) + ")"

                regex += (
                        "(" +
                        NamingConvention.Utils.remove_start_and_end_tokens(NamingConvention.Field.Species.get_regex()) +
                        ")*"
                )

                if len(NamingConvention.Field.Entity._targeted_part_suffixes) > 0:
                    regex += "(" + "|".join(NamingConvention.Field.Entity._targeted_part_suffixes) + ")"

                return "^" + regex + "$"

            @staticmethod
            def is_valid(value):
                return re.compile(NamingConvention.Field.Entity.get_regex()).match(value) is not None

        class Method:
            _methods = dict()

            @staticmethod
            def add_method(method, related_quality, skip_validation=False):
                if not isinstance(method, str):
                    raise TypeError("The 'method' argument must be a string")
                if isinstance(related_quality, list) or isinstance(related_quality, set):
                    for quality in related_quality:
                        NamingConvention.Field.Method.add_method(method, quality, skip_validation=skip_validation)
                    return NamingConvention.Field.Method
                if not isinstance(related_quality, str):
                    raise TypeError("The 'related_quality' argument must be a string or a list of strings")
                if (not skip_validation
                        and not NamingConvention.Field.Quality.is_valid(related_quality, skip_suffixes=True)):
                    raise ValueError(f"The 'related_quality' ({related_quality}) argument must correspond to a valid "
                                     "Quality field. Be sure to save the relevant Quality before adding this Method. "
                                     "Not recommended: you can also use the 'skip_validation=True' argument.")

                if method not in NamingConvention.Field.Method._methods:
                    NamingConvention.Field.Method._methods[method] = set()
                NamingConvention.Field.Method._methods[method].add(related_quality)
                return NamingConvention.Field.Method

            @staticmethod
            def add_methods(methods, skip_validation=False):
                if not isinstance(methods, dict):
                    raise TypeError("The 'methods' argument must be a dictionary "
                                    "with a method as key and a corresponding (list of) quality as value.")
                for method, quality in methods.items():
                    NamingConvention.Field.Method.add_method(method, quality, skip_validation=skip_validation)
                return NamingConvention.Field.Method

            @staticmethod
            def get_qualities_for(method):
                return NamingConvention.Field.Method._methods.get(method, set())

            @staticmethod
            def get_methods_for(quality):
                return {m for m, q in NamingConvention.Field.Method._methods.items() if quality in q}

            @staticmethod
            def get_regex():
                regex = "(" + "|".join(NamingConvention.Field.Method._methods.keys()) + ")"

                return "^" + regex + "$"

            @staticmethod
            def is_valid(value):
                return re.compile(NamingConvention.Field.Method.get_regex()).match(value) is not None

        class Object:
            _objects = set()

            @staticmethod
            def add_object(value):
                if isinstance(value, NamingConvention.Utils.ValueBuilder):
                    value = value.build()
                if not isinstance(value, str):
                    raise TypeError("The 'value' argument must be a string")
                NamingConvention.Field.Object._objects.add(value)
                return NamingConvention.Field.Object

            @staticmethod
            def add_objects(objects):
                if not isinstance(objects, list) and not isinstance(objects, set):
                    raise TypeError("The 'objects' argument must be a list or a set")
                for _object in objects:
                    NamingConvention.Field.Object.add_object(_object)
                return NamingConvention.Field.Object

            @staticmethod
            def get_regex():
                regex = "(" + "|".join(NamingConvention.Field.Object._objects) + ")"

                return "^" + regex + "$"

            @staticmethod
            def is_valid(value):
                return re.compile(NamingConvention.Field.Object.get_regex()).match(value) is not None

        class Quality:
            _qualities = set()
            _details_suffixes = {""}  # Pre-instantiate optional suffix
            _statistic_suffixes = set()  # Pre-instantiate optional suffix

            @staticmethod
            def add_quality(value):
                if isinstance(value, NamingConvention.Utils.ValueBuilder):
                    value = value.build()
                if not isinstance(value, str):
                    raise TypeError("The 'value' argument must be a string")
                NamingConvention.Field.Quality._qualities.add(value)
                return NamingConvention.Field.Quality

            @staticmethod
            def add_qualities(qualities):
                if not isinstance(qualities, list) and not isinstance(qualities, set):
                    raise TypeError("The 'qualities' argument must be a list or a set")
                for quality in qualities:
                    NamingConvention.Field.Quality.add_quality(quality)
                return NamingConvention.Field.Quality

            @staticmethod
            def add_details_suffix(value):
                if isinstance(value, NamingConvention.Utils.ValueBuilder):
                    value = value.build()
                if not isinstance(value, str):
                    raise TypeError("The 'value' argument must be a string")
                NamingConvention.Field.Quality._details_suffixes.add(value)
                return NamingConvention.Field.Quality

            @staticmethod
            def add_details_suffixes(suffixes):
                if not isinstance(suffixes, list) and not isinstance(suffixes, set):
                    raise TypeError("The 'suffixes' argument must be a list or a set")
                for suffix in suffixes:
                    NamingConvention.Field.Quality.add_details_suffix(suffix)
                return NamingConvention.Field.Quality

            @staticmethod
            def add_statistic_suffix(value):
                if isinstance(value, NamingConvention.Utils.ValueBuilder):
                    value = value.build()
                if not isinstance(value, str):
                    raise TypeError("The 'value' argument must be a string")
                NamingConvention.Field.Quality._statistic_suffixes.add(value)
                return NamingConvention.Field.Quality

            @staticmethod
            def add_statistic_suffixes(suffixes):
                if not isinstance(suffixes, list) and not isinstance(suffixes, set):
                    raise TypeError("The 'suffixes' argument must be a list or a set")
                for suffix in suffixes:
                    NamingConvention.Field.Quality.add_statistic_suffix(suffix)
                return NamingConvention.Field.Quality

            @staticmethod
            def get_regex(skip_suffixes=False):
                regex = "(" + "|".join(NamingConvention.Field.Quality._qualities) + ")"

                if not skip_suffixes and len(NamingConvention.Field.Quality._details_suffixes) > 0:
                    regex += "(" + "|".join(NamingConvention.Field.Quality._details_suffixes) + ")*"

                if not skip_suffixes and len(NamingConvention.Field.Quality._statistic_suffixes) > 0:
                    regex += "(" + "|".join(NamingConvention.Field.Quality._statistic_suffixes) + ")+"

                return "^" + regex + "$"

            @staticmethod
            def is_valid(value, skip_suffixes=False):
                return re.compile(NamingConvention.Field.Quality.get_regex(skip_suffixes)).match(value) is not None

        class Sensor:
            _sensors = set()

            @staticmethod
            def add_sensor(value):
                if isinstance(value, NamingConvention.Utils.ValueBuilder):
                    value = value.build()
                if not isinstance(value, str):
                    raise TypeError("The 'value' argument must be a string")
                NamingConvention.Field.Sensor._sensors.add(value)
                return NamingConvention.Field.Sensor

            @staticmethod
            def add_sensors(sensors):
                if not isinstance(sensors, list) and not isinstance(sensors, set):
                    raise TypeError("The 'sensors' argument must be a list or a set")
                for sensor in sensors:
                    NamingConvention.Field.Sensor.add_sensor(sensor)
                return NamingConvention.Field.Sensor

            @staticmethod
            def get_regex():
                regex = "(" + "|".join(NamingConvention.Field.Sensor._sensors) + ")+"

                return "^" + regex + "$"

            @staticmethod
            def is_valid(value):
                return re.compile(NamingConvention.Field.Sensor.get_regex()).match(value) is not None

        class Species:
            _species = set()

            @staticmethod
            def add_species(species):
                if isinstance(species, list) or isinstance(species, set):
                    for a_species in species:
                        NamingConvention.Field.Species.add_species(a_species)
                    return NamingConvention.Field.Species
                if isinstance(species, NamingConvention.Utils.ValueBuilder):
                    species = species.build()
                if not isinstance(species, str):
                    raise TypeError("The 'species' argument must be a (list/set of) string")
                NamingConvention.Field.Species._species.add(species)
                return NamingConvention.Field.Species

            @staticmethod
            def get_regex():
                regex = "(" + "|".join(NamingConvention.Field.Species._species) + ")+"

                return "^" + regex + "$"

            @staticmethod
            def is_valid(value):
                return re.compile(NamingConvention.Field.Species.get_regex()).match(value) is not None

        class Trait:

            @staticmethod
            def get_regex(skip_quality_suffixes=False):
                entity_regex = NamingConvention.Field.Entity.get_regex()
                quality_regex = NamingConvention.Field.Quality.get_regex(skip_suffixes=skip_quality_suffixes)

                entity_regex = NamingConvention.Utils.remove_start_and_end_tokens(entity_regex)
                quality_regex = NamingConvention.Utils.remove_start_and_end_tokens(quality_regex)

                return "^" + entity_regex + quality_regex + "$"

            @staticmethod
            def is_valid(value, skip_quality_suffixes=False):
                regex = re.compile(NamingConvention.Field.Trait.get_regex(skip_quality_suffixes=skip_quality_suffixes))
                return regex.match(value) is not None

        class Unit:
            _units = set()

            @staticmethod
            def add_unit(value):
                if isinstance(value, NamingConvention.Utils.ValueBuilder):
                    value = value.build()
                if not isinstance(value, str):
                    raise TypeError("The 'value' argument must be a string")
                NamingConvention.Field.Unit._units.add(value)
                return NamingConvention.Field.Unit

            @staticmethod
            def add_units(units):
                if not isinstance(units, list) and not isinstance(units, set):
                    raise TypeError("The 'units' argument must be a list or a set")
                for unit in units:
                    NamingConvention.Field.Unit.add_unit(unit)
                return NamingConvention.Field.Unit

            @staticmethod
            def get_regex():
                regex = ("(uless|p{0,1}(" + "|".join(NamingConvention.Field.Unit._units) + ")(p(" +
                         "|".join(NamingConvention.Field.Unit._units) + ")|" +
                         NamingConvention.Utils.INTEGER_PATTERN + ")*)")

                return "^" + regex + "$"

            @staticmethod
            def is_valid(value):
                return re.compile(NamingConvention.Field.Unit.get_regex()).match(value) is not None

        class Vector:
            _vectors = set()

            @staticmethod
            def add_vector(value):
                if isinstance(value, NamingConvention.Utils.ValueBuilder):
                    value = value.build()
                if not isinstance(value, str):
                    raise TypeError("The 'value' argument must be a string")
                NamingConvention.Field.Vector._vectors.add(value)
                return NamingConvention.Field.Vector

            @staticmethod
            def add_vectors(vectors):
                if not isinstance(vectors, list) and not isinstance(vectors, set):
                    raise TypeError("The 'vectors' argument must be a list or a set")
                for vector in vectors:
                    NamingConvention.Field.Vector.add_vector(vector)
                return NamingConvention.Field.Vector

            @staticmethod
            def get_regex():
                regex = "(" + "|".join(NamingConvention.Field.Vector._vectors) + ")"

                return "^" + regex + "$"

            @staticmethod
            def is_valid(value):
                return re.compile(NamingConvention.Field.Vector.get_regex()).match(value) is not None

    class Version:

        @staticmethod
        def get_regex():
            return "^([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+)?$"

        @staticmethod
        def is_valid(value):
            return re.compile(NamingConvention.Version.get_regex()).match(value) is not None


NamingConvention.Field.Action.add_actions([
    "BandRegistration",
    "Crop",
    "Extract",
    "Filter",
    "Fusion",
    "Concatenate"
])

NamingConvention.Field.Entity.add_entities([
    "Canopy",
    "Background",
    "Ear",
    "Grain",
    NamingConvention.Utils.ValueBuilder("Inflorescence").add_possible_suffixes(["", "Male", "Female"]),
    "Leaf",
    "Plant",
    "Residues",
    "Root",
    "Row",
    "Soil",
    "Stem"
]).add_targeted_part_suffixes([
    "Contaminated",
    "DiseaseSpot",
    "Green",
    "Senescent",
    "Voxel",
    "Yellow"
])

NamingConvention.Field.Object.add_objects([
    "3DPC",
    "CSV",
    "HDF5",
    "Image",
    "JSON",
    "Mission",
    "Voxel"
])

NamingConvention.Field.Quality.add_qualities([
    "Area",
    "AreaDensity",
    "AreaIndex",
    "ChlorophyllContent",
    "CoverFraction",
    "Density",
    "Diameter",
    "FAPAR",
    "FIPAR",
    "Fraction",
    "GapFraction",
    "Height",
    "InclinationAngle",
    "Length",
    "Lodging",
    "Mass",
    "NitrogenContent",
    "Number",
    "Radiance",
    "Reflectance",
    "SpectralIndex",
    "Temperature",
    "Transmittance",
    "Volume",
    "WaterContent",
    "Width"
]).add_details_suffixes([
    NamingConvention.Utils.INTEGER_PATTERN + "nm",
    NamingConvention.Utils.INTEGER_PATTERN + "deg"
]).add_statistic_suffixes([
    "Mean",
    "Med",
    "Std",
    "Min",
    "Max",
    "Flag"
])

NamingConvention.Field.Method.add_methods({
    "BandCombination": ["SpectralIndex"],
    "DirectMeasurement": ["AreaIndex", "ChlorophyllContent", "Density", "FAPAR", "FIPAR", "Height", "InclinationAngle",
                          "NitrogenContent", "Number", "Temperature", "WaterContent"],
    "EmpiricalModel": ["AreaIndex", "ChlorophyllContent", "CoverFraction", "Density", "FAPAR", "FIPAR",
                       "InclinationAngle", "Lodging", "NitrogenContent", "Number", "WaterContent"],
    "Extraction": ["Reflectance"],
    "GeometricalModel": ["FAPAR", "FIPAR", "InclinationAngle"],
    "ImageProcessing": ["Area", "CoverFraction", "Density", "FAPAR", "FIPAR", "Fraction", "Number"],
    "Photogrammetry": ["Height"],
    "PhysicalModel": ["AreaIndex", "ChlorophyllContent", "CoverFraction", "FAPAR", "FIPAR", "InclinationAngle",
                      "NitrogenContent", "WaterContent"],
    "Radiothermometer": ["Temperature"],
    "ThermalImaging": ["Temperature"],
    "VisualScore": ["CoverFraction", "Density", "InclinationAngle", "Lodging"]
})  # Note : We declare the methods after the qualities in order to be able to pass validation

NamingConvention.Field.Sensor.add_sensors([
    "Any",
    "RGB",
    "LiD",
    "MSpec",
    "HSpec"
])

NamingConvention.Field.Species.add_species([
    "AC",
    "All",
    "Bar",
    "Can",
    "Fab",
    "Mai",
    "Mix",
    "Orc",
    "Pot",
    "Sor",
    "Soy",
    "Sug",
    "Sun",
    "Tri",
    "Vin",
    "Wee",
    "Whe"
])

NamingConvention.Field.Unit.add_units([
    "kg",
    "g",
    "mg",
    "ug",
    "m",
    "cm",
    "mm",
    "um",
    "nm",
    "deg",
    "degC",
    "degK",
    "percent"
])

NamingConvention.Field.Vector.add_vectors([
    "Pheno",
    "Philo",
    "PhenoVigne",
    "UAV",
    "Lit"
])

# NamingConvention.Version.add_suffixes([
#     "lit",
#     "pheno",
#     "philo",
#     "uav"
# ])
