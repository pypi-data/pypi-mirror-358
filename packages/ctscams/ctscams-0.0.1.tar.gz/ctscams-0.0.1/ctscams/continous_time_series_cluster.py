
import matplotlib.pyplot as plt
import ruptures as rpt  # Change point detection library
import pandas as pd
from tqdm.notebook import tqdm_notebook
import math

def continous_time_series_clustering(df,time_col,level="D", plot=True, penalty=0.1):
    # Convert "created_at" to datetime and sort by time
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.sort_values(time_col).reset_index(drop=True)


    df["timestamp"] = df[time_col].dt.to_period(level)
    time_counts = df.groupby("timestamp").size().reset_index(name="tweet_count")

    # Prepare data for trend analysis
    time_series = time_counts["tweet_count"].values

    # Apply Change Point Detection
    model = rpt.Pelt(model="rbf").fit(time_series)  # "rbf" detects variance and mean changes
    change_points = model.predict(pen=penalty)  # Penalty adjusts sensitivity to change points
    
    # Assign each segment a cluster
    time_counts["cluster"] = 0  # Initialize clusters
    current_cluster = 0
    for i in tqdm_notebook(range(len(change_points) - 1)):
        start = change_points[i]
        end = change_points[i + 1] if i + 1 < len(change_points) else len(time_counts)
        time_counts.loc[start:end, "cluster"] = current_cluster
        current_cluster += 1
        # Ensure timestamp is in datetime format


    # Ensure timestamp is correctly formatted
    if isinstance(time_counts["timestamp"].dtype, pd.PeriodDtype):
        time_counts["timestamp"] = time_counts["timestamp"].dt.to_timestamp()
    else:
        time_counts["timestamp"] = pd.to_datetime(time_counts["timestamp"])

    df[time_col] = pd.to_datetime(df[time_col])  # Ensure datetime format

    if level == "D" or level == "W-SUN":
        time_counts["day"] = time_counts["timestamp"].dt.date
        df["day"] = df[time_col].dt.date
        df = pd.merge(time_counts[["day", "cluster"]], df, on=["day"], how="right")
        tweet_counts_by_day_and_cluster = df.groupby(["day", "cluster"]).size().unstack() 
    elif level == "M":
        time_counts["month"] = time_counts["timestamp"].dt.to_period("M")
        df["month"] = df[time_col].dt.to_period("M")  
        df = pd.merge(time_counts[["month", "cluster"]], df, on=["month"], how="right")
        tweet_counts_by_day_and_cluster = df.groupby(["month", "cluster"]).size().unstack() 
    elif level == "YE" or level == "Y":
        time_counts["year"] = time_counts["timestamp"].dt.year
        df["year"] = df[time_col].dt.year  
        df = pd.merge(time_counts[["year", "cluster"]], df, on=["year"], how="right")
        tweet_counts_by_day_and_cluster = df.groupby(["year", "cluster"]).size().unstack()

    else:
        raise ValueError("Invalid level specified. Use 'D', 'W-SUN', 'M', or 'YE'.")
    
    if plot==True:
        plot_fig(tweet_counts_by_day_and_cluster,level)



    return(df)

