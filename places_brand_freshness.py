import streamlit as st
from read_data import read_from_gsheets
import altair as alt
from datetime import datetime, timedelta
import pandas as pd
import streamlit.components.v1 as components



st.set_page_config(
    page_title="Places Summary Statistics - Brands Freshness",
    layout="wide"
)
### Brand Freshness ####
# raw df
brand_freshness_grouped_df = read_from_gsheets("Brand freshness grouped")
numeric_columns = ['brand_count', 'country_brand_count', 'pct_of_brands', 'tidy_country_rank', 'country_poi_count']
brand_freshness_grouped_df[numeric_columns] = brand_freshness_grouped_df[numeric_columns].apply(pd.to_numeric)
brand_freshness_grouped_df['pct_of_brands'] = brand_freshness_grouped_df['pct_of_brands'] * 100

# pivoted table
reshaped_df = brand_freshness_grouped_df.pivot(index='tidy_country_code', columns='file_age_range', values='pct_of_brands')
reshaped_df = reshaped_df.reset_index()

# brand totals by country
brand_totals_df = brand_freshness_grouped_df.groupby(['tidy_country_code', 'tidy_country_rank']).agg({'brand_count': 'sum'}).reset_index()

# joined table
joined_df = pd.merge(brand_totals_df, reshaped_df, on='tidy_country_code', how='inner')
column_order = ['tidy_country_code', 'tidy_country_rank', 'brand_count', '0-30d', '31-60d', '61-90d', '91-120d', '120d+']
joined_df = joined_df[column_order].sort_values(by='tidy_country_rank', ascending=True).reset_index(drop=True)
joined_df["% of brand freshness < 30 days"] = joined_df["0-30d"]
joined_df["% of brand freshness < 60 days"] = joined_df["0-30d"] + joined_df["31-60d"]
joined_df["% of brand freshness < 90 days"] = joined_df["% of brand freshness < 60 days"] + joined_df["61-90d"]
joined_df = joined_df[["tidy_country_code", "brand_count", "% of brand freshness < 30 days", "% of brand freshness < 60 days", "% of brand freshness < 90 days"]]
joined_df = joined_df.rename(columns={"tidy_country_code": "Country Code", "brand_count": "Distinct Brand Count"})

joined_df_styled = (
    joined_df.style
    .apply(lambda x: ['background-color: #D7E8ED' if i % 2 == 0 else '' for i in range(len(x))], axis=0)
    .format({
        "Distinct Brand Count": "{:,.0f}",
        "% of brand freshness < 30 days": "{:.1f}%",
        "% of brand freshness < 60 days": "{:.1f}%",
        "% of brand freshness < 90 days": "{:.1f}%",
    })
)

st.dataframe(joined_df_styled, hide_index=True)

#### Brand Freshness Top 30 ####
brand_freshness_30_df = read_from_gsheets("Brand freshness")[
    ["iso_country_code", "file_age_range", "country_poi_count", "pct_of_brands"]
]
brand_freshness_30_df["country_poi_count"] = pd.to_numeric(brand_freshness_30_df["country_poi_count"])
brand_freshness_30_df["pct_of_brands"] = pd.to_numeric(brand_freshness_30_df["pct_of_brands"])
brand_freshness_30_df["pct_of_brands_rounded"] = round(brand_freshness_30_df["pct_of_brands"],4)
brand_freshness_30_df["pct_of_brands"] *= 100

top_30_unique = (
    brand_freshness_30_df.sort_values("country_poi_count", ascending=False)["country_poi_count"]
    .unique()[:30]
)

brand_freshness_30_df = brand_freshness_30_df[
    brand_freshness_30_df["country_poi_count"].isin(top_30_unique)
]

brand_freshness_30_df["iso_country_code"] = pd.Categorical(
    brand_freshness_30_df["iso_country_code"],
    categories=brand_freshness_30_df["iso_country_code"].unique(),
    ordered=True,
)

brand_freshness_30_df = brand_freshness_30_df.sort_values(by='country_poi_count', ascending=False)

brand_freshness_30_df.rename(
    columns={
        "iso_country_code": "Country Code",
        "file_age_range": "File Age Range",
        "pct_of_brands": "Percent of Brands",
    },
    inplace=True,
)

freshness_list = ['120d+', '91-120d', '61-90d', '31-60d', '0-30d'] 
brand_freshness_30_df['Order'] = brand_freshness_30_df['File Age Range'].map({value: index for index, value in enumerate(freshness_list)})
y_range = [0, 100]


