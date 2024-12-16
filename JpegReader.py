from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
import csv
import os

# Python program to extract metadata from JPEG files and save them to a CSV file
# Pillow used to extract exchangeable Image File Format (EXIF) data
# Geopy used for location information, Nominatim used to create address


 #FUNCTIONS

def getExifData(filePath):

    #Extract EXIF metadata from an jpeg file.
    try:
        image = Image.open(filePath)
        exifData = image._getexif()

        if not exifData:
            print(f"No metadata found")
            return None

        metadata = {}

        for tagId, value in exifData.items():
            tagName = TAGS.get(tagId, tagId)
            metadata[tagName] = value
        return metadata
    
    except Exception as e:
        print(f"ERROR: Cannot perform EXIF extraction: {e}")
        return None

def gpsToDecimal(gpsData, ref):

   #Convert GPS data in degrees, minutes, and seconds to decimal format
    try:
        degrees, minutes, seconds = gpsData
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

        if ref in ['S', 'W']:  # South and West coordinates are negative
            decimal *= -1
        return decimal
    
    except Exception as e:
        print(f"Error converting GPS data: {e}")
        return None

def gpsCord(exifData):

    #Extract and convert GPS coordinates from EXIF data
    gpsInfo = exifData.get("GPSInfo")
   
    if not gpsInfo:
        return None, None

    try:
        #Calculate GPS data
        gps_lat = gpsInfo[2]  # Latitude degrees, minutes, seconds (DMS)
        gps_lat_ref = gpsInfo[1]  #Latitude(N or S)
        gps_lon = gpsInfo[4]  # Longitude degrees, minutes, seconds (DMS)
        gps_lon_ref = gpsInfo[3]  #Longitude(E or W)

        # Convert to decimal
        latitude = gpsToDecimal(gps_lat, gps_lat_ref)
        longitude = gpsToDecimal(gps_lon, gps_lon_ref)
        return latitude, longitude
    
    except Exception as e:
        print(f"Error calculating GPS data: {e}")
        return None, None

def gpsToAddress(latitude, longitude):

    #convert GPS coordinates to an address
    try:
        geoAddress = Nominatim(user_agent="gpsToAddress")
        location = geoAddress.reverse((latitude, longitude), exactly_one=True)
        return location.address if location else "Address not found"
    
    except Exception as e:
        print(f"Error retrieving address: {e}")
        return None

def csvMetadata(metadata, latitude, longitude, address, outputFile):
    
    # Create output file
    try:
         # format CSV file

        with open(outputFile, mode='w', newline='', encoding='utf-8') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(["Tag", "Value"])  
            for key, value in metadata.items():
                writer.writerow([key, value])  
            

            # Add GPS and address to the CSV
            if latitude and longitude:
                writer.writerow(["GPS Latitude", latitude])
                writer.writerow(["GPS Longitude", longitude])
            if address:
                writer.writerow(["Address", address])
        print(f"Metadata saved to {outputFile}")
    except Exception as e:
        print(f"Error saving metadata to CSV: {e}")

#MAIN

def main():
    # Prompt the user for the image file path
    filePath = input("Enter the path to the JPEG file: ")

    # Check if the file exists
    if not os.path.isfile(filePath):
        print(f"File not found: {filePath}")
        return

    # Check file is a JPEG or jpg
    if not filePath.lower().endswith(('.jpg', '.jpeg')):
        print(f"The file must be a JPEG image: {filePath}")
        return

    # Extract EXIF metadata
    exifData = getExifData(filePath)
    if exifData:
        print("EXIF Metadata:")
        for key, value in exifData.items():
            print(f"{key}: {value}")

        # Calculate GPS data
        latitude, longitude = gpsCord(exifData)
        address = None
        if latitude and longitude:
            print(f"\nGPS Coordinates: {latitude}, {longitude}")
            address = gpsToAddress(latitude, longitude)
            print(f"Address: {address}")

        # Save metadata to CSV
        outputFile = f"{os.path.splitext(filePath)[0]}Metadata.csv"
        csvMetadata(exifData, latitude, longitude, address, outputFile)

if __name__ == "__main__":
    main()


    
