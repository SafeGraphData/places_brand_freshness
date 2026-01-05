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
# Keep-alive comment: 2025-06-22 07:23:14.074432
# Keep-alive comment: 2025-06-22 18:23:05.075744
# Keep-alive comment: 2025-06-23 05:23:21.304306
# Keep-alive comment: 2025-06-23 16:23:15.690689
# Keep-alive comment: 2025-06-24 03:23:21.624609
# Keep-alive comment: 2025-06-24 14:23:02.201535
# Keep-alive comment: 2025-06-25 01:22:55.213553
# Keep-alive comment: 2025-06-25 12:23:17.822268
# Keep-alive comment: 2025-06-25 23:23:19.911674
# Keep-alive comment: 2025-06-26 10:23:27.433245
# Keep-alive comment: 2025-06-26 21:24:52.276408
# Keep-alive comment: 2025-06-27 08:23:20.357600
# Keep-alive comment: 2025-06-27 19:23:17.176270
# Keep-alive comment: 2025-06-28 06:23:23.462513
# Keep-alive comment: 2025-06-28 17:23:13.560678
# Keep-alive comment: 2025-06-29 04:23:03.248202
# Keep-alive comment: 2025-06-29 15:22:53.321211
# Keep-alive comment: 2025-06-30 02:23:14.675991
# Keep-alive comment: 2025-06-30 13:22:57.773458
# Keep-alive comment: 2025-07-01 00:25:01.128078
# Keep-alive comment: 2025-07-01 11:23:17.177885
# Keep-alive comment: 2025-07-01 22:23:20.709280
# Keep-alive comment: 2025-07-02 09:23:15.184807
# Keep-alive comment: 2025-07-02 20:25:04.439542
# Keep-alive comment: 2025-07-03 07:23:29.631272
# Keep-alive comment: 2025-07-03 18:22:56.682247
# Keep-alive comment: 2025-07-04 05:23:18.666572
# Keep-alive comment: 2025-07-04 16:23:14.104171
# Keep-alive comment: 2025-07-05 03:23:13.269320
# Keep-alive comment: 2025-07-05 14:23:17.628638
# Keep-alive comment: 2025-07-06 01:23:15.765890
# Keep-alive comment: 2025-07-06 12:23:12.009257
# Keep-alive comment: 2025-07-06 23:23:14.017323
# Keep-alive comment: 2025-07-07 10:23:15.351762
# Keep-alive comment: 2025-07-07 21:23:14.245024
# Keep-alive comment: 2025-07-08 08:23:18.238371
# Keep-alive comment: 2025-07-08 19:23:14.895190
# Keep-alive comment: 2025-07-09 06:23:24.710250
# Keep-alive comment: 2025-07-09 17:23:58.577392
# Keep-alive comment: 2025-07-10 04:23:13.389985
# Keep-alive comment: 2025-07-10 15:23:20.780036
# Keep-alive comment: 2025-07-11 02:23:12.311698
# Keep-alive comment: 2025-07-11 13:23:13.862372
# Keep-alive comment: 2025-07-12 00:22:59.623400
# Keep-alive comment: 2025-07-12 11:23:17.373203
# Keep-alive comment: 2025-07-12 22:23:13.215438
# Keep-alive comment: 2025-07-13 09:23:13.103311
# Keep-alive comment: 2025-07-13 20:22:57.789594
# Keep-alive comment: 2025-07-14 07:23:11.521253
# Keep-alive comment: 2025-07-14 18:23:34.577050
# Keep-alive comment: 2025-07-15 05:23:24.733532
# Keep-alive comment: 2025-07-15 16:23:19.223776
# Keep-alive comment: 2025-07-16 03:23:18.173231
# Keep-alive comment: 2025-07-16 14:23:20.096780
# Keep-alive comment: 2025-07-17 01:23:13.747157
# Keep-alive comment: 2025-07-17 12:23:20.840741
# Keep-alive comment: 2025-07-17 23:23:11.712679
# Keep-alive comment: 2025-07-18 10:23:34.196792
# Keep-alive comment: 2025-07-18 21:23:13.542301
# Keep-alive comment: 2025-07-19 08:23:53.297473
# Keep-alive comment: 2025-07-19 19:22:58.489456
# Keep-alive comment: 2025-07-20 06:23:22.651914
# Keep-alive comment: 2025-07-20 17:23:28.869354
# Keep-alive comment: 2025-07-21 04:23:23.705844
# Keep-alive comment: 2025-07-21 15:23:11.670005
# Keep-alive comment: 2025-07-22 02:23:32.912211
# Keep-alive comment: 2025-07-22 13:23:47.597298
# Keep-alive comment: 2025-07-23 00:23:20.038504
# Keep-alive comment: 2025-07-23 11:23:10.963748
# Keep-alive comment: 2025-07-23 22:23:12.862609
# Keep-alive comment: 2025-07-24 09:23:30.399048
# Keep-alive comment: 2025-07-24 20:23:15.499423
# Keep-alive comment: 2025-07-25 07:23:10.551276
# Keep-alive comment: 2025-07-25 18:23:15.749735
# Keep-alive comment: 2025-07-26 05:23:08.433014
# Keep-alive comment: 2025-07-26 16:23:14.593496
# Keep-alive comment: 2025-07-27 03:23:08.922572
# Keep-alive comment: 2025-07-27 14:22:58.653224
# Keep-alive comment: 2025-07-28 01:23:20.924182
# Keep-alive comment: 2025-07-28 12:23:16.753237
# Keep-alive comment: 2025-07-28 23:23:20.102854
# Keep-alive comment: 2025-07-29 10:22:49.695914
# Keep-alive comment: 2025-07-29 21:23:19.792099
# Keep-alive comment: 2025-07-30 08:23:16.352009
# Keep-alive comment: 2025-07-30 19:23:25.371798
# Keep-alive comment: 2025-07-31 06:23:29.182387
# Keep-alive comment: 2025-07-31 17:23:15.310249
# Keep-alive comment: 2025-08-01 04:23:12.920034
# Keep-alive comment: 2025-08-01 15:23:25.254631
# Keep-alive comment: 2025-08-02 02:23:08.033707
# Keep-alive comment: 2025-08-02 13:23:18.805112
# Keep-alive comment: 2025-08-03 00:23:14.140551
# Keep-alive comment: 2025-08-03 11:23:19.731117
# Keep-alive comment: 2025-08-03 22:23:14.648663
# Keep-alive comment: 2025-08-04 09:23:12.082755
# Keep-alive comment: 2025-08-04 20:23:16.919272
# Keep-alive comment: 2025-08-05 07:23:19.897177
# Keep-alive comment: 2025-08-05 18:23:21.479827
# Keep-alive comment: 2025-08-06 05:23:14.928902
# Keep-alive comment: 2025-08-06 16:25:05.957837
# Keep-alive comment: 2025-08-07 03:23:18.076412
# Keep-alive comment: 2025-08-07 14:23:21.154053
# Keep-alive comment: 2025-08-08 01:23:09.225081
# Keep-alive comment: 2025-08-08 12:23:21.131429
# Keep-alive comment: 2025-08-08 23:23:21.332205
# Keep-alive comment: 2025-08-09 10:23:13.868564
# Keep-alive comment: 2025-08-09 21:23:36.300391
# Keep-alive comment: 2025-08-10 08:23:20.178030
# Keep-alive comment: 2025-08-10 19:23:20.012857
# Keep-alive comment: 2025-08-11 06:23:14.720125
# Keep-alive comment: 2025-08-11 17:23:22.065054
# Keep-alive comment: 2025-08-12 04:23:21.081324
# Keep-alive comment: 2025-08-12 15:23:13.387491
# Keep-alive comment: 2025-08-13 02:23:20.465875
# Keep-alive comment: 2025-08-13 13:23:18.925610
# Keep-alive comment: 2025-08-14 00:23:14.013930
# Keep-alive comment: 2025-08-14 11:23:22.098453
# Keep-alive comment: 2025-08-14 22:23:15.212485
# Keep-alive comment: 2025-08-15 09:23:14.837088
# Keep-alive comment: 2025-08-15 20:23:04.355327
# Keep-alive comment: 2025-08-16 07:23:28.966186
# Keep-alive comment: 2025-08-16 18:23:15.565321
# Keep-alive comment: 2025-08-17 05:23:17.773649
# Keep-alive comment: 2025-08-17 16:23:13.469331
# Keep-alive comment: 2025-08-18 03:23:16.016096
# Keep-alive comment: 2025-08-18 14:23:17.740599
# Keep-alive comment: 2025-08-19 01:23:15.495222
# Keep-alive comment: 2025-08-19 12:23:22.036860
# Keep-alive comment: 2025-08-19 23:23:42.503965
# Keep-alive comment: 2025-08-20 10:23:18.664816
# Keep-alive comment: 2025-08-20 21:23:20.524303
# Keep-alive comment: 2025-08-21 08:23:17.061069
# Keep-alive comment: 2025-08-21 19:23:22.597646
# Keep-alive comment: 2025-08-22 06:23:20.450856
# Keep-alive comment: 2025-08-22 17:23:15.829739
# Keep-alive comment: 2025-08-23 04:23:24.165206
# Keep-alive comment: 2025-08-23 15:23:13.600915
# Keep-alive comment: 2025-08-24 02:23:13.058141
# Keep-alive comment: 2025-08-24 13:23:15.239466
# Keep-alive comment: 2025-08-25 00:23:20.675317
# Keep-alive comment: 2025-08-25 11:23:21.180241
# Keep-alive comment: 2025-08-25 22:23:15.434959
# Keep-alive comment: 2025-08-26 09:23:17.896329
# Keep-alive comment: 2025-08-26 20:23:21.382078
# Keep-alive comment: 2025-08-27 07:23:25.937521
# Keep-alive comment: 2025-08-27 18:22:55.553524
# Keep-alive comment: 2025-08-28 05:23:26.010856
# Keep-alive comment: 2025-08-28 16:23:16.222887
# Keep-alive comment: 2025-08-29 03:22:59.101825
# Keep-alive comment: 2025-08-29 14:23:07.148537
# Keep-alive comment: 2025-08-30 01:23:04.015494
# Keep-alive comment: 2025-08-30 12:23:00.039006
# Keep-alive comment: 2025-08-30 23:23:03.355113
# Keep-alive comment: 2025-08-31 10:22:59.339320
# Keep-alive comment: 2025-08-31 21:23:10.865955
# Keep-alive comment: 2025-09-01 08:23:15.723715
# Keep-alive comment: 2025-09-01 19:23:11.204088
# Keep-alive comment: 2025-09-02 06:23:00.563862
# Keep-alive comment: 2025-09-02 17:23:12.267438
# Keep-alive comment: 2025-09-03 04:23:03.604646
# Keep-alive comment: 2025-09-03 15:23:07.559325
# Keep-alive comment: 2025-09-04 02:23:08.294397
# Keep-alive comment: 2025-09-04 13:23:20.499721
# Keep-alive comment: 2025-09-05 00:22:59.718000
# Keep-alive comment: 2025-09-05 11:22:56.112636
# Keep-alive comment: 2025-09-05 22:23:05.178309
# Keep-alive comment: 2025-09-06 09:23:00.491130
# Keep-alive comment: 2025-09-06 20:22:59.754302
# Keep-alive comment: 2025-09-07 07:23:04.773105
# Keep-alive comment: 2025-09-07 18:23:04.966038
# Keep-alive comment: 2025-09-08 05:23:00.879959
# Keep-alive comment: 2025-09-08 16:23:08.348509
# Keep-alive comment: 2025-09-09 03:23:33.068516
# Keep-alive comment: 2025-09-09 14:23:08.760532
# Keep-alive comment: 2025-09-10 01:22:59.210747
# Keep-alive comment: 2025-09-10 12:23:12.620641
# Keep-alive comment: 2025-09-10 23:23:00.689619
# Keep-alive comment: 2025-09-11 10:23:03.422108
# Keep-alive comment: 2025-09-11 21:23:00.542015
# Keep-alive comment: 2025-09-12 08:23:16.151502
# Keep-alive comment: 2025-09-12 19:23:06.699146
# Keep-alive comment: 2025-09-13 06:22:53.314480
# Keep-alive comment: 2025-09-13 17:22:59.624640
# Keep-alive comment: 2025-09-14 04:22:49.802060
# Keep-alive comment: 2025-09-14 15:23:01.334100
# Keep-alive comment: 2025-09-15 02:22:58.967479
# Keep-alive comment: 2025-09-15 13:23:03.081605
# Keep-alive comment: 2025-09-16 00:23:00.497790
# Keep-alive comment: 2025-09-16 11:23:06.588323
# Keep-alive comment: 2025-09-16 22:22:59.616082
# Keep-alive comment: 2025-09-17 09:23:03.221497
# Keep-alive comment: 2025-09-17 20:23:12.274958
# Keep-alive comment: 2025-09-18 07:23:07.673710
# Keep-alive comment: 2025-09-18 18:23:07.476888
# Keep-alive comment: 2025-09-19 05:23:01.652030
# Keep-alive comment: 2025-09-19 16:23:37.070182
# Keep-alive comment: 2025-09-20 03:23:04.446236
# Keep-alive comment: 2025-09-20 14:23:06.224210
# Keep-alive comment: 2025-09-21 01:23:06.091136
# Keep-alive comment: 2025-09-21 12:23:06.175681
# Keep-alive comment: 2025-09-21 23:23:01.057315
# Keep-alive comment: 2025-09-22 10:23:05.024599
# Keep-alive comment: 2025-09-22 21:23:00.724737
# Keep-alive comment: 2025-09-23 08:23:03.821872
# Keep-alive comment: 2025-09-23 19:23:09.736703
# Keep-alive comment: 2025-09-24 06:23:01.558827
# Keep-alive comment: 2025-09-24 17:23:08.538367
# Keep-alive comment: 2025-09-25 04:27:28.606429
# Keep-alive comment: 2025-09-25 15:23:12.980841
# Keep-alive comment: 2025-09-26 02:23:07.052307
# Keep-alive comment: 2025-09-26 13:23:11.759713
# Keep-alive comment: 2025-09-26 19:31:38.984362
# Keep-alive comment: 2025-09-27 05:31:42.696106
# Keep-alive comment: 2025-09-27 15:31:38.018465
# Keep-alive comment: 2025-09-28 01:31:42.288468
# Keep-alive comment: 2025-09-28 11:31:43.389290
# Keep-alive comment: 2025-09-28 21:31:43.097295
# Keep-alive comment: 2025-09-29 07:31:50.015692
# Keep-alive comment: 2025-09-29 17:31:59.220180
# Keep-alive comment: 2025-09-30 03:31:37.370810
# Keep-alive comment: 2025-09-30 13:31:45.441188
# Keep-alive comment: 2025-09-30 23:32:02.157423
# Keep-alive comment: 2025-10-01 09:32:11.280534
# Keep-alive comment: 2025-10-01 19:31:43.710293
# Keep-alive comment: 2025-10-02 05:32:11.442540
# Keep-alive comment: 2025-10-02 15:32:10.146905
# Keep-alive comment: 2025-10-03 01:31:42.229988
# Keep-alive comment: 2025-10-03 11:32:03.531695
# Keep-alive comment: 2025-10-03 21:31:38.219260
# Keep-alive comment: 2025-10-04 07:31:36.959094
# Keep-alive comment: 2025-10-04 17:31:47.855157
# Keep-alive comment: 2025-10-05 03:31:41.401819
# Keep-alive comment: 2025-10-05 13:31:46.624712
# Keep-alive comment: 2025-10-05 23:32:07.706281
# Keep-alive comment: 2025-10-06 09:32:13.859590
# Keep-alive comment: 2025-10-06 19:31:48.497676
# Keep-alive comment: 2025-10-07 05:31:44.930739
# Keep-alive comment: 2025-10-07 15:32:07.737146
# Keep-alive comment: 2025-10-08 01:31:43.332367
# Keep-alive comment: 2025-10-08 11:31:45.117068
# Keep-alive comment: 2025-10-08 21:31:44.055443
# Keep-alive comment: 2025-10-09 07:31:47.480044
# Keep-alive comment: 2025-10-09 17:31:47.863962
# Keep-alive comment: 2025-10-10 03:31:33.187177
# Keep-alive comment: 2025-10-10 13:31:26.714340
# Keep-alive comment: 2025-10-10 23:31:37.598730
# Keep-alive comment: 2025-10-11 09:31:43.347365
# Keep-alive comment: 2025-10-11 19:31:37.114882
# Keep-alive comment: 2025-10-12 05:31:40.308673
# Keep-alive comment: 2025-10-12 15:31:46.286450
# Keep-alive comment: 2025-10-13 01:31:40.265753
# Keep-alive comment: 2025-10-13 11:32:11.798795
# Keep-alive comment: 2025-10-13 21:31:34.533404
# Keep-alive comment: 2025-10-14 07:31:38.383595
# Keep-alive comment: 2025-10-14 17:31:41.676540
# Keep-alive comment: 2025-10-15 03:31:38.188813
# Keep-alive comment: 2025-10-15 13:31:42.432410
# Keep-alive comment: 2025-10-15 23:31:44.507243
# Keep-alive comment: 2025-10-16 09:31:41.586430
# Keep-alive comment: 2025-10-16 19:31:47.964358
# Keep-alive comment: 2025-10-17 05:31:45.399431
# Keep-alive comment: 2025-10-17 15:32:02.818571
# Keep-alive comment: 2025-10-18 01:31:39.163881
# Keep-alive comment: 2025-10-18 11:32:03.816771
# Keep-alive comment: 2025-10-18 21:32:13.426911
# Keep-alive comment: 2025-10-19 07:31:32.951485
# Keep-alive comment: 2025-10-19 17:32:08.472717
# Keep-alive comment: 2025-10-20 03:32:07.019983
# Keep-alive comment: 2025-10-20 13:31:47.176924
# Keep-alive comment: 2025-10-20 23:31:39.737103
# Keep-alive comment: 2025-10-21 09:31:46.396378
# Keep-alive comment: 2025-10-21 19:33:47.890223
# Keep-alive comment: 2025-10-22 05:31:40.401890
# Keep-alive comment: 2025-10-22 15:32:47.477050
# Keep-alive comment: 2025-10-23 01:31:40.679980
# Keep-alive comment: 2025-10-23 11:31:52.632209
# Keep-alive comment: 2025-10-23 21:31:42.216767
# Keep-alive comment: 2025-10-24 07:33:00.563866
# Keep-alive comment: 2025-10-24 17:31:50.707452
# Keep-alive comment: 2025-10-25 03:31:43.464987
# Keep-alive comment: 2025-10-25 13:32:07.231815
# Keep-alive comment: 2025-10-25 23:31:39.921637
# Keep-alive comment: 2025-10-26 09:31:32.700015
# Keep-alive comment: 2025-10-26 19:32:10.080181
# Keep-alive comment: 2025-10-27 05:31:49.707772
# Keep-alive comment: 2025-10-27 15:32:07.824748
# Keep-alive comment: 2025-10-28 01:31:43.183624
# Keep-alive comment: 2025-10-28 11:31:45.831772
# Keep-alive comment: 2025-10-28 21:31:34.056938
# Keep-alive comment: 2025-10-29 07:31:40.445788
# Keep-alive comment: 2025-10-29 17:31:50.329743
# Keep-alive comment: 2025-10-30 03:31:39.872399
# Keep-alive comment: 2025-10-30 13:32:13.120950
# Keep-alive comment: 2025-10-30 23:31:45.179794
# Keep-alive comment: 2025-10-31 09:33:00.019230
# Keep-alive comment: 2025-10-31 19:31:34.939299
# Keep-alive comment: 2025-11-01 05:31:43.449106
# Keep-alive comment: 2025-11-01 15:31:32.092537
# Keep-alive comment: 2025-11-02 01:31:44.694800
# Keep-alive comment: 2025-11-02 11:31:44.998101
# Keep-alive comment: 2025-11-02 21:31:59.132177
# Keep-alive comment: 2025-11-03 07:31:40.985956
# Keep-alive comment: 2025-11-03 17:31:47.304913
# Keep-alive comment: 2025-11-04 03:31:46.230193
# Keep-alive comment: 2025-11-04 13:32:13.323265
# Keep-alive comment: 2025-11-04 23:32:04.821905
# Keep-alive comment: 2025-11-05 09:32:17.030363
# Keep-alive comment: 2025-11-05 19:31:45.468099
# Keep-alive comment: 2025-11-06 05:32:14.650087
# Keep-alive comment: 2025-11-06 15:31:59.611580
# Keep-alive comment: 2025-11-07 01:31:42.816916
# Keep-alive comment: 2025-11-07 11:31:49.920639
# Keep-alive comment: 2025-11-07 21:31:47.013096
# Keep-alive comment: 2025-11-08 07:31:33.674584
# Keep-alive comment: 2025-11-08 17:31:48.562890
# Keep-alive comment: 2025-11-09 03:32:23.127711
# Keep-alive comment: 2025-11-09 13:31:44.657077
# Keep-alive comment: 2025-11-09 23:31:34.732754
# Keep-alive comment: 2025-11-10 09:31:42.478225
# Keep-alive comment: 2025-11-10 19:31:57.831308
# Keep-alive comment: 2025-11-11 05:31:41.583994
# Keep-alive comment: 2025-11-11 15:31:40.999971
# Keep-alive comment: 2025-11-12 01:31:46.891073
# Keep-alive comment: 2025-11-12 11:31:50.505244
# Keep-alive comment: 2025-11-12 21:32:07.439022
# Keep-alive comment: 2025-11-13 07:31:30.832869
# Keep-alive comment: 2025-11-13 17:31:42.059917
# Keep-alive comment: 2025-11-14 03:31:48.081673
# Keep-alive comment: 2025-11-14 13:32:08.886573
# Keep-alive comment: 2025-11-14 23:31:40.582329
# Keep-alive comment: 2025-11-15 09:31:43.228582
# Keep-alive comment: 2025-11-15 19:31:49.083949
# Keep-alive comment: 2025-11-16 05:31:40.963279
# Keep-alive comment: 2025-11-16 15:31:44.767604
# Keep-alive comment: 2025-11-17 01:31:35.057463
# Keep-alive comment: 2025-11-17 11:32:08.971286
# Keep-alive comment: 2025-11-17 21:31:38.535528
# Keep-alive comment: 2025-11-18 07:31:40.594273
# Keep-alive comment: 2025-11-18 17:31:41.153468
# Keep-alive comment: 2025-11-19 03:31:43.981056
# Keep-alive comment: 2025-11-19 13:31:37.295501
# Keep-alive comment: 2025-11-19 23:31:37.992493
# Keep-alive comment: 2025-11-20 09:31:46.557730
# Keep-alive comment: 2025-11-20 19:33:35.877210
# Keep-alive comment: 2025-11-21 05:31:40.550202
# Keep-alive comment: 2025-11-21 15:31:47.479150
# Keep-alive comment: 2025-11-22 01:31:49.088229
# Keep-alive comment: 2025-11-22 11:31:34.301451
# Keep-alive comment: 2025-11-22 21:31:45.383691
# Keep-alive comment: 2025-11-23 07:31:45.980840
# Keep-alive comment: 2025-11-23 17:31:48.796962
# Keep-alive comment: 2025-11-24 03:31:39.387732
# Keep-alive comment: 2025-11-24 13:31:37.699211
# Keep-alive comment: 2025-11-24 23:31:48.622127
# Keep-alive comment: 2025-11-25 09:32:09.472205
# Keep-alive comment: 2025-11-25 19:31:43.615585
# Keep-alive comment: 2025-11-26 05:31:58.616215
# Keep-alive comment: 2025-11-26 15:32:02.260114
# Keep-alive comment: 2025-11-27 01:31:46.228351
# Keep-alive comment: 2025-11-27 11:31:43.166762
# Keep-alive comment: 2025-11-27 21:31:35.444524
# Keep-alive comment: 2025-11-28 07:31:33.499994
# Keep-alive comment: 2025-11-28 17:31:46.251836
# Keep-alive comment: 2025-11-29 03:31:40.350236
# Keep-alive comment: 2025-11-29 13:31:50.477026
# Keep-alive comment: 2025-11-29 23:31:40.314074
# Keep-alive comment: 2025-11-30 09:31:42.046608
# Keep-alive comment: 2025-11-30 19:31:33.517317
# Keep-alive comment: 2025-12-01 05:31:30.578960
# Keep-alive comment: 2025-12-01 15:31:38.251923
# Keep-alive comment: 2025-12-02 01:31:20.991556
# Keep-alive comment: 2025-12-02 11:31:43.761871
# Keep-alive comment: 2025-12-02 21:31:46.223867
# Keep-alive comment: 2025-12-03 07:31:43.280782
# Keep-alive comment: 2025-12-03 17:31:51.381007
# Keep-alive comment: 2025-12-04 03:31:40.634429
# Keep-alive comment: 2025-12-04 13:31:39.572088
# Keep-alive comment: 2025-12-04 23:31:40.219969
# Keep-alive comment: 2025-12-05 09:31:40.290214
# Keep-alive comment: 2025-12-05 19:31:35.496508
# Keep-alive comment: 2025-12-06 05:31:39.296904
# Keep-alive comment: 2025-12-06 15:31:25.968240
# Keep-alive comment: 2025-12-07 01:31:35.166206
# Keep-alive comment: 2025-12-07 11:31:39.324923
# Keep-alive comment: 2025-12-07 21:31:36.073029
# Keep-alive comment: 2025-12-08 07:31:49.011962
# Keep-alive comment: 2025-12-08 17:31:36.993404
# Keep-alive comment: 2025-12-09 03:31:39.333111
# Keep-alive comment: 2025-12-09 13:31:40.219012
# Keep-alive comment: 2025-12-09 23:31:40.215732
# Keep-alive comment: 2025-12-10 09:31:42.776920
# Keep-alive comment: 2025-12-10 19:31:46.919168
# Keep-alive comment: 2025-12-11 05:31:20.787384
# Keep-alive comment: 2025-12-11 15:31:44.929883
# Keep-alive comment: 2025-12-12 01:31:39.083633
# Keep-alive comment: 2025-12-12 11:31:28.841176
# Keep-alive comment: 2025-12-12 21:31:45.819916
# Keep-alive comment: 2025-12-13 07:31:37.912273
# Keep-alive comment: 2025-12-13 17:31:40.237933
# Keep-alive comment: 2025-12-14 03:31:42.966244
# Keep-alive comment: 2025-12-14 13:31:38.178518
# Keep-alive comment: 2025-12-14 23:31:33.691782
# Keep-alive comment: 2025-12-15 09:31:40.519358
# Keep-alive comment: 2025-12-15 19:31:40.649804
# Keep-alive comment: 2025-12-16 05:31:46.486117
# Keep-alive comment: 2025-12-16 15:31:36.283252
# Keep-alive comment: 2025-12-17 01:32:07.755961
# Keep-alive comment: 2025-12-17 11:31:33.881065
# Keep-alive comment: 2025-12-17 21:34:50.376521
# Keep-alive comment: 2025-12-18 07:31:41.128361
# Keep-alive comment: 2025-12-18 17:31:58.158891
# Keep-alive comment: 2025-12-19 03:31:52.800624
# Keep-alive comment: 2025-12-19 13:31:47.634905
# Keep-alive comment: 2025-12-19 23:32:17.858511
# Keep-alive comment: 2025-12-20 09:31:24.385064
# Keep-alive comment: 2025-12-20 19:31:40.086546
# Keep-alive comment: 2025-12-21 05:31:37.331897
# Keep-alive comment: 2025-12-21 15:31:22.771945
# Keep-alive comment: 2025-12-22 01:31:36.995144
# Keep-alive comment: 2025-12-22 11:31:40.683240
# Keep-alive comment: 2025-12-22 21:31:24.093195
# Keep-alive comment: 2025-12-23 07:31:42.386787
# Keep-alive comment: 2025-12-23 17:31:43.305096
# Keep-alive comment: 2025-12-24 03:31:29.925354
# Keep-alive comment: 2025-12-24 13:31:25.335725
# Keep-alive comment: 2025-12-24 23:31:31.655670
# Keep-alive comment: 2025-12-25 09:31:45.125514
# Keep-alive comment: 2025-12-25 19:31:39.534345
# Keep-alive comment: 2025-12-26 05:31:39.118527
# Keep-alive comment: 2025-12-26 15:31:39.279277
# Keep-alive comment: 2025-12-27 01:31:34.187397
# Keep-alive comment: 2025-12-27 11:31:37.395385
# Keep-alive comment: 2025-12-27 21:31:38.318889
# Keep-alive comment: 2025-12-28 07:31:38.727819
# Keep-alive comment: 2025-12-28 17:31:44.886799
# Keep-alive comment: 2025-12-29 03:31:33.912042
# Keep-alive comment: 2025-12-29 13:31:39.652653
# Keep-alive comment: 2025-12-29 23:31:35.118748
# Keep-alive comment: 2025-12-30 09:31:24.685739
# Keep-alive comment: 2025-12-31 05:31:36.496559
# Keep-alive comment: 2025-12-31 15:31:36.500340
# Keep-alive comment: 2026-01-01 01:31:45.929505
# Keep-alive comment: 2026-01-01 11:31:40.948065
# Keep-alive comment: 2026-01-01 21:31:51.868008
# Keep-alive comment: 2026-01-02 07:31:41.485927
# Keep-alive comment: 2026-01-02 17:31:40.387645
# Keep-alive comment: 2026-01-03 03:31:37.250170
# Keep-alive comment: 2026-01-03 13:31:42.968072
# Keep-alive comment: 2026-01-03 23:31:43.286044
# Keep-alive comment: 2026-01-04 09:31:35.197356
# Keep-alive comment: 2026-01-04 19:31:41.940871
# Keep-alive comment: 2026-01-05 05:31:40.494964