import streamlit as st
import matplotlib.pyplot as plt
import matplotlib as mpl
import importlib
import dataframe
from dataframe import read_csv

# configure
plt.rcParams["mathtext.default"] = "regular"
mpl.rcParams["text.usetex"] = False

# reloads library in app
importlib.reload(dataframe)

# youtube data for join step
youtube_df = read_csv("Data/Top_Songs_YouTube.csv").select(
    ["title", "view_count", "channel", "channel_follower_count"]
)

# main title for app
st.set_page_config(
    page_title="Spotify Listening Dashboard",
    page_icon="🎧",
    layout="wide"
)

# sidebar
st.sidebar.title("Menu")
option = st.sidebar.radio(
    "",
    [
        "Home",
        "Data Preview / Summary",
        "Listening Leaderboard",
        "Filter",
        "Plot",
        "Join",
        "About",
        "Download and Convert Listening Data"
    ]
)

# header
st.markdown(
    """
    <div style="text-align:center;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/8/84/Spotify_icon.svg" width="100">
        <h2 style="color:#1DB954;">Spotify Listening Insights</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# home
if option == "Home":
    st.markdown(
        """
        <div style="text-align:center; color:white; background-color:#121212; padding:25px; border-radius:12px;">
            <h2>🎧 Welcome to Your Spotify Listening Dashboard</h2>
            <p>
                Discover trends in your Spotify listening history through interactive charts and summaries.
            </p>
            <p>
                Use the sidebar to navigate — upload your Spotify data or use the default sample!
            </p>
            <p><i>Uploader appears once you leave the home page.</i></p>
        </div>
        """,
        unsafe_allow_html=True
    )

# download spotify data page
elif option == "Download and Convert Listening Data":
    st.markdown(
        """
        <div style="text-align:center; color:white; background-color:#121212; padding:25px; border-radius:12px;">
            <h2>How to Retrieve and Convert Your Spotify Listening Data</h2>
            <h3>Download</h3>
            <p>1. Open the <a href="https://www.spotify.com/us/account/privacy/">Spotify Account Privacy Page</a>.</p>
            <p>2. Request your data under "Account Data".</p>
            <p>3. Confirm the email request.</p>
            <p>4. Wait ~4 days for the email with your download link.</p>
            <h3>Convert to CSV</h3>
            <p>
                1. Make a copy of this 
                <a href="https://colab.research.google.com/drive/1LakN37X4A_BlwrK-n2zvAtcNUeX-V7R_?usp=sharing">
                Colab Notebook
                </a>.
            </p>
            <p>2. Follow the instructions in the notebook to create your csv file for the to upload into the dashboard.</p>
            <p><i>Uploader appears once you leave the home page.</i></p>
        </div>
        """,
        unsafe_allow_html=True
    )
# about
elif option == "About":
    st.markdown(
        """
        <div style="text-align:center; color:white; background-color:#121212; padding:25px; border-radius:12px;">
            <h2>About This Application</h2>
            <p>Created by Alyssa Keehan</p>
            <p>DSCI 551: Foundations of Data Management</p>
            <p>
                This dashboard analyzes your Spotify listening history using a
                custom-built DataFrame library developed for the class.
            </p>
            <p><i>Uploader appears once you leave the home page.</i></p>
        </div>
        """,
        unsafe_allow_html=True
    )

# all other pages require data input
else:
    st.subheader("📂 Choose Your Data Source")
    # inserted for grading purposes. allows grader to use default data
    use_default = st.checkbox("Use default dataset (Data/streaming_history.csv)")

    df = None
    
    # use default data
    # leverages read_csv function in dataframe class
    if use_default:
        try:
            df = read_csv("Data/streaming_history.csv")
            st.success("Loaded default dataset successfully!")
        except Exception as e:
            st.error(f"Failed to load default data: {e}")
    # use uploaded data
    # leverages read_csv function in dataframe class
    else:
        uploaded_file = st.file_uploader(
            "Upload your Spotify listening CSV",
            type="csv"
        )

        if uploaded_file is not None:
            df = read_csv(uploaded_file)
            st.success("File uploaded successfully!")
    # warning message to user to select option
    if df is None:
        st.warning("Please upload a file or use the default dataset.")
        st.stop()

    # data preview
    # uses aggregate method
    if option == "Data Preview / Summary":
        st.subheader("👀 Data Preview")
        n = st.number_input("Number of rows to display:", min_value=1, value=10)
        st.table(df.to_rows(n))

        st.subheader("🎶 Listening Summary")
        summary_rows = []

        for col in df.columns:
            if col == "":
                continue

            values = df.data[col]
            unique_count = len(set(values))

            if col == "msPlayed":
                try:
                    max_val = f"{df.aggregate(col, max):.0f}"
                    min_val = f"{df.aggregate(col, min):.0f}"
                    sum_val = f"{df.aggregate(col, sum):.0f}"
                except Exception:
                    max_val = min_val = sum_val = None
            else:
                max_val = min_val = sum_val = None

            summary_rows.append(
                {
                    "Column": col,
                    "Unique Count": unique_count,
                    "Max": max_val,
                    "Min": min_val,
                    "Sum": sum_val,
                }
            )

        st.table(summary_rows)

    # leaderboard
    elif option == "Listening Leaderboard":
        st.subheader("🏆 Top Artist / Track by Listens")
        col = st.selectbox("Select column:", ["artistName", "trackName"])
        values = df.data[col]

        counts = {}
        for v in values:
            counts[v] = counts.get(v, 0) + 1

        rows = [
            {"value": k, "count": counts[k]}
            for k in counts
        ]

        rows.sort(key=lambda x: x["count"], reverse=True)
        st.table(rows)

    # filter
    # uses filter, select 
    elif option == "Filter":
        st.subheader("🎯 Filter Data")

        selected_column = st.selectbox("Filter by:", ["artistName", "trackName"])
        unique_values = sorted([str(v) for v in df.unique(selected_column)])

        selected_value = st.selectbox("Select value:", unique_values)

        other_col = (
            "trackName"
            if selected_column == "artistName"
            else "artistName"
        )

        filtered_df = df.filter(lambda row: row[selected_column] == selected_value).select(["endTime", other_col, "msPlayed"])

        st.write(f"Filtered {filtered_df.num_rows} rows.")

        sort_column = st.selectbox("Sort by:", ["endTime", "msPlayed"])
        order = st.radio("Sort order:", ["Ascending", "Descending"])

        rows = filtered_df.to_rows()
        try:
            rows.sort(
                key=lambda x: x[sort_column]
                if x[sort_column] is not None
                else float("-inf"),
                reverse=(order == "Descending"),
            )
        except TypeError:
            st.warning("Cannot sort mixed-type column.")

        st.table(rows)

    # plot
    # uses group_by, aggregate
    elif option == "Plot":
        st.subheader("📊 Plot Data")

        plot_type = st.selectbox("Select plot type:",["Bar Chart 📊", "Pie Chart 🥧", "Line Chart 📈"])

        # categorical data 
        if plot_type in ["Bar Chart 📊", "Pie Chart 🥧"]:
            selected_cat = st.selectbox("Categorical variable:",["artistName", "trackName"])
            selected_num = st.selectbox("Numerical variable:",["listens", "msPlayed"])

            grouped = df.group_by(selected_cat)

            rows = []
            for name, gdf in grouped.items():
                if selected_num == "listens":
                    val = gdf.aggregate(selected_cat, lambda x: len(x))
                else:
                    val = gdf.aggregate("msPlayed", lambda x: sum(int(v) for v in x))

                rows.append({selected_cat: name, selected_num: val})

            rows.sort(key=lambda x: x[selected_num], reverse=True)
            st.table(rows[:10])

            labels = [str(row[selected_cat])[:15].replace("$", "\\$") for row in rows[:20]]
            values = [row[selected_num] for row in rows[:20]]

            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor("#000")
            ax.set_facecolor("#121212")

            if plot_type == "Bar Chart 📊":
                ax.bar(labels, values, color="#1DB954")
            else:
                ax.pie(values, labels=labels, autopct="%1.1f%%")

            ax.set_title(
                f"Top {len(labels)} {selected_cat} by {selected_num}",
                color="white"
            )
            plt.xticks(rotation=45, ha="right", color="white")
            plt.yticks(color="white")
            st.pyplot(fig)

        # numerical 
        else:
            selected_col = st.selectbox("Filter by:", ["artistName", "trackName"])
            unique_vals = sorted([str(v) for v in df.unique(selected_col)])
            selected_val = st.selectbox("Select value:", unique_vals)

            selected_num = st.selectbox("Measure:", ["listens", "msPlayed"])

            filtered = [
                row for row in df.to_rows()
                if row[selected_col] == selected_val
            ]

            agg = {}
            for row in filtered:
                date = str(row["endTime"])[:10]
                if selected_num == "listens":
                    agg[date] = agg.get(date, 0) + 1
                else:
                    agg[date] = agg.get(date, 0) + int(row["msPlayed"])

            from datetime import datetime

            try:
                rows = sorted(agg.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))
            except:
                rows = list(agg.items())

            labels = [x[0] for x in rows]
            values = [x[1] for x in rows]

            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor("#000")
            ax.set_facecolor("#121212")
            ax.plot(labels, values, marker="o", color="#1DB954")

            ax.set_title(f"{selected_num} over time", color="white")
            ax.set_xlabel("Date", color="white")
            ax.set_ylabel(selected_num, color="white")
            plt.xticks(rotation=45, ha="right", color="white")
            plt.yticks(color="white")
            st.pyplot(fig)

    # join
    # uses group_by, aggregate
    elif option == "Join":
        st.subheader("🔗 Join Streaming Data with YouTube Top Songs")

        st.subheader("YouTube Data Preview")
        st.table(youtube_df.to_rows(10))

        grouped = df.group_by("trackName")

        agg_rows = []
        for track, gdf in grouped.items():
            artist = gdf["artistName"][0] if "artistName" in gdf.columns else None
            listens = gdf.aggregate("trackName", lambda col: len(col))
            ms = gdf.aggregate("msPlayed", lambda col: sum(int(v) for v in col))

            agg_rows.append({
                "trackName": track,
                "artistName": artist,
                "listens": listens,
                "msPlayed": ms,
            })

        agg_rows.sort(key=lambda x: x["listens"], reverse=True)

        agg_df = dataframe.DataFrame(
            {
                "trackName": [r["trackName"] for r in agg_rows],
                "artistName": [r["artistName"] for r in agg_rows],
                "listens": [r["listens"] for r in agg_rows],
                "msPlayed": [r["msPlayed"] for r in agg_rows],
            }
        )

        st.subheader("Aggregated Data Preview")
        st.table(agg_df.to_rows(10))

        joined_df = agg_df.join(
            youtube_df,
            left_on="trackName",
            right_on="title",
            how="inner",
            substring=True,
        )

        filtered = {col: [] for col in joined_df.columns}

        for i in range(joined_df.num_rows):
            artist = str(joined_df["artistName"][i]).lower().strip()
            channel = str(joined_df["channel"][i]).lower().strip()

            if artist == channel:
                for col in joined_df.columns:
                    filtered[col].append(joined_df[col][i])

        joined_df = dataframe.DataFrame(filtered)

        st.subheader("Final Joined Results")
        if joined_df.num_rows == 0:
            st.warning("No matching rows.")
        else:
            st.table(joined_df.to_rows(15))
