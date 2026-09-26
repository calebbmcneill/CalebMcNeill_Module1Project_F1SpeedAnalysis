"""
AIPI 510 - Sourcing Data Analytics
Module 1 Project: F1 Speed Analysis
Author: Caleb McNeill
Formula 1 Speed Analysis Blog Application

Streamlit app for visualizing Formula 1 race data.
Synthesizes EDA analysis into public presentation.

"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from scipy.stats import pearsonr

DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"
COMBINED_SEASON_CSV = (
    DATA_DIRECTORY / "f1_season_data_2023_2025_combined_20260922_114820_066553.csv"
)

NUMERIC_DROP_COLUMNS = [
    "Session Key",
    "Driver Number",
    "Position",
    "Overall Time (s)",
    "Lane Duration (s)",
    "Year",
]

SELECTED_FEATURES = [
    "Adjusted Overall Time (s)",
    "Average i1 Speed (km/h)",
    "Average st Speed (km/h)",
    "Max i2 Speed (km/h)",
]


@st.cache_data
def load_season_data() -> pd.DataFrame:
    """Load and clean the combined 2023-2025 season dataset."""
    df = pd.read_csv(COMBINED_SEASON_CSV)
    df = df.dropna(subset=["Adjusted Overall Time (s)"])
    df = df.dropna(subset=["Max i2 Speed (km/h)"])
    return df


def get_numeric_df(df: pd.DataFrame) -> pd.DataFrame:
    """Return the numeric feature columns used throughout the EDA."""
    return df.select_dtypes(include="number").drop(
        columns=NUMERIC_DROP_COLUMNS, errors="ignore"
    )


@st.cache_data
def build_correlation_heatmap(numeric_df: pd.DataFrame, title: str) -> plt.Figure:
    """Build a correlation heatmap figure for the given numeric dataframe."""
    correlation_matrix = numeric_df.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        correlation_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title(title)
    ax.set_xticks(ax.get_xticks())
    ax.set_yticks(ax.get_yticks())
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    fig.tight_layout()
    return fig


def render_correlation_heatmap(numeric_df: pd.DataFrame, title: str) -> None:
    """Render a cached correlation heatmap for the given numeric dataframe."""
    st.pyplot(build_correlation_heatmap(numeric_df, title))


@st.cache_data
def build_pairplot(numeric_df: pd.DataFrame, title: str) -> plt.Figure:
    """Build a pair plot figure with Pearson p-values annotated on each panel."""
    pair_plot = sns.pairplot(
        numeric_df,
        corner=True,
        diag_kind="hist",
        plot_kws={"alpha": 0.45, "s": 18},
    )
    for row_index in range(1, len(numeric_df.columns)):
        for column_index in range(row_index):
            paired_values = numeric_df.iloc[:, [column_index, row_index]].dropna()
            if len(paired_values) >= 2:
                _, p_value = pearsonr(
                    paired_values.iloc[:, 0], paired_values.iloc[:, 1]
                )
                pair_plot.axes[row_index, column_index].text(
                    0.05,
                    0.95,
                    f"p = {p_value:.3g}",
                    transform=pair_plot.axes[row_index, column_index].transAxes,
                    ha="left",
                    va="top",
                    fontsize=9,
                )
    pair_plot.figure.suptitle(title, y=1.02)
    pair_plot.figure.text(0.5, 0.01, f"n = {len(numeric_df)}", ha="center")
    return pair_plot.figure


def render_pairplot(numeric_df: pd.DataFrame, title: str) -> None:
    """Render a cached pair plot with Pearson p-values annotated on each panel."""
    st.pyplot(build_pairplot(numeric_df, title))


@st.cache_data
def build_boxplot(numeric_df: pd.DataFrame, title: str) -> plt.Figure:
    """Build a box plot figure for the given numeric dataframe."""
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.boxplot(data=numeric_df, ax=ax)
    ax.set_title(title)
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_ylabel("Value")
    fig.tight_layout()
    return fig


def render_boxplot(numeric_df: pd.DataFrame, title: str) -> None:
    """Render a cached box plot for the given numeric dataframe."""
    st.pyplot(build_boxplot(numeric_df, title))


st.set_page_config(page_title="F1 Speed Analysis Blog", layout="wide")

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    }
    .stApp {
        background: linear-gradient(180deg, #0e1117 0%, #15181f 100%);
    }
    strong {
        font-weight: 800 !important;
        color: #ff3b3b;
    }
    h1 {
        color: #f5f5f5 !important;
        font-weight: 900 !important;
        letter-spacing: 0.5px;
        border-bottom: 4px solid #ff1e1e;
        padding-bottom: 0.4rem;
    }
    h2 {
        color: #ff1e1e !important;
        font-weight: 800 !important;
        margin-top: 2rem !important;
    }
    h3 {
        color: #f5f5f5 !important;
        font-weight: 700 !important;
        border-left: 5px solid #ff1e1e;
        padding-left: 0.6rem;
    }
    p, li, .stMarkdown {
        font-size: 1.05rem;
        line-height: 1.6;
    }
    [data-testid="stCaptionContainer"] {
        color: #9aa0a6 !important;
        font-style: italic;
    }
    div[data-testid="stImage"] img {
        border-radius: 10px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.45);
    }
    div[data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    hr {
        border-top: 2px solid #ff1e1e33;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("The Tortoise and the Hare: The Art of Speed in Formula 1 Racing")
st.subheader("A blog about understanding the basics of speed and strategy in Formula 1")
st.caption("Duke University AIPI 510: Sourcing Data for Analytics - Module 1 Project | Caleb McNeill | OpenF1 API")

st.markdown("Prolific Formula 1 driver Max Verstappen when asked by a reporter what it was like "
        "to nail the perfect lap of Suzuka (Japan F1 Race), he said: ")
st.markdown("**“If you want to drive the car, I can let you have a go. " 
            "But I think you’re gonna poop your pants.”**")

st.link_button("Read more about F1's toughest tracks", "https://www.redbull.com/us-en/f1-toughest-track-ever")

st.header("Formula 1 Racing and the Pursuit of Speed")
st.markdown(
    "From the 2023 to 2025 Formula 1 World Championship seasons, Formula 1 drivers spent an average "
        "of **1 hour, 30 minutes, and 42 seconds** driving in a championship Grand Prix race, according to "
        "open-source data from the OpenF1 API. Across every track, the lowest average value of the "
        "official fixed speed sensor data reported by OpenF1 is **247.1 km/h or 153.5 mph**. If you were "
        "driving at that speed for that amount of time on public roads, you could have left the National "
        "Mall in Washington, DC after the IndyCar Freedom 250 Grand Prix by 5 pm and made it (with time "
        "to spare but not so comfortably) to a sunset dinner on the Hudson Bay in New York City. "
        "**Intense!!!**"
        )

st.divider()

st.markdown(
    "**Speed is the essence of Formula 1 racing.** At least… that was my initial guess from someone " \
"who knows very little about the sport and motorsports in general! Thanks to open-source data from " \
"the free **OpenF1 Application Programming Interface (API)**, I broke down the most basic physics that " \
"encapsulates the heart of the racing world, but first... "
)

st.header("Why does this speed analysis matter to you?")
st.markdown(
    "The motorsports industry revolves around building vehicles that win and goes to extreme " \
        "effort to optimize performance within the constraints of the sport. By shedding light" \
        " on the data available and common assumptions that amateurs (like me) would make about" \
        " metrics that lead to performance, we can begin to confirm or deny our assumptions and " \
        "understanding of the available motorsports data and what leads to success in " \
        "motorsports. This data study will create a basic foundation of knowledge and research " \
        "to start my own preparation and potentially help others looking to start their " \
        "own careers in motorsports engineering.",
    )

st.header("The Basic Physics of Speed")
st.markdown(
    "Before diving into the data, it helps to start with the simplest equation in motion" \
    " and the fundamental quantity that Formula 1 fans care about the most: "
    "**velocity**."
)


st.latex(r"velocity (v) = \frac{distance (d)}{time (t)}")

st.markdown(
    "Every track on the F1 World Championship tour is broken into three sectors for common timing and " \
    "administrative purposes. Every speed OpenF1 reports is collected by an electric timing system " \
    "consisting of buried cables spread strategically across the track that receive radio signals from " \
    "transponders on each car. The timing loops precisely measure times within ten-thousandths " \
    "of a second or less. This allows for precise calculation of velocity: distance traveled over elapsed time, " \
    "measured at three pivotal fixed points on each track: the first intermediate sensor (i1), the second intermediate sensor "
    "(i2), and the speed trap (st) near the end of the longest straight. "
)
st.markdown(
    "**Intermediate sensor 1 (i1 Speed):** Captures speed performance gained through the " \
"first sector of the track."
)
st.markdown(
    "**Intermediate sensor 2 (i2 Speed):** Captures speed performance gained through the second " \
    "sector of the track. Usually located in one of the more challenging parts of the track."
    )
st.markdown(
    "**Speed trap (st Speed):** Captures speed performance gained through the expected" \
" highest-speed sector of the track."
)

st.markdown(
    "In the image below, you can see the sensors annoted (T) for Speed Trap, (S1) "
"for Intermediate Sensor 1, and (S2) for Intermediate Sensor 2 at the Belgian Grand Prix circuit."
)

st.image(
    str(Path(__file__).resolve().parent / "2026_Spa_Franc_Circuit_Map.png"), 
    caption="2026 Belgian Grand Prix - Spa-Francorchamps Circuit"
    )
st.caption("Source: The Fédération Internationale de l'Automobile")

st.markdown(
    "Average speeds from our data represent the typical velocity achieved by drivers in each sector, " \
    "while max speeds capture the single fastest instant recorded by that sensor. The same equation, " \
    "rearranged, is what separates a race winner from the rest of the field: for a fixed track distance," \
    " the only way to lower a driver's time, or by our variable '**Adjusted Overall Time**,' is to raise " \
    "average velocity across every sector of the lap. This is the goal for every driver on the track: " \
    "**Get the lowest time!**"
)

st.image(str(Path(__file__).resolve().parent / "velocity_controls_time.gif"))

st.markdown(
    "**Or is it more complicated than that?** Well... obviously, but at the fundamental level of the science, " \
    "higher velocities should equate to reduced times on the F1 track and therefore, winning!" \
    " There certainly has to be more to the equation and F1 teams know it, so let's explore the data to find out why.")

df = load_season_data()
numeric_df = get_numeric_df(df)

st.header("The Data Behind the Study")
st.markdown(
    "This analysis uses the OpenF1 API's combined 2023-2025 Formula 1 World Championship season "
    "dataset: one row per driver per race, with finishing position, overall race time, and six "
    "speed features captured at the Intermediate Sensor 1 (i1), Intermediate Sensor 2 (i2), and " \
    "Speed Trap (st) sensors (both average and max)."
)
st.subheader("Example Samples from the Dataset")
st.dataframe(
    df.head(10).drop(columns=["Session Key", "Session"], errors="ignore"),
    hide_index=True,
)

st.markdown(
    "I first completed a statistical analysis and exploration of an original set of **924 F1 race performances** " \
    "from the Open F1 API. In doing so, I started to see key patterns and relationships in the data, and some " \
    "interesting nuances that give insight into why **speed may not be everything in Formula 1**. Here are some " \
    "quick steps I took to clean and prepare the data for analysis:"
)

st.markdown(
    "1. I adjusted the overall race times of the drivers to subtract the time they spent in the pit "
    "lanes for maintenance from their overall speed performance (since F1 pit lanes enforce speed limits)." \
    " This gives a more accurate depiction of the time each driver spent on the track optimizing the car’s" \
    " performance. The equation is Overall Time - Pit Lane Time = Adjusted Overall Time."
)
st.markdown(
    "2. Then, I removed data anomalies and uninformative outliers caused by race cancellations and " \
    "extraordinary administrative delays."
)

st.markdown(
    "3. I narrowed the analysis to three key features " \
    "that raised the most questions and delivered the most interesting correlations with respect to our " \
    "physics lesson and the “Adjusted Overall Time.” The results are as follows:"
)

st.header("Key Findings and Interpretations")
st.subheader("2023-2025 Seasons: Correlations between our Sensor Speeds and the Adjusted Overall Time")
st.markdown(
    "The heatmap values represent the Pearson correlation coefficients between each pair of features. " \
    "Simply put, they indicate the strength and direction of their linear relationships or lack thereof. "
    "A correlation close to 1 or -1 indicates a strong linear relationship, while a correlation " \
    "near 0 suggests little to no linear relationship. By the results of all negative values, the data " \
    "indicates that higher speeds in our sensor measurements generally correspond to faster" \
    " adjusted overall race times. No surprises there."
)
st.image(str(Path(__file__).resolve().parent / "Final_Speed_Features.png"))
st.markdown(
    "But for physics being a hard science, the correlation numbers seem a little low. We know that higher"
    " speeds should equate to less time on the track... **so why aren't these correlations closer to -1?**" \
    " There are more questions to explore in the plots below!"
    )
st.subheader("2023-2025 Seasons: Speed Feature Pair Plots")
st.markdown(
    "These pair plots below provide a visual representation of every data point and the relationships " \
    "between our key speed features and the Adjusted Overall Time. " \
    "They help to identify patterns, trends, and potential outliers that may not be immediately apparent " \
    "from the correlation heatmap alone. Without surprise from our plot on the left, our drivers that maintain " \
    "the fastest top speeds at the Speed Trap (anticipated fastest part of the track) tend to have better Adjusted " \
    "Overall Times, even if the correlation is only moderate. Higher speeds through the first sector of the course also" \
    " tend to mean higher speds at the speed trap, but our correlation is getting weaker. Where my curiosity rose the most" \
    " is in the pair plots for what is called 'Cornering Speed' (in most cases measured at Intermediate Sensor 2). "
)
st.image(str(Path(__file__).resolve().parent / "Final_Speed_Feature_Pair_Plots.png"))

st.markdown(
    "Intermediate sensor 2 is often measured at one of the most technical parts of the track, and focuses on a skill " \
    "F1 teams refer to as 'cornering.' Essentially, it is the part of the track where drivers have to skillfully '" \
    "navigate a turn. Drivers are still focused on speed in cornering, but they must balance it with precision and control. " \
    "When we are in a study focused on maximizing speed, the right pair plot exemplifies a speed trade-off that starts defying" \
    "our original physics-based assumptions. **But why would less speed ever equate to higher times?** Good question. " \
    "Let's ask the Top 5 drivers from every applicable race in 2023-2025."
)

st.subheader("Top 5 Finishers: Correlation Heatmap")
st.markdown(
    "The heatmap below shows the correlations between the top 5 finishers' speed features and their Adjusted Overall Times. " \
    " Though the data sample has less points to analyze and therefore less statistical power, I chose to analyzethe Top 5 finishers" \
    " because they are generally going to have the most competitive performances throughout the duration of each race." \
    " This helps to understand how the fastest drivers optimize their performances in relation to their sensor-measured speeds"
    " and what they do when it comes time to handle the corners. From the heatmap, we can still see the general trend that" \
    " overall speed takes the cake, but less so with the cornering speeds in both average and maximum measurements."
)
st.image(str(Path(__file__).resolve().parent / "Top5_heatmap.png"))
st.markdown(
    "So we see the trand continuing with our Top 5 finishers, but as a general statistics rule, correlation does not equal causation."
    "**So what is causing these lesser correlations at Intermediate Sensor 1 and Intermediate Sensor 2?** To get a closer understanding," \
    "let's look at a specific track to better understand context in a more practical Formula 1 setting."
)

st.subheader("Track Spotlight: Circuit de Spa-Francorchamps, The Belgian Grand Prix")
st.markdown(
    "The heatmap below focuses on the Spa-Francorchamps track (depicted earlier in the article) between the 2023-2026 races, highlighting the correlations " \
    "between speed features and adjusted overall times for this specific circuit. I chose Spa-Francorchamps" \
    "because it is one of the most challenging, iconic, and historic tracks in the Formula 1 calendar. " \
    "Even though the data sample set is down to 56 performances, this allows us to see how performance at " \
    "In the data at Spa, we really see where the rubber meets the road... hopefully you can keep reading after that one."
)

st.image(str(Path(__file__).resolve().parent / "Spa_Franc_heatmap.png"))

st.markdown(
    "As we zoom in on specific aspects of performance, such as corner handling at Intermediate Sensor 2, we gain a more " \
    "granular understanding of how drivers navigate the track. Average sector speed throughout the track still produces" \
    "lower average times, but max speeds tell a much different story. The corners at Intermediate Sensor 2 are so challenging" \
    "that the correlation between Max Sector 2 Speed and overall performance is surprisingly low and even has the opposite effect" \
    "at times from our underlying physics priciples of speed. The image below illustrates Oscar Piastri, the leading" \
    "driver at Lap 42 of 44 handling the menacing Turns 14 and 15. The image provides a closer look at how specific speed " \
    "features manifest in real track conditions. Notice how the drivers have clearly defined a racing line that veers " \
    "almost completely off the track. Piastri, however, sucessfully controls his own line precisely **inside** " \
    "the established racing line throughout the corner, maintaining track traction, ensuring optimal performance."
)
st.image(str(Path(__file__).resolve().parent / "Spa_i2_sensor_distance.png"), 
         caption="Oscar Piastri's Corner handling at Intermediate Sensor 2")
st.caption("Source: ESPN F1 https://youtu.be/1oXuRgRynR4?t=1344")
st.markdown(
    "**What did we just observe?** We observed a new hypothesis challenging our analysis model's earlier assumption about F1 racing: " \
    "that **the distance drivers drive in a F1 race is NOT fixed in an F1 race** and therefore negigible compared to the impact " \
    "of speed. In this year's 2026 F1 season, the winner of Spa-Francorchamps, Kimi Antonelli drove on average up to 4 km/h slower" \
    " than Charles Leclerc in the second place finish of the same race. With two important car telemetry stats from another free open-source "
    " F1 data repository, the **FastF1** Python library, " \
    "we see that **Antonelli drove almost 0.8 km less than Charles Leclerc. Leclerc started only meters behind Antonelli" \
    " and drove up to 4 km/h faster on average, but still lost to Antonelli by two seconds.** These are only two data points" \
    " and not enough to draw conclusions now, but it certainly opens the door for further investigation. This is where the " \
    "art of racing emerges out of the confines of the hard science of physics. The weather at that race as well as the year before" \
    " yielded heavy rains prior to the race making track conditions more difficult to negotiate. This also impacts tire management" \
    "strategies and overall race performance, adding another layer of complexity to our analysis. Drivers had to slow speeds" \
    " to maintain traction but maintain enough downforce and speed to remain competitive." \
    " **Speed is clearly a critical factor, but it is clearly not the only one.**" \
    " The following section establishes new research questions that arose from our analysis, " \
    "guiding future investigations into motorsports performance."
)

st.header("New Research Questions")
st.markdown(
    "To continue understanding motorsports and racing on a deeper level, we need to understand many more questions" \
    "this study uncovered:"
)
st.subheader("What other factors influence performance other than speed?")
st.subheader("How does a driver's ability to minimize the distance driven on the track balance with their need for speed?")
st.subheader("How do factors outside of our simple speed-focused analysis come into play?")
st.divider()
st.markdown(
    "This data cannot quite speak to these questions yet, but at least we are now **getting up to speed!**"
)