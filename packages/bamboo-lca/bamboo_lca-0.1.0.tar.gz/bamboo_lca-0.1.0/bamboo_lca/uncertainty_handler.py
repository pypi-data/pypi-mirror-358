import bw_processing as bwp
import pandas as pd
import numpy as np
from .metadata_manager import *


class UncertaintyHandler:
    def __init__(self):
        self.metadata = metadata_manager.get_metadata()

    def calc_specific_uncertainty(self, data, uncertainty):
        loc = np.log(data)
        scale = np.log(uncertainty)

        return loc, scale

    def generate_uncertainty_tuple(self, data, type, gsd, uncertainty_negative):
        """
        Generate the uncertainty tuple for one value.

        Parameters:
            * data: The input or output value of the one exchange in the system.
            * type: The type of uncertainty, such as 2.
            * gsd: Geometric Standard Deviation, used to calculate sigma of lognormal distribution.
            * uncertainty_negative: uncertainty negative
        """
        data = abs(data)
        if type in [0, 1]:
            uncertainty_tuple = (type, data, np.NaN, np.NaN, np.NaN, np.NaN, uncertainty_negative)
        elif type == 2:  # no need to consider data == 0, because sparse matrix only save non-zero values.
            if gsd == 0:
                uncertainty_tuple = (0, data, np.NaN, np.NaN, np.NaN, np.NaN, uncertainty_negative)
            else:
                uncertainty_tuple = (type, np.log(data), np.log(gsd), np.NaN, np.NaN, np.NaN, uncertainty_negative)
        elif type == 3: # normal
            uncertainty_tuple = (type, data, np.NaN, np.NaN, np.NaN, np.NaN, uncertainty_negative)
        elif type == 4: # uniform
            uncertainty_tuple = (type, np.NaN, np.NaN, np.NaN, (data - data * gsd), (data + data * gsd), uncertainty_negative)

        return uncertainty_tuple
    
    def get_uncertainty_value(self, strategy, act_index, row):
        """
        Get uncertainty values by strategy from metadata.

        Parameters:
            * strategy: The strategy of adding uncertainty, "itemwise" or "columnwise".
            * act_index: The index of the activity.
            * row: The row number of the corresponding activity.
        """
        if self.metadata is None:
            print("Please write your uncertainty information into metadata first.")
        
        if len(self.metadata) < row:  # If biosphere, indices need to be subtracted from technosphere indices.
            row = row - len(self.metadata) + 1

        if strategy == "itemwise":
            specific = self.metadata[act_index].get("Exchange uncertainty amount", 0)
            if isinstance(specific, list):
                uncertainty_value = specific[row]
            else:  # because some activity don't have uncertainty at all, in this case is background system
                uncertainty_value = specific
        elif strategy == "columnwise":
            uncertainty_value = self.metadata[act_index].get("Exchange uncertainty amount", 0)
            uncertainty_value = 0 if np.isnan(uncertainty_value) else uncertainty_value

        return uncertainty_value
    
    def get_uncertainty_negative(self, strategy, act_index, row):
        """
        Get uncertainty negative (TRUE or FALSE) by strategy from metadata.

        Parameters:
            * strategy: The strategy of adding uncertainty, "itemwise" or "columnwise".
            * act_index: The index of the activity.
            * row: The row number of the corresponding activity.
        """
        if self.metadata is None:
            print("Please write your uncertainty information into metadata first.")
        
        if len(self.metadata) < row:  # If biosphere, indices need to be subtracted from technosphere indices.
            row = row - len(self.metadata) + 1

        if strategy == "itemwise":
            specific = self.metadata[act_index].get("Exchange negative", False)
            if isinstance(specific, list):
                uncertainty_negative = specific[row]
            else:  # because some activity don't have uncertainty at all, in this case is background system
                uncertainty_negative = specific
        elif strategy == "columnwise":
            uncertainty_negative = self.metadata[act_index].get("Exchange negative", False)

        return uncertainty_negative

    def add_nonuniform_uncertainty(self, bw_data, bw_indices, bw_flip, bg_strategy, fg_num=None, fg_strategy=None):
        """
        Prepare uncertainty array for datapackage. By default, foreground system is not considered, but you can set youself.

        Parameters:
            * bw_data: One of the technosphere/bioshphere/characterization factor matrix in datapackage needed format.
            * bw_indices: Matrix indices in datapackage needed format.
            * bw_flip: Flip array of technosphere in datapackage needed format.
            * bg_strategy: The uncertainty stragegy for one matrix in background system, two options available: "itemwise" and "columnwise"
            * fg_num: The number of columns in the foreground system.
            * fg_strategy: The uncertainty stragegy fsor one matrix in foreground system, two options available: "itemwise" and "columnwise"
        """
        if self.metadata is None:
            print("Please write your uncertainty information into metadata first.")

        uncertainty_array = []
        for i, data in enumerate(bw_data):
            row, col = bw_indices[i]
            act_index = col
            uncertainty_type = self.metadata[act_index].get("Activity uncertainty type", 0)
            if fg_num is not None and fg_strategy is not None:
                if act_index < fg_num: # foreground situation
                    strategy = fg_strategy
                else:
                    strategy = bg_strategy
            else:
                strategy = bg_strategy
            uncertainty_array.append(self.generate_uncertainty_tuple(data, uncertainty_type, self.get_uncertainty_value(strategy, act_index, row), self.get_uncertainty_negative(strategy, act_index, row)))

        return np.array(uncertainty_array, dtype=bwp.UNCERTAINTY_DTYPE)
    
    def add_uniform_uncertainty(self, type, gsd, bw_data, bw_flip):
        """
        Generate the uncertainty tuple for one value.

        Parameters:
            * type: The type of uncertainty, such as "Uniform".
            * gsd: Geometric Standard Deviation, used to calculate sigma of lognormal distribution.
            * bw_data: All values for foreground system or background system.
            * bw_flip: The flip array of technosphere.
        """
        uncertainty_array = np.zeros(len(bw_data), dtype=bwp.UNCERTAINTY_DTYPE)

        if bw_flip is not None:
            for i in range(len(bw_data)):
                if bw_flip[i] == True:
                    uncertainty_array[i] = self.generate_uncertainty_tuple(bw_data[i], type, gsd)
                else:
                    uncertainty_array[i] = (0, bw_data[i], np.NaN, np.NaN, np.NaN, np.NaN, False)
        else:
            for i in range(len(bw_data)):
                uncertainty_array[i] = self.generate_uncertainty_tuple(bw_data[i], type, gsd)

        return uncertainty_array

    # TODO: Ignore the flip first, modify it after generate all uncertainty tuples. -> Not use this function, so it's ok for now.
    def add_multifunctionality_flip(self, extend_data: pd.DataFrame, act_column: str, flip_column: str, dp_flip: np.ndarray, dp_indices: np.ndarray, activities: list) -> np.ndarray:
        """
        Add flip sign for multifunctionality foreground system. (It's used when user's input is all positive values and only the last column shows to flip or not.)
        
        Parameters:
            * extend_data: user input file in dataframe format.
            * flip_column: the column name of flip sign in user's input.
            * dp_flip: the prepared flip numpy array for datapackage.
            * dp_indices: the prepared indices numpy array for datapackage.
        """
        for flip, indices in zip(dp_flip, dp_indices):
            if indices[1] == 0:
                flip_sign = extend_data[extend_data[act_column] == activities[indices[0]]][flip_column]
                if not flip_sign.empty:
                    flip_sign = flip_sign.iloc[0]
                    if flip_sign == False:
                        dp_flip[indices[0]] = False
                else:
                    pass

        return dp_flip
    
    def add_multifunctionality_negative(self, extend_data, act_column: str, negative_column: str, dp_uncertainty, dp_indices, activities: list):
        """
        Add uncertainty negative for multifunctionality foreground system.
        """
        for uncertainty, indices in zip(dp_uncertainty, dp_indices):
            if indices[1] == 0:
                if indices[0] >= len(activities):
                    negative_sign = extend_data[extend_data[act_column] == activities[indices[0]-len(activities)]][negative_column] # minus technosphere row.
                    pos = dp_indices.tolist().index((indices[0], indices[1]))
                    if not negative_sign.empty:
                        if negative_sign == True:
                            dp_uncertainty[pos][-1] = True
                        elif negative_sign == False:
                            dp_uncertainty[pos][-1] = False
                    else:
                        pass

        return dp_uncertainty