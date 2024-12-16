// Import satellite image collection
var dataset = ee.ImageCollection('JAXA/GCOM-C/L3/OCEAN/SST/V3')
                .filterDate('2022-01-01', '2022-02-01')
                // filter to daytime data only
                .filter(ee.Filter.eq('SATELLITE_DIRECTION', 'D'));

// Multiply with slope coefficient and add offset
var dataset = dataset.mean().multiply(0.0012).add(-10);

var vis = {
  bands: ['SST_AVE'],
  min: 0,
  max: 30,
  palette: ['000000', '005aff', '43c8c8', 'fff700', 'ff0000'],
};

Map.setCenter(128.45, 33.33, 5);

// Filter and select images
var geometry = geometry;
// Clip the images
var clippedImage = dataset.clip(geometry);

Map.addLayer(clippedImage, vis, 'Sea Surface Temperature');

// Export the clipped image to Google Drive
Export.image.toDrive({
  image: clippedImage,
  description: "january",
  folder: "EXPORT_FOLDER_NAME",
  fileNamePrefix: "PREFIX",
  region: geometry,
  maxPixels: 791367
});