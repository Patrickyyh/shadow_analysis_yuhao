from pymongo import MongoClient
from django.http import JsonResponse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .solarposition import *
from .shadowingfunction_wallheight_13 import shadowingfunction_wallheight_13
import os
from bson.binary import Binary
import pickle

client = MongoClient('mongodb+srv://yeyuhao12345:12345@app.4ka8no9.mongodb.net/?retryWrites=true&w=majority')
db = client.get_database('data_db')
records = db.test_data
print(records.count_documents({}))
def test(request):
   file_path = os.path.join(os.path.dirname(__file__), 'dsm_local_array.npy')
   dsm = np.load(file_path)
   dsm = np.nan_to_num(dsm, nan=0)
   lon = -95.30052
   lat = 29.73463

   utc_offset= -6

   # Create a date range from 6:00 to 20:00 with a 10-minute interval

   timestamps = pd.date_range('2023-09-12 11:00', '2023-09-12 11:10', freq='30T')

   # Create a DataFrame using the timestamps as a column
   df_solar_data = pd.DataFrame({'TimeStamp': timestamps})
   # UTC time
   df_solar_data['TimeStamp'] = pd.DatetimeIndex(df_solar_data['TimeStamp']) - pd.DateOffset(hours=utc_offset)
   # To_Datetime
   df_solar_data["TimeStamp"] = df_solar_data["TimeStamp"].apply(pd.to_datetime)
   df_solar_data.set_index("TimeStamp", inplace = True)

   # Add time index
   df_solar_data["TimeStamp"] = df_solar_data.index

   df_solar_data.head()
   # Get_sun's position df
   df_solar = get_solarposition(df_solar_data.index, lat, lon)

   # Add time index
   df_solar['TimeStamp'] = pd.DatetimeIndex(df_solar.index) + pd.DateOffset(hours=utc_offset)

   df_solar = df_solar[['TimeStamp', 'apparent_zenith', 'zenith', 'apparent_elevation', 'elevation',
                      'azimuth', 'equation_of_time']]

   # To_Datetime
   df_solar["TimeStamp"] = df_solar["TimeStamp"].apply(pd.to_datetime)
   df_solar.set_index("TimeStamp", inplace = True)

   df_solar["TimeStamp"] = df_solar.index
   df_solar = df_solar[['TimeStamp', 'elevation', 'zenith', 'azimuth']]

   df_solar = df_solar.rename(columns={"elevation": "Elevation","azimuth": "Azimuth", "zenith": "Zenith"})
   scale = 1
   walls = np.zeros((dsm.shape[0], dsm.shape[1]))
   dirwalls = np.zeros((dsm.shape[0], dsm.shape[1]))
   i = 0
   altitude = df_solar['Elevation'][i]
   azimuth = df_solar['Azimuth'][i]
   hour = df_solar.index[i].hour
   minute = df_solar.index[i].minute
   print(hour, minute)

   sh, wallsh, wallsun, facesh, facesun = shadowingfunction_wallheight_13(dsm, azimuth, altitude, scale, walls, dirwalls * np.pi / 180.)
   sh_array = Binary(pickle.dumps(sh, protocol=2), subtype=128 )
   # wallsh_array = Binary(pickle.dumps(wallsh, protocol=2), subtype=128 )
   # wallsun_array =Binary(pickle.dumps(wallsun, protocol=2), subtype=128 )
   # facesh_array = Binary(pickle.dumps(facesh, protocol=2), subtype=128 )
   # facesun_array =Binary(pickle.dumps(facesun, protocol=2), subtype=128 )

   new_data =  {
      'sh' : sh_array,
      'time': df_solar.index[i]
   }

   ## remove all the data in the collection
   records.delete_many({})
   records.insert_one(new_data)

   return JsonResponse({'status': "Shadow analysis result stored into Database Successfuly !!"})
