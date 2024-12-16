# -*- coding: utf-8 -*-

import arcpy
import arcpy.management
from arcpy.sa import *

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Manatee Habitat Analysis"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [ManateeTool]

class ManateeTool:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Manatee Habitat Suitability Tool"
        self.description = ""

    def getParameterInfo(self):
        """Define the tool parameters."""
        param0 = arcpy.Parameter(
            displayName = "Sea Surface Temperature Raster:", 
            name = "waterTempRaster", 
            datatype = "DERasterBand",
            parameterType= "Required", 
            direction = "Input"
            )
        param1 = arcpy.Parameter(
            displayName = "Sea Surface Temperature Weight (as a percent):", 
            name = "waterTempRaster_weight", 
            datatype = "GPDouble", 
            parameterType= "Required", 
            direction = "Input"
            )
        param1.value = 25

        param2 = arcpy.Parameter(
            displayName = "Seagrass Density Shapefile:", 
            name = "seagrassDensityShapefile", 
            datatype = "DEShapefile",
            parameterType= "Required", 
            direction = "Input"
            )
        param3 = arcpy.Parameter(
            displayName = "Seagrass Density Weight (as a percent):", 
            name = "seagrassDensityShapefile_weight", 
            datatype = "GPDouble", 
            parameterType= "Required", 
            direction = "Input"
            )
        param3.value = 40

        param4 = arcpy.Parameter(
            displayName = "Red Tide Events Shapefile:", 
            name = "redTideShapefile", 
            datatype = "DEShapefile",
            parameterType= "Required", 
            direction = "Input"
            )
        param5 = arcpy.Parameter(
            displayName = "Red Tide Events Weight (as a percent):", 
            name = "redTideShapefile_weight", 
            datatype = "GPDouble", 
            parameterType= "Required", 
            direction = "Input"
            )
        param5.value = 15

        param6 = arcpy.Parameter(
            displayName = "Boat Ramp Locations Shapefile:", 
            name = "boatRampShapefile", 
            datatype = "DEShapefile",
            parameterType= "Required", 
            direction = "Input"
            )
        param7 = arcpy.Parameter(
            displayName = "Boat Ramp Locations Weight (as a percent):", 
            name = "boatRampShapefile_weight", 
            datatype = "GPDouble", 
            parameterType= "Required", 
            direction = "Input"
            )
        param7.value = 20
        param8 = arcpy.Parameter(
            displayName = "Data Output Folder", 
            name = "outputFolder", 
            datatype = "DEFolder", 
            parameterType= "Required", 
            direction = "Input"
            )

        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        
        if (parameters[1].value + parameters[3].value + parameters[5].value + parameters[7].value) != 100:
            arcpy.AddError("Weights do not sum to 100!")
            return
        
        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = parameters[8].value

        # Licenses
        arcpy.CheckOutExtension("3D")
        arcpy.CheckOutExtension("spatial")
        arcpy.CheckOutExtension("ImageAnalyst")

        PREFIX_tif = parameters[0].value
        Seagrass_Habitat_in_Florida_shp = parameters[2].value
        Recent_Harmful_Algal_Bloom_HAB_Events_shp = parameters[4].value
        boatramps = parameters[6].value

        '''
        Sea temp:
        '''

        # Process: Reclassify (4) (Reclassify) (3d)
        reclassifyTemp_tif = r"reclassifyTemp.tif"
        with arcpy.EnvManager(extent="-88 24 -79 31 GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]]"):
            arcpy.ddd.Reclassify(in_raster=PREFIX_tif, reclass_field="VALUE", remap="0 19.999000 0;20 21.999000 50;22 26.999000 100;27 27.573050 50;NODATA 0", out_raster=reclassifyTemp_tif)
        reclassifyTemp_tif = arcpy.Raster(reclassifyTemp_tif)
        arcpy.AddMessage("Reclassified Sea Temperature Raster")

        '''
        Seagrass:
        '''

        # Process: Polygon to Raster (Polygon to Raster) (conversion)
        sgPointToRaster_tif = r"sgPointToRaster.tif"
        with arcpy.EnvManager(extent="-88 24 -79 31 GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]]"):
            arcpy.conversion.PolygonToRaster(in_features=Seagrass_Habitat_in_Florida_shp, value_field="SEAGRASSco", out_rasterdataset=sgPointToRaster_tif)
        arcpy.AddMessage("Converted Seagrass Polygon to Raster")

        # Process: Reclassify (2) (Reclassify) (3d)
        Reclass_sgPTR = r"Reclass_sgPTR"
        arcpy.ddd.Reclassify(in_raster=sgPointToRaster_tif, reclass_field="Value", remap="1 50;2 0;NODATA -100", out_raster=Reclass_sgPTR)
        Reclass_sgPTR = arcpy.Raster(Reclass_sgPTR)
        arcpy.AddMessage("Reclassified Seagrass Raster")

        '''
        Algae:
        '''

        # Process: Buffer (3) (Buffer) (analysis)
        Recent_Harmful_Algal_Buffer = r"Recent_Harmful_Algal__Buffer"
        arcpy.analysis.Buffer(in_features=Recent_Harmful_Algal_Bloom_HAB_Events_shp, out_feature_class=Recent_Harmful_Algal_Buffer, buffer_distance_or_field="1 Miles")

        # Process: Polygon to Raster (3) (Polygon to Raster) (conversion)
        algaePointToRaster_tif = r"algaePointToRaster.tif"
        with arcpy.EnvManager(extent="-88 24 -79 31 GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]]"):
            arcpy.conversion.PolygonToRaster(in_features=Recent_Harmful_Algal_Buffer, value_field="ABcode", out_rasterdataset=algaePointToRaster_tif)
        arcpy.AddMessage("Converted Algae Polygon to Raster")

        # Process: Reclassify (5) (Reclassify) (3d)
        Reclass_algae = r"Reclass_algae"
        arcpy.ddd.Reclassify(in_raster=algaePointToRaster_tif, reclass_field="VALUE", remap="1 -50;NODATA 0", out_raster=Reclass_algae)
        Reclass_algae = arcpy.Raster(Reclass_algae)
        arcpy.AddMessage("Reclassified Algae Raster")

        '''
        Boat ramps:
        '''
        
        # Process: Buffer (2) (Buffer) (analysis)
        boatramps_Buffer = r"boatramps_Buffer"
        with arcpy.EnvManager(extent="-88 24 -79 31 GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]]"):
            arcpy.analysis.Buffer(in_features=boatramps, out_feature_class=boatramps_Buffer, buffer_distance_or_field="0.5 Miles")

        # Process: Polygon to Raster (2) (Polygon to Raster) (conversion)
        boatPointToRaster_tif = r"boatPointToRaster.tif"
        with arcpy.EnvManager(extent="-88 24 -79 31 GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]]"):
            arcpy.conversion.PolygonToRaster(in_features=boatramps_Buffer, value_field="Vehicle", out_rasterdataset=boatPointToRaster_tif)
        arcpy.AddMessage("Converted Boat Ramp Polygon to Raster")

        # Process: Reclassify (3) (Reclassify) (3d)
        Reclass_boat1 = r"Reclass_boat1"
        arcpy.ddd.Reclassify(in_raster=boatPointToRaster_tif, reclass_field="VALUE", remap="0 5 0;5 22 -10;22 56 -25;56 104 -50;104 200 -100;NODATA 20", out_raster=Reclass_boat1)
        Reclass_boat1 = arcpy.Raster(Reclass_boat1)
        arcpy.AddMessage("Reclassified Boat Ramp Raster")
        
        '''
        Final raster calc + save as finalRaster.tif:
        '''

        # Process: Raster Calculator (Raster Calculator) (ia)
        finalRaster_tif = r"finalRaster.tif"
        Raster_Calculator = finalRaster_tif
        with arcpy.EnvManager(extent="-88 24 -79 31 GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]]"):
            finalRaster_tif = (reclassifyTemp_tif * parameters[1].value) + (Reclass_sgPTR * parameters[3].value) + (Reclass_algae * parameters[5].value) + (Reclass_boat1 * parameters[7].value) 
            finalRaster_tif.save(Raster_Calculator)
        arcpy.AddMessage("Calculated suitability model, saved as " + str(parameters[8].value) + "/finalRaster.tif")

        arcpy.management.Delete(r"'boatPointToRaster.tif';'algaePointToRaster.tif';'sgPointToRaster.tif';'reclassifyTemp.tif'")

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return