brand_freshness_30 = alt.Chart(brand_freshness_30_df).mark_bar().encode(
    x=alt.X('Country Code', sort=None, title=None),
      y=alt.Y('Percent of Brands:Q', scale=alt.Scale(domain=y_range)),
    color=alt.Color('File Age Range:N', scale=alt.Scale(domain=freshness_list)),
    order = alt.Order('Order:O', sort = 'descending'),
    tooltip=[alt.Tooltip('Country Code'),
             alt.Tooltip('pct_of_brands_rounded', format = ",.2%", title="Percent of Brands"),
             alt.Tooltip('File Age Range')]
).properties(
    width=800,
    height=400
).configure_axisX(
    labelFontSize=10,  # Set the font size of x-axis labels
    labelAngle=0
)

st.write("Brand Freshness - Top 30 Countries by Branded POI Count")
st.altair_chart(brand_freshness_30,use_container_width=True)


hide_streamlit_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden;}
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

css = '''
<style>
section.main > div:has(~ footer ) {
     padding-top: 0px;
    padding-bottom: 0px;
}

[data-testid="ScrollToBottomContainer"] {
    overflow: hidden;
}
</style>
'''

st.markdown(css, unsafe_allow_html=True)

# Keep-alive comment: 2025-04-25 16:08:51.997462
# Keep-alive comment: 2025-04-25 16:18:49.533049
# Keep-alive comment: 2025-04-26 00:24:24.366870
# Keep-alive comment: 2025-04-26 11:24:18.750588
# Keep-alive comment: 2025-04-26 22:23:18.283397
# Keep-alive comment: 2025-04-27 09:23:49.356818
# Keep-alive comment: 2025-04-27 20:23:44.167763
# Keep-alive comment: 2025-04-28 07:24:21.682476
# Keep-alive comment: 2025-04-28 18:24:34.669966
# Keep-alive comment: 2025-04-29 05:24:03.769550
# Keep-alive comment: 2025-04-29 16:24:49.070664
# Keep-alive comment: 2025-04-30 03:23:38.777305
# Keep-alive comment: 2025-04-30 14:24:08.070061
# Keep-alive comment: 2025-05-01 01:24:18.494194
# Keep-alive comment: 2025-05-01 12:23:49.980698
# Keep-alive comment: 2025-05-01 23:23:22.874603
# Keep-alive comment: 2025-05-02 10:24:09.283075
# Keep-alive comment: 2025-05-02 21:23:20.464631
# Keep-alive comment: 2025-05-03 08:23:44.470323
# Keep-alive comment: 2025-05-03 19:24:02.685048
# Keep-alive comment: 2025-05-04 06:24:08.459858
# Keep-alive comment: 2025-05-04 17:23:17.403281
# Keep-alive comment: 2025-05-05 04:24:28.244343
# Keep-alive comment: 2025-05-05 15:23:47.915317
# Keep-alive comment: 2025-05-06 02:24:38.360248
# Keep-alive comment: 2025-05-06 13:23:40.870338
# Keep-alive comment: 2025-05-07 00:23:39.129564
# Keep-alive comment: 2025-05-07 11:23:51.870187
# Keep-alive comment: 2025-05-07 22:23:50.445403
# Keep-alive comment: 2025-05-08 09:23:59.048235
# Keep-alive comment: 2025-05-08 20:23:51.256320
# Keep-alive comment: 2025-05-09 07:24:01.873969
# Keep-alive comment: 2025-05-09 18:24:13.723025
# Keep-alive comment: 2025-05-10 05:23:56.126245
# Keep-alive comment: 2025-05-10 16:23:43.398718
# Keep-alive comment: 2025-05-11 03:23:42.040790
# Keep-alive comment: 2025-05-11 14:23:33.520275
# Keep-alive comment: 2025-05-12 01:23:39.586022
# Keep-alive comment: 2025-05-12 12:24:10.237020
# Keep-alive comment: 2025-05-12 23:23:42.654434
# Keep-alive comment: 2025-05-13 10:24:47.103161
# Keep-alive comment: 2025-05-13 21:23:43.801259
# Keep-alive comment: 2025-05-14 08:24:14.286028
# Keep-alive comment: 2025-05-14 19:24:14.074522
# Keep-alive comment: 2025-05-15 06:24:11.014694
# Keep-alive comment: 2025-05-15 17:24:41.805445
# Keep-alive comment: 2025-05-16 04:23:55.501532
# Keep-alive comment: 2025-05-16 15:22:59.476943
# Keep-alive comment: 2025-05-17 02:23:16.369714
# Keep-alive comment: 2025-05-17 13:24:00.150532
# Keep-alive comment: 2025-05-18 00:23:14.466596
# Keep-alive comment: 2025-05-18 11:23:46.023317
# Keep-alive comment: 2025-05-18 22:23:40.335542
# Keep-alive comment: 2025-05-19 09:24:17.858537
# Keep-alive comment: 2025-05-19 20:23:16.334050
# Keep-alive comment: 2025-05-20 07:23:32.334557
# Keep-alive comment: 2025-05-20 18:24:44.519109
# Keep-alive comment: 2025-05-21 05:23:15.689090
# Keep-alive comment: 2025-05-21 16:23:25.315967
# Keep-alive comment: 2025-05-22 03:23:19.409559
# Keep-alive comment: 2025-05-22 14:23:24.022145
# Keep-alive comment: 2025-05-23 01:23:22.094587
# Keep-alive comment: 2025-05-23 12:23:22.323537
# Keep-alive comment: 2025-05-23 23:23:25.615226
# Keep-alive comment: 2025-05-24 10:23:23.337039
# Keep-alive comment: 2025-05-24 21:23:19.837720
# Keep-alive comment: 2025-05-25 08:23:20.700916
# Keep-alive comment: 2025-05-25 19:23:25.732472
# Keep-alive comment: 2025-05-26 06:23:13.291683
# Keep-alive comment: 2025-05-26 17:23:15.218614
# Keep-alive comment: 2025-05-27 04:23:21.121849
# Keep-alive comment: 2025-05-27 15:23:26.001283
# Keep-alive comment: 2025-05-28 02:23:35.010563
# Keep-alive comment: 2025-05-28 13:23:26.809510
# Keep-alive comment: 2025-05-29 00:23:18.802407
# Keep-alive comment: 2025-05-29 11:23:14.876924
# Keep-alive comment: 2025-05-29 22:23:28.172114
# Keep-alive comment: 2025-05-30 09:23:13.895813
# Keep-alive comment: 2025-05-30 20:23:14.605303
# Keep-alive comment: 2025-05-31 07:23:26.464156
# Keep-alive comment: 2025-05-31 18:23:21.080817
# Keep-alive comment: 2025-06-01 05:23:20.540566
# Keep-alive comment: 2025-06-01 16:23:33.346366
# Keep-alive comment: 2025-06-02 03:23:34.559756
# Keep-alive comment: 2025-06-02 14:23:26.362369
# Keep-alive comment: 2025-06-03 01:23:16.116161
# Keep-alive comment: 2025-06-03 12:23:31.472488
# Keep-alive comment: 2025-06-03 23:23:27.687351
# Keep-alive comment: 2025-06-04 10:23:25.943461
# Keep-alive comment: 2025-06-04 21:23:05.008860
# Keep-alive comment: 2025-06-05 08:23:28.521089
# Keep-alive comment: 2025-06-05 19:23:19.363491
# Keep-alive comment: 2025-06-06 06:23:16.303134
# Keep-alive comment: 2025-06-06 17:22:59.194482
# Keep-alive comment: 2025-06-07 04:23:01.067978
# Keep-alive comment: 2025-06-07 15:23:09.904891
# Keep-alive comment: 2025-06-08 02:23:15.001567
# Keep-alive comment: 2025-06-08 13:23:16.456294
# Keep-alive comment: 2025-06-09 00:22:59.123883
# Keep-alive comment: 2025-06-09 11:23:14.593183
# Keep-alive comment: 2025-06-09 22:23:23.462005
# Keep-alive comment: 2025-06-10 09:23:26.501431
# Keep-alive comment: 2025-06-10 20:23:19.068365
# Keep-alive comment: 2025-06-11 07:23:20.488628
# Keep-alive comment: 2025-06-11 18:25:10.289049
# Keep-alive comment: 2025-06-12 05:23:17.455382
# Keep-alive comment: 2025-06-12 16:23:21.092106
# Keep-alive comment: 2025-06-13 03:23:21.605372
# Keep-alive comment: 2025-06-13 14:23:11.324711
# Keep-alive comment: 2025-06-14 01:23:31.481283
# Keep-alive comment: 2025-06-14 12:23:17.484309
# Keep-alive comment: 2025-06-14 23:23:08.725709
# Keep-alive comment: 2025-06-15 10:22:55.517279
# Keep-alive comment: 2025-06-15 21:23:29.571050
# Keep-alive comment: 2025-06-16 08:23:26.973201
# Keep-alive comment: 2025-06-16 19:23:10.918878
# Keep-alive comment: 2025-06-17 06:23:47.577092
# Keep-alive comment: 2025-06-17 17:23:15.718509
# Keep-alive comment: 2025-06-18 04:23:21.540978
# Keep-alive comment: 2025-06-18 15:23:22.309925
# Keep-alive comment: 2025-06-19 02:23:19.221802
# Keep-alive comment: 2025-06-19 13:23:19.877554
# Keep-alive comment: 2025-06-20 00:23:15.499801
# Keep-alive comment: 2025-06-20 11:24:04.975607
# Keep-alive comment: 2025-06-20 22:23:24.059058
# Keep-alive comment: 2025-06-21 09:23:09.359318
# Keep-alive comment: 2025-06-21 20:23:21.613114