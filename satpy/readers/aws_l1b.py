# Copyright (c) 2023 Pytroll Developers

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Reader for the Arctic Weather Satellite (AWS) Sounder level-1b data.

Test data provided by ESA August 23, 2023.
"""

import logging

# import dask.array as da
# import numpy as np
import xarray as xr

from .netcdf_utils import NetCDF4FileHandler

# from datetime import datetime

# from netCDF4 import default_fillvals


logger = logging.getLogger(__name__)

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

# DUMMY_STARTTIME = datetime(2023, 7, 7, 12, 0)
# DUMMY_ENDTIME = datetime(2023, 7, 7, 12, 10)
# # dict containing all available auxiliary data parameters to be read using the index map. Keys are the
# # parameter name and values are the paths to the variable inside the netcdf
#
# AUX_DATA = {
#     'scantime_utc': 'data/navigation/aws_scantime_utc',
#     'solar_azimuth_angle': 'data/navigation/aws_solar_azimuth_angle',
#     'solar_zenith_angle': 'data/navigation/aws_solar_zenith_angle',
#     'satellite_azimuth_angle': 'data/navigation/aws_satellite_azimuth_angle',
#     'satellite_zenith_angle': 'data/navigation/aws_satellite_zenith_angle',
#     'surface_type': 'data/navigation/aws_surface_type',
#     'terrain_elevation': 'data/navigation/aws_terrain_elevation',
#     'aws_lat': 'data/navigation/aws_lat',
#     'aws_lon': 'data/navigation/aws_lon',
#     'latitude': 'data/navigation/aws_lat',
#     'longitude': 'data/navigation/aws_lon',
# }
#
AWS_CHANNEL_NAMES_TO_NUMBER = {'1': 1, '2': 2, '3': 3, '4': 4,
                               '5': 5, '6': 6, '7': 7, '8': 8,
                               '9': 9, '10': 10, '11': 11, '12': 12,
                               '13': 13, '14': 14, '15': 15, '16': 16,
                               '17': 17, '18': 18, '19': 19}

AWS_CHANNEL_NAMES = list(AWS_CHANNEL_NAMES_TO_NUMBER.keys())
# AWS_CHANNELS = set(AWS_CHANNEL_NAMES)
#
#
# def get_channel_index_from_name(chname):
#     """Get the AWS channel index from the channel name."""
#     chindex = AWS_CHANNEL_NAMES_TO_NUMBER.get(chname, 0) - 1
#     if 0 <= chindex < 19:
#         return chindex
#     raise AttributeError(f"Channel name {chname!r} not supported")
#
#
# def _get_aux_data_name_from_dsname(dsname):
#     aux_data_name = [key for key in AUX_DATA.keys() if key in dsname]
#     if len(aux_data_name) > 0:
#         return aux_data_name[0]
#
#


class AWSL1BFile(NetCDF4FileHandler):
    """Class implementing the AWS L1b Filehandler.

    This class implements the ESA Arctic Weather Satellite (AWS) Level-1b
    NetCDF reader. It is designed to be used through the :class:`~satpy.Scene`
    class using the :mod:`~satpy.Scene.load` method with the reader
    ``"aws_l1b_nc"``.

    """

    def __init__(self, filename, filename_info, filetype_info, auto_maskandscale=True):
        """Initialize the handler."""
        super().__init__(filename, filename_info, filetype_info)
        self.filename_info = filename_info

    @property
    def start_time(self):
        """Get the start time."""
        return self.filename_info["start_time"]

    @property
    def end_time(self):
        """Get the end time."""
        return self.filename_info["end_time"]

    @property
    def sensor(self):
        """Get the sensor name."""
        return self['/attr/instrument']

    @property
    def platform_name(self):
        """Get the platform name."""
        return self.filename_info["platform_name"]

    def get_dataset(self, dataset_id, dataset_info):
        """Get the data."""
        if dataset_id["name"] in AWS_CHANNEL_NAMES:
            channel_data = self[dataset_info["file_key"]]
            channel_data.coords["n_channels"] = AWS_CHANNEL_NAMES
            data_array = channel_data.sel(n_channels=dataset_id["name"])
        elif (dataset_id["name"].startswith("lon") or dataset_id["name"].startswith("lat")
              or dataset_id["name"].startswith("solar_azimuth")
              or dataset_id["name"].startswith("solar_zenith")
              or dataset_id["name"].startswith("satellite_azimuth")
              or dataset_id["name"].startswith("satellite_zenith")):
            channel_data = self[dataset_info["file_key"]]
            channel_data.coords["n_geo_groups"] = [0, 1, 2, 3]
            n_horn = dataset_info["n_horns"]
            data_array = channel_data.sel(n_geo_groups=n_horn)
        else:
            raise NotImplementedError

        if "scale_factor" in data_array.attrs and "add_offset" in data_array.attrs:
            with xr.set_options(keep_attrs=True):
                data_array = data_array * data_array.attrs["scale_factor"] + data_array.attrs["add_offset"]
            data_array.attrs.pop("scale_factor")
            data_array.attrs.pop("add_offset")
        # if "missing_value" in data_array.attrs:
        #     with xr.set_options(keep_attrs=True):
        #         data_array = data_array.where(data_array != data_array.attrs["missing_value"])
        return data_array


# class AWSL1BFile(NetCDF4FileHandler):
#     """Class implementing the AWS L1b Filehandler.
#
#     This class implements the ESA Arctic Weather Satellite (AWS) Level-1b
#     NetCDF reader. It is designed to be used through the :class:`~satpy.Scene`
#     class using the :mod:`~satpy.Scene.load` method with the reader
#     ``"aws_l1b_nc"``.
#
#     """
#
#     _platform_name_translate = {
#         "": "AWS",
#     }
#
#     def __init__(self, filename, filename_info, filetype_info):
#         """Initialize file handler."""
#         xarray_kwargs = {'decode_times': False}
#         super().__init__(filename, filename_info,
#                          filetype_info,
#                          xarray_kwargs=xarray_kwargs,
#                          cache_var_size=10000,
#                          cache_handle=True)
#         logger.debug('Reading: {}'.format(self.filename))
#         logger.debug('Start: {}'.format(self.start_time))
#         logger.debug('End: {}'.format(self.end_time))
##
#         self._channel_names = AWS_CHANNEL_NAMES

#
#     @property
#     def sub_satellite_longitude_start(self):
#         """Get the longitude of sub-satellite point at start of the product."""
#         return self['status/satellite/subsat_longitude_start'].data.item()
#
#     @property
#     def sub_satellite_latitude_start(self):
#         """Get the latitude of sub-satellite point at start of the product."""
#         return self['status/satellite/subsat_latitude_start'].data.item()
#
#     @property
#     def sub_satellite_longitude_end(self):
#         """Get the longitude of sub-satellite point at end of the product."""
#         return self['status/satellite/subsat_longitude_end'].data.item()
#
#     @property
#     def sub_satellite_latitude_end(self):
#         """Get the latitude of sub-satellite point at end of the product."""
#         return self['status/satellite/subsat_latitude_end'].data.item()
#
#     def get_dataset(self, dataset_id, dataset_info):
#         """Get dataset using file_key in dataset_info."""
#         logger.debug('Reading {} from {}'.format(dataset_id['name'], self.filename))
#
#         var_key = dataset_info['file_key']
#         # if _get_aux_data_name_from_dsname(dataset_id['name']) is not None:
#         if _get_aux_data_name_from_dsname(var_key) is not None:
#             nhorn = dataset_info['n_horns']
#             standard_name = dataset_info['standard_name']
#
#             # variable = self._get_dataset_aux_data(var_key, nhorn)  # (dataset_id['name'])
#             variable = self._get_dataset_aux_data(standard_name, nhorn)  # (dataset_id['name'])
#         elif dataset_id['name'] in AWS_CHANNELS:
#             logger.debug(f'Reading in file to get dataset with key {var_key}.')
#             variable = self._get_dataset_channel(dataset_id, dataset_info)
#         else:
#             logger.warning(f'Could not find key {var_key} in NetCDF file, no valid Dataset created')  # noqa: E501
#             return None
#
#         variable = self._manage_attributes(variable, dataset_info)
#         variable = self._drop_coords(variable)
#         variable = self._standardize_dims(variable)
#
#         if dataset_info['standard_name'] in ['longitude', 'latitude']:
#             data = variable.data[:, :]
#             if dataset_info['standard_name'] in ['longitude']:
#                 data = self._scale_lons(data)
#             lon_or_lat = xr.DataArray(
#                 data,
#                 attrs=variable.attrs,
#                 dims=(variable.dims[0], variable.dims[1])
#             )
#             variable = lon_or_lat
#
#         return variable
#
#     @staticmethod
#     def _scale_lons(lons):
#         return xr.where(lons > 180, lons - 360, lons)
#
#     @staticmethod
#     def _standardize_dims(variable):
#         """Standardize dims to y, x."""
#         if 'n_scans' in variable.dims:
#             variable = variable.rename({'n_fovs': 'x', 'n_scans': 'y'})
#         if variable.dims[0] == 'x':
#             variable = variable.transpose('y', 'x')
#         return variable
#
#     @staticmethod
#     def _drop_coords(variable):
#         """Drop coords that are not in dims."""
#         for coord in variable.coords:
#             if coord not in variable.dims:
#                 variable = variable.drop_vars(coord)
#         return variable
#
#     def _manage_attributes(self, variable, dataset_info):
#         """Manage attributes of the dataset."""
#         variable.attrs.setdefault('units', None)
#         variable.attrs.update(dataset_info)
#         variable.attrs.update(self._get_global_attributes())
#         return variable
#
#     def _get_dataset_channel(self, key, dataset_info):
#         """Load dataset corresponding to channel measurement.
#
#         Load a dataset when the key refers to a measurand, whether uncalibrated
#         (counts) or calibrated in terms of brightness temperature or radiance.
#
#         """
#         # Get the dataset
#         # Get metadata for given dataset
#         grp_pth = dataset_info['file_key']
#         channel_index = get_channel_index_from_name(key['name'])
#
#         # data = self[grp_pth][:, :, channel_index]
#         data = self[grp_pth][channel_index, :, :]
#         data = data.transpose()
#         # This transposition should not be needed were the format following the EPS-SG format spec!!
#         attrs = data.attrs.copy()
#
#         fv = attrs.pop(
#             "FillValue",
#             default_fillvals.get(data.dtype.str[1:], np.nan))
#         vr = attrs.get("valid_range", [-np.inf, np.inf])
#
#         if key['calibration'] == "counts":
#             attrs["_FillValue"] = fv
#             nfv = fv
#         else:
#             nfv = np.nan
#         data = data.where(data >= vr[0], nfv)
#         data = data.where(data <= vr[1], nfv)
#
#         # Manage the attributes of the dataset
#         data.attrs.setdefault('units', None)
#         data.attrs.update(dataset_info)
#
#         dataset_attrs = getattr(data, 'attrs', {})
#         dataset_attrs.update(dataset_info)
#         dataset_attrs.update({
#             "platform_name": self.platform_name,
#             "sensor": self.sensor,
#             "orbital_parameters": {'sub_satellite_latitude_start': self.sub_satellite_latitude_start,
#                                    'sub_satellite_longitude_start': self.sub_satellite_longitude_start,
#                                    'sub_satellite_latitude_end': self.sub_satellite_latitude_end,
#                                    'sub_satellite_longitude_end': self.sub_satellite_longitude_end},
#         })
#
#         try:
#             dataset_attrs.update(key.to_dict())
#         except AttributeError:
#             dataset_attrs.update(key)
#
#         data.attrs.update(dataset_attrs)
#         return data
#
#     def _get_dataset_aux_data(self, dsname, nhorn):
#         """Get the auxiliary data arrays using the index map."""
#         # Geolocation and navigation data:
#         if dsname in ['latitude', 'longitude',
#                       'solar_azimuth_angle', 'solar_zenith_angle',
#                       'satellite_azimuth_angle', 'satellite_zenith_angle',
#                       'surface_type', 'terrain_elevation']:
#             var_key = AUX_DATA.get(dsname)
#         else:
#             raise NotImplementedError(f"Dataset {dsname!r} not supported!")
#
#         try:
#             variable = self[var_key][nhorn, :, :]
#         except KeyError:
#             logger.exception("Could not find key %s in NetCDF file, no valid Dataset created", var_key)
#             raise
#
#         # Scale the data:
#         if 'scale_factor' in variable.attrs and 'add_offset' in variable.attrs:
#             missing_value = variable.attrs['missing_value']
#             variable.data = da.where(variable.data == missing_value, np.nan,
#                                      variable.data * variable.attrs['scale_factor'] + variable.attrs['add_offset'])
#
#         return variable
#
#     def _get_global_attributes(self):
#         """Create a dictionary of global attributes."""
#         return {
#             'filename': self.filename,
#             'start_time': self.start_time,
#             'end_time': self.end_time,
#             'spacecraft_name': self.platform_name,
#             'sensor': self.sensor,
#             'filename_start_time': self.filename_info['start_time'],
#             'filename_end_time': self.filename_info['end_time'],
#             'platform_name': self.platform_name,
#             'quality_group': self._get_quality_attributes(),
#         }
#
#     def _get_quality_attributes(self):
#         """Get quality attributes."""
#         quality_group = self['quality']
#         quality_dict = {}
#         for key in quality_group:
#             # Add the values (as Numpy array) of each variable in the group
#             # where possible
#             try:
#                 quality_dict[key] = quality_group[key].values
#             except ValueError:
#                 quality_dict[key] = None
#
#         quality_dict.update(quality_group.attrs)
#         return quality_dict
