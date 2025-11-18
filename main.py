import streamlit as st
import matplotlib.pyplot as plt
import matplotlib as mpl
import importlib
import dataframe
from dataframe import read_csv

# MATPLOTLIB CONFIG
plt.rcParams["mathtext.default"] = "regular"
mpl.rcParams['text.usetex'] = False

# RELOAD FOR DEVELOPMENT
importlib.reload(dataframe)

# YOUTUBE DATA (STATIC)
youtube_df = read_csv("Data/Top_Songs_YouTube.csv").select(['title','view_count','channel', 'channel_follower_count'])

# PAGE CONFIG
st.set_page_config(page_title="Spotify Listening Dashboard", page_icon="🎧", layout="wide")

# SIDEBAR MENU
st.sidebar.title("Menu")
option = st.sidebar.radio(
    "",
    ["Home", "Data Preview / Summary", "Listening Leaderboard", "Filter", "Plot", "Join", "About","Download and Convert Listening Data"]
)

# HEADER
st.markdown(
    """
    <div style="text-align:center;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/8/84/Spotify_icon.svg" width="100">
        <h2 style="color:#1DB954;">Spotify Listening Insights</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# HOME PAGE
if option == "Home":
    st.markdown(
        """
        <div style="text-align:center; color:white; background-color:#121212; padding:25px; border-radius:12px;">
            <h2>🎧 Welcome to Your Spotify Listening Dashboard</h2>
            <p>
                Discover trends in your Spotify listening history through interactive charts and summaries.
                Explore your top artists, favorite tracks, and listening habits over time.
            </p>
            <p>
                Use the sidebar to navigate between pages — upload your Spotify data to get started!
            </p>
            <p><i>Note: the uploader appears once you leave this home page.</i></p>
        </div>
        """,
        unsafe_allow_html=True
    )
elif option == "Download and Convert Listening Data":
    st.markdown(
        """
        <div style="text-align:center; color:white; background-color:#121212; padding:25px; border-radius:12px;">
            <h2>How to Retrieve and Convert Your Spotify Listening Data</h2>
            <h3>Download</h3>
            <p>
                1. Open Your <a href="https://www.spotify.com/us/account/privacy/">Spotify Account Privacy Page</a>
            </p>
            <p>
                Use the sidebar to navigate between pages — upload your Spotify data to get started!
            </p>
            <p><i>Note: the uploader appears once you leave this home page.</i></p>
        </div>
        """,
        unsafe_allow_html=True
    )
elif option == "About":
    st.markdown(
        """
        <div style="text-align:center; color:white; background-color:#121212; padding:25px; border-radius:12px;">
            <h2>About This Application</h2>
            <p>
                Created by Alyssa Keehan
            </p>
            <p>
                DSCI 551: Foundations of Data Management
            </p>
            <p>
                <b>Project Objectives:</b> The goals of the project are to understand what happens under the
                hood of these libraries and their functions, and provide you with hands-on experiences in
                developing and using these functions. Your application may be a search app or an app that analyzes data.
            <p>
            <p>
                <b>Data Preview / Summary:</b> Leverages developed <i>read_csv</i> function from the 
                <b><u>DataFrame</u></b> program as well as <i>aggregate</i> method in the 
                <b><u>DataFrame</u></b> class.
            </p>
            <p>
                <b>Listening Leaderboard:</b> Shows either Top Artists or Top Tracks by Listens in Descending Order.
            </p>
            <p>
                <b>Filter:</b> Leverages developed <i>filter</i> and <i>select</i> methods in the 
                <b><u>DataFrame</u></b> class. Allows user to search for either an Artist or a Track Name
                and see how many times they streamed for either that artist or that song.
            </p>
            <p>
                <b>Plot:</b> Leverages developed <i>group_by</i> method in the 
                <b><u>DataFrame</u></b> class. Allows user to analyze their listening data by either a pie chart, bar chart or time series chart.
            </p>
            <p>
                <b>Join:</b> Leverages developed <i>join, aggregate & group_by</i> methods in the 
                <b><u>DataFrame</u></b> class.
            </p>
            <p><i>Note: the uploader appears once you leave this home page.</i></p>
        </div>
        """,
        unsafe_allow_html=True
    )
# OTHER PAGES (REQUIRE FILE UPLOAD)
else:
    uploaded_file = st.file_uploader("📂 Upload your Spotify listening data", type="csv")

    if uploaded_file is not None:
        st.success("✅ File uploaded successfully!")
        df = read_csv(uploaded_file)

        #DATA PREVIEW / SUMMARY
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

                summary_rows.append({
                    "Column": col,
                    "Unique Count": unique_count,
                    "Max": max_val,
                    "Min": min_val,
                    "Sum": sum_val
                })
            st.table(summary_rows)

        # LISTENING LEADERBOARD
        elif option == "Listening Leaderboard":
            st.subheader("🏆 Top Artist / Track by Listens")
            col = st.selectbox("Select column:", ['artistName','trackName'])
            values = df.data[col]
            counts = {}
            for v in values:
                counts[v] = counts.get(v, 0) + 1
            table_rows = [{"value": k, "count": counts[k]} for k in counts]
            table_rows.sort(key=lambda x: x["count"], reverse=True)
            st.table(table_rows)

        # FILTER DATA
        elif option == "Filter":
            st.subheader("🎯 Filter Data")
            selected_column = st.selectbox("Select column to filter by:", ['artistName','trackName'])
            unique_values = sorted([str(v) for v in df.unique(selected_column)])
            selected_value = st.selectbox("Select value:", unique_values, index=50)

            unused_column = 'trackName' if selected_column == 'artistName' else 'artistName'
            filtered_df = df.filter(lambda row: row[selected_column] == selected_value).select(['endTime', unused_column, 'msPlayed'])
            st.write(f"Filtered {filtered_df.num_rows} rows.")

            sort_column = st.selectbox("Select column to sort by:", ['endTime','msPlayed'])
            sort_order = st.radio("Sort order:", ["Ascending", "Descending"])

            rows = filtered_df.to_rows()
            try:
                rows.sort(
                    key=lambda x: x[sort_column] if x[sort_column] is not None else float('-inf'),
                    reverse=(sort_order == "Descending")
                )
            except TypeError:
                st.warning("Cannot sort column with mixed types. Sorting skipped.")
            st.table(rows)

        # PLOT DATA
        elif option == "Plot":
            st.subheader("📊 Plot Data")

            plot_type = st.selectbox("Select plot type:", ["Bar Chart 📊", "Pie Chart 🥧", "Line Chart 📈"])

            if plot_type in ["Bar Chart 📊", "Pie Chart 🥧"]:
                selected_categorical_value = st.selectbox("Select categorical variable:", ['artistName', 'trackName'])
                selected_numerical_value = st.selectbox("Select numerical variable:", ['listens', 'msPlayed'])

                grouped = df.group_by(selected_categorical_value)
                plot_rows = []

                for group_name, group_df in grouped.items():
                    if selected_numerical_value == "listens":
                        # Use aggregate with len() to count rows
                        value = group_df.aggregate(selected_categorical_value, lambda x: len(x))
                    else:
                        # Use aggregate with sum() to total up msPlayed
                        value = group_df.aggregate("msPlayed", lambda x: sum(int(v) for v in x))
        
                    plot_rows.append({selected_categorical_value: group_name,selected_numerical_value: value})

                plot_rows.sort(key=lambda x: x[selected_numerical_value], reverse=True)
                st.table(plot_rows[:10])

                if plot_type == "Bar Chart 📊":
                    n_bars = st.number_input("# Bars to display:", min_value=5, value=20)
                    labels = [str(row[selected_categorical_value])[:15].replace('$','\$') for row in plot_rows[:n_bars]]
                    values = [row[selected_numerical_value] for row in plot_rows[:n_bars]]

                    fig, ax = plt.subplots(figsize=(8,5))
                    fig.patch.set_facecolor("#000000")
                    ax.set_facecolor("#121212")
                    ax.bar(labels, values, color="#1DB954")
                    ax.set_xlabel(selected_categorical_value, color="white")
                    ax.set_ylabel(selected_numerical_value, color="white")
                    ax.set_title(f"Top {n_bars} {selected_categorical_value} by {selected_numerical_value}", color="white")
                    plt.xticks(rotation=45, ha="right", color="white")
                    plt.yticks(color="white")
                    plt.tight_layout()
                    st.pyplot(fig)

                elif plot_type == "Pie Chart 🥧":
                    n_slices = st.number_input("# Slices to display:", min_value=5, value=20)
                    labels = [str(row[selected_categorical_value])[:15].replace('$','\$') for row in plot_rows[:n_slices]]
                    values = [row[selected_numerical_value] for row in plot_rows[:n_slices]]

                    fig, ax = plt.subplots(figsize=(6,6))
                    fig.patch.set_facecolor("#000000")
                    ax.set_facecolor("#121212")
                    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
                    for text in texts + autotexts:
                        text.set_color("#FFFFFF")
                        text.set_fontweight("bold")
                        text.set_fontsize(11)
                    ax.axis("equal")
                    ax.set_title(f"Top {n_slices} {selected_categorical_value} by {selected_numerical_value}",
                                 color="#FFFFFF", fontsize=14, fontweight="bold")
                    st.pyplot(fig)

            else:
                selected_column = st.selectbox("Select column to filter by:", ['artistName', 'trackName'])
                unique_values = sorted([str(v) for v in df.unique(selected_column)])
                selected_value = st.selectbox("Select value:", unique_values, index=50)
                selected_numerical_value = st.selectbox("Select numerical variable:", ['listens', 'msPlayed'])

                filtered_rows = [row for row in df.to_rows() if row[selected_column] == selected_value]
                agg = {}
                for row in filtered_rows:
                    date = str(row['endTime'])[:10]
                    if selected_numerical_value == 'listens':
                        agg[date] = agg.get(date, 0) + 1
                    else:
                        agg[date] = agg.get(date, 0) + int(row['msPlayed'])

                from datetime import datetime
                try:
                    plot_rows = sorted(agg.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))
                except Exception:
                    plot_rows = list(agg.items())

                labels = [x[0] for x in plot_rows]
                values = [x[1] for x in plot_rows]

                fig, ax = plt.subplots(figsize=(10,5))
                fig.patch.set_facecolor("#000000")
                ax.set_facecolor("#121212")
                ax.plot(labels, values, marker="o", color="#1DB954")
                ax.set_xlabel("Date", color="white")
                ax.set_ylabel(selected_numerical_value, color="white")
                ax.set_title(f"{selected_numerical_value} for {selected_value} over time", color="white")
                plt.xticks(rotation=45, ha="right", color="white")
                plt.yticks(color="white")
                plt.tight_layout()
                st.pyplot(fig)

        # JOIN SECTION
        elif option == "Join":
            st.subheader("🔗 Join Streaming Data with Top YouTube Content")

            # --- Step 1: Preview YouTube Data ---
            st.subheader("YouTube Data Preview")
            st.table(youtube_df.to_rows(10))

            # --- Step 2: Aggregate streaming data by trackName ---
            grouped = df.group_by("trackName")
            aggregated_rows = []

            for track, group_df in grouped.items():
                # Artist from first row
                artist = group_df["artistName"][0] if "artistName" in group_df.columns else None

                # Total listens using aggregate() on any column (trackName)
                total_listens = group_df.aggregate("trackName", lambda col: len(col))

                # Total msPlayed using aggregate()
                total_msPlayed = group_df.aggregate("msPlayed", lambda col: sum(int(v) for v in col))

                aggregated_rows.append({
                    "trackName": track,
                    "artistName": artist,
                    "listens": total_listens,
                    "msPlayed": total_msPlayed
                })

            # --- Step 3: Sort by total listens descending ---
            aggregated_rows.sort(key=lambda x: x["listens"], reverse=True)

            # --- Step 4: Create aggregated DataFrame ---
            agg_df = dataframe.DataFrame({
                "trackName": [r["trackName"] for r in aggregated_rows],
                "artistName": [r["artistName"] for r in aggregated_rows],
                "listens": [r["listens"] for r in aggregated_rows],
                "msPlayed": [r["msPlayed"] for r in aggregated_rows]
            })

            st.subheader("Aggregated Streaming Data Preview")
            st.table(agg_df.to_rows(10))

            # --- Step 5: Join with YouTube Data (substring match) ---
            joined_df = agg_df.join(
                youtube_df,
                left_on="trackName",
                right_on="title",
                how="inner",
                substring=True
            )

            # --- Step 6: Manual row-by-row filter for artistName == Channel ---
            filtered_data = {col: [] for col in joined_df.columns}

            for i in range(joined_df.num_rows):
                artist = str(joined_df["artistName"][i]).strip().lower() if joined_df["artistName"][i] is not None else ""
                channel = str(joined_df["channel"][i]).strip().lower() if joined_df["channel"][i] is not None else ""

                if artist == channel:
                    for col in joined_df.columns:
                        filtered_data[col].append(joined_df[col][i])

            # Replace joined_df with the filtered version
            joined_df = dataframe.DataFrame(filtered_data)

            # --- Step 7: Display final joined data ---
            st.subheader("Joined Streaming + YouTube Data (Aggregated by Track)")
            if joined_df.num_rows == 0:
                st.warning("No matches found after filtering by artist/channel.")
            else:
                st.table(joined_df.to_rows(15))

    else:
        st.warning("📂 Please upload a file to continue.")
