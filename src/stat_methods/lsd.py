"""
Class for Fishers LSD
"""
from math import sqrt
import scipy.stats as stats
import pandas as pd
from statsmodels.formula.api import ols
import statsmodels.api as sm
import numpy as np
import plotly.graph_objects as go

class FishersLSD:
    def __init__(self, df, treatment, response, groupby=None, groupby_value=None, confidence=0.95):
        # Check if data in a pandas dataframe
        if isinstance(df, pd.DataFrame):
            pass
        else:
            raise RuntimeError("Observed data is not a DataFrame.")

        self.df = df[df[groupby]==groupby_value].reset_index(drop=True)
        self.confidence=confidence
        self.response=response
        self.treatment=treatment
        self.groupby=groupby
        self.groupby_value = groupby_value,
    
    def table(self):
        """
        Perform the fischers LSD on all pairwise combinations of
        mean differences for k groups to determine if the difference
        is significant. This function takes data in long form, that is
        where k groups are in a single column and values are in another.

        ### Parameters:
            data: DataFrame
                The sample data (Long Form)
            
            treatment: str
                The treatment variable from the data that defines the k
                categories
            
            response: str
                The response variable from the data that defines the value
                of the observation

            confidence:
                the degree of confidence with which to estimate the chi
                squared constant; the default is .95.
        """
        # Run a one-way anova to obtain the mse and within groups dof
        model = ols(f'{self.response} ~ C({self.treatment})', data=self.df).fit()
        anova_table = sm.stats.anova_lm(model,typ=1)
        mse = anova_table.iloc[1][2]
        within_groups_dof = anova_table.iloc[1][0]
        alpha = 1 - self.confidence

        # Create a dictionary mapping the population number to the population name
        population_dict = dict([(i+1, j) for i, j in enumerate(self.df[self.treatment].unique())])

        # Compute the sample means for each population
        sample_means = [np.mean(self.df[self.df[self.treatment] == k][self.response]) for k in self.df[self.treatment].unique()]

        # Determine and track the population pairs used for pairwise comparison
        pairs = []
        diffmean = []
        critical_values = []
        for i in range(len(sample_means)-1):
            for j in range(i+1, len(sample_means)):
                # Get the names for each k population
                pairs.append((f'{population_dict[i+1]} vs. {population_dict[j+1]}'))
                # Calculate the absolute differences between i and j populations
                diffmean.append(abs(sample_means[i]-sample_means[j]))
                # Calculate the critical value for each pairwise comparison
                n_i = len(self.df[self.df[self.treatment] == population_dict[i+1]])
                n_j = len(self.df[self.df[self.treatment] == population_dict[j+1]])
                critical_value = stats.t.ppf(1 - alpha/2, within_groups_dof) * sqrt(mse*(1/n_i + 1/n_j))
                critical_values.append(critical_value)
        
        # Determine the significance of each pairwise comparison
        significance_result = []
        for abs_mean, crit_val in zip(diffmean, critical_values):
            if abs_mean >= crit_val:
                significance_result.append('Populations are significantly different')
            else:
                significance_result.append('Populations are not significantly different')

        # Create a results summary to return as output
        df_dict = {
            'pairs': pairs,
            'abs_diff': diffmean,
            'critical_value': critical_values,
            'significance': significance_result
        }

        result_df = pd.DataFrame(df_dict)
        
        return result_df

    def plot(self):
        lsd_table = self.table()
        
        comparison_iter = 0
        df_pop_li = []

        for pair in lsd_table['pairs']:
            comparison_iter += 1
            pop1 = pair.split(' vs. ')[0]
            pop2 = pair.split(' vs. ')[1]
            pop_test=[]
            for pop in [pop1, pop2]:
                df = self.df[self.df[self.treatment] == pop].reset_index(drop=True)
                df['comparison'] = str(comparison_iter)
                pop_test.append(df)
            df_pop_li.append(pd.concat(pop_test))

        df_comparison = pd.concat(df_pop_li).reset_index(drop=True)

        fig = go.Figure()
        pop1_colors = ['seagreen', 'seagreen', 'seagreen', 'slateblue', 'slateblue', 'sienna']
        pop2_colors = ['slateblue', 'sienna', 'silver', 'sienna', 'silver', 'silver']
        show_legend = [True, False, False, False, False, True]


        for i in range(0,len(pd.unique(df_comparison['comparison']))):
            pop1 = df_comparison[df_comparison['comparison'] == str(i+1)][self.treatment].unique()[0]
            pop2 = df_comparison[df_comparison['comparison'] == str(i+1)][self.treatment].unique()[1]
            d = {str(i+1): [pop1, pop2]}
            for key, value in d.items():
                fig.add_trace(
                    go.Violin(
                        x=df_comparison['comparison'][(df_comparison[self.treatment] == value[0]) & (df_comparison['comparison'] == key)],
                        y=df_comparison[self.response][(df_comparison[self.treatment] == value[0]) & (df_comparison['comparison'] == key)],
                        legendgroup=value[0], name=value[0], scalegroup=value[0],
                        side='negative',
                        marker=dict(color=pop1_colors[i]),
                        showlegend=show_legend[i]
                    )
                )
                
                fig.add_trace(
                    go.Violin(
                        x=df_comparison['comparison'][(df_comparison[self.treatment] == value[1]) & (df_comparison['comparison'] == key)],
                        y=df_comparison[self.response][(df_comparison[self.treatment] == value[1]) & (df_comparison['comparison'] == key)],
                        legendgroup=value[1], name=value[1], scalegroup=value[1],
                        side='positive',
                        marker=dict(color=pop2_colors[i]),
                        showlegend=show_legend[i]
                    )
                )

        # update characteristics shared by all traces
        fig.update_traces(
            meanline_visible=True)
        fig.update_layout(
            title_text=f"Change between pre and post test scored, question {self.groupby_value}<br><i>by pairwise comparison of race/ethnicity",
            violinmode='overlay')
        return fig.show()