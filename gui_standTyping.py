import streamlit as st
import datetime
import sentinelVars as svars
import ee

ee.Initialize()

st.header('Stand Typing Dashboard')
st.header('Segment your forest in homogeneous plots using Sentinel data and Aereal Laser Scaner data from the PNOA')
st.markdown('This webb app is offers a methodology for stand typing based in EO data.')

start_date = st.date_input( "Select a start date", datetime.date(2017,3,28))
end_date = st.date_input( "Select a end date", datetime.date(2018,3,28))

print('start_date',start_date)
print('end_date', end_date)

gaul = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level2").filter(ee.Filter.eq('ADM2_NAME','Soria'))
s1 = svars.get_sentinel1_vars(str(start_date),str(end_date),gaul)
s2 = svars.get_sentinel2_vars(str(start_date),str(end_date),gaul)
print('Size collection of s1: ',s1.size().getInfo())
print('Band Names of s2 median composite: ',s2.bandNames().getInfo())