def plot_fig(tweet_counts_by_day_and_cluster, level):
    
    if level == "D" or level=="W-SUN":
        print(tweet_counts_by_day_and_cluster.index)
        tweet_counts_by_day_and_cluster.index = pd.to_datetime(tweet_counts_by_day_and_cluster.index)
        if isinstance(tweet_counts_by_day_and_cluster.index, pd.PeriodIndex):
            tweet_counts_by_day_and_cluster.index = tweet_counts_by_day_and_cluster.index.to_timestamp()

        # Fill missing values with 0 to ensure all clusters are represented
        tweet_counts_by_day_and_cluster = tweet_counts_by_day_and_cluster.fillna(0)

        # Initialize the plot
        plt.figure(figsize=(12, 6))

        # Define a colormap for the clusters (you can customize this)
        colormap = plt.cm.tab10

        # Loop over the rows of the data to draw connected lines with the next cluster's color
        for i in range(len(tweet_counts_by_day_and_cluster) - 1):
            # Determine the cluster with the highest count for the current and next months
            current_cluster = tweet_counts_by_day_and_cluster.iloc[i].idxmax()
            next_cluster = tweet_counts_by_day_and_cluster.iloc[i + 1].idxmax()
            
            # Get the current and next month's x-values (dates) and y-values (tweet counts)
            x_values = tweet_counts_by_day_and_cluster.index[i:i + 2]
            y_values = [
                tweet_counts_by_day_and_cluster.loc[x_values[0], current_cluster],
                tweet_counts_by_day_and_cluster.loc[x_values[1], next_cluster],
            ]
            
            # Use the color of the "next cluster" (end of the segment)
            color = colormap(next_cluster % 10)  # Modulo ensures we don't exceed colormap range
            
            # Plot the line with the next cluster's color
            plt.plot(x_values, y_values, color=color, label=f'Cluster {next_cluster}' if i == 0 else "")

        # Add labels, title, and legend
        plt.title('Frequency of Tweets by Day (delineated by clusters)', fontsize=16)
        plt.xlabel('Day', fontsize=20)
        plt.ylabel('Number of Tweets', fontsize=20)
        plt.xticks(fontsize=12.5, rotation=45)
        plt.yticks(fontsize=15)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.show()

    elif level == "M":
        tweet_counts_by_month_and_cluster=tweet_counts_by_day_and_cluster
        tweet_counts_by_month_and_cluster.index = tweet_counts_by_month_and_cluster.index.to_timestamp()

        # Fill missing values with 0 to ensure all clusters are represented
        tweet_counts_by_month_and_cluster = tweet_counts_by_month_and_cluster.fillna(0)

        # Initialize the plot
        plt.figure(figsize=(12, 6))

        # Define a colormap for the clusters (you can customize this)
        colormap = plt.cm.tab10

        # Loop over the rows of the data to draw connected lines with the next cluster's color
        for i in range(len(tweet_counts_by_month_and_cluster) - 1):
            # Determine the cluster with the highest count for the current and next months
            current_cluster = tweet_counts_by_month_and_cluster.iloc[i].idxmax()
            next_cluster = tweet_counts_by_month_and_cluster.iloc[i + 1].idxmax()
            
            # Get the current and next month's x-values (dates) and y-values (tweet counts)
            x_values = tweet_counts_by_month_and_cluster.index[i:i + 2]
            y_values = [
                tweet_counts_by_month_and_cluster.loc[x_values[0], current_cluster],
                tweet_counts_by_month_and_cluster.loc[x_values[1], next_cluster],
            ]
            
            # Use the color of the "next cluster" (end of the segment)
            color = colormap(next_cluster % 10)  # Modulo ensures we don't exceed colormap range
            
            # Plot the line with the next cluster's color
            plt.plot(x_values, y_values, color=color, label=f'Cluster {next_cluster}' if i == 0 else "")

        # Add labels, title, and legend
        plt.title('Frequency of Tweets by Month (delineated by clusters)', fontsize=16)
        plt.xlabel('Month', fontsize=20)
        plt.ylabel('Number of Tweets', fontsize=20)
        plt.xticks(fontsize=12.5, rotation=45)
        plt.yticks(fontsize=15)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.show()




    elif level=="YE" or level=="Y":
        tweet_counts_by_year_and_cluster=tweet_counts_by_day_and_cluster
        tweet_counts_by_year_and_cluster.index = pd.to_datetime(tweet_counts_by_year_and_cluster.index, format='%Y')
        #tweet_counts_by_year_and_cluster.index = tweet_counts_by_year_and_cluster.index.to_timestamp()


        # Fill missing values with 0 to ensure all clusters are represented
        tweet_counts_by_year_and_cluster = tweet_counts_by_year_and_cluster.fillna(0)

        # Initialize the plot
        plt.figure(figsize=(12, 6))

        # Define a colormap for the clusters (you can customize this)
        colormap = plt.cm.tab10

        # Loop over the rows of the data to draw connected lines with the next cluster's color
        for i in range(len(tweet_counts_by_year_and_cluster) - 1):
            # Determine the cluster with the highest count for the current and next months
            current_cluster = tweet_counts_by_year_and_cluster.iloc[i].idxmax()
            next_cluster = tweet_counts_by_year_and_cluster.iloc[i + 1].idxmax()
            
            # Get the current and next month's x-values (dates) and y-values (tweet counts)
            x_values = tweet_counts_by_year_and_cluster.index[i:i + 2]
            y_values = [
                tweet_counts_by_year_and_cluster.loc[x_values[0], current_cluster],
                tweet_counts_by_year_and_cluster.loc[x_values[1], next_cluster],
            ]
            
            # Use the color of the "next cluster" (end of the segment)
            color = colormap(next_cluster % 10)  # Modulo ensures we don't exceed colormap range
            
            # Plot the line with the next cluster's color
            plt.plot(x_values, y_values, color=color, label=f'Cluster {next_cluster}' if i == 0 else "")

        # Add labels, title, and legend
        plt.title('Frequency of Tweets by year (delineated by clusters)', fontsize=16)
        plt.xlabel('Year', fontsize=20)
        plt.ylabel('Number of Tweets', fontsize=20)
        plt.xticks(fontsize=15, rotation=45)
        plt.yticks(fontsize=15)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.show()



    else:
        raise ValueError("Invalid level specified. Use 'D', 'week', 'month', or 'YE'.")
    # Plot the frequency with different colors for each cluster
    plt.figure(figsize=(12, 6))



def cluster_sampling(df,sample_size,stratified_col=None):
    df=df.reset_index(drop=True)
    if stratified_col==None:
        # Sample random rows
        df=df.sample(frac=1, random_state=42).reset_index(drop=True)
        sampled_rows = df.sample(n=sample_size, random_state=42)  # Setting seed for reproducibility
        # Create a new column with default value 0
        df['selected'] = 0
        # Mark sampled rows with 1
        df.loc[sampled_rows.index, 'selected'] = 1
    else:
        df=df.sample(frac=1,random_state=42).reset_index(drop=True)
        num_groups = df[stratified_col].nunique()
        samples_per_group = math.ceil(sample_size / num_groups)
        sampled_df = df.groupby(stratified_col, group_keys=False).apply(lambda x: x.sample(n=min(samples_per_group, len(x)), random_state=42))
        df['selected'] = 0
        df.loc[sampled_df.index, 'selected'] = 1
    # else:
    #     # Use StratifiedShuffleSplit for proportionate stratified sampling
    #     splitter = StratifiedShuffleSplit(n_splits=1, test_size=None, train_size=sample_size, random_state=42)

    #     for train_idx, _ in splitter.split(df, df[stratified_col]):
    #         sampled_df = df.iloc[train_idx]

    #     # Mark the selected samples
    #     df['selected'] = 0
    #     df.loc[sampled_df.index, 'selected'] = 1

    return(df)








