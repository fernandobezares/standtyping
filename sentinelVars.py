import ee
#import geemap

##ee.Authenticate()
ee.Initialize()


def maskS2clouds(image):
    qa = image.select('QA60')

      # Bits 10 and 11 are clouds and cirrus, respectively.
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11

    # Both flags should be set to zero, indicating clear conditions.
    mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))

    # Return the masked and scaled data, without the QA bands.
    return image.updateMask(mask).divide(10000)\
        .select("B.*")\
        .copyProperties(image, ["system:time_start"])


def addNDVI(image):
    """Compute NDVI for Sentinel2 image"""
    ndvi = image.normalizedDifference(["B8","B4"]).rename('ndvi')
    return image.addBands(ndvi)


def get_sentinel2_vars(start_date,end_date,geo):
    """This function calls ee to obtain a cloudless median composite of a Sentinel scene"""
    s2 = ee.ImageCollection("COPERNICUS/S2_SR")\
        .filterDate(start_date,end_date)\
        .filterBounds(geo) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))\
        .map(maskS2clouds)\
        .map(addNDVI)\
        .median()

    return s2

# S1 collection
# ----------------------------------------------------------------------------------------------------
def get_sentinel1_vars(start_date,end_date,geo):
    s1 =  ee.ImageCollection('COPERNICUS/S1_GRD') \
    .filterDate(start_date,end_date)\
    .filterBounds(geo)\
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))\
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))\
    .filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))\
    .filter(ee.Filter.eq('instrumentMode', 'IW'))


    return s1

