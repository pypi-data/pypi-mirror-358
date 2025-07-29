import sys
import os
from urllib.request import build_opener


def gfs_forecast(start_date, total_forecast_hours):
    # Validate input
    if not isinstance(start_date, str) or len(start_date) != 10:
        raise ValueError("start_date must be a string in 'YYYYMMDDHH' format")
    if not isinstance(total_forecast_hours, int) or total_forecast_hours < 0:
        raise ValueError("total_forecast_hours must be a non-negative integer")
    
    # Create a list of forecast hours to download
    forecast_hours = range(0, total_forecast_hours + 1, 3)  # Fetch every 3 hours
    filelist = []
    
    # Construct the file URLs
    for hour in forecast_hours:
        hour_str = f"{hour:03d}"  # Format hour to three digits
        file_url = f'https://data.rda.ucar.edu/d084001/2024/{start_date[:8]}/gfs.0p25.{start_date}.f{hour_str}.grib2'
        filelist.append(file_url)

    # Create a URL opener
    download_from_filelist(filelist)



def download_from_filelist(filelist):
    opener = build_opener()

    # Download each file
    for file in filelist:
        ofile = os.path.basename(file)
        sys.stdout.write(f"downloading {ofile} ... ")
        sys.stdout.flush()
        
        try:
            infile = opener.open(file)
            total_size = int(infile.info().get('Content-Length', -1))  # Use -1 if Content-Length is not available
            bytes_downloaded = 0

            with open(ofile, "wb") as outfile:
                chunk_size = 8192  # 8 KB chunks
                while True:
                    chunk = infile.read(chunk_size)
                    if not chunk:
                        break
                    outfile.write(chunk)
                    bytes_downloaded += len(chunk)
                    
                    # Calculate size in MB
                    size_mb_downloaded = bytes_downloaded / (1024 * 1024)  # Convert bytes to MB
                    
                    # Display progress
                    if total_size >= 0:  # If total size is known
                        total_size_mb = total_size / (1024 * 1024)  # Convert total size to MB
                        progress = (bytes_downloaded / total_size) * 100
                        sys.stdout.write(f"\r{ofile} - Downloaded {size_mb_downloaded:.2f} MB of {total_size_mb:.2f} MB ({progress:.2f}%)")
                    else:  # If total size is unknown
                        sys.stdout.write(f"\r{ofile} - Downloaded {size_mb_downloaded:.2f} MB (unknown total size)")

                    sys.stdout.flush()

            sys.stdout.write("\n done\n")
        except Exception as e:
            sys.stdout.write(f"failed: {e}\n")

