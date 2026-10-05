import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

class BioprocessMonitor:
    def __init__(self, filepath, ph_lims, temperature_lims):
        """
        Utility class used to monitor bioprocesses by
        generating dashboards and summaries.

        Parameters
        ----------
        filepath : str
            Input CSV dataset path.
        ph_lims : tuple[float, float]
            Lower and upper acceptable pH limits.
        temperature_lims : tuple[float, float]
            Lower and upper acceptable temperature limits.
        """
        self.df = pd.read_csv(filepath)
        self.ph_min = ph_lims[0]
        self.ph_max = ph_lims[1]
        self.temp_min = temperature_lims[0]
        self.temp_max = temperature_lims[1]




    def extract_batch(self, batch_id):
        """
        Extracts data corresponding to a single batch.

        Parameters
        ----------
        batch_id : int
            Batch identifier.

        Returns
        -------
        pandas.DataFrame
            DataFrame containing only rows associated with
            the requested batch.
        """
        df_batch = self.df.loc[self.df.loc[:, "batch_id"] == batch_id, :]
        return df_batch

    def optimal_ph_mask(self, df_batch):
        """
        Determines whether each pH measurement falls within
        the acceptable operating range.

        Parameters
        ----------
        df_batch : pandas.DataFrame
            Batch-specific DataFrame.

        Returns
        -------
        array-like of bool
            A mask whereby True indicates that the measurement
            is within the acceptable operating range.
        """
        mask = (self.ph_min <= df_batch.loc[:, "pH"]) * (df_batch.loc[:, "pH"] <= self.ph_max)
        return mask


    def optimal_temperature_mask(self, df_batch):
        """
        Determines whether each temperature measurement falls
        within the acceptable operating range.

        Parameters
        ----------
        df_batch : pandas.DataFrame
            Batch-specific DataFrame.

        Returns
        -------
        array-like of bool
            A mask whereby True indicates that the measurement
            is within the acceptable operating range.
        """
        mask = (self.temp_min <= df_batch.loc[:, "temperature_C"]) * (df_batch.loc[:, "temperature_C"] <= self.temp_max)
        return mask



    def get_n_batches(self):
        """
        Determines the number of unique batches present
        in the dataset.

        Returns
        -------
        int
            Total number of distinct batch identifiers.
        """
        n_batches=len(self.df['batch_id'].unique())
        return n_batches

    def export_dashboard(self, batch_id, filepath):
        """
        Creates and saves a dashboard figure for a single batch.

        Parameters
        ----------
        batch_id : int
            Batch identifier.
        filepath : str
            Output PNG image path.

        Dashboard Requirements
        ----------------------
        Create a 2 × 2 figure containing:

        Top-Left
            Glucose, biomass, and product concentrations versus time.
            - A different color and marker should be used for each substance.

        Top-Right
            Temperature versus time.
            - Measurements within the acceptable temperature range
              should be displayed as green circles.
            - Measurements outside the acceptable temperature range
              should be displayed as red X markers.

        Bottom-Left
            pH versus time.
            - Measurements within the acceptable pH range
              should be displayed as green circles.
            - Measurements outside the acceptable pH range
              should be displayed as red X markers.

        Bottom-Right
            Dissolved oxygen versus time.

        Additional Requirements
        -----------------------
        - Use scatter plots.
        - Add x-axis and y-axis labels.
        - Add legends where appropriate.
        - Apply consistent formatting across all subplots unless
          indicated otherwise.
        - Apply a tick spacing of 6 h on the x-axis for all subplots.
        - Save the figure to the provided filepath.
        - Close the figure after saving.
        """
        df_batch = self.extract_batch(batch_id)
        ph_mask = self.optimal_ph_mask(df_batch)
        temp_mask = self.optimal_temperature_mask(df_batch)

        t = df_batch.loc[:, "time_h"]

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 7), dpi=200, layout="constrained")

        kwargs_scatter = dict(s=20, edgecolors="black", linewidth=0.5)
        kwargs_x_marker = dict(s=20, linewidth=1.0)

        #Top-left
        ax = axes[0, 0]
        ax.scatter(t, df_batch.loc[:, "C_glucose_g_L^-1"], label="Glucose", color="tab:blue", marker="o",**kwargs_scatter)
        ax.scatter(t, df_batch.loc[:, "C_biomass_g_L^-1"], label="Biomass", color="tab:orange", marker="D",**kwargs_scatter)
        ax.scatter(t, df_batch.loc[:, "C_product_g_L^-1"], label="Product", color="tab:green", marker="s",**kwargs_scatter)

        #Top Right
        ax = axes[0, 1]
        ax.scatter(t.loc[temp_mask], df_batch.loc[temp_mask, "temperature_C"],label="Optimal", color="green", marker="o", **kwargs_scatter)
        ax.scatter(t.loc[~temp_mask], df_batch.loc[~temp_mask, "temperature_C"],label="Not optimal", color="red", marker="x", **kwargs_x_marker)

        #Bottom-Left
        ax = axes[1, 0]
        ax.scatter(t.loc[ph_mask], df_batch.loc[ph_mask, "pH"],label="Optimal", color="green", marker="o", **kwargs_scatter)
        ax.scatter(t.loc[~ph_mask], df_batch.loc[~ph_mask, "pH"],label="Not optimal", color="red", marker="x", **kwargs_x_marker)

        #Bottom-Right
        ax = axes[1, 1]
        ax.scatter(t, df_batch.loc[:, "DO_percent"], color="tab:purple", marker="o", **kwargs_scatter)

        ylabels = ["Concentration [g/L]", "Temperature [C]", "pH", "Dissolved Oxygen [%]"]

        for ax, ylabel in zip(axes.ravel(), ylabels):
            ax.xaxis.set_major_locator(MultipleLocator(6))
            ax.set_xlabel("Time [h]", fontsize=10)
            ax.set_ylabel(ylabel, fontsize=10)
            ax.tick_params(axis="both", which="major", labelsize=10)

        axes[0, 0].legend(fontsize=10)
        axes[0, 1].legend(fontsize=10)
        axes[1, 0].legend(fontsize=10)

        fig.savefig(filepath)
        plt.close(fig)







    def export_summary(self, filepath):
        """
        Generates a batch summary table and exports it to a CSV file.

        Parameters
        ----------
        filepath : str
            Output CSV table path.

        Summary Table Columns
        ---------------------
        batch_id
            Batch identifier.

        ph_optimal_percent
            Percentage of measurements in a batch within the
            acceptable pH range, rounded to 2 decimal places.

        temperature_optimal_percent
            Percentage of measurements in a batch within the
            acceptable temperature range, rounded to 2 decimal places.

        C_product_g_L^-1_final
            Final product concentration for the batch.
        """
        n_batches = self.get_n_batches()
        records = []

        for batch_id in range(1, n_batches + 1):
            df_batch = self.extract_batch(batch_id)
            ph_mask = self.optimal_ph_mask(df_batch)
            temp_mask = self.optimal_temperature_mask(df_batch)

            ph_percent = round(ph_mask.mean() * 100, 2)
            temp_percent = round(temp_mask.mean() * 100, 2)
            c_product_final = df_batch.loc[:, "C_product_g_L^-1"].iloc[-1]

            record = (batch_id, ph_percent, temp_percent, c_product_final)
            records.append(record)

        column_names = ["batch_id", "ph_optimal_percent", "temperature_optimal_percent", "C_product_g_L^-1_final"]
        df_summary = pd.DataFrame(records, columns=column_names)
        df_summary.to_csv(filepath, index=False